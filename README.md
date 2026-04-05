# SRM 智能体系统 - 企业采购智能化解决方案

> 从采购全生命周期视角，讲述如何配置业务流程实现采购智能化

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)

---

## 📋 项目概览

SRM（Supplier Relationship Management）智能体系统是一个面向中国企业采购场景的智能自动化解决方案。系统包含 **12个智能体技能**，覆盖采购全生命周期（采购前→采购中→采购后）以及跨部门横向扩展场景。

### 核心能力
- **AI驱动**：基于LLM的自然语言理解和流程编排
- **全流程覆盖**：从需求解析到付款审批的完整闭环
- **国内适配**：符合中国法律法规和商业惯例
- **多部门协作**：采购、HR、法务、市场、IT等多职能支持

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Playwright（数据抓取）
- OpenAI API Key 或国内大模型API

### 安装依赖

```bash
# 克隆仓库
git clone <repository-url>
cd srm

# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入API密钥
```

### 使用单个技能

```python
# 示例：使用电商采购研究技能
from skills.srm_ecommerce_procurement_research import EcommerceResearcher

researcher = EcommerceResearcher()
results = researcher.research("机械键盘", platforms=["jd", "taobao"])
print(results.to_markdown())
```

### 运行完整流程

```python
# 采购全生命周期示例
from skills import (
    ProcurementRequirementParser,
    EcommerceResearcher,
    SupplierRiskAssessor,
    ContractGenerator,
    ContractAuditor,
    InvoiceMatcher
)

# 1. 解析需求
parser = ProcurementRequirementParser()
bom = parser.parse("给研发部买10台机械键盘，预算5000以内")

# 2. 多平台比价
researcher = EcommerceResearcher()
price_report = researcher.research_from_bom(bom)

# 3. 供应商风控
assessor = SupplierRiskAssessor()
risk_report = assessor.assess(price_report.suppliers)

# ... 继续后续流程
```

---

## 📁 项目结构

```
srm/
├── skills/                          # 智能体技能目录
│   ├── srm-procurement-requirement-parser/    # 需求解析
│   ├── srm-ecommerce-procurement-research/    # 电商采购研究
│   ├── srm-supplier-risk-assessor/            # 供应商风控
│   ├── srm-contract-generator/                # 合同生成
│   ├── srm-contract-audit/                    # 合同审核
│   ├── srm-invoice-matcher/                   # 三单匹配
│   ├── srm-talent-salary-researcher/          # 人才薪酬研究
│   ├── srm-competitor-monitor/                # 竞品监测
│   ├── srm-ip-infringement-scanner/           # 侵权巡检
│   ├── srm-im-bot-gateway/                    # IM机器人网关
│   ├── srm-web-reader/                        # 网页阅读
│   └── srm-asset-maintenance-tracker/         # 资产维保
├── docs/                            # 文档目录
│   ├── SKILLS.md                   # 技能详细说明
│   └── concept.md                  # 概念设计文档
├── logs/                            # 日志目录
├── README.md                        # 项目说明
└── .env.example                     # 环境变量示例
```

### 技能目录命名规范

所有技能遵循统一的命名规范：`srm-{function}-{subfunction}`

- `srm-`：项目前缀
- `{function}`：职能领域（procurement/talent/competitor/ip/asset）
- `{subfunction}`：具体功能（research/assess/generate/audit/match）

---

## 🤖 智能体调用系统（Agent Calling System）

### 面向AI智能体的调用接口

本系统为AI智能体提供了标准化的调用接口，支持自然语言意图识别和技能路由。

#### 1. 技能发现（Skill Discovery）

每个技能目录包含 `SKILL.md` 文件，遵循 OpenCode Skill Protocol：

```yaml
name: ecommerce-procurement-research
description: Use when researching product prices from Chinese e-commerce platforms (Taobao, JD, PDD, 1688)

parameters:
  keyword:
    type: string
    description: Product name or search keyword
    required: true
  platforms:
    type: array
    description: Platforms to search
    enum: [taobao, jd, pdd, "1688"]
    default: [jd, taobao]
  
output:
  format: markdown
  schema: |
    | rank | product_name | price | rating | platform |
    |------|--------------|-------|--------|----------|
```

