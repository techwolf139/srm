"""合同管理的飞书文档集成"""
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from srm_feishu_docs_bridge.sync_manager import DocumentSyncManager
from srm_feishu_docs_bridge.models import DocumentMetadata


class ContractFeishuIntegration:
    """合同飞书集成功能"""

    def __init__(self):
        self.sync_manager = DocumentSyncManager()

    def create_contract_document(
        self,
        contract_content: str,
        contract_data: Dict[str, Any],
    ) -> DocumentMetadata:
        """创建合同草稿到飞书文档"""
        title = f"采购合同 - {contract_data.get('supplier_name', '未知供应商')}"
        formatted_content = self._format_contract_markdown(contract_content, contract_data)

        return self.sync_manager.create_contract_draft(
            title=title,
            content=formatted_content,
            po_number=contract_data.get("po_number"),
            supplier_name=contract_data.get("supplier_name"),
        )

    def create_audit_report(
        self,
        contract_doc_id: str,
        audit_findings: List[Dict[str, Any]],
        risk_summary: Dict[str, Any],
    ) -> DocumentMetadata:
        """创建审核报告并关联到合同文档"""
        content = self._format_audit_markdown(audit_findings, risk_summary)

        return self.sync_manager.create_contract_audit_report(
            contract_doc_id=contract_doc_id,
            audit_content=content,
            audit_results=risk_summary,
        )

    def _format_contract_markdown(self, content: str, data: Dict[str, Any]) -> str:
        """格式化合同为 Markdown"""
        return f"""# 采购合同

## 基本信息

- **供应商**: {data.get('supplier_name', '')}
- **合同金额**: ¥{data.get('total_amount', 0):,.2f}
- **采购单号**: {data.get('po_number', '')}
- **创建时间**: {data.get('created_at', '')}

## 合同正文

{content}

---
*本合同由 SRM 智能体系统自动生成*
"""

    def _format_audit_markdown(
        self, findings: List[Dict[str, Any]], summary: Dict[str, Any]
    ) -> str:
        """格式化审核报告为 Markdown"""
        md = ["# 合同审核报告\n"]

        md.append(
            f"""## 风险汇总

| 风险等级 | 数量 |
|---------|------|
| 🔴 严重 | {summary.get('critical', 0)} |
| 🟠 高风险 | {summary.get('high', 0)} |
| 🟡 中风险 | {summary.get('medium', 0)} |
| 🟢 低风险 | {summary.get('low', 0)} |

**综合评分**: {summary.get('score', 0)}/100

"""
        )

        md.append("## 详细发现\n")
        for i, finding in enumerate(findings, 1):
            md.append(
                f"""### {i}. {finding.get('type', '问题')}

- **位置**: {finding.get('location', 'N/A')}
- **描述**: {finding.get('description', '')}
- **建议**: {finding.get('suggestion', '')}

---
"""
            )

        return "\n".join(md)