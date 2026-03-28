"""数据模型定义"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class DocType(Enum):
    """文档类型"""
    CONTRACT_DRAFT = "contract_draft"
    CONTRACT_AUDIT = "contract_audit"
    CONTRACT_SIGNED = "contract_signed"
    INVOICE_MATCH = "invoice_match"
    REQUIREMENT = "requirement"
    PAYMENT = "payment"


class DocStatus(Enum):
    """文档状态"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class DocumentMetadata:
    """文档元数据"""
    doc_id: str
    doc_type: DocType
    title: str
    url: str
    version: int = 1
    parent_doc_id: Optional[str] = None
    related_docs: List[str] = field(default_factory=list)
    created_by: str = ""
    status: DocStatus = DocStatus.DRAFT
    extra: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "doc_type": self.doc_type.value,
            "title": self.title,
            "url": self.url,
            "version": self.version,
            "parent_doc_id": self.parent_doc_id,
            "related_docs": self.related_docs,
            "created_by": self.created_by,
            "status": self.status.value,
            "extra": self.extra,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        return cls(
            doc_id=data["doc_id"],
            doc_type=DocType(data["doc_type"]),
            title=data["title"],
            url=data["url"],
            version=data.get("version", 1),
            parent_doc_id=data.get("parent_doc_id"),
            related_docs=data.get("related_docs", []),
            created_by=data.get("created_by", ""),
            status=DocStatus(data.get("status", "draft")),
            extra=data.get("extra", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class DocumentChain:
    """文档链路（单个采购单的完整文档集合）"""
    chain_id: str
    po_number: Optional[str] = None
    supplier_name: Optional[str] = None
    total_amount: Optional[float] = None
    requirement_doc: Optional[DocumentMetadata] = None
    contract_draft_doc: Optional[DocumentMetadata] = None
    contract_audit_doc: Optional[DocumentMetadata] = None
    contract_signed_doc: Optional[DocumentMetadata] = None
    invoice_match_doc: Optional[DocumentMetadata] = None
    payment_doc: Optional[DocumentMetadata] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_all_docs(self) -> List[DocumentMetadata]:
        """获取所有关联文档"""
        docs = []
        for attr in [
            "requirement_doc",
            "contract_draft_doc",
            "contract_audit_doc",
            "contract_signed_doc",
            "invoice_match_doc",
            "payment_doc",
        ]:
            doc = getattr(self, attr)
            if doc:
                docs.append(doc)
        return docs