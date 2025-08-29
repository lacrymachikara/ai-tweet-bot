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

    def get_reddit_ai_trends(self):
        """RedditからAI関連のトレンド情報を取得"""
        try:
            subreddits = [
                'MachineLearning',
                'artificial', 
                'MediaSynthesis',
                'StableDiffusion',
                'ChatGPT'
            ]
            
            trends = []
            for subreddit in subreddits:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                    headers = {'User-Agent': 'AI-Tweet-Bot/1.0'}
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        for post in data['data']['children']:
                            post_data = post['data']
                            if post_data['ups'] > 100:  # 人気投稿のみ
                                trends.append({
                                    'title': post_data['title'],
                                    'score': post_data['ups'],
                                    'subreddit': subreddit,
                                    'url': post_data['url']
                                })
                except Exception as e:
                    logger.warning(f"Reddit {subreddit} 取得エラー: {e}")
                    continue
                
                time.sleep(1)  # レート制限対策
                
            return sorted(trends, key=lambda x: x['score'], reverse=True)[:5]
        
        except Exception as e:
            logger.error(f"Reddit情報取得エラー: {e}")
            return []

    def get_ai_news_feeds(self):
        """AIニュースサイトからRSS情報を取得"""
        try:
            rss_feeds = [
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://rss.cnn.com/rss/edition.rss',
                'https://techcrunch.com/feed/'
            ]
            
            news_items = []
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:3]:
                        if any(keyword in entry.title.lower() for keyword in 
                              ['ai', 'artificial intelligence', 'machine learning', 
                               'chatgpt', 'openai', 'midjourney', 'stable diffusion']):
                            news_items.append({
                                'title': entry.title,
                                'published': entry.get('published', ''),
                                'link': entry.link
                            })
                except Exception as e:
                    logger.warning(f"RSS feed {feed_url} エラー: {e}")
                    continue
                    
            return news_items[:5]
        
        except Exception as e:
            logger.error(f"AIニュース取得エラー: {e}")
            return []

    def get_github_ai_trends(self):
        """GitHubからトレンドAIプロジェクトを取得"""
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'artificial-intelligence OR machine-learning OR stable-diffusion',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                projects = []
                for repo in data['items']:
                    projects.append({
                        'name': repo['name'],
                        'description': repo['description'],
                        'stars': repo['stargazers_count'],
                        'language': repo.get('language', 'Unknown')
                    })
                return projects
            
            return []
        
        except Exception as e:
            logger.error(f"GitHub トレンド取得エラー: {e}")
            return []

    def extract_ai_keywords(self, text):
        """テキストからAI関連キーワードを抽出"""
        ai_keywords = [
            'GPT', 'ChatGPT', 'OpenAI', 'Claude', 'Gemini',
            'Midjourney', 'DALL-E', 'Stable Diffusion', 'Flux',
            'Veo3', 'Kling', 'Seedance', 'Pika', 'Dreamina',
            'LLM', 'Transformer', 'Neural Network', 'Deep Learning',
            'Computer Vision', 'NLP', 'Generative AI'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in ai_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
                
        return found_keywords

    def generate_chikara_style_content(self, source_info):
        """最新情報をチカラさんの口調で生成"""
        
        # チカラさんの口調パターン
        intro_patterns = [
            "最新のAI情報チェックしてたら",
            "AI界隈で話題になってる",
            "今朝見つけたAIニュースで",
            "AIトレンド調べてたら",
            "気になるAI情報発見！"
        ]
        
        reaction_patterns = [
            "これすごくない？",
            "想像以上にすごい",
            "これは革命的だと思う",
            "技術の進歩が早すぎる",
            "もう未来が来てる感じ"
        ]
        
        question_patterns = [
            "みんなはどう思う？",
            "使ってみた人いる？",
            "これについてどう感じる？",
            "みんなの意見聞かせて",
            "感想教えて"
        ]
        
        # コンテンツ生成
        intro = random.choice(intro_patterns)
        reaction = random.choice(reaction_patterns)
        question = random.choice(question_patterns)
        
        # 情報源に応じた内容生成
        if source_info['type'] == 'reddit':
            content = f"{intro} {source_info['title'][:50]}... {reaction} {question}"
        elif source_info['type'] == 'news':
            content = f"{intro} {source_info['title'][:50]}... {reaction} {question}"
        elif source_info['type'] == 'github':
            content = f"GitHubで{source_info['name']}っていうAIプロジェクトが話題！{reaction} {question}"
        else:
            # フォールバック用の固定コンテンツ
            topics = [
                "Midjourney V7のパーソナライゼーション機能",
                "Flux AIの無料高品質生成",
                "Veo3の音付き8秒動画",
                "Kling AIの自然な動き生成",
                "AI画像生成の最新進歩"
            ]
            topic = random.choice(topics)
            content = f"{topic}について調べてみた。{reaction} {question}"
        
        # 文字数制限（280文字以内）
        if len(content) > 280:
            content = content[:277] + "..."
            
        return content

    def avoid_duplicate_content(self):
        """重複投稿チェック（簡易版）"""
        try:
            # 自分の最新5ツイートを取得
            recent_tweets = self.api.user_timeline(count=5, tweet_mode='extended')
            recent_content = [tweet.full_text for tweet in recent_tweets]
            return recent_content
        except Exception as e:
            logger.warning(f"重複チェックエラー: {e}")
            return []

    def calculate_engagement_score(self, content):
        """エンゲージメントスコア計算"""
        score = 0
        
        # 質問形式
        if '？' in content or '?' in content:
            score += 10
            
        # 感情表現
        emotion_words = ['すごい', '革命的', '未来', '驚き', 'ヤバイ']
        for word in emotion_words:
            if word in content:
                score += 5
                
        # AI関連キーワード
        ai_keywords = self.extract_ai_keywords(content)
        score += len(ai_keywords) * 3
        
        # 文字数（140-200文字が理想）
        length = len(content)
        if 140 <= length <= 200:
            score += 15
        elif 100 <= length <= 250:
            score += 10
            
        return score

    def generate_tweet(self):
        """メイン投稿生成メソッド"""
        try:
            # 最新情報収集
            logger.info("最新AI情報を収集中...")
            
            reddit_trends = self.get_reddit_ai_trends()
            ai_news = self.get_ai_news_feeds()
            github_projects = self.get_github_ai_trends()
            
            # 情報ソース選択
            all_sources = []
            
            for trend in reddit_trends[:3]:
                all_sources.append({
                    'type': 'reddit',
                    'title': trend['title'],
                    'score': trend['score']
                })
                
            for news in ai_news[:3]:
                all_sources.append({
                    'type': 'news', 
                    'title': news['title']
                })
                
            for project in github_projects[:2]:
                all_sources.append({
                    'type': 'github',
                    'name': project['name'],
                    'description': project['description']
                })
            
            # コンテンツ候補生成
            content_candidates = []
            
            if all_sources:
                for source in all_sources[:5]:  # 上位5つのソース
                    content = self.generate_chikara_style_content(source)
                    engagement_score = self.calculate_engagement_score(content)
                    
                    content_candidates.append({
                        'content': content,
                        'score': engagement_score,
                        'source': source
                    })
            
            # フォールバック用固定コンテンツ
            fallback_sources = [
                {'type': 'fallback', 'title': 'AI画像生成技術の最新動向'},
                {'type': 'fallback', 'title': 'AI動画生成ツールの比較'},
                {'type': 'fallback', 'title': 'プロンプトエンジニアリングのコツ'}
            ]
            
            for fallback in fallback_sources:
                content = self.generate_chikara_style_content(fallback)
                engagement_score = self.calculate_engagement_score(content)
                content_candidates.append({
                    'content': content,
                    'score': engagement_score,
                    'source': fallback
                })
            
            # 重複チェック
            recent_tweets = self.avoid_duplicate_content()
            
            # 最適なコンテンツ選択
            best_content = None
            for candidate in sorted(content_candidates, key=lambda x: x['score'], reverse=True):
                content = candidate['content']
                
                # 重複チェック
                is_duplicate = False
                for recent in recent_tweets:
                    if self.similarity_check(content, recent) > 0.7:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    best_content = content
                    logger.info(f"選択されたコンテンツ (スコア: {candidate['score']}): {content[:50]}...")
                    break
            
            return best_content or content_candidates[0]['content']  # フェイルセーフ
            
        except Exception as e:
            logger.error(f"ツイート生成エラー: {e}")
            
            # エラー時のフォールバック
            fallback_tweets = [
                "AI技術の進歩、日々感じることが多い。みんなは最近どんなAIツール使ってる？",
                "画像生成AIの精度向上がすごい。制作現場でも活用の幅が広がってる。みんなの使い方教えて",
                "動画生成AIも実用レベルになってきた。映像制作の未来が楽しみ。どう思う？"
            ]
            return random.choice(fallback_tweets)

    def similarity_check(self, text1, text2):
        """テキスト類似度チェック（簡易版）"""
        try:
            # 単語レベルでの類似度計算
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0
        except:
            return 0

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
            
        except tweepy.TooManyRequests:
            logger.warning("Twitter API制限に達しました")
            return False
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
