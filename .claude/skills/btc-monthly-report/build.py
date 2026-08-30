#!/usr/bin/env python3
"""
BTC 月度报告构建器 —— Markdown → HTML（→ PDF 由调用方用 Chrome 渲染）

用法:
    python3 .claude/skills/btc-monthly-report/build.py 202608

会读取 professional/btc_research_report_<YYYYMM>.md
       professional/btc_questions_summary_<YYYYMM>.md
输出   professional/btc_research_report_<YYYYMM>.html

导航 ID 全自动探测，无需手工映射（消除拼音 slug 坑）。
"""
import sys, os, re, html as _html

try:
    import markdown
except ImportError:
    sys.exit("缺少依赖: pip3 install markdown")

EXT = ['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br']


def build_nav(md_html):
    """从生成的 HTML 里自动抽取 h2 的 id 和文本，构造导航项。"""
    items = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', md_html, re.S):
        hid = m.group(1)
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        # 标签精简: 砍掉冒号/括号后的补充说明，保留主干
        label = re.split(r'[：（(]', text)[0].strip()
        if len(label) > 22:
            label = label[:21] + '…'
        items.append((label, hid))
    return items


def nav_html(items):
    return "\n".join(
        f'<a href="#{h}">{_html.escape(l)}</a>' for l, h in items
    )


CSS = """
:root{--accent:#f7931a;--blue:#2563eb;--bg:#fafaf9;--card:#fff;--text:#1c1917;--text2:#57534e;--border:#e7e5e4;--callout-bg:#fffbeb;--callout-bdr:#f59e0b;--code-bg:#f5f5f4;--sidebar-w:260px;--touch:44px}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;scroll-padding-top:20px}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Helvetica Neue",Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.78;font-size:15px;padding-top:52px}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}strong{font-weight:700;color:#1c1917}hr{border:none;border-top:1px solid var(--border);margin:2rem 0}
.topbar{position:fixed;top:0;left:0;right:0;z-index:300;height:52px;background:#1c1917;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border-bottom:2px solid var(--accent)}
.topbar .brand{font-weight:700;font-size:1rem;color:var(--accent);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.topbar button{background:none;border:1px solid #44403c;color:#fff;font-size:1.25rem;width:var(--touch);height:var(--touch);border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent}
.topbar button:active{background:#44403c}.scroll-progress{position:absolute;bottom:-2px;left:0;height:3px;background:var(--accent);width:0%}
.sidebar{position:fixed;top:0;left:0;z-index:250;width:var(--sidebar-w);max-width:85vw;height:100vh;background:#1c1917;color:#d6d3d1;overflow-y:auto;padding:64px 14px 24px 16px;font-size:.82rem;border-right:2px solid var(--accent);transform:translateX(-100%);transition:transform .25s ease}
.sidebar.open{transform:translateX(0)}.sidebar h2{color:var(--accent);font-size:1rem;margin-bottom:.9rem;padding-bottom:.5rem;border-bottom:1px solid #44403c;letter-spacing:.5px}
.sidebar a{color:#a8a29e;display:flex;align-items:center;min-height:var(--touch);padding:.3rem 0;line-height:1.45}
.sidebar a:hover,.sidebar a:focus{color:#fff;outline:none}.sidebar a.active{color:var(--accent);font-weight:600}
.sidebar .nav-section{color:#78716c;font-size:.68rem;text-transform:uppercase;letter-spacing:1.2px;margin:1.1rem 0 .3rem;font-weight:700}
.sidebar .divider{border:none;border-top:1px solid #44403c;margin:.9rem 0}.sidebar-footer{font-size:.65rem;color:#78716c;margin-top:1rem;line-height:1.6}
.overlay{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.5)}.overlay.show{display:block}
.main{padding:0}.hero{background:linear-gradient(135deg,#1c1917 0%,#292524 50%,#1c1917 100%);color:#fff;padding:32px 18px;border-bottom:3px solid var(--accent)}
.hero h1{font-size:clamp(1.3rem,5vw,2rem);font-weight:800;margin-bottom:.6rem;letter-spacing:-.5px;border:none;padding:0}
.hero .subtitle{color:#d6d3d1;font-size:clamp(.8rem,2.5vw,.95rem);line-height:1.6}.hero .badges{margin-top:.8rem;display:flex;gap:8px;flex-wrap:wrap}
.badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:.7rem;font-weight:600}
.badge-btc{background:var(--accent);color:#1c1917}.badge-date{background:#44403c;color:#d6d3d1}.badge-warn{background:#7f1d1d;color:#fca5a5}
.content{padding:28px 18px 60px}h1{font-size:1.6rem;font-weight:800;margin:2rem 0 .8rem;padding-bottom:.5rem;border-bottom:2px solid var(--border);letter-spacing:-.3px}
h2{font-size:1.3rem;font-weight:700;margin:1.8rem 0 .7rem;color:#292524}h3{font-size:1.08rem;font-weight:700;margin:1.4rem 0 .5rem;color:#44403c}h4{font-size:.95rem;font-weight:700;margin:1rem 0 .4rem;color:#57534e}p{margin:.5rem 0}
blockquote{background:var(--callout-bg);border-left:4px solid var(--callout-bdr);margin:.8rem 0;padding:10px 16px;border-radius:0 6px 6px 0;color:#78716c;font-size:.92em}blockquote p{margin:.2rem 0}
.tbl{width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;margin:1rem 0;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
table{width:100%;min-width:520px;border-collapse:collapse;font-size:.85rem;background:var(--card)}thead{background:#292524;color:#fff}
thead th{padding:10px 12px;text-align:left;font-weight:700;font-size:.78rem;text-transform:uppercase;letter-spacing:.3px;white-space:nowrap}
tbody td{padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:top}tbody tr:last-child td{border-bottom:none}tbody tr:nth-child(even){background:#fafaf9}tbody tr:hover{background:#fff7ed}
code{background:var(--code-bg);padding:2px 6px;border-radius:4px;font-family:"SF Mono","Fira Code",Menlo,Consolas,monospace;font-size:.85em;color:#d97706;word-break:break-word}
pre{background:#1c1917;color:#e7e5e4;padding:14px 16px;border-radius:8px;overflow-x:auto;margin:.8rem 0;font-size:.8rem;line-height:1.6}pre code{background:none;color:inherit;padding:0}
.section-divider{margin:3rem 0 2rem;border-top:3px solid var(--accent)}.content .hero{border-radius:10px;padding:28px 22px}
@media(min-width:1024px){body{padding-top:0}.topbar{display:none}.overlay{display:none!important}.sidebar{transform:translateX(0);padding-top:24px;z-index:100}.main{margin-left:var(--sidebar-w)}.hero{padding:44px clamp(40px,5vw,90px)}.content{padding:40px clamp(40px,5vw,90px) 90px;max-width:1400px}body{font-size:16px}h1{font-size:1.85rem}h2{font-size:1.4rem}h3{font-size:1.15rem}}
@media print{.topbar,.sidebar,.overlay{display:none!important}body{padding-top:0;font-size:11px}.main{margin:0}.content{padding:0;max-width:100%}.hero{background:#fff!important;color:#000!important;border-bottom:2px solid #000;padding:1.5rem}.tbl{box-shadow:none}table{min-width:auto;border:1px solid #ccc;font-size:10px}@page{margin:1.5cm}}
"""

