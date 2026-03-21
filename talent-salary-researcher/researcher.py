"""
人才寻访与薪酬对标
"""
import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ResumeData:
    name: str
    current_company: str = ""
    current_title: str = ""
    work_years: int = 0
    education: str = ""
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    skills: list = None
    location: str = ""
    update_date: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
    
    @property
    def expected_salary(self):
        if self.expected_salary_min and self.expected_salary_max:
            return (self.expected_salary_min, self.expected_salary_max)
        return None


SKILL_KEYWORDS = {
    "python": ["Python", "Django", "FastAPI", "Flask"],
    "java": ["Java", "Spring", "SpringBoot"],
    "go": ["Go", "Golang"],
    "frontend": ["React", "Vue", "Angular", "前端"],
    "backend": ["后端", "服务端"],
    "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
    "cloud": ["AWS", "阿里云", "腾讯云", "Kubernetes", "Docker"],
    "ai": ["AI", "Machine Learning", "深度学习", "NLP"],
}


def parse_jd_for_skills(jd_text: str) -> dict:
    """从JD中提取关键信息"""
    skills = []
    jd_upper = jd_text.upper()
    
    for category, keywords in SKILL_KEYWORDS.items():
        for kw in keywords:
            if kw.upper() in jd_upper:
                skills.append(kw)
    
    # 提取工作年限
    import re
    years_match = re.search(r'(\d+)\+?\s*年', jd_text)
    min_years = int(years_match.group(1)) if years_match else 0
    
    # 提取薪资范围
    salary_match = re.search(r'(\d+)[Kk]-(\d+)[Kk]', jd_text)
    if salary_match:
        salary_range = (int(salary_match.group(1)), int(salary_match.group(2)))
    else:
        salary_range = None
    
    # 提取学历
    education_levels = ["博士", "硕士", "本科", "大专", "高中"]
    education = None
    for edu in education_levels:
        if edu in jd_text:
            education = edu
            break
    
    # 提取城市
    cities = ["北京", "上海", "深圳", "广州", "杭州", "成都", "武汉", "南京"]
    location = None
    for city in cities:
        if city in jd_text:
            location = city
            break
    
    # 提取职位名称
    title_match = re.search(r'(高级|资深|中级|初级)?\s*([\u4e00-\u9fa5]+\w*)\s*(工程师|开发|设计|经理|总监)', jd_text)
    if title_match:
        title = title_match.group(0)
    else:
        title = "未知职位"
    
    return {
        "title": title,
        "skills": list(set(skills)),
        "min_years": min_years,
        "education": education or "本科",
        "location": location or "未知",
        "salary_range": salary_range,
        "headcount": 1
    }


def benchmark_salary(
    position: str,
    level: str,
    city: str,
    industry: str = "互联网",
    mock_data: bool = True
) -> dict:
    """薪酬对标"""
    # 模拟市场数据
    market_data = [
        25000, 28000, 30000, 32000, 35000, 38000, 40000,
        42000, 45000, 48000, 50000, 55000, 60000, 70000
    ]
    
    if mock_data:
        market_data = [m * (0.8 + hash(position) % 40 / 100) for m in market_data]
    
    sorted_data = sorted(market_data)
    n = len(sorted_data)
    
    def percentile(data, p):
        idx = int(len(data) * p)
        return data[min(idx, len(data) - 1)]
    
    p25 = percentile(sorted_data, 0.25)
    p50 = percentile(sorted_data, 0.50)
    p75 = percentile(sorted_data, 0.75)
    
    level_factors = {
        "entry": 0.7,
        "junior": 0.85,
        "mid": 1.0,
        "senior": 1.2,
        "expert": 1.5
    }
    
    factor = level_factors.get(level, 1.0)
    base = p50 * factor
    
    return {
        "position": position,
        "level": level,
        "city": city,
        "industry": industry,
        "market_data": {
            "p25": round(p25),
            "p50": round(p50),
            "p75": round(p75),
            "sample_size": len(market_data)
        },
        "recommendation": {
            "low": round(base * 0.9 / 1000) * 1000,
            "mid": round(base / 1000) * 1000,
            "high": round(base * 1.1 / 1000) * 1000
        },
        "unit": "K/月"
    }


def filter_candidates(
    resumes: list,
    requirements: dict
) -> list:
    """筛选候选人"""
    filtered = []
    
    required_skills = set(requirements.get("skills", []))
    
    for resume in resumes:
        score = 0
        
        # 技能匹配
        resume_skills = set(resume.skills) if isinstance(resume.skills, list) else set()
        if required_skills:
            skill_match = len(required_skills & resume_skills) / len(required_skills)
            score += skill_match * 40
        else:
            score += 20
        
        # 工作年限
        min_years = requirements.get("min_years", 0)
        max_years = requirements.get("max_years", 99)
        if min_years <= resume.work_years <= max_years:
            score += 20
        
        # 学历
        edu_levels = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
        req_edu = edu_levels.get(requirements.get("min_education", "本科"), 2)
        res_edu = edu_levels.get(resume.education, 1)
        if res_edu >= req_edu:
            score += 15
        
        # 期望薪资
        if resume.expected_salary and requirements.get("salary_range"):
            exp_min, exp_max = resume.expected_salary
            budget_min, budget_max = requirements["salary_range"]
            if exp_min <= budget_max * 1.2:
                score += 15
        
        # 地点
        if resume.location == requirements.get("location"):
            score += 10
        
        resume.match_score = score
        if score >= 50:
            filtered.append(resume)
    
    return sorted(filtered, key=lambda x: x.match_score, reverse=True)


if __name__ == "__main__":
    # Demo
    jd = """
    高级Python开发工程师
    
    岗位要求：
    - 5年+ Python开发经验
    - 熟悉FastAPI、Django
    - 本科及以上学历
    - 深圳南山
    
    薪资：30K-50K
    """
    
    jd_info = parse_jd_for_skills(jd)
    print("JD解析:", json.dumps(jd_info, ensure_ascii=False, indent=2))
    
    benchmark = benchmark_salary("Python开发", "senior", "深圳")
    print("\n薪酬对标:", json.dumps(benchmark, ensure_ascii=False, indent=2))
