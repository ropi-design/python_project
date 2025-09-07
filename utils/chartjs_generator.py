import pandas as pd
import json


def create_hourly_chart_chartjs(df):
    """時間帯別ERチャートを作成（Chart.js用）"""
    if df.empty or "hour" not in df.columns or "er_percentage" not in df.columns:
        return None

    # 時間帯別の平均ERを計算
    hourly_data = df.groupby("hour")["er_percentage"].mean().round(2).reset_index()
    hourly_data = hourly_data.sort_values("hour")
    hourly_data["時間"] = hourly_data["hour"].astype(str) + "時"

    # Chart.js用のデータ形式に変換
    chart_data = {
        "labels": hourly_data["時間"].tolist(),
        "datasets": [
            {
                "label": "エンゲージメント率 (%)",
                "data": hourly_data["er_percentage"].tolist(),
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 2,
                "tension": 0.1,
            }
        ],
    }

    # Chart.js用のオプション
    y_max = float(hourly_data["er_percentage"].max())
    chart_options = {
        "responsive": True,
        "maintainAspectRatio": False,
        "scales": {
            "y": {
                "beginAtZero": True,
                "min": 0,
                "max": y_max * 1.1,
                "ticks": {"stepSize": 1.0},
                "title": {"display": True, "text": "エンゲージメント率 (%)"},
            },
            "x": {"title": {"display": True, "text": "時間帯"}},
        },
        "plugins": {
            "legend": {"display": True},
            "title": {"display": True, "text": "時間帯別平均エンゲージメント率"},
        },
    }

    return {"type": "chartjs", "chartType": "bar", "data": chart_data, "options": chart_options}


def create_weekly_chart_chartjs(df):
    """曜日別ERチャートを作成（Chart.js用）"""
    if df.empty or "weekday" not in df.columns or "er_percentage" not in df.columns:
        return None

    # 曜日別の平均ERを計算
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_data = df.groupby("weekday")["er_percentage"].mean().round(2).reset_index()

    # 曜日順にソート
    weekday_data["weekday"] = pd.Categorical(weekday_data["weekday"], categories=weekday_order, ordered=True)
    weekday_data = weekday_data.sort_values("weekday")

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
    weekday_data["曜日"] = weekday_data["weekday"].map(weekday_jp)

    # Chart.js用のデータ形式に変換
    chart_data = {
        "labels": weekday_data["曜日"].tolist(),
        "datasets": [
            {
                "label": "エンゲージメント率 (%)",
                "data": weekday_data["er_percentage"].tolist(),
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 2,
                "tension": 0.1,
            }
        ],
    }

    # Chart.js用のオプション
    y_max = float(weekday_data["er_percentage"].max())
    chart_options = {
        "responsive": True,
        "maintainAspectRatio": False,
        "scales": {
            "y": {
                "beginAtZero": True,
                "min": 0,
                "max": y_max * 1.1,
                "ticks": {"stepSize": 0.5},
                "title": {"display": True, "text": "エンゲージメント率 (%)"},
            },
            "x": {"title": {"display": True, "text": "曜日"}},
        },
        "plugins": {
            "legend": {"display": True},
            "title": {"display": True, "text": "曜日別平均エンゲージメント率"},
        },
    }

    return {"type": "chartjs", "chartType": "bar", "data": chart_data, "options": chart_options}


def create_hashtag_chart_chartjs(df, top_n=10):
    """ハッシュタグ分析チャートを作成（Chart.js用）"""
    if df.empty or "hashtags" not in df.columns:
        return None

    # ハッシュタグを分割してカウント
    all_hashtags = []
    for hashtags in df["hashtags"].dropna():
        if isinstance(hashtags, str) and hashtags.strip():
            # カンマで分割し、#記号を除去して小文字に変換
            tags = [tag.strip().replace("#", "").lower() for tag in hashtags.split(",") if tag.strip()]
            # 各タグをさらにスペースで分割して個別の単語にする
            for tag in tags:
                words = tag.split()
                all_hashtags.extend(words)

    if not all_hashtags:
        return None

    # ハッシュタグの出現回数をカウント
    hashtag_counts = pd.Series(all_hashtags).value_counts().head(top_n)

    # Chart.js用のデータ形式に変換
    chart_data = {
        "labels": hashtag_counts.index.tolist(),
        "datasets": [
            {
                "label": "使用回数",
                "data": hashtag_counts.values.tolist(),
                "backgroundColor": "rgba(75, 192, 192, 0.6)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 2,
            }
        ],
    }

    # Chart.js用のオプション
    y_max = float(hashtag_counts.max())
    chart_options = {
        "responsive": True,
        "maintainAspectRatio": False,
        "scales": {
            "y": {
                "beginAtZero": True,
                "min": 0,
                "max": y_max * 1.1,
                "ticks": {"stepSize": 1},
                "title": {"display": True, "text": "使用回数"},
            },
            "x": {"title": {"display": True, "text": "ハッシュタグ"}},
        },
        "plugins": {"legend": {"display": True}, "title": {"display": True, "text": "ハッシュタグ使用頻度"}},
    }

    return {"type": "chartjs", "chartType": "bar", "data": chart_data, "options": chart_options}
