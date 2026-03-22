---
name: contract-manager
description: Use when drafting procurement contracts from templates, reviewing contract clauses against Chinese law, or checking compliance with corporate red-line terms
---

# Contract Manager

## Overview

自动生成采购合同（填充模板）和审核合同条款是否符合国内法规和企业红线要求。支持《民法典》合同编相关条款检查。

## When to Use

**触发条件：**
- 采购询价完成，需生成正式合同
- 供应商提供合同，需法务审核
- 合同审批流程前检查
- 合同变更/补充协议起草

**不适用：**
- 复杂涉外合同（建议专业律师）
- 标的额超过一定金额（国企/上市公司规定）

## 核心功能

### 1. 合同自动生成

根据采购信息填充标准模板：
```
采购信息 → 合同各条款自动填充
```

### 2. 合同条款审核

对企业提供的合同进行红队分析：
```
合同文本 → 条款提取 → 风险点识别 → 修改建议
```

## 国内法规适配

### 《民法典》合同编重点条款

| 条款 | 要点 |
|------|------|
| 第465条 | 合同约束力 |
| 第496条 | 格式条款定义 |
| 第497条 | 格式条款无效情形 |
| 第506条 | 合同无效情形 |
| 第585条 | 违约金上限（不超过实际损失30%） |
| 第590条 | 不可抗力条款 |
| 第591条 | 减损义务 |

### 企业红线条款（内控）

| 风险类型 | 红线标准 | 建议修改 |
|----------|----------|----------|
| 违约金比例 | >合同金额20% | 下调至15%以内 |
| 管辖法院 | 对方所在地 | 建议改为"原告所在地" |
| 付款账期 | 预付>50% | 建议月结或验收后付款 |
| 保密条款 | 无上限赔偿 | 建议限定金额 |
| 知识产权 | 无限制转让 | 建议限定用途 |

## 输入格式

### 采购信息输入
```json
{
  "supplier_name": "深圳市xxx科技有限公司",
  "contact_person": "张三",
  "contact_phone": "13800138000",
  "items": [
    {
      "item_name": "机械键盘",
      "quantity": 10,
      "unit_price": 299.00,
      "total_price": 2990.00
    }
  ],
  "total_amount": 2990.00,
  "payment_terms": "验收后30天付款",
  "delivery_date": "2026-04-15",
  "warranty_period": "1年"
}
```

### 合同文本输入
支持直接粘贴合同文本或上传PDF/Word

## 输出格式

### 生成的合同
完整合同文本（Markdown/DOCX），包含：
- 甲方（采购方）信息
- 乙方（供应商）信息
- 合同标的
- 价格条款
- 交付条款
- 验收标准
- 违约责任
- 争议解决
- 签章页

### 审核报告
```json
{
  "overall_risk": "MEDIUM",
  "risk_score": 55,
  "clauses": [
    {
      "clause": "违约金为合同金额的30%",
      "issue": "违约金比例过高",
      "legal_ref": "《民法典》第585条：不超过实际损失的30%",
      "suggestion": "建议调整为20%或以下",
      "severity": "HIGH"
    },
    {
      "clause": "管辖法院为乙方所在地",
      "issue": "管辖法院对甲方不利",
      "legal_ref": "《民事诉讼法》第34条",
      "suggestion": "建议改为原告所在地或合同签订地",
      "severity": "MEDIUM"
    }
  ],
  "summary": "合同存在2个高风险条款，建议修改后再签署"
}
```

## 模板字段

```
{{party_a_name}}       # 甲方（采购方）名称
{{party_a_address}}    # 甲方地址
{{party_b_name}}       # 乙方（供应商）名称
{{party_b_address}}    # 乙方地址
{{contract_no}}       # 合同编号
{{sign_date}}          # 签订日期
{{item_list}}          # 采购物品清单
{{total_amount}}       # 合同总金额
{{payment_terms}}      # 付款条件
{{delivery_date}}      # 交付日期
{{warranty_period}}    # 质保期
{{party_a_sign}}       # 甲方签章
{{party_b_sign}}       # 乙方签章
```

## 使用流程

```python
from contract_manager import ContractGenerator, ContractReviewer

# 1. 生成合同
generator = ContractGenerator()
contract = generator.generate(
    purchase_info=purchase_data,
    template="standard_procurement"
)

# 2. 审核合同（如对方提供）
reviewer = ContractReviewer()
report = reviewer.review(
    contract_text=supplier_contract,
    red_lines=corporate_red_lines
)
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 不核实对方签章 | 合同需双签或公证 |
| 忽略发票条款 | 国内合同需明确发票类型（增值税专用发票/普通发票） |
| 违约金过高 | 《民法典》第585条上限约束 |
| 口头变更合同 | 所有变更需书面补充协议 |
| 忽视知识产权 | 采购设备需明确知识产权归属 |

## 质量检查表

- [ ] 合同金额与采购询价一致
- [ ] 发票条款明确（含税率）
- [ ] 违约金≤20%
- [ ] 管辖法院为甲方有利条款
- [ ] 不可抗力条款完整
- [ ] 质保期与采购要求一致
- [ ] 有明确的验收标准
- [ ] 签署页完整（双签+日期+盖章）
