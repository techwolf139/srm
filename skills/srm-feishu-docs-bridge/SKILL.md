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