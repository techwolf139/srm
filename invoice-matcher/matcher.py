"""
三单匹配器 - 采购单、收货单、发票核对
"""
import json
from datetime import datetime
from typing import Optional


def verify_invoice_locally(invoice_data: dict) -> dict:
    """本地发票规则验证"""
    issues = []
    
    # 检查发票代码格式
    code = invoice_data.get("invoice_code", "")
    if not code.isdigit() or len(code) != 12:
        issues.append("发票代码应为12位数字")
    
    # 检查发票号码格式
    number = invoice_data.get("invoice_number", "")
    if not number.isdigit() or len(number) != 8:
        issues.append("发票号码应为8位数字")
    
    # 检查开票日期
    invoice_date = invoice_data.get("invoice_date", "")
    if invoice_date:
        try:
            date_obj = datetime.strptime(invoice_date, "%Y-%m-%d")
            if date_obj > datetime.now():
                issues.append("开票日期不能晚于当前日期")
        except ValueError:
            issues.append("开票日期格式错误")
    
    # 检查金额
    total = invoice_data.get("total_amount", 0)
    tax = invoice_data.get("tax_amount", 0)
    pre_tax = invoice_data.get("不含税金额", 0)
    if abs(total - tax - pre_tax) > 0.01:
        issues.append("价税合计不等于税额+不含税金额")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


def match_three_way(
    po: dict,
    gr: dict,
    invoice: dict,
    tolerance: float = 0.01
) -> dict:
    """三单匹配"""
    results = {
        "po_number": po.get("po_number", ""),
        "gr_number": gr.get("gr_number", ""),
        "invoice_number": invoice.get("invoice_number", ""),
        "matches": [],
        "mismatches": [],
        "warnings": [],
        "status": "PENDING"
    }
    
    # 1. 金额匹配
    po_amount = po.get("total_amount", 0)
    invoice_amount = invoice.get("total_amount", 0)
    diff = abs(po_amount - invoice_amount)
    if diff <= tolerance:
        results["matches"].append({"field": "amount", "value": invoice_amount})
    else:
        results["mismatches"].append({
            "field": "amount",
            "po": po_amount,
            "invoice": invoice_amount,
            "diff": po_amount - invoice_amount
        })
    
    # 2. 税率匹配
    po_tax_rate = po.get("tax_rate", 0)
    inv_tax_rate = invoice.get("tax_rate", 0)
    if po_tax_rate == inv_tax_rate:
        results["matches"].append({"field": "tax_rate", "value": f"{inv_tax_rate*100 if inv_tax_rate < 1 else inv_tax_rate}%"})
    else:
        results["mismatches"].append({
            "field": "tax_rate",
            "po": f"{po_tax_rate*100 if po_tax_rate < 1 else po_tax_rate}%",
            "invoice": f"{inv_tax_rate*100 if inv_tax_rate < 1 else inv_tax_rate}%"
        })
    
    # 3. 供应商匹配
    po_supplier = po.get("supplier_name", "")
    inv_seller = invoice.get("seller_name", "")
    if po_supplier and inv_seller:
        if po_supplier in inv_seller or inv_seller in po_supplier:
            results["matches"].append({"field": "supplier", "value": inv_seller})
        else:
            # 可能是公司简称不同，给个警告
            results["warnings"].append({
                "field": "supplier",
                "po": po_supplier,
                "invoice": inv_seller,
                "note": "供应商名称略有差异，请人工核实"
            })
    
    # 4. 数量匹配
    po_items = {i.get("item_name", ""): i.get("quantity", 0) for i in po.get("items", [])}
    inv_items = {i.get("name", ""): i.get("quantity", 0) for i in invoice.get("items", [])}
    qty_issues = []
    for item, po_qty in po_items.items():
        if item in inv_items:
            inv_qty = inv_items[item]
            if inv_qty > po_qty:
                qty_issues.append(f"{item}发票数量({inv_qty})>采购数量({po_qty})")
            else:
                results["matches"].append({"field": f"item:{item}", "value": f"{inv_qty}/{po_qty}"})
    if qty_issues:
        results["mismatches"].extend([{"field": "quantity", "detail": i} for i in qty_issues])
    
    # 确定状态
    if results["mismatches"]:
        if len(results["mismatches"]) <= 2 and not any("amount" in str(m) for m in results["mismatches"]):
            results["status"] = "PARTIAL_MATCH"
        else:
            results["status"] = "MISMATCH"
    else:
        results["status"] = "MATCHED"
    
    results["match_rate"] = len(results["matches"]) / (len(results["matches"]) + len(results["mismatches"]) + 0.001)
    
    return results


def generate_match_report(match_result: dict) -> str:
    """生成匹配报告"""
    status_emoji = {
        "MATCHED": "✅",
        "PARTIAL_MATCH": "⚠️",
        "MISMATCH": "❌",
        "PENDING": "⏳"
    }
    
    lines = ["# 三单匹配报告\n"]
    lines.append(f"**状态:** {status_emoji.get(match_result['status'], '')} {match_result['status']}\n")
    lines.append(f"**采购单:** {match_result['po_number']}  ")
    lines.append(f"**收货单:** {match_result['gr_number']}  ")
    lines.append(f"**发票号:** {match_result['invoice_number']}\n")
    
    if match_result["matches"]:
        lines.append("\n## ✅ 匹配项\n")
        for m in match_result["matches"]:
            lines.append(f"- {m['field']}: {m.get('value', 'OK')}")
    
    if match_result["warnings"]:
        lines.append("\n## ⚠️ 警告项（请人工核实）\n")
        for w in match_result["warnings"]:
            lines.append(f"- {w['field']}: {w.get('note', '')}")
            lines.append(f"  - 采购单: {w.get('po', '')}")
            lines.append(f"  - 发票: {w.get('invoice', '')}")
    
    if match_result["mismatches"]:
        lines.append("\n## ❌ 不匹配项\n")
        for m in match_result["mismatches"]:
            if "detail" in m:
                lines.append(f"- {m['field']}: {m['detail']}")
            else:
                lines.append(f"- {m['field']}: 采购单={m.get('po','')}, 发票={m.get('invoice','')}")
    
    lines.append(f"\n**匹配率:** {match_result.get('match_rate', 0)*100:.1f}%\n")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    po = {
        "po_number": "PO-20260315-001",
        "supplier_name": "深圳市xxx科技有限公司",
        "total_amount": 2990.00,
        "tax_rate": 0.13,
        "items": [
            {"item_name": "机械键盘", "quantity": 10}
        ]
    }
    
    gr = {
        "gr_number": "GR-20260318-001",
        "signed_date": "2026-03-18",
        "items": [
            {"item_name": "机械键盘", "quantity": 10}
        ]
    }
    
    invoice = {
        "invoice_number": "12345678",
        "invoice_code": "144031900100",
        "invoice_date": "2026-03-15",
        "seller_name": "深圳市xxx科技有限公司",
        "total_amount": 2990.00,
        "tax_amount": 345.39,
        "不含税金额": 2644.61,
        "tax_rate": 0.13,
        "items": [
            {"name": "*键盘*机械键盘", "quantity": 10, "price": 299.00}
        ]
    }
    
    result = match_three_way(po, gr, invoice)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("\n" + generate_match_report(result))
