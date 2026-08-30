---
name: btc-monthly-report
description: 生成或更新 BTC 月度专业调研报告（Markdown + HTML + PDF）。当 _dalin 说"生成 X 月版报告""更新 BTC 报告""出一份新的比特币调研""按上次那套做一份"时使用。也用于修改已有月份的报告后重新出 HTML/PDF。
---

# BTC 月度专业调研报告

产出一套四件产物，放在 `professional/`：

| 文件 | 说明 |
|------|------|
| `btc_research_report_<YYYYMM>.md` | 完整报告，11 章 |
| `btc_questions_summary_<YYYYMM>.md` | 简明速查，10-11 节 |
| `btc_research_report_<YYYYMM>.html` | 网页版（脚本生成，勿手写） |
| `btc_research_report_<YYYYMM>.pdf` | PDF（Chrome 无头渲染） |

通俗版是**另一条线**，放 `general/`，不在本技能范围（且被 gitignore 排除）。

---

## 第 1 步：抓数据

用 WebSearch 覆盖这 7 类。**不要凭记忆写数字**——每个月都变，写错就是硬伤。

1. **价格与市场**：现价、距 ATH 回撤、市值、关键支撑阻力、恐惧贪婪指数
2. **ETF 资金流**：当月净流入/出、YTD 累计、总 AUM、IBIT / FBTC 分项
3. **宏观**：美联储主席立场与利率路径、CPI / PCE、10 年美债、DXY、油价、黄金、标普
4. **链上**：MVRV、MVRV Z-Score、STH-MVRV、SOPR、LTH-SOPR、已实现价格、LTH 已实现价格、交易所余额、Puell Multiple
5. **上市公司储备**：总持仓、Strategy / Metaplanet / MARA 等头部动向、**有没有人在卖**、mNAV
6. **监管**：CLARITY 法案进度与通过概率、SBR / ARMA、各国政策
7. **AI 相关**：矿工转 AI/HPC、AI Agent 支付（x402 / L402 / 闪电网络）、量子威胁、AI 诈骗

搜索时把年月写进 query（如 `Bitcoin ETF flows August 2026`），否则容易搜到旧数据。

## 第 2 步：写完整报告（11 章）

框架固定，逐月只换数据和判断：

| 章 | 内容 | 逐月要更新什么 |
|---|------|--------------|
| 0 | 核心结论摘要（一页速览表） | 全部 |
| 1 | 起源与历史背景 | 基本不动 |
| 2 | 发展阶段划分（五阶段） | 只在阶段五追加当月大事 |
| 3 | 当前现状（资产属性 / 市场结构 / 链上 / 宏观 / 技术生态） | **全部重写** |
| 4 | 上市公司比特币储备 | **全部重写** |
| 5 | AI 科技的多维影响 | 更新进展 |
| 6 | 核心价值逻辑（多头 ★ 评分 / 空头 ★ 评分） | 调整强度评级 |
| 7 | 与其他资产比较（黄金 / 美股 / 美债 / ETH） | 更新表现数据 |
| 8 | 未来 1–5 年关键变量（催化剂日历） | **全部重写** |
| 9 | 三种情景推演 + 主观概率 | 调整概率并说明理由 |
| 10 | 投资与风险启示 | 更新周期判断 |
| 11 | 附录（阶段速查 / 减半对比 / 储备速查 / AI 速查 / 数据来源） | 更新数据行 |

写作要求（_dalin 的明确偏好）：

- **中文**。专有名词保留英文原文但要解释它是什么
- **不写成宣传文**。多空都要给，不确定的地方明说"未验证"
- **重点不是预测价格**，是理解历史、现状、逻辑、可能性
- 表格优先于长段落
- 报告开头的引用块里写明「本版更新要点」——列出相比上一版变了什么
- 情景概率变动要说明原因（如"悲观概率上调，因 Strategy 开始抛售"）

## 第 3 步：写简明总结

10-11 节，是完整报告的浓缩，给快速复习用。固定以「如果你只有 3 分钟，记住这 5 句话」收尾。

末尾注明配套文件：``> 详细论证请阅读 `btc_research_report_<YYYYMM>.md`。``

## 第 4 步：构建 HTML + PDF

**不要手写 HTML**，用脚本：

```bash
python3 .claude/skills/btc-monthly-report/build.py <YYYYMM>
```

脚本会自检并打印导航条数、锚点是否全部命中、表格容器数、有无重复锚点。**校验不过会退出非零**。

然后按脚本末尾打印的命令生成 PDF（Chrome 无头模式，会自动套用 `@media print` 样式隐藏侧边栏）。

## 第 5 步：提交

```bash
git add professional/ && git commit && git push
```

---

## 三个坑（已在脚本里根治，别自己绕回去）

### ① 中文标题的锚点是拼音 slug
Python markdown 把「4. 上市公司比特币储备」转成 `id="4-7"`、「5. AI 科技对 BTC 的多维影响」转成 `id="5-ai-btc"`。**凭空猜必然点不动导航。** 脚本改为从生成的 HTML 里自动抽取 h2 的真实 id，不再手工映射。

### ② 两份 Markdown 合并会撞锚点
完整报告和简明总结各自编号，都可能生成 `id="_1"`。合成一页后点第二个会跳到第一个。脚本给总结的所有标题 id 加 `s-` 前缀隔离，并在自检里检测重复。

### ③ 布局两件事
- **桌面端正文不能设窄的固定 max-width**。曾经设 900px，结果窗口拉大后右侧一大片空白。现用 `padding: clamp(40px,5vw,90px)` 流式铺满，只在超宽屏（>1660px）用 1400px 兜底
- **表格必须包 `.tbl` 滚动容器**。专业版表格设了 `min-width:520px`（5-7 列对比矩阵），不包容器在手机上会撑破版面

---

## 数据来源清单

链上 Glassnode / CryptoQuant · ETF 流量 Farside / CoinGlass / The Block · 上市公司储备 BitcoinTreasuries.com / CoinGlass · 宏观 CME FedWatch / 美联储 · 机构研究 Fidelity / Bernstein / CryptoQuant

## 分析框架来源

报告骨架来自 `anthropics/financial-services` 插件的四个 Skill，装在中央缓存（不在本项目内）：

- `market-researcher:sector-overview` — 行业全景、市场结构
- `equity-research:thesis-tracker` — 多空逻辑评分卡
- `equity-research:catalyst-calendar` — 催化剂日历
- `financial-analysis:competitive-analysis` — 资产横向对比矩阵

启用配置在 `.claude/settings.json`。新机器恢复：`claude plugin marketplace add anthropics/financial-services`
