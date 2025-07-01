# README

## 项目概述

本项目是一个基于Vue.js前端和Flask后端的智能视觉检测系统，集成了YOLO目标检测模型和AI大模型分析功能，支持多种场景的图像和视频识别，包括烟雾检测、火焰识别、人员落水检测等多个应用场景。

## 项目结构

```
Root/
├── Web-Front/                    # Vue.js前端应用
├── Collective Backend/           # Flask后端应用
├── DataBase.sql                  # 数据库结构文件
└── 会议纪要文档
```

## 前端文件说明 (Web-Front/)

### 核心配置文件

- **<mcfile name="package.json" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/package.json"></mcfile>**: 项目依赖配置，包含Vue 3、Vue Router、Vuex等核心依赖
- **<mcfile name="vue.config.js" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/vue.config.js"></mcfile>**: Vue CLI配置文件，配置开发服务器和构建选项
- **<mcfile name="babel.config.js" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/babel.config.js"></mcfile>**: Babel转译配置
- **<mcfile name="jsconfig.json" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/jsconfig.json"></mcfile>**: JavaScript项目配置，设置路径别名

### 路由配置

- **<mcfile name="index.js" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/router/index.js"></mcfile>**: Vue Router路由配置
  - 定义了所有页面路由（首页、登录、产品市场、测试页面、AI分析等）
  - 实现路由守卫，保护需要认证的页面
  - 自动重定向未认证用户到登录页

### 状态管理

- **<mcfile name="index.js" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/store/index.js"></mcfile>**: Vuex状态管理
  - 管理用户登录状态和用户信息
  - 提供`setUser`、`clearUser`等mutations
  - 包含`logout` action处理用户登出

### 主要页面组件

#### 1. 应用入口
- **<mcfile name="App.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/App.vue"></mcfile>**: 应用根组件，包含导航栏和路由视图

#### 2. 首页和介绍页面
- **<mcfile name="Home.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/Home.vue"></mcfile>**: 系统首页，展示项目介绍和功能概览
- **<mcfile name="ProjectIntro.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/ProjectIntro.vue"></mcfile>**: 项目详细介绍页面
- **<mcfile name="About.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/About.vue"></mcfile>**: 关于页面

#### 3. 用户认证
- **<mcfile name="Login.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/Login.vue"></mcfile>**: 用户登录和注册页面
  - 支持用户注册和登录功能
  - 登录成功后保存用户状态到Vuex
  - 自动跳转到产品市场页面

#### 4. 核心功能页面
- **<mcfile name="ProductMarket.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/ProductMarket.vue"></mcfile>**: 产品市场页面
  - 展示10种不同的检测模型（烟雾、火焰、人员落水等）
  - 每个模型都有对应的图片展示和权重文件
  - 点击后跳转到测试页面并传递模型参数

- **<mcfile name="Test.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/Test.vue"></mcfile>**: 核心检测功能页面
  - 支持图像和视频文件上传
  - 调用后端YOLO模型进行目标检测
  - 显示原始文件和处理后结果的对比
  - 支持模式切换（图像/视频）
  - 集成DDoS防护错误处理
  - 提供保存处理结果和跳转AI分析功能

- **<mcfile name="AiAnalysis.vue" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/views/AiAnalysis.vue"></mcfile>**: AI大模型分析页面
  - 基于豆包视觉理解模型提供智能分析
  - 支持对检测结果进行深度分析和建议
  - 实现DDoS攻击检测后的自动处理流程
  - 包含用户确认对话框和自动退出登录功能

## 后端文件说明 (Collective Backend/ultralytics/)

### 主应用文件

- **<mcfile name="app.py" path="/Users/Erikline/Desktop/大型软件设计/Collective Backend/ultralytics/app.py"></mcfile>**: Flask主应用文件
  - 集成YOLO目标检测模型
  - 提供用户认证API（注册、登录、登出）
  - 实现文件上传和处理功能
  - 集成豆包AI大模型分析
  - 应用DDoS防护装饰器
  - 配置CORS支持前端跨域请求

### 核心模块

#### 1. DDoS防护模块
- **<mcfile name="ddos_detector.py" path="/Users/Erikline/Desktop/大型软件设计/Collective Backend/ultralytics/modules/ddos_detector.py"></mcfile>**: DDoS攻击检测器
  - **功能**: 实时监控用户行为，检测潜在的DDoS攻击
  - **阈值配置**: 会话数阈值(10)、对话数阈值(10)、时间窗口(1分钟)
  - **核心方法**:
    - `update_user_stats()`: 更新用户攻击统计
    - `check_ddos_attack()`: 检测DDoS攻击
    - `ban_user_for_ddos()`: 根据攻击次数动态调整封禁时长
    - `reset_user_stats()`: 定时重置用户统计

#### 2. 用户管理模块
- **用户管理器**: 处理用户注册、认证、封禁状态检查等功能

#### 3. 数据库配置
- **数据库连接**: 提供数据库查询执行功能

