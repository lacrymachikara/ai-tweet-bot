import tweepy
import os
import random
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twitter API認証
def authenticate_twitter():
    try:
        auth = tweepy.OAuthHandler(
            os.environ['TWITTER_API_KEY'],
            os.environ['TWITTER_API_SECRET']
        )
        auth.set_access_token(
            os.environ['TWITTER_ACCESS_TOKEN'],
            os.environ['TWITTER_ACCESS_TOKEN_SECRET']
        )
        api = tweepy.API(auth)
        # 認証テスト
        api.verify_credentials()
        logger.info("Twitter API認証成功")
        return api
    except Exception as e:
        logger.error(f"Twitter API認証エラー: {e}")
        raise

# チカラさんの口調パターン
CHIKARA_PATTERNS = [
    "すごい進歩ですね！", "想像以上にすごい", "これは革命的", 
    "知ってました？", "みんなはどう思う？", "教えてください",
    "試してみた結果", "使ってみた感想", "検証してみた",
    "おすすめです", "注目の技術", "最新情報"
]

# AI関連キーワード
AI_TOPICS = [
    "Midjourney V7のパーソナライゼーション機能", 
    "Flux AIの無料プラン",
    "Veo3の8秒動画生成",
    "Kling AIの自然な動き",
    "DALL-E 3の画質向上",
    "Seedanceの音付き動画",
    "AI画像生成の最新トレンド",
    "映像制作でのAI活用",
    "プロンプトエンジニアリング",
    "リアルタイムAI処理"
]

# コンテンツ生成
def generate_tweet_content():
    pattern = random.choice(CHIKARA_PATTERNS)
    topic = random.choice(AI_TOPICS)
    
    templates = [
        f"{topic}、{pattern} みんなはもう試した？",
        f"{topic}について調べてみました。{pattern} どう感じますか？",
        f"最近{topic}が話題ですね。{pattern} 使ってる人いますか？",
        f"{topic}の機能、{pattern} おすすめの使い方あったら教えて",
        f"{topic}を検証した結果、{pattern} みんなの感想聞かせて"
    ]
    
    tweet = random.choice(templates)
    
    # 文字数制限チェック
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    return tweet

# メイン実行
def main():
    try:
        # Twitter API認証
        api = authenticate_twitter()
        
        # ツイート内容生成
        tweet_content = generate_tweet_content()
        
        # ツイート投稿
        api.update_status(tweet_content)
        
        logger.info(f"ツイート投稿成功: {tweet_content}")
        print(f"投稿完了: {tweet_content}")
        
    except Exception as e:
        logger.error(f"エラー発生: {e}")
        print(f"エラー: {e}")

if __name__ == "__main__":
    main()
