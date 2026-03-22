"""
供应商风险评估器
"""
import json
import time
from typing import Optional


TIANYANCHA_API_KEY = None
QICHACHA_API_KEY = None


def assess_supplier(
    supplier_name: str,
    use_mock: bool = True,
) -> dict:
    """
    评估单个供应商风险
    
    Args:
        supplier_name: 供应商/公司名称
        use_mock: 是否使用模拟数据（无API Key时）
    """
    if use_mock or not (TIANYANCHA_API_KEY or QICHACHA_API_KEY):
        return _mock_assessment(supplier_name)
    
    # 实际API调用
    # data = query_tianyancha(supplier_name)
    # data = query_qichacha(supplier_name)
    
    return _mock_assessment(supplier_name)


def _mock_assessment(supplier_name: str) -> dict:
    """模拟评估结果（用于测试）"""
    return {
        "supplier_name": supplier_name,
        "unified_credit_code": "91440300MA5DXXXXX",
        "risk_score": 25,
        "risk_level": "LOW",
        "dimensions": {
            "dishonest_count": 0,
            "litigation_count": 1,
            "abnormal_count": 0,
            "penalty_count": 0,
            "tax_abnormal": False,
            "registered_capital": "100万(实缴100万)",
            "established_date": "2018-05-15",
            "business_status": "存续"
        },
        "recommendation": "供应商可推荐",
        "details": [
            {"type": "litigation", "count": 1, "summary": "合同纠纷1起，已结案"}
        ],
        "data_sources": ["天眼查(模拟)", "国家企业信用信息公示系统(模拟)"],
        "checked_at": "2026-03-21T10:00:00+08:00"
    }


def assess_suppliers_from_csv(csv_path: str) -> list[dict]:
    """批量评估CSV中的供应商"""
    import pandas as pd
    
    df = pd.read_csv(csv_path)
    
    # 尝试找到供应商列
    supplier_col = None
    for col in ["supplier_name", "shop_name", "supplier", "店铺名称"]:
        if col in df.columns:
            supplier_col = col
            break
    
    if supplier_col is None:
        raise ValueError(f"CSV中未找到供应商列，可用列: {df.columns.tolist()}")
    
    results = []
    for name in df[supplier_col].unique():
        if pd.isna(name):
            continue
        result = assess_supplier(str(name))
        result["source_row"] = df[df[supplier_col] == name].iloc[0].to_dict()
        results.append(result)
        time.sleep(0.5)  # 避免请求过快
    
    return results


def calculate_risk_score(dimensions: dict) -> tuple[int, str]:
    """计算风险分数和等级"""
    score = 0
    score += dimensions.get("dishonest_count", 0) * 25
    score += dimensions.get("litigation_count", 0) * 20
    score += dimensions.get("abnormal_count", 0) * 20
    score += dimensions.get("penalty_count", 0) * 15
    if dimensions.get("tax_abnormal"):
        score += 10
    if dimensions.get("capital_unpaid", False):
        score += 10
    
    if score <= 30:
        level = "LOW"
    elif score <= 60:
        level = "MEDIUM"
    else:
        level = "HIGH"
    
    return min(score, 100), level


def generate_risk_report(assessments: list[dict], include_mock: bool = True) -> str:
    """生成Markdown风险评估报告"""
    if include_mock:
        assessments = [a for a in assessments if "模拟" not in str(a.get("data_sources", []))]
        if not assessments:
            assessments = [_mock_assessment("示例供应商")]
    
    lines = ["# 供应商风险评估报告\n"]
    lines.append(f"**生成时间:** {assessments[0]['checked_at'] if assessments else 'N/A'}\n")
    
    # 按风险等级分组
    high_risk = [a for a in assessments if a["risk_level"] == "HIGH"]
    medium_risk = [a for a in assessments if a["risk_level"] == "MEDIUM"]
    low_risk = [a for a in assessments if a["risk_level"] == "LOW"]
    
    lines.append(f"**汇总:** 高风险 {len(high_risk)} | 中风险 {len(medium_risk)} | 低风险 {len(low_risk)}\n")
    
    # 高风险供应商
    if high_risk:
        lines.append("\n## 🔴 高风险供应商（不推荐）\n")
        lines.append("| 供应商 | 风险分 | 主要风险 | 建议 |")
        lines.append("|--------|--------|----------|------|")
        for a in high_risk:
            details = "; ".join([d["summary"] for d in a.get("details", [])])
            lines.append(f"| {a['supplier_name']} | {a['risk_score']} | {details} | {a['recommendation']} |")
    
    # 中风险供应商
    if medium_risk:
        lines.append("\n## 🟡 中风险供应商（谨慎合作）\n")
        lines.append("| 供应商 | 风险分 | 主要风险 | 建议 |")
        lines.append("|--------|--------|----------|------|")
        for a in medium_risk:
            details = "; ".join([d["summary"] for d in a.get("details", [])])
            lines.append(f"| {a['supplier_name']} | {a['risk_score']} | {details} | {a['recommendation']} |")
    
    # 低风险供应商
    if low_risk:
        lines.append("\n## 🟢 低风险供应商（可推荐）\n")
        lines.append("| 供应商 | 风险分 | 成立时间 | 建议 |")
        lines.append("|--------|--------|----------|------|")
        for a in low_risk:
            est_date = a.get("dimensions", {}).get("established_date", "N/A")
            lines.append(f"| {a['supplier_name']} | {a['risk_score']} | {est_date} | {a['recommendation']} |")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    result = assess_supplier("深圳市xxx科技有限公司")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    report = generate_risk_report([result])
    print("\n" + report)
