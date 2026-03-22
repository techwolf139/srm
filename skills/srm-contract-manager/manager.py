"""
合同管理器 - 合同生成与审核
"""
import json
import re
from datetime import datetime
from typing import Optional


# 企业红线条款配置
DEFAULT_RED_LINES = {
    "max_penalty_rate": 0.20,      # 最高违约金比例 20%
    "favorable_jurisdiction": True, # 管辖法院应有利于甲方
    "max_prepay_rate": 0.50,        # 最高预付比例 50%
    "ip_limitation": True,          # 知识产权应有限制
}


def generate_contract(
    purchase_info: dict,
    template: str = "standard_procurement",
    party_a: Optional[dict] = None,
) -> dict:
    """
    根据采购信息生成合同
    
    Args:
        purchase_info: 采购信息（含供应商、物品、金额等）
        template: 模板名称
        party_a: 甲方信息（采购方）
    """
    contract_no = f"CG-{datetime.now().strftime('%Y%m%d')}-{len(purchase_info.get('items', []))}"
    
    # 默认甲方信息（可从企业ERP获取）
    if party_a is None:
        party_a = {
            "name": "XX公司",
            "address": "XX市XX区XX路XX号",
            "contact": "采购部",
            "phone": "400-xxx-xxxx"
        }
    
    # 构建物品清单
    items_text = []
    total = 0
    for i, item in enumerate(purchase_info.get("items", []), 1):
        name = item.get("item_name", "")
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0)
        subtotal = qty * price
        total += subtotal
        items_text.append(f"{i}. {name} x {qty} @ ¥{price} = ¥{subtotal:.2f}")
    
    items_list_md = "\n".join(items_text)
    
    # 生成合同内容
    contract = f"""# 采购合同

**合同编号：** {contract_no}  
**签订日期：** {datetime.now().strftime('%Y年%m月%d日')}

---

## 甲方（采购方）

| 项目 | 内容 |
|------|------|
| 名称 | {party_a['name']} |
| 地址 | {party_a['address']} |
| 联系人 | {party_a['contact']} |
| 电话 | {party_a['phone']} |

## 乙方（供应商）

| 项目 | 内容 |
|------|------|
| 名称 | {purchase_info.get('supplier_name', '')} |
| 地址 | {purchase_info.get('supplier_address', '')} |
| 联系人 | {purchase_info.get('contact_person', '')} |
| 电话 | {purchase_info.get('contact_phone', '')} |

---

## 一、合同标的

乙方同意向甲方出售以下物品：

{items_list_md}

**合同总金额：¥{total:.2f}（大写：{num_to_chinese(total)}元）**

---

## 二、质量标准

{purchase_info.get('quality_standard', '符合国家相关质量标准及甲方要求')}

---

## 三、交付条款

- **交付日期：** {purchase_info.get('delivery_date', '甲方通知后7个工作日内')}
- **交付地点：** {purchase_info.get('delivery_address', party_a['address'])}
- **运输方式：** {purchase_info.get('shipping_method', '乙方负责运输，费用含在合同金额内')}

---

## 四、付款条款

- **付款方式：** {purchase_info.get('payment_terms', '验收后30天付款')}
- **发票类型：** 增值税{purchase_info.get('invoice_type', '普通')}发票
- **发票税率：** {purchase_info.get('tax_rate', '6')}%

---

## 五、验收标准

{purchase_info.get('acceptance_criteria', '按国家相关标准及甲方要求验收，如有问题收货后7日内提出')}

---

## 六、质保条款

- **质保期：** {purchase_info.get('warranty_period', '1年')}或 {purchase_info.get('warranty_conditions', '以验收合格日期起算')}
- **质保范围：** {purchase_info.get('warranty_scope', '非人为损坏的硬件故障')}

---

## 七、违约责任

1. 甲方逾期付款的，每逾期一日按合同金额的{purchase_info.get('late_payment_rate', '0.05')}向乙方支付违约金。
2. 乙方逾期交付的，每逾期一日按合同金额的{purchase_info.get('late_delivery_rate', '0.05')}向甲方支付违约金。
3. 违约金总额不超过合同金额的20%。
4. 因不可抗力导致合同无法履行的，双方协商解决。

---

## 八、争议解决

本合同适用中华人民共和国法律。如有争议，提交{purchase_info.get('jurisdiction', '甲方所在地人民法院')}管辖。

---

## 九、其他约定

{purchase_info.get('other_terms', '本合同一式两份，甲乙双方各执一份，具有同等法律效力。')}

---

## 签署页

| 甲方（签章） | 乙方（签章） |
|--------------|--------------|
| 签字：_______ | 签字：_______ |
| 日期：_______ | 日期：_______ |
| 盖章：_______ | 盖章：_______ |
"""
    
    return {
        "contract_no": contract_no,
        "contract_text": contract,
        "total_amount": total,
        "party_a": party_a,
        "party_b": purchase_info.get("supplier_name"),
        "generated_at": datetime.now().isoformat()
    }