JS = """(function(){var s=document.getElementById('sidebar'),o=document.getElementById('overlay'),m=document.getElementById('menuBtn'),l=s.querySelectorAll('a'),p=document.getElementById('scrollProgress');
var d=function(){return window.matchMedia('(min-width:1024px)').matches};
function op(){s.classList.add('open');o.classList.add('show');m.textContent='\\u2715'}
function cl(){s.classList.remove('open');o.classList.remove('show');m.textContent='\\u2630'}
m.addEventListener('click',function(){s.classList.contains('open')?cl():op()});
o.addEventListener('click',cl);
l.forEach(function(a){a.addEventListener('click',function(){if(!d())cl()})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!d())cl()});
var ob=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){l.forEach(function(a){a.classList.remove('active')});var t=s.querySelector('a[href="#'+e.target.id+'"]');if(t)t.classList.add('active')}})},{rootMargin:'-10% 0px -75% 0px'});
document.querySelectorAll('h2[id],h3[id]').forEach(function(el){ob.observe(el)});
window.addEventListener('scroll',function(){var h=document.documentElement.scrollHeight-document.documentElement.clientHeight;if(h>0&&p)p.style.width=(window.scrollY/h*100)+'%'})})()"""


def main():
    if len(sys.argv) < 2 or not re.fullmatch(r'\d{6}', sys.argv[1]):
        sys.exit("用法: python3 build.py <YYYYMM>   例: python3 build.py 202608")
    ym = sys.argv[1]
    year, month = ym[:4], ym[4:].lstrip('0')

    base = 'professional'
    rp_md = os.path.join(base, f'btc_research_report_{ym}.md')
    sm_md = os.path.join(base, f'btc_questions_summary_{ym}.md')
    out = os.path.join(base, f'btc_research_report_{ym}.html')

    for p in (rp_md, sm_md):
        if not os.path.exists(p):
            sys.exit(f"找不到: {p}")

    def render(path, id_prefix=''):
        with open(path, encoding='utf-8') as f:
            h = markdown.markdown(f.read(), extensions=EXT)
        # 表格包滚动容器（防止宽表在窄屏撑破版面）
        h = h.replace('<table>', '<div class="tbl"><table>').replace('</table>', '</table></div>')
        # 两份 md 各自编号，合成一页会撞 id（如两个 #_1）——给总结加前缀隔离
        if id_prefix:
            h = re.sub(r'(<h[1-6] id=")([^"]+)(")', lambda m: m.group(1) + id_prefix + m.group(2) + m.group(3), h)
        return h

    rp, sm = render(rp_md), render(sm_md, id_prefix='s-')
    rnav, snav = build_nav(rp), build_nav(sm)

    doc = f'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BTC / Bitcoin 完整调研与分析报告 — {year}年{month}月</title>