#### 2. 意图路由（Intent Routing）

```python
# IM机器人网关自动路由用户意图到对应技能
INTENT_ROUTING_TABLE = {
    "询价": "srm-ecommerce-procurement-research",
    "比价": "srm-ecommerce-procurement-research",
    "供应商风控": "srm-supplier-risk-assessor",
    "查公司": "srm-supplier-risk-assessor",
    "生成合同": "srm-contract-generator",
    "审核合同": "srm-contract-audit",
    "发票匹配": "srm-invoice-matcher",
    "招聘": "srm-talent-salary-researcher",
    "竞品监控": "srm-competitor-monitor",
    "侵权检测": "srm-ip-infringement-scanner",
    "读网页": "srm-web-reader",
}
```

#### 3. 技能调用协议

```python
# 标准技能接口
class SkillInterface:
    """所有技能必须实现的接口"""
    
    @property
    def name(self) -> str:
        """技能唯一标识名"""
        pass
    
    @property
    def description(self) -> str:
        """技能功能描述（用于LLM路由）"""
        pass
    
    def can_handle(self, intent: str) -> bool:
        """判断是否可以处理该意图"""
        pass
    
    def execute(self, input_data: dict) -> dict:
        """执行技能逻辑"""
        pass
```

#### 4. 数据流转规范

```
用户输入 → 意图识别(NLP) → 技能路由 → 参数提取 → 技能执行 → 结果格式化 → 返回用户
```

#### 5. 技能间协作

```python
# 技能可以链式调用
workflow = [
    {"skill": "srm-procurement-requirement-parser", "input": "user_request"},
    {"skill": "srm-ecommerce-procurement-research", "input": "bom_output"},
    {"skill": "srm-supplier-risk-assessor", "input": "csv_suppliers"},
    {"skill": "srm-contract-generator", "input": "selected_supplier"},
]
```

---

## 🏗️ 技术架构

### 技术栈

| 类别 | 技术选型 |
|------|----------|
| **编程语言** | Python 3.10+ |
| **数据抓取** | Playwright（动态网页）、Jina Reader API（静态网页） |
| **数据处理** | Pandas、NumPy |
| **LLM调用** | OpenAI API / 智谱AI / 通义千问 |
| **API框架** | FastAPI（可选） |
| **企业集成** | 飞书SDK、企业微信SDK、钉钉SDK |
| **国内数据源** | 天眼查API、企查查API、裁判文书网 |
| **发票查验** | 国家税务总局发票查验平台 |

---

## 一、平台集成

SRM 系统已支持与主流采购及企业数据平台的对接，实现采购全流程数字化管理。

### 国内主流电商平台对接 (ecommerce-procurement-research)

**功能覆盖**：
- 商品比价：淘宝/天猫/京东/拼多多/1688 多平台价格抓取
- 数据清洗：统一商品标题、规格、价格格式
- 竞品监控：历史价格追踪、促销力度分析
- 供应商筛选：按销量/评分/价格排序

**接入方式**：Playwright 爬虫 + Jina Reader API

---

### 企业信用数据源对接 (supplier-risk-assessor)

**功能覆盖**：
- 工商信息查询：天眼查、企查查企业工商登记
- 失信被执行人：裁判文书网、中国执行信息公开网
- 经营异常：国家企业信用信息公示系统
- 行政处罚：市场监督管理总局数据
- 涉诉查询：裁判文书网案件记录

**接入方式**：官方 API / 网页抓取

---

## 二、核心业务场景

### 场景1：采购需求智能解析

**用户痛点**：业务部门提交采购需求语言随意（"要买个好用的笔记本"），采购团队理解成本高，沟通反复。

**解决思路**：

