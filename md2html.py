# -*- coding: utf-8 -*-
"""Convert ALL insight-report markdown files in the workspace into standalone,
styled HTML files with embedded images, plus a grouped index page."""
import base64
import html as html_mod
import os
import re

import markdown

BASE = r"D:\中长期技术"
FILES = [
    # (md_name, group, tag, description)
    ("洞察报告_Token经济总纲_业务背景趋势与智能体技术要求推导.md", "Token经济系列",
     "总纲篇 · 全链推导",
     "业务背景与发展趋势 → Token对网络的要求 → 对智能体/多智能体（含互联协议）的技术要求：一条可追溯的完整推导链"),
    ("洞察报告_面向Token运营的互联网基础设施演进思考.md", "Token经济系列",
     "系列一 · 网络视角",
     "以Token运营为核心驱动力的原生智网：Token Net/TDN四层架构、关键技术拆解与运维智能体新要求"),
    ("洞察报告_从算电到Token_智能经济新形态的底层逻辑与普惠之路.md", "Token经济系列",
     "系列二 · 价值视角",
     "信通院算电-Token价值链、三维匹配降耗路径与Token成本价格模型，含设备商影响专章"),
    ("洞察报告_Token经济对ADN的诉求与影响_两篇联合分析.md", "Token经济系列",
     "系列三 · 自治视角",
     "两篇联合推演：Token经济对ADN（自动驾驶网络）的八大诉求、六大影响与L2→L4路线图"),
    ("洞察报告_面向微秒级响应的万兆光网关键技术与创新应用研究.md", "Token经济系列",
     "系列四 · 接入视角",
     "万兆光网微秒级确定性：50G-PON单帧多突发/开窗优化/现网样本入算验证，含设备商影响与ADN诉求专章"),
    ("洞察报告_智能体与多智能体的技术诉求分析.md", "Token经济系列",
     "系列五 · 智能体视角",
     "对智能体/多智能体的技术诉求：个体-协同-网络-治理四层诉求矩阵、关键技术架构与设备商机会"),
    ("Agensh论文分析报告.md", "其他分析文档",
     "论文分析",
     "《Agensh: Scaling Organizational Intelligence to 1,024 Agents》（Microsoft Research）全文分析报告"),
    ("Agensh洞察_问题-解法-ADN启发.md", "其他分析文档",
     "论文洞察",
     "Agensh论文的背景、问题与解法，以及对自动驾驶网络（ADN）的启发；配图引自论文官方HTML版"),
    ("issue6_sampling.md", "其他分析文档",
     "调研记录",
     "《通信世界》2026年第6期杂志文章ID区间抽样调查记录"),
]

CSS = """
:root{--accent:#1a5fb4;--ink:#22313f;--line:#d8e0ea}
*{box-sizing:border-box}
body{margin:0;background:#eef1f5;color:var(--ink);line-height:1.9;
  font-family:"Microsoft YaHei","PingFang SC","Noto Sans SC","Segoe UI",sans-serif}
.page{max-width:1000px;margin:28px auto;background:#fff;padding:52px 64px 64px;
  box-shadow:0 2px 24px rgba(20,40,80,.10);border-radius:10px}
header.meta{border-bottom:1px solid var(--line);margin-bottom:28px;padding-bottom:14px;
  display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
header.meta .brand{font-size:13px;color:#6b7a8c;letter-spacing:1px}
h1{font-size:27px;color:#122a44;line-height:1.5;border-bottom:3px solid var(--accent);
  padding-bottom:14px;margin:0 0 24px}
h2{font-size:20px;color:var(--accent);border-left:5px solid var(--accent);
  padding-left:12px;margin:40px 0 16px}
h3{font-size:16.5px;color:#1f3b5c;margin:28px 0 12px}
h4{font-size:15px;color:#33475b;margin:22px 0 10px}
p{margin:10px 0}
strong{color:#0e2c4e}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px}
th{background:#eaf1f9;color:#143a63;font-weight:600}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}
tbody tr:nth-child(even) td{background:#f8fafd}
blockquote{border-left:4px solid #7fa8d9;background:#f2f7fd;margin:18px 0;padding:12px 20px;
  color:#3c4c5e;border-radius:0 8px 8px 0}
blockquote p{margin:6px 0}
img{max-width:100%;display:block;margin:12px auto;border:1px solid #e0e6ee;
  border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.05)}
code{background:#f0f3f7;padding:1px 6px;border-radius:4px;font-size:.92em;
  font-family:Consolas,Monaco,monospace}
hr{border:none;border-top:1px solid var(--line);margin:34px 0}
ul,ol{padding-left:26px}
li{margin:4px 0}
a{color:var(--accent)}
nav.toc{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
  padding:18px 26px;margin:0 0 30px}
nav.toc .toc-title{font-size:14px;font-weight:700;color:#143a63;margin-bottom:8px;letter-spacing:2px}
nav.toc a{text-decoration:none;color:#245b9e;font-size:14px}
nav.toc a:hover{text-decoration:underline}
nav.toc ol{margin:0;padding-left:24px}
nav.toc li{margin:3px 0}
nav.toc .lv3 a{color:#5c7590;font-size:13px}
@media print{
  body{background:#fff}
  .page{box-shadow:none;margin:0;max-width:none;padding:10mm 6mm;border-radius:0}
  nav.toc{display:none}
}
"""

