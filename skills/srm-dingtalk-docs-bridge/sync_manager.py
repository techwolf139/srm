"""钉钉文档同步管理器"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .client import DingTalkClient, DingTalkAPIError, DingTalkDocument
from .models import DocumentMetadata, DocumentChain, DocType, DocStatus
from .config import DingTalkConfig

# 配置日志记录
logger = logging.getLogger(__name__)


class DingTalkDocumentSyncManager:
    """钉钉文档同步管理器"""

    def __init__(
        self,
        config: Optional[DingTalkConfig] = None,
        storage_path: str = "./data/doc_chains",
    ):
        self.config = config or DingTalkConfig.from_env()
        self.client = DingTalkClient(
            app_key=self.config.app_key,
            app_secret=self.config.app_secret,
        )
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_contract_draft(
        self,
        title: str,
        content: str,
        po_number: Optional[str] = None,
        supplier_name: Optional[str] = None,
    ) -> DocumentMetadata:
        """创建合同草稿文档"""
        dingtalk_doc = self.client.create_document(
            title=title,
            content=content,
        )

        metadata = DocumentMetadata(
            doc_id=dingtalk_doc.doc_id,
            doc_type=DocType.CONTRACT_DRAFT,
            title=title,
            url=dingtalk_doc.url,
            version=1,
            status=DocStatus.DRAFT,
            extra={"po_number": po_number, "supplier_name": supplier_name},
        )

        self._save_metadata(metadata)
        return metadata

    def create_contract_audit_report(
        self,
        contract_doc_id: str,
        audit_content: str,
        audit_results: Dict[str, Any],
    ) -> DocumentMetadata:
        """创建合同审核报告文档"""
        contract_doc = self.client.get_document(contract_doc_id)
        title = f"审核报告 - {contract_doc.title}"

        dingtalk_doc = self.client.create_document(
            title=title,
            content=audit_content,
        )

        metadata = DocumentMetadata(
            doc_id=dingtalk_doc.doc_id,
            doc_type=DocType.CONTRACT_AUDIT,
            title=title,
            url=dingtalk_doc.url,
            version=1,
            parent_doc_id=contract_doc_id,
            status=DocStatus.PENDING_REVIEW,
            extra={"audit_results": audit_results},
        )

        self._save_metadata(metadata)
        self._add_audit_comment(contract_doc_id, metadata)
        return metadata

    def create_invoice_match_report(
        self,
        po_number: str,
        match_content: str,
        match_result: Dict[str, Any],
        contract_doc_id: Optional[str] = None,
    ) -> DocumentMetadata:
        """创建三单匹配报告文档"""
        title = f"三单匹配报告 - PO:{po_number}"

        dingtalk_doc = self.client.create_document(
            title=title,
            content=match_content,
        )

        related_docs = []
        if contract_doc_id:
            related_docs.append(contract_doc_id)

        status = (
            DocStatus.APPROVED
            if match_result.get("status") == "MATCHED"
            else DocStatus.PENDING_REVIEW
        )

        metadata = DocumentMetadata(
            doc_id=dingtalk_doc.doc_id,
            doc_type=DocType.INVOICE_MATCH,
            title=title,
            url=dingtalk_doc.url,
            version=1,
            related_docs=related_docs,
            status=status,
            extra={"po_number": po_number, "match_result": match_result},
        )

        self._save_metadata(metadata)

        if contract_doc_id:
            self._link_documents(contract_doc_id, metadata.doc_id)

        return metadata

    def _add_audit_comment(
        self, 
        contract_doc_id: str, 
        audit_metadata: DocumentMetadata
    ) -> None:
        """在合同文档下添加审核评论"""
        comment_content = f"""📋 合同审核完成

审核报告已生成：{audit_metadata.url}
审核状态：{audit_metadata.status.value}