### 依赖文件
- **<mcfile name="requirements.txt" path="/Users/Erikline/Desktop/大型软件设计/Collective Backend/ultralytics/requirements.txt"></mcfile>**: Python依赖包列表

## 数据库设计 (DataBase.sql)

**<mcfile name="DataBase.sql" path="/Users/Erikline/Desktop/大型软件设计/DataBase.sql"></mcfile>**: 完整的数据库结构定义，包含15个表：

### 用户管理模块（4个表）
1. **user_names**: 用户基本信息表
2. **permissions**: 用户权限管理表
3. **session_users**: 用户会话管理表
4. **user_attack_stats**: 用户攻击行为统计表（DDoS防护）

### 管理员管理模块（2个表）
5. **admin_names**: 管理员信息表
6. **admin_permissions**: 管理员权限表

### 会话对话模块（4个表）
7. **sessions**: 会话记录表
8. **conversations**: 对话记录表
9. **session_images**: 会话图片存储表
10. **conversation_responses**: 对话响应表

### 安全防护模块（5个表）
11. **banned_users**: 被封禁用户表
12. **login_attempts**: 登录尝试记录表
13. **security_logs**: 安全日志表
14. **system_settings**: 系统设置表
15. **audit_logs**: 审计日志表

## 主要功能特性

### 1. 智能视觉检测
- 支持10种不同场景的目标检测（烟雾、火焰、人员落水等）
- 基于YOLO模型的实时图像和视频处理
- 处理结果可视化展示

### 2. AI大模型分析
- 集成豆包视觉理解模型
- 对检测结果提供智能分析和建议
- 支持多轮对话交互

### 3. 用户管理系统
- 完整的用户注册、登录、权限管理
- 会话管理和状态保持
- 管理员权限分离

### 4. 安全防护机制
- **DDoS攻击检测**: 实时监控用户行为模式
- **动态封禁**: 根据攻击严重程度调整封禁时长
- **自动处理**: 检测到攻击后自动清除会话并重定向
- **审计日志**: 完整的安全事件记录

### 5. 系统监控
- 用户行为统计和分析
- 系统性能监控
- 安全事件日志记录

## 技术栈

### 前端
- **Vue.js 3**: 渐进式JavaScript框架
- **Vue Router**: 单页应用路由管理
- **Vuex**: 状态管理
- **Composition API**: Vue 3新特性

### 后端
- **Flask**: Python Web框架
- **YOLO (Ultralytics)**: 目标检测模型
- **OpenAI API**: 大模型集成
- **MySQL**: 关系型数据库
- **Flask-CORS**: 跨域资源共享

### 安全特性
- **会话管理**: Flask Session
- **DDoS防护**: 自定义检测算法
- **权限控制**: 基于角色的访问控制
- **数据加密**: 密码哈希存储

## 部署说明

### 前端部署
```bash
cd Web-Front
npm install
npm run dev  # 开发环境
```

### 后端部署
```bash
pip install -r requirements.txt
cd "Collective Backend/ultralytics"
python app.py
```

### 数据库初始化
```bash
mysql -u username -p < DataBase.sql
```

## 开发团队协作指南

### 前端开发
1. **组件开发**: 遵循Vue 3 Composition API规范
2. **路由管理**: 在<mcfile name="index.js" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/router/index.js"></mcfile>中添加新路由
3. **状态管理**: 在<mcfile name="index.js" path="/Users/Erikline/Desktop/大型软件设计/Web-Front/src/store/index.js"></mcfile>中管理全局状态
4. **API调用**: 统一使用fetch API，注意错误处理

### 后端开发
1. **API开发**: 在<mcfile name="app.py" path="/Users/Erikline/Desktop/大型软件设计/Collective Backend/ultralytics/app.py"></mcfile>中添加新接口
2. **安全防护**: 使用`@require_auth`和`@ddos_protection`装饰器
3. **数据库操作**: 使用`execute_query`函数进行数据库操作
4. **日志记录**: 使用logging模块记录重要操作

### 数据库修改
1. **表结构变更**: 修改<mcfile name="DataBase.sql" path="/Users/Erikline/Desktop/大型软件设计/DataBase.sql"></mcfile>
2. **数据迁移**: 编写相应的迁移脚本
3. **索引优化**: 根据查询需求添加适当索引

## 注意事项

1. **安全配置**: 修改Flask应用的`secret_key`为安全密钥
2. **API密钥**: 配置豆包AI模型的API密钥
3. **数据库连接**: 配置正确的数据库连接参数
4. **CORS设置**: 根据部署环境调整CORS配置
5. **DDoS阈值**: 根据实际需求调整DDoS检测阈值

## 故障排除

### 常见问题
1. **前端路由问题**: 检查路由守卫和认证状态
2. **API调用失败**: 检查CORS配置和后端服务状态
3. **DDoS误报**: 调整检测阈值或时间窗口
4. **数据库连接**: 检查数据库服务和连接配置

### 调试建议
1. **前端**: 使用浏览器开发者工具查看网络请求和控制台错误
2. **后端**: 查看Flask应用日志和数据库查询日志
3. **数据库**: 使用SQL客户端直接查询验证数据状态
        