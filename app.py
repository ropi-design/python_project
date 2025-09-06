from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
import pandas as pd
from werkzeug.utils import secure_filename
from utils.data_loader import load_csv, get_sample_data
from utils.analysis import (
    calculate_summary_stats,
    rank_by_er,
    avg_by_hour,
    avg_by_weekday,
    simple_hashtag_summary,
    generate_improvement_suggestions,
    generate_content_recommendations,
    calculate_engagement_metrics,
)
from utils.chart_generator import create_hourly_chart, create_weekly_chart, create_hashtag_chart

app = Flask(__name__)
app.secret_key = "your-secret-key-here"

# アップロード設定
UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {"csv"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """メインページ"""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """ファイルアップロード処理"""
    if "file" not in request.files:
        flash("ファイルが選択されていません")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("ファイルが選択されていません")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        try:
            df = load_csv(filepath)
            return redirect(url_for("analysis", filename=filename))
        except Exception as e:
            flash(f"ファイルの読み込みエラー: {str(e)}")
            return redirect(url_for("index"))
    else:
        flash("CSVファイルを選択してください")
        return redirect(url_for("index"))


@app.route("/sample")
def load_sample():
    """サンプルデータを読み込み"""
    try:
        df = get_sample_data()
        return redirect(url_for("analysis", filename="sample_data.csv"))
    except Exception as e:
        flash(f"サンプルデータの読み込みエラー: {str(e)}")
        return redirect(url_for("index"))


@app.route("/analysis/<filename>")
def analysis(filename):
    """分析ページ"""
    try:
        if filename == "sample_data.csv":
            df = get_sample_data()
        else:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            df = load_csv(filepath)

        if df.empty:
            flash("データが空です")
            return redirect(url_for("index"))

        # 統計情報を計算
        stats = calculate_summary_stats(df)

        # ランキングデータ
        top_rankings = rank_by_er(df, top=True, n=10)
        bottom_rankings = rank_by_er(df, top=False, n=10)

        # 時間帯別分析
        hourly_data = avg_by_hour(df)
        hourly_chart = create_hourly_chart(df) if not hourly_data.empty else None

        # 曜日別分析
        weekly_data = avg_by_weekday(df)
        weekly_chart = create_weekly_chart(df) if not weekly_data.empty else None

        # ハッシュタグ分析
        hashtag_data = simple_hashtag_summary(df, top_n=10)
        hashtag_chart = create_hashtag_chart(df, top_n=10) if not hashtag_data.empty else None

        # 改善提案を生成
        improvement_suggestions = generate_improvement_suggestions(df)

        # 内容分析による改善提案を生成
        content_recommendations = generate_content_recommendations(df)

        # エンゲージメント指標を計算
        engagement_metrics = calculate_engagement_metrics(df)

        return render_template(
            "analysis.html",
            stats=stats,
            top_rankings=top_rankings,
            bottom_rankings=bottom_rankings,
            hourly_data=hourly_data,
            weekly_data=weekly_data,
            hashtag_data=hashtag_data,
            hourly_chart=hourly_chart,
            weekly_chart=weekly_chart,
            hashtag_chart=hashtag_chart,
            improvement_suggestions=improvement_suggestions,
            content_recommendations=content_recommendations,
            engagement_metrics=engagement_metrics,
            filename=filename,
        )

    except Exception as e:
        flash(f"分析エラー: {str(e)}")
        return redirect(url_for("index"))


@app.route("/api/chart/<chart_type>")
def get_chart(chart_type):
    """チャートデータをAPIで取得"""
    filename = request.args.get("filename", "sample_data.csv")

    try:
        if filename == "sample_data.csv":
            df = get_sample_data()
        else:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            df = load_csv(filepath)

        if chart_type == "hourly":
            chart_data = create_hourly_chart(df)
        elif chart_type == "weekly":
            chart_data = create_weekly_chart(df)
        elif chart_type == "hashtag":
            chart_data = create_hashtag_chart(df)
        else:
            return jsonify({"error": "Invalid chart type"}), 400

        return jsonify({"chart": chart_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # データディレクトリを作成
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    app.run(debug=True, host="0.0.0.0", port=3000)