<style>{CSS}</style></head><body>
<div class="topbar"><span class="brand">₿ BTC 调研报告 ({year}.{month})</span><button id="menuBtn" aria-label="菜单">☰</button><div class="scroll-progress" id="scrollProgress"></div></div>
<div class="overlay" id="overlay"></div>
<nav class="sidebar" id="sidebar"><h2>₿ BTC 调研报告 {year}.{month}</h2>
<div class="nav-section">完整报告</div><a href="#hero">首页概览</a>
{nav_html(rnav)}
<hr class="divider"><div class="nav-section">简明总结</div>
{nav_html(snav)}
<hr class="divider"><div class="sidebar-footer">数据截止：{year} 年 {month} 月<br><span style="color:#dc2626;">⚠ 不构成投资建议</span></div></nav>
<main class="main">
<div class="hero" id="hero"><h1>₿ BTC / Bitcoin<br>完整调研与分析报告</h1>
<div class="subtitle">金融资产 · 技术网络 · 货币实验 · 宏观资产 · 行业生态<br>基于 Claude for Financial Services 框架的系统性多角度分析</div>
<div class="badges"><span class="badge badge-btc">₿ Bitcoin</span><span class="badge badge-date">{year} 年 {month} 月</span><span class="badge badge-warn">⚠ 不构成投资建议</span></div></div>
<div class="content"><div id="full-report">{rp}</div>
<hr class="section-divider">
<div id="summary"><div class="hero"><h1>\U0001F4CB 核心问题与简明总结</h1><div class="subtitle">配套完整报告使用 · 快速复习与核心结论速查</div></div>{sm}</div>
<hr style="margin-top:3rem"><blockquote><p><strong>最后提醒</strong>：本报告尽力呈现多角度分析，不做投资建议。加密资产投资风险极高，请基于独立研究和自身风险承受能力做出决策。如有疑问，请咨询持牌金融顾问。</p></blockquote>
<p style="text-align:center;color:var(--text2);font-size:.8rem;margin-top:2rem">Generated with Claude for Financial Services</p></div>
</main>
<script>{JS}</script>
</body></html>'''

    with open(out, 'w', encoding='utf-8') as f:
        f.write(doc)

    # 自检：导航链接必须全部命中真实锚点
    hrefs = [h for h in re.findall(r'href="#([^"]+)"', doc) if 'target.id' not in h]
    ids = set(re.findall(r'id="([^"]+)"', doc))
    missing = [h for h in hrefs if h not in ids]
    all_ids = re.findall(r'<h[1-6] id="([^"]+)"', doc)
    dupes = sorted({i for i in all_ids if all_ids.count(i) > 1})

    print(f"✅ {out}  ({len(doc):,} bytes)")
    print(f"   导航 {len(hrefs)} 条 | 锚点校验: {'全部命中' if not missing else '❌ 失效 ' + str(missing)}")
    print(f"   表格滚动容器 {doc.count('class=\"tbl\"')} 个")
    print(f"   重复锚点: {'无' if not dupes else '❌ ' + str(dupes)}")
    if missing or dupes:
        sys.exit(1)
    print(f"\n下一步生成 PDF：")
    print(f'   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \\')
    print(f'     --no-pdf-header-footer --print-to-pdf-no-header \\')
    print(f'     --print-to-pdf="{base}/btc_research_report_{ym}.pdf" \\')
    print(f'     "file://$(pwd)/{out}"')


if __name__ == '__main__':
    main()
