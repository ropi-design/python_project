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


def calculate_engagement_metrics(df):
    """エンゲージメント指標を計算"""
    if df.empty:
        return {}

    # 必要な列が存在するかチェック
    required_columns = ["followers_at_post", "likes", "comments", "saves"]
    if not all(col in df.columns for col in required_columns):
        return {"error": "必要なデータが不足しています"}

    # エンゲージメント数を計算
    df["engagement_total"] = df["likes"] + df["comments"] + df["saves"]

    # フォロワー数ベースのエンゲージメント率
    df["er_by_followers"] = (df["engagement_total"] / df["followers_at_post"] * 100).round(2)

    metrics = {
        "フォロワー数ベース": {
            "平均ER": f"{df['er_by_followers'].mean():.2f}%",
            "最高ER": f"{df['er_by_followers'].max():.2f}%",
            "最低ER": f"{df['er_by_followers'].min():.2f}%",
            "中央値ER": f"{df['er_by_followers'].median():.2f}%",
            "計算式": "（いいね＋コメント＋保存）÷ フォロワー数 × 100",
        }
    }

    # インプレッション数ベースのエンゲージメント率（インプレッション列が存在する場合）
    if "impressions" in df.columns:
        # インプレッション数が0でない行のみを対象
        valid_impressions = df["impressions"] > 0
        if valid_impressions.any():
            df.loc[valid_impressions, "er_by_impressions"] = (
                df.loc[valid_impressions, "engagement_total"] / df.loc[valid_impressions, "impressions"] * 100
            ).round(2)

            # 有効なデータのみで統計を計算
            valid_data = df[valid_impressions]["er_by_impressions"]
            metrics["インプレッション数ベース"] = {
                "平均ER": f"{valid_data.mean():.2f}%",
                "最高ER": f"{valid_data.max():.2f}%",
                "最低ER": f"{valid_data.min():.2f}%",
                "中央値ER": f"{valid_data.median():.2f}%",
                "計算式": "（いいね＋コメント＋保存）÷ インプレッション数 × 100",
            }
        else:
            metrics["インプレッション数ベース"] = {
                "平均ER": "データなし",
                "最高ER": "データなし",
                "最低ER": "データなし",
                "中央値ER": "データなし",
                "計算式": "（いいね＋コメント＋保存）÷ インプレッション数 × 100",
            }

    return metrics


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


