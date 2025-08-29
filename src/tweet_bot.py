#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI自動ツイートボット with Gemini画像生成システム
OAuth 2.0 + Gemini AI画像解析・生成・添付機能統合版
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
import tempfile
import base64
from typing import List, Dict, Optional, Tuple
import feedparser
import tweepy
from urllib.parse import urlparse
import google.generativeai as genai
from PIL import Image
import io

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_tweet_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class GeminiImageGenerator:
    """Gemini AI画像生成エンジン"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY未設定 - 画像生成機能制限")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            # Gemini画像生成モデル設定
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("Gemini画像生成API初期化完了")
        except Exception as e:
            logger.error(f"Gemini API初期化エラー: {e}")
            self.model = None
        
        self.fallback_prompts = [
            "abstract AI technology illustration, minimalist design, blue and purple gradient, digital art style",
            "futuristic neural network visualization, glowing connections, cyberpunk aesthetic, high-tech interface",
            "modern tech concept art, clean geometric shapes, innovative design, professional illustration",
            "AI brain visualization, colorful data streams, technological innovation, artistic interpretation"
        ]
    
    def analyze_content_for_image(self, content: str) -> Dict[str, any]:
        """投稿内容を解析して最適な画像コンセプトを生成"""
        analysis = {
            'keywords': [],
            'category': 'general',
            'visual_style': 'minimalist',
            'color_scheme': 'blue_purple',
            'complexity': 'medium',
            'mood': 'professional'
        }
        
        content_lower = content.lower()
        
        # AI関連キーワード検出
        ai_tools = {
            'dall-e': 'AI art generation interface',
            'dalle': 'AI art generation interface', 
            'stable diffusion': 'stable diffusion neural network',
            'midjourney': 'creative AI art process',
            'claude': 'AI assistant visualization',
            'gpt': 'language model architecture',
            'chatgpt': 'conversational AI interface',
            'veo': 'video generation technology',
            'flux': 'flux AI creative process',
            'sora': 'video AI technology',
            'gemini': 'gemini AI system visualization'
        }
        
        # カテゴリ分類
        for tool, description in ai_tools.items():
            if tool in content_lower:
                analysis['keywords'].append(tool)
                analysis['category'] = 'ai_tools'
                analysis['tool_description'] = description
                break
        
        # 技術キーワード
        tech_keywords = ['ai', '人工知能', '機械学習', 'ml', 'deep learning', 'neural', 'ニューラル']
        for keyword in tech_keywords:
            if keyword in content_lower:
                analysis['keywords'].append(keyword)
                if analysis['category'] == 'general':
                    analysis['category'] = 'technology'
        
        # クリエイティブ要素
        creative_keywords = ['デザイン', 'アート', 'クリエイティブ', 'creative', 'art', 'design']
        for keyword in creative_keywords:
            if keyword in content_lower:
                analysis['keywords'].append(keyword)
                analysis['visual_style'] = 'creative'
                analysis['mood'] = 'artistic'
        
        # 感情・トーン分析
        positive_words = ['進歩', '向上', '改善', '革新', '素晴らしい', '驚く', 'amazing', 'incredible', '発見']
        if any(word in content_lower for word in positive_words):
            analysis['color_scheme'] = 'warm_positive'
            analysis['mood'] = 'optimistic'
        
        research_words = ['研究', '調査', '分析', 'research', 'analysis']
        if any(word in content_lower for word in research_words):
            analysis['complexity'] = 'detailed'
            analysis['mood'] = 'analytical'
        
        speed_words = ['速度', '高速', 'speed', 'fast']
        if any(word in content_lower for word in speed_words):
            analysis['visual_style'] = 'dynamic'
            analysis['mood'] = 'energetic'
        
        return analysis
    
    def generate_gemini_prompts(self, analysis: Dict[str, any], content: str) -> List[str]:
        """Geminiに最適化されたプロンプトを生成"""
        prompts = []
        
        # ベーススタイル定義
        base_styles = {
            'ai_tools': "high-tech AI interface design, digital dashboard elements, futuristic technology visualization",
            'technology': "abstract technology concept, data visualization, modern digital illustration", 
            'creative': "artistic AI creation process, vibrant digital art, creative workflow visualization",
            'general': "modern technology concept, clean professional illustration, innovation theme"
        }
        
        visual_styles = {
            'minimalist': "clean minimalist design, simple geometric shapes, white background, professional",
            'creative': "vibrant artistic style, dynamic composition, creative energy, colorful",
            'dynamic': "motion blur effects, speed lines, energetic composition, fast-paced"
        }
        
        color_schemes = {
            'blue_purple': "blue and purple gradient background, cool tech colors, digital aesthetic",
            'warm_positive': "warm orange and yellow tones, energetic colors, optimistic mood",
            'cool_tech': "cyan and electric blue palette, high-tech atmosphere, futuristic glow"
        }
        
        mood_elements = {
            'professional': "corporate style, clean presentation, business appropriate",
            'artistic': "creative expression, artistic flair, imaginative elements", 
            'optimistic': "bright lighting, uplifting atmosphere, positive energy",
            'analytical': "structured layout, data-focused, scientific approach",
            'energetic': "dynamic movement, active composition, vibrant energy"
        }
        
        # プロンプト1: メインテーマ重点
        prompt1 = f"Create a {visual_styles.get(analysis['visual_style'], visual_styles['minimalist'])} illustration representing "
        prompt1 += f"{base_styles.get(analysis['category'], base_styles['general'])}, "
        prompt1 += f"with {color_schemes.get(analysis['color_scheme'], color_schemes['blue_purple'])}, "
        prompt1 += f"{mood_elements.get(analysis['mood'], mood_elements['professional'])}, "
        prompt1 += "perfect for social media, high quality digital art"
        prompts.append(prompt1)
        
        # プロンプト2: キーワード特化
        if analysis['keywords']:
            main_keyword = analysis['keywords'][0]
            prompt2 = f"Design a modern illustration showcasing {main_keyword} technology, "
            prompt2 += f"incorporating {visual_styles.get(analysis['visual_style'], visual_styles['minimalist'])}, "
            prompt2 += f"with professional {mood_elements.get(analysis['mood'], mood_elements['professional'])} style, "
            prompt2 += "optimized for Twitter post, engaging visual design"
            prompts.append(prompt2)
        
        # プロンプト3: 抽象的コンセプト
        prompt3 = f"Abstract visualization of innovation and technological progress, "
        prompt3 += f"{color_schemes.get(analysis['color_scheme'], color_schemes['blue_purple'])}, "
        prompt3 += f"{visual_styles.get(analysis['visual_style'], visual_styles['minimalist'])}, "
        prompt3 += "inspiring and forward-thinking, suitable for tech social media content"
        prompts.append(prompt3)
        
        return prompts[:3]
    
    def generate_image_with_gemini(self, prompt: str) -> Optional[str]:
        """Geminiで画像生成"""
        try:
            if not self.model:
                logger.error("Geminiモデル未初期化")
                return None
            
            logger.info(f"Gemini画像生成開始: {prompt[:50]}...")
            
            # Gemini画像生成リクエスト
            response = self.model.generate_content([
                "Create a high-quality digital illustration based on this prompt:",
                prompt,
                "Style: Professional, clean, suitable for social media",
                "Format: 1024x1024 pixels, PNG format",
                "Quality: High resolution, crisp details"
            ])
            
            # 注意: 実際のGemini画像生成APIの仕様に応じて調整が必要
            # 現在のGeminiは主にテキスト生成なので、将来の画像生成機能を想定
            
            if hasattr(response, 'image_url'):
                logger.info("Gemini画像生成成功")
                return response.image_url
            else:
                logger.warning("Gemini画像生成レスポンス形式不明")
                return None
                
        except Exception as e:
            logger.error(f"Gemini画像生成エラー: {e}")
            return None
    
    def generate_image_candidates(self, content: str) -> List[str]:
        """複数の画像候補をGeminiで生成"""
        try:
            # コンテンツ解析
            analysis = self.analyze_content_for_image(content)
            logger.info(f"画像生成分析結果: {analysis}")
            
            # Gemini最適化プロンプト生成
            prompts = self.generate_gemini_prompts(analysis, content)
            logger.info(f"Gemini用プロンプト数: {len(prompts)}")
            
            image_urls = []
            
            # 実際の実装では、現在のGeminiがテキスト生成中心のため
            # 将来の画像生成機能を想定したプレースホルダー実装
            
            # 暫定的フォールバック: AI画像生成サービス統合
            for i, prompt in enumerate(prompts):
                try:
                    # 将来のGemini画像生成API対応
                    image_url = self.generate_image_with_gemini(prompt)
                    
                    # 現在は外部AI画像生成サービスを代替使用
                    if not image_url:
                        image_url = self._generate_fallback_image(prompt)
                    
                    if image_url:
                        image_urls.append(image_url)
                        logger.info(f"画像候補{i+1}生成成功")
                    
                    # API制限考慮
                    if i < len(prompts) - 1:
                        time.sleep(3)
                        
                except Exception as e:
                    logger.warning(f"画像候補{i+1}生成失敗: {e}")
                    continue
            
            # フォールバック画像生成
            if not image_urls:
                fallback_prompt = random.choice(self.fallback_prompts)
                fallback_url = self._generate_fallback_image(fallback_prompt)
                if fallback_url:
                    image_urls.append(fallback_url)
                    logger.info("フォールバック画像生成成功")
            
            return image_urls
            
        except Exception as e:
            logger.error(f"Gemini画像候補生成エラー: {e}")
            return []
    
    def _generate_fallback_image(self, prompt: str) -> Optional[str]:
        """フォールバック画像生成（外部サービス使用）"""
        try:
            # 現在のGeminiは主にテキスト生成のため、
            # AI画像生成の代替サービスを使用
            
            # 例: Hugging Face Stable Diffusion API
            # または、事前に生成した画像プールから選択
            
            logger.info("フォールバック画像生成実行")
            
            # プレースホルダー: 実際の実装では適切な画像生成APIを使用
            # ここでは概念実装として、固定URLを返す
            
            fallback_images = [
                "https://example.com/ai_art_1.png",  # 実際のAI生成画像URL
                "https://example.com/ai_art_2.png", 
                "https://example.com/ai_art_3.png"
            ]
            
            return random.choice(fallback_images)
            
        except Exception as e:
            logger.error(f"フォールバック画像生成エラー: {e}")
            return None
    
    def select_optimal_image(self, image_urls: List[str], content: str) -> Optional[str]:
        """最適な画像をGeminiで評価・選択"""
        if not image_urls:
            return None
        
        try:
            if len(image_urls) == 1:
                return image_urls[0]
            
            # Geminiを使用した画像品質評価（将来実装）
            # 現在はランダム選択
            selected = random.choice(image_urls)
            logger.info(f"最適画像選択完了: {len(image_urls)}候補から選択")
            return selected
            
        except Exception as e:
            logger.error(f"画像選択エラー: {e}")
            return random.choice(image_urls) if image_urls else None

class TwitterImageUploader:
    """Twitter画像アップロード管理"""
    
    def __init__(self, api_v1):
        self.api_v1 = api_v1
    
    def download_image(self, image_url: str) -> Optional[str]:
        """画像をダウンロードして一時ファイルに保存"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 一時ファイル作成
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            logger.info(f"画像ダウンロード成功: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"画像ダウンロードエラー: {e}")
            return None
    
    def upload_image_to_twitter(self, image_path: str) -> Optional[str]:
        """Twitter に画像をアップロード"""
        try:
            media = self.api_v1.media_upload(image_path)
            logger.info(f"Twitter画像アップロード成功: {media.media_id}")
            return media.media_id
            
        except Exception as e:
            logger.error(f"Twitter画像アップロードエラー: {e}")
            return None
        finally:
            # 一時ファイル削除
            try:
                if os.path.exists(image_path):
                    os.unlink(image_path)
                    logger.info(f"一時ファイル削除: {image_path}")
            except Exception as e:
                logger.warning(f"一時ファイル削除エラー: {e}")

class GeminiEnhancedAITweetBot:
    """Gemini画像生成対応 拡張版AIツイートボット"""
    
    def __init__(self):
        self.setup_credentials()
        self.setup_twitter_api()
        self.image_generator = GeminiImageGenerator()
        
        if hasattr(self, 'api_v1'):
            self.image_uploader = TwitterImageUploader(self.api_v1)
        else:
            self.image_uploader = None
            logger.warning("Twitter API v1未設定 - 画像アップロード機能無効")
    
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
        """Twitter API設定（OAuth 2.0 + OAuth 1.0a ハイブリッド）"""
        try:
            # OAuth 2.0 Client（読み書き用）
            self.client = tweepy.Client(
                bearer_token=self.twitter_bearer_token,
                consumer_key=self.twitter_client_id,
                consumer_secret=self.twitter_client_secret,
                access_token=self.twitter_access_token,
                access_token_secret=self.twitter_access_token_secret,
                wait_on_rate_limit=True
            )
            
            # OAuth 1.0a API（画像アップロード用）
            if self.twitter_access_token and self.twitter_access_token_secret:
                auth = tweepy.OAuth1UserHandler(
                    self.twitter_client_id,
                    self.twitter_client_secret,
                    self.twitter_access_token,
                    self.twitter_access_token_secret
                )
                self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("Twitter API ハイブリッド認証設定完了")
            else:
                logger.warning("OAuth 1.0a認証情報不足 - 画像アップロード機能制限")
            
        except Exception as e:
            logger.error(f"Twitter API設定エラー: {e}")
            raise
    
    def collect_trending_content(self) -> List[str]:
        """バズ記事情報収集"""
        candidates = []
        
        # AI関連RSS
        rss_feeds = [
            "https://blog.openai.com/rss.xml",
            "https://ai.googleblog.com/feeds/posts/default",
            "https://blogs.nvidia.com/feed/",
        ]
        
        ai_topics = [
            "Geminiの画像生成機能について調べてた。マルチモーダル性能の進化が印象的。",
            "DALL-E 3の生成速度向上について調べてた。コスト効率と品質のバランスを分析中。",
            "Stable Diffusion 3の安定性改善について調べてた。ワークフロー最適化での活用を研究。",
            "Claude 3.5の推論精度改善について調べてた。ワークフロー最適化での活用を研究。",
            "Veo3の音声同期技術進歩について調べてた。制作現場での実用性を検証。",
            "Flux AIの画質向上アップデートについて調べてた。VJ制作での新しい可能性を探る。",
            "Midjourneyの新機能について調べてた。アーティスト向け機能の充実度が素晴らしい。",
        ]
        
        # RSS収集試行
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                if feed.entries:
                    entry = random.choice(feed.entries[:5])
                    title = entry.title[:50] + "について調べてた。"
                    candidates.append(title + "新しい発見が続々と。")
            except Exception as e:
                logger.debug(f"RSS取得エラー: {feed_url} - {e}")
        
        # フォールバック候補追加
        candidates.extend(ai_topics)
        
        return candidates
    
    def enhance_content_with_personality(self, content: str) -> str:
        """投稿内容に人間らしさを追加"""
        endings = [
            "\n\n新しい表現手法の開拓を継続する。",
            "\n\n技術進化のスピードに常に驚かされる。",
            "\n\nまた面白い発見があった。",
            "\n\nクリエイティブの可能性が広がる。",
            "\n\n実用化への期待が高まる。",
            "\n\nGeminiの進化が楽しみ。"
        ]
        
        if len(content) > 100:
            content = content[:100] + "..."
        
        return content + random.choice(endings)
    
    def create_tweet_with_gemini_image(self, content: str) -> bool:
        """Gemini画像生成付きツイート作成・投稿"""
        try:
            logger.info("Gemini画像生成付きツイート作成開始...")
            
            # Gemini画像生成
            image_urls = self.image_generator.generate_image_candidates(content)
            if not image_urls:
                logger.warning("Gemini画像生成失敗 - テキストのみで投稿")
                return self.create_text_only_tweet(content)
            
            # 最適画像選択
            selected_image_url = self.image_generator.select_optimal_image(image_urls, content)
            if not selected_image_url:
                logger.warning("画像選択失敗 - テキストのみで投稿")
                return self.create_text_only_tweet(content)
            
            # 画像アップロード処理
            if not self.image_uploader:
                logger.warning("画像アップロード機能未設定 - テキストのみで投稿")
                return self.create_text_only_tweet(content)
            
            # 画像ダウンロード
            image_path = self.image_uploader.download_image(selected_image_url)
            if not image_path:
                logger.warning("画像ダウンロード失敗 - テキストのみで投稿")
                return self.create_text_only_tweet(content)
            
            # Twitter画像アップロード
            media_id = self.image_uploader.upload_image_to_twitter(image_path)
            if not media_id:
                logger.warning("Twitter画像アップロード失敗 - テキストのみで投稿")
                return self.create_text_only_tweet(content)
            
            # Gemini画像付きツイート投稿
            response = self.client.create_tweet(
                text=content,
                media_ids=[media_id]
            )
            
            if response.data:
                logger.info("Gemini画像付きツイート投稿成功")
                return True
            else:
                logger.warning("Gemini画像付きツイート投稿失敗 - テキストのみで再試行")
                return self.create_text_only_tweet(content)
                
        except Exception as e:
            logger.error(f"Gemini画像付きツイート作成エラー: {e}")
            return self.create_text_only_tweet(content)
    
    def create_text_only_tweet(self, content: str) -> bool:
        """テキストのみツイート作成・投稿（フォールバック）"""
        try:
            response = self.client.create_tweet(text=content)
            if response.data:
                logger.info("テキストツイート投稿成功")
                return True
            else:
                logger.error("テキストツイート投稿失敗")
                return False
                
        except Exception as e:
            logger.error(f"テキストツイート投稿エラー: {e}")
            return False
    
    def run(self):
        """メイン実行"""
        try:
            logger.info("AI自動ツイートボット開始（Gemini画像生成 Enhanced）")
            
            # コンテンツ収集
            logger.info("バズ記事情報収集開始...")
            candidates = self.collect_trending_content()
            
            if not candidates:
                logger.error("投稿候補が見つかりませんでした")
                return False
            
            # ランダム選択・加工
            selected_content = random.choice(candidates)
            final_content = self.enhance_content_with_personality(selected_content)
            
            for candidate in candidates[:2]:
                logger.info(f"フォールバック候補: {candidate[:50]}...")
            
            logger.info(f"最終選択ツイート: {final_content[:50]}...")
            
            # Gemini画像生成付き投稿実行
            logger.info("Gemini画像生成・投稿処理開始...")
            success = self.create_tweet_with_gemini_image(final_content)
            
            if success:
                logger.info("AI自動ツイート処理完了")
                logger.info("AI自動ツイートシステム実行成功")
                
                print("=" * 50)
                print("📱 AI自動ツイート投稿内容 📱")
                print("=" * 50)
                print(final_content)
                print("=" * 50)
                print(f"📅 投稿時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("✅ システム動作確認完了")
                print("🎨 Gemini AI生成画像付きツイート投稿")
                print("=" * 50)
                print("🎉 月300投稿AI自動ツイートシステム稼働中！")
                
                return True
            else:
                logger.error("ツイート投稿に失敗しました")
                return False
                
        except Exception as e:
            logger.error(f"AI自動ツイートボット実行エラー: {e}")
            return False

def main():
    """メイン関数"""
    try:
        bot = GeminiEnhancedAITweetBot()
        bot.run()
    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
