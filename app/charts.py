"""
Plotlyグラフを作成するモジュール
時間帯別・曜日別のエンゲージメント率グラフを提供
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def bar_hourly_er(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    時間帯別エンゲージメント率の棒グラフを作成

    Args:
        df: 時間帯別集計のDataFrame

    Returns:
        PlotlyのFigureオブジェクト
    """
    if df.empty or "hour" not in df.columns:
        return None

    # 時間を24時間表記に変換
    df_display = df.copy()
    df_display["時間"] = df_display["hour"].astype(str) + "時"

    fig = px.bar(
        df_display,
        x="時間",
        y="平均ER(%)",
        title="時間帯別平均エンゲージメント率",
        color="平均ER(%)",
        color_continuous_scale="viridis",
        text="平均ER(%)",
        hover_data=["投稿数"],
    )

    fig.update_layout(xaxis_title="投稿時間", yaxis_title="平均ER(%)", showlegend=False, height=400)

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    return fig


def bar_weekly_er(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    曜日別エンゲージメント率の棒グラフを作成

    Args:
        df: 曜日別集計のDataFrame

    Returns:
        PlotlyのFigureオブジェクト
    """
    if df.empty or "weekday" not in df.columns:
        return None

    # 日本語の曜日に変換
    weekday_jp = {
        "Monday": "月曜日",
        "Tuesday": "火曜日",
        "Wednesday": "水曜日",
        "Thursday": "木曜日",
        "Friday": "金曜日",
        "Saturday": "土曜日",
        "Sunday": "日曜日",
    }

    df_display = df.copy()
    df_display["曜日"] = df_display["weekday"].map(weekday_jp)

    fig = px.bar(
        df_display,
        x="曜日",
        y="平均ER(%)",
        title="曜日別平均エンゲージメント率",
        color="平均ER(%)",
        color_continuous_scale="plasma",
        text="平均ER(%)",
        hover_data=["投稿数"],
    )

    fig.update_layout(xaxis_title="曜日", yaxis_title="平均ER(%)", showlegend=False, height=400)

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

    return fig


def create_engagement_trend(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    投稿日時別のエンゲージメント率トレンドを作成

    Args:
        df: 投稿データのDataFrame

    Returns:
        PlotlyのFigureオブジェクト
    """
    if df.empty or "posted_at" not in df.columns or "er_percentage" not in df.columns:
        return None

    # 日付でグループ化して平均ERを計算
    df_trend = df.copy()
    df_trend["date"] = df_trend["posted_at"].dt.date
    daily_avg = df_trend.groupby("date")["er_percentage"].mean().reset_index()

    fig = px.line(daily_avg, x="date", y="er_percentage", title="日別エンゲージメント率の推移", markers=True)

    fig.update_layout(xaxis_title="投稿日", yaxis_title="平均ER(%)", height=400)

    return fig
