# 合同与三单匹配飞书文档集成实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个将合同生成、审核和三单匹配结果自动同步到飞书文档的集成系统，实现全链路的可追溯性和文档化管理。

**Architecture:** 通过创建一个新的 `srm-feishu-docs-bridge` 技能作为飞书文档的连接器，将现有的合同生成、审核和三单匹配技能串联起来。合同文档、审核报告和三单匹配结果都会以飞书文档的形式存储，并通过文档ID建立关联关系，形成完整的采购单据链路。

**Tech Stack:** Python 3.10+, FastAPI, 飞书开放 API (Docs API + Bot API), python-docx, markdown, pytest

---

## 背景与现状分析

### 现有技能状态

| 技能 | 状态 | 说明 |
|------|------|------|
| `srm-contract-manager` | ✅ 存在 | 包含合同生成和审核功能，使用 docx_helpers.py 处理 Word 文档 |
| `srm-contract-audit` | ✅ 存在 | 专业的合同审计，输出结构化的审核报告 |
| `srm-invoice-matcher` | ✅ 存在 | 三单匹配逻辑，输出 Markdown 格式的匹配报告 |
| `srm-im-bot-gateway` | ✅ 存在 | IM 网关，包含飞书 Webhook 集成文档 |
| `srm-contract-generator` | ❌ 缺失 | 需要新建，负责从模板生成合同草稿 |
| `srm-feishu-docs-bridge` | ❌ 缺失 | 需要新建，飞书文档集成的核心连接器 |

### 集成目标

1. **合同文档化**：合同草稿自动生成飞书文档
2. **审核可追溯**：审核结果以评论/子文档形式关联到合同文档
3. **三单关联**：发票匹配结果与对应合同建立文档级关联
4. **版本控制**：合同修改历史自动记录
5. **审批流程**：飞书审批流与合同状态同步

---

## 核心数据模型

### 飞书文档元数据 (FeishuDocMetadata)

```python
@dataclass
class FeishuDocMetadata:
    """飞书文档元数据结构"""
    doc_id: str                    # 飞书文档唯一ID
    doc_title: str                 # 文档标题
    doc_type: str                  # 文档类型: contract|audit|invoice_match
    doc_url: str                   # 文档访问链接
    created_at: datetime           # 创建时间
    updated_at: datetime           # 更新时间
    version: int                   # 版本号
    parent_doc_id: Optional[str]   # 父文档ID（用于关联）
    related_docs: List[str]        # 关联文档ID列表
    created_by: str                # 创建者
    status: str                    # 文档状态
    extra_metadata: Dict           # 扩展元数据
```

### 采购单据链路 (ProcurementDocumentChain)

```python
@dataclass
class ProcurementDocumentChain:
    """采购单据完整链路"""
    chain_id: str                  # 链路唯一ID
    po_number: str                 # 采购单号
    
    # 各阶段文档
    requirement_doc: Optional[FeishuDocMetadata]    # 需求文档
    contract_draft_doc: Optional[FeishuDocMetadata] # 合同草稿
    contract_audit_doc: Optional[FeishuDocMetadata] # 审核报告
    signed_contract_doc: Optional[FeishuDocMetadata]# 签署后合同
    invoice_match_doc: Optional[FeishuDocMetadata]  # 三单匹配报告
    payment_doc: Optional[FeishuDocMetadata]        # 付款审批单
    
    # 关联信息
    supplier_name: str
    total_amount: float
    status: str                    # 整体链路状态
    created_at: datetime
    completed_at: Optional[datetime]
```

---

## 实施任务列表

### Task 1: 创建项目基础设施

**目标:** 搭建飞书文档集成的基础代码结构和配置

**Files:**
- Create: `skills/srm-feishu-docs-bridge/__init__.py`
- Create: `skills/srm-feishu-docs-bridge/SKILL.md`
- Create: `skills/srm-feishu-docs-bridge/config.py`
- Create: `requirements-feishu.txt`

**Step 1: 创建技能目录结构**

```bash
mkdir -p skills/srm-feishu-docs-bridge
cd skills/srm-feishu-docs-bridge
touch __init__.py config.py client.py models.py sync_manager.py
```

**Step 2: 编写依赖配置**

Create: `requirements-feishu.txt`
```
# 飞书文档集成依赖
requests>=2.31.0
python-dateutil>=2.8.2
python-docx>=0.8.11
markdown>=3.5.0
```

**Step 3: 编写配置文件**

