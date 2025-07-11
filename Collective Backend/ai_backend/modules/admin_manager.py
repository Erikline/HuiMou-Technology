from datetime import datetime, timedelta
from config.database import execute_query
import logging

class AdminManager:
    @staticmethod
    def get_banned_users():
        """获取封禁用户列表"""
        try:
            banned_users = execute_query(
                """
                SELECT bu.*, un.username
                FROM banned_users bu
                LEFT JOIN user_names un ON bu.user_id = un.user_id
                WHERE bu.is_active = 1
                ORDER BY bu.banned_at DESC
                """,
                fetch=True
            )
            return banned_users or []
        except Exception as e:
            logging.error(f"Error getting banned users: {e}")
            return []
    
    @staticmethod
    def ban_user(user_id, reason='manual_ban', duration=1440):
        """封禁用户
        Args:
            user_id: 用户ID
            reason: 封禁原因
            duration: 封禁时长（分钟）
        """
        try:
            if not user_id:
                raise ValueError("User ID is required")
            
            # 检查用户是否存在
            user_exists = execute_query(
                "SELECT 1 FROM user_names WHERE user_id = %s",
                (user_id,),
                fetch=True
            )
            
            if not user_exists:
                raise ValueError("User not found")
            
            # 检查是否已经有任何封禁记录（不管是否活跃）
            existing_ban = execute_query(
                "SELECT banned_id, is_active FROM banned_users WHERE user_id = %s",
                (user_id,),
                fetch=True
            )
            
            unban_time = datetime.now() + timedelta(minutes=duration)
            
            if existing_ban:
                # 更新现有封禁记录（无论之前是否活跃）
                execute_query(
                    """
                    UPDATE banned_users 
                    SET ban_reason = %s, ban_duration = %s, unban_at = %s, 
                        banned_at = NOW(), is_active = 1
                    WHERE user_id = %s
                    """,
                    (reason, duration, unban_time, user_id)
                )
            else:
                # 创建新的封禁记录
                execute_query(
                    """
                    INSERT INTO banned_users 
                    (user_id, ban_reason, ban_duration, unban_at, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                    """,
                    (user_id, reason, duration, unban_time)
                )
            
            # 将用户权限设为NULL（封禁状态）
            execute_query(
                "UPDATE permissions SET permission_value = NULL WHERE user_id = %s",
                (user_id,)
            )
            
            logging.info(f"User {user_id} banned successfully. Reason: {reason}, Duration: {duration} minutes")
            
        except Exception as e:
            logging.error(f"Error banning user {user_id}: {e}")
            raise
    
    @staticmethod
    def unban_user(user_id):
        """解封用户"""
        try:
            if not user_id:
                raise ValueError("User ID is required")
            
            # 检查是否被封禁
            banned_record = execute_query(
                "SELECT banned_id FROM banned_users WHERE user_id = %s AND is_active = 1",
                (user_id,),
                fetch=True
            )
            
            if not banned_record:
                raise ValueError("User is not currently banned")
            
            # 更新封禁记录为非活跃状态
            execute_query(
                "UPDATE banned_users SET is_active = 0 WHERE user_id = %s AND is_active = 1",
                (user_id,)
            )
            
            # 恢复用户权限
            execute_query(
                "UPDATE permissions SET permission_value = 1 WHERE user_id = %s",
                (user_id,)
            )
            
            logging.info(f"User {user_id} unbanned successfully")
            
        except Exception as e:
            logging.error(f"Error unbanning user {user_id}: {e}")
            raise