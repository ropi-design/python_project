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
    hourly_data = hourly_data.sort_values("hour")
    hourly_data["時間"] = hourly_data["hour"].astype(str) + "時"
    hourly_data["text_label"] = hourly_data["er_percentage"].apply(lambda x: f"{x:.1f}%")

    # Plotly Expressを使用してシンプルに作成
    import plotly.express as px

    fig = px.bar(
        hourly_data,
        x="時間",
        y="er_percentage",
        title="時間帯別平均エンゲージメント率",
        text="text_label",
        color="er_percentage",
        color_continuous_scale="Viridis",
    )

    # テキストとカラーマップの設定
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=12, color="black"),
        marker=dict(
            line=dict(width=1, color="white"),
            showscale=False,
        ),
    )

    # レイアウトの設定
    fig.update_layout(
        template="plotly_white",
        height=500,
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60),
        xaxis=dict(
            title="時間帯",
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
        ),
        yaxis=dict(
            title="エンゲージメント率 (%)",
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
        ),
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
    weekday_data["text_label"] = weekday_data["er_percentage"].apply(lambda x: f"{x:.1f}%")


    # デバッグ情報を出力
    print(f"DEBUG: create_weekly_chart - weekday_data shape: {weekday_data.shape}")
    print(f"DEBUG: create_weekly_chart - weekday_data columns: {weekday_data.columns.tolist()}")
    print(f"DEBUG: create_weekly_chart - weekday_data data:")
    print(weekday_data)

    # Plotly Expressを使用して確実に縦棒グラフを作成
    import plotly.express as px

    fig = px.bar(
        weekday_data,
        x="曜日",
        y="er_percentage",
        title="曜日別平均エンゲージメント率",
        labels={"曜日": "曜日", "er_percentage": "エンゲージメント率 (%)"},
        text="text_label",
    )

    # テキストフォーマットとカラーマップを設定
    fig.update_traces(
        textposition="auto",
        marker=dict(
            color=weekday_data["er_percentage"],
            colorscale="Plasma",
            showscale=False,  # カラーバーを非表示
            line=dict(width=1, color="white"),
            cmin=weekday_data["er_percentage"].min(),  # 色の最小値
            cmax=weekday_data["er_percentage"].max(),  # 色の最大値
        ),
    )

    # Y軸の範囲を適切に設定
    y_max = weekday_data["er_percentage"].max()
    y_range = [0, y_max * 1.2] if y_max > 0 else [0, 1]

    fig.update_layout(
        template="plotly_white",
        height=400,
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(type="category", categoryorder="array", categoryarray=weekday_data["曜日"].tolist()),
        yaxis=dict(
            type="linear", range=y_range, title="エンゲージメント率 (%)", dtick=1 if y_max <= 10 else 2
        ),
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
            # カンマで分割し、#記号を除去して小文字に変換
            tags = [tag.strip().replace("#", "").lower() for tag in hashtags.split(",") if tag.strip()]
            all_hashtags.extend(tags)

    if not all_hashtags:
        return None

    # ハッシュタグの出現回数をカウント
    hashtag_counts = pd.Series(all_hashtags).value_counts().head(top_n)

    # データが少ない場合は実際の数だけ表示
    actual_top_n = len(hashtag_counts)

    # テキストラベルを作成（数値を棒の上に表示）
    text_labels = [f"{val}回" for val in hashtag_counts.values]

    fig = go.Figure(
        data=[
            go.Bar(
                x=hashtag_counts.values,
                y=hashtag_counts.index,
                orientation="h",
                marker=dict(
                    color=hashtag_counts.values,
                    colorscale="Viridis",
                    showscale=False,  # カラーバーを非表示
                    line=dict(width=1, color="white"),
                    cmin=hashtag_counts.values.min(),  # 色の最小値
                    cmax=hashtag_counts.values.max(),  # 色の最大値
                ),
                text=text_labels,
                textposition="inside",  # 棒の内側にテキストを配置
                textfont=dict(size=12, color="white", family="Arial Black"),  # 白い太字で表示
            )
        ]
    )

    fig.update_layout(
        title=f"ハッシュタグ使用頻度（上位{actual_top_n}位）",
        xaxis_title="使用回数",
        yaxis_title="ハッシュタグ",
        template="plotly_white",
        height=max(400, actual_top_n * 50),  # データ数に応じて高さを調整
        showlegend=False,
        margin=dict(l=120, r=80, t=60, b=60),  # 左マージンを拡大してハッシュタグ名を表示
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            gridwidth=1,
        ),
    )

    return json.dumps(fig, cls=PlotlyJSONEncoder)
