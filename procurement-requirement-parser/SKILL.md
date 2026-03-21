---
name: procurement-requirement-parser
description: Use when parsing unstructured procurement requests (chat logs, emails, text) into structured BOM for procurement workflows
---

# Procurement Requirement Parser

## Overview

Extracts structured procurement requirements from unstructured text input using LLM analysis. Converts informal requests into standardized BOM (物料清单) format ready for downstream procurement agents.

## When to Use

**Trigger conditions:**
- User submits procurement request as chat/email text
- Request contains informal language ("好一点"、"看着大气")
- Quantity, budget, or specs are implied but not explicit
- Request needs to be forwarded to `ecommerce-procurement-research` agent

**Not for:**
- Structured input (already has quantity, budget, specs)
- Urgent/emergency procurement with explicit details

## Input → Output Mapping

| Unstructured Input | Structured Output |
|-------------------|-------------------|
| "买10台机械键盘" | `quantity: 10, category: 键盘, item: 机械键盘` |
| "预算5000以内" | `budget_max: 5000, currency: CNY` |
| "手感好一点的" | `requirements: [手感好], priority: quality` |
| "给研发部" | `department: 研发部, requester: (extract from context)` |

## Extraction Schema

```json
{
  "items": [
    {
      "rank": 1,
      "item_name": "机械键盘",
      "category": "办公外设",
      "quantity": 10,
      "unit": "台",
      "budget_max": null,
      "requirements": ["手感好", "青轴"],
      "brand_preference": null,
      "priority": "quality"
    }
  ],
  "department": "研发部",
  "requester": null,
  "urgency": "normal",
  "budget_total": null,
  "notes": "性价比优先"
}
```

## Parsing Prompt Template

```
你是一个采购需求解析专家。请从以下非结构化文本中提取采购需求，输出JSON格式：

输入文本：
{user_input}

要求：
1. 提取所有采购物品，物品名称尽量具体
2. 从上下文推断数量（如果未明确，设为1）
3. 推断预算范围（如果未明确，设为null）
4. 提取特殊要求（如"手感好"、"品牌好"）到requirements数组
5. 判断优先级：quality（质量优先）、price（价格优先）、balanced（均衡）
6. 推断部门（如果未明确，从上下文判断或设为null）

输出格式（仅JSON，无其他内容）：
{
  "items": [...],
  "department": "...",
  "urgency": "normal|urgent|low",
  "budget_total": number|null,
  "notes": "..."
}
```

## Field Definitions

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `item_name` | string | 具体物品名称 | "机械键盘", "iPhone 15手机壳" |
| `category` | string | 物品分类 | "办公外设", "IT设备", "家具" |
| `quantity` | integer | 数量，默认1 | 10 |
| `unit` | string | 单位 | "台", "个", "套" |
| `budget_max` | number\|null | 单件预算上限 | 500 |
| `requirements` | string[] | 特殊要求 | ["手感好", "青轴"] |
| `brand_preference` | string\|null | 品牌偏好 | "Cherry", "罗技" |
| `priority` | enum | 优先级 | "quality", "price", "balanced" |
| `department` | string\|null | 需求部门 | "研发部" |
| `urgency` | enum | 紧急程度 | "urgent", "normal", "low" |

## Category Taxonomy

| 分类 | 示例物品 |
|------|----------|
| IT设备 | 电脑、显示器、键鼠 |
| 办公外设 | 打印机、扫描仪、投影仪 |
| 办公家具 | 办公桌、椅子、文件柜 |
| 办公用品 | 纸张、笔、本子 |
| 数码配件 | 手机壳、充电宝、数据线 |
| 工具/仪器 | 万用表、螺丝刀套装 |

## Output Integration

Parsed BOM can be passed to `ecommerce-procurement-research` skill:

```python
# Extract keywords for price research
for item in parsed_bom["items"]:
    keywords = item["item_name"]
    if item.get("requirements"):
        keywords += " " + " ".join(item["requirements"])
    # Pass to ProductResearcher
```

## Common Mistakes

| Mistake | Fix |
|---------|------|
| 忽略隐含数量 | "买键盘" → quantity=1, not null |
| 预算单位混淆 | 统一为CNY，"5000以内" → budget_max=5000 |
| 特殊要求丢失 | "要好看的" → requirements=["外观好看"] |
| 多物品未拆分 | "键盘鼠标一套" → 分开为2个items |

## Quality Checklist

- [ ] 每件物品有明确item_name（非"东西"、"设备"）
- [ ] 数量正确（默认1，未明确时推断）
- [ ] requirements数组非空（至少包含推断的质量/价格偏好）
- [ ] priority与特殊要求一致（"质量好" → priority=quality）
- [ ] 多物品分别列出（不合并）
