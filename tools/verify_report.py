#!/usr/bin/env python3
"""
报告发布前的机械核查（审查流程第 1 层）

用法:
    python3 tools/verify_report.py sol 202608

它抓的是**机器能确定的错误**，不判断推理好坏——那是 _bian 的活。
重点是第 1 项：图表里显示的数字如果在正文里找不到，几乎一定是编的。
（2026-09 SOL 首期就发生过：图表里的「2025 月均 28 亿笔」没有任何来源，
  靠人工渲染检查才偶然发现。这个检查把它变成必然发现。）

退出码 0 = 全过；1 = 有 FAIL。
"""
import sys, os, re, json

C_OK, C_WARN, C_FAIL, C_DIM, C_END = '\033[32m', '\033[33m', '\033[31m', '\033[2m', '\033[0m'

# 传统金融机构关键词——用于检查是否配平了加密原生来源的看多偏向
TRADFI = ['Deutsche Bank', 'Citi', 'JPMorgan', 'Goldman', 'Morgan Stanley',
          'Standard Chartered', 'Bernstein', 'BlackRock', '21Shares', 'Fidelity',
          'VanEck', 'Bloomberg', '美联储', 'CME', 'BIS', 'IMF']

NUM = re.compile(r'-?\d[\d,]*\.?\d*')


def norm_nums(text):
    """抽取并归一化数字（去逗号、去尾零）"""
    out = set()
    for m in NUM.findall(text):
        t = m.replace(',', '').lstrip('-')
        if not t or t == '.':
            continue
        try:
            v = float(t)
        except ValueError:
            continue
        if v == 0:
            continue
        out.add(round(v, 4))
    return out