def review_contract(
    contract_text: str,
    red_lines: dict = None,
) -> dict:
    """
    审核合同条款，识别风险点
    
    Args:
        contract_text: 合同文本
        red_lines: 红线条款配置
    """
    if red_lines is None:
        red_lines = DEFAULT_RED_LINES
    
    issues = []
    score = 0
    
    # 检查违约金比例
    penalty_matches = re.findall(r'([0-9.]+)%?', contract_text)
    for match in penalty_matches:
        rate = float(match) if '.' in match else int(match) / 100
        if rate > red_lines["max_penalty_rate"]:
            issues.append({
                "clause": f"违约金比例为{rate*100 if rate < 1 else rate}%",
                "issue": f"违约金比例超过{red_lines['max_penalty_rate']*100}%红线",
                "legal_ref": "《民法典》第585条：违约金不超过实际损失30%",
                "suggestion": f"建议调整为{red_lines['max_penalty_rate']*100}%以内",
                "severity": "HIGH"
            })
            score += 30
    
    # 检查管辖法院
    jurisdiction_patterns = [
        r'管辖法院[为:]?\s*([^，,。\n]+)',
        r'争议解决[,:]\s*([^，,。\n]+)',
    ]
    for pattern in jurisdiction_patterns:
        match = re.search(pattern, contract_text)
        if match:
            jurisdiction = match.group(1).strip()
            if "甲方" not in jurisdiction and "原告" not in jurisdiction:
                issues.append({
                    "clause": f"管辖法院为{jurisdiction}",
                    "issue": "管辖法院对甲方不利",
                    "legal_ref": "《民事诉讼法》第34条",
                    "suggestion": "建议改为原告所在地或合同签订地",
                    "severity": "MEDIUM"
                })
                score += 20
    
    # 检查预付款比例
    prepay_matches = re.findall(r'预付[款]?\s*[为:]?\s*([0-9.]+)%?', contract_text)
    for match in prepay_matches:
        rate = float(match) if '.' in match else int(match) / 100
        if rate > red_lines["max_prepay_rate"]:
            issues.append({
                "clause": f"预付款比例为{rate*100 if rate < 1 else rate}%",
                "issue": f"预付款比例超过{red_lines['max_prepay_rate']*100}%",
                "suggestion": f"建议预付款不超过{red_lines['max_prepay_rate']*100}%，或改为月结",
                "severity": "MEDIUM"
            })
            score += 15
    
    # 检查发票条款
    if "发票" not in contract_text:
        issues.append({
            "clause": "未明确发票条款",
            "issue": "缺少发票约定",
            "suggestion": "建议明确发票类型（增值税专用发票/普通发票）和税率",
            "severity": "LOW"
        })
        score += 5
    
    # 确定风险等级
    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    return {
        "overall_risk": level,
        "risk_score": min(score, 100),
        "clauses": issues,
        "summary": f"合同存在{len(issues)}个风险点，建议{'修改后再签署' if level != 'LOW' else '可接受'}",
        "reviewed_at": datetime.now().isoformat()
    }


def num_to_chinese(num: float) -> str:
    """数字转中文大写金额"""
    units = ['', '万', '仟', '佰', '拾', '元']
    digits = '零壹贰叁肆伍陆柒捌玖'
    
    if num >= 10000:
        return f"{int(num/10000)}万{int(num%10000)}元"
    
    result = []
    for i, c in enumerate(str(int(num))):
        idx = int(c)
        result.append(digits[idx])
        if i < len(str(int(num))) - 1:
            result.append(units[len(str(int(num))) - i - 1])
    return ''.join(result)


if __name__ == "__main__":
    # Demo
    purchase = {
        "supplier_name": "深圳市xxx科技有限公司",
        "contact_person": "张三",
        "contact_phone": "13800138000",
        "items": [
            {"item_name": "机械键盘", "quantity": 10, "unit_price": 299},
            {"item_name": "鼠标", "quantity": 10, "unit_price": 99}
        ],
        "payment_terms": "验收后30天付款",
        "delivery_date": "2026-04-15",
        "warranty_period": "1年"
    }
    
    result = generate_contract(purchase)
    print(f"合同编号: {result['contract_no']}")
    print(f"合同金额: ¥{result['total_amount']}")
    
    # 测试审核
    bad_contract = "违约金为合同金额的30%，管辖法院为乙方所在地，预付款50%"
    review = review_contract(bad_contract)
    print(json.dumps(review, ensure_ascii=False, indent=2))
