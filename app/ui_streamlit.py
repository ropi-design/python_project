"""
Streamlit UIのメインモジュール
サイドバー、KPIカード、グラフ、テーブルを表示
"""

import streamlit as st
import pandas as pd

from .loaders import load_csv
from .logic import compute_er, rank_by_er, avg_by_hour, avg_by_weekday, simple_hashtag_summary
from .charts import bar_hourly_er, bar_weekly_er


def main():
    """メインのStreamlitアプリケーション"""

    # ページ設定
    st.set_page_config(
        page_title="Instagram ER分析アプリ", page_icon="📊", layout="wide", initial_sidebar_state="expanded"
    )

    # ヘッダー
    st.title("📊 Instagram エンゲージメント率分析アプリ")
    st.markdown("CSVファイルをアップロードして、投稿のエンゲージメント率を分析しましょう！")

    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")

        # ファイルアップロード
        uploaded_file = st.file_uploader(
            "CSVファイルを選択",
            type=["csv"],
            help="必須列: post_id, posted_at, likes, comments, saves, followers_at_post",
        )

        # 計算基準選択
        er_basis = st.selectbox(
            "エンゲージメント率の計算基準",
            ["followers", "reach"],
            help="フォロワー数基準またはリーチ数基準でERを計算",
        )

        # 表示件数設定
        ranking_count = st.slider("ランキング表示件数", 5, 20, 10)

        st.markdown("---")
        st.markdown("### 📋 必須CSV列")
        st.markdown(
            """
        - `post_id`: 投稿ID
        - `posted_at`: 投稿日時 (YYYY-MM-DD HH:MM)
        - `likes`: いいね数
        - `comments`: コメント数
        - `saves`: 保存数
        - `followers_at_post`: 投稿時のフォロワー数
        """
        )

        st.markdown("### 🔍 任意CSV列")
        st.markdown(
            """
        - `reach`: リーチ数
        - `impressions`: インプレッション数
        - `media_type`: メディアタイプ
        - `caption`: キャプション
        - `hashtags`: ハッシュタグ（カンマ区切り）
        """
        )

    # メインコンテンツ
    if uploaded_file is not None:
        # CSV読み込み
        df = load_csv(uploaded_file)

        if not df.empty:
            # データの状態を確認
            st.write(f"**データ読み込み完了:** {len(df)}件の投稿")
            st.write(f"**列名:** {list(df.columns)}")

            # 計算基準に応じてERを再計算（必要に応じて）
            if er_basis == "reach" and "reach" in df.columns:
                df = compute_er(df, "reach")
                st.write("リーチ基準でERを再計算しました")
            elif er_basis == "followers":
                st.write("フォロワー基準のERを使用します（既に計算済み）")

            # KPIカード
            display_kpi_cards(df)

            # タブ表示
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📈 ランキング", "⏰ 時間分析", "📅 曜日分析", "🏷️ ハッシュタグ分析"]
            )

            with tab1:
                display_rankings(df, ranking_count)

            with tab2:
                display_hourly_analysis(df)

            with tab3:
                display_weekly_analysis(df)

            with tab4:
                display_hashtag_analysis(df)

    else:
        # ファイル未アップロード時の表示
        st.info("👆 左のサイドバーからCSVファイルをアップロードしてください")

        # サンプルデータの説明
        st.markdown("### 📊 サンプルデータ形式")
        sample_data = {
            "post_id": ["POST001", "POST002"],
            "posted_at": ["2025-01-01 19:30", "2025-01-02 12:00"],
            "likes": [120, 80],
            "comments": [15, 9],
            "saves": [20, 10],
            "reach": [4500, 2800],
            "impressions": [6000, 3500],
            "followers_at_post": [8200, 8250],
            "hashtags": ["#夏 #海 #旅行", "#グルメ #ランチ"],
        }

        st.dataframe(pd.DataFrame(sample_data), use_container_width=True)


def display_kpi_cards(df: pd.DataFrame):
    """KPIカードを表示"""
    st.header("🎯 主要指標")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_er = df["er_percentage"].mean()
        st.metric("平均エンゲージメント率", f"{avg_er:.2f}%" if not pd.isna(avg_er) else "N/A", delta=None)

    with col2:
        post_count = len(df)
        st.metric("総投稿数", f"{post_count:,}", delta=None)

    with col3:
        if "reach" in df.columns:
            avg_reach = df["reach"].mean()
            st.metric("平均リーチ数", f"{avg_reach:,.0f}" if not pd.isna(avg_reach) else "N/A", delta=None)
        else:
            st.metric("平均リーチ数", "N/A", delta=None)

    with col4:
        avg_likes = df["likes"].mean()
        st.metric("平均いいね数", f"{avg_likes:.0f}" if not pd.isna(avg_likes) else "N/A", delta=None)


def display_rankings(df: pd.DataFrame, count: int):
    """ランキング表示"""
    st.header("🏆 エンゲージメント率ランキング")

    # デバッグ情報を表示
    st.write(f"**デバッグ情報:** DataFrame行数: {len(df)}, ER列存在: {'er_percentage' in df.columns}")
    if "er_percentage" in df.columns:
        st.write(f"ER列の型: {df['er_percentage'].dtype}, NaN数: {df['er_percentage'].isnull().sum()}")
        st.write(f"ER値の範囲: {df['er_percentage'].min():.2f}% ~ {df['er_percentage'].max():.2f}%")

        # データの詳細を表示
        st.write("**データサンプル:**")
        st.write(df[["post_id", "er_percentage", "engagement_total"]].head())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥇 上位ランキング")
        try:
            top_rankings = rank_by_er(df, top=True, n=count)
            st.write(f"上位ランキング結果: {len(top_rankings)}件")
            if not top_rankings.empty:
                display_ranking_table(top_rankings, "上位")
            else:
                st.error("ランキング結果が空です")
        except Exception as e:
            st.error(f"上位ランキングエラー: {str(e)}")

    with col2:
        st.subheader("🥉 下位ランキング")
        try:
            bottom_rankings = rank_by_er(df, top=False, n=count)
            st.write(f"下位ランキング結果: {len(bottom_rankings)}件")
            if not bottom_rankings.empty:
                display_ranking_table(bottom_rankings, "下位")
            else:
                st.error("ランキング結果が空です")
        except Exception as e:
            st.error(f"下位ランキングエラー: {str(e)}")


