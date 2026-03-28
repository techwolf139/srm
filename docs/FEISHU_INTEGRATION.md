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
cp .env.example .env
vim .env  # 填入你的应用凭证
```

### 5. 验证集成

```python
from skills.srm_feishu_docs_bridge import DocumentSyncManager

manager = DocumentSyncManager()

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

## 最佳实践

1. **定期备份**: 定期备份 `./data/doc_chains` 目录中的元数据
2. **监控限额**: 注意飞书 API 调用限额，大批量操作时添加延迟
3. **版本管理**: 重要合同修改时，创建新版本而非直接覆盖
4. **权限控制**: 通过飞书文档的分享功能控制访问权限

## 相关文档

- [飞书开放平台文档](https://open.feishu.cn/document/home/index)
- [飞书文档 API](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-create)
- [SKILLS.md](./SKILLS.md) - 技能详细说明