请及时查看审核意见并处理。
"""
        try:
            self.client.add_comment(contract_doc_id, comment_content)
        except DingTalkAPIError as e:
            logger.warning(f"添加审核评论失败：{e}")
            return

    def _link_documents(self, source_doc_id: str, target_doc_id: str) -> None:
        """建立文档关联关系"""
        source_meta = self._load_metadata(source_doc_id)
        if source_meta and target_doc_id not in source_meta.related_docs:
            source_meta.related_docs.append(target_doc_id)
            source_meta.updated_at = datetime.now()
            self._save_metadata(source_meta)

    def _save_metadata(self, metadata: DocumentMetadata) -> None:
        """保存文档元数据到本地"""
        file_path = self.storage_path / f"{metadata.doc_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)

    def _load_metadata(self, doc_id: str) -> Optional[DocumentMetadata]:
        """从本地加载文档元数据"""
        file_path = self.storage_path / f"{doc_id}.json"
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return DocumentMetadata.from_dict(data)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            logger.error(f"加载文档元数据失败：{e}")
            return None

    def get_document_chain(self, po_number: str) -> Optional[DocumentChain]:
        """获取采购单的完整文档链路"""
        chain_file = self.storage_path / f"chain_{po_number}.json"
        if not chain_file.exists():
            return None

        with open(chain_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return self._deserialize_chain(data)

    def save_document_chain(self, chain: DocumentChain) -> None:
        """保存文档链路"""
        chain_file = self.storage_path / f"chain_{chain.po_number}.json"
        with open(chain_file, "w", encoding="utf-8") as f:
            json.dump(self._serialize_chain(chain), f, ensure_ascii=False, indent=2)

    def update_document_status(self, doc_id: str, status: DocStatus) -> None:
        """更新文档状态"""
        metadata = self._load_metadata(doc_id)
        if metadata:
            metadata.status = status
            metadata.updated_at = datetime.now()
            self._save_metadata(metadata)

    def _serialize_chain(self, chain: DocumentChain) -> Dict[str, Any]:
        """序列化文档链路"""
        return {
            "chain_id": chain.chain_id,
            "po_number": chain.po_number,
            "supplier_name": chain.supplier_name,
            "total_amount": chain.total_amount,
            "requirement_doc": chain.requirement_doc.to_dict() if chain.requirement_doc else None,
            "contract_draft_doc": chain.contract_draft_doc.to_dict() if chain.contract_draft_doc else None,
            "contract_audit_doc": chain.contract_audit_doc.to_dict() if chain.contract_audit_doc else None,
            "contract_signed_doc": chain.contract_signed_doc.to_dict() if chain.contract_signed_doc else None,
            "invoice_match_doc": chain.invoice_match_doc.to_dict() if chain.invoice_match_doc else None,
            "payment_doc": chain.payment_doc.to_dict() if chain.payment_doc else None,
            "created_at": chain.created_at.isoformat(),
            "updated_at": chain.updated_at.isoformat(),
        }

    def _deserialize_chain(self, data: Dict[str, Any]) -> DocumentChain:
        """反序列化文档链路"""
        return DocumentChain(
            chain_id=data["chain_id"],
            po_number=data.get("po_number"),
            supplier_name=data.get("supplier_name"),
            total_amount=data.get("total_amount"),
            requirement_doc=DocumentMetadata.from_dict(data["requirement_doc"]) if data.get("requirement_doc") else None,
            contract_draft_doc=DocumentMetadata.from_dict(data["contract_draft_doc"]) if data.get("contract_draft_doc") else None,
            contract_audit_doc=DocumentMetadata.from_dict(data["contract_audit_doc"]) if data.get("contract_audit_doc") else None,
            contract_signed_doc=DocumentMetadata.from_dict(data["contract_signed_doc"]) if data.get("contract_signed_doc") else None,
            invoice_match_doc=DocumentMetadata.from_dict(data["invoice_match_doc"]) if data.get("invoice_match_doc") else None,
            payment_doc=DocumentMetadata.from_dict(data["payment_doc"]) if data.get("payment_doc") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )