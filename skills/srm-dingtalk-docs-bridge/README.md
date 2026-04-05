
# SRM 钉钉文档桥接（srm-dingtalk-docs-bridge）

## 功能概述

将合同生成、审核和三单匹配结果同步到钉钉文档。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements-dingtalk.txt
```

### 2. 配置环境变量

```bash
export DINGTALK_APP_KEY="your_app_key"
export DINGTALK_APP_SECRET="your_app_secret"
```

### 3. 使用示例

```python
from skills.srm_dingtalk_docs_bridge import (
    DingTalkClient,
    DingTalkDocumentSyncManager,
    DingTalkTemplateAdapter,
)

# 初始化客户端
client = DingTalkClient(
    app_key="your_app_key",
    app_secret="your_app_secret",
)

# 初始化同步管理器
manager = DingTalkDocumentSyncManager()

# 生成合同内容
adapter = DingTalkTemplateAdapter()
content = adapter.generate_contract_draft(
    title="采购合同",
    contract_data={
        "supplier_name": "测试供应商",
        "total_amount": 50000.00,
    }
)

# 创建钉钉文档
doc_metadata = manager.create_contract_draft(
    title="采购合同",
    content=content,
    po_number="PO-2024-001",
    supplier_name="测试供应商"
)

print(f"文档已创建：{doc_metadata.url}")
```

## 环境配置

| 变量名 | 必需 | 说明 |
|-------|------|------|
| `DINGTALK_APP_KEY` | 是 | 钉钉应用凭证 Key |
| `DINGTALK_APP_SECRET` | 是 | 钉钉应用凭证 Secret |
| `DINGTALK_BASE_URL` | 否 | 钉钉 API 基础 URL |

## API 文档

参考 [钉钉开放平台文档](https://open.dingtalk.com/document)

---

*最后更新时间：2026 年 4 月*