```
非结构化文本 → NLP语义解析 → 结构化BOM → 标准采购单
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | procurement-requirement-parser | 将"好用的笔记本"解析为品牌、配置、数量 |
| 2 | ecommerce-procurement-research | 多平台比价，获取市场行情 |
| 3 | supplier-risk-assessor | 筛选合格供应商 |

**业务价值**：需求沟通轮次减少 → 采购周期缩短

---

### 场景2：供应商准入风控

**用户痛点**：新供应商合作前不了解其经营状况，遇到皮包公司或失信企业风险高。

**解决思路**：

```
供应商名称 → 多数据源核查 → 风险评分 → 准入决策
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | supplier-risk-assessor | 查询工商、失信、涉诉、行政处罚 |
| 2 | 风险评分模型 | 加权计算综合风险分 |
| 3 | 人工复核 | 高风险供应商人工审核 |

**风险维度与权重**：

| 维度 | 权重 | 数据来源 |
|------|------|----------|
| 失信被执行人 | 25% | 中国执行信息公开网 |
| 涉诉记录 | 20% | 裁判文书网 |
| 经营异常 | 20% | 国家企业信用信息公示系统 |
| 行政处罚 | 15% | 市场监督管理总局 |
| 税务异常 | 10% | 税务部门公开信息 |
| 注册资本实缴 | 10% | 企业年报 |

**业务价值**：供应商风险提前识别 → 损失规避

---

### 场景3：合同生成与审核

**用户痛点**：合同条款依赖法务人工审核，耗时长；格式不统一，易漏关键条款。

**解决思路**：

```
采购信息 → 模板填充 → 合同草稿 → AI审核 → 风险提示 → 人工签署
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | contract-generator | 自动填充合同模板（甲方/乙方/金额/交付/质保） |
| 2 | contract-audit | AI预审，识别风险条款（违约金/管辖法院/预付款） |
| 3 | Human Approval | 法务最终确认 |

**国内法规适配**：

| 《民法典》条款 | 要点 |
|---------------|------|
| 第465条 | 合同约束力 |
| 第496条 | 格式条款定义 |
| 第497条 | 格式条款无效情形 |
| 第506条 | 合同无效情形 |
| 第585条 | **违约金上限（不超过实际损失30%）** |
| 第590条 | 不可抗力条款 |

**业务价值**：合同审核从天级降到分钟级 → 法务效率提升

---

### 场景4：三单匹配与付款

**用户痛点**：采购单、收货单、发票人工核对，三单不一致时溯源困难，财务付款慢。

**解决思路**：

```
采购单(PO) ←→ 收货单(GR) ←→ 发票(Invoice) → 三单匹配 → 付款审批
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | invoice-matcher | 自动核对三单金额、数量、税率 |
| 2 | 异常标记 | 部分匹配时自动标记异常项 |
| 3 | Human Approval | 财务付款审批 |

**匹配规则**：
- 金额匹配：发票含税金额 ≈ 采购单金额 (±0.01允许误差)
- 数量匹配：发票数量 ≤ 采购数量
- 税率匹配：与采购要求一致
- 供应商匹配：发票销售方 ≈ 采购供应商

**国内发票支持**：

| 发票类型 | 税率 | 可抵扣 |
|----------|------|--------|
| 增值税专用发票 | 6%/9%/13% | 是 |
| 增值税普通发票 | 6%/9%/13% | 否 |
| 电子发票 | 同上 | 同上 |

**业务价值**：三单核对自动化 → 付款周期缩短 → 供应商满意度提升

---

### 场景5：人才招聘与薪酬对标

**用户痛点**：招聘时不了解市场薪酬水平，定薪随意导致人才流失或成本浪费。

**解决思路**：

```
职位JD解析 → 市场薪酬数据查询 → P25/P50/P75分位对标 → Offer建议
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | talent-salary-researcher | 解析JD中的职级/技能要求 |
| 2 | 薪酬数据查询 | 拉勾/猎聘/看准网薪酬数据 |
| 3 | 分位计算 | 按经验年限计算P25/P50/P75 |

**薪酬对标算法**：

```python
level_factors = {
    "entry": 0.7,      # 校招
    "junior": 0.85,    # 1-3年
    "mid": 1.0,        # 3-5年
    "senior": 1.2,     # 5-8年
    "expert": 1.5       # 8年+
}
```

**业务价值**：薪酬定薪有据可依 → 人才offer接受率提升

---

### 场景6：竞品舆情监测

**用户痛点**：不了解竞品动态，错失市场反应时机。

**解决思路**：

```
竞品关键词 → 全平台数据抓取 → 舆情分析 → 周报推送
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | competitor-monitor | 小红书/抖音/微博/什么值得买数据抓取 |
| 2 | 情感分析 | 正负面评价分类 |
| 3 | 竞品对比 | 价格/功能/口碑多维度对比 |

**支持平台**：

| 平台 | 数据类型 | 抓取难度 |
|------|----------|----------|
| 小红书 | 种草笔记、商品链接 | 中 |
| 抖音 | 短视频、直播 | 高 |
| 微博 | 品牌官微、话题 | 低 |
| 什么值得买 | 优惠信息、历史价 | 低 |

**业务价值**：竞品动态实时掌握 → 市场决策有依据

---

### 场景7：知识产权侵权巡检

**用户痛点**：品牌被仿冒、商标被滥用，线下维权效率低。

**解决思路**：

```
品牌/商标信息 → 电商平台巡检 → 侵权证据截图 → 投诉提交
```

**配置方案**：

| 步骤 | 技能 | 解决的问题 |
|------|------|-----------|
| 1 | ip-infringement-scanner | 淘宝/京东/拼多多/1688 侵权检测 |
| 2 | 证据固化 | 自动截图 + 商标证关联 |
| 3 | 批量投诉 | 阿里知产平台/京东维权平台批量提交 |

**侵权类型**：

| 类型 | 说明 | 证据要求 |
|------|------|----------|
| 商标侵权 | 未经授权使用注册商标 | 商标证 + 侵权截图 |
| 专利侵权 | 外观/实用新型/发明专利 | 专利证书 + 侵权证据 |
| 著作权侵权 | 图片、文案抄袭 | 著作权登记证 + 侵权内容 |
| 假货 | 假冒品牌 | 鉴定报告 + 购买鉴定 |

**业务价值**：品牌保护效率提升 → 假货打击力度加强

---

## 三、预置业务流程（开箱即用）

### 流程A：采购全生命周期

**适用场景**：从需求录入到付款完成的完整采购闭环

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  需求录入   │ →  │  需求解析   │ →  │  多平台比价 │
│ (非结构化) │    │ (BOM输出)   │    │ (CSV报告)  │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  供应商风控 │
                                        │ (风险评分)  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  合同生成   │
                                        │ (模板填充)  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  合同审核   │
                                        │ (AI预审)   │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  Human签署  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  三单匹配   │
                                        │ (发票核对)  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  付款审批   │
                                        └─────────────┘
```

**解决的问题**：
- 需求理解歧义 → 结构化解析
- 价格不透明 → 多平台比价
- 供应商风险未知 → 多数据源核查
- 合同条款遗漏 → 模板填充+AI审核
- 三单人工核对 → 自动匹配
- 付款审批慢 → 流程自动化

---

### 流程B：供应商准入审查

**适用场景**：新供应商首次合作前的准入审核

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  供应商名称 │ →  │  工商查询   │ →  │  失信核查   │
│ (天眼查)    │    │ (工商信息)  │    │ (执行信息)  │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  涉诉查询   │
                                        │ (裁判文书)  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  经营异常   │
                                        │ (信用公示)  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  风险评分   │
                                        │ (综合评级)  │
                                        └─────────────┘
                                              ↓
                                        ┌─────────────┐
                                        │  Human准入  │
                                        └─────────────┘
```

**解决的问题**：
- 不了解供应商背景 → 工商信息自动查
- 不知是否有失信记录 → 多法院数据覆盖
- 风险程度不量化 → 标准风险评分模型
- 准入决策主观 → 分级阈值+人工复核

---

### 流程C：IM机器人对话式采购

