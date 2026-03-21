---
name: talent-salary-researcher
description: Use when researching candidate resumes from Chinese job platforms, benchmarking salaries for positions, or generating recruitment salary reports
---

# Talent & Salary Researcher

## Overview

在招聘网站（Boss直聘、猎聘、智联招聘等）自动抓取候选人简历，收集同行业薪酬数据，生成薪资对标报告。

## When to Use

**触发条件：**
- 招聘季需快速筛选大量简历
- 新岗位定薪需要市场薪酬数据
- 年度调薪需要薪酬对标
- 竞争对手人才分布研究

**不适用：**
- 高管猎头（建议专业猎头）
- 紧急招聘（速度优先）

## 支持平台

| 平台 | 域名 | 数据类型 |
|------|------|----------|
| Boss直聘 | zhipin.com | 简历、薪资范围 |
| 猎聘 | liepin.com | 高端人才 |
| 智联招聘 | zhaopin.com | 综合简历 |
| 前程无忧 | 51job.com | 综合简历 |
| 拉勾网 | lagou.com | 互联网人才 |
| 脉脉 | maimai.cn | 职场社交、薪资 |

## 薪酬数据来源

| 来源 | 数据类型 | 可靠性 |
|------|----------|--------|
| 薪智 | 行业薪酬报告 | 高（付费） |
| 看准网 | 员工自报薪资 | 中 |
| 智联薪酬报告 | 年度报告 | 高 |
| 猎聘薪酬报告 | 行业报告 | 高 |
| 面试候选人 | 期望薪资 | 参考 |

## 抓取字段

```python
class ResumeData:
    name: str              # 姓名（脱敏处理）
    current_company: str   # 当前公司
    current_title: str     # 当前职位
    work_years: int        # 工作年限
    education: str          # 学历
    expected_salary: tuple # 期望薪资范围 (min, max)
    skills: list[str]      # 技能标签
    location: str          # 所在城市
    update_date: str       # 更新日期
```

## JD解析

```python
def parse_jd_for_skills(jd_text: str) -> dict:
    """从JD中提取关键信息"""
    return {
        "title": "高级Python开发工程师",
        "department": "技术部",
        "location": "深圳",
        "requirements": [
            "Python", "FastAPI", "PostgreSQL",
            "5年+经验", "本科+
        ],
        "nice_to_have": ["Kubernetes", "AWS"],
        "salary_range": (30, 50),  # K/月
        "headcount": 2
    }
```

## 薪酬对标算法

```python
def benchmark_salary(
    target_position: str,
    target_level: str,
    target_city: str,
    target_industry: str = "互联网"
) -> dict:
    """
    薪酬对标核心算法
    """
    # 从数据源获取市场数据
    market_data = fetch_market_salary(
        position=target_position,
        city=target_city,
        industry=target_industry
    )
    
    # 计算P25/P50/P75分位
    p25 = percentile(market_data, 0.25)
    p50 = percentile(market_data, 0.50)
    p75 = percentile(market_data, 0.75)
    
    # 根据级别确定建议薪资
    level_factors = {
        "entry": 0.7,      # 校招
        "junior": 0.85,    # 1-3年
        "mid": 1.0,        # 3-5年
        "senior": 1.2,     # 5-8年
        "expert": 1.5      # 8年+
    }
    
    base = p50 * level_factors.get(target_level, 1.0)
    
    return {
        "position": target_position,
        "level": target_level,
        "city": target_city,
        "market_data": {
            "p25": p25,
            "p50": p50,
            "p75": p75,
            "sample_size": len(market_data)
        },
        "recommendation": {
            "low": base * 0.9,
            "mid": base,
            "high": base * 1.1
        }
    }
```

## 报告生成

```markdown
# 薪酬对标报告

**岗位:** 高级Python开发工程师
**级别:** 3-5年（Mid-Level）
**城市:** 深圳
**行业:** 互联网/电商
**生成时间:** 2026-03-21

## 市场数据

| 分位 | 月薪 | 年薪（14薪） |
|------|------|--------------|
| P25 | ¥35,000 | ¥490,000 |
| P50 | ¥42,000 | ¥588,000 |
| P75 | ¥55,000 | ¥770,000 |

## 建议薪资

| 候选层级 | 建议月薪 | 建议年薪 | 说明 |
|----------|----------|----------|------|
| 入门 | ¥30,000 | ¥420,000 | P25左右 |
| 中等 | ¥42,000 | ¥588,000 | P50，市场中间 |
| 优秀 | ¥50,000 | ¥700,000 | P75-80 |

## 竞争态势

- 深圳Python岗位竞争指数: 7.2/10
- 平均招聘周期: 25天
- 候选人期望 vs 市场: +15%
```

## 候选人筛选

```python
def filter_candidates(
    resumes: list[ResumeData],
    requirements: dict
) -> list[ResumeData]:
    """根据需求筛选候选人"""
    filtered = []
    
    for resume in resumes:
        score = 0
        
        # 技能匹配
        required_skills = set(requirements.get("skills", []))
        resume_skills = set(resume.skills)
        skill_match = len(required_skills & resume_skills) / len(required_skills)
        score += skill_match * 40
        
        # 工作年限
        if requirements.get("min_years", 0) <= resume.work_years <= requirements.get("max_years", 99):
            score += 20
        
        # 学历
        education_levels = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
        if education_levels.get(resume.education, 0) >= education_levels.get(requirements.get("min_education", "本科"), 2):
            score += 15
        
        # 期望薪资
        if resume.expected_salary:
            exp_min, exp_max = resume.expected_salary
            budget_min, budget_max = requirements.get("salary_range", (0, 999999))
            if exp_min <= budget_max and exp_max >= budget_min:
                score += 15
        
        # 地点
        if resume.location == requirements.get("location"):
            score += 10
        
        resume.match_score = score
        if score >= 60:
            filtered.append(resume)
    
    return sorted(filtered, key=lambda x: x.match_score, reverse=True)
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 只看简历不验证 | 建议安排面试核实 |
| 薪资期望过高 | 可考虑股权/期权补充 |
| 忽略城市差异 | 北上深 vs 二线城市差异大 |
| 技能要求过多 | 聚焦3-5个核心技能 |
| 忽视软技能 | 沟通、团队协作同样重要 |

## 质量检查表

- [ ] JD关键技能已提取
- [ ] 市场薪酬数据来源标注
- [ ] 建议薪资有P50分位参考
- [ ] 候选人列表有匹配分数
- [ ] 报告包含数据时效性说明
