---
name: dingtalk-docs-bridge
description: Use when creating, updating, or managing DingTalk documents for procurement contracts, audit reports, or invoice matching results. Handles document creation, version control, and cross-document linking.
---

# DingTalk Docs Bridge

## Overview

将合同、审核报告和三单匹配结果同步到钉钉文档，建立可追溯的文档链路。

## Capabilities

- 创建钉钉文档（从 Markdown/DOCX 模板）
- 更新文档内容
- 添加文档评论（用于审核意见）
- 建立文档关联
- 版本历史管理

## Input/Output

**Input:**
- doc_type: contract|audit|invoice_match
- content: Markdown 或 DOCX 内容
- metadata: 文档元数据

**Output:**
- doc_id: 钉钉文档 ID
- doc_url: 访问链接
- version: 版本号

## Configuration

**环境变量:**
- `DINGTALK_APP_KEY`: 钉钉应用凭证 Key
- `DINGTALK_APP_SECRET`: 钉钉应用凭证 Secret