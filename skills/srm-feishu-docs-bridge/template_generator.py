"""合同文档模板生成"""
from datetime import datetime
from typing import Dict, Any


class ContractTemplateGenerator:
    """合同文档模板生成器"""

    @staticmethod
    def generate_contract_draft(title: str, contract_data: Dict[str, Any]) -> str:
        """生成合同草稿文档内容"""
        supplier_name = contract_data.get("supplier_name", "未知供应商")
        total_amount = contract_data.get("total_amount", 0)
        delivery_date = contract_data.get("delivery_date", "")
        
        content = f"""# 合同草書

## 一、合同基本信息

| 字段 | 内容 |
|------|------|
| 合同名称 | {title} |
| 供应商 | {supplier_name} |
| 合同金额 | ¥{total_amount:,.2f} |
| 签订日期 | {datetime.now().strftime('%Y-%m-%d')} |
| 交付日期 | {delivery_date or '待填写'} |

## 二、合同条款

### 1. 服务内容

[请在此处填写具体服务内容]

### 2. 价格与支付

- 合同总额：**¥{total_amount:,.2f}**
- 支付方式：[请指定支付方式]
- 支付周期：[请指定支付周期]

### 3. 交付与验收

- 交付时间：{delivery_date or '未指定'}
- 交付方式：[请指定交付方式]
- 验收标准：[请指定验收标准]

### 4. 违约责任

双方应严格按照合同约定履行义务，任何一方违约应承担相应的违约责任。

### 5. 争议解决

如发生争议，双方应友好协商解决；协商不成，可向有管辖权的人民法院提起诉讼。

---

*本草案仅供参考，请在签署前由法务部门审核。*
"""
        return content

    @staticmethod
    def generate_audit_report(contract_title: str, audit_results: Dict[str, Any]) -> str:
        """生成合同审核报告"""
        risks = audit_results.get("risks", [])
        summary = audit_results.get("summary", "审核完成")
        risk_count = len(risks)
        
        content = f"""# 📋 合同审核报告

## 审核概况

- 合同名称：{contract_title}
- 审核时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 审核结论：{summary}
- 发现问题：{risk_count} 项

## 🔍 风险清单

"""
        for i, risk in enumerate(risks, 1):
            content += f"""### {i}. {risk.get("risk_level", "未知")}风险

- **条款位置**: {risk.get("location", "未指定")}
- **问题描述**: {risk.get("description", "未描述")}
- **法律依据**: {risk.get("legal_basis", "未引用")}
- **修改建议**: {risk.get("recommendation", "无建议")}

"""
        content += """## ✅ 审查通过建议

请根据上述风险清单修改合同，重点关注：
1. 高风险条款需法务部门再审
2. 中风险条款建议修改
3. 低风险条款供参考

**审核人**: AI 助手  
**审核状态**: 待修改
"""
        return content

    @staticmethod
    def generate_invoice_match_report(po_number: str, match_result: Dict[str, Any]) -> str:
        """生成三单匹配报告"""
        status = match_result.get("status", "未知")
        score = match_result.get("match_score", 0)
        discrepancies = match_result.get("discrepancies", [])
        
        status_icon = "✅" if status == "MATCHED" else "⚠️"
        status_text = "匹配成功" if status == "MATCHED" else "存在差异"
        
        content = f"""# 📊 三单匹配报告

## 匹配概况

| 项目 | 内容 |
|------|------|
| 采购单号 | PO:{po_number} |
| 匹配时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| 匹配结果 | {status_icon} {status_text} |
| 匹配评分 | {score:.0%} |

## 📋 匹配详情

### 金额匹配
- 采购金额：¥{match_result.get("po_amount", 0):,.2f}
- 发票金额：¥{match_result.get("invoice_amount", 0):,.2f}
- 验收金额：¥{match_result.get("gr_amount", 0):,.2f}

### 数量匹配
- 采购数量：{match_result.get("po_quantity", 0)}
- 发票数量：{match_result.get("invoice_quantity", 0)}
- 验收数量：{match_result.get("gr_quantity", 0)}

## 🚨 差异项 (共{len(discrepancies)}项)
"""
        for disc in discrepancies:
            content += f"""
- **{disc.get("field", "字段")}**: 
  - 采购值：{disc.get("po_value", "N/A")}
  - 发票值：{disc.get("invoice_value", "N/A")}
  - 差异原因：{disc.get("reason", "未说明")}
"""
        content += f"""
## 📌 处理建议

{'✅ 三单完全匹配，可以进入付款流程。' if status == "MATCHED" else f'⚠️ 发现 {len(discrepancies)} 项差异，需人工核查后再处理。'}

---

*本报告仅供内部参考，不作为最终付款依据。*
"""
        return content