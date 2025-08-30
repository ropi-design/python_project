"""
エンゲージメント率計算と集計ロジックを行うモジュール
"""

import pandas as pd
import numpy as np
from typing import Literal


def compute_er(df: pd.DataFrame, basis: Literal["followers", "reach"] = "followers") -> pd.DataFrame:
    """
    エンゲージメント率を計算する

    Args:
        df: 投稿データのDataFrame
        basis: 計算基準（"followers" または "reach"）

    Returns:
        ER計算済みのDataFrame
    """
    if df.empty:
        return df

    df = df.copy()

    if basis == "followers":
        if "followers_at_post" in df.columns:
            df["er_percentage"] = (df["engagement_total"] / df["followers_at_post"] * 100).round(2)
        else:
            df["er_percentage"] = np.nan
    elif basis == "reach":
        if "reach" in df.columns:
            df["er_percentage"] = (df["engagement_total"] / df["reach"] * 100).round(2)
        else:
            df["er_percentage"] = np.nan

    return df


def rank_by_er(df: pd.DataFrame, top: bool = True, n: int = 10) -> pd.DataFrame:
    """
    エンゲージメント率でランキングを作成

    Args:
        df: 投稿データのDataFrame
        top: Trueなら上位、Falseなら下位
        n: 表示件数

    Returns:
        ランキング済みのDataFrame
    """
    if df.empty or "er_percentage" not in df.columns:
        return df

    # NaNを除外してソート
    df_clean = df.dropna(subset=["er_percentage"])

    if df_clean.empty:
        return df_clean

    if top:
        return df_clean.nlargest(n, "er_percentage")
    else:
        return df_clean.nsmallest(n, "er_percentage")


def avg_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    時間帯別の平均エンゲージメント率を計算

    Args:
        df: 投稿データのDataFrame

    Returns:
        時間帯別集計のDataFrame
    """
    if df.empty or "hour" not in df.columns or "er_percentage" not in df.columns:
        return pd.DataFrame()

    hourly_avg = df.groupby("hour")["er_percentage"].agg(["mean", "count"]).round(2)
    hourly_avg.columns = ["平均ER(%)", "投稿数"]
    hourly_avg = hourly_avg.reset_index()

    return hourly_avg


def avg_by_weekday(df: pd.DataFrame) -> pd.DataFrame:
    """
    曜日別の平均エンゲージメント率を計算

    Args:
        df: 投稿データのDataFrame

    Returns:
        曜日別集計のDataFrame
    """
    if df.empty or "weekday" not in df.columns or "er_percentage" not in df.columns:
        return pd.DataFrame()

    # 曜日の順序を定義
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    weekday_avg = df.groupby("weekday")["er_percentage"].agg(["mean", "count"]).round(2)
    weekday_avg.columns = ["平均ER(%)", "投稿数"]
    weekday_avg = weekday_avg.reset_index()

    # 曜日順でソート
    weekday_avg["weekday"] = pd.Categorical(weekday_avg["weekday"], categories=weekday_order, ordered=True)
    weekday_avg = weekday_avg.sort_values("weekday")

    return weekday_avg


def simple_hashtag_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    ハッシュタグ別の集計を作成

    Args:
        df: 投稿データのDataFrame

    Returns:
        ハッシュタグ別集計のDataFrame
    """
    if df.empty or "hashtags" not in df.columns:
        return pd.DataFrame()

    # ハッシュタグを分割して展開
    hashtag_data = []
    for _, row in df.iterrows():
        if pd.notna(row["hashtags"]) and row["hashtags"]:
            hashtags = [tag.strip() for tag in str(row["hashtags"]).split(",") if tag.strip()]
            for tag in hashtags:
                hashtag_data.append(
                    {
                        "hashtag": tag,
                        "er_percentage": row.get("er_percentage", np.nan),
                        "engagement_total": row.get("engagement_total", 0),
                    }
                )

    if not hashtag_data:
        return pd.DataFrame()

    hashtag_df = pd.DataFrame(hashtag_data)

    # ハッシュタグ別に集計
    summary = (
        hashtag_df.groupby("hashtag")
        .agg({"er_percentage": ["mean", "count"], "engagement_total": "sum"})
        .round(2)
    )

    summary.columns = ["平均ER(%)", "使用回数", "総エンゲージメント"]
    summary = summary.reset_index()
    summary = summary.sort_values("平均ER(%)", ascending=False)

    return summary
