/*
=============================================================================
                        AI图像识别与对话系统数据库设计
=============================================================================

设计目标：
1. 实现用户管理和权限控制
2. 支持AI图像识别和多轮对话功能
3. 提供敏感内容过滤和安全防护
4. 防范DDoS攻击和恶意行为
5. 确保数据完整性和系统安全性

表结构概览（共计15个表）：
- 用户相关表：4个（用户基本信息、密码、安全统计）
- 管理员相关表：2个（管理员信息、密码）
- 权限控制表：1个（权限管理）
- 会话对话表：7个（会话管理、消息记录、AI响应）
- 安全防护表：1个（敏感词库）

=============================================================================
*/
-- =============================================================================
-- 创建 & 使用数据库
-- =============================================================================
CREATE DATABASE IF NOT EXISTS AIDataBase CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE AIDataBase;


-- =============================================================================
-- 用户管理模块（4个表）
-- =============================================================================

-- 1. 用户名-用户id映射表
-- 功能：存储用户名到用户ID的唯一映射关系
-- 设计理念：分离用户标识和内部ID，便于用户名修改和系统扩展
CREATE TABLE user_names (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '系统内部用户ID，自增主键',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名，唯一标识符',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '用户角色：user=普通用户, admin=管理员'
);

-- 2. 用户id-密码映射表
-- 功能：存储用户密码信息，与用户基本信息分离提高安全性
-- 安全考虑：密码应使用SHA256或更强的加密算法存储
CREATE TABLE user_passwords (
    user_id INT PRIMARY KEY COMMENT '用户ID，关联user_names表',
    password VARCHAR(255) NOT NULL COMMENT '加密后的用户密码，会议中建议使用bcrypt加密，但也可以用SHA256、MD5等',
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE
) COMMENT='用户密码表，存储加密后的用户登录凭证';

-- 3. 用户安全统计表
-- 功能：汇总用户的安全相关统计数据
-- 设计理念：实时统计，支持多维度安全监控
-- 注意事项：记得在后端设置触发阈值，超过此值将被封禁
CREATE TABLE user_security_stats (
    user_id INT PRIMARY KEY COMMENT '用户ID，关联user_names表',
    total_keyword_triggers INT DEFAULT 0 COMMENT '累计关键词触发次数',
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE
) COMMENT='用户安全统计表，汇总用户的安全监控数据';

-- 4. 用户攻击行为统计表
-- 功能：记录用户的攻击行为统计，用于DDoS防护
-- 算法：总攻击次数 = Σ(Δt时间内的总会话次数) + Σ(Δt时间内的总对话次数)
-- 注意事项：需要在后端设置阈值
CREATE TABLE user_attack_stats (
    user_id INT PRIMARY KEY COMMENT '用户ID，关联user_names表',
    delta_time_window INT DEFAULT 1 COMMENT '时间窗口大小（分钟）',
    session_count INT DEFAULT 0 COMMENT '用户在时间窗口内的总会话次数',
    conversation_count INT DEFAULT 0 COMMENT '用户在时间窗口内的总对话次数',
    is_ddos TINYINT(1) DEFAULT 0 COMMENT '是否检测到DDoS攻击：0=正常，1=检测到攻击',
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE
) COMMENT='用户攻击行为统计表，用于DDoS攻击检测和防护';

-- =============================================================================
-- 管理员管理模块（2个表）
-- =============================================================================

-- 5. 管理员名-管理员id映射表
-- 功能：存储管理员基本信息，与用户表分离管理
-- 设计理念：管理员和普通用户采用不同的表结构，便于权限管理
CREATE TABLE admin_names (
    admin_name VARCHAR(50) PRIMARY KEY COMMENT '管理员用户名，唯一标识符',
    admin_id INT UNIQUE NOT NULL AUTO_INCREMENT COMMENT '系统内部管理员ID，自增主键'
) COMMENT='管理员基本信息表，存储管理员身份标识';

-- 6. 管理员id-密码映射表
-- 功能：存储管理员密码，与管理员基本信息分离
-- 安全考虑：管理员密码应使用更强的加密算法和更复杂的密码策略
CREATE TABLE admin_passwords (
    admin_id INT PRIMARY KEY COMMENT '管理员ID，关联admin_names表',
    password VARCHAR(255) NOT NULL COMMENT '加密后的管理员密码，建议使用强加密算法，同用户，只要我们采用一致的加密体系就可以了',
    FOREIGN KEY (admin_id) REFERENCES admin_names(admin_id) ON DELETE CASCADE
) COMMENT='管理员密码表，存储管理员登录凭证';

-- =============================================================================
-- 权限控制模块（1个表）
-- =============================================================================

