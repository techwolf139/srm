"""文档存储管理"""
import logging
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentMetadata:
    """文档元数据"""
    
    def __init__(
        self,
        doc_id: str,
        doc_type: str,
        title: str,
        url: str,
        version: int = 1,
        status: str = "draft",
        extra: Dict[str, Any] = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        related_docs: List[str] = None,
        parent_doc_id: str = None,
    ):
        self.doc_id = doc_id
        self.doc_type = doc_type
        self.title = title
        self.url = url
        self.version = version
        self.status = status
        self.extra = extra or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.related_docs = related_docs or []
        self.parent_doc_id = parent_doc_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "doc_type": self.doc_type,
            "title": self.title,
            "url": self.url,
            "version": self.version,
            "status": self.status,
            "extra": self.extra,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "related_docs": self.related_docs,
            "parent_doc_id": self.parent_doc_id,
        }
    
    def update_status(self, new_status: str):
        """更新文档状态"""
        self.status = new_status
        self.updated_at = datetime.now()


class StorageManager:
    """文档存储管理器"""
    
    def __init__(self, storage_path: str = "./data/doc_chains"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_document(self, metadata: DocumentMetadata) -> bool:
        """保存文档元数据"""
        try:
            file_path = self.storage_path / f"{metadata.doc_id}.json"
            data = metadata.to_dict()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存文档元数据失败：{e}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[DocumentMetadata]:
        """获取文档元数据"""
        try:
            file_path = self.storage_path / f"{doc_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return DocumentMetadata(**data)
        except Exception as e:
            logger.error(f"读取文档元数据失败：{e}")
            return None
    
    def get_pending_documents(self, platform: Optional[str] = None) -> List[DocumentMetadata]:
        """获取待同步文档"""
        pending = []
        
        for file_path in self.storage_path.glob("*.json"):
            doc_meta = self.get_document(file_path.stem)
            if doc_meta and doc_meta.status in ["draft", "pending_review"]:
                pending.append(doc_meta)
        
        return pending
    
    def filter_documents_by_type(
        self, 
        doc_types: List[str],
        status_filter: Optional[str] = None,
    ) -> List[DocumentMetadata]:
        """筛选文档"""
        filtered = []
        
        for file_path in self.storage_path.glob("*.json"):
            doc_meta = self.get_document(file_path.stem)
            if doc_meta:
                if doc_meta.doc_type in doc_types:
                    if status_filter is None or doc_meta.status == status_filter:
                        filtered.append(doc_meta)
        
        return filtered
    
    def update_document_status(self, doc_id: str, new_status: str) -> bool:
        """更新文档状态"""
        doc_meta = self.get_document(doc_id)
        if doc_meta:
            doc_meta.update_status(new_status)
            return self.save_document(doc_meta)
        return False