def display_ranking_table(df: pd.DataFrame, rank_type: str):
    """ランキングテーブルを表示"""
    display_df = df[["post_id", "posted_at", "er_percentage", "engagement_total"]].copy()
    display_df["posted_at"] = display_df["posted_at"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["er_percentage"] = display_df["er_percentage"].round(2)
    display_df.columns = ["投稿ID", "投稿日時", "ER(%)", "エンゲージメント合計"]

    st.dataframe(display_df, use_container_width=True)


def display_hourly_analysis(df: pd.DataFrame):
    """時間帯分析を表示"""
    st.header("⏰ 時間帯別分析")

    # デバッグ情報を表示
    st.write(f"**デバッグ情報:** DataFrame行数: {len(df)}, hour列存在: {'hour' in df.columns}")
    if "hour" in df.columns:
        st.write(f"hour列の値: {df['hour'].tolist()}")
        st.write(f"hour列の型: {df['hour'].dtype}")

    hourly_data = avg_by_hour(df)
    st.write(f"時間分析結果: {len(hourly_data)}件, 空か: {hourly_data.empty}")

    if not hourly_data.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = bar_hourly_er(hourly_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("時間帯別データ")
            st.dataframe(hourly_data, use_container_width=True)
    else:
        st.error("時間帯別のデータが不足しています")
        st.write("**問題の詳細:**")
        st.write(f"- hour列の存在: {'hour' in df.columns}")
        st.write(f"- er_percentage列の存在: {'er_percentage' in df.columns}")
        if "hour" in df.columns and "er_percentage" in df.columns:
            st.write(f"- hour列の値: {df['hour'].tolist()}")
            st.write(f"- er_percentage列の値: {df['er_percentage'].tolist()}")


def display_weekly_analysis(df: pd.DataFrame):
    """曜日分析を表示"""
    st.header("📅 曜日別分析")

    # デバッグ情報を表示
    st.write(f"**デバッグ情報:** DataFrame行数: {len(df)}, weekday列存在: {'weekday' in df.columns}")
    if "weekday" in df.columns:
        st.write(f"weekday列の値: {df['weekday'].tolist()}")
        st.write(f"weekday列の型: {df['weekday'].dtype}")

    weekly_data = avg_by_weekday(df)
    st.write(f"曜日分析結果: {len(weekly_data)}件, 空か: {weekly_data.empty}")

    if not weekly_data.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = bar_weekly_er(weekly_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("曜日別データ")
            st.dataframe(weekly_data, use_container_width=True)
    else:
        st.error("曜日別のデータが不足しています")
        st.write("**問題の詳細:**")
        st.write(f"- weekday列の存在: {'weekday' in df.columns}")
        st.write(f"- er_percentage列の存在: {'er_percentage' in df.columns}")
        if "weekday" in df.columns and "er_percentage" in df.columns:
            st.write(f"- weekday列の値: {df['weekday'].tolist()}")
            st.write(f"- er_percentage列の値: {df['er_percentage'].tolist()}")


def display_hashtag_analysis(df: pd.DataFrame):
    """ハッシュタグ分析を表示"""
    st.header("🏷️ ハッシュタグ分析")

    # デバッグ情報を表示
    st.write(f"**デバッグ情報:** DataFrame行数: {len(df)}, hashtags列存在: {'hashtags' in df.columns}")
    if "hashtags" in df.columns:
        st.write(f"hashtags列の値: {df['hashtags'].tolist()[:3]}...")  # 最初の3件のみ表示

    hashtag_data = simple_hashtag_summary(df)
    st.write(f"ハッシュタグ分析結果: {len(hashtag_data)}件, 空か: {hashtag_data.empty}")

    if not hashtag_data.empty:
        st.subheader("ハッシュタグ別集計")
        st.dataframe(hashtag_data, use_container_width=True)

        # ハッシュタグ別の散布図
        if len(hashtag_data) > 1:
            fig = create_hashtag_scatter(hashtag_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("ハッシュタグデータが不足しています")
        st.write("**問題の詳細:**")
        st.write(f"- hashtags列の存在: {'hashtags' in df.columns}")
        st.write(f"- er_percentage列の存在: {'er_percentage' in df.columns}")
        if "hashtags" in df.columns:
            st.write(f"- hashtags列の値: {df['hashtags'].tolist()}")


def create_hashtag_scatter(df: pd.DataFrame):
    """ハッシュタグ別の散布図を作成"""
    try:
        import plotly.express as px

        fig = px.scatter(
            df,
            x="使用回数",
            y="平均ER(%)",
            size="総エンゲージメント",
            color="平均ER(%)",
            hover_name="hashtag",
            title="ハッシュタグ別パフォーマンス",
            size_max=20,
        )

        fig.update_layout(height=400)
        return fig
    except ImportError:
        return None


if __name__ == "__main__":
    main()