-- 7. 统一权限管理表
-- 修改后的统一权限管理表
-- 功能：实现用户和管理员的细粒度权限控制，被封禁用户权限设为NULL
DROP TABLE IF EXISTS permissions;
CREATE TABLE permissions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '权限记录唯一ID',
    user_id INT NULL COMMENT '普通用户ID，与admin_id互斥',
    admin_id INT NULL COMMENT '管理员ID，与user_id互斥',
    permission_value TINYINT(1) NULL COMMENT '权限值：0=无权限，1=有权限，NULL=被封禁用户（无任何权限）',
    permission_type ENUM('upload', 'chat', 'manage', 'view_ALLdiagram', 'ban_user','unban_user') NOT NULL COMMENT '权限类型：upload=上传图片，chat=对话，manage=管理用户,view_ALLdiagram=查看所有图表,ban_user=封禁用户,unban_user=解封用户',
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES admin_names(admin_id) ON DELETE CASCADE,
    CONSTRAINT chk_user_or_admin CHECK (
        (user_id IS NOT NULL AND admin_id IS NULL) OR
        (admin_id IS NOT NULL AND user_id IS NULL)
    )
) COMMENT='统一权限管理表，实现细粒度的权限控制，被封禁用户权限为NULL';

-- =============================================================================
-- 会话对话模块（7个表）
-- =============================================================================

-- 8. 会话-用户关联表
-- 功能：建立会话与用户的关联关系，每个会话对应一个用户
-- 业务逻辑：会话id等于当前上传的图片id（根据需求文档）
CREATE TABLE session_users (
    session_id BIGINT PRIMARY KEY COMMENT '会话ID，等于上传的图片ID',
    user_id INT NOT NULL COMMENT '发起会话的用户ID',
    image_path VARCHAR(500) COMMENT '上传图片的存储路径',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '会话创建时间，也需要作为前端端一个组件进行展示',
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE
)COMMENT='会话用户关联表，记录每个会话的发起用户';

-- 9. 会话检测类别表
-- 功能：存储每个会话的图像检测类别信息
-- 业务场景：AI图像识别后确定的图片类别（如：动物、植物、物体等）
CREATE TABLE session_categories (
    session_id BIGINT PRIMARY KEY COMMENT '会话ID，关联session_users表',
    detection_category ENUM(
    'smoke_detection',           -- 烟雾识别
    'fire_detection',            -- 火焰识别
    'person_drowning',           -- 人员落水识别
    'solar_panel_inspection',    -- 光伏巡检识别
    'river_floating_objects',    -- 河道漂浮物识别
    'crop_growth_monitoring',    -- 农田作物生长情况识别
    'pedestrian_red_light',      -- 行人闯红灯识别
    'vehicle_red_light',         -- 车辆闯红灯识别
    'person_fall_detection',     -- 人员摔倒识别
    'scenic_area_crowd'          -- 景区客流量识别
    ) NOT NULL COMMENT '图像检测类别：具体的AI识别功能类型',
    FOREIGN KEY (session_id) REFERENCES session_users(session_id) ON DELETE CASCADE
) COMMENT='会话检测类别表，存储AI图像识别的类别结果';

-- 10. 会话识别结果表
-- 功能：存储AI对上传图片的详细识别结果
-- 数据类型：使用TEXT类型存储可能较长的识别描述
CREATE TABLE session_results (
    session_id BIGINT PRIMARY KEY COMMENT '会话ID，关联session_users表',
    recognition_result TEXT NOT NULL COMMENT 'AI图像识别的详细结果描述',
    processed_image_path VARCHAR(500) COMMENT '处理后图片的本地存储路径',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '识别完成时间',
    FOREIGN KEY (session_id) REFERENCES session_users(session_id) ON DELETE CASCADE
) COMMENT='会e话识别结果表，存储AI图像识别的详细结果';

