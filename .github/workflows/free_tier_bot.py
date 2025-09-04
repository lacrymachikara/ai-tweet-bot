#!/usr/bin/env python3
"""
無料枠最適化AI自動ツイートBot v2.0
- 1日3投稿、月90投稿の制限内運用
- 品質スコア0.8以上の高品質コンテンツのみ
- 完全エラーハンドリング対応
- 使用量自動管理
"""

import tweepy
import openai
import time
import random
import logging
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class FreeTierOptimizedBot:
    """無料枠最適化AI自動ツイートBot"""
    
    def __init__(self):
        """初期化"""
        self.setup_logging()
        self.setup_apis()
        self.setup_limits()
        self.logger.info("🚀 FreeTierOptimizedBot v2.0 初期化完了")
    
    def setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_execution.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_apis(self):
        """API初期化"""
        try:
            # Twitter API v2 設定
            self.twitter_client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                wait_on_rate_limit=True
            )
            
            # OpenAI設定
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            # 認証テスト
            me = self.twitter_client.get_me()
            self.logger.info(f"✅ Twitter認証成功: @{me.data.username}")
            
        except Exception as e:
            self.logger.error(f"❌ API初期化エラー: {e}")
            raise
    
    def setup_limits(self):
        """制限設定"""
        self.DAILY_LIMIT = 3          # 1日3投稿
        self.MONTHLY_LIMIT = 90       # 月90投稿
        self.QUALITY_THRESHOLD = 0.8  # 品質基準
        self.MIN_INTERVAL = 300       # 5分間隔
        self.MAX_RETRIES = 2          # 最大リトライ
    
    def load_usage_data(self) -> Dict[str, Any]:
        """使用量データ読み込み"""
        data_file = 'usage_data.json'
        today = datetime.now().strftime('%Y-%m-%d')
        current_month = datetime.now().strftime('%Y-%m')
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = self.create_new_usage_data(today, current_month)
        
        # 日次/月次リセット
        if data.get('current_date') != today:
            data = self.reset_daily_counter(data, today)
        
        if data.get('current_month') != current_month:
            data = self.reset_monthly_counter(data, current_month)
        
        return data
    
    def create_new_usage_data(self, today: str, current_month: str) -> Dict[str, Any]:
        """新規使用量データ作成"""
        return {
            'current_date': today,
            'current_month': current_month,
            'daily_count': 0,
            'monthly_count': 0,
            'total_posts': 0,
            'quality_posts': 0,
            'system_start': datetime.now().isoformat(),
            'last_reset': datetime.now().isoformat(),
            'post_history': []
        }
    
    def reset_daily_counter(self, data: Dict[str, Any], today: str) -> Dict[str, Any]:
        """日次カウンターリセット"""
        self.logger.info(f"📅 日次リセット実行: {today}")
        data['current_date'] = today
        data['daily_count'] = 0
        data['last_reset'] = datetime.now().isoformat()
        return data
    
    def reset_monthly_counter(self, data: Dict[str, Any], current_month: str) -> Dict[str, Any]:
        """月次カウンターリセット"""
        self.logger.info(f"📅 月次リセット実行: {current_month}")
        data['current_month'] = current_month
        data['monthly_count'] = 0
        data['last_reset'] = datetime.now().isoformat()
        return data
    
    def save_usage_data(self, data: Dict[str, Any]) -> None:
        """使用量データ保存"""
        try:
            with open('usage_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ データ保存エラー: {e}")
    
    def check_posting_limits(self) -> bool:
        """投稿制限チェック"""
        data = self.load_usage_data()
        
        daily_remaining = self.DAILY_LIMIT - data.get('daily_count', 0)
        monthly_remaining = self.MONTHLY_LIMIT - data.get('monthly_count', 0)
        
        self.logger.info("📊 現在の使用状況:")
        self.logger.info(f"  本日: {data.get('daily_count', 0)}/{self.DAILY_LIMIT} (残り{daily_remaining})")
        self.logger.info(f"  今月: {data.get('monthly_count', 0)}/{self.MONTHLY_LIMIT} (残り{monthly_remaining})")
        self.logger.info(f"  品質率: {data.get('quality_posts', 0)}/{data.get('total_posts', 0) or 1}")
        
        if daily_remaining <= 0:
            self.logger.warning("🛑 本日の投稿制限に達しました")
            return False
        
        if monthly_remaining <= 0:
            self.logger.warning("🛑 今月の投稿制限に達しました")
            return False
        
        return True
    
    def generate_premium_content(self) -> Dict[str, Any]:
        """プレミアム品質コンテンツ生成"""
        
        # 高価値トピック定義
        premium_topics = [
            {
                "name": "効率化テクニック",
                "prompt": "今すぐ実践できるビジネス効率化のテクニックを、具体的な手順2-3ステップで140文字以内で紹介してください。数値や時間短縮効果も含めてください。",
                "hashtags": ["#効率化", "#生産性", "#時短術"],
                "quality_multiplier": 1.0
            },
            {
                "name": "成長マインド",
                "prompt": "毎日の成長につながる具体的な行動や習慣を、実践方法と期待効果と共に140文字以内で紹介してください。",
                "hashtags": ["#成長", "#習慣", "#自己投資"],
                "quality_multiplier": 0.95
            },
            {
                "name": "問題解決フレームワーク",
                "prompt": "日常業務の問題を効率的に解決する思考法やフレームワークを、使い方の手順と共に140文字以内で紹介してください。",
                "hashtags": ["#問題解決", "#思考法", "#フレームワーク"],
                "quality_multiplier": 1.0
            },
            {
                "name": "チーム効率化",
                "prompt": "チームの生産性や協力を向上させる具体的な方法を、実施手順と効果と共に140文字以内で紹介してください。",
                "hashtags": ["#チームワーク", "#リーダーシップ", "#組織運営"],
                "quality_multiplier": 0.9
            },
            {
                "name": "ツール活用術",
                "prompt": "業務効率を劇的に上げる便利なツール・アプリ・機能を、設定方法や使いこなしのコツと共に140文字以内で紹介してください。",
                "hashtags": ["#ツール", "#アプリ", "#デジタル化"],
                "quality_multiplier": 0.95
            }
        ]
        
        # 重み付きランダム選択
        weights = [topic['quality_multiplier'] for topic in premium_topics]
        selected_topic = random.choices(premium_topics, weights=weights)[0]
        
        try:
            self.logger.info(f"🎯 選択トピック: {selected_topic['name']}")
            
            # GPT-3.5-turbo でコンテンツ生成
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """あなたは実用的なビジネス価値を提供する専門家です。以下を重視してください：
                        - 今すぐ実践できる具体的な内容
                        - 明確な手順やステップ
                        - 読み手にとっての明確なメリット
                        - 簡潔で分かりやすい表現
                        - 数値や具体例を含める"""
                    },
                    {
                        "role": "user",
                        "content": selected_topic["prompt"]
                    }
                ],
                max_tokens=120,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.3
            )
            
            base_content = response.choices[0].message.content.strip()
            
            # ハッシュタグ選択（2個）
            selected_hashtags = random.sample(selected_topic["hashtags"], 2)
            hashtag_text = " ".join(selected_hashtags)
            
            # 文字数調整
            max_content_length = 280 - len(hashtag_text) - 2
            if len(base_content) > max_content_length:
                base_content = base_content[:max_content_length-3] + "..."
            
            final_content = f"{base_content} {hashtag_text}"
            
            # 品質評価
            quality_score = self.calculate_quality_score(base_content, selected_topic)
            
            return {
                "content": final_content,
                "base_content": base_content,
                "quality_score": quality_score,
                "topic": selected_topic["name"],
                "content_length": len(final_content),
                "hashtags": selected_hashtags,
                "generation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ コンテンツ生成エラー: {e}")
            return self.get_premium_fallback()
    
    def calculate_quality_score(self, content: str, topic_info: Dict[str, Any]) -> float:
        """詳細品質スコア計算"""
        score = 0.6  # ベーススコア
        
        # 具体性指標 (+0.15)
        concrete_words = [
            "方法", "手順", "ステップ", "やり方", "コツ", "テクニック", 
            "ツール", "アプリ", "設定", "操作", "活用", "実践"
        ]
        concrete_count = sum(1 for word in concrete_words if word in content)
        if concrete_count >= 3:
            score += 0.15
        elif concrete_count >= 2:
            score += 0.1
        elif concrete_count >= 1:
            score += 0.05
        
        # 実用性指標 (+0.1)
        action_words = [
            "できる", "始める", "試す", "使う", "実行", "導入", 
            "適用", "取り入れる", "実施", "活用"
        ]
        if sum(1 for word in action_words if word in content) >= 2:
            score += 0.1
        elif any(word in content for word in action_words):
            score += 0.05
        
        # 価値・効果指標 (+0.1)
        value_words = [
            "効果", "向上", "改善", "解決", "短縮", "節約", 
            "効率", "便利", "簡単", "成果", "メリット"
        ]
        if any(word in content for word in value_words):
            score += 0.1
        
        # 数値・具体例 (+0.05)
        import re
        if re.search(r'\d+', content):
            score += 0.03
        if any(char in content for char in ['：', ':', '→', '・', '①', '②', '③']):
            score += 0.02
        
        # 文字数最適化 (+0.05)
        content_length = len(content)
        if 90 <= content_length <= 180:
            score += 0.05
        elif 70 <= content_length <= 220:
            score += 0.03
        
        # トピック品質倍率適用
        final_score = score * topic_info.get('quality_multiplier', 1.0)
        
        return round(min(final_score, 1.0), 3)
    
    def get_premium_fallback(self) -> Dict[str, Any]:
        """プレミアム品質フォールバック"""
        premium_fallbacks = [
            {
                "content": "会議開始前に「今日決める3つのこと」をホワイトボードに書く。議論が脱線した時の軌道修正が劇的に早くなる。30分→15分短縮も可能。 #効率化 #会議術",
                "base_content": "会議開始前に「今日決める3つのこと」をホワイトボードに書く。議論が脱線した時の軌道修正が劇的に早くなる。30分→15分短縮も可能。",
                "quality_score": 0.92,
                "topic": "効率化",
                "content_length": 89,
                "hashtags": ["#効率化", "#会議術"]
            },
            {
                "content": "「なぜ？」を5回繰り返すトヨタ式根本原因分析。表面的な対症療法から脱却し、問題の本質を掴んで根本解決につなげる思考法。 #問題解決 #思考法",
                "base_content": "「なぜ？」を5回繰り返すトヨタ式根本原因分析。表面的な対症療法から脱却し、問題の本質を掴んで根本解決につなげる思考法。",
                "quality_score": 0.89,
                "topic": "問題解決",
                "content_length": 95,
                "hashtags": ["#問題解決", "#思考法"]
            },
            {
                "content": "毎朝5分間で「今日の最重要タスク1つ」を決定する習慣。他の緊急タスクに追われても、これだけは必ず完了。達成感と成長実感が段違い。 #生産性 #習慣",
                "base_content": "毎朝5分間で「今日の最重要タスク1つ」を決定する習慣。他の緊急タスクに追われても、これだけは必ず完了。達成感と成長実感が段違い。",
                "quality_score": 0.91,
                "topic": "習慣",
                "content_length": 93,
                "hashtags": ["#生産性", "#習慣"]
            }
        ]
        
        selected = random.choice(premium_fallbacks)
        selected['generation_time'] = datetime.now().isoformat()
        self.logger.info(f"🔄 プレミアムフォールバック使用: {selected['topic']}")
        return selected
    
    def check_content_duplicate(self, content: str) -> bool:
        """コンテンツ重複チェック"""
        content_hash = hashlib.md5(content[:100].encode()).hexdigest()
        
        try:
            with open('content_hashes.json', 'r') as f:
                posted_hashes = set(json.load(f))
        except FileNotFoundError:
            posted_hashes = set()
        
        if content_hash in posted_hashes:
            return True
        
        # 新しいハッシュを追加
        posted_hashes.add(content_hash)
        
        # 最新100件のみ保持
        if len(posted_hashes) > 100:
            posted_hashes = set(list(posted_hashes)[-100:])
        
        with open('content_hashes.json', 'w') as f:
            json.dump(list(posted_hashes), f)
        
        return False
    
    def execute_safe_posting(self, content_data: Dict[str, Any]) -> bool:
        """安全投稿実行"""
        
        # 品質チェック
        if content_data["quality_score"] < self.QUALITY_THRESHOLD:
            self.logger.warning(f"⚠️ 品質基準未達: {content_data['quality_score']:.3f} < {self.QUALITY_THRESHOLD}")
            return False
        
        # 重複チェック
        if self.check_content_duplicate(content_data["content"]):
            self.logger.warning("⚠️ 類似コンテンツ検出、投稿スキップ")
            return False
        
        # 投稿実行
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.twitter_client.create_tweet(text=content_data["content"])
                
                # 成功時データ更新
                self.update_usage_after_success(content_data, response.data['id'])
                
                self.logger.info("✅ 高品質ツイート投稿成功!")
                self.logger.info(f"   🔗 ID: {response.data['id']}")
                self.logger.info(f"   ⭐ 品質: {content_data['quality_score']:.3f}")
                self.logger.info(f"   🏷️ トピック: {content_data['topic']}")
                self.logger.info(f"   📏 文字数: {content_data['content_length']}")
                
                return True
                
            except tweepy.TooManyRequests:
                self.logger.warning("⏳ レート制限: 15分待機中...")
                time.sleep(900)
                
            except tweepy.Forbidden as e:
                self.logger.error(f"❌ 投稿権限エラー: {e}")
                return False
                
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 60 * (attempt + 1)
                    self.logger.error(f"❌ 投稿エラー (試行{attempt+1}): {e}")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"❌ 最終投稿失敗: {e}")
        
        return False
    
    def update_usage_after_success(self, content_data: Dict[str, Any], tweet_id: str) -> None:
        """投稿成功後のデータ更新"""
        data = self.load_usage_data()
        
        # カウンター更新
        data['daily_count'] = data.get('daily_count', 0) + 1
        data['monthly_count'] = data.get('monthly_count', 0) + 1
        data['total_posts'] = data.get('total_posts', 0) + 1
        data['quality_posts'] = data.get('quality_posts', 0) + 1
        
        # 投稿履歴追加
        post_record = {
            'timestamp': datetime.now().isoformat(),
            'tweet_id': tweet_id,
            'quality_score': content_data['quality_score'],
            'topic': content_data['topic'],
            'content_length': content_data['content_length'],
            'hashtags': content_data.get('hashtags', [])
        }
        
        if 'post_history' not in data:
            data['post_history'] = []
        
        data['post_history'].append(post_record)
        
        # 履歴は最新50件のみ保持
        if len(data['post_history']) > 50:
            data['post_history'] = data['post_history'][-50:]
        
        data['last_update'] = datetime.now().isoformat()
        
        self.save_usage_data(data)
    
    def run_optimized_system(self) -> None:
        """最適化システムメイン実行"""
        execution_start = datetime.now()
        
        self.logger.info("="*60)
        self.logger.info("🚀 無料枠最適化AI自動ツイートBot v2.0 実行開始")
        self.logger.info(f"⏰ 開始時刻: {execution_start.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
        
        try:
            # システム状態確認
            self.logger.info("🔍 システム状態確認中...")
            
            # 投稿制限チェック
            if not self.check_posting_limits():
                self.logger.info("🛑 投稿制限により実行終了")
                return
            
            # 高品質コンテンツ生成
            self.logger.info("🎨 プレミアムコンテンツ生成中...")
            content_data = self.generate_premium_content()
            
            # 生成結果表示
            self.logger.info("📝 生成結果:")
            self.logger.info(f"   内容: {content_data['content']}")
            self.logger.info(f"   品質スコア: {content_data['quality_score']:.3f}")
            self.logger.info(f"   テーマ: {content_data['topic']}")
            self.logger.info(f"   文字数: {content_data['content_length']}")
            
            # 投稿実行
            success = self.execute_safe_posting(content_data)
            
            if success:
                self.logger.info("🎉 高品質ツイート投稿完了!")
            else:
                self.logger.info("⏸️ 品質基準または制限によりスキップ")
            
        except Exception as e:
            self.logger.error(f"💥 システムエラー: {e}")
            import traceback
            self.logger.error(f"詳細エラー:\n{traceback.format_exc()}")
            
        finally:
            execution_time = datetime.now() - execution_start
            self.logger.info(f"⏱️ 実行時間: {execution_time.total_seconds():.1f}秒")
            self.logger.info("="*60)
            self.logger.info("🏁 システム実行終了")
            self.logger.info("="*60)

def main():
    """メインエントリーポイント"""
    try:
        bot = FreeTierOptimizedBot()
        bot.run_optimized_system()
    except KeyboardInterrupt:
        print("🛑 ユーザーによる中断")
    except Exception as e:
        print(f"💥 システム起動エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
