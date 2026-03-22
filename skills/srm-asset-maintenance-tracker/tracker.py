"""
IT资产维保跟踪器
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class ITAsset:
    asset_id: str
    asset_name: str
    category: str
    brand: str
    model: str
    serial_number: str
    purchase_date: str
    purchase_price: float
    warranty_end: str
    maintenance_end: str = ""
    depreciation_years: int = 5
    assigned_to: str = ""
    location: str = ""
    status: str = "in_use"
    
    def to_dict(self) -> dict:
        return asdict(self)


def get_warranty_status(asset: ITAsset) -> dict:
    """计算维保状态"""
    today = datetime.now()
    
    try:
        warranty_end = datetime.strptime(asset.warranty_end, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"status": "unknown", "risk_level": "unknown", "days_to_warranty": None}
    
    maintenance_end = None
    if asset.maintenance_end:
        try:
            maintenance_end = datetime.strptime(asset.maintenance_end, "%Y-%m-%d")
        except (ValueError, TypeError):
            pass
    
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
    elif days_to_warranty <= 90:
        status = "expiring_soon"
        risk_level = "low"
        actions.append("维保90天内到期")
    
    return {
        "status": status,
        "risk_level": risk_level,
        "days_to_warranty": days_to_warranty,
        "days_to_maintenance": days_to_maintenance,
        "actions": actions
    }


def calculate_depreciation(
    purchase_price: float,
    purchase_date: str,
    depreciation_years: int = 5
) -> dict:
    """计算资产折旧（中国税法直线法）"""
    try:
        purchase = datetime.strptime(purchase_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {
            "purchase_price": purchase_price,
            "current_value": purchase_price,
            "accumulated_depreciation": 0,
            "depreciation_rate": 0,
            "isFullyDepreciated": False
        }
    
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


def suggest_action(asset: ITAsset) -> dict:
    """建议续保或报废"""
    depreciation = calculate_depreciation(
        asset.purchase_price,
        asset.purchase_date,
        asset.depreciation_years
    )
    
    warranty_status = get_warranty_status(asset)
    
    if depreciation["isFullyDepreciated"]:
        return {
            "action": "retire",
            "reason": "资产已提完折旧，建议报废",
            "priority": "high"
        }
    
    if depreciation["depreciation_rate"] > 80:
        return {
            "action": "evaluate_retire",
            "reason": f"资产折旧{depreciation['depreciation_rate']}%，评估是否报废",
            "priority": "medium"
        }
    
    days = warranty_status["days_to_warranty"]
    if days is not None and days < 60:
        return {
            "action": "renew_maintenance",
            "reason": f"维保{days}天后到期",
            "priority": "high" if days < 30 else "medium"
        }
    
    return {
        "action": "monitor",
        "reason": "资产状态正常",
        "priority": "low"
    }


def generate_asset_report(assets: list[ITAsset]) -> str:
    """生成资产报告"""
    lines = ["# IT资产维保报告\n"]
    lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append(f"**资产总数:** {len(assets)}\n")
    
    # 按状态分组
    status_counts = {"active": 0, "expiring_soon": 0, "expired": 0}
    action_groups = {"renew": [], "retire": [], "monitor": []}
    
    for asset in assets:
        warranty_status = get_warranty_status(asset)
        status_counts[warranty_status["status"]] = status_counts.get(warranty_status["status"], 0) + 1
        
        action = suggest_action(asset)
        if action["action"] in ["renew_maintenance", "evaluate_retire"]:
            action_groups["renew"].append((asset, action))
        elif action["action"] == "retire":
            action_groups["retire"].append((asset, action))
        else:
            action_groups["monitor"].append((asset, action))
    
    lines.append("\n## 概览\n")
    lines.append(f"- 正常在用: {status_counts.get('active', 0)}台")
    lines.append(f"- 维保即将到期: {status_counts.get('expiring_soon', 0)}台")
    lines.append(f"- 维保已过期: {status_counts.get('expired', 0)}台")
    
    if action_groups["renew"]:
        lines.append("\n## 需要续保/评估\n")
        for asset, action in action_groups["renew"]:
            lines.append(f"- **{asset.asset_name}** ({asset.asset_id}): {action['reason']}")
    
    if action_groups["retire"]:
        lines.append("\n## 建议报废\n")
        for asset, action in action_groups["retire"]:
            lines.append(f"- **{asset.asset_name}** ({asset.asset_id}): {action['reason']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    asset = ITAsset(
        asset_id="PC-001",
        asset_name="联想ThinkPad X1",
        category="笔记本",
        brand="联想",
        model="X1 Carbon",
        serial_number="SN123456",
        purchase_date="2020-03-15",
        purchase_price=8000.0,
        warranty_end="2026-04-01",
        depreciation_years=5
    )
    
    status = get_warranty_status(asset)
    print("维保状态:", json.dumps(status, ensure_ascii=False, indent=2))
    
    depreciation = calculate_depreciation(asset.purchase_price, asset.purchase_date)
    print("\n折旧:", json.dumps(depreciation, ensure_ascii=False, indent=2))
    
    action = suggest_action(asset)
    print("\n建议:", json.dumps(action, ensure_ascii=False, indent=2))
