# crypto-research

加密资产研究报告库。按月出具，每个资产分**专业版**和**通俗版**两条线。

> ⚠️ 本仓库所有内容仅供研究参考，**不构成任何投资建议**。

> 📌 本仓库原名 `longBTC`，2026-09 起扩展为多资产研究，改名为 `crypto-research`。
> 旧链接由 GitHub 自动重定向（实测返回 301），无需修改。

---

## 目录结构

```
btc/                            比特币
  professional/                 专业版（面向分析师 / 从业者）
    btc_research_report_YYYYMM.md      完整报告，11 章
    btc_research_report_YYYYMM.html    网页版（侧边导航 + 移动适配）
    btc_research_report_YYYYMM.pdf     PDF
    btc_questions_summary_YYYYMM.md    简明速查
    charts/*-YYYYMM.svg                图表
    thesis_scorecard.md                跨期论点记分卡（不带月份，持续追加）
  general/                      通俗版（面向普通人，不进仓库）

sol/                            Solana
  professional/                 结构同 btc/，但章节框架有约四成差异

.claude/skills/                 报告生成技能（随仓库版本化，不放全局）
```

文件一律带 `YYYYMM` 后缀。各资产的 `general/` 目录被 `.gitignore` 排除，仅存本地。

## 已有版本

### BTC

| 版本 | 专业版 | 通俗版 | 当期核心判断 |
|------|:---:|:---:|------|
| 2026-06 | ✅ | ✅ | Warsh 就任、市场定价零降息；首次纳入上市公司储备与 AI 两章 |
| 2026-07 | ✅ | — | ETF 创史上最大单月流出 $45 亿；Strategy 单日抛售 $2.16 亿，最大买方转为卖方 |
| 2026-08 | ✅ | — | BTC +25.1% 收 $78,548；ETF 单月流入 $35.2 亿创年内最佳；7 月偏空判断被证伪。新增图表、情景推导方法、机构空方观点、滚动记分卡 |

### SOL

| 版本 | 专业版 | 通俗版 | 当期核心判断 |
|------|:---:|:---:|------|
| 2026-08 | ✅ | — | 首期。核心矛盾是**收入崩塌 87% 但用量创新高**（8 月 52 亿笔交易）；「Solana 老宕机」论据已过时（30 个月零中断）；首次全网治理投票 SIMD-0550 以 67% 惊险通过、SIMD-0553 被否 |

**框架差异**：相对 BTC 版改动约四成。减半周期、算力/矿工不适用，替换为通胀销毁机制、质押与验证者经济；新增网络稳定性、生态数据、治理投票、L1 竞争。**最根本的是估值锚不同**——BTC 靠稀缺性，SOL 是生产性资产、应看网络收入。

## 两个版本的区别

|  | 专业版 | 通俗版 |
|---|---|---|
| 读者 | 分析师、从业者 | 无金融背景的普通人 |
| 语言 | 术语、链上指标、MVRV / SOPR | 说人话，三个比喻讲清楚 |
| 结构 | 11 章 + 速查 | 10 节 |
| 回答的问题 | 多角度分析、情景推演 | 我该买吗？怎么买？注意什么？ |
| 篇幅 | ~25 页 | ~9 页 |

## 论点记分卡

每个资产各有一份记分卡（`btc/professional/thesis_scorecard.md`、`sol/professional/thesis_scorecard.md`），记录历次判断的对错。**截至 2026-08，已检验的 8 个论点里只说对 1 个（13%）**，
主要失误模式是把「结构性脆弱」误判为「即将断裂」。

这个数字公开挂着是有意的——一份不检查自己历史准确率的研究报告，价值要打很大折扣。

## 生成新一期

```bash
# 交给 Claude Code，它会按 .claude/skills/ 里的流程走
生成 2026 年 9 月版 BTC 报告
```

只做 HTML/PDF 重建（Markdown 已改好时）：

```bash
python3 .claude/skills/btc-monthly-report/build.py 202609              # BTC
python3 .claude/skills/btc-monthly-report/build.py 202609 --asset sol  # SOL
# 脚本会打印 PDF 生成命令，复制执行即可
```

脚本自带校验：导航锚点必须全部命中、不得有重复锚点，否则退出非零。

## 换机器后恢复

报告框架依赖 Anthropic 官方的金融服务插件，装在中央缓存（不在本仓库内）：

```bash
claude plugin marketplace add anthropics/financial-services
claude plugin install financial-analysis@claude-for-financial-services --scope project
claude plugin install equity-research@claude-for-financial-services --scope project
claude plugin install market-researcher@claude-for-financial-services --scope project
```

启用清单见 `.claude/settings.json`。用到的四个分析框架：

- `market-researcher:sector-overview` — 行业全景
- `equity-research:thesis-tracker` — 多空逻辑评分卡
- `equity-research:catalyst-calendar` — 催化剂日历
- `financial-analysis:competitive-analysis` — 资产横向对比

另需 Python `markdown` 库和 Google Chrome（PDF 渲染）。

## 免责声明

本仓库内容为研究性质的分析记录，不构成投资、法律、税务或会计建议。加密资产风险极高，请基于独立研究和自身风险承受能力做出决策。
