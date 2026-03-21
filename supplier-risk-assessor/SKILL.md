---
name: supplier-risk-assessor
description: Use when assessing supplier risk from Chinese e-commerce platforms, checking company credibility, litigation history, or generating supplier admission reports
---

# Supplier Risk Assessor

## Overview

评估供应商风险，查询国内企业信用数据平台（天眼查、企查查、裁判文书网等），生成供应商准入评估报告，过滤高风险供应商。

## When to Use

**触发条件：**
- 收到 `ecommerce-procurement-research` 输出的 CSV（含供应商名称）
- 需要验证低价供应商是否靠谱
- 采购决策前需要风控评估
- 新供应商准入审核

**不适用：**
- 已认证老供应商
- 紧急采购（速度优先于风控）

## 输入 → 输出

| 输入 | 输出 |
|------|------|
| CSV（含 supplier_name 列） | 风险评估报告（Markdown） |
| 供应商名称列表 | 批量风险评估结果 |
| 电商平台店铺URL | 店铺主体企业信息 + 风险数据 |

## 风险维度（国内适配）

| 维度 | 数据来源 | 权重 |
|------|----------|------|
| 失信被执行人 | 中国执行信息公开网 | 25% |
| 涉诉记录 | 裁判文书网 | 20% |
| 经营异常 | 国家企业信用信息公示系统 | 20% |
| 行政处罚 | 市场监督管理总局 | 15% |
| 税务异常 | 税务部门公开信息 | 10% |
| 注册资本实缴 | 企业年报 | 10% |

## 风险评分公式

```
risk_score = (
  dishonest_count * 25 +      # 失信记录
  litigation_count * 20 +      # 诉讼记录
  abnormal_count * 20 +       # 经营异常
  penalty_count * 15 +        # 行政处罚
  tax_abnormal * 10 +         # 税务异常
  capital_unpaid * 10          # 注册资金未实缴
)
```

**风险等级：**
- `LOW` (0-30): 供应商可推荐
- `MEDIUM` (31-60): 建议谨慎合作，需担保
- `HIGH` (61-100): 供应商不推荐

## 国内数据源集成

### 1. 天眼查 API（推荐）
```python
# 需配置 TIANYANCHA_API_KEY
def query_tianyancha(company_name: str) -> dict:
    """查询企业工商信息、风险数据"""
    headers = {"Authorization": f"Bearer {TIANYANCHA_API_KEY}"}
    response = requests.get(
        f"https://api.tianyancha.com/v4/company/{company_name}/risk",
        headers=headers,
        timeout=10
    )
    return response.json()
```

### 2. 企查查 API
```python
# 需配置 QICHACHA_API_KEY
def query_qichacha(company_name: str) -> dict:
    """查询企业风险、失信、被执行人信息"""
    headers = {"Token": QICHACHA_API_KEY}
    response = requests.get(
        f"https://www.qcc.com/api/company/{company_name}/risk",
        headers=headers,
        timeout=10
    )
    return response.json()
```

### 3. 裁判文书网（公开数据）
```python
def query_wenshu(court: str = "default", case_number: str = "") -> dict:
    """查询涉诉记录（需验证码处理）"""
    # https://wenshu.court.gov.cn
    pass
```

### 4. 中国执行信息公开网
```python
def query_zxgk(company_name: str) -> dict:
    """查询失信被执行人信息"""
    # https://zxgk.court.gov.cn
    pass
```

### 5. 国家企业信用信息公示系统
```python
def query_gsxt(company_name: str) -> dict:
    """查询经营异常、行政处罚、严重违法"""
    # https://www.gsxt.gov.cn
    pass
```

### 备选：1688供应商特供
```python
def parse_1688_supplier(supplier_id: str) -> dict:
    """解析1688供应商ID获取企业信息"""
    # 1688店铺通常有认证企业信息
    pass
```

## 输出格式

```json
{
  "supplier_name": "深圳市xxx科技有限公司",
  "unified_credit_code": "91440300MA5xxxxx",
  "risk_score": 45,
  "risk_level": "MEDIUM",
  "dimensions": {
    "dishonest_count": 0,
    "litigation_count": 2,
    "abnormal_count": 0,
    "penalty_count": 1,
    "tax_abnormal": false,
    "registered_capital": "100万(实缴50万)",
    "established_date": "2015-03-20",
    "business_status": "存续"
  },
  "recommendation": "建议谨慎合作，建议要求预付款或支付宝担保交易",
  "details": [
    {"type": "litigation", "count": 2, "summary": "合同纠纷2起，案值共3.2万"},
    {"type": "penalty", "count": 1, "summary": "2023年税务罚款5000元"}
  ],
  "data_sources": ["天眼查", "国家企业信用信息公示系统"],
  "checked_at": "2026-03-21T10:00:00+08:00"
}
```

## 批量处理

```python
def assess_suppliers_from_csv(csv_path: str) -> list[dict]:
    """批量评估CSV中的所有供应商"""
    import pandas as pd
    df = pd.read_csv(csv_path)
    results = []
    for _, row in df.iterrows():
        supplier_name = row.get("supplier_name") or row.get("shop_name")
        if supplier_name:
            risk = assess_supplier(supplier_name)
            risk["source_row"] = row.to_dict()
            results.append(risk)
    return results
```

## 报告生成

```python
def generate_risk_report(assessments: list[dict]) -> str:
    """生成供应商风险评估Markdown报告"""
    # 按风险分数排序
    # 高风险供应商红色预警
    # 中风险供应商黄色预警
    # 低风险供应商绿色通过
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 只看价格忽略风险 | 风险评分必须参与最终决策 |
| 忽略失信被执行人 | 国内特有的"老赖"问题 |
| 忽略经营异常 | 经营异常=执照可被吊销 |
| 信任新公司 | 成立<1年风险较高 |
| 不查税务异常 | 税务异常影响发票获取 |
| 只用一家数据源 | 建议天眼查+企查查交叉验证 |

## 质量检查表

- [ ] 每个供应商都有风险分数和等级
- [ ] 高风险供应商红色标记
- [ ] 有明确的准入/不准入建议
- [ ] 报告包含数据来源和时间戳（北京时间）
- [ ] 包含统一社会信用代码
- [ ] 关联到采购询价的原始价格数据
