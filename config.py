"""
システム設定管理
"""
from datetime import datetime

# 無料枠制限設定
FREE_TIER_LIMITS = {
    'daily_posts': 3,
    'monthly_posts': 90,
    'quality_threshold': 0.8,
    'min_interval_seconds': 300
}

# ツイート品質設定
QUALITY_CONFIG = {
    'min_content_length': 50,
    'max_content_length': 200,
    'required_concrete_words': 1,
    'required_action_words': 1
}

# ログ設定
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'bot_execution.log'
}

# システムメタデータ
SYSTEM_INFO = {
    'version': '2.0.0',
    'name': 'FreeTierOptimizedBot',
    'description': '無料枠最適化AI自動ツイートBot',
    'last_updated': datetime.now().isoformat()
}
