import hashlib
import time
from datetime import datetime, timedelta
from ai_backend.config.database import execute_query
import logging

class UserManager:
    @staticmethod
    def hash_password(password):
        """使用SHA256加密密码"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_invite_code(invite_code):
        """验证管理员邀请码"""
        try:
            result = execute_query(
                "SELECT invite_code FROM admin_invite_codes WHERE invite_code = %s",
                (invite_code,),
                fetch=True
            )
            return len(result) > 0
        except Exception as e:
            logging.error(f"Error verifying invite code: {e}")
            return False
    
    @staticmethod
    def create_admin(username, password, invite_code):
        """创建管理员用户"""
        try:
            # 验证邀请码
            if not UserManager.verify_invite_code(invite_code):
                raise Exception("Invalid invite code")
            
            # 插入管理员名
            execute_query(
                "INSERT INTO admin_names (admin_name) VALUES (%s)",
                (username,)
            )
            
            # 获取管理员ID
            admin_data = execute_query(
                "SELECT admin_id FROM admin_names WHERE admin_name = %s",
                (username,),
                fetch=True
            )
            
            if not admin_data:
                raise Exception("Failed to create admin")
            
            admin_id = admin_data[0]['admin_id']
            
            # 插入密码
            hashed_password = UserManager.hash_password(password)
            execute_query(
                "INSERT INTO admin_passwords (admin_id, password) VALUES (%s, %s)",
                (admin_id, hashed_password)
            )
            
            # 设置管理员权限
            admin_permissions = ['manage', 'view_ALLdiagram']
            for perm in admin_permissions:
                execute_query(
                    "INSERT INTO permissions (admin_id, permission_value, permission_type) VALUES (%s, %s, %s)",
                    (admin_id, 1, perm)
                )
            
            return admin_id
        except Exception as e:
            logging.error(f"Error creating admin: {e}")
            raise
    
    @staticmethod
    def create_user(username, password):
        """创建新用户"""
        try:
            # 插入用户名
            execute_query(
                "INSERT INTO user_names (username) VALUES (%s)",
                (username,)
            )
            
            # 获取用户ID
            user_data = execute_query(
                "SELECT user_id FROM user_names WHERE username = %s",
                (username,),
                fetch=True
            )
            
            if not user_data:
                raise Exception("Failed to create user")
            
            user_id = user_data[0]['user_id']
            
            # 插入密码
            hashed_password = UserManager.hash_password(password)
            execute_query(
                "INSERT INTO user_passwords (user_id, password) VALUES (%s, %s)",
                (user_id, hashed_password)
            )
            
            # 初始化安全统计
            execute_query(
                "INSERT INTO user_security_stats (user_id) VALUES (%s)",
                (user_id,)
            )
            
            # 初始化攻击统计
            execute_query(
                "INSERT INTO user_attack_stats (user_id) VALUES (%s)",
                (user_id,)
            )
            
            # 设置默认权限
            permissions = ['upload', 'chat']
            for perm in permissions:
                execute_query(
                    "INSERT INTO permissions (user_id, permission_value, permission_type) VALUES (%s, %s, %s)",
                    (user_id, 1, perm)
                )
            
            return user_id
        except Exception as e:
            import traceback
            traceback.print_exc()  # 输出完整堆栈
            logging.error(f"Error creating user: {e}")
            raise

    @staticmethod
    def authenticate_user(username, password):
        """用户认证"""
        try:
            hashed_password = UserManager.hash_password(password)
            
            # 先尝试普通用户认证
            user_data = execute_query(
                """
                SELECT un.user_id, un.username, 'user' as role
                FROM user_names un
                JOIN user_passwords up ON un.user_id = up.user_id
                WHERE un.username = %s AND up.password = %s
                """,
                (username, hashed_password),
                fetch=True
            )
            
            if user_data:
                return user_data[0]
            
            # 再尝试管理员认证
            admin_data = execute_query(
                """
                SELECT an.admin_id as user_id, an.admin_name as username, 'admin' as role
                FROM admin_names an
                JOIN admin_passwords ap ON an.admin_id = ap.admin_id
                WHERE an.admin_name = %s AND ap.password = %s
                """,
                (username, hashed_password),
                fetch=True
            )
            
            if admin_data:
                return admin_data[0]
            
            return None
        except Exception as e:
            logging.error(f"Error authenticating user: {e}")
            return None
    
    @staticmethod
    def is_user_banned(user_id):
        """检查用户是否被封禁"""
        try:
            banned_data = execute_query(
                """
                SELECT ban_duration, banned_at, unban_at, is_active
                FROM banned_users 
                WHERE user_id = %s AND is_active = 1
                """,
                (user_id,),
                fetch=True
            )
            
            if not banned_data:
                return False, None
            
            ban_info = banned_data[0]
            
            # 检查是否为永久封禁
            if ban_info['ban_duration'] is None:
                return True, "永久封禁"
            
            # 检查临时封禁是否过期
            if ban_info['unban_at'] and datetime.now() > ban_info['unban_at']:
                # 解除封禁
                execute_query(
                    "UPDATE banned_users SET is_active = 0 WHERE user_id = %s",
                    (user_id,)
                )
                return False, None
            
            return True, f"封禁至 {ban_info['unban_at']}"
        except Exception as e:
            logging.error(f"Error checking ban status: {e}")
            return False, None