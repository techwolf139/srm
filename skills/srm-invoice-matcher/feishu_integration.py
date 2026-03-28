"""三单匹配的飞书文档集成"""
from typing import Optional, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from srm_feishu_docs_bridge.sync_manager import DocumentSyncManager
from srm_feishu_docs_bridge.models import DocumentMetadata


class InvoiceMatcherFeishuIntegration:
    """三单匹配飞书集成功能"""

    def __init__(self):
        self.sync_manager = DocumentSyncManager()

    def create_match_report(
        self,
        po_number: str,
        match_result: Dict[str, Any],
        contract_doc_id: Optional[str] = None,
    ) -> DocumentMetadata:
        """创建三单匹配报告到飞书文档"""
        content = self._format_match_markdown(match_result)

        return self.sync_manager.create_invoice_match_report(
            po_number=po_number,
            match_content=content,
            match_result=match_result,
            contract_doc_id=contract_doc_id,
        )

    def _format_match_markdown(self, result: Dict[str, Any]) -> str:
        """格式化匹配报告为 Markdown"""
        status = result.get("status", "UNKNOWN")
        status_emoji = {
            "MATCHED": "✅",
            "PARTIAL_MATCH": "⚠️",
            "MISMATCH": "❌",
        }.get(status, "❓")

        md = f"""# 三单匹配报告

## 匹配结果

**状态**: {status_emoji} {status}

| 项目 | 信息 |
|------|------|
| 采购单号 | {result.get('po_number', 'N/A')} |
| 发票号码 | {result.get('invoice_number', 'N/A')} |
| 匹配率 | {result.get('match_rate', 0):.1%} |

## 匹配详情

### 匹配项
"""

        for match in result.get("matches", []):
            md += f"- ✅ {match}\n"

        md += "\n### 不匹配项\n"
        for mismatch in result.get("mismatches", []):
            if isinstance(mismatch, dict):
                md += f"- ❌ **{mismatch['field']}**: 采购单={mismatch.get('po', 'N/A')}, 发票={mismatch.get('invoice', 'N/A')}\n"
            else:
                md += f"- ❌ {mismatch}\n"

        md += """
## 处理建议

"""
        if status == "MATCHED":
            md += "✅ 三单匹配通过，可以进行付款审批。"
        elif status == "PARTIAL_MATCH":
            md += "⚠️ 存在部分不匹配项，建议人工审核后处理。"
        else:
            md += "❌ 匹配失败，请与供应商核实单据信息。"

        return md