Create: `skills/srm-feishu-docs-bridge/config.py`
```python
"""飞书文档集成配置"""
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class FeishuConfig:
    """飞书API配置"""
    app_id: str
    app_secret: str
    base_url: str = "https://open.feishu.cn/open-apis"
    
    # 文档相关配置
    default_folder_token: Optional[str] = None  # 默认文件夹
    doc_template_id: Optional[str] = None       # 合同模板文档ID
    
    @classmethod
    def from_env(cls) -> "FeishuConfig":
        """从环境变量加载配置"""
        return cls(
            app_id=os.getenv("FEISHU_APP_ID", ""),
            app_secret=os.getenv("FEISHU_APP_SECRET", ""),
            base_url=os.getenv("FEISHU_BASE_URL", "https://open.feishu.cn/open-apis"),
            default_folder_token=os.getenv("FEISHU_DEFAULT_FOLDER_TOKEN"),
            doc_template_id=os.getenv("FEISHU_DOC_TEMPLATE_ID")
        )
```

**Step 4: 编写 SKILL.md 文档**

Create: `skills/srm-feishu-docs-bridge/SKILL.md`
```markdown
---
name: feishu-docs-bridge
description: Use when creating, updating, or managing Feishu (Lark) documents for procurement contracts, audit reports, or invoice matching results. Handles document creation, version control, and cross-document linking.
---

# Feishu Docs Bridge

## Overview

将合同、审核报告和三单匹配结果同步到飞书文档，建立可追溯的文档链路。

## Capabilities

- 创建飞书文档（从Markdown/DOCX模板）
- 更新文档内容
- 添加文档评论（用于审核意见）
- 建立文档关联
- 版本历史管理

## Input/Output

**Input:**
- doc_type: contract|audit|invoice_match
- content: Markdown或DOCX内容
- metadata: 文档元数据

**Output:**
- doc_id: 飞书文档ID
- doc_url: 访问链接
- version: 版本号
```

**Step 5: 提交**

```bash
git add skills/srm-feishu-docs-bridge/
git add requirements-feishu.txt
git commit -m "feat: create feishu-docs-bridge skill structure and config"
```

---

### Task 2: 实现飞书API客户端

**目标:** 实现与飞书开放平台API的通信客户端

**Files:**
- Create: `skills/srm-feishu-docs-bridge/client.py`
- Test: `tests/test_feishu_client.py`

**Step 1: 编写测试 - Token获取**

Create: `tests/test_feishu_client.py`
```python
import pytest
from unittest.mock import Mock, patch
from skills.srm_feishu_docs_bridge.client import FeishuClient

def test_get_tenant_access_token():
    """测试获取租户访问令牌"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "code": 0,
            "tenant_access_token": "test-token-123",
            "expire": 7200
        }
        mock_post.return_value.status_code = 200
        
        client = FeishuClient(app_id="test_id", app_secret="test_secret")
        token = client._get_tenant_access_token()
        
        assert token == "test-token-123"
        assert client._token_expire > 0
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_feishu_client.py::test_get_tenant_access_token -v
```
Expected: FAIL - "No module named 'skills.srm_feishu_docs_bridge'"

**Step 3: 实现 FeishuClient 类**

Create: `skills/srm-feishu-docs-bridge/client.py`
```python
"""飞书API客户端"""
import requests
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class FeishuDocument:
    """飞书文档对象"""
    doc_id: str
    title: str
    url: str
    version: int
    created_time: int
    modified_time: int

class FeishuClient:
    """飞书开放平台API客户端"""
    
    def __init__(self, app_id: str, app_secret: str, base_url: str = "https://open.feishu.cn/open-apis"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url
        self._tenant_access_token: Optional[str] = None
        self._token_expire: int = 0
    
    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        # 检查token是否过期
        if self._tenant_access_token and time.time() < self._token_expire:
            return self._tenant_access_token
        
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        
        data = response.json()
        if data.get("code") != 0:
            raise FeishuAPIError(f"获取token失败: {data}")
        
        self._tenant_access_token = data["tenant_access_token"]
        self._token_expire = time.time() + data.get("expire", 7200) - 300  # 提前5分钟刷新
        return self._tenant_access_token
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._get_tenant_access_token()}"
        
        response = requests.request(method, url, headers=headers, **kwargs)
        data = response.json()
        
        if data.get("code") != 0:
            raise FeishuAPIError(f"API调用失败: {data}")
        
        return data
    
    def create_document(self, title: str, content: str, folder_token: Optional[str] = None) -> FeishuDocument:
        """创建飞书文档"""
        endpoint = "/docx/v1/documents"
        payload = {"title": title}
        if folder_token:
            payload["folder_token"] = folder_token
        
        response = self._request("POST", endpoint, json=payload)
        doc_data = response["data"]
        
        # 创建后添加内容
        doc_id = doc_data["document"]["document_id"]
        self._add_document_content(doc_id, content)
        
        return FeishuDocument(
            doc_id=doc_id,
            title=title,
            url=f"https://xxx.feishu.cn/docx/{doc_id}",
            version=1,
            created_time=doc_data["document"]["create_time"],
            modified_time=doc_data["document"]["modify_time"]
        )
    
    def _add_document_content(self, doc_id: str, content: str) -> None:
        """向文档添加内容（简化为纯文本）"""
        # 实际实现需要调用 blocks API 将 Markdown 转换为飞书文档块
        endpoint = f"/docx/v1/documents/{doc_id}/blocks"
        # 这里简化处理，实际应该将 Markdown 解析为 blocks
        pass
    
    def update_document(self, doc_id: str, content: str) -> FeishuDocument:
        """更新文档内容"""
        # 实现文档更新逻辑
        pass
    
    def add_comment(self, doc_id: str, content: str, position: Optional[Dict] = None) -> str:
        """添加文档评论"""
        endpoint = f"/drive/v1/files/{doc_id}/comments"
        payload = {"content": content}
        if position:
            payload["position"] = position
        
        response = self._request("POST", endpoint, json=payload)
        return response["data"]["comment_id"]
    
    def get_document(self, doc_id: str) -> FeishuDocument:
        """获取文档信息"""
        endpoint = f"/docx/v1/documents/{doc_id}"
        response = self._request("GET", endpoint)
        doc = response["data"]["document"]
        
        return FeishuDocument(
            doc_id=doc["document_id"],
            title=doc["title"],
            url=f"https://xxx.feishu.cn/docx/{doc_id}",
            version=doc.get("revision", 1),
            created_time=doc["create_time"],
            modified_time=doc["modify_time"]
        )

class FeishuAPIError(Exception):
    """飞书API错误"""
    pass
```

**Step 4: 运行测试**

```bash
pytest tests/test_feishu_client.py::test_get_tenant_access_token -v
```
Expected: PASS

**Step 5: 提交**

```bash
git add skills/srm-feishu-docs-bridge/client.py
git add tests/test_feishu_client.py
git commit -m "feat: implement Feishu API client with token management"
```

---

### Task 3: 实现文档同步管理器

**目标:** 实现文档创建、更新、关联的核心管理逻辑

**Files:**
- Create: `skills/srm-feishu-docs-bridge/sync_manager.py`
- Create: `skills/srm-feishu-docs-bridge/models.py`

**Step 1: 编写数据模型**

Create: `skills/srm-feishu-docs-bridge/models.py`
```python
"""数据模型定义"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class DocType(Enum):
    """文档类型"""
    CONTRACT_DRAFT = "contract_draft"      # 合同草稿
    CONTRACT_AUDIT = "contract_audit"      # 审核报告
    CONTRACT_SIGNED = "contract_signed"    # 签署后合同
    INVOICE_MATCH = "invoice_match"        # 三单匹配
    REQUIREMENT = "requirement"            # 采购需求
    PAYMENT = "payment"                    # 付款审批

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
            "updated_at": self.updated_at.isoformat()
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
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

@dataclass
class DocumentChain:
    """文档链路（单个采购单的完整文档集合）"""
    chain_id: str
    po_number: Optional[str] = None
    supplier_name: Optional[str] = None
    total_amount: Optional[float] = None
    
    # 各阶段文档
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
        for attr in ["requirement_doc", "contract_draft_doc", "contract_audit_doc",
                     "contract_signed_doc", "invoice_match_doc", "payment_doc"]:
            doc = getattr(self, attr)
            if doc:
                docs.append(doc)
        return docs
```

**Step 2: 实现同步管理器**

Create: `skills/srm-feishu-docs-bridge/sync_manager.py`
```python
"""文档同步管理器"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from .client import FeishuClient
from .models import DocumentMetadata, DocumentChain, DocType, DocStatus
from .config import FeishuConfig

class DocumentSyncManager:
    """文档同步管理器 - 管理本地元数据与飞书文档的同步"""
    
    def __init__(self, config: Optional[FeishuConfig] = None, storage_path: str = "./data/doc_chains"):
        self.config = config or FeishuConfig.from_env()
        self.client = FeishuClient(
            app_id=self.config.app_id,
            app_secret=self.config.app_secret,
            base_url=self.config.base_url
        )
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def create_contract_draft(
        self,
        title: str,
        content: str,
        po_number: Optional[str] = None,
        supplier_name: Optional[str] = None,
        folder_token: Optional[str] = None
    ) -> DocumentMetadata:
        """创建合同草稿文档"""
        # 创建飞书文档
        feishu_doc = self.client.create_document(
            title=title,
            content=content,
            folder_token=folder_token or self.config.default_folder_token
        )
        
        # 构建元数据
        metadata = DocumentMetadata(
            doc_id=feishu_doc.doc_id,
            doc_type=DocType.CONTRACT_DRAFT,
            title=title,
            url=feishu_doc.url,
            version=1,
            status=DocStatus.DRAFT,
            extra={
                "po_number": po_number,
                "supplier_name": supplier_name
            }
        )
        
        # 保存到本地存储
        self._save_metadata(metadata)
        
        return metadata
    
    def create_contract_audit_report(
        self,
        contract_doc_id: str,
        audit_content: str,
        audit_results: Dict[str, Any]
    ) -> DocumentMetadata:
        """创建合同审核报告文档"""
        # 获取合同文档信息
        contract_doc = self.client.get_document(contract_doc_id)
        
        title = f"审核报告 - {contract_doc.title}"
        
        # 创建审核报告文档
        feishu_doc = self.client.create_document(
            title=title,
            content=audit_content,
            folder_token=self.config.default_folder_token
        )
        
        metadata = DocumentMetadata(
            doc_id=feishu_doc.doc_id,
            doc_type=DocType.CONTRACT_AUDIT,
            title=title,
            url=feishu_doc.url,
            version=1,
            parent_doc_id=contract_doc_id,  # 关联到合同文档
            status=DocStatus.PENDING_REVIEW,
            extra={"audit_results": audit_results}
        )
        
        self._save_metadata(metadata)
        
        # 在合同文档下添加评论通知
        self._add_audit_comment(contract_doc_id, metadata)
        
        return metadata
    
    def create_invoice_match_report(
        self,
        po_number: str,
        match_content: str,
        match_result: Dict[str, Any],
        contract_doc_id: Optional[str] = None
    ) -> DocumentMetadata:
        """创建三单匹配报告文档"""
        title = f"三单匹配报告 - PO:{po_number}"
        
        feishu_doc = self.client.create_document(
            title=title,
            content=match_content,
            folder_token=self.config.default_folder_token
        )
        
        related_docs = []
        if contract_doc_id:
            related_docs.append(contract_doc_id)
        
        metadata = DocumentMetadata(
            doc_id=feishu_doc.doc_id,
            doc_type=DocType.INVOICE_MATCH,
            title=title,
            url=feishu_doc.url,
            version=1,
            related_docs=related_docs,
            status=DocStatus.APPROVED if match_result.get("status") == "MATCHED" else DocStatus.PENDING_REVIEW,
            extra={
                "po_number": po_number,
                "match_result": match_result
            }
        )
        
        self._save_metadata(metadata)
        
        # 如果有关联合同，更新合同的关联文档列表
        if contract_doc_id:
            self._link_documents(contract_doc_id, metadata.doc_id)
        
        return metadata
    
    def _add_audit_comment(self, contract_doc_id: str, audit_metadata: DocumentMetadata) -> None:
        """在合同文档下添加审核评论"""
        comment_content = f"""📋 合同审核完成

审核报告已生成：{audit_metadata.url}
审核状态：{audit_metadata.status.value}

请及时查看审核意见并处理。
"""
        self.client.add_comment(contract_doc_id, comment_content)
    
    def _link_documents(self, source_doc_id: str, target_doc_id: str) -> None:
        """建立文档关联关系"""
        # 更新源文档的元数据
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
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return DocumentMetadata.from_dict(data)
    
    def get_document_chain(self, po_number: str) -> Optional[DocumentChain]:
        """获取采购单的完整文档链路"""
        chain_file = self.storage_path / f"chain_{po_number}.json"
        if not chain_file.exists():
            return None
        
        with open(chain_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 反序列化文档链路
            return self._deserialize_chain(data)
    
    def save_document_chain(self, chain: DocumentChain) -> None:
        """保存文档链路"""
        chain_file = self.storage_path / f"chain_{chain.po_number}.json"
        with open(chain_file, "w", encoding="utf-8") as f:
            json.dump(self._serialize_chain(chain), f, ensure_ascii=False, indent=2)
    
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
            "updated_at": chain.updated_at.isoformat()
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
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def update_document_status(self, doc_id: str, status: DocStatus) -> None:
        """更新文档状态"""
        metadata = self._load_metadata(doc_id)
        if metadata:
            metadata.status = status
            metadata.updated_at = datetime.now()
            self._save_metadata(metadata)
```

**Step 3: 提交**

```bash
git add skills/srm-feishu-docs-bridge/models.py
git add skills/srm-feishu-docs-bridge/sync_manager.py
git commit -m "feat: implement document sync manager with chain tracking"
```

---

### Task 4: 集成到现有技能

**目标:** 将飞书文档集成到合同管理和三单匹配技能中

**Files:**
- Modify: `skills/srm-contract-manager/__init__.py`
- Create: `skills/srm-contract-manager/feishu_integration.py`
- Modify: `skills/srm-invoice-matcher/__init__.py`
- Create: `skills/srm-invoice-matcher/feishu_integration.py`

**Step 1: 创建合同管理飞书集成模块**

Create: `skills/srm-contract-manager/feishu_integration.py`
```python
"""合同管理的飞书文档集成"""
from typing import Optional, Dict, Any
import sys
import os

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from srm_feishu_docs_bridge.sync_manager import DocumentSyncManager
from srm_feishu_docs_bridge.models import DocumentMetadata

class ContractFeishuIntegration:
    """合同飞书集成功能"""
    
    def __init__(self):
        self.sync_manager = DocumentSyncManager()
    
    def create_contract_document(
        self,
        contract_content: str,
        contract_data: Dict[str, Any]
    ) -> DocumentMetadata:
        """创建合同草稿到飞书文档"""
        title = f"采购合同 - {contract_data.get('supplier_name', '未知供应商')}"
        
        # 格式化合同内容为 Markdown
        formatted_content = self._format_contract_markdown(contract_content, contract_data)
        
        return self.sync_manager.create_contract_draft(
            title=title,
            content=formatted_content,
            po_number=contract_data.get("po_number"),
            supplier_name=contract_data.get("supplier_name")
        )
    
    def create_audit_report(
        self,
        contract_doc_id: str,
        audit_findings: list,
        risk_summary: Dict[str, Any]
    ) -> DocumentMetadata:
        """创建审核报告并关联到合同文档"""
        # 生成审核报告内容
        content = self._format_audit_markdown(audit_findings, risk_summary)
        
        return self.sync_manager.create_contract_audit_report(
            contract_doc_id=contract_doc_id,
            audit_content=content,
            audit_results=risk_summary
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
    
    def _format_audit_markdown(self, findings: list, summary: Dict[str, Any]) -> str:
        """格式化审核报告为 Markdown"""
        md = ["# 合同审核报告\n"]
        
        # 风险汇总
        md.append(f"""## 风险汇总

| 风险等级 | 数量 |
|---------|------|
| 🔴 严重 | {summary.get('critical', 0)} |
| 🟠 高风险 | {summary.get('high', 0)} |
| 🟡 中风险 | {summary.get('medium', 0)} |
| 🟢 低风险 | {summary.get('low', 0)} |

**综合评分**: {summary.get('score', 0)}/100

""")
        
        # 详细发现
        md.append("## 详细发现\n")
        for i, finding in enumerate(findings, 1):
            md.append(f"""### {i}. {finding.get('type', '问题')}

- **位置**: {finding.get('location', 'N/A')}
- **描述**: {finding.get('description', '')}
- **建议**: {finding.get('suggestion', '')}

---
""")
        
        return "\n".join(md)
```

**Step 2: 更新合同管理包初始化**

Modify: `skills/srm-contract-manager/__init__.py`
```python
"""合同管理技能"""
from .manager import ContractGenerator, ContractReviewer

# 可选的飞书集成（如果环境配置了飞书）
try:
    from .feishu_integration import ContractFeishuIntegration
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False

__all__ = ["ContractGenerator", "ContractReviewer"]
if FEISHU_AVAILABLE:
    __all__.append("ContractFeishuIntegration")
```

**Step 3: 创建三单匹配飞书集成模块**

Create: `skills/srm-invoice-matcher/feishu_integration.py`
```python
"""三单匹配的飞书文档集成"""
from typing import Optional, Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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
        contract_doc_id: Optional[str] = None
    ) -> DocumentMetadata:
        """创建三单匹配报告到飞书文档"""
        # 生成报告内容
        content = self._format_match_markdown(match_result)
        
        return self.sync_manager.create_invoice_match_report(
            po_number=po_number,
            match_content=content,
            match_result=match_result,
            contract_doc_id=contract_doc_id
        )
    
    def _format_match_markdown(self, result: Dict[str, Any]) -> str:
        """格式化匹配报告为 Markdown"""
        status = result.get("status", "UNKNOWN")
        status_emoji = {
            "MATCHED": "✅",
            "PARTIAL_MATCH": "⚠️",
            "MISMATCH": "❌"
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
```

**Step 4: 更新三单匹配包初始化**

Modify: `skills/srm-invoice-matcher/__init__.py`
```python
"""三单匹配技能"""
from .matcher import (
    match_three_way,
    verify_invoice_locally,
    generate_match_report
)

# 可选的飞书集成
try:
    from .feishu_integration import InvoiceMatcherFeishuIntegration
    FEISHU_AVAILABLE = True
except ImportError:
    FEISHU_AVAILABLE = False

__all__ = ["match_three_way", "verify_invoice_locally", "generate_match_report"]
if FEISHU_AVAILABLE:
    __all__.append("InvoiceMatcherFeishuIntegration")
```

