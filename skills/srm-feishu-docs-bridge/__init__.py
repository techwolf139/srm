"""飞书文档桥接技能

将合同生成、审核和三单匹配结果同步到飞书文档。
"""
from .config import FeishuConfig
from .client import FeishuClient, FeishuAPIError, FeishuDocument
from .models import DocumentMetadata, DocumentChain, DocType, DocStatus
from .sync_manager import DocumentSyncManager
from .template_generator import ContractTemplateGenerator

__all__ = [
    "FeishuConfig",
    "FeishuClient",
    "FeishuAPIError",
    "FeishuDocument",
    "DocumentMetadata",
    "DocumentChain",
    "DocType",
    "DocStatus",
    "DocumentSyncManager",
    "ContractTemplateGenerator",
]