**适用场景**：业务部门通过企业微信/飞书/钉钉机器人发起采购

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  用户消息   │ →  │  意图识别   │ →  │  技能路由   │
│ (@机器人)   │    │ (NLP分类)   │    │ (路由表)    │
└─────────────┘    └─────────────┘    └─────────────┘
                                              ↓
                              ┌───────────────┼───────────────┐
                              ↓               ↓               ↓
                        ┌───────────┐   ┌───────────┐   ┌───────────┐
                        │ 询价技能  │   │ 风控技能  │   │ 合同技能  │
                        └───────────┘   └───────────┘   └───────────┘
```

**IM路由表**：

| 命令示例 | 触发技能 | 说明 |
|----------|----------|------|
| 询价 "iPhone 15手机壳" | `ecommerce-procurement-research` | 多平台比价 |
| 供应商风控 "xxx公司" | `supplier-risk-assessor` | 风险评估 |
| 合同审核 | `contract-audit` | 条款审核 |
| 合同生成 | `contract-generator` | 模板填充 |
| 发票报销 | `invoice-matcher` | 三单匹配 |
| 人才招聘 "Python开发" | `talent-salary-researcher` | 薪酬对标 |
| 竞品监控 | `competitor-monitor` | 舆情分析 |
| 侵权巡检 | `ip-infringement-scanner` | 侵权检测 |
| 帮我读一下这个网页 | `web-reader` | Jina Reader |
| 帮助 | `im-bot-gateway` | 技能说明 |

**解决的问题**：
- 采购需登录系统 → 群聊@机器人即可
- 不知道用什么技能 → 自然语言意图识别
- 技能分散难找 → 统一入口

---

## 四、自定义场景配置

### 如何设计新采购流程

**Step 1：明确业务目标**
- 要解决什么问题？（降本/合规/效率）
- 涉及哪些角色（需求方/采购/财务/法务）？
- 关键节点有哪些？

**Step 2：选择技能组件**

| 目标 | 推荐技能 |
|------|----------|
| 需求解析 | procurement-requirement-parser |
| 多平台比价 | ecommerce-procurement-research |
| 供应商风控 | supplier-risk-assessor |
| 合同生成 | contract-generator |
| 合同审核 | contract-audit |
| 三单匹配 | invoice-matcher |
| 薪酬对标 | talent-salary-researcher |
| 竞品监测 | competitor-monitor |
| 侵权巡检 | ip-infringement-scanner |
| IM集成 | im-bot-gateway |
| 网页读取 | web-reader |

**Step 3：配置数据流转**

```
输入数据 → 步骤1(技能A) → 输出数据 → 步骤2(技能B) → ...
```

**Step 4：设定业务规则**
- 风险评分阈值多少触发人工审核？
- 哪些合同条款是红线？
- 发票匹配允许误差多少？

---

### 示例：紧急采购绿色通道

**目标**：紧急需求快速完成采购，保障业务连续性

**流程设计**：

```
1. 紧急需求标记 → 2. 简化比价（仅主流平台） → 3. 风险快筛 → 4. 合同直签 → 5. 先行付款
```

**配置说明**：

| 步骤 | 技能 | 关键逻辑 |
|------|------|----------|
| 1 | procurement-requirement-parser | 标记"紧急"标签 |
| 2 | ecommerce-procurement-research | 仅京东/天猫（发货快） |
| 3 | supplier-risk-assessor | 快速模式（工商+失信） |
| 4 | contract-generator | 简化模板 |
| 5 | invoice-matcher | 先付款后补票 |

**效果**：紧急需求采购周期从3天缩短到4小时

---

### 示例：供应商年度绩效评估

**目标**：年底评估供应商表现，决定续约

**流程设计**：

```
1. 采购记录拉取 → 2. 三单匹配数据 → 3. 合同履约情况 → 4. 风险复查 → 5. 综合评分
```

**配置说明**：

| 步骤 | 技能 | 关键逻辑 |
|------|------|----------|
| 1 | invoice-matcher | 汇总全年三单匹配率 |
| 2 | contract-audit | 合同履约纠纷记录 |
| 3 | supplier-risk-assessor | 年底风险复查 |
| 4 | 综合评分 | 履约率+风险+价格综合排名 |

---

## 五、典型行业方案

### 制造业

**痛点**：原材料采购批量大、供应商多、合同条款复杂

**推荐流程**：
```
需求解析(BOM) → 1688比价 → 供应商风控 → 合同审核(重条款) → 三单匹配 → 付款
```

**亮点**：
- BOM自动解析
- 批量采购价格谈判依据
- 合同条款严格审核
- 发票税率精确匹配

---

### 互联网/科技公司

**痛点**：采购品类多（设备/软件/外包）、需求分散、响应要快

**推荐流程**：
```
IM机器人(@询价) → 多平台比价 → 轻量风控 → 快速合同 → IM审批
```

**亮点**：
- 群聊@即可询价
- 4小时出比价报告
- 合同模板自动填充
- 移动端审批

---

### 贸易/零售

**痛点**：商品采购渠道多、假货风险、侵权隐患

**推荐流程**：
```
供应商准入(严) → 合同审核 → 知识产权巡检 → 定期复查
```

**亮点**：
- 供应商严格准入
- 合同条款防骗条款
- 品牌侵权定期巡检
- 1688/拼多多价格监控

---

## 六、业务指标监控

配置完流程后，建议监控以下指标：

| 流程 | 监控指标 | 目标值 |
|------|----------|--------|
| 采购履约 | 需求响应时间 | <4小时 |
| 采购履约 | 比价报告产出 | <1小时 |
| 供应商管理 | 风控覆盖率 | 100% |
| 供应商管理 | 新供应商准入周期 | <3天 |
| 合同管理 | 合同审核周期 | <2小时 |
| 合同管理 | 风险条款识别率 | >95% |
| 财务管理 | 三单匹配通过率 | >90% |
| 财务管理 | 付款周期 | <5天 |

---

## 七、常见问题

**Q1：如何对接现有ERP系统？**
> 通过API调用技能服务，输入JSON格式数据，获取结构化输出，支持SAP/用友/金蝶

**Q2：采购数据如何保证安全性？**
> 数据不上报第三方，全程本地化处理，仅返回结构化结果

**Q3：可以只启用部分流程吗？**
> 可以，按需选择单个技能或组合使用，支持模块化部署

**Q4：供应商风险评分准不准？**
> 评分基于公开数据源，建议作为参考，最终决策需人工复核

**Q5：合同审核能替代法务吗？**
> 不能替代，仅为辅助工具，高风险条款需法务人工确认

---

## 八、联系支持

如需定制化场景配置，请联系：
- 产品团队：设计专属采购流程
- 技术团队：API对接支持
- 运营团队：规则配置咨询

---

## 附录：技能目录

| # | 技能目录 | 职能 |
|---|----------|------|
| 1 | `skills/srm-ecommerce-procurement-research/` | 采购询价（多平台比价） |
| 2 | `skills/srm-procurement-requirement-parser/` | 需求解析（采购前） |
| 3 | `skills/srm-supplier-risk-assessor/` | 供应商风控（采购中） |
| 4 | `skills/srm-contract-generator/` | 合同生成（采购后） |
| 5 | `skills/srm-contract-audit/` | 合同审核（采购后） |
| 6 | `skills/srm-invoice-matcher/` | 三单匹配（采购后） |
| 7 | `skills/srm-talent-salary-researcher/` | 人才招聘（HR） |
| 8 | `skills/srm-competitor-monitor/` | 竞品监测（市场） |
| 9 | `skills/srm-ip-infringement-scanner/` | 侵权巡检（法务） |
| 10 | `skills/srm-im-bot-gateway/` | IM集成（基础设施） |
| 11 | `skills/srm-web-reader/` | 网页阅读（基础设施） |
| 12 | `skills/srm-asset-maintenance-tracker/` | 资产维保（IT） |

详细技能说明请参考 [docs/SKILLS.md](docs/SKILLS.md)

---

## 九、开发者指南

### 开发新技能

#### 1. 创建技能目录

```bash
mkdir -p skills/srm-{your-skill-name}
cd skills/srm-{your-skill-name}
```

#### 2. 必需文件

```
skills/srm-your-skill/
├── __init__.py          # 技能入口
├── {skill_name}.py      # 核心逻辑
└── SKILL.md             # 技能说明（AI智能体调用协议）
```

#### 3. SKILL.md 模板

```markdown
---
name: your-skill-name
description: Use when [触发条件描述]
---