def analyze_content_patterns(df):
    """投稿内容のパターンを分析してエンゲージメント率との関係を調査"""
    if df.empty or "er_percentage" not in df.columns:
        return {"error": "データが不足しています"}

    content_analysis = {
        "hashtag_patterns": {},
        "time_patterns": {},
        "engagement_patterns": {},
        "recommendations": [],
    }

    # ハッシュタグのパターン分析
    if "hashtags" in df.columns:
        hashtag_analysis = []
        for _, row in df.iterrows():
            if pd.notna(row["hashtags"]) and pd.notna(row["er_percentage"]):
                hashtags = [
                    tag.strip().lower().replace("#", "")
                    for tag in str(row["hashtags"]).split(",")
                    if tag.strip()
                ]
                hashtag_analysis.append(
                    {
                        "hashtag_count": len(hashtags),
                        "er_percentage": row["er_percentage"],
                        "hashtags": hashtags,
                    }
                )

        if hashtag_analysis:
            hashtag_df = pd.DataFrame(hashtag_analysis)

            # ハッシュタグ数の分析
            hashtag_count_stats = (
                hashtag_df.groupby("hashtag_count")["er_percentage"].agg(["mean", "count"]).round(2)
            )
            hashtag_count_stats = hashtag_count_stats[
                hashtag_count_stats["count"] >= 2
            ]  # 2回以上使用されたもののみ

            if not hashtag_count_stats.empty:
                best_hashtag_count = hashtag_count_stats["mean"].idxmax()
                best_er = hashtag_count_stats.loc[best_hashtag_count, "mean"]
                content_analysis["hashtag_patterns"]["optimal_count"] = {
                    "count": best_hashtag_count,
                    "avg_er": best_er,
                }

            # 個別ハッシュタグの効果分析
            all_hashtags = []
            for hashtags in hashtag_df["hashtags"]:
                all_hashtags.extend(hashtags)

            hashtag_er_data = []
            for _, row in hashtag_df.iterrows():
                for tag in row["hashtags"]:
                    hashtag_er_data.append({"hashtag": tag, "er": row["er_percentage"]})

            if hashtag_er_data:
                tag_df = pd.DataFrame(hashtag_er_data)
                tag_stats = tag_df.groupby("hashtag")["er"].agg(["mean", "count"]).round(2)
                tag_stats = tag_stats[tag_stats["count"] >= 2]  # 2回以上使用されたハッシュタグのみ

                if not tag_stats.empty:
                    # 効果的なハッシュタグ（上位5位）
                    effective_tags = tag_stats.nlargest(5, "mean")
                    content_analysis["hashtag_patterns"]["effective_tags"] = effective_tags.to_dict("index")

                    # 効果の低いハッシュタグ（下位5位）
                    ineffective_tags = tag_stats.nsmallest(5, "mean")
                    content_analysis["hashtag_patterns"]["ineffective_tags"] = ineffective_tags.to_dict(
                        "index"
                    )

    # 時間帯パターンの詳細分析
    if "hour" in df.columns:
        hourly_stats = df.groupby("hour")["er_percentage"].agg(["mean", "count"]).round(2)
        hourly_stats = hourly_stats[hourly_stats["count"] >= 2]  # 2回以上投稿された時間帯のみ

        if not hourly_stats.empty:
            # 時間帯をカテゴリに分類
            time_categories = {
                "morning": [6, 7, 8, 9, 10, 11],
                "afternoon": [12, 13, 14, 15, 16, 17],
                "evening": [18, 19, 20, 21, 22, 23],
                "night": [0, 1, 2, 3, 4, 5],
            }

            category_performance = {}
            for category, hours in time_categories.items():
                category_data = hourly_stats[hourly_stats.index.isin(hours)]
                if not category_data.empty:
                    category_performance[category] = {
                        "avg_er": category_data["mean"].mean(),
                        "post_count": category_data["count"].sum(),
                        "best_hour": category_data["mean"].idxmax(),
                    }

            content_analysis["time_patterns"] = category_performance

    # エンゲージメント率の分布分析
    er_stats = df["er_percentage"].describe()
    content_analysis["engagement_patterns"] = {
        "mean": er_stats["mean"],
        "median": er_stats["50%"],
        "std": er_stats["std"],
        "high_performers": len(df[df["er_percentage"] > er_stats["75%"]]),
        "low_performers": len(df[df["er_percentage"] < er_stats["25%"]]),
    }

    return content_analysis


