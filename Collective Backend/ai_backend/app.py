import hashlib
import logging
import os
import secrets
import random
import shutil
import time
import uuid
import base64
from datetime import datetime
from functools import wraps

import cv2
from flask import Flask, request, jsonify, render_template, session, send_from_directory
from flask_cors import CORS
from moviepy import *
from openai import OpenAI

from ultralytics import YOLO
from modules.user_manager import UserManager
from modules.ddos_detector import DDoSDetector
from config.database import execute_query
from scheduler import scheduler

# 设置环境变量
os.environ['VOLC_ACCESSKEY'] = 'AKLTNmZlNTYxZDc4ZDBhNGE5ZmEzMDc3ZTBhZmQyZGE0ZDM'
os.environ['VOLC_SECRETKEY'] = 'TlRZMlptWmhZbVl6TjJVMU5HRmpPR0kwTURNMU1UQmlabUkxWXpCak9EYw=='
os.environ['ARK_API_KEY'] = '72eb22d2-c2ae-43f5-99d7-7f8e122f8045'  # 豆包视觉模型API Key

# Flask 应用初始化
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# 新增：处理后图片目录
PROCESSED_DIR = 'processed_images'
os.makedirs(PROCESSED_DIR, exist_ok=True)

# 修复CORS配置
CORS(app, 
     resources={r"*": {"origins": ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8081", "http://127.0.0.1:8081", "http://localhost:5001", "http://127.0.0.1:5001"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# 设置日志
logging.basicConfig(level=logging.INFO)

# 目录和路径
WEIGHTS_DIR = 'PtSource'
UPLOAD_DIR = 'uploads'
RESULTS_DIR = 'runs/predict/latest'

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# 大模型 API 客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),  
)

# 装饰器：检查用户认证和封禁状态
# 装饰器：检查用户认证和封禁状态
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        role = session.get('role', 'user')
        
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        # 验证用户是否存在
        if role == 'admin':
            user_exists = execute_query(
                "SELECT 1 FROM admin_names WHERE admin_id = %s",
                (user_id,),
                fetch=True
            )
        else:
            user_exists = execute_query(
                "SELECT 1 FROM user_names WHERE user_id = %s",
                (user_id,),
                fetch=True
            )
            
        if not user_exists:
            session.clear()  # 清除无效的会话
            return jsonify({"error": "Invalid user session. Please log in again."}), 401
        
        # 检查用户是否被封禁（仅对普通用户）
        if role == 'user':
            is_banned, ban_info = UserManager.is_user_banned(user_id)
            if is_banned:
                return jsonify({"error": f"Account banned: {ban_info}"}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# 装饰器：DDoS检测
def ddos_protection(action_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if user_id:
                # 更新用户统计
                DDoSDetector.update_user_stats(user_id, action_type)
                
                # 检查DDoS攻击
                if DDoSDetector.check_ddos_attack(user_id):
                    # 获取封禁详细信息
                    ban_info = DDoSDetector.get_user_attack_summary(user_id)
                    unban_time = ban_info['unban_at'] if ban_info else None
                    
                    # 清除用户session
                    session.clear()
                    
                    return jsonify({
                        "error": "ddos_ban",
                        "message": "疑似DDoS攻击，您已被系统封禁24小时",
                        "ban_duration": "24小时",
                        "unban_time": unban_time.isoformat() if unban_time else None,
                        "redirect": True
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ===================== 多轮对话核心工具 =====================
def build_chat_context(session_id: int, max_rounds: int = 10):
    """
    把历史 user/assistant 消息按轮次拼成 OpenAI messages。
    最新 max_rounds 轮，过长会截断。
    """
    rows = execute_query(
        """
        SELECT um.round_id,
               um.message_content      AS user_msg,
               ar.response_content     AS ai_msg
        FROM   user_messages um
        LEFT JOIN ai_responses ar
               ON um.session_id = ar.session_id
              AND um.round_id  = ar.round_id
        WHERE  um.session_id = %s
        ORDER  BY um.round_id
        """,
        (session_id,),
        fetch=True
    )

    # 保留最近 max_rounds 轮
    rows = rows[-max_rounds:]

    context = []
    for r in rows:
        context.append({"role": "user",      "content": r["user_msg"]})
        if r["ai_msg"]:
            context.append({"role": "assistant","content": r["ai_msg"]})
    return context


# ===================== 纯文本多轮对话接口 =====================
@app.route('/chat', methods=['POST'])
@require_auth
@ddos_protection('conversation')
def chat_endpoint():
    """
    前端纯文本对话：
    POST /chat  { "session_id":123, "userQuery":"..." }
    返回 {"assistant":"...", "round_id":n}
    """
    data       = request.json or {}
    session_id = data.get('session_id')
    user_query = data.get('userQuery')
    user_id    = session.get('user_id')

    if not session_id or not user_query:
        return jsonify({"error":"Missing session_id or userQuery"}), 400

    # 取下一轮轮次
    round_id = execute_query(
        "SELECT COALESCE(MAX(round_id),0)+1 AS nxt FROM user_messages WHERE session_id=%s",
        (session_id,), fetch=True
    )[0]['nxt']

    # ---- 写入用户消息
    execute_query(
        "INSERT INTO user_messages (session_id,round_id,message_content) VALUES (%s,%s,%s)",
        (session_id, round_id, user_query)
    )

    # ---- 组装上下文 ---------------------------------
    messages = build_chat_context(session_id)

    # ⭐ 取此次会话对应的处理后图片路径
    img_row = execute_query(
        "SELECT processed_image_path FROM session_results WHERE session_id=%s",
        (session_id,), fetch=True
    )
    if img_row and img_row[0]["processed_image_path"]:
        img_path = img_row[0]["processed_image_path"]
        # 把图片转 base64，再塞到 messages 开头
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        messages.insert(
            0,
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    },
                    {"type": "text", "text": "(已知图片内容，继续对话)"}
                ],
            },
        )

    # 把当前用户问题追加到末尾
    messages.append({"role": "user", "content": user_query})

    # ---- 调大模型
    completion = client.chat.completions.create(
        model="doubao-1.5-vision-lite-250315",
        messages=messages
    )
    assistant_reply = completion.choices[0].message.content

    # ---- 写入 AI 回复
    execute_query(
        "INSERT INTO ai_responses (session_id,round_id,response_content) VALUES (%s,%s,%s)",
        (session_id, round_id, assistant_reply)
    )

    return jsonify({"assistant": assistant_reply, "round_id": round_id})


# ===================== 获取历史记录接口 =====================
@app.route('/history/<int:session_id>', methods=['GET'])
@require_auth
def get_history(session_id):
    """
    GET /history/123  → 返回该会话全部轮次 [{role:"user",content:"..."},{role:"assistant",...},...]
    """
    rows = execute_query(
        """
        SELECT um.round_id,
               um.message_content  AS user_msg,
               ar.response_content AS ai_msg
        FROM   user_messages um
        LEFT JOIN ai_responses ar
               ON um.session_id = ar.session_id
              AND um.round_id  = ar.round_id
        WHERE  um.session_id = %s
        ORDER  BY um.round_id
        """,
        (session_id,),
        fetch=True
    )
    history=[]
    for r in rows:
        history.append({"role":"user",      "content": r["user_msg"]})
        if r["ai_msg"]:
            history.append({"role":"assistant","content": r["ai_msg"]})
    return jsonify(history)


# ========= 用户所有会话列表 =========
@app.route('/history/sessions', methods=['GET'])
@require_auth
def list_user_sessions():
    """返回当前用户的所有会话（含图片路径）"""
    user_id = session.get('user_id')
    rows = execute_query(
        """
        SELECT su.session_id,
               su.created_at,
               sc.detection_category,
               sr.processed_image_path
        FROM   session_users su
        LEFT JOIN session_categories sc
               ON su.session_id = sc.session_id
        LEFT JOIN session_results sr
               ON su.session_id = sr.session_id
        WHERE  su.user_id = %s
        ORDER  BY su.created_at DESC
        """,
        (user_id,),
        fetch=True
    )
    return jsonify(rows)


# ========= 会话详情（你已写过，但保留） =========
# GET /history/<session_id> 路由  —— 之前已在 chat 代码块中实现


# 用户认证接口
@app.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    identity = data.get('identity', 'user')
    invite_code = data.get('inviteCode')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    try:
        if identity == 'admin':
            if not invite_code:
                return jsonify({"error": "Invite code required for admin registration"}), 400
            admin_id = UserManager.create_admin(username, password, invite_code)
            return jsonify({"message": "Admin created successfully", "admin_id": admin_id}), 201
        else:
            user_id = UserManager.create_user(username, password)
            return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    user = UserManager.authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    # 检查封禁状态（仅对普通用户）
    if user['role'] == 'user':
        is_banned, ban_info = UserManager.is_user_banned(user['user_id'])
        if is_banned:
            return jsonify({"error": f"Account banned: {ban_info}"}), 403
    
    session['user_id'] = user['user_id']
    session['username'] = user['username']
    session['role'] = user['role']
    
    return jsonify({
        "message": "Login successful",
        "user_id": user['user_id'],
        "username": user['username'],
        "role": user['role']
    })

@app.route('/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({"message": "Logout successful"})

@app.route('/auth/force-logout', methods=['POST'])
def force_logout():
    """强制退出登录（用于封禁后清理session）"""
    session.clear()
    return jsonify({"message": "Forced logout successful", "redirect_to": "/"})

# 新增路由，用于提供处理后的图片
@app.route('/processed_images/<filename>')
def serve_processed_image(filename):
    return send_from_directory(PROCESSED_DIR, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
@require_auth
@ddos_protection('session')
def detect():
    """处理文件上传、模型预测和结果返回（支持同图复用会话）"""
    if 'source' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['source']
    weight_file = request.form.get('weight_file', '烟雾.pt')
    file_type = request.form.get('fileType', 'image')
    user_id = session.get('user_id')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # ---------- 计算上传文件 SHA256，用于去重 ---------------------
    file_bytes = file.read()
    file_hash  = hashlib.sha256(file_bytes).hexdigest()

    # ---------- 查询是否已有相同图片会话 -------------------------
    reused = execute_query(
        """
        SELECT session_id
        FROM   session_users
        WHERE  user_id   = %s
          AND  file_hash = %s
        """,
        (user_id, file_hash),
        fetch=True
    )

    if reused:
        # —— 曾经上传过同一张图，直接复用旧 session_id ——
        session_id = reused[0]['session_id']
    else:
        # ---------- 生成唯一 session_id -------------------------
        session_id = int(str(int(time.time()))[-6:]) + random.randint(1000, 9999)
        while execute_query(
            "SELECT 1 FROM session_users WHERE session_id=%s",
            (session_id,), fetch=True
        ):
            session_id = int(str(int(time.time()))[-6:]) + random.randint(1000, 9999)

        # ---------- 保存原图到 uploads/ 目录 --------------------
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        source_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(source_path, 'wb') as f:
            f.write(file_bytes)

        # ---------- 写入 session_users（带 file_hash）-----------
        execute_query(
            """
            INSERT INTO session_users (session_id, user_id, image_path, file_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, user_id, source_path, file_hash)
        )

    # ========== 以下逻辑：预测、保存结果、写入其它表 ==========
    # 1. 若之前已经处理过，则直接从 session_results 取 processed_image_path
    processed_row = execute_query(
        "SELECT processed_image_path FROM session_results WHERE session_id=%s",
        (session_id,), fetch=True
    )

    if processed_row:
        permanent_path = processed_row[0]['processed_image_path']
    else:
        # -------- 处理模型 ------------------------------------
        model = YOLO(os.path.join(WEIGHTS_DIR, weight_file))
        if file_type == 'video':
            tmp_path = process_video(model, source_path)
        else:
            tmp_path = process_image(model, source_path)

        # 永久目录
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        permanent_filename = f"processed_{session_id}_{os.path.basename(tmp_path)}"
        permanent_path     = os.path.join(PROCESSED_DIR, permanent_filename)
        shutil.copy2(tmp_path, permanent_path)
        safe_delete(tmp_path)

        # 写入 session_results
        execute_query(
            """
            INSERT INTO session_results (session_id, recognition_result, processed_image_path)
            VALUES (%s, %s, %s)
            """,
            (session_id, f"使用{weight_file}模型识别完成", permanent_path)
        )

        # 写入 session_categories（若首次）
        if not execute_query(
            "SELECT 1 FROM session_categories WHERE session_id=%s",
            (session_id,), fetch=True
        ):
            category_map = {
                '烟雾.pt':'smoke_detection','火焰.pt':'fire_detection','人员落水.pt':'person_drowning',
                '光伏板.pt':'solar_panel_inspection','河道漂浮物.pt':'river_floating_objects',
                '植物生长.pt':'crop_growth_monitoring','人闯红灯.pt':'pedestrian_red_light',
                '车闯红灯.pt':'vehicle_red_light','人员摔倒.pt':'person_fall_detection',
                '景区人流量识别.pt':'scenic_area_crowd'
            }
            execute_query(
                "INSERT INTO session_categories (session_id,detection_category) VALUES (%s,%s)",
                (session_id, category_map.get(weight_file,'smoke_detection'))
            )

    # 返回 URL 友好路径
    return jsonify({
        "result"    : permanent_path.replace("\\", "/"),
        "session_id": session_id,
        "message"   : "图片处理完成（自动复用或新建会话）"
    })
    
    # except Exception as e:
    #     logging.error(f"Error processing file: {str(e)}")
    #     return jsonify({"error": str(e)}), 500

@app.route('/history/<int:session_id>', methods=['DELETE'])
@require_auth
def delete_session(session_id):
    """删除当前用户的一条会话记录"""
    user_id = session.get('user_id')

    # 安全：只允许删除自己的会话
    row = execute_query(
        "SELECT session_id FROM session_users WHERE session_id = %s AND user_id = %s",
        (session_id, user_id),
        fetch=True
    )

    if not row:
        return jsonify({'error': '无权删除该会话'}), 403

    execute_query("DELETE FROM session_users WHERE session_id = %s", (session_id,))
    return jsonify({'success': True})

@app.route('/analyze', methods=['POST'])
@require_auth
@ddos_protection('conversation')
def analyze_endpoint():
    """处理大模型分析请求 - 使用豆包视觉模型分析本地图片。"""
    data = request.json
    user_query = data.get('userQuery', '这是什么？')
    session_id = data.get('session_id')
    user_id = session.get('user_id')

    if not user_query or not session_id:
        return jsonify({"error": "Missing user query or session ID"}), 400

    try:
        # 从数据库获取处理后的图片路径
        result_data = execute_query(
            "SELECT processed_image_path FROM session_results WHERE session_id = %s",
            (session_id,),
            fetch=True
        )
        
        if not result_data or not result_data[0]['processed_image_path']:
            return jsonify({"error": "No processed image found for this session"}), 404
        
        processed_image_path = result_data[0]['processed_image_path']
        
        # 检查文件是否存在
        if not os.path.exists(processed_image_path):
            return jsonify({"error": "Processed image file not found"}), 404
        
        # 将本地图片转换为base64编码，以便发送给豆包模型
        with open(processed_image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 记录用户消息
        if session_id:
            # 获取当前轮次
            round_data = execute_query(
                "SELECT COALESCE(MAX(round_id), 0) + 1 as next_round FROM user_messages WHERE session_id = %s",
                (session_id,),
                fetch=True
            )
            round_id = round_data[0]['next_round'] if round_data else 1
            
            execute_query(
                "INSERT INTO user_messages (session_id, round_id, message_content) VALUES (%s, %s, %s)",
                (session_id, round_id, user_query)
            )
        
        # 使用豆包视觉模型分析本地图片
        response = client.chat.completions.create(
            model="doubao-1.5-vision-lite-250315",  # 豆包视觉模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                        {"type": "text", "text": user_query},
                    ],
                }
            ],
        )

        analysis_result = response.choices[0].message.content
        clean_result = remove_symbols(analysis_result)
        
        # 记录AI响应
        if session_id:
            execute_query(
                "INSERT INTO ai_responses (session_id, round_id, response_content) VALUES (%s, %s, %s)",
                (session_id, round_id, clean_result)
            )
        
        return jsonify({
            "analysis_result": clean_result,
            "processed_image_path": processed_image_path
        })

    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        return jsonify({"error": str(e)}), 500

def process_video(model, source_path):
    """处理视频文件。"""
    cap = cv2.VideoCapture(source_path)
    if not cap.isOpened():
        logging.error(f"Failed to open video file: {source_path}")
        raise ValueError(f"Failed to open video file: {source_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model.predict(frame, save=False, imgsz=640, conf=0.25, iou=0.45)
        if results is None or len(results) == 0:
            logging.error(f"Model prediction failed for frame")
            raise ValueError(f"Model prediction failed for frame")
        annotated_frame = results[0].plot()
        frames.append(annotated_frame)

    cap.release()

    result_file_path = os.path.join(RESULTS_DIR, f'processed_video_{uuid.uuid4()}.mp4')
    processed_video = ImageSequenceClip(frames, fps=fps)
    try:
        processed_video.write_videofile(result_file_path, codec='libx264')
        logging.info(f"Video saved successfully: {result_file_path}")
    except Exception as e:
        logging.error(f"Error saving video: {str(e)}")
        raise e

    return result_file_path

def process_image(model, source_path):
    """处理图片文件。"""
    results = model.predict(source_path, imgsz=640, conf=0.3, iou=0.5)
    annotated_image = results[0].plot()

    result_file_path = os.path.join(RESULTS_DIR, f'processed_image_{uuid.uuid4()}.jpg')

    try:
        cv2.imwrite(result_file_path, annotated_image)
        logging.info(f"Image saved successfully: {result_file_path}")
    except Exception as e:
        logging.error(f"Error saving image: {str(e)}")
        raise e

    return result_file_path

def clean_results_dir():
    """清理 RESULTS_DIR 目录中的文件。"""
    if os.path.exists(RESULTS_DIR):
        try:
            for filename in os.listdir(RESULTS_DIR):
                file_path = os.path.join(RESULTS_DIR, filename)
                safe_delete(file_path)
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"Failed to clean RESULTS_DIR: {str(e)}")

def safe_delete(file_path):
    """安全地删除文件或目录。"""
    if os.path.exists(file_path):
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            logging.info(f"Deleted: {file_path}")
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Reason: {str(e)}")

def remove_symbols(text):
    """移除字符串中的星号和井号。"""
    return text.replace('*', '').replace('#', '')

# 在现有代码基础上添加以下接口

@app.route('/admin/user-stats/<int:user_id>', methods=['GET'])
@require_auth
def get_user_stats(user_id):
    """获取用户攻击统计信息（管理员接口）"""
    try:
        stats = DDoSDetector.get_user_attack_summary(user_id)
        if stats:
            return jsonify(stats)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/reset-stats', methods=['POST'])
@require_auth
def reset_all_stats():
    """重置所有用户攻击统计（管理员接口）"""
    try:
        DDoSDetector.reset_user_stats()
        return jsonify({"message": "All user stats reset successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/banned-users', methods=['GET'])
@require_auth
def get_banned_users():
    """获取所有被封禁用户列表（管理员接口）"""
    try:
        banned_users = execute_query(
            """
            SELECT bu.*, un.username 
            FROM banned_users bu
            JOIN user_names un ON bu.user_id = un.user_id
            WHERE bu.is_active = 1
            ORDER BY bu.banned_at DESC
            """,
            fetch=True
        )
        return jsonify(banned_users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/unban-user/<int:user_id>', methods=['POST'])
@require_auth
def unban_user(user_id):
    """解封用户（管理员接口）"""
    try:
        # 解除封禁
        execute_query(
            "UPDATE banned_users SET is_active = 0 WHERE user_id = %s",
            (user_id,)
        )
        
        # 恢复用户权限
        execute_query(
            "UPDATE permissions SET permission_value = 1 WHERE user_id = %s AND permission_value IS NULL",
            (user_id,)
        )
        
        return jsonify({"message": "User unbanned successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 在文件末尾添加
from scheduler import scheduler

if __name__ == '__main__':
    # 启动定时任务
    scheduler.start()
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        # 停止定时任务
        scheduler.stop()
