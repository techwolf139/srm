"""
知识产权侵权巡检
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class InfringementCase:
    platform: str
    shop_name: str
    shop_url: str
    product_url: str
    product_name: str
    price: float
    infringement_type: str
    evidence_screenshots: list = None
    first_seen: str = ""
    last_checked: str = ""
    status: str = "pending"
    
    def __post_init__(self):
        if self.evidence_screenshots is None:
            self.evidence_screenshots = []
        if not self.first_seen:
            self.first_seen = datetime.now().isoformat()
        if not self.last_checked:
            self.last_checked = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Brand:
    name: str
    trademark_no: str
    trademark_certificate: str
    logo_url: str = ""
    official_website: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


def generate_evidence_report(
    cases: list[InfringementCase],
    brand: Brand,
) -> str:
    """生成侵权证据报告"""
    lines = ["# 知识产权侵权证据报告\n"]
    lines.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append(f"**涉及品牌:** {brand.name}\n")
    lines.append(f"**商标证号:** {brand.trademark_no}\n")
    
    # 按平台分组统计
    by_platform = {}
    for case in cases:
        platform = case.platform
        if platform not in by_platform:
            by_platform[platform] = []
        by_platform[platform].append(case)
    
    lines.append("\n## 侵权概况\n")
    lines.append("| 平台 | 侵权店铺数 | 商品数 | 均价 |")
    lines.append("|------|-----------|--------|------|")
    
    for platform, platform_cases in by_platform.items():
        shops = set(c.shop_name for c in platform_cases)
        prices = [c.price for c in platform_cases]
        avg_price = sum(prices) / len(prices) if prices else 0
        lines.append(f"| {platform} | {len(shops)} | {len(platform_cases)} | ¥{avg_price:.0f} |")
    
    # 重点侵权店铺
    lines.append("\n## 重点侵权店铺\n")
    
    priority_shops = sorted(
        cases, 
        key=lambda x: x.price, 
        reverse=False
    )[:10]
    
    for i, case in enumerate(priority_shops, 1):
        lines.append(f"\n### {i}. {case.shop_name}（{case.platform}）\n")
        lines.append(f"- **店铺链接:** {case.shop_url}")
        lines.append(f"- **商品链接:** {case.product_url}")
        lines.append(f"- **商品名称:** {case.product_name}")
        lines.append(f"- **售价:** ¥{case.price}")
        lines.append(f"- **侵权类型:** {case.infringement_type}")
        lines.append(f"- **首次发现:** {case.first_seen[:10]}")
        lines.append(f"- **状态:** {case.status}")
    
    # 维权建议
    lines.append("\n## 维权建议\n")
    lines.append("1. **优先处理:** 销量大、评分高的店铺")
    lines.append("2. **投诉渠道:**")
    lines.append("   - 淘宝/天猫: 阿里知产保护平台 (ipp.alibaba.com)")
    lines.append("   - 京东: 京东维权平台")
    lines.append("   - 拼多多: 拼多多知产保护")
    lines.append("3. **处理周期:** 3-7个工作日")
    lines.append("4. **后续行动:** 未下架则发律师函")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    brand = Brand(
        name="XX品牌",
        trademark_no="CN12345678",
        trademark_certificate="https://example.com/cert.pdf"
    )
    
    cases = [
        InfringementCase(
            platform="淘宝",
            shop_name="xxx旗舰店",
            shop_url="https://shopxxx.taobao.com",
            product_url="https://item.xxx.com/123",
            product_name="XX品牌同款 键盘",
            price=89.0,
            infringement_type="商标侵权",
            status="pending"
        ),
        InfringementCase(
            platform="拼多多",
            shop_name="低价批发店",
            shop_url="https://mobile.pinduoduo.com/shop/xxx",
            product_url="https://mobile.pinduoduo.com/goods/123",
            product_name="XX品牌 机械键盘",
            price=45.0,
            infringement_type="假货",
            status="pending"
        ),
    ]
    
    report = generate_evidence_report(cases, brand)
    print(report)
