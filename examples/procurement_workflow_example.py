"""
采购全生命周期飞书文档集成示例

展示如何从合同生成到三单匹配的飞书文档链路
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.srm_contract_manager import generate_contract, review_contract
from skills.srm_contract_manager.feishu_integration import ContractFeishuIntegration
from skills.srm_invoice_matcher import match_three_way
from skills.srm_invoice_matcher.feishu_integration import InvoiceMatcherFeishuIntegration


def run_procurement_workflow():
    """运行完整的采购工作流示例"""

    print("=" * 60)
    print("🚀 采购全生命周期 - 飞书文档集成示例")
    print("=" * 60)

    print("\n📄 阶段1: 生成合同草稿")

    contract_data = {
        "po_number": "PO-2025-001",
        "supplier_name": "深圳科技有限公司",
        "total_amount": 29900.00,
        "items": [{"name": "机械键盘", "quantity": 100, "unit_price": 299.00}],
        "payment_terms": "验收后30天付款",
        "delivery_date": "2025-04-15",
        "warranty_period": "1年",
    }

    contract_content = generate_contract(contract_data)
    print(f"✅ 合同内容已生成")

    contract_integration = ContractFeishuIntegration()
    contract_doc = contract_integration.create_contract_document(
        contract_content=contract_content, contract_data=contract_data
    )

    print(f"✅ 合同草稿已创建到飞书文档")
    print(f"   文档链接: {contract_doc.url}")
    print(f"   文档ID: {contract_doc.doc_id}")

    print("\n🔍 阶段2: 审核合同")

    audit_results = review_contract(contract_content)

    audit_doc = contract_integration.create_audit_report(
        contract_doc_id=contract_doc.doc_id,
        audit_findings=audit_results.get("findings", []),
        risk_summary=audit_results.get("summary", {}),
    )

    print(f"✅ 审核报告已创建")
    print(f"   报告链接: {audit_doc.url}")
    print(f"   风险等级: {audit_results.get('summary', {}).get('overall_risk', 'N/A')}")

    print("\n📊 阶段3: 三单匹配")

    po = {
        "po_number": "PO-2025-001",
        "supplier_name": "深圳科技有限公司",
        "total_amount": 29900.00,
        "tax_rate": 0.13,
        "items": [{"item_name": "机械键盘", "quantity": 100}],
    }

    gr = {"gr_number": "GR-2025-001", "items": [{"item_name": "机械键盘", "quantity": 100}]}

    invoice = {
        "invoice_number": "INV-2025-001",
        "invoice_code": "144031900100",
        "seller_name": "深圳科技有限公司",
        "total_amount": 29900.00,
        "tax_amount": 3451.33,
        "tax_rate": 0.13,
        "items": [{"name": "*计算机*机械键盘", "quantity": 100, "price": 299.00}],
    }

    match_result = match_three_way(po, gr, invoice)

    invoice_integration = InvoiceMatcherFeishuIntegration()
    match_doc = invoice_integration.create_match_report(
        po_number=po["po_number"],
        match_result=match_result,
        contract_doc_id=contract_doc.doc_id,
    )

    print(f"✅ 三单匹配报告已创建")
    print(f"   报告链接: {match_doc.url}")
    print(f"   匹配状态: {match_result['status']}")

    print("\n" + "=" * 60)
    print("📋 文档链路汇总")
    print("=" * 60)
    print(
        f"""
采购单号: {contract_data['po_number']}
供应商: {contract_data['supplier_name']}
金额: ¥{contract_data['total_amount']:,.2f}

📄 合同草稿: {contract_doc.url}
🔍 审核报告: {audit_doc.url}
📊 三单匹配: {match_doc.url}

所有文档已在飞书文档中建立关联，可实现全链路追溯。
"""
    )


if __name__ == "__main__":
    if not os.getenv("FEISHU_APP_ID"):
        print("⚠️ 警告: 未配置 FEISHU_APP_ID 环境变量")
        print("请先配置飞书API密钥后再运行此示例")
        print("\n设置方法:")
        print("  export FEISHU_APP_ID=cli_xxxxx")
        print("  export FEISHU_APP_SECRET=xxxxxxxx")
    else:
        run_procurement_workflow()