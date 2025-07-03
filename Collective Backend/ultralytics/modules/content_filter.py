import time

from config.database import execute_query
from typing import Dict, List


class DatabaseContentFilter:
    def __init__(self):
        self.cached_keywords = None
        self.last_update = 0

    def _refresh_cache(self):
        """从数据库刷新敏感词缓存"""
        results = execute_query(
            "SELECT keyword, category FROM sensitive_keywords",
            fetch=True
        )
        self.cached_keywords = {}
        for item in results:
            self.cached_keywords.setdefault(item['category'], []).append(item['keyword'])
        self.last_update = time.time()

    def check_text(self, text: str) -> Dict[str, bool]:
        """检查文本是否包含敏感词"""
        if not self.cached_keywords or time.time() - self.last_update > 3600:  # 1小时缓存
            self._refresh_cache()

        return {
            'has_porn': any(kw in text for kw in self.cached_keywords.get('porn', [])),
            'has_violence': any(kw in text for kw in self.cached_keywords.get('violence', [])),
            'has_politics': any(kw in text for kw in self.cached_keywords.get('politics', []))
        }


# 全局实例
content_filter = DatabaseContentFilter()
