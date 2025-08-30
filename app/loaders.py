"""
データ読み込みと前処理を行うモジュール
CSVファイルの読み込み、Graph API用の関数枠を提供
"""

import pandas as pd
import streamlit as st
import numpy as np
from typing import Dict, Any


def load_csv(path: Any) -> pd.DataFrame:
    """
    CSVファイルを読み込み、前処理を行う

    Args:
        path: CSVファイルのパス (またはUploadedFileオブジェクト)

    Returns:
        前処理済みのDataFrame
    """
    try:
        # CSV読み込み
        df = pd.read_csv(path)

        # デバッグ: CSV読み込み直後のカラム順序を確認
        st.sidebar.write("---")
        st.sidebar.write("**CSV読み込み直後のカラム順序:**")
        st.sidebar.write(f"カラム名: {list(df.columns)}")
        st.sidebar.write("---")

        # デバッグ: CSV読み込み直後のデータ型と欠損値を確認
        st.sidebar.write("---")
        st.sidebar.write("**loaders.py デバッグ情報 (CSV読み込み直後):**")
        st.sidebar.write(f"DataFrame行数: {len(df)}")
        st.sidebar.write(f"likes dtype (初期): {df['likes'].dtype}")
        st.sidebar.write(f"likes NaN数 (初期): {df['likes'].isnull().sum()}")
        st.sidebar.write(f"comments dtype (初期): {df['comments'].dtype}")
        st.sidebar.write(f"comments NaN数 (初期): {df['comments'].isnull().sum()}")
        st.sidebar.write(f"saves dtype (初期): {df['saves'].dtype}")
        st.sidebar.write(f"saves NaN数 (初期): {df['saves'].isnull().sum()}")
        st.sidebar.write(f"followers_at_post dtype (初期): {df['followers_at_post'].dtype}")
        st.sidebar.write(f"followers_at_post NaN数 (初期): {df['followers_at_post'].isnull().sum()}")
        st.sidebar.write("---")

        # 必須列の存在確認
        required_columns = ["post_id", "posted_at", "likes", "comments", "saves", "followers_at_post"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"必須列が不足しています: {missing_columns}")
            return pd.DataFrame()

        # カラムの順序を正しく設定
        # CSVファイルのカラム順序が期待と異なる場合の対応
        if len(df.columns) >= len(required_columns):
            # 最初の8列を正しい順序で取得
            df = df.iloc[:, :8]  # 最初の8列のみを使用
            df.columns = required_columns + ["reach", "impressions"]  # カラム名を正しく設定

            st.sidebar.write("---")
            st.sidebar.write("**カラム順序を修正しました:**")
            st.sidebar.write(f"修正後のカラム名: {list(df.columns)}")
            st.sidebar.write("---")

        # 日時列の処理
        st.sidebar.write("---")
        st.sidebar.write("**posted_at列の処理前の値:**")
        st.sidebar.write(f"最初の5件: {df['posted_at'].head().tolist()}")
        st.sidebar.write(f"データ型: {df['posted_at'].dtype}")
        st.sidebar.write("---")

        # 日時変換を明示的なフォーマットで実行
        df["posted_at"] = pd.to_datetime(df["posted_at"], format="%Y-%m-%d %H:%M", errors="coerce")

        st.sidebar.write("**posted_at列の処理後の値:**")
        st.sidebar.write(f"最初の5件: {df['posted_at'].head().tolist()}")
        st.sidebar.write(f"データ型: {df['posted_at'].dtype}")
        st.sidebar.write(f"NaN数: {df['posted_at'].isnull().sum()}")
        st.sidebar.write("---")

        if df["posted_at"].isnull().any():
            st.warning("posted_at列に無効な日時データがあります。NaNとして処理されます。")

        # weekdayとhour列を追加
        df["weekday"] = df["posted_at"].dt.day_name(locale="ja_JP.UTF-8")  # 日本語曜日
        df["hour"] = df["posted_at"].dt.hour

        st.sidebar.write("**weekdayとhour列の計算結果:**")
        st.sidebar.write(f"weekday列の値: {df['weekday'].head().tolist()}")
        st.sidebar.write(f"hour列の値: {df['hour'].head().tolist()}")
        st.sidebar.write(f"hour列の型: {df['hour'].dtype}")
        st.sidebar.write(f"hour列のNaN数: {df['hour'].isnull().sum()}")
        st.sidebar.write("---")

        # 数値列の処理
        numeric_columns = ["likes", "comments", "saves", "reach", "impressions", "followers_at_post"]
        for col in numeric_columns:
            if col in df.columns:
                # デバッグ: 数値変換前の値を確認
                if col == "likes":
                    st.sidebar.write("---")
                    st.sidebar.write(f"**{col}列の数値変換前の値:**")
                    st.sidebar.write(f"最初の5件: {df[col].head().tolist()}")
                    st.sidebar.write(f"データ型: {df[col].dtype}")
                    st.sidebar.write("---")

                # 数値変換前に文字列として扱い、余分な空白を除去
                df[col] = df[col].astype(str).str.strip()

                # デバッグ: 空白除去後の値を確認
                if col == "likes":
                    st.sidebar.write(f"**{col}列の空白除去後の値:**")
                    st.sidebar.write(f"最初の5件: {df[col].head().tolist()}")
                    st.sidebar.write("---")

                # 数値に変換、変換できない場合はNaN
                df[col] = pd.to_numeric(df[col], errors="coerce")

                # デバッグ: 数値変換後の値を確認
                if col == "likes":
                    st.sidebar.write(f"**{col}列の数値変換後の値:**")
                    st.sidebar.write(f"最初の5件: {df[col].head().tolist()}")
                    st.sidebar.write(f"NaN数: {df[col].isnull().sum()}")
                    st.sidebar.write("---")

                if df[col].isnull().any():
                    st.warning(f"{col}列に数値変換できないデータがあります。NaNとして処理されます。")

        # デバッグ: 数値変換後のデータ型と欠損値を確認
        st.sidebar.write("---")
        st.sidebar.write("**loaders.py デバッグ情報 (数値変換後):**")
        st.sidebar.write(f"DataFrame行数: {len(df)}")
        st.sidebar.write(f"likes dtype: {df['likes'].dtype}, NaN数: {df['likes'].isnull().sum()}")
        st.sidebar.write(f"comments dtype: {df['comments'].dtype}, NaN数: {df['comments'].isnull().sum()}")
        st.sidebar.write(f"saves dtype: {df['saves'].dtype}, NaN数: {df['saves'].isnull().sum()}")
        st.sidebar.write(f"followers_at_post dtype: {df['followers_at_post'].dtype}")
        st.sidebar.write(f"followers_at_post NaN数: {df['followers_at_post'].isnull().sum()}")
        st.sidebar.write("---")

        # エンゲージメント合計を計算
        df["engagement_total"] = df["likes"] + df["comments"] + df["saves"]

        # エンゲージメント率を計算
        # 分母が0の場合はNaNにする
        df["er_percentage"] = np.where(
            df["followers_at_post"] == 0,
            np.nan,
            (df["engagement_total"] / df["followers_at_post"] * 100).round(2),
        )

        # デバッグ: ER計算後のデータ型と欠損値を確認
        st.sidebar.write("---")
        st.sidebar.write("**loaders.py デバッグ情報 (ER計算後):**")
        st.sidebar.write(f"engagement_total dtype: {df['engagement_total'].dtype}")
        st.sidebar.write(f"engagement_total NaN数: {df['engagement_total'].isnull().sum()}")
        st.sidebar.write(f"er_percentage dtype: {df['er_percentage'].dtype}")
        st.sidebar.write(f"er_percentage NaN数: {df['er_percentage'].isnull().sum()}")
        min_er = df["er_percentage"].min()
        max_er = df["er_percentage"].max()
        st.sidebar.write(f"er_percentage値の範囲: {min_er:.2f}% ~ {max_er:.2f}%\n")
        st.sidebar.write("---")

        # ハッシュタグ列の処理
        if "hashtags" in df.columns:
            df["hashtags"] = df["hashtags"].fillna("").astype(str)

        st.success(f"CSVファイルを正常に読み込みました。投稿数: {len(df)}")
        return df

    except Exception as e:
        st.error(f"CSVファイルの読み込みまたは前処理中にエラーが発生しました: {e}")
        return pd.DataFrame()


def fetch_media_list() -> Dict[str, Any]:
    """Graph APIから投稿一覧を取得する想定。未実装"""
    st.info("Graph APIからの投稿一覧取得は未実装です。")
    return {}


def fetch_media_insights(media_id: str) -> Dict[str, Any]:
    """Graph APIから投稿インサイトを取得する想定。未実装"""
    st.info(f"Graph APIからの投稿インサイト取得は未実装です。Media ID: {media_id}")
    return {}