def generate_content_recommendations(df):
    """内容分析に基づく具体的な改善提案を生成"""
    if df.empty or "er_percentage" not in df.columns:
        return {"error": "データが不足しています"}

    content_analysis = analyze_content_patterns(df)
    if "error" in content_analysis:
        return content_analysis

    recommendations = []

    # ハッシュタグ戦略の提案
    if "hashtag_patterns" in content_analysis and content_analysis["hashtag_patterns"]:
        patterns = content_analysis["hashtag_patterns"]

        if "optimal_count" in patterns:
            optimal_count = patterns["optimal_count"]["count"]
            avg_er = patterns["optimal_count"]["avg_er"]
            recommendations.append(
                {
                    "category": "ハッシュタグ戦略",
                    "title": f"最適なハッシュタグ数の活用",
                    "description": f"ハッシュタグ{optimal_count}個使用時の平均ERは{avg_er}%で最も高いパフォーマンスを示しています。",
                    "recommendation": f"投稿には{optimal_count}個程度のハッシュタグを使用することをお勧めします。",
                    "priority": "高",
                    "action_items": [
                        f"ハッシュタグを{optimal_count}個に調整する",
                        "効果の低いハッシュタグを削除する",
                        "効果的なハッシュタグを優先的に使用する",
                    ],
                }
            )

        if "effective_tags" in patterns and patterns["effective_tags"]:
            effective_tags = list(patterns["effective_tags"].keys())[:3]  # 上位3位
            recommendations.append(
                {
                    "category": "ハッシュタグ戦略",
                    "title": "効果的なハッシュタグの積極活用",
                    "description": f"#{', #'.join(effective_tags)}などのハッシュタグが高いエンゲージメント率を示しています。",
                    "recommendation": "これらのハッシュタグを積極的に使用し、投稿内容に合わせて組み合わせることをお勧めします。",
                    "priority": "中",
                    "action_items": [
                        f"#{effective_tags[0]}をメインハッシュタグとして使用",
                        f"#{effective_tags[1]}と#{effective_tags[2]}をサブハッシュタグとして組み合わせ",
                        "効果の低いハッシュタグを避ける",
                    ],
                }
            )

    # 時間帯戦略の提案
    if "time_patterns" in content_analysis and content_analysis["time_patterns"]:
        time_patterns = content_analysis["time_patterns"]

        # 最も効果的な時間帯カテゴリを見つける
        best_category = max(time_patterns.keys(), key=lambda x: time_patterns[x]["avg_er"])
        best_er = time_patterns[best_category]["avg_er"]
        best_hour = time_patterns[best_category]["best_hour"]

        category_names = {
            "morning": "朝（6-11時）",
            "afternoon": "午後（12-17時）",
            "evening": "夕方（18-23時）",
            "night": "夜間（0-5時）",
        }

        recommendations.append(
            {
                "category": "投稿時間戦略",
                "title": f"最適な時間帯での投稿",
                "description": f"{category_names[best_category]}の平均ERは{best_er}%で最も高いパフォーマンスを示しています。特に{best_hour}時が最も効果的です。",
                "recommendation": f"重要な投稿は{category_names[best_category]}、特に{best_hour}時頃に投稿することをお勧めします。",
                "priority": "高",
                "action_items": [
                    f"投稿スケジュールを{category_names[best_category]}に調整",
                    f"特に{best_hour}時を投稿のゴールデンタイムとして設定",
                    "投稿前の時間帯分析を継続的に実施",
                ],
            }
        )

    # エンゲージメント率の改善提案
    if "engagement_patterns" in content_analysis:
        patterns = content_analysis["engagement_patterns"]
        mean_er = patterns["mean"]
        median_er = patterns["median"]

        if mean_er < 3.0:  # 業界平均を下回る場合
            recommendations.append(
                {
                    "category": "コンテンツ戦略",
                    "title": "エンゲージメント率の全体的な向上",
                    "description": f"現在の平均ERは{mean_er:.1f}%で、業界平均（3%）を下回っています。中央値は{median_er:.1f}%です。",
                    "recommendation": "投稿の質を向上させ、フォロワーとの関係性を深めるコンテンツを投稿することをお勧めします。",
                    "priority": "高",
                    "action_items": [
                        "ストーリーテリングを重視したコンテンツ作成",
                        "フォロワーとの双方向コミュニケーションを促進",
                        "視覚的に魅力的な画像・動画の使用",
                        "キャプションで質問を投げかけてコメントを促進",
                    ],
                }
            )
        elif mean_er > 5.0:  # 業界平均を大きく上回る場合
            recommendations.append(
                {
                    "category": "コンテンツ戦略",
                    "title": "優秀なパフォーマンスの維持・向上",
                    "description": f"現在の平均ERは{mean_er:.1f}%で、業界平均を大きく上回っています。",
                    "recommendation": "現在の戦略を継続し、さらに高パフォーマンスな投稿のパターンを分析して活用してください。",
                    "priority": "低",
                    "action_items": [
                        "高パフォーマンス投稿の成功要因を詳細分析",
                        "成功パターンを他の投稿にも適用",
                        "フォロワーの反応を継続的にモニタリング",
                    ],
                }
            )

    # 投稿頻度の最適化提案
    if "posted_at" in df.columns:
        df["posted_at"] = pd.to_datetime(df["posted_at"])
        df["date"] = df["posted_at"].dt.date
        daily_posts = df.groupby("date").size()

        if len(daily_posts) > 1:
            avg_daily_posts = daily_posts.mean()

            if avg_daily_posts < 0.5:  # 2日に1回未満
                recommendations.append(
                    {
                        "category": "投稿頻度戦略",
                        "title": "投稿頻度の最適化",
                        "description": f"現在の投稿頻度は1日平均{avg_daily_posts:.1f}回です。",
                        "recommendation": "投稿頻度を増やすことで、フォロワーとの接触機会を増やし、エンゲージメント率の向上が期待できます。",
                        "priority": "中",
                        "action_items": [
                            "週3-4回の投稿頻度を目標に設定",
                            "投稿スケジュールを事前に計画",
                            "定期的な投稿でフォロワーの期待値を管理",
                        ],
                    }
                )
            elif avg_daily_posts > 2:  # 1日2回以上
                recommendations.append(
                    {
                        "category": "投稿頻度戦略",
                        "title": "投稿頻度の最適化",
                        "description": f"現在の投稿頻度は1日平均{avg_daily_posts:.1f}回です。",
                        "recommendation": "過度な投稿はフォロワーの関心を削ぐ可能性があります。質の高いコンテンツに集中することをお勧めします。",
                        "priority": "低",
                        "action_items": [
                            "投稿頻度を1日1回程度に調整",
                            "質の高いコンテンツの作成に集中",
                            "投稿間隔を適切に保つ",
                        ],
                    }
                )

    return {
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "high_priority": len([r for r in recommendations if r["priority"] == "高"]),
        "medium_priority": len([r for r in recommendations if r["priority"] == "中"]),
        "low_priority": len([r for r in recommendations if r["priority"] == "低"]),
        "content_analysis": content_analysis,
    }