# Your Skill Name

## Overview

[技能功能概述]

## When to Use

**触发条件：**
- [条件1]
- [条件2]

**不适用：**
- [不适用场景]

## Input / Output

| 输入 | 输出 |
|------|------|
| [输入描述] | [输出描述] |

## Example

```python
from skills.srm_your_skill import YourSkill

skill = YourSkill()
result = skill.execute({"key": "value"})
```
```

#### 4. Python 实现模板

```python
# skills/srm-your-skill/__init__.py
from .your_skill import YourSkill

__all__ = ["YourSkill"]
```

```python
# skills/srm-your-skill/your_skill.py

class YourSkill:
    """技能功能描述"""
    
    name = "your-skill-name"
    description = "Use when..."
    
    def __init__(self):
        # 初始化配置
        pass
    
    def can_handle(self, intent: str) -> bool:
        """判断是否可以处理该意图"""
        keywords = ["关键词1", "关键词2"]
        return any(kw in intent for kw in keywords)
    
    def execute(self, input_data: dict) -> dict:
        """执行技能逻辑"""
        # 验证输入
        self._validate_input(input_data)
        
        # 执行业务逻辑
        result = self._process(input_data)
        
        # 返回结果
        return {
            "status": "success",
            "data": result,
            "message": "处理完成"
        }
    
    def _validate_input(self, input_data: dict):
        """验证输入数据"""
        required_fields = ["field1", "field2"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"缺少必需字段: {field}")
    
    def _process(self, input_data: dict) -> dict:
        """核心业务逻辑"""
        pass
