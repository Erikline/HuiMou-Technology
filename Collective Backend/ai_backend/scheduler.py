import schedule
import time
import threading
from modules.ddos_detector import DDoSDetector
from modules.user_manager import UserManager
import logging

class TaskScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """启动定时任务"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            logging.info("Task scheduler started")
    
    def stop(self):
        """停止定时任务"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """运行调度器"""
        # 每小时重置用户攻击统计
        schedule.every().hour.do(DDoSDetector.reset_user_stats)
        
        # 每10分钟检查并自动解封到期用户
        schedule.every(10).minutes.do(self._auto_unban_expired_users)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def _auto_unban_expired_users(self):
        """自动解封到期用户"""
        try:
            from datetime import datetime
            from config.database import execute_query
            
            # 查找到期的封禁用户
            expired_bans = execute_query(
                """
                SELECT user_id FROM banned_users 
                WHERE is_active = 1 AND unban_at IS NOT NULL AND unban_at <= NOW()
                """,
                fetch=True
            )
            
            for ban in expired_bans:
                user_id = ban['user_id']
                
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
                
                logging.info(f"Auto-unbanned user {user_id}")
                
        except Exception as e:
            logging.error(f"Error in auto unban: {e}")

# 全局调度器实例
scheduler = TaskScheduler()