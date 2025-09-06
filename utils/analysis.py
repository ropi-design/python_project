import pandas as pd
import numpy as np


def calculate_summary_stats(df):
    """サマリー統計を計算"""
    if df.empty:
        return {}

    stats = {
        "total_posts": len(df),
        "avg_er": df["er_percentage"].mean() if "er_percentage" in df.columns else 0,
        "max_er": df["er_percentage"].max() if "er_percentage" in df.columns else 0,
        "min_er": df["er_percentage"].min() if "er_percentage" in df.columns else 0,
        "avg_likes": df["likes"].mean() if "likes" in df.columns else 0,
        "avg_comments": df["comments"].mean() if "comments" in df.columns else 0,
        "avg_saves": df["saves"].mean() if "saves" in df.columns else 0,
        "avg_engagement": df["engagement_total"].mean() if "engagement_total" in df.columns else 0,
    }

    return stats


def rank_by_er(df, top=True, n=10):
    """エンゲージメント率でランキングを作成"""
    if df.empty or "er_percentage" not in df.columns:
        return pd.DataFrame()

    df_clean = df.dropna(subset=["er_percentage"])

    if df_clean.empty:
        return pd.DataFrame()

    if top:
        return df_clean.nlargest(n, "er_percentage")
    else:
        return df_clean.nsmallest(n, "er_percentage")


def avg_by_hour(df):
    """時間帯別の平均ERを計算"""
    if df.empty or "hour" not in df.columns or "er_percentage" not in df.columns:
        return pd.DataFrame()

    hourly_avg = df.groupby("hour")["er_percentage"].agg(["mean", "count"]).round(2)
    hourly_avg.columns = ["平均ER", "投稿数"]
    hourly_avg = hourly_avg.reset_index()
    hourly_avg["時間"] = hourly_avg["hour"].astype(str) + "時"

    return hourly_avg


def avg_by_weekday(df):
    """曜日別の平均ERを計算"""
    if df.empty or "weekday" not in df.columns or "er_percentage" not in df.columns:
        return pd.DataFrame()

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_avg = df.groupby("weekday")["er_percentage"].agg(["mean", "count"]).round(2)
    weekday_avg.columns = ["平均ER", "投稿数"]
    weekday_avg = weekday_avg.reset_index()

    # 曜日順にソート
    weekday_avg["weekday"] = pd.Categorical(weekday_avg["weekday"], categories=weekday_order, ordered=True)
    weekday_avg = weekday_avg.sort_values("weekday")

    # 日本語曜日名を追加
    weekday_jp = {
        "Monday": "月曜日",
        "Tuesday": "火曜日",
        "Wednesday": "水曜日",
        "Thursday": "木曜日",
        "Friday": "金曜日",
        "Saturday": "土曜日",
        "Sunday": "日曜日",
    }
    weekday_avg["曜日"] = weekday_avg["weekday"].map(weekday_jp)

    return weekday_avg


def simple_hashtag_summary(df, top_n=10):
    """ハッシュタグの簡単な分析"""
    if df.empty or "hashtags" not in df.columns:
        return pd.DataFrame()

    # ハッシュタグを分割してカウント
    all_hashtags = []
    for hashtags in df["hashtags"].dropna():
        if isinstance(hashtags, str) and hashtags.strip():
            tags = [tag.strip().lower() for tag in hashtags.split(",") if tag.strip()]
            all_hashtags.extend(tags)

    if not all_hashtags:
        return pd.DataFrame()

    # ハッシュタグの出現回数をカウント
    hashtag_counts = pd.Series(all_hashtags).value_counts().head(top_n)

    result_df = pd.DataFrame({"ハッシュタグ": hashtag_counts.index, "使用回数": hashtag_counts.values})

    return result_df
