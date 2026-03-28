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
cd examples

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