def generate_improvement_suggestions(df):
    """エンゲージメント率向上のための改善提案を生成"""
    if df.empty or "er_percentage" not in df.columns:
        return {"error": "データが不足しています"}

    suggestions = []

    # 1. 時間帯分析
    if "hour" in df.columns:
        hourly_stats = df.groupby("hour")["er_percentage"].agg(["mean", "count"]).round(2)
        best_hour = hourly_stats["mean"].idxmax()
        worst_hour = hourly_stats["mean"].idxmin()
        best_er = hourly_stats.loc[best_hour, "mean"]
        worst_er = hourly_stats.loc[worst_hour, "mean"]

        if best_er > worst_er * 1.2:  # 20%以上の差がある場合
            suggestions.append(
                {
                    "category": "時間帯",
                    "title": f"投稿時間の最適化",
                    "description": f"{best_hour}時の平均ERは{best_er}%で、{worst_hour}時の{worst_er}%より{((best_er/worst_er-1)*100):.1f}%高いです。",
                    "recommendation": f"投稿を{best_hour}時頃に集中させることで、エンゲージメント率の向上が期待できます。",
                    "priority": "高",
                }
            )

    # 2. 曜日分析
    if "weekday" in df.columns:
        weekday_stats = df.groupby("weekday")["er_percentage"].agg(["mean", "count"]).round(2)
        best_weekday = weekday_stats["mean"].idxmax()
        worst_weekday = weekday_stats["mean"].idxmin()
        best_er = weekday_stats.loc[best_weekday, "mean"]
        worst_er = weekday_stats.loc[worst_weekday, "mean"]

        weekday_jp = {
            "Monday": "月曜日",
            "Tuesday": "火曜日",
            "Wednesday": "水曜日",
            "Thursday": "木曜日",
            "Friday": "金曜日",
            "Saturday": "土曜日",
            "Sunday": "日曜日",
        }

        if best_er > worst_er * 1.15:  # 15%以上の差がある場合
            suggestions.append(
                {
                    "category": "曜日",
                    "title": f"投稿曜日の最適化",
                    "description": f"{weekday_jp.get(best_weekday, best_weekday)}の平均ERは{best_er}%で、{weekday_jp.get(worst_weekday, worst_weekday)}の{worst_er}%より{((best_er/worst_er-1)*100):.1f}%高いです。",
                    "recommendation": f"重要な投稿は{weekday_jp.get(best_weekday, best_weekday)}に投稿することをお勧めします。",
                    "priority": "中",
                }
            )

    # 3. ハッシュタグ分析
    if "hashtags" in df.columns:
        # ハッシュタグとERの関係を分析
        hashtag_er_data = []
        for _, row in df.iterrows():
            if pd.notna(row["hashtags"]) and pd.notna(row["er_percentage"]):
                hashtags = [
                    tag.strip().lower().replace("#", "")
                    for tag in str(row["hashtags"]).split(",")
                    if tag.strip()
                ]
                for tag in hashtags:
                    hashtag_er_data.append({"hashtag": tag, "er": row["er_percentage"]})

        if hashtag_er_data:
            hashtag_df = pd.DataFrame(hashtag_er_data)
            hashtag_avg = hashtag_df.groupby("hashtag")["er"].agg(["mean", "count"]).round(2)
            hashtag_avg = hashtag_avg[hashtag_avg["count"] >= 2]  # 2回以上使用されたハッシュタグのみ

            if not hashtag_avg.empty:
                best_hashtag = hashtag_avg["mean"].idxmax()
                best_hashtag_er = hashtag_avg.loc[best_hashtag, "mean"]
                worst_hashtag = hashtag_avg["mean"].idxmin()
                worst_hashtag_er = hashtag_avg.loc[worst_hashtag, "mean"]

                if best_hashtag_er > worst_hashtag_er * 1.3:  # 30%以上の差がある場合
                    suggestions.append(
                        {
                            "category": "ハッシュタグ",
                            "title": f"ハッシュタグ戦略の見直し",
                            "description": f"#{best_hashtag}の平均ERは{best_hashtag_er}%で、#{worst_hashtag}の{worst_hashtag_er}%より{((best_hashtag_er/worst_hashtag_er-1)*100):.1f}%高いです。",
                            "recommendation": f"#{best_hashtag}のような効果的なハッシュタグを積極的に使用し、効果の低いハッシュタグは避けることをお勧めします。",
                            "priority": "中",
                        }
                    )

    # 4. エンゲージメント率の全体的な分析
    avg_er = df["er_percentage"].mean()
    if avg_er < 3.0:  # 業界平均の3%を下回る場合
        suggestions.append(
            {
                "category": "全体的な改善",
                "title": "エンゲージメント率の向上",
                "description": f"現在の平均ERは{avg_er:.1f}%で、Instagramの業界平均（3%）を下回っています。",
                "recommendation": "投稿の質を向上させ、フォロワーとの関係性を深めるコンテンツを投稿することをお勧めします。",
                "priority": "高",
            }
        )
    elif avg_er > 5.0:  # 5%を超える場合
        suggestions.append(
            {
                "category": "全体的な改善",
                "title": "優秀なパフォーマンス",
                "description": f"現在の平均ERは{avg_er:.1f}%で、業界平均を大きく上回っています。",
                "recommendation": "現在の戦略を継続し、さらに高パフォーマンスな投稿のパターンを分析して活用してください。",
                "priority": "低",
            }
        )

    # 5. 投稿頻度の分析
    if "posted_at" in df.columns:
        df["posted_at"] = pd.to_datetime(df["posted_at"])
        df["date"] = df["posted_at"].dt.date
        daily_posts = df.groupby("date").size()

        if len(daily_posts) > 1:
            avg_daily_posts = daily_posts.mean()
            if avg_daily_posts < 0.5:  # 2日に1回未満
                suggestions.append(
                    {
                        "category": "投稿頻度",
                        "title": "投稿頻度の増加",
                        "description": f"現在の投稿頻度は1日平均{avg_daily_posts:.1f}回です。",
                        "recommendation": "投稿頻度を増やすことで、フォロワーとの接触機会を増やし、エンゲージメント率の向上が期待できます。",
                        "priority": "中",
                    }
                )
            elif avg_daily_posts > 2:  # 1日2回以上
                suggestions.append(
                    {
                        "category": "投稿頻度",
                        "title": "投稿頻度の最適化",
                        "description": f"現在の投稿頻度は1日平均{avg_daily_posts:.1f}回です。",
                        "recommendation": "過度な投稿はフォロワーの関心を削ぐ可能性があります。質の高いコンテンツに集中することをお勧めします。",
                        "priority": "低",
                    }
                )

    return {
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
        "high_priority": len([s for s in suggestions if s["priority"] == "高"]),
        "medium_priority": len([s for s in suggestions if s["priority"] == "中"]),
        "low_priority": len([s for s in suggestions if s["priority"] == "低"]),
    }
