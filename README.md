# longBTC

BTC / Bitcoin 调研报告库。按月出具，分**专业版**和**通俗版**两条线。

> ⚠️ 本仓库所有内容仅供研究参考，**不构成任何投资建议**。

---

## 目录结构

```
professional/                  专业版（面向分析师 / 从业者）
  btc_research_report_YYYYMM.md      完整报告，11 章
  btc_research_report_YYYYMM.html    网页版（侧边导航 + 移动适配）
  btc_research_report_YYYYMM.pdf     PDF
  btc_questions_summary_YYYYMM.md    简明速查

general/                       通俗版（面向普通人，本仓库不收录）
  btc_for_everyone_YYYYMM.*

.claude/skills/btc-monthly-report/   月度报告生成技能
```

文件一律带 `YYYYMM` 后缀。通俗版目录被 `.gitignore` 排除，仅存本地。

## 已有版本

| 版本 | 专业版 | 通俗版 | 当期核心判断 |
|------|:---:|:---:|------|
| 2026-06 | ✅ | ✅ | Warsh 就任、市场定价零降息；首次纳入上市公司储备与 AI 两章 |
| 2026-07 | ✅ | — | ETF 创史上最大单月流出 $45 亿；Strategy 单日抛售 $2.16 亿，最大买方转为卖方 |

## 两个版本的区别

|  | 专业版 | 通俗版 |
|---|---|---|
| 读者 | 分析师、从业者 | 无金融背景的普通人 |
| 语言 | 术语、链上指标、MVRV / SOPR | 说人话，三个比喻讲清楚 |
| 结构 | 11 章 + 速查 | 10 节 |
| 回答的问题 | 多角度分析、情景推演 | 我该买吗？怎么买？注意什么？ |
| 篇幅 | ~25 页 | ~9 页 |

## 生成新一期

```bash
# 交给 Claude Code，它会按 .claude/skills/btc-monthly-report/ 的流程走
生成 2026 年 8 月版报告
```

只做 HTML/PDF 重建（Markdown 已改好时）：

```bash
python3 .claude/skills/btc-monthly-report/build.py 202608
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
