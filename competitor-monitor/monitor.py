"""
竞品动态与舆情监测
"""
import json
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class CompetitorPost:
    platform: str
    author: str
    content: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    posted_at: str = ""
    product_link: str = ""
    sentiment: str = "neutral"
    sentiment_score: float = 0.5
    topics: list = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []


@dataclass
class CompetitorData:
    name: str
    posts: list = None
    
    def __post_init__(self):
        if self.posts is None:
            self.posts = []
    
    def get_total_engagement(self) -> int:
        return sum(p.likes + p.comments * 2 + p.shares * 3 for p in self.posts)
    
    def get_sentiment_distribution(self) -> dict:
        dist = {"positive": 0, "negative": 0, "neutral": 0}
        for p in self.posts:
            dist[p.sentiment] = dist.get(p.sentiment, 0) + 1
        return dist


def generate_weekly_report(
    competitor_data: list[CompetitorData],
    start_date: str = None,
    end_date: str = None
) -> str:
    """生成竞品周报"""
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    lines = [f"# 竞品分析周报\n"]
    lines.append(f"**监控周期:** {start_date} ~ {end_date}\n")
    
    competitors = [d.name for d in competitor_data]
    lines.append(f"**竞品:** {', '.join(competitors)}\n")
    lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    # 概览表
    lines.append("\n## 一、本周动态概览\n")
    lines.append("| 竞品 | 帖子数 | 总互动 | 正面 | 负面 | 中性 |")
    lines.append("|------|--------|--------|------|------|------|")
    
    for data in competitor_data:
        eng = data.get_total_engagement()
        sent = data.get_sentiment_distribution()
        lines.append(f"| {data.name} | {len(data.posts)} | {eng:,} | {sent['positive']} | {sent['negative']} | {sent['neutral']} |")
    
    # 重点帖子
    lines.append("\n## 二、高互动帖子\n")
    for data in competitor_data:
        top_posts = sorted(data.posts, key=lambda x: x.likes + x.comments * 2, reverse=True)[:3]
        if top_posts:
            lines.append(f"\n### {data.name}\n")
            for p in top_posts:
                lines.append(f"- **[{p.platform}]** {p.content[:80]}...")
                lines.append(f"  - 点赞:{p.likes} 评论:{p.comments} 情感:{p.sentiment}")
    
    # 情感趋势
    lines.append("\n## 三、舆情分析\n")
    for data in competitor_data:
        sent = data.get_sentiment_distribution()
        total = len(data.posts) or 1
        pos_pct = sent['positive'] / total * 100
        neg_pct = sent['negative'] / total * 100
        lines.append(f"- **{data.name}**: 正面{pos_pct:.0f}% | 负面{neg_pct:.0f}%")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    posts_a = [
        CompetitorPost("小红书", "用户A", "这个产品真的很好用", likes=1200, comments=85, sentiment="positive"),
        CompetitorPost("微博", "官方账号", "新品发布 #XX话题#", likes=3500, comments=420, sentiment="neutral"),
        CompetitorPost("抖音", "测评达人", "不推荐这个", likes=200, comments=30, sentiment="negative"),
    ]
    
    data_a = CompetitorData(name="竞品A", posts=posts_a)
    
    report = generate_weekly_report([data_a])
    print(report)
