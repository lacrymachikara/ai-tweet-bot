# AI自動ツイートシステム 🤖✨

チカラさんの口調でAI画像・映像生成の最新情報を自動投稿するTwitterボットシステム

## 🎯 機能概要

- **自動ツイート投稿**: 1日3回（朝9時・昼12時・夜8時 JST）の定期投稿
- - **チカラさん風の口調**: 親しみやすい標準語での自然な投稿
  - - **AI情報特化**: AI画像生成・映像生成技術の最新情報を配信
    - - **エンゲージメント最適化**: 質問形式でフォロワーとの交流促進
      - - **完全無料運用**: GitHub Actions利用で運用コスト0円
       
        - ## 🚀 セットアップ手順
       
        - ### 1. Twitter API認証情報の取得
       
        - 1. [Twitter Developer Portal](https://developer.twitter.com/)でアプリを作成
          2. 2. 以下の認証情報を取得：
             3.    - API Key
                   -    - API Secret Key
                        -    - Access Token
                             -    - Access Token Secret
                              
                                  - ### 2. GitHub Secretsの設定
                              
                                  - リポジトリの「Settings」→「Secrets and variables」→「Actions」で以下を設定：
                              
                                  - ```
                                    TWITTER_API_KEY: あなたのAPI Key
                                    TWITTER_API_SECRET: あなたのAPI Secret Key
                                    TWITTER_ACCESS_TOKEN: あなたのAccess Token
                                    TWITTER_ACCESS_TOKEN_SECRET: あなたのAccess Token Secret
                                    ```

                                    ### 3. 手動実行テスト

                                    1. 「Actions」タブ→「AI Tweet Bot」workflow選択
                                    2. 2. 「Run workflow」ボタンで手動実行
                                       3. 3. 正常にツイートされることを確認
                                         
                                          4. ## 📁 ファイル構造
                                         
                                          5. ```
                                             ai-tweet-bot/
                                             ├── .github/
                                             │   └── workflows/
                                             │       └── auto-tweet.yml    # GitHub Actions設定
                                             ├── src/
                                             │   └── tweet_bot.py         # メインスクリプト
                                             ├── requirements.txt         # 依存関係
                                             └── README.md               # このファイル
                                             ```

                                             ## 🎨 ツイート例

                                             ```
                                             おはようございます！

                                             AIの画像生成技術、また進歩してるんですね！新しいAI画像生成モデルのリリースって知ってました？

                                             #StableDiffusion #AI画像生成 #AI映像生成 #生成AI #クリエイティブAI
                                             ```

                                             ## ⚙️ 設定内容

                                             ### スケジュール設定
                                             - **朝の投稿**: 毎日9:00 JST
                                             - - **昼の投稿**: 毎日12:00 JST
                                               - - **夜の投稿**: 毎日20:00 JST
                                                
                                                 - ### ツイート内容の特徴
                                                 - - チカラさんの自然な口調を再現
                                                   - - AI技術への興味と驚きを表現
                                                     - - フォロワーへの質問でエンゲージメント促進
                                                       - - 適切なハッシュタグで露出最適化
                                                        
                                                         - ## 🔧 カスタマイズ
                                                        
                                                         - ### 投稿時間の変更
                                                         - `.github/workflows/auto-tweet.yml`のcron設定を編集：
                                                        
                                                         - ```yaml
                                                           schedule:
                                                             - cron: '0 0 * * *'   # 朝9時JST（UTC 0時）
                                                             - cron: '0 3 * * *'   # 昼12時JST（UTC 3時）
                                                             - cron: '0 11 * * *'  # 夜8時JST（UTC 11時）
                                                           ```

                                                           ### 口調パターンの追加
                                                           `src/tweet_bot.py`の`chikara_patterns`配列に新しいパターンを追加

                                                           ### AI関連キーワードの更新
                                                           `ai_keywords`配列に最新のAI技術キーワードを追加

                                                           ## 📊 運用状況

                                                           - ✅ 自動投稿システム: 稼働中
                                                           - - ✅ エラーハンドリング: 実装済み
                                                             - - ✅ ログ出力: 詳細ログ記録
                                                               - - ✅ レート制限対応: 自動待機機能
                                                                
                                                                 - ## 🛠️ トラブルシューティング
                                                                
                                                                 - ### よくある問題
                                                                
                                                                 - 1. **ツイートが投稿されない**
                                                                   2.    - GitHub Secretsの設定を確認
                                                                         -    - Twitter API認証情報が正しいか確認
                                                                          
                                                                              - 2. **重複投稿エラー**
                                                                                3.    - 同じ内容の連続投稿は制限されます
                                                                                      -    - 少し時間をおいて再実行してください
                                                                                       
                                                                                           - 3. **API制限エラー**
                                                                                             4.    - Twitter API制限に達した場合は自動で待機します
                                                                                               
                                                                                                   - ## 📝 更新履歴
                                                                                               
                                                                                                   - - v1.0.0: 初期版リリース
                                                                                                     -   - 基本的な自動ツイート機能
                                                                                                         -   - チカラさん風口調の実装
                                                                                                             -   - GitHub Actions連携
                                                                                                              
                                                                                                                 - ## 🤝 貢献
                                                                                                              
                                                                                                                 - プルリクエストやイシューの報告を歓迎します！
                                                                                                              
                                                                                                                 - ## 📄 ライセンス
                                                                                                              
                                                                                                                 - MIT License
                                                                                                              
                                                                                                                 - ## 📞 サポート
                                                                                                              
                                                                                                                 - 質問や問題がある場合は、GitHubのIssuesでお知らせください。
                                                                                                              
                                                                                                                 - ---
                                                                                                                 
                                                                                                                 **注意**: このシステムは教育・学習目的で作成されています。商用利用の際はTwitter APIの利用規約を必ずご確認ください。