**Step 5: 提交**

```bash
git add skills/srm-contract-manager/feishu_integration.py
git add skills/srm-contract-manager/__init__.py
git add skills/srm-invoice-matcher/feishu_integration.py
git add skills/srm-invoice-matcher/__init__.py
git commit -m "feat: integrate feishu docs bridge with contract and invoice matcher skills"
```

---

### Task 5: 创建完整工作流示例

**目标:** 创建一个完整的工作流示例，展示从合同生成到三单匹配的飞书文档链路

**Files:**
- Create: `examples/procurement_workflow_example.py`
- Create: `examples/README.md`

**Step 1: 编写工作流示例**

Create: `examples/procurement_workflow_example.py`
```python
"""
采购全生命周期飞书文档集成示例

展示如何从合同生成到三单匹配，自动创建飞书文档链路
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from skills.srm_contract_manager import ContractGenerator, ContractReviewer
from skills.srm_contract_manager.feishu_integration import ContractFeishuIntegration
from skills.srm_invoice_matcher import match_three_way
from skills.srm_invoice_matcher.feishu_integration import InvoiceMatcherFeishuIntegration

def run_procurement_workflow():
    """运行完整的采购工作流示例"""
    
    print("=" * 60)
    print("🚀 采购全生命周期 - 飞书文档集成示例")
    print("=" * 60)
    
    # ========== 阶段1: 生成合同草稿 ==========
    print("\n📄 阶段1: 生成合同草稿")
    
    contract_data = {
        "po_number": "PO-2025-001",
        "supplier_name": "深圳科技有限公司",
        "total_amount": 29900.00,
        "items": [
            {"name": "机械键盘", "quantity": 100, "unit_price": 299.00}
        ],
        "payment_terms": "验收后30天付款",
        "delivery_date": "2025-04-15",
        "warranty_period": "1年"
    }
    
    # 生成合同内容
    generator = ContractGenerator()
    contract_content = generator.generate(contract_data)
    
    print(f"✅ 合同内容已生成")
    
    # 创建飞书文档
    contract_integration = ContractFeishuIntegration()
    contract_doc = contract_integration.create_contract_document(
        contract_content=contract_content,
        contract_data=contract_data
    )
    
    print(f"✅ 合同草稿已创建到飞书文档")
    print(f"   文档链接: {contract_doc.url}")
    print(f"   文档ID: {contract_doc.doc_id}")
    
    # ========== 阶段2: 审核合同 ==========
    print("\n🔍 阶段2: 审核合同")
    
    reviewer = ContractReviewer()
    audit_results = reviewer.review(contract_content)
    
    # 创建审核报告文档
    audit_doc = contract_integration.create_audit_report(
        contract_doc_id=contract_doc.doc_id,
        audit_findings=audit_results["findings"],
        risk_summary=audit_results["summary"]
    )
    
    print(f"✅ 审核报告已创建")
    print(f"   报告链接: {audit_doc.url}")
    print(f"   风险等级: {audit_results['summary']['overall_risk']}")
    
    # ========== 阶段3: 三单匹配 ==========
    print("\n📊 阶段3: 三单匹配")
    
    # 模拟采购单、收货单、发票数据
    po = {
        "po_number": "PO-2025-001",
        "supplier_name": "深圳科技有限公司",
        "total_amount": 29900.00,
        "tax_rate": 0.13,
        "items": [{"item_name": "机械键盘", "quantity": 100}]
    }
    
    gr = {
        "gr_number": "GR-2025-001",
        "items": [{"item_name": "机械键盘", "quantity": 100}]
    }
    
    invoice = {
        "invoice_number": "INV-2025-001",
        "invoice_code": "144031900100",
        "seller_name": "深圳科技有限公司",
        "total_amount": 29900.00,
        "tax_amount": 3451.33,
        "tax_rate": 0.13,
        "items": [{"name": "*计算机*机械键盘", "quantity": 100, "price": 299.00}]
    }
    
    # 执行三单匹配
    match_result = match_three_way(po, gr, invoice)
    
    # 创建三单匹配报告
    invoice_integration = InvoiceMatcherFeishuIntegration()
    match_doc = invoice_integration.create_match_report(
        po_number=po["po_number"],
        match_result=match_result,
        contract_doc_id=contract_doc.doc_id  # 关联到合同文档
    )
    
    print(f"✅ 三单匹配报告已创建")
    print(f"   报告链接: {match_doc.url}")
    print(f"   匹配状态: {match_result['status']}")
    
    # ========== 阶段4: 汇总 ==========
    print("\n" + "=" * 60)
    print("📋 文档链路汇总")
    print("=" * 60)
    print(f"""
采购单号: {contract_data['po_number']}
供应商: {contract_data['supplier_name']}
金额: ¥{contract_data['total_amount']:,.2f}

📄 合同草稿: {contract_doc.url}
🔍 审核报告: {audit_doc.url}
📊 三单匹配: {match_doc.url}

所有文档已在飞书文档中建立关联，可实现全链路追溯。
""")

if __name__ == "__main__":
    # 注意: 运行此示例需要配置飞书API密钥
    # export FEISHU_APP_ID=your_app_id
    # export FEISHU_APP_SECRET=your_app_secret
    
    if not os.getenv("FEISHU_APP_ID"):
        print("⚠️ 警告: 未配置 FEISHU_APP_ID 环境变量")
        print("请先配置飞书API密钥后再运行此示例")
        print("\n设置方法:")
        print("  export FEISHU_APP_ID=cli_xxxxx")
        print("  export FEISHU_APP_SECRET=xxxxxxxx")
    else:
        run_procurement_workflow()
```

