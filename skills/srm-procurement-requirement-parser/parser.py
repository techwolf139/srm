"""
采购需求解析器 - 将非结构化文本转为标准BOM
"""
import json
import re
from typing import Optional


# Category taxonomy for classification
CATEGORY_KEYWORDS = {
    "IT设备": ["电脑", "笔记本", "显示器", "主机", "服务器", "键盘", "鼠标", "耳机"],
    "办公外设": ["打印机", "扫描仪", "投影仪", "复印机", "传真机"],
    "办公家具": ["办公桌", "椅子", "文件柜", "书架", "会议桌", "储物柜"],
    "办公用品": ["纸张", "笔", "本子", "文件夹", "订书机", "胶带"],
    "数码配件": ["手机壳", "充电宝", "数据线", "U盘", "移动硬盘"],
    "工具/仪器": ["万用表", "螺丝刀", "工具箱", "仪器", "测量仪"],
}


def classify_category(item_name: str) -> str:
    """根据物品名称推断分类"""
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in item_name:
                return category
    return "其他"


def parse_requirement_text(
    text: str,
    department: Optional[str] = None,
    requester: Optional[str] = None,
    llm_client=None,
) -> dict:
    """
    解析非结构化采购需求文本

    Args:
        text: 非结构化文本（如微信聊天记录、邮件正文）
        department: 部门（可从上下文推断）
        requester: 申请人（可从上下文推断）
        llm_client: LLM客户端（支持openai兼容接口）

    Returns:
        dict: 结构化BOM
    """
    if llm_client is None:
        # Fallback: rule-based parsing
        return _rule_based_parse(text, department, requester)

    # LLM-based parsing
    prompt = f"""你是一个采购需求解析专家。请从以下非结构化文本中提取采购需求，输出JSON格式：

输入文本：
{text}

要求：
1. 提取所有采购物品，物品名称尽量具体
2. 从上下文推断数量（如果未明确，设为1）
3. 推断预算范围（如果未明确，设为null）
4. 提取特殊要求（如"手感好"、"品牌好"）到requirements数组
5. 判断优先级：quality（质量优先）、price（价格优先）、balanced（均衡）
6. 推断部门（如果未明确，从上下文判断或设为null）

输出格式（仅JSON，无其他内容）：
{{
  "items": [{{
    "rank": 1,
    "item_name": "物品名称",
    "category": "分类",
    "quantity": 数量,
    "unit": "单位",
    "budget_max": null或数字,
    "requirements": ["特殊要求"],
    "brand_preference": null或品牌,
    "priority": "quality|price|balanced"
  }}],
  "department": "部门或null",
  "urgency": "normal|urgent|low",
  "budget_total": null或总预算,
  "notes": "备注"
}}"""

    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    result = json.loads(response.choices[0].message.content)
    return result


def _rule_based_parse(text: str, department: Optional[str], requester: Optional[str]) -> dict:
    """基于规则的解析（无LLM时使用）"""
    items = []

    # Extract quantity patterns
    quantity_pattern = r"(\d+)(?:台|个|套|件|把|个)?"
    quantities = re.findall(r"\d+", text)

    # Extract budget patterns
    budget_match = re.search(r"预算[是为]?\s*(\d+(?:\.\d+)?)\s*(?:元|以内|以下)?", text)
    budget_total = float(budget_match.group(1)) if budget_match else None

    # Extract requirements
    requirements = []
    if "好" in text:
        if "手感" in text:
            requirements.append("手感好")
        if "质量" in text or "品质" in text:
            requirements.append("质量好")
        if "品牌" in text:
            requirements.append("品牌好")
        if "外观" in text or "好看" in text:
            requirements.append("外观好看")

    # Infer priority
    if any(kw in text for kw in ["便宜", "省钱", "预算", "性价比"]):
        priority = "price"
    elif any(kw in text for kw in ["质量", "好", "专业", "品牌"]):
        priority = "quality"
    else:
        priority = "balanced"

    # Extract item name (simplified)
    item_name = text.split("买")[1].split("，")[0].split("。")[0] if "买" in text else text[:20]

    # Classify category
    category = classify_category(item_name)

    items.append({
        "rank": 1,
        "item_name": item_name.strip(),
        "category": category,
        "quantity": int(quantities[0]) if quantities else 1,
        "unit": "台",
        "budget_max": None,
        "requirements": requirements,
        "brand_preference": None,
        "priority": priority,
    })

    return {
        "items": items,
        "department": department,
        "requester": requester,
        "urgency": "normal",
        "budget_total": budget_total,
        "notes": "",
    }


def format_as_bom_table(parsed: dict) -> str:
    """格式化为BOM表格"""
    lines = ["# 采购需求清单\n"]
    lines.append(f"**部门:** {parsed.get('department', 'N/A')}  ")
    lines.append(f"**紧急度:** {parsed.get('urgency', 'normal')}  ")
    lines.append(f"**总预算:** {parsed.get('budget_total', '待定')}元\n")

    lines.append("| # | 物品名称 | 分类 | 数量 | 单位 | 预算上限 | 特殊要求 | 优先级 |")
    lines.append("|---|----------|------|------|------|----------|----------|--------|")

    for i, item in enumerate(parsed.get("items", []), 1):
        requirements = ", ".join(item.get("requirements", []) or ["无"])
        lines.append(
            f"| {i} | {item.get('item_name', 'N/A')} | {item.get('category', 'N/A')} | "
            f"{item.get('quantity', 1)} | {item.get('unit', '台')} | "
            f"{item.get('budget_max', '待定')} | {requirements} | {item.get('priority', 'balanced')} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    test_text = "我们需要给研发部买10台机械键盘，手感好一点的，预算5000以内"
    result = _rule_based_parse(test_text, "研发部", None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + format_as_bom_table(result))
