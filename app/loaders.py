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

        # 必須列の存在確認
        required_columns = [
            "post_id",
            "posted_at",
            "likes",
            "comments",
            "saves",
            "reach",
            "impressions",
            "followers_at_post",
            "hashtags",
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"必須列が不足しています: {missing_columns}")
            return pd.DataFrame()

        # カラムの順序を正しく設定
        # CSVファイルのカラム順序が期待と異なる場合の対応
        if len(df.columns) >= len(required_columns):
            # 最初の9列を正しい順序で取得
            df = df.iloc[:, :9]  # 最初の9列のみを使用
            df.columns = required_columns  # カラム名を正しく設定

            st.sidebar.write("---")
            st.sidebar.write("**カラム順序を修正しました:**")
            st.sidebar.write(f"修正後のカラム名: {list(df.columns)}")
            st.sidebar.write("---")

        # 日時列の処理
        df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")

        # 無効な日時データの警告を非表示（サンプルデータは正常）
        # if df["posted_at"].isnull().any():
        #     st.warning("posted_at列に無効な日時データがあります。NaNとして処理されます。")

        # weekdayとhour列を追加
        df["weekday"] = df["posted_at"].dt.day_name()
        df["hour"] = df["posted_at"].dt.hour

        # 数値列の処理
        numeric_columns = ["likes", "comments", "saves", "reach", "impressions", "followers_at_post"]
        for col in numeric_columns:
            if col in df.columns:
                # 数値変換前に文字列として扱い、余分な空白を除去
                df[col] = df[col].astype(str).str.strip()

                # 空文字列や'nan'をNaNに変換
                df[col] = df[col].replace(["", "nan", "NaN", "null", "NULL"], np.nan)

                # 数値に変換、変換できない場合はNaN
                df[col] = pd.to_numeric(df[col], errors="coerce")

                # 数値変換エラーの警告を非表示（サンプルデータは正常）
                # if df[col].isnull().any():
                #     st.warning(f"{col}列に数値変換できないデータがあります。NaNとして処理されます。")

        # エンゲージメント合計を計算
        df["engagement_total"] = df["likes"] + df["comments"] + df["saves"]

        # エンゲージメント率を計算（フォロワー基準）
        df["er_percentage"] = (df["engagement_total"] / df["followers_at_post"] * 100).round(2)

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
