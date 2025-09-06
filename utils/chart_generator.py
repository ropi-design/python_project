import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import pandas as pd
import json


def create_hourly_chart(df):
    """時間帯別ERチャートを作成"""
    if df.empty or "hour" not in df.columns or "er_percentage" not in df.columns:
        return None

    # 時間帯別の平均ERを計算
    hourly_data = df.groupby("hour")["er_percentage"].mean().round(2).reset_index()
    hourly_data["時間"] = hourly_data["hour"].astype(str) + "時"

    fig = go.Figure(
        data=[
            go.Bar(
                x=hourly_data["時間"],
                y=hourly_data["er_percentage"],
                marker_color="rgba(58, 71, 80, 0.6)",
                text=hourly_data["er_percentage"],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="時間帯別平均エンゲージメント率",
        xaxis_title="時間",
        yaxis_title="エンゲージメント率 (%)",
        template="plotly_white",
        height=400,
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_weekly_chart(df):
    """曜日別ERチャートを作成"""
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

    fig = go.Figure(
        data=[
            go.Bar(
                x=weekday_data["曜日"],
                y=weekday_data["er_percentage"],
                marker_color="rgba(58, 71, 80, 0.6)",
                text=weekday_data["er_percentage"],
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="曜日別平均エンゲージメント率",
        xaxis_title="曜日",
        yaxis_title="エンゲージメント率 (%)",
        template="plotly_white",
        height=400,
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)


def create_hashtag_chart(df, top_n=10):
    """ハッシュタグ分析チャートを作成"""
    if df.empty or "hashtags" not in df.columns:
        return None

    # ハッシュタグを分割してカウント
    all_hashtags = []
    for hashtags in df["hashtags"].dropna():
        if isinstance(hashtags, str) and hashtags.strip():
            tags = [tag.strip().lower() for tag in hashtags.split(",") if tag.strip()]
            all_hashtags.extend(tags)

    if not all_hashtags:
        return None

    # ハッシュタグの出現回数をカウント
    hashtag_counts = pd.Series(all_hashtags).value_counts().head(top_n)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=hashtag_counts.values,
                y=hashtag_counts.index,
                mode="markers",
                marker=dict(
                    size=hashtag_counts.values * 2,
                    color=hashtag_counts.values,
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="使用回数"),
                ),
                text=hashtag_counts.values,
                textposition="middle right",
            )
        ]
    )

    fig.update_layout(
        title=f"ハッシュタグ使用頻度（上位{top_n}位）",
        xaxis_title="使用回数",
        yaxis_title="ハッシュタグ",
        template="plotly_white",
        height=400,
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
