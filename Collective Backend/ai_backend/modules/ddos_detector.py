import time
from datetime import datetime, timedelta
from ai_backend.config.database import execute_query
import logging

class DDoSDetector:
    # DDoS检测阈值配置
    SESSION_THRESHOLD = 10  # 时间窗口内最大会话数
    CONVERSATION_THRESHOLD = 10  # 时间窗口内最大对话数
    TIME_WINDOW = 1  # 时间窗口（分钟）
    BAN_DURATION = 1440  # 封禁时长（分钟，24小时）
    
    @staticmethod
    def update_user_stats(user_id, action_type):
        """更新用户攻击统计"""
        try:
            # 获取当前统计数据
            stats = execute_query(
                "SELECT session_count, conversation_count, delta_time_window FROM user_attack_stats WHERE user_id = %s",
                (user_id,),
                fetch=True
            )
            
            if not stats:
                # 如果没有记录，创建新记录
                execute_query(
                    "INSERT INTO user_attack_stats (user_id, delta_time_window) VALUES (%s, %s)",
                    (user_id, DDoSDetector.TIME_WINDOW)
                )
                session_count = 0
                conversation_count = 0
            else:
                session_count = stats[0]['session_count']
                conversation_count = stats[0]['conversation_count']
            
            # 根据动作类型更新计数
            if action_type == 'session':
                session_count += 1
            elif action_type == 'conversation':
                conversation_count += 1
            
            # 更新统计数据
            execute_query(
                "UPDATE user_attack_stats SET session_count = %s, conversation_count = %s WHERE user_id = %s",
                (session_count, conversation_count, user_id)
            )
            
            return session_count, conversation_count
        except Exception as e:
            logging.error(f"Error updating user stats: {e}")
            return 0, 0
    
    @staticmethod
    def check_ddos_attack(user_id):
        """检测DDoS攻击 - 基于用户id+总攻击次数（delta范围内）"""
        try:
            # 获取用户统计数据
            stats = execute_query(
                "SELECT session_count, conversation_count, is_ddos, delta_time_window FROM user_attack_stats WHERE user_id = %s",
                (user_id,),
                fetch=True
            )
            
            if not stats:
                return False
            
            session_count = stats[0]['session_count']
            conversation_count = stats[0]['conversation_count']
            delta_time_window = stats[0]['delta_time_window']
            
            # 计算总攻击次数（在delta时间窗口内）
            total_attacks = session_count + conversation_count
            
            # 动态阈值计算：基于时间窗口调整阈值
            adjusted_session_threshold = DDoSDetector.SESSION_THRESHOLD * delta_time_window
            adjusted_conversation_threshold = DDoSDetector.CONVERSATION_THRESHOLD * delta_time_window
            adjusted_total_threshold = adjusted_session_threshold + adjusted_conversation_threshold
            
            # 检查是否超过阈值
            is_ddos = (session_count > adjusted_session_threshold or 
                      conversation_count > adjusted_conversation_threshold or
                      total_attacks > adjusted_total_threshold)
            
            if is_ddos:
                # 更新DDoS标记
                execute_query(
                    "UPDATE user_attack_stats SET is_ddos = 1 WHERE user_id = %s",
                    (user_id,)
                )
                
                # 封禁用户
                DDoSDetector.ban_user_for_ddos(user_id, total_attacks)
                
                logging.warning(f"DDoS attack detected for user {user_id}. Total attacks: {total_attacks} in {delta_time_window} minute(s)")
                return True
            
            return False
        except Exception as e:
            logging.error(f"Error checking DDoS attack: {e}")
            return False
    
    @staticmethod
    def ban_user_for_ddos(user_id, attack_count):
        """因DDoS攻击封禁用户 - 根据攻击次数动态调整封禁时长"""
        try:
            # 计算封禁时长（根据攻击次数调整）
            if attack_count > 200:
                ban_duration = 20160  # 14天
            elif attack_count > 100:
                ban_duration = 10080  # 7天
            elif attack_count > 50:
                ban_duration = 4320   # 3天
            else:
                ban_duration = DDoSDetector.BAN_DURATION  # 1天
            
            unban_time = datetime.now() + timedelta(minutes=ban_duration)
            
            # 检查是否已经被封禁
            existing_ban = execute_query(
                "SELECT banned_id FROM banned_users WHERE user_id = %s AND is_active = 1",
                (user_id,),
                fetch=True
            )
            
            if existing_ban:
                # 更新现有封禁记录
                execute_query(
                    """
                    UPDATE banned_users 
                    SET ban_duration = %s, unban_at = %s, ban_description = %s
                    WHERE user_id = %s AND is_active = 1
                    """,
                    (ban_duration, unban_time, f"DDoS攻击检测，攻击次数: {attack_count}", user_id)
                )
            else:
                # 创建新的封禁记录
                execute_query(
                    """
                    INSERT INTO banned_users 
                    (user_id, ban_reason, ban_description, ban_duration, unban_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, 'ddos_attack', f"DDoS攻击检测，攻击次数: {attack_count}", ban_duration, unban_time)
                )
            
            # 将用户权限设为NULL（封禁状态）
            execute_query(
                "UPDATE permissions SET permission_value = NULL WHERE user_id = %s",
                (user_id,)
            )
            
            logging.info(f"User {user_id} banned for DDoS attack. Duration: {ban_duration} minutes, Attack count: {attack_count}")
        except Exception as e:
            logging.error(f"Error banning user for DDoS: {e}")
    
    @staticmethod
    def reset_user_stats():
        """重置所有用户的攻击统计（定时任务）"""
        try:
            execute_query(
                "UPDATE user_attack_stats SET session_count = 0, conversation_count = 0, is_ddos = 0"
            )
            logging.info("User attack stats reset successfully")
        except Exception as e:
            logging.error(f"Error resetting user stats: {e}")
    
    @staticmethod
    def get_user_attack_summary(user_id):
        """获取用户攻击统计摘要"""
        try:
            stats = execute_query(
                """
                SELECT uas.*, bu.ban_reason, bu.ban_description, bu.unban_at, bu.is_active as is_banned
                FROM user_attack_stats uas
                LEFT JOIN banned_users bu ON uas.user_id = bu.user_id AND bu.is_active = 1
                WHERE uas.user_id = %s
                """,
                (user_id,),
                fetch=True
            )
            return stats[0] if stats else None
        except Exception as e:
            logging.error(f"Error getting user attack summary: {e}")
            return None