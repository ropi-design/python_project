"""
Streamlit UIのメインモジュール
サイドバー、KPIカード、グラフ、テーブルを表示
"""

import streamlit as st
import pandas as pd

from .loaders import load_csv
from .logic import compute_er, rank_by_er, avg_by_hour, avg_by_weekday, simple_hashtag_summary
from .charts import bar_hourly_er, bar_weekly_er


def load_css():
    """カスタムCSSを読み込み"""
    # インラインCSSで直接スタイルを適用
    st.markdown(
        """
        <style>
        /* サイドバーのスタイル */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%) !important;
            border-right: 1px solid #cbd5e1 !important;
            color: #1e293b !important;
        }
        
        .sidebar .sidebar-content h3 {
            color: white !important;
            font-weight: 700 !important;
            font-family: 'Inter', sans-serif !important;
            margin-bottom: 1.5rem !important;
            padding: 1rem 1.5rem !important;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            border-radius: 12px !important;
            text-align: center !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* ファイルアップローダーのスタイル */
        .stFileUploader {
            background: rgba(255, 255, 255, 0.98) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            border: 2px dashed #3b82f6 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin-bottom: 1.5rem !important;
        }
        
        .stFileUploader:hover {
            border-color: #1d4ed8 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px rgba(0,0,0,0.1) !important;
            background: rgba(255, 255, 255, 1) !important;
            border-width: 3px !important;
        }
        
        /* セレクトボックスのスタイル */
        .stSelectbox {
            background: rgba(255, 255, 255, 0.98) !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            border: 1px solid rgba(59, 130, 246, 0.2) !important;
            margin-bottom: 1.5rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stSelectbox:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 15px rgba(0,0,0,0.1) !important;
            border-color: rgba(59, 130, 246, 0.4) !important;
            background: rgba(255, 255, 255, 1) !important;
        }
        
        /* スライダーのスタイル */
        .stSlider {
            background: rgba(255, 255, 255, 0.98) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            border: 1px solid rgba(59, 130, 246, 0.2) !important;
            margin-bottom: 1.5rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .stSlider:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 10px 15px rgba(0,0,0,0.1) !important;
            border-color: rgba(59, 130, 246, 0.4) !important;
            background: rgba(255, 255, 255, 1) !important;
        }
        
        /* サイドバー内のテキストとラベルの改善 */
        .sidebar .sidebar-content label {
            color: #1e293b !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            margin-bottom: 0.5rem !important;
            display: block !important;
        }
        
        .sidebar .sidebar-content .stMarkdown {
            color: #374151 !important;
        }
        
        .sidebar .sidebar-content .stMarkdown h4 {
            color: #1e293b !important;
            font-weight: 600 !important;
            margin-bottom: 0.75rem !important;
        }
        
        .sidebar .sidebar-content .stMarkdown ul {
            color: #4b5563 !important;
        }
        
        .sidebar .sidebar-content .stMarkdown code {
            background: rgba(59, 130, 246, 0.1) !important;
            color: #1d4ed8 !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 4px !important;
            font-family: 'Monaco', 'Menlo', monospace !important;
            border: 1px solid rgba(59, 130, 246, 0.2) !important;
        }
        
        /* セパレーターの改善 */
        .sidebar .sidebar-content hr {
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent) !important;
            margin: 2rem 0 !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def main():
    """メインのStreamlitアプリケーション"""

    # カスタムCSSを読み込み
    load_css()

    # ページ設定
    st.set_page_config(
        page_title="Instagram ER分析アプリ", page_icon="📊", layout="wide", initial_sidebar_state="expanded"
    )

    # ヘッダー
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 3rem;">
            <h1 class="gradient-text">
                📊 Instagram エンゲージメント率分析アプリ
            </h1>
            <p style="font-size: 1.2rem; color: #64748b; margin-top: 1rem;">
                CSVファイルをアップロードして、投稿のエンゲージメント率を分析しましょう！
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # サイドバー
    with st.sidebar:
        st.markdown("### ⚙️ 設定パネル")

        # カスタムスタイルを適用
        st.markdown(
            """
            <style>
            .sidebar .sidebar-content {
                background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        # ファイルアップロード
        st.markdown("**📁 CSVファイルを選択**")
        uploaded_file = st.file_uploader(
            "",
            type=["csv"],
            help="必須列: post_id, posted_at, likes, comments, saves, followers_at_post",
        )

        st.markdown("---")

        # 計算基準選択
        st.markdown("**🎯 エンゲージメント率の計算基準**")
        er_basis = st.selectbox(
            "",
            ["followers", "reach"],
            help="フォロワー数基準またはリーチ数基準でERを計算",
        )

        st.markdown("---")

        # 表示件数設定
        st.markdown("**🏆 ランキング表示件数**")
        ranking_count = st.slider("", 5, 20, 10)

        st.markdown("---")

        # 必須CSV列の説明
        with st.container():
            st.markdown("**📋 必須CSV列**")
            st.markdown(
                """
            - `post_id`: 投稿ID
            - `posted_at`: 投稿日時
            - `likes`: いいね数
            - `comments`: コメント数
            - `saves`: 保存数
            - `followers_at_post`: 投稿時のフォロワー数
            """
            )

        st.markdown("---")

        # 任意CSV列の説明
        with st.container():
            st.markdown("**🔍 任意CSV列**")
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
            st.markdown(
                """
                <div style="background: rgba(34, 197, 94, 0.1); padding: 1rem; 
                     border-radius: 12px; border-left: 4px solid #22c55e; 
                     margin-bottom: 2rem;">
                    <h4 style="color: #22c55e; margin: 0;">✅ データ読み込み完了</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #374151;">
                        <strong>{}</strong>件の投稿、<strong>{}</strong>列のデータを読み込みました
                    </p>
                </div>
            """.format(
                    len(df), len(df.columns)
                ),
                unsafe_allow_html=True,
            )

            # 計算基準に応じてERを再計算（必要に応じて）
            if er_basis == "reach" and "reach" in df.columns:
                df = compute_er(df, "reach")
                st.success("🎯 リーチ基準でERを再計算しました")
            elif er_basis == "followers":
                st.info("👥 フォロワー基準のERを使用します（既に計算済み）")

            # KPIカード
            display_kpi_cards(df)

            # タブ表示
            tab1, tab2, tab3, tab4 = st.tabs(
                ["🏆 ランキング", "⏰ 時間分析", "📅 曜日分析", "🏷️ ハッシュタグ分析"]
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
        st.markdown(
            """
            <div style="text-align: center; padding: 4rem 2rem; 
                 background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                 border-radius: 20px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📁</div>
                <h2 style="color: #374151; margin-bottom: 1rem;">
                    ファイルをアップロードしてください
                </h2>
                <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">
                    左のサイドバーからCSVファイルをアップロードして分析を開始しましょう
                </p>
                <div style="background: rgba(255, 255, 255, 0.8); padding: 1rem; 
                     border-radius: 12px; display: inline-block;">
                    <p style="margin: 0; color: #374151;">
                        💡 サンプルデータ形式は下記をご確認ください
                    </p>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

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
    st.markdown(
        """
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2>🎯 主要指標</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_er = df["er_percentage"].mean()
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);">
                <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {avg_er:.2f}% if not pd.isna(avg_er) else "N/A"
                </div>
                <div style="font-size: 1rem; opacity: 0.9;">平均エンゲージメント率</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        post_count = len(df)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(240, 147, 251, 0.3);">
                <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {post_count:,}
                </div>
                <div style="font-size: 1rem; opacity: 0.9;">総投稿数</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        if "reach" in df.columns:
            avg_reach = df["reach"].mean()
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);">
                    <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {avg_reach:,.0f} if not pd.isna(avg_reach) else "N/A"
                    </div>
                    <div style="font-size: 1rem; opacity: 0.9;">平均リーチ数</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);">
                    <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">N/A</div>
                    <div style="font-size: 1rem; opacity: 0.9;">平均リーチ数</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    with col4:
        avg_likes = df["likes"].mean()
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(67, 233, 123, 0.3);">
                <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {avg_likes:.0f} if not pd.isna(avg_likes) else "N/A"
                </div>
                <div style="font-size: 1rem; opacity: 0.9;">平均いいね数</div>
            </div>
        """,
            unsafe_allow_html=True,
        )


def display_rankings(df: pd.DataFrame, count: int):
    """ランキング表示"""
    st.markdown(
        """
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2>🏆 エンゲージメント率ランキング</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%); color: white; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;">
                <h3 style="margin: 0; text-align: center;">🥇 上位ランキング</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        try:
            top_rankings = rank_by_er(df, top=True, n=count)
            if not top_rankings.empty:
                display_ranking_table(top_rankings, "上位")
            else:
                st.error("ランキング結果が空です")
        except Exception as e:
            st.error(f"上位ランキングエラー: {str(e)}")

    with col2:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #374151; padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;">
                <h3 style="margin: 0; text-align: center;">🥉 下位ランキング</h3>
            </div>
        """,
            unsafe_allow_html=True,
        )

        try:
            bottom_rankings = rank_by_er(df, top=False, n=count)
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
    st.markdown(
        """
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2>⏰ 時間帯別分析</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    hourly_data = avg_by_hour(df)

    if not hourly_data.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = bar_hourly_er(hourly_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.9); padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #374151; margin-bottom: 1rem;">📊 時間帯別データ</h3>
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.dataframe(hourly_data, use_container_width=True)
    else:
        st.error("時間帯別のデータが不足しています")


