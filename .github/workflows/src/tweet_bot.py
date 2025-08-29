#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tweepy
import requests
import random
import json
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AITweetBot:
      def __init__(self):
                # Twitter API認証
                self.api_key = os.environ.get('TWITTER_API_KEY')
                self.api_secret = os.environ.get('TWITTER_API_SECRET')
                self.access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
                self.access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

        # Twitter APIクライアント初期化
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )

        # チカラさんの口調パターン
                self.chikara_patterns = [
                    "AIの画像生成技術、また進歩してるんですね！{}って知ってました？",
                    "最新のAI映像生成、これすごくないですか？{}みたいな感じで！",
                    "AI技術の発展スピード、本当に驚きです。{}について皆さんはどう思いますか？",
                    "今日見つけたAI情報！{}なんですが、これ実用化されたらどんな変化が起きそうですか？",
                    "AIの進化が止まりませんね。{}みたいな技術、もう日常になりそうです！",
                    "気になるAI技術を発見！{}って、もう未来の話じゃないんですね",
                    "AI画像・映像生成の世界、毎日新しい発見があります。{}について調べてみたんですが...",
                    "最近のAI技術、本当にすごいです！{}なんて、一年前は想像もできませんでした",
                ]

        # AI関連キーワード
                self.ai_keywords = [
                    "Stable Diffusion", "Midjourney", "DALL-E", "ChatGPT", "Runway ML",
                    "AI画像生成", "AI映像生成", "機械学習", "ディープラーニング", "GAN",
                    "Diffusion Model", "Text-to-Image", "Text-to-Video", "AI Art",
                    "クリエイティブAI", "生成AI", "OpenAI", "Anthropic", "Google AI"
                ]

      def get_ai_news_topics(self):
                """AI関連の最新トピックを生成"""
                topics = [
                    "新しいAI画像生成モデルのリリース",
                    "AI映像生成技術の商用化",
                    "クリエイティブ業界でのAI活用事例",
                    "AI生成コンテンツの著作権問題",
                    "個人クリエイターのAI活用術",
                    "企業のAIツール導入事例",
                    "AI技術の民主化進展",
                    "次世代AI生成技術の予測",
                    "AIとアートの融合事例",
                    "AI生成コンテンツの品質向上"
                ]
                return random.choice(topics)

      def generate_tweet_content(self):
                """チカラさんの口調でツイート内容を生成"""
                topic = self.get_ai_news_topics()
                pattern = random.choice(self.chikara_patterns)
                keyword = random.choice(self.ai_keywords)

        # 現在時刻に応じた挨拶
                current_hour = datetime.now().hour
                if 6 <= current_hour < 12:
                              greeting = "おはようございます！"
elif 12 <= current_hour < 18:
            greeting = "こんにちは！"
else:
            greeting = "こんばんは！"

        # ツイート内容生成
          main_content = pattern.format(topic)

        # ハッシュタグ追加
        hashtags = f"\n\n#{keyword.replace(' ', '')} #AI画像生成 #AI映像生成 #生成AI #クリエイティブAI"

        tweet_content = f"{greeting}\n\n{main_content}{hashtags}"

        # 文字数制限チェック（280文字以内）
        if len(tweet_content) > 280:
                      tweet_content = tweet_content[:277] + "..."

        return tweet_content

    def post_tweet(self):
              """ツイートを投稿"""
              try:
                            tweet_content = self.generate_tweet_content()

            # ツイート投稿
                  response = self.client.create_tweet(text=tweet_content)

            logger.info(f"ツイート投稿成功: {tweet_content}")
            logger.info(f"Tweet ID: {response.data['id']}")

            return True

except Exception as e:
            logger.error(f"ツイート投稿エラー: {e}")
            return False

    def run(self):
              """メイン実行関数"""
        logger.info("AI Tweet Bot 開始")

        # 認証情報チェック
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                      logger.error("Twitter API認証情報が不足しています")
                      return False

        # ツイート投稿実行
        success = self.post_tweet()

        if success:
                      logger.info("AI Tweet Bot 正常終了")
else:
              logger.error("AI Tweet Bot エラー終了")

        return success

if __name__ == "__main__":
      bot = AITweetBot()
      bot.run()