**Step 2: 编写示例说明文档**

Create: `examples/README.md`
```markdown
# SRM 飞书文档集成示例

本目录包含飞书文档集成的使用示例。

## 前提条件

1. 拥有飞书开放平台应用
2. 配置以下环境变量:

```bash
export FEISHU_APP_ID=cli_xxxxx
export FEISHU_APP_SECRET=xxxxxxxxxxxx
export FEISHU_DEFAULT_FOLDER_TOKEN=xxxxxxxx  # 可选，默认存储文件夹
```

3. 确保应用具有以下权限:
   - `docx:document:read` - 读取文档
   - `docx:document:write` - 创建和修改文档
   - `drive:file:read` - 读取文件信息
   - `drive:file:write` - 创建文件

## 运行示例

```bash
# 进入示例目录
cd examples

# 运行完整工作流示例
python procurement_workflow_example.py
```

## 示例说明

### procurement_workflow_example.py

展示完整的采购工作流:
1. 生成合同草稿并创建飞书文档
2. 审核合同并生成审核报告
3. 执行三单匹配并创建匹配报告
4. 自动建立文档关联

## 集成效果

运行示例后，你将在飞书文档中看到:

- **合同草稿文档** - 包含完整合同内容
- **审核报告文档** - 包含风险提示和修改建议（关联到合同）
- **三单匹配报告** - 包含匹配结果和处理建议（关联到合同）

所有文档通过 `parent_doc_id` 和 `related_docs` 建立关联，形成完整的追溯链路。
```

**Step 3: 提交**

```bash
git add examples/
git commit -m "docs: add procurement workflow example with feishu integration"
```

---

### Task 6: 添加环境变量示例和文档

**目标:** 完善配置文档和环境变量示例

**Files:**
- Create: `.env.example`
- Create: `docs/FEISHU_INTEGRATION.md`

**Step 1: 创建环境变量示例文件**

Create: `.env.example`
```bash
# 飞书开放平台配置
# 获取方式: https://open.feishu.cn/app

# 应用凭证（必填）
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx

# API 基础地址（可选，默认使用国内版）
FEISHU_BASE_URL=https://open.feishu.cn/open-apis

# 默认存储文件夹 Token（可选）
# 在飞书云盘中创建文件夹后，从URL中获取
FEISHU_DEFAULT_FOLDER_TOKEN=

# 合同模板文档ID（可选）
# 用于基于模板创建合同文档
FEISHU_DOC_TEMPLATE_ID=

# 其他配置
FEISHU_WEBHOOK_SECRET=  # Webhook 验证密钥
```

**Step 2: 创建飞书集成说明文档**

Create: `docs/FEISHU_INTEGRATION.md`
```markdown
# 飞书文档集成指南

本指南介绍如何将 SRM 智能体系统与飞书文档集成，实现合同和三单匹配结果的可追溯管理。

## 架构概览

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  合同生成技能    │────▶│ 飞书文档桥接器   │────▶│  飞书文档        │
│                 │     │ (feishu-bridge)  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
┌─────────────────┐     ┌──────────────────┐
│ 三单匹配技能    │────▶│  文档链路管理    │
│                 │     │ (DocumentChain)  │
└─────────────────┘     └──────────────────┘
```

## 快速开始

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 点击"创建企业自建应用"
3. 填写应用名称和描述
4. 进入应用详情页，获取 **App ID** 和 **App Secret**

### 2. 配置应用权限

在"权限管理"中，添加以下权限:

- `docx:document` - 文档操作权限组
- `drive:drive` - 云盘操作权限组
- `im:chat` - 消息发送权限（可选，用于通知）

### 3. 发布应用版本

1. 进入"版本管理与发布"
2. 点击"创建版本"
3. 填写版本信息
4. 提交审核（企业内部应用可立即发布）

