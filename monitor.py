#!/usr/bin/env python3
"""
無料枠最適化Botシステム監視ツール
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

class SystemMonitor:
    """システム監視クラス"""
    
    def __init__(self):
        self.data_file = 'usage_data.json'
        self.log_file = 'bot_execution.log'
    
    def load_system_data(self) -> Dict[str, Any]:
        """システムデータ読み込み"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def generate_comprehensive_report(self) -> str:
        """包括的レポート生成"""
        data = self.load_system_data()
        current_time = datetime.now()
        
        report_lines = [
            "=" * 60,
            "🤖 無料枠最適化AI自動ツイートBot - 詳細レポート",
            "=" * 60,
            f"📅 レポート生成時刻: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        if not data:
            report_lines.append("❌ システムデータが見つかりません")
            return "\n".join(report_lines)
        
        # 基本統計
        daily_count = data.get('daily_count', 0)
        monthly_count = data.get('monthly_count', 0)
        total_posts = data.get('total_posts', 0)
        quality_posts = data.get('quality_posts', 0)
        
        report_lines.extend([
            "📊 基本使用統計:",
            f"  本日投稿数: {daily_count}/3 ({(daily_count/3)*100:.1f}%)",
            f"  今月投稿数: {monthly_count}/90 ({(monthly_count/90)*100:.1f}%)",
            f"  総投稿数: {total_posts}",
            f"  高品質投稿数: {quality_posts}",
            f"  品質率: {(quality_posts/max(total_posts,1))*100:.1f}%",
            ""
        ])
        
        # 制限状況
        daily_remaining = 3 - daily_count
        monthly_remaining = 90 - monthly_count
        
        report_lines.extend([
            "🎯 制限・残量状況:",
            f"  本日残り投稿: {daily_remaining}",
            f"  今月残り投稿: {monthly_remaining}",
            f"  無料枠使用率: {(monthly_count/90)*100:.1f}%",
            f"  推定月末到達投稿数: {monthly_count + (daily_count * 25)}" if daily_count > 0 else "  推定月末到達投稿数: 計算不可",
            ""
        ])
        
        # 品質分析
        if 'post_history' in data and data['post_history']:
            recent_posts = data['post_history'][-10:]  # 直近10投稿
            avg_quality = sum(post.get('quality_score', 0) for post in recent_posts) / len(recent_posts)
            topics = [post.get('topic', 'Unknown') for post in recent_posts]
            topic_counts = {topic: topics.count(topic) for topic in set(topics)}
            
            report_lines.extend([
                "📈 品質分析 (直近10投稿):",
                f"  平均品質スコア: {avg_quality:.3f}",
                f"  品質基準達成率: 100%" if avg_quality >= 0.8 else f"  品質基準達成率: {(avg_quality/0.8)*100:.1f}%",
                "  トピック分布:"
            ])
            
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"    {topic}: {count}回")
            
            report_lines.append("")
        
        # 最新投稿情報
        if 'last_update' in data:
            last_update = datetime.fromisoformat(data['last_update'].replace('Z', '+00:00'))
            time_since_last = current_time - last_update.replace(tzinfo=None)
            
            report_lines.extend([
                "🕐 最新アクティビティ:",
                f"  最終更新: {data['last_update']}",
                f"  経過時間: {time_since_last}",
            ])
            
            if 'post_history' in data and data['post_history']:
                latest_post = data['post_history'][-1]
                report_lines.extend([
                    f"  最新投稿ID: {latest_post.get('tweet_id', 'N/A')}",
                    f"  品質スコア: {latest_post.get('quality_score', 'N/A')}",
                    f"  トピック: {latest_post.get('topic', 'N/A')}",
                ])
            
            report_lines.append("")
        
        # システム健全性評価
        health_score = self.calculate_system_health(data)
        health_status = "優良" if health_score >= 0.8 else "良好" if health_score >= 0.6 else "要注意"
        
        report_lines.extend([
            "🏥 システム健全性:",
            f"  健全性スコア: {health_score:.2f}",
            f"  システム状態: {health_status}",
            f"  推奨アクション: {self.get_recommendations(data)}",
            ""
        ])
        
        report_lines.extend([
            "=" * 60,
            "📋 レポート終了",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def calculate_system_health(self, data: Dict[str, Any]) -> float:
        """システム健全性スコア計算"""
        score = 0.0
        
        # 投稿頻度健全性 (0.3)
        daily_count = data.get('daily_count', 0)
        if daily_count <= 3:
            score += 0.3 * (daily_count / 3)
        
        # 品質維持健全性 (0.4)
        if 'post_history' in data and data['post_history']:
            recent_quality = [post.get('quality_score', 0) for post in data['post_history'][-5:]]
            avg_quality = sum(recent_quality) / len(recent_quality)
            score += 0.4 * min(avg_quality / 0.8, 1.0)
        
        # 制限遵守健全性 (0.3)
        monthly_count = data.get('monthly_count', 0)
        if monthly_count <= 90:
            score += 0.3 * (1 - monthly_count / 90)
        
        return min(score, 1.0)
    
    def get_recommendations(self, data: Dict[str, Any]) -> str:
        """推奨アクション生成"""
        daily_count = data.get('daily_count', 0)
        monthly_count = data.get('monthly_count', 0)
        
        if monthly_count >= 85:
            return "月末制限接近中、投稿頻度を調整してください"
        elif daily_count >= 3:
            return "本日の制限に達しました、明日まで待機"
        elif monthly_count < 30:
            return "順調に運用中、現在のペースを維持"
        else:
            return "正常運用中"

def main():
    """メイン実行"""
    monitor = SystemMonitor()
    report = monitor.generate_comprehensive_report()
    print(report)
    
    # レポートファイル保存
    with open(f'system_report_{datetime.now().strftime("%Y%m%d_%H%M")}.txt', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    main()