```

### 测试技能

```python
# tests/test_your_skill.py
import pytest
from skills.srm_your_skill import YourSkill

def test_your_skill():
    skill = YourSkill()
    
    # 测试 can_handle
    assert skill.can_handle("关键词1") == True
    assert skill.can_handle("无关内容") == False
    
    # 测试 execute
    result = skill.execute({"field1": "value1", "field2": "value2"})
    assert result["status"] == "success"
```

---

## 十、贡献指南

### 提交 Issue

- 使用清晰的标题描述问题
- 提供复现步骤
- 附上错误日志和截图
- 标明环境和版本信息

### 提交 Pull Request

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 编写文档字符串
- 添加单元测试

---

## 十一、路线图

### 近期计划 (v1.x)
- [ ] 完善现有技能的错误处理和边界情况
- [ ] 添加更多单元测试和集成测试
- [ ] 优化数据抓取性能和稳定性
- [ ] 完善文档和示例代码

### 中期计划 (v2.0)
- [ ] 引入工作流引擎，支持复杂流程编排
- [ ] 添加Web管理界面
- [ ] 支持更多企业IM平台（Slack、Teams）
- [ ] 引入向量数据库，支持RAG增强

### 长期愿景
- [ ] 构建技能市场，支持第三方技能插件
- [ ] 多智能体协作框架
- [ ] 支持私有化部署和混合云架构

---

## 十二、许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 十三、致谢

感谢以下开源项目和技术：
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Jina AI](https://jina.ai/) - 网页内容提取
- [OpenAI](https://openai.com/) - 大语言模型
- [智谱AI](https://www.zhipuai.cn/) - 国产大模型

---

*持续更新中... 最后更新时间：2025年3月*

---

## 十一、开发者指南

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行测试
pytest

# 查看覆盖率
pytest --cov

# 生成 HTML 报告
pytest --cov --cov-report=html
open htmlcov/index.html
```
