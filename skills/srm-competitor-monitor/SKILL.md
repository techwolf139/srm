---
name: competitor-monitor
description: Use when monitoring competitor activities on Chinese social media (小红书, 抖音, 微博), tracking product launches, price changes, or generating competitor intelligence reports
---

# Competitor Monitor

## Overview

监控竞品在小红书、抖音、微博等平台的产品宣发、价格变化、用户评论，生成竞品分析周报。

## When to Use

**触发条件：**
- 竞品发布新品
- 竞品价格调整
- 每周竞品动态总结
- 危机舆情监控
- 重要营销活动追踪

**不适用：**
- 实时舆情告警（建议专业舆情系统）
- 全网覆盖（建议专业舆情服务商）

## 支持平台

| 平台 | 数据类型 | 抓取难度 |
|------|----------|----------|
| 小红书 | 种草笔记、商品链接、用户评论 | 中 |
| 抖音 | 短视频、直播、商品橱窗 | 高（需官方API） |
| 微博 | 品牌官微、话题、热搜 | 低 |
| 微信 | 公众号文章 | 中（需爬虫） |
| 什么值得买 | 优惠信息、商品历史价 | 低 |

## 监控维度

| 维度 | 指标 | 数据来源 |
|------|------|----------|
| 产品 | 新品发布、产品迭代 | 小红书、微博 |
| 价格 | 促销信息、到手价 | 什么值得买、京东 |
| 口碑 | 笔记数、点赞、评论 | 小红书、微博 |
| 营销 | 话题热度、投放力度 | 微博热搜、抖音挑战赛 |
| 舆情 | 正负面评价、投诉 | 全平台 |

## 数据抓取

```python
class CompetitorPost:
    platform: str       # 平台
    author: str         # 作者
    content: str        # 内容
    likes: int          # 点赞数
    comments: int       # 评论数
    shares: int         # 转发数
    posted_at: str      # 发布时间
    product_link: str   # 商品链接
    sentiment: str      # 情感倾向 (positive/negative/neutral)
    topics: list[str]   # 关联话题


def fetch_xiaohongshu(keyword: str, competitor: str) -> list[CompetitorPost]:
    """抓取小红书数据"""
    # 需要 Playwright 或 Appium
    pass


def fetch_weibo(brand_name: str) -> list[CompetitorPost]:
    """抓取微博数据"""
    # 官方API或网页抓取
    pass
```

## 情感分析

```python
def analyze_sentiment(text: str) -> dict:
    """情感分析"""
    # 使用LLM或专业情感分析API
    return {
        "sentiment": "positive",  # positive/negative/neutral
        "score": 0.85,            # 0-1
        "keywords": ["值得买", "推荐", "种草"],
        "negative_keywords": []
    }
```

## 竞品分析报告

```markdown
# 竞品分析周报

**监控周期:** 2026-03-15 ~ 2026-03-21
**竞品:** 竞品A、竞品B
**生成时间:** 2026-03-21 10:00

---

## 一、本周动态概览

| 竞品 | 产品上新 | 价格调整 | 营销活动 | 舆情概览 |
|------|----------|----------|----------|----------|
| 竞品A | 2款新品 | 降价10% | 618预热 | 正面为主 |
| 竞品B | 1款新品 | 无 | 话题营销 | 中性 |

---

## 二、重点关注

### 2.1 竞品A新品发布

**产品:** XX型号
**上市日期:** 2026-03-18
**定价:** ¥2999
**差异化:** 强调拍照、性能

**舆情反应:**
- 正面: 85% (用户评价积极)
- 中性: 10%
- 负面: 5% (吐槽价格)

**值得关注:** 对方强调"性价比"，可能对我们中端产品形成压力

---

## 三、价格监控

| 产品 | 竞品A | 竞品B | 我们 |
|------|-------|-------|------|
| 同类A | ¥2999 | ¥2899 | ¥3099 |
| 同类B | ¥1999 | ¥2099 | ¥1899 |

**结论:** 竞品B价格略低，需关注

---

## 四、营销活动

| 竞品 | 活动 | 平台 | 热度 |
|------|------|------|------|
| 竞品A | #XX话题 | 微博 | 500万 |
| 竞品B | 抖音挑战赛 | 抖音 | 1000万 |

---

## 五、建议

1. 竞品A新品定位中高端，建议加强我们产品的差异化宣传
2. 竞品B价格略低，可考虑调整赠品策略
3. 竞品A本周话题营销效果好，建议关注其持续性
```

## 定时任务配置

```python
# 每周一早上9点生成周报
CRON_SCHEDULE = "0 9 * * 1"

def weekly_report_task():
    """定时任务"""
    competitors = load_competitor_list()
    all_data = []
    
    for competitor in competitors:
        posts = fetch_all_platforms(competitor)
        all_data.extend(posts)
    
    report = generate_weekly_report(all_data)
    send_to_dingtalk(report)
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 数据样本太小 | 建议至少抓取100条数据 |
| 只看声量不看转化 | 关注评论区的真实反馈 |
| 忽视负面舆情 | 负面舆情可能是产品问题信号 |
| 抓取频率过高 | 遵守平台规则，避免IP封禁 |

## 质量检查表

- [ ] 数据来源平台标注
- [ ] 抓取时间范围明确
- [ ] 情感分析有依据
- [ ] 价格数据有截图/链接佐证
- [ ] 报告有明确结论和建议
