import pandas as pd
import numpy as np
from datetime import datetime
import os


def load_csv(file_path):
    """
    CSVファイルを読み込んで前処理を行う

    Args:
        file_path: CSVファイルのパス

    Returns:
        pd.DataFrame: 前処理済みのDataFrame
    """
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(file_path)

        # 必要な列を確認
        required_columns = [
            "post_id",
            "posted_at",
            "followers_at_post",
            "reach",
            "likes",
            "comments",
            "saves",
            "engagement_total",
            "hashtags",
        ]

        # 列名を統一
        if "post_id" not in df.columns and "id" in df.columns:
            df = df.rename(columns={"id": "post_id"})
        if "engagement_total" not in df.columns and "engagement" in df.columns:
            df = df = df.rename(columns={"engagement": "engagement_total"})

        # 必要な列のみを選択
        available_columns = [col for col in required_columns if col in df.columns]
        df = df[available_columns]

        # 日時列の処理
        if "posted_at" in df.columns:
            df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")
            df["hour"] = df["posted_at"].dt.hour
            df["weekday"] = df["posted_at"].dt.day_name()

        # 数値列の処理
        numeric_columns = ["followers_at_post", "reach", "likes", "comments", "saves"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].replace(["", "nan", "NaN", "null", "NULL"], np.nan)
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # engagement_totalを計算（likes + comments + saves）
        if all(col in df.columns for col in ["likes", "comments", "saves"]):
            df["engagement_total"] = df["likes"] + df["comments"] + df["saves"]

        # エンゲージメント率を計算
        if "followers_at_post" in df.columns and "engagement_total" in df.columns:
            # フォロワー数が0またはNaNの場合は、リーチ数を使用
            if "reach" in df.columns and not df["reach"].isna().all():
                df["er_percentage"] = (df["engagement_total"] / df["reach"] * 100).round(2)
                df.loc[df["reach"] == 0, "er_percentage"] = np.nan
            else:
                df["er_percentage"] = (df["engagement_total"] / df["followers_at_post"] * 100).round(2)
                df.loc[df["followers_at_post"] == 0, "er_percentage"] = np.nan

        # ハッシュタグ列の処理
        if "hashtags" in df.columns:
            df["hashtags"] = df["hashtags"].fillna("").astype(str)

        return df

    except Exception as e:
        raise Exception(f"CSVファイルの読み込みエラー: {str(e)}")


def get_sample_data():
    """サンプルデータを取得"""
    sample_path = os.path.join(os.path.dirname(__file__), "..", "data", "instagram_engagement_data.csv")
    return load_csv(sample_path)