def display_weekly_analysis(df: pd.DataFrame):
    """曜日分析を表示"""
    st.markdown(
        """
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2>📅 曜日別分析</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    weekly_data = avg_by_weekday(df)

    if not weekly_data.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = bar_weekly_er(weekly_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.9); padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #374151; margin-bottom: 1rem;">📊 曜日別データ</h3>
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.dataframe(weekly_data, use_container_width=True)
    else:
        st.error("曜日別のデータが不足しています")


def display_hashtag_analysis(df: pd.DataFrame):
    """ハッシュタグ分析を表示"""
    st.markdown(
        """
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2>🏷️ ハッシュタグ分析</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    hashtag_data = simple_hashtag_summary(df)

    if not hashtag_data.empty:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.9); padding: 1.5rem; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #374151; margin-bottom: 1rem;">📊 ハッシュタグ別集計</h3>
                </div>
            """,
                unsafe_allow_html=True,
            )
            st.dataframe(hashtag_data, use_container_width=True)

        with col2:
            # ハッシュタグ別の散布図
            if len(hashtag_data) > 1:
                fig = create_hashtag_scatter(hashtag_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("ハッシュタグデータが不足しています")


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

        fig.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", size=12),
            title_font_size=16,
            title_font_color="#374151",
        )

        fig.update_traces(marker=dict(line=dict(width=2, color="white"), opacity=0.8))

        return fig
    except ImportError:
        return None


if __name__ == "__main__":
    main()
