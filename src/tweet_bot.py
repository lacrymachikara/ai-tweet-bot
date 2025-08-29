#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI自動ツイートボット - 安定動作版（テキストのみ）
"""

import os
import sys
import logging
import requests
import json
import random
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
import feedparser
import tweepy

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class StableAITweetBot:
    """安定動作版AIツイートボット（テキストのみ）"""
    
    def __init__(self):
        self.setup_credentials()
        self.setup_twitter_api()
    
    def setup_credentials(self):
        """認証情報設定"""
        self.twitter_client_id = os.getenv('TWITTER_CLIENT_ID')
        self.twitter_client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        required_vars = [
            'TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET', 'TWITTER_BEARER_TOKEN'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"必須環境変数が未設定: {missing_vars}")
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    def setup_twitter_api(self):
        """Twitter API設定"""
        try:
            # OAuth 2.0 Client
            self.client = tweepy.Client(
                bearer_token=self.twitter_bearer_token,
                consumer_key=self.twitter_client_id,
                consumer_secret=self.twitter_client_secret,
                access_token=self.twitter_access_token,
                access_token_secret=self.twitter_access_token_secret,
                wait_on_rate_limit=True
            )
            
            logger.info("Twitter API認証設定完了")
            
        except Exception as e:
            logger.error(f"Twitter API設定エラー: {e}")
            raise
    
    def collect_trending_content(self) -> List[str]:
        """バズ記事情報収集"""
        candidates = []
        
        # AI関連トピック
        ai_topics = [
            "Veo3の音声同期技術進歩について調べてた。制作現場での実用性を検証。",
            "DALL-E 3の生成速度向上について調べてた。コスト効率と品質のバランスを分析中。",
            "Stable Diffusion 3の安定性改善について調べてた。ワークフロー最適化での活用を研究。",
            "Claude 3.5の推論精度改善について調べてた。ワークフロー最適化での活用を研究。",
            "Flux AIの画質向上アップデートについて調べてた。VJ制作での新しい可能性を探る。",
            "Geminiの多言語対応強化について調べてた。グローバル展開での活用を検討。",
            "Midjourneyの新機能について調べてた。アーティスト向け機能の充実度が素晴らしい。",
            "Soraの動画生成精度向上について調べてた。映像制作の革新的変化を実感。",
            "ChatGPTの推論能力改善について調べてた。コーディング支援の精度が向上。",
            "LLaMAの軽量化技術について調べてた。エッジデバイス展開の可能性を検証。"
        ]
        
        # RSS収集試行
        rss_feeds = [
            "https://blog.openai.com/rss.xml",
            "https://ai.googleblog.com/feeds/posts/default",
        ]
        
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    entry = random.choice(feed.entries[:3])
                    title = entry.title[:50] + "について調べてた。"
                    candidates.append(title + "新しい発見が続々と。")
                    logger.info(f"RSS収集成功: {entry.title[:30]}...")
            except Exception as e:
                logger.debug(f"RSS取得エラー: {feed_url} - {e}")
        
        candidates.extend(ai_topics)
        logger.info(f"コンテンツ候補収集完了: {len(candidates)}件")
        return candidates
    
    def enhance_content_with_personality(self, content: str) -> str:
        """投稿内容に人間らしさを追加"""
        endings = [
            "\n\n新しい表現手法の開拓を継続する。",
            "\n\n技術進化のスピードに常に驚かされる。", 
            "\n\nまた面白い発見があった。",
            "\n\nクリエイティブの可能性が広がる。",
            "\n\n実用化への期待が高まる。",
            "\n\nAIの進化が止まらない。"
        ]
        
        if len(content) > 100:
            content = content[:100] + "..."
        
        return content + random.choice(endings)
    
    def create_tweet(self, content: str) -> bool:
        """ツイート作成・投稿"""
        try:
            logger.info("ツイート投稿開始...")
            
            response = self.client.create_tweet(text=content)
            
            if response.data:
                logger.info("✅ ツイート投稿成功")
                return True
            else:
                logger.error("❌ ツイート投稿失敗 - レスポンスエラー")
                return False
                
        except tweepy.Unauthorized as e:
            logger.error(f"❌ Twitter認証エラー: {e}")
            logger.info("🔍 Twitter Developer Portalでアプリ権限を確認してください")
            return False
        except tweepy.Forbidden as e:
            logger.error(f"❌ Twitter権限エラー: {e}")
            logger.info("🔍 App permissionsが 'Read and write' に設定されているか確認してください")
            return False
        except Exception as e:
            logger.error(f"❌ ツイート投稿エラー: {e}")
            return False
    
    def run(self):
        """メイン実行"""
        try:
            logger.info("🚀 AI自動ツイートボット開始（安定版）")
            
            # コンテンツ収集
            logger.info("📊 バズ記事情報収集開始...")
            candidates = self.collect_trending_content()
            
            if not candidates:
                logger.error("❌ 投稿候補が見つかりませんでした")
                return False
            
            # ランダム選択・加工
            selected_content = random.choice(candidates)
            final_content = self.enhance_content_with_personality(selected_content)
            
            # ログ出力
            for candidate in candidates[:2]:
                logger.info(f"候補: {candidate[:50]}...")
            
            logger.info(f"最終選択ツイート: {final_content[:50]}...")
            
            # ツイート投稿
            success = self.create_tweet(final_content)
            
            if success:
                logger.info("🎉 AI自動ツイート処理完了")
                
                print("=" * 50)
                print("📱 AI自動ツイート投稿内容 📱")
                print("=" * 50)
                print(final_content)
                print("=" * 50)
                print(f"📅 投稿時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("✅ システム動作確認完了")
                print("=" * 50)
                print("🎉 月300投稿AI自動ツイートシステム稼働中！")
                
                return True
            else:
                logger.error("❌ ツイート投稿に失敗しました")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI自動ツイートボット実行エラー: {e}")
            return False

def main():
    """メイン関数"""
    try:
        bot = StableAITweetBot()
        bot.run()
    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
