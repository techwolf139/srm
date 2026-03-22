---
name: invoice-matcher
description: Use when matching procurement orders with invoices and delivery receipts, verifying Chinese VAT invoices, or automating three-way matching reconciliation
---

# Invoice Matcher (三单匹配)

## Overview

三单匹配（采购单、收货单、发票）核对，OCR识别国内增值税发票，验证发票真伪，触发财务付款流程。

## When to Use

**触发条件：**
- 货物已签收，需要核对发票与采购单一致性
- 财务审核付款申请
- 月末对账/结账
- 审计准备

**不适用：**
- 采购单据尚未确认
- 发票与实物严重不符

## 三单匹配原理

```
采购单 (PO)     ←→  采购询价确认的价格、数量
    ↓
收货单 (GR)    ←→  物流签收单/入库单
    ↓
发票 (Invoice)  ←→  增值税发票金额、税率
```

**匹配规则：**
- 金额匹配：发票含税金额 ≈ 采购单金额 (±0.01允许误差)
- 数量匹配：发票数量 ≤ 采购数量
- 税率匹配：发票税率与采购要求一致

## 国内发票类型

| 发票类型 | 税率 | 可抵扣 | 适用场景 |
|----------|------|--------|----------|
| 增值税专用发票 | 6%/9%/13% | 是 | 一般纳税人采购 |
| 增值税普通发票 | 6%/9%/13% | 否 | 个人/小规模纳税人 |
| 电子发票 | 同上 | 同上 | 数字化管理 |

## OCR识别

### 推荐方案

| 服务商 | 识别率 | 费用 | 备注 |
|--------|--------|------|------|
| 百度OCR | ~98% | 按调用量 | 支持增值税发票 |
| 腾讯OCR | ~97% | 按调用量 | 企业用户优惠 |
| 阿里云OCR | ~96% | 按调用量 | 性价比高 |
| 手动录入 | N/A | 人工成本 | 小批量可行 |

### OCR字段提取

```python
def parse_invoice_ocr(image_bytes: bytes) -> dict:
    """OCR识别增值税发票关键字段"""
    return {
        "invoice_code": "144031900100",      # 发票代码
        "invoice_number": "12345678",          # 发票号码
        "invoice_date": "2026-03-15",          # 开票日期
        "seller_name": "xxx科技有限公司",      # 销售方名称
        "seller_tax_no": "91440300MA5xxx",     # 销售方税号
        "buyer_name": "YY公司",                # 购买方名称
        "buyer_tax_no": "91320000AAABBB",     # 购买方税号
        "total_amount": 2990.00,               # 价税合计
        "tax_amount": 345.39,                  # 税额
        "不含税金额": 2644.61,
        "items": [                              # 商品明细
            {"name": "*键盘*机械键盘", "quantity": 10, "price": 299.00}
        ]
    }
```

## 发票查验

### 国家税务总局发票查验平台

```python
def verify_invoice(invoice_code: str, invoice_number: str, invoice_date: str, total: float) -> dict:
    """
    查验发票真伪
    API: https://inv-veri.chinatax.gov.cn
    """
    # 需注册企业账号，获取API权限
    pass
```

### 简易查验规则

| 检查项 | 规则 |
|--------|------|
| 发票代码 | 12位数字 |
| 发票号码 | 8位数字 |
| 开票日期 | 不能晚于当前日期 |
| 金额 | 与采购单金额一致 |
| 销售方 | 与供应商一致 |

## 三单匹配算法

```python
def match_three_way(
    po: dict,      # 采购单
    gr: dict,      # 收货单
    invoice: dict, # 发票
    tolerance: float = 0.01
) -> dict:
    """三单匹配核心逻辑"""
    results = {
        "po_number": po.get("po_number"),
        "gr_number": gr.get("gr_number"),
        "invoice_number": invoice.get("invoice_number"),
        "matches": [],
        "mismatches": [],
        "status": "PENDING"
    }
    
    # 1. 金额匹配
    po_amount = po.get("total_amount", 0)
    invoice_amount = invoice.get("total_amount", 0)
    if abs(po_amount - invoice_amount) <= tolerance:
        results["matches"].append("amount")
    else:
        results["mismatches"].append({
            "field": "amount",
            "po": po_amount,
            "invoice": invoice_amount,
            "diff": po_amount - invoice_amount
        })
    
    # 2. 数量匹配
    po_items = {i["item_name"]: i["quantity"] for i in po.get("items", [])}
    inv_items = {i["name"]: i["quantity"] for i in invoice.get("items", [])}
    for item, qty in po_items.items():
        inv_qty = inv_items.get(item, 0)
        if inv_qty <= qty:
            results["matches"].append(f"item:{item}")
        else:
            results["mismatches"].append(f"item:{item} qty mismatch")
    
    # 3. 税率匹配
    po_tax_rate = po.get("tax_rate", 0)
    inv_tax_rate = invoice.get("tax_rate", 0)
    if po_tax_rate == inv_tax_rate:
        results["matches"].append("tax_rate")
    else:
        results["mismatches"].append({
            "field": "tax_rate",
            "po": po_tax_rate,
            "invoice": inv_tax_rate
        })
    
    # 4. 供应商匹配
    if po.get("supplier_name") == invoice.get("seller_name"):
        results["matches"].append("supplier")
    else:
        results["mismatches"].append({
            "field": "supplier",
            "po": po.get("supplier_name"),
            "invoice": invoice.get("seller_name")
        })
    
    # 确定状态
    if not results["mismatches"]:
        results["status"] = "MATCHED"
    elif len(results["mismatches"]) <= 2:
        results["status"] = "PARTIAL_MATCH"
    else:
        results["status"] = "MISMATCH"
    
    return results
```

## 匹配结果处理

| 状态 | 处理方式 |
|------|----------|
| MATCHED | 自动通过，发起付款流程 |
| PARTIAL_MATCH | 标记异常，人工审核 |
| MISMATCH | 拒绝付款，联系供应商 |

## 付款流程集成

```python
def create_payment_request(match_result: dict, po: dict) -> dict:
    """创建付款申请单"""
    return {
        "payment_request_no": f"PR-{datetime.now().strftime('%Y%m%d%H%M')}",
        "supplier_name": po.get("supplier_name"),
        "bank_account": po.get("bank_account"),
        "amount": po.get("total_amount"),
        "invoice_numbers": [match_result["invoice_number"]],
        "approval_workflow": "default",  # 飞书/钉钉审批流
        "status": "pending_approval"
    }
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 发票金额与采购单不符 | 核对是否是折扣、赠品导致 |
| 税率不匹配 | 确认采购时约定的税率 |
| 供应商名称不一致 | 可能因公司简称导致，人工核实 |
| 发票过期 | 增值税发票360天内必须认证 |
| 重复报销 | 检查发票号码是否已使用 |

## 质量检查表

- [ ] 发票真伪已查验
- [ ] 三单金额一致（在容差范围内）
- [ ] 税率与采购要求一致
- [ ] 供应商名称匹配
- [ ] 发票在有效期内（360天）
- [ ] 无重复报销记录
- [ ] 付款申请单已创建
