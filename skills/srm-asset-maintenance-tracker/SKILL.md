---
name: asset-maintenance-tracker
description: Use when tracking IT asset warranties and maintenance contracts, automating renewal alerts, or generating equipment procurement recommendations
---

# Asset Maintenance Tracker

## Overview

跟踪IT设备（电脑、服务器、网络设备）的维保期限，在到期前自动发起延保询价或报废重采流程。

## When to Use

**触发条件：**
- 设备维保即将到期（30/60/90天提醒）
- 设备故障率上升
- 设备使用年限到期
- 年度IT资产盘点
- 设备报废评估

**不适用：**
- 实时故障处理
- 紧急采购

## 设备分类

| 类别 | 示例 | 典型使用寿命 | 维保周期 |
|------|------|-------------|----------|
| 台式电脑 | 办公台式机 | 5年 | 3年 |
| 笔记本电脑 | ThinkPad等 | 3年 | 3年 |
| 服务器 | Dell PowerEdge | 5年 | 3年 |
| 网络设备 | 交换机、路由器 | 5年 | 3年 |
| 打印机 | 激光打印机 | 4年 | 2年 |
| 显示器 | 27寸显示器 | 5年 | 可不维保 |

## 数据结构

```python
class ITAsset:
    asset_id: str           # 资产编号
    asset_name: str         # 资产名称
    category: str          # 类别
    brand: str             # 品牌
    model: str             # 型号
    serial_number: str      # 序列号
    purchase_date: str     # 采购日期
    warranty_end: str       # 质保到期日
    maintenance_end: str    # 维保到期日
    depreciation_years: int # 折旧年限
    current_value: float    # 当前净值
    assigned_to: str       # 使用人
    location: str          # 位置
    status: str            # in_use/maintenance/retired
```

## 维保状态计算

```python
def get_warranty_status(asset: ITAsset) -> dict:
    """计算维保状态"""
    today = datetime.now()
    warranty_end = parse_date(asset.warranty_end)
    maintenance_end = parse_date(asset.maintenance_end) if asset.maintenance_end else None
    
    days_to_warranty = (warranty_end - today).days
    days_to_maintenance = (maintenance_end - today).days if maintenance_end else None
    
    status = "active"
    risk_level = "low"
    actions = []
    
    if days_to_warranty < 0:
        status = "expired"
        risk_level = "high"
        actions.append("维保已过期，建议立即续保")
    elif days_to_warranty <= 30:
        status = "expiring_soon"
        risk_level = "high"
        actions.append("维保30天内到期，请尽快处理")
    elif days_to_warranty <= 60:
        status = "expiring_soon"
        risk_level = "medium"
        actions.append("维保60天内到期")
    
    return {
        "status": status,
        "risk_level": risk_level,
        "days_to_warranty": days_to_warranty,
        "days_to_maintenance": days_to_maintenance,
        "actions": actions
    }
```

## 折旧计算

```python
def calculate_depreciation(
    purchase_price: float,
    purchase_date: str,
    depreciation_years: int = 5
) -> dict:
    """
    计算资产折旧
    中国税法：直线法折旧
    """
    purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
    today = datetime.now()
    
    months_used = (today.year - purchase.year) * 12 + (today.month - purchase.month)
    total_months = depreciation_years * 12
    
    depreciation_rate = min(months_used / total_months, 1.0)
    current_value = purchase_price * (1 - depreciation_rate)
    accumulated_depreciation = purchase_price * depreciation_rate
    
    return {
        "purchase_price": purchase_price,
        "current_value": round(current_value, 2),
        "accumulated_depreciation": round(accumulated_depreciation, 2),
        "depreciation_rate": round(depreciation_rate * 100, 1),
        "isFullyDepreciated": depreciation_rate >= 1.0
    }
```

## 续保/报废建议

```python
def suggest_action(asset: ITAsset) -> dict:
    """建议续保或报废"""
    depreciation = calculate_depreciation(
        asset.purchase_price,
        asset.purchase_date,
        asset.depreciation_years
    )
    
    warranty_status = get_warranty_status(asset)
    
    # 判断逻辑
    if depreciation["isFullyDepreciated"]:
        return {
            "action": "retire",
            "reason": "资产已提完折旧，建议报废",
            "priority": "high"
        }
    
    if depreciation["depreciation_rate"] > 80:
        return {
            "action": "evaluate_retire",
            "reason": "资产折旧>80%，评估是否报废",
            "priority": "medium"
        }
    
    if warranty_status["days_to_warranty"] < 60:
        return {
            "action": "renew_maintenance",
            "reason": f"维保{warranty_status['days_to_warranty']}天后到期",
            "priority": "high" if warranty_status["days_to_warranty"] < 30 else "medium"
        }
    
    return {
        "action": "monitor",
        "reason": "资产状态正常",
        "priority": "low"
    }
```

## 报告生成

```markdown
# IT资产维保报告

**生成时间:** 2026-03-21
**统计范围:** 全公司IT设备

---

## 一、概览

| 状态 | 数量 | 占比 |
|------|------|------|
| 正常在用 | 156 | 72% |
| 维保即将到期(30天) | 12 | 6% |
| 维保已过期 | 5 | 2% |
| 折旧>80% | 18 | 8% |
| 已报废 | 26 | 12% |

---

## 二、急需处理

### 2.1 维保已过期 (5台)

| 资产编号 | 设备名称 | 使用人 | 购买日期 | 当前价值 |
|----------|----------|--------|----------|----------|
| PC-001 | 联想ThinkPad | 张三 | 2020-03-15 | ¥800 |
| PC-002 | 联想ThinkPad | 李四 | 2020-03-15 | ¥800 |

### 2.2 维保30天内到期 (12台)

| 资产编号 | 设备名称 | 维保到期 | 建议 |
|----------|----------|----------|------|
| SRV-001 | Dell服务器 | 2026-04-10 | 立即续保 |

---

## 三、续保询价建议

| 部门 | 设备数 | 预估续保费用 | 优先级 |
|------|--------|-------------|--------|
| 研发部 | 5台 | ¥15,000 | 高 |
| 市场部 | 3台 | ¥9,000 | 中 |

**操作建议:**
1. 联系 Dell 售后获取续保报价
2. 对比第三方维保服务
3. 考虑设备整体更换方案
```

## 常见错误

| 错误 | 纠正 |
|------|------|
| 维保过期才处理 | 设置30/60/90天多级提醒 |
| 不记录序列号 | 序列号是维保凭证 |
| 忽略小设备 | 显示器、键盘也应纳入管理 |
| 不做年度盘点 | 实际盘点对账资产台账 |

## 质量检查表

- [ ] 资产台账与实物一致
- [ ] 维保到期日已记录
- [ ] 续保建议有依据
- [ ] 报废建议有折旧计算支撑
- [ ] 报告包含具体设备清单
