#!/usr/bin/env python3
"""
簡易Web監視ダッシュボード
"""

import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            try:
                with open('usage_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                html = self.generate_dashboard_html(data)
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                error_html = f"<html><body><h1>エラー: {e}</h1></body></html>"
                self.wfile.write(error_html.encode('utf-8'))
    
    def generate_dashboard_html(self, data):
        """ダッシュボードHTML生成"""
        daily_count = data.get('daily_count', 0)
        monthly_count = data.get('monthly_count', 0)
        quality_posts = data.get('quality_posts', 0)
        total_posts = data.get('total_posts', 0) or 1
        
        usage_rate = (monthly_count / 90) * 100
        quality_rate = (quality_posts / total_posts) * 100
        
        return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI自動ツイートBot 監視ダッシュボード</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; border-radius: 8px; min-width: 150px; text-align: center; }}
        .metric.good {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
        .metric.warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; }}
        .metric.danger {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .progress-bar {{ width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; transition: width 0.5s ease; }}
        .progress-fill.good {{ background-color: #28a745; }}
        .progress-fill.warning {{ background-color: #ffc107; }}
        .progress-fill.danger {{ background-color: #dc3545; }}
        h1 {{ text-align: center; color: #333; }}
        .update-time {{ text-align: center; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI自動ツイートBot 監視ダッシュボード</h1>
        <div class="update-time">最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="metric {'good' if daily_count <= 3 else 'danger'}">
            <h3>本日投稿数</h3>
            <div style="font-size: 24px; font-weight: bold;">{daily_count}/3</div>
            <div class="progress-bar">
                <div class="progress-fill {'good' if daily_count <= 3 else 'danger'}" style="width: {min((daily_count/3)*100, 100)}%"></div>
            </div>
        </div>
        
        <div class="metric {'good' if usage_rate < 70 else 'warning' if usage_rate < 85 else 'danger'}">
            <h3>月間使用率</h3>
            <div style="font-size: 24px; font-weight: bold;">{usage_rate:.1f}%</div>
            <div style="font-size: 14px;">{monthly_count}/90投稿</div>
            <div class="progress-bar">
                <div class="progress-fill {'good' if usage_rate < 70 else 'warning' if usage_rate < 85 else 'danger'}" style="width: {usage_rate}%"></div>
            </div>
        </div>
        
        <div class="metric {'good' if quality_rate >= 80 else 'warning'}">
            <h3>品質投稿率</h3>
            <div style="font-size: 24px; font-weight: bold;">{quality_rate:.1f}%</div>
            <div style="font-size: 14px;">{quality_posts}/{total_posts}投稿</div>
            <div class="progress-bar">
                <div class="progress-fill {'good' if quality_rate >= 80 else 'warning'}" style="width: {quality_rate}%"></div>
            </div>
        </div>
        
        <div style="margin-top: 30px;">
            <h3>📊 詳細統計</h3>
            <p><strong>システム稼働開始:</strong> {data.get('system_start', 'N/A')}</p>
            <p><strong>最終更新:</strong> {data.get('last_update', 'N/A')}</p>
            <p><strong>総投稿数:</strong> {total_posts}</p>
            <p><strong>高品質投稿数:</strong> {quality_posts}</p>
        </div>
    </div>
    
    <script>
        // 30秒毎に自動更新
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """

def run_dashboard(port=8000):
    """ダッシュボード起動"""
    server = HTTPServer(('localhost', port), DashboardHandler)
    print(f"🌐 監視ダッシュボード起動: http://localhost:{port}")
    print("Ctrl+C で停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 ダッシュボード停止")
        server.shutdown()

if __name__ == "__main__":
    run_dashboard()