### 4. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的应用凭证
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxx
```

### 5. 验证集成

```python
from skills.srm_feishu_docs_bridge import DocumentSyncManager

manager = DocumentSyncManager()

# 测试创建文档
doc = manager.create_contract_draft(
    title="测试合同",
    content="# 测试内容",
    po_number="TEST-001",
    supplier_name="测试供应商"
)

print(f"文档创建成功: {doc.url}")
```

## 文档类型说明

| 文档类型 | 说明 | 关联关系 |
|---------|------|---------|
| CONTRACT_DRAFT | 合同草稿 | 根文档 |
| CONTRACT_AUDIT | 审核报告 | parent = 合同草稿 |
| CONTRACT_SIGNED | 签署后合同 | parent = 合同草稿 |
| INVOICE_MATCH | 三单匹配报告 | related = 合同草稿 |
| PAYMENT | 付款审批 | related = 合同草稿 |

## 追溯链路

系统通过以下方式实现追溯:

1. **Parent-Child 关系**: 审核报告作为子文档关联到合同
2. **Related Docs**: 三单匹配报告与合同建立双向关联
3. **PO Number**: 所有文档共享同一个采购单号
4. **文档元数据**: 本地存储完整的文档关系图谱

## 高级配置

### 自定义文档模板

你可以在飞书中创建一个合同模板，然后在创建合同时基于该模板:

```python
from skills.srm_feishu_docs_bridge.config import FeishuConfig

config = FeishuConfig.from_env()
config.doc_template_id = "你的模板文档ID"
```

### Webhook 集成

配置飞书事件订阅，实现文档变更通知:

```python
from skills.srm_im_bot_gateway import handle_feishu_webhook

# 在你的 webhook 处理器中
@app.post("/webhook/feishu")
async def webhook(request):
    event = await request.json()
    handle_feishu_webhook(event)
```

## 故障排除

### Token 获取失败

**症状**: `FeishuAPIError: 获取token失败`

**解决方案**:
1. 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
2. 确认应用已发布
3. 检查应用是否有足够的权限

### 文档创建失败

**症状**: `API调用失败: {'code': 99991661, 'msg': 'forbidden'}`

**解决方案**:
1. 确认应用有 `docx:document:write` 权限
2. 确认应用已开通文档权限
3. 检查文件夹 Token 是否有访问权限

### 关联失败

**症状**: 文档创建成功但无法关联

**解决方案**:
1. 检查本地存储目录 `./data/doc_chains` 是否存在且有写入权限
2. 检查文档 ID 是否正确传递

## 最佳实践

1. **定期备份**: 定期备份 `./data/doc_chains` 目录中的元数据
2. **监控限额**: 注意飞书 API 调用限额，大批量操作时添加延迟
3. **版本管理**: 重要合同修改时，创建新版本而非直接覆盖
4. **权限控制**: 通过飞书文档的分享功能控制访问权限

## 相关文档

- [飞书开放平台文档](https://open.feishu.cn/document/home/index)
- [飞书文档 API](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-create)
- [SKILLS.md](./SKILLS.md) - 技能详细说明
```

**Step 3: 提交**

```bash
git add .env.example
git add docs/FEISHU_INTEGRATION.md
git commit -m "docs: add feishu integration guide and environment config"
```

---

## 实施计划总结

### 已创建的文件

```
srm/
├── skills/
│   └── srm-feishu-docs-bridge/          # 新增技能
│       ├── __init__.py
│       ├── SKILL.md
│       ├── config.py
│       ├── client.py                    # 飞书API客户端
│       ├── models.py                    # 数据模型
│       └── sync_manager.py              # 同步管理器
│
├── skills/srm-contract-manager/
│   └── feishu_integration.py            # 飞书集成
│
├── skills/srm-invoice-matcher/
│   └── feishu_integration.py            # 飞书集成
│
├── examples/
│   ├── README.md
│   └── procurement_workflow_example.py  # 完整示例
│
├── docs/
│   └── FEISHU_INTEGRATION.md            # 集成指南
│
├── tests/
│   └── test_feishu_client.py            # 测试文件
│
├── requirements-feishu.txt              # 依赖
└── .env.example                         # 环境变量示例
```

### 下一步行动

完成上述 Task 1-6 后，系统具备以下能力:

1. ✅ **合同文档化**: 合同自动生成飞书文档
2. ✅ **审核可追溯**: 审核报告关联到合同文档
3. ✅ **三单关联**: 匹配报告与合同建立关联
4. ✅ **版本控制**: 文档版本自动记录
5. ✅ **链路追溯**: 通过采购单号查询完整文档链路

### 执行选项

**Plan complete and saved to `docs/plans/2025-03-28-feishu-docs-integration.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**

---

*计划编制完成 - 2025年3月*
