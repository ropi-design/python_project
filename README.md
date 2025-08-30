# 📊 Instagram ER 分析アプリ

Instagram 投稿のエンゲージメント率（ER）を分析・可視化する Streamlit アプリケーションです。

## 🎯 機能

- **CSV ファイル読み込み**: 投稿データを CSV から読み込み
- **ER 自動計算**: いいね・コメント・保存数からエンゲージメント率を自動計算
- **KPI ダッシュボード**: 主要指標をカード形式で表示
- **ランキング表示**: 上位・下位の投稿をランキング形式で表示
- **時間分析**: 時間帯別・曜日別のエンゲージメント率分析
- **ハッシュタグ分析**: ハッシュタグ別のパフォーマンス分析
- **美しいグラフ**: Plotly を使用したインタラクティブな可視化

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
streamlit run streamlit_app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 📊 必須 CSV 列

以下の列が必須です：

| 列名                | 説明                 | 例               |
| ------------------- | -------------------- | ---------------- |
| `post_id`           | 投稿 ID              | POST001          |
| `posted_at`         | 投稿日時             | 2025-01-01 19:30 |
| `likes`             | いいね数             | 120              |
| `comments`          | コメント数           | 15               |
| `saves`             | 保存数               | 20               |
| `followers_at_post` | 投稿時のフォロワー数 | 8200             |

## 🔍 任意 CSV 列

以下の列は任意ですが、より詳細な分析が可能になります：

| 列名          | 説明                         | 例             |
| ------------- | ---------------------------- | -------------- |
| `reach`       | リーチ数                     | 4500           |
| `impressions` | インプレッション数           | 6000           |
| `media_type`  | メディアタイプ               | photo          |
| `caption`     | キャプション                 | 素敵な海の景色 |
| `hashtags`    | ハッシュタグ（カンマ区切り） | #夏 #海 #旅行  |

## 📁 プロジェクト構成

```
insta-er-app/
  ├─ app/
  │   ├─ __init__.py          # パッケージ初期化
  │   ├─ loaders.py           # CSV読み込み・前処理
  │   ├─ logic.py             # ER計算・集計ロジック
  │   ├─ charts.py            # Plotlyグラフ作成
  │   └─ ui_streamlit.py      # Streamlit UI
  ├─ data/
  │   └─ sample_data.csv      # テスト用サンプルデータ
  ├─ streamlit_app.py         # 起動エントリーポイント
  ├─ requirements.txt          # 依存関係
  └─ README.md                # このファイル
```

## 🎮 使い方

1. **CSV ファイルの準備**: 上記の必須列を含む CSV ファイルを準備
2. **ファイルアップロード**: 左サイドバーから CSV ファイルをアップロード
3. **設定調整**: 計算基準（フォロワー/リーチ）とランキング表示件数を設定
4. **分析結果確認**:
   - KPI カードで主要指標を確認
   - ランキングタブで上位・下位投稿を確認
   - 時間分析タブで時間帯・曜日別の傾向を確認
   - ハッシュタグ分析タブでタグ別パフォーマンスを確認

## 🔮 今後の拡張予定

### Graph API 連携（無料、プロアカウント必須）

以下の機能を将来的に実装予定です：

- **投稿一覧取得**: `fetch_media_list()` 関数
- **投稿インサイト取得**: `fetch_media_insights(media_id)` 関数
- **リアルタイムデータ**: 最新の投稿データを自動取得
- **定期更新**: スケジュールされたデータ更新

### 環境変数設定

Graph API 連携時は以下の環境変数を設定してください：

```bash
# .env ファイルを作成
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_API_VERSION=v18.0
```

## 🛠️ 技術スタック

- **Python 3.8+**: メイン言語
- **Streamlit**: Web アプリケーションフレームワーク
- **Pandas**: データ処理・分析
- **Plotly**: インタラクティブなグラフ作成
- **NumPy**: 数値計算

## 📝 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 🤝 コントリビューション

バグ報告や機能要望、プルリクエストを歓迎します！

---

**注意**: このアプリケーションは Instagram の公式 API ではありません。データの使用には Instagram の利用規約を遵守してください。