INDEX_CSS = CSS + """
.card{border:1px solid var(--line);border-radius:12px;padding:22px 28px;margin:18px 0;
  background:#fcfdff;transition:box-shadow .15s}
.card:hover{box-shadow:0 4px 18px rgba(20,40,80,.12)}
.card h2{border:none;padding:0;margin:0 0 6px;font-size:18px}
.card h2 a{text-decoration:none;color:#143a63}
.card .tag{display:inline-block;font-size:12px;color:var(--accent);background:#e8f0fb;
  border-radius:20px;padding:2px 12px;margin-bottom:8px}
.card p{margin:6px 0 0;color:#4c5c6d;font-size:14px}
.group-title{font-size:15px;font-weight:700;color:#143a63;letter-spacing:2px;
  border-left:4px solid var(--accent);padding-left:10px;margin:34px 0 10px}
"""


def build_toc(toc_tokens):
    rows = []
    for tok in toc_tokens:
        if tok["level"] == 1:
            for c in tok.get("children", []):
                rows.append((2, c))
        elif tok["level"] in (2, 3):
            rows.append((tok["level"], tok))
    if not rows:
        return ""
    items = []
    i = 0
    while i < len(rows):
        lv, tok = rows[i]
        if lv == 2:
            children = []
            j = i + 1
            while j < len(rows) and rows[j][0] == 3:
                t = rows[j][1]
                children.append(f'<li class="lv3"><a href="#{t["id"]}">{html_mod.escape(t["name"])}</a></li>')
                j += 1
            if children:
                items.append(
                    f'<li><a href="#{tok["id"]}">{html_mod.escape(tok["name"])}</a>'
                    f"<ol>{''.join(children)}</ol></li>"
                )
                i = j
                continue
            items.append(f'<li><a href="#{tok["id"]}">{html_mod.escape(tok["name"])}</a></li>')
        i += 1
    return f'<nav class="toc"><div class="toc-title">目 录</div><ol>{"".join(items)}</ol></nav>'


def embed_images(body_html, md_dir):
    def repl(m):
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        img_path = os.path.join(md_dir, src.replace("/", os.sep))
        try:
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return f'src="data:image/png;base64,{b64}"'
        except OSError:
            return m.group(0)
    return re.sub(r'src="([^"]+)"', repl, body_html)


def get_title(text, toc_tokens):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        return m.group(1).strip()
    if toc_tokens:
        return toc_tokens[0]["name"]
    return "洞察报告"


def convert(md_name):
    md_path = os.path.join(BASE, md_name)
    md_dir = os.path.dirname(md_path)
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"])
    body = md.convert(text)
    body = embed_images(body, md_dir)
    toc = build_toc(md.toc_tokens)
    title = get_title(text, md.toc_tokens)
    page = (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{html_mod.escape(title)}</title>\n<style>{CSS}</style>\n</head>\n<body>\n"
        '<div class="page">\n'
        '<header class="meta"><span class="brand">洞察报告 · 深度分析</span>'
        '<span class="brand">自包含HTML · 可离线查看/直接打印</span></header>\n'
        f"{body}\n"
        "</div>\n</body>\n</html>"
    )
    if toc:
        anchor = "</blockquote>"
        idx = page.find(anchor)
        if idx != -1:
            pos = idx + len(anchor)
            page = page[:pos] + "\n" + toc + page[pos:]
        else:
            h1_end = page.find("</h1>")
            if h1_end != -1:
                pos = h1_end + len("</h1>")
                page = page[:pos] + "\n" + toc + page[pos:]
    out_path = os.path.join(BASE, md_name[:-3] + ".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    n_img = page.count("data:image/png;base64,")
    return out_path, title, n_img


def build_index():
    order = ["Token经济系列", "其他分析文档"]
    sections = []
    for group in order:
        cards = []
        for md_name, tag, desc, out_path, title in entries_by_group.get(group, []):
            href = html_mod.escape(os.path.basename(out_path))
            cards.append(
                f'<div class="card"><span class="tag">{html_mod.escape(tag)}</span>'
                f'<h2><a href="{href}">{html_mod.escape(title)}</a></h2>'
                f"<p>{html_mod.escape(desc)}</p>"
                f'<p><a href="{href}">打开完整报告 →</a></p></div>'
            )
        if cards:
            sections.append(f'<div class="group-title">{group}</div>' + "".join(cards))
    page = (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>洞察报告索引</title>\n"
        f"<style>{INDEX_CSS}</style>\n</head>\n<body>\n<div class=\"page\">\n"
        "<h1>洞察报告索引</h1>"
        "<p>系列深度分析文档汇总。Token经济系列四篇构成完整分析链：<strong>网络视角 → 价值视角 → 自治视角 → 接入视角</strong>。"
        "各报告均为自包含HTML（图片已内嵌），可离线查看、直接打印。</p>"
        + "".join(sections)
        + '<hr><p style="color:#6b7a8c;font-size:13px">Markdown源文件与提取图片（report_assets目录）保留在同目录下。</p>'
        "</div>\n</body>\n</html>"
    )
    out = os.path.join(BASE, "洞察报告索引.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    return out


entries_by_group = {}


def main():
    for md_name, group, tag, desc in FILES:
        out_path, title, n_img = convert(md_name)
        entries_by_group.setdefault(group, []).append((md_name, tag, desc, out_path, title))
        print(f"OK  images_embedded={n_img}  ->  {md_name[:-3]}.html".encode("ascii", "backslashreplace").decode())
    idx = build_index()
    print("OK  index built")


if __name__ == "__main__":
    main()
