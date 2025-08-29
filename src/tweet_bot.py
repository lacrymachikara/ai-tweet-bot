import tweepy
import os
import random
import logging
import requests
from datetime import datetime, timezone
import feedparser
import json
import time
from bs4 import BeautifulSoup
import re

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AITweetBot:
    def __init__(self):
        self.api = self.authenticate_twitter()
        
    def authenticate_twitter(self):
        try:
            auth = tweepy.OAuthHandler(
                os.environ['TWITTER_API_KEY'],
                os.environ['TWITTER_API_SECRET']
            )
            auth.set_access_token(
                os.environ['TWITTER_ACCESS_TOKEN'],
                os.environ['TWITTER_ACCESS_TOKEN_SECRET']
            )
            api = tweepy.API(auth, wait_on_rate_limit=True)
            api.verify_credentials()
            logger.info("Twitter API認証成功")
            return api
        except Exception as e:
            logger.error(f"Twitter API認証エラー: {e}")
            raise

    def get_viral_ai_content(self):
        """海外でバズってるAI記事・情報を収集"""
        try:
            viral_content = []
            
            # Reddit AI関連の人気投稿
            subreddits = ['MachineLearning', 'artificial', 'OpenAI', 'MediaSynthesis']
            
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"
                    headers = {'User-Agent': 'AI-Tweet-Bot/1.0'}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for post in data['data']['children']:
                            post_data = post['data']
                            if post_data['ups'] > 500:  # 高エンゲージメント
                                viral_content.append({
                                    'title': post_data['title'],
                                    'score': post_data['ups'],
                                    'source': 'reddit',
                                    'url': post_data['url'],
                                    'subreddit': subreddit
                                })
                except Exception as e:
                    logger.warning(f"Reddit {subreddit} エラー: {e}")
                    continue
                    
                time.sleep(1)
                
            return sorted(viral_content, key=lambda x: x['score'], reverse=True)[:10]
        
        except Exception as e:
            logger.error(f"バズコンテンツ取得エラー: {e}")
            return []

    def generate_natural_buzz_tweet(self, content_info):
        """人間らしい自然なバズ記事ツイート生成"""
        
        # 自然な導入
        intro_patterns = [
            "海外でこの記事がめちゃくちゃバズってる！",
            "この海外の記事、すごい話題になってる",
            "海外AI界隈でこれが大注目されてる",
            "向こうでバズってるこの記事見て驚いた",
            "海外のAI業界でこれが話題沸騰中",
            "海外でこれがトレンド入りしてる",
            "この記事、海外で大反響呼んでる"
        ]
        
        # AI技術への感想パターン
        reaction_patterns = [
            "想像以上の精度で驚いた",
            "技術の進歩が早すぎる", 
            "これは制作現場を変える",
            "実用レベルに到達してる",
            "映像制作の概念が変わりそう",
            "クオリティが段違いになってる",
            "プロ仕様の機能が無料とか信じられない",
            "これまでの常識を覆す技術"
        ]
        
        # 具体的な活用シーン
        application_patterns = [
            "映像制作での活用方法を考えてる",
            "クライアントワークでも使えそう",
            "制作時間の短縮に直結しそう",
            "VJ映像制作に応用できるかも",
            "リアルタイム処理での可能性を感じる",
            "アイデア出しから完成まで一貫してできそう",
            "予算の少ないプロジェクトでも高品質が実現できる"
        ]
        
        # 自然な終わり方（質問なし）
        ending_patterns = [
            "実際使ったらまた報告する",
            "これは期待大だな", 
            "早く試してみたい",
            "制作現場で活用してみる予定",
            "また新しい発見があったらシェアする",
            "これで作業効率が変わりそう",
            "技術の進歩が本当にすごい",
            "導入を本格的に検討してる",
            "クリエイティブの可能性が広がる"
        ]
        
        # タイトルからAI関連キーワード抽出
        title = content_info['title'].lower()
        ai_tools = ['gpt', 'chatgpt', 'openai', 'midjourney', 'dall-e', 'stable diffusion', 
                   'flux', 'claude', 'gemini', 'sora', 'kling', 'veo', 'runway']
        
        mentioned_tool = None
        for tool in ai_tools:
            if tool in title:
                mentioned_tool = tool.upper()
                break
        
        # 投稿生成
        intro = random.choice(intro_patterns)
        
        # メイン内容（タイトル要約）
        if mentioned_tool:
            main_content = f"{mentioned_tool}の新機能、{random.choice(reaction_patterns).replace('これは', 'これ')}。"
        else:
            main_content = f"AI画像生成技術、{random.choice(reaction_patterns)}。"
        
        # 活用への言及
        application = random.choice(application_patterns)
        
        # 終わり方
        ending = random.choice(ending_patterns)
        
        # 全体構成
        tweet_content = f"{intro}\n\n{main_content}\n{application}。\n\n{ending}。"
        
        # 文字数調整（280文字制限）
        if len(tweet_content) > 280:
            # 長い場合は短縮版
            short_content = f"{intro}\n\n{main_content}\n\n{ending}。"
            if len(short_content) > 280:
                tweet_content = short_content[:277] + "..."
            else:
                tweet_content = short_content
        
        return tweet_content

    def generate_fallback_tweet(self):
        """バズ記事がない時のフォールバック投稿"""
        
        ai_topics = [
            "Midjourney V7のパーソナライゼーション機能",
            "Flux AIの無料高品質生成", 
            "Veo3の音付き8秒動画生成",
            "Kling AIの自然な動き表現",
            "Claude 3.5の推論能力向上",
            "DALL-E 3の画質改善",
            "Stable Diffusion 3の精度向上"
        ]
        
        personal_comments = [
            "制作現場での活用を検討してる",
            "実際に使ってみて驚いた",
            "クライアントワークでも使えそう", 
            "映像制作の効率が格段に上がる",
            "VJ映像制作での可能性を感じる"
        ]
        
        endings = [
            "また新しい発見があったら報告する",
            "導入して本格活用してみる予定",
            "技術の進歩に毎日驚かされる",
            "クリエイティブの幅が確実に広がってる"
        ]
        
        topic = random.choice(ai_topics)
        comment = random.choice(personal_comments)
        ending = random.choice(endings)
        
        return f"{topic}について調べてた。\n{comment}。\n\n{ending}。"

    def avoid_duplicate_content(self):
        """重複投稿チェック"""
        try:
            recent_tweets = self.api.user_timeline(count=5, tweet_mode='extended')
            recent_content = [tweet.full_text for tweet in recent_tweets]
            return recent_content
        except Exception as e:
            logger.warning(f"重複チェックエラー: {e}")
            return []

    def similarity_check(self, text1, text2):
        """テキスト類似度チェック"""
        try:
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0
        except:
            return 0

    def generate_tweet(self):
        """メイン投稿生成"""
        try:
            logger.info("バズ記事情報収集中...")
            
            # バズ記事取得
            viral_content = self.get_viral_ai_content()
            
            # 重複チェック
            recent_tweets = self.avoid_duplicate_content()
            
            # 投稿候補生成
            tweet_candidates = []
            
            # バズ記事ベース投稿
            for content in viral_content[:5]:
                tweet = self.generate_natural_buzz_tweet(content)
                
                # 重複チェック
                is_duplicate = False
                for recent in recent_tweets:
                    if self.similarity_check(tweet, recent) > 0.6:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    tweet_candidates.append(tweet)
            
            # フォールバック投稿も追加
            for _ in range(3):
                fallback_tweet = self.generate_fallback_tweet()
                
                is_duplicate = False
                for recent in recent_tweets:
                    if self.similarity_check(fallback_tweet, recent) > 0.6:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    tweet_candidates.append(fallback_tweet)
            
            # ランダム選択
            if tweet_candidates:
                selected_tweet = random.choice(tweet_candidates)
                logger.info(f"選択されたツイート: {selected_tweet[:50]}...")
                return selected_tweet
            
            # 最終フォールバック
            return self.generate_fallback_tweet()
            
        except Exception as e:
            logger.error(f"ツイート生成エラー: {e}")
            return "AI技術の進歩、日々感じることが多い。制作現場での活用方法を常に模索してる。"

    def post_tweet(self):
        """ツイート投稿実行"""
        try:
            tweet_content = self.generate_tweet()
            
            if not tweet_content:
                logger.error("ツイートコンテンツの生成に失敗")
                return False
                
            # 投稿実行
            self.api.update_status(tweet_content)
            
            logger.info(f"ツイート投稿成功: {tweet_content}")
            print(f"✅ 投稿完了: {tweet_content}")
            
            return True
            
        except Exception as e:
            logger.error(f"ツイート投稿エラー: {e}")
            return False

def main():
    """メイン実行関数"""
    try:
        logger.info("AI自動ツイートボット開始")
        
        bot = AITweetBot()
        success = bot.post_tweet()
        
        if success:
            logger.info("AI自動ツイート実行完了")
        else:
            logger.error("AI自動ツイート実行失敗")
            
    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")

if __name__ == "__main__":
    main()