class Report:
    def __init__(self, asset, ym):
        self.asset, self.ym = asset, ym
        base = os.path.join(asset, 'professional')
        self.base = base
        self.md_path = os.path.join(base, f'{asset}_research_report_{ym}.md')
        self.sm_path = os.path.join(base, f'{asset}_questions_summary_{ym}.md')
        self.sc_path = os.path.join(base, 'thesis_scorecard.md')
        self.charts_dir = os.path.join(base, 'charts')
        self.fails, self.warns = [], []

    def read(self, p):
        return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

    def fail(self, tag, msg):
        self.fails.append((tag, msg))

    def warn(self, tag, msg):
        self.warns.append((tag, msg))

    # ── 1. 图表数字溯源（最重要）────────────────────────────
    def check_chart_numbers(self):
        md = self.read(self.md_path) + self.read(self.sm_path)
        md_nums = norm_nums(md)
        if not os.path.isdir(self.charts_dir):
            self.warn('图表', '无 charts 目录')
            return
        svgs = [f for f in os.listdir(self.charts_dir)
                if f.endswith('.svg') and self.ym in f]
        if not svgs:
            self.warn('图表', f'没有 {self.ym} 的图表文件')
            return
        for fn in sorted(svgs):
            svg = self.read(os.path.join(self.charts_dir, fn))
            # 只取 <text> 里真正显示给读者的内容，忽略坐标
            shown = ' '.join(re.findall(r'<text[^>]*>(.*?)</text>', svg, re.S))
            shown = re.sub(r'<[^>]+>', ' ', shown)
            orphans = sorted(n for n in norm_nums(shown) if n not in md_nums)
            # 年份与百分号刻度是常见的合法孤儿，单独放行
            orphans = [n for n in orphans
                       if not (1900 <= n <= 2100) and n not in (10, 20, 30, 40, 50, 100, 150, 200, 250, 300, 400, 500)]
            if orphans:
                self.fail('图表溯源',
                          f'{fn} 显示了正文中没有的数字: {orphans} '
                          f'← 每个都要能在正文找到，否则就是编的')

    # ── 2. 来源核实状态表 ──────────────────────────────────
    def check_source_table(self):
        md = self.read(self.md_path)
        if '核实状态' not in md:
            self.fail('来源', '附录缺少「数据来源与核实状态」表')
            return
        tail = md[md.find('核实状态'):]
        marks = {'✅': tail.count('✅'), '⚠️': tail.count('⚠️'), '❌': tail.count('❌')}
        if sum(marks.values()) < 3:
            self.fail('来源', f'核实状态标记过少 {marks}，看不出哪些是一手、哪些没核实')
        elif marks['✅'] == 0:
            self.warn('来源', '没有任何一条标为「已直接抓取」——本期完全依赖搜索摘要')

    # ── 3. 空方 / 非加密原生来源 ───────────────────────────
    def check_bear_sources(self):
        md = self.read(self.md_path)
        hits = [k for k in TRADFI if k in md]
        if not hits:
            self.fail('来源偏向',
                      '全文未引用任何传统金融机构。加密原生媒体结构上看多，必须配平')
        elif len(hits) < 2:
            self.warn('来源偏向', f'仅引用 {hits}，配平力度偏弱')

    # ── 4. 价格区间必须有推导方法 ──────────────────────────
    def check_derivation(self):
        md = self.read(self.md_path)
        has_range = re.search(r'\$\s?\d[\d,]*\s*[–\-—]\s*\$?\s?\d', md)
        if has_range and not re.search(r'推导|推演方法|怎么推出来', md):
            self.fail('方法论',
                      '给了价格区间却没有推导说明——精确数字若无方法论，就是给主观判断打包装')
        if has_range and not re.search(r'弱点|局限|不确定', md):
            self.warn('方法论', '有价格区间但未声明方法的弱点')

    # ── 5. 记分卡本期登记 ──────────────────────────────────
    def check_scorecard(self):
        sc = self.read(self.sc_path)
        if not sc:
            self.fail('记分卡', f'缺少 {self.sc_path}')
            return
        y, m = self.ym[:4], self.ym[4:].lstrip('0')
        if f'{y}-{self.ym[4:]}' not in sc and f'{y} 年 {m} 月' not in sc:
            self.fail('记分卡', f'未登记 {y}-{self.ym[4:]} 期的论点')
        if '检验条件' not in sc:
            self.fail('记分卡', '论点缺少可证伪的检验条件，不予登记')

    # ── 6. 数据新鲜度 ─────────────────────────────────────
    def check_freshness(self):
        md = self.read(self.md_path)
        y = int(self.ym[:4])
        old = sorted({int(x) for x in re.findall(r'(20\d\d)\s*年', md) if int(x) < y - 1})
        if old and len(old) > 6:
            self.warn('新鲜度', f'引用了较多早于 {y-1} 年的年份 {old[:8]}…（历史章节属正常）')

    # ── 7. 数字清单（供人工抽查）────────────────────────────
    def number_inventory(self):
        md = self.read(self.md_path)
        big = sorted({n for n in norm_nums(md) if n > 1000}, reverse=True)[:12]
        pct = sorted({n for n in norm_nums(md) if 0 < n < 100})[:0]  # 占位，不输出
        return big

    def run(self):
        for fn in (self.check_chart_numbers, self.check_source_table,
                   self.check_bear_sources, self.check_derivation,
                   self.check_scorecard, self.check_freshness):
            fn()
        return self.fails, self.warns


def main():
    if len(sys.argv) < 3:
        sys.exit('用法: python3 tools/verify_report.py <asset> <YYYYMM>')
    asset, ym = sys.argv[1].lower(), sys.argv[2]
    r = Report(asset, ym)
    if not os.path.exists(r.md_path):
        sys.exit(f'找不到报告: {r.md_path}')

    print(f'\n核查 {asset.upper()} {ym[:4]}-{ym[4:]}  （第 1 层：机械核查）')
    print('─' * 62)
    fails, warns = r.run()

    for tag, msg in fails:
        print(f'{C_FAIL}FAIL{C_END}  [{tag}] {msg}')
    for tag, msg in warns:
        print(f'{C_WARN}WARN{C_END}  [{tag}] {msg}')
    if not fails and not warns:
        print(f'{C_OK}全部通过{C_END}')

    big = r.number_inventory()
    print(f'\n{C_DIM}供人工抽查的大数（前 12）：{big}{C_END}')
    print('─' * 62)
    print(f'结果：{len(fails)} FAIL / {len(warns)} WARN')
    if fails:
        print(f'{C_FAIL}→ 有 FAIL，不得发布{C_END}\n')
        sys.exit(1)
    print(f'{C_OK}→ 第 1 层通过，可进入第 2 层（_bian 审推理）{C_END}\n')


if __name__ == '__main__':
    main()