-- 11. 用户消息表
-- 功能：存储用户在对话中发送的消息内容
-- 设计要点：支持多轮对话，通过round_id区分对话轮次
CREATE TABLE user_messages (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '消息记录唯一ID',
    session_id BIGINT NOT NULL COMMENT '所属会话ID',
    round_id INT NOT NULL COMMENT '对话轮次ID，从1开始递增',
    message_content TEXT NOT NULL COMMENT '用户发送的消息内容',
    FOREIGN KEY (session_id) REFERENCES session_users(session_id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_round (session_id, round_id)
) COMMENT='用户消息表，存储用户在多轮对话中发送的消息';

-- 12. AI响应表
-- 功能：存储AI对用户消息的回复内容
-- 对应关系：与user_messages表通过session_id和round_id关联
CREATE TABLE ai_responses (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'AI响应记录唯一ID',
    session_id BIGINT NOT NULL COMMENT '所属会话ID',
    round_id INT NOT NULL COMMENT '对话轮次ID，与用户消息对应',
    response_content TEXT NOT NULL COMMENT 'AI生成的回复内容',
    FOREIGN KEY (session_id) REFERENCES session_users(session_id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_round (session_id, round_id)
) COMMENT='AI响应表，存储AI在多轮对话中的回复内容';

-- 13. 关键词触发详情表
-- 功能：记录每轮对话的敏感关键词触发详情
-- 设计理念：详细记录每次触发事件，便于审核和分析
CREATE TABLE keyword_trigger_details (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '触发记录唯一ID',
    session_id BIGINT NOT NULL COMMENT '所属会话ID',
    round_id INT NOT NULL COMMENT '对话轮次ID',
    user_id INT NOT NULL COMMENT '触发用户ID，冗余字段便于统计',
    keyword_triggered TINYINT(1) DEFAULT 0 COMMENT '当前对话轮次是否触发关键词：0=未触发，1=触发',
    triggered_keywords TEXT NULL COMMENT '触发的具体关键词列表，JSON格式存储',
    FOREIGN KEY (session_id) REFERENCES session_users(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_round (session_id, round_id)
) COMMENT='关键词触发详情表，记录每轮对话的敏感内容检测结果';


-- =============================================================================
-- 安全防护模块（2个表）
-- =============================================================================

-- 14. 敏感关键词库表
-- 功能：存储系统的敏感词汇库，用于内容过滤
-- 分类管理：按照敏感内容类型进行分类管理
CREATE TABLE sensitive_keywords (
    keyword_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '关键词唯一ID',
    keyword VARCHAR(100) NOT NULL COMMENT '敏感关键词内容',
    category ENUM(
        '涉黄内容',         -- 色情、性暗示等不当内容
        '暴力内容',         -- 暴力、血腥、伤害等内容
        '政治敏感',         -- 政治敏感话题和人物
        '赌博相关',         -- 赌博、博彩等内容
        '毒品相关',         -- 毒品、吸毒等违法内容
        '恐怖主义',         -- 恐怖主义、极端主义
        '诈骗欺诈',         -- 诈骗、欺诈、虚假信息
        '仇恨言论',         -- 种族歧视、仇恨言论
        '隐私泄露',         -- 个人隐私、身份信息泄露
        '非法交易',         -- 非法买卖、走私等
        '邪教相关',         -- 邪教、迷信等内容
        '其他敏感'          -- 其他类型的敏感内容
    ) NOT NULL COMMENT '关键词分类'
) COMMENT='敏感关键词库表，存储用于内容过滤的敏感词汇';


-- 15. 被封禁用户表
-- 功能：专门管理被封禁用户的信息，与权限表配合实现完整的权限控制
-- 设计理念：独立管理封禁状态，便于权限查询和管理
CREATE TABLE banned_users (
    banned_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '封禁记录唯一ID',
    user_id INT UNIQUE NOT NULL COMMENT '被封禁的用户ID',
    ban_reason ENUM('keyword_trigger', 'ddos_attack', 'manual_ban', 'violation') NOT NULL COMMENT '封禁原因：keyword_trigger=关键词触发，ddos_attack=DDoS攻击，manual_ban=手动封禁，violation=违规行为',
    ban_description VARCHAR(500) NULL COMMENT '封禁详细描述',
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '封禁时间',
    ban_duration INT NULL COMMENT '封禁时长（分钟），NULL表示永久封禁',
    unban_at TIMESTAMP NULL COMMENT '解封时间，NULL表示永久封禁',
    banned_by_admin_id INT NULL COMMENT '执行封禁的管理员ID，NULL表示系统自动封禁',
    is_active TINYINT(1) DEFAULT 1 COMMENT '封禁状态：0=已解封，1=封禁中',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '封禁开始时间，用于解禁',
    FOREIGN KEY (user_id) REFERENCES user_names(user_id) ON DELETE CASCADE,
    FOREIGN KEY (banned_by_admin_id) REFERENCES admin_names(admin_id) ON DELETE SET NULL
) COMMENT='被封禁用户管理表，专门记录和管理用户封禁状态';

-- 16. 管理员邀请码表
CREATE TABLE admin_invite_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invite_code VARCHAR(50) UNIQUE NOT NULL COMMENT '邀请码',
    used_by_user_id INT NULL COMMENT '使用该邀请码的用户ID',
    FOREIGN KEY (used_by_user_id) REFERENCES user_names(user_id)
) COMMENT='管理员邀请码表';

-- =============================================================================
-- 系统初始化数据
-- =============================================================================

-- 创建默认管理员账户
INSERT INTO admin_names (admin_name) VALUES ('admin');
INSERT INTO admin_passwords (admin_id, password) VALUES (1, SHA2('admin123', 256));

-- 为默认管理员分配权限
INSERT INTO permissions (admin_id, permission_value, permission_type) VALUES 
(1, 1, 'manage'),           -- 用户管理权限
(1, 1, 'view_ALLdiagram');  -- 查看所有图表权限

-- 封禁用户
-- INSERT INTO banned_users (user_id, ban_reason, ban_duration) VALUES 
-- (违规用户ID, 'keyword_trigger', 1440); -- 封禁24小时


-- 敏感关键词预设数据
INSERT INTO sensitive_keywords (keyword, category) VALUES
-- 涉黄内容
('色情', '涉黄内容'),
('裸体', '涉黄内容'),
('性交', '涉黄内容'),
('淫秽', '涉黄内容'),
('黄色网站', '涉黄内容'),
('成人影片', '涉黄内容'),

-- 暴力内容
('杀人', '暴力内容'),
('血腥', '暴力内容'),
('暴力', '暴力内容'),
('砍杀', '暴力内容'),
('虐待', '暴力内容'),
('酷刑', '暴力内容'),
('自杀', '暴力内容'),

-- 政治敏感
('政治敏感', '政治敏感'),
('反政府', '政治敏感'),
('颠覆国家', '政治敏感'),
('分裂国家', '政治敏感'),
('台独', '政治敏感'),
('港独', '政治敏感'),

-- 赌博相关
('赌博', '赌博相关'),
('博彩', '赌博相关'),
('赌场', '赌博相关'),
('老虎机', '赌博相关'),
('网络赌博', '赌博相关'),
('彩票诈骗', '赌博相关'),

-- 毒品相关
('毒品', '毒品相关'),
('吸毒', '毒品相关'),
('海洛因', '毒品相关'),
('冰毒', '毒品相关'),
('大麻', '毒品相关'),
('可卡因', '毒品相关'),
('制毒', '毒品相关'),

-- 恐怖主义
('恐怖主义', '恐怖主义'),
('恐怖袭击', '恐怖主义'),
('爆炸', '恐怖主义'),
('炸弹', '恐怖主义'),
('极端主义', '恐怖主义'),
('圣战', '恐怖主义'),

-- 诈骗欺诈
('诈骗', '诈骗欺诈'),
('欺诈', '诈骗欺诈'),
('虚假信息', '诈骗欺诈'),
('网络诈骗', '诈骗欺诈'),
('电信诈骗', '诈骗欺诈'),
('金融诈骗', '诈骗欺诈'),
('传销', '诈骗欺诈'),

-- 仇恨言论
('种族歧视', '仇恨言论'),
('仇恨言论', '仇恨言论'),
('民族歧视', '仇恨言论'),
('宗教歧视', '仇恨言论'),
('性别歧视', '仇恨言论'),
('地域歧视', '仇恨言论'),

-- 隐私泄露
('身份证号', '隐私泄露'),
('手机号码', '隐私泄露'),
('银行卡号', '隐私泄露'),
('个人隐私', '隐私泄露'),
('泄露信息', '隐私泄露'),
('人肉搜索', '隐私泄露'),

-- 非法交易
('非法买卖', '非法交易'),
('走私', '非法交易'),
('黑市交易', '非法交易'),
('器官买卖', '非法交易'),
('人口贩卖', '非法交易'),
('军火交易', '非法交易'),

-- 邪教相关
('邪教', '邪教相关'),
('法轮功', '邪教相关'),
('全能神', '邪教相关'),
('迷信', '邪教相关'),
('邪教组织', '邪教相关'),
('洗脑', '邪教相关'),

-- 其他敏感
('反社会', '其他敏感'),
('危害公共安全', '其他敏感'),
('煽动暴乱', '其他敏感'),
('破坏社会秩序', '其他敏感'),
('违法犯罪', '其他敏感'),
('有害信息', '其他敏感');

-- 插入预设的管理员邀请码（可重复使用）
INSERT INTO admin_invite_codes (invite_code) VALUES 
('ADMIN2025'),
('MANAGER001'),
('SUPERVISOR'),
('HUIMOU_ADMIN'),
('TECH_LEAD'),
('SYSTEM_ADMIN'),
('MASTER_KEY'),
('ADMIN_ACCESS'),
('CONTROL_PANEL'),
('ROOT_ACCESS');
