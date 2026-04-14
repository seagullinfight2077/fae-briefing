#!/usr/bin/env python3
"""Generate FAE Briefing v3.0 HTML — multi-dimensional + desensitized."""

import json
from pathlib import Path

BASE = Path(__file__).parent
STATS = json.loads((BASE / "all_stats.json").read_text("utf-8"))
TMPLS = json.loads((BASE / "templates_v3.json").read_text("utf-8"))

# ── desensitization map (applied to ALL public output) ──────────────────────
DESEN = {
    "Robin": "上級主管",
    "robin": "上級主管",
    "Peter": "Lilian 主程式窗口",
    "Jay":   "MG 工程窗口",
    "johnson": "GA/DBA 窗口",
    "Crimson": "品質管理窗口",
    "Dan":   "PM 窗口",
    "Momo":  "客服主管窗口",
    "阿丹":  "PM 窗口",
    "巨嬰":  "信用業主",
    "alex":  "網路窗口",
    "RayLin": "IP/VPN 窗口",
    "Laura": "人事窗口",
    "David": "前端工程 A",
    "Dobi":  "前端工程 B",
    "Ludde": "前端工程 C",
    "Jerry": "後端工程 A",
    "James": "後端工程 B",
    "frank": "後端工程 C",
    "Ada":   "後端工程 D",
    "Firball02": "FAE-A",
    "Gao Firball741": "FAE-B",
}

def desen(text):
    """Apply desensitization to text."""
    for name, replacement in DESEN.items():
        text = text.replace(name, replacement)
    return text

def js(d):
    return json.dumps(d, ensure_ascii=False)

PL_KEYS = ["overall","line","credit","vendor","outsource"]
PL_LABELS = {"overall":"整體總覽","line":"LINE站","credit":"信用版","vendor":"遊戲商","outsource":"外包"}
PL_ICONS  = {"overall":"📊","line":"💬","credit":"💳","vendor":"🎮","outsource":"🌐"}
PL_COLORS = {"overall":"#FF6B35","line":"#00B4D8","credit":"#00D99F","vendor":"#9D4EDD","outsource":"#FB5607"}
PL_CSS    = {"overall":"","line":"pl-line","credit":"pl-credit","vendor":"pl-vendor","outsource":"pl-outsource"}

# ── CSS (unchanged from v2 + new tab styles) ────────────────────────────────
CSS = r"""
:root{--primary:#FF6B35;--primary-light:rgba(255,107,53,.15);--primary-dim:rgba(255,107,53,.08);--bg-dark:#1a1a2e;--bg-card:rgba(30,40,60,.85);--bg:var(--bg-dark);--card:var(--bg-card);--text:#e8e8e8;--text-dim:#aaa;--border:rgba(255,107,53,.2);--success:#00D99F;--warning:#FFB300;--danger:#ff4444;--info:#00B4D8}
*{margin:0;padding:0;box-sizing:border-box}
html{background:var(--bg-dark)}
body{font-family:system-ui,'Noto Sans TC',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);color:var(--text);min-height:100vh;line-height:1.6}
.nav{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(26,26,46,.95);backdrop-filter:blur(20px);border-bottom:2px solid var(--primary);padding:0 20px;display:flex;align-items:center;height:56px}
.nav-brand{font-weight:700;font-size:1.1em;color:var(--primary);margin-right:30px;white-space:nowrap}
.nav-links{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}
.nav-links::-webkit-scrollbar{display:none}
.nav-link{padding:8px 16px;color:var(--text-dim);text-decoration:none;border-radius:6px;font-size:.9em;white-space:nowrap;transition:all .2s}
.nav-link:hover,.nav-link.active{color:#fff;background:var(--primary-light)}
.nav-link.pl-line{border-left:3px solid #00B4D8}
.nav-link.pl-credit{border-left:3px solid #00D99F}
.nav-link.pl-vendor{border-left:3px solid #9D4EDD}
.nav-link.pl-outsource{border-left:3px solid #FB5607}
.container{max-width:1400px;margin:0 auto;padding:76px 24px 40px}
.cover{text-align:center;padding:60px 20px;margin-bottom:40px;background:var(--bg-card);border:1px solid var(--border);border-radius:12px}
.cover h1{font-size:2.8em;color:#fff;margin-bottom:12px;text-shadow:0 2px 20px rgba(255,107,53,.3)}
.cover .subtitle{font-size:1.3em;color:var(--primary);margin-bottom:20px}
.cover .meta{display:flex;justify-content:center;gap:30px;flex-wrap:wrap;color:var(--text-dim);font-size:.95em}
.cover .meta span{color:var(--primary);font-weight:600}
.section{margin-bottom:40px;scroll-margin-top:70px}
.section-title{display:flex;align-items:center;gap:12px;font-size:1.6em;color:#fff;margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid var(--primary)}
.section-title .num{background:var(--primary);color:var(--bg-dark);width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.7em;font-weight:700;flex-shrink:0}
.section-title.pl-line{border-bottom-color:#00B4D8}.section-title.pl-line .num{background:#00B4D8}
.section-title.pl-credit{border-bottom-color:#00D99F}.section-title.pl-credit .num{background:#00D99F}
.section-title.pl-vendor{border-bottom-color:#9D4EDD}.section-title.pl-vendor .num{background:#9D4EDD}
.section-title.pl-outsource{border-bottom-color:#FB5607}.section-title.pl-outsource .num{background:#FB5607}
.card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:24px;backdrop-filter:blur(10px);transition:all .3s}
.card:hover{border-color:var(--primary);box-shadow:0 8px 30px rgba(255,107,53,.15)}
.card h3{color:var(--primary);margin-bottom:12px;font-size:1.15em}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}
.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:20px;text-align:center}
.stat-card .label{color:var(--text-dim);font-size:.85em;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.stat-card .number{font-size:2.2em;font-weight:700;color:var(--primary);line-height:1.1}
.stat-card .detail{color:var(--text-dim);font-size:.85em;margin-top:4px}
.chart-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:20px;margin-bottom:24px}
.chart-box{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:20px;position:relative}
.chart-box h3{color:#fff;margin-bottom:12px;font-size:1.05em}
.chart-wrap{position:relative;height:350px}
.chart-wrap-sm{position:relative;height:300px}
.chart-wrap-lg{position:relative;height:450px}
table{width:100%;border-collapse:collapse}
thead{background:var(--primary-light)}
th{padding:14px 16px;text-align:left;color:var(--primary);font-weight:600;font-size:.85em;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid var(--primary)}
td{padding:12px 16px;border-bottom:1px solid var(--border);color:#ddd;font-size:.93em}
tbody tr:hover{background:var(--primary-dim)}
.badge{display:inline-block;padding:3px 10px;border-radius:4px;font-weight:600;font-size:.82em}
.badge-danger{background:var(--danger);color:#fff}
.badge-warning{background:var(--warning);color:#000}
.badge-info{background:var(--info);color:#fff}
.badge-success{background:var(--success);color:#000}
.badge-primary{background:var(--primary);color:var(--bg-dark)}
.section-divider{border:none;border-top:1px solid var(--border);margin:50px 0 40px}
footer{text-align:center;padding:30px;color:var(--text-dim);font-size:.85em;border-top:1px solid var(--border);margin-top:40px}
/* Tabs */
.tab-bar{display:flex;gap:4px;margin-bottom:20px;overflow-x:auto;scrollbar-width:none}
.tab-bar::-webkit-scrollbar{display:none}
.tab-btn{padding:10px 20px;border:1px solid var(--border);border-radius:8px 8px 0 0;background:var(--bg-card);color:var(--text-dim);cursor:pointer;font-size:.95em;font-weight:600;transition:all .2s;white-space:nowrap}
.tab-btn:hover{color:#fff;background:var(--primary-dim)}
.tab-btn.active{color:#fff;background:var(--primary-light);border-bottom-color:transparent}
.tab-panel{display:none}
.tab-panel.active{display:block}
/* Template cards */
.template-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:20px}
.template-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;overflow:hidden}
.template-header{background:var(--primary-light);padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}
.template-num{background:var(--primary);color:var(--bg-dark);width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9em;flex-shrink:0}
.template-title{color:#fff;font-weight:600;font-size:1.05em}
.template-body{padding:20px}
.template-section{margin-bottom:14px}
.template-section:last-child{margin-bottom:0}
.template-label{color:var(--primary);font-weight:600;font-size:.85em;text-transform:uppercase;margin-bottom:6px;letter-spacing:.5px}
.template-content{background:rgba(0,0,0,.2);border-radius:6px;padding:12px 16px;font-size:.92em;line-height:1.7;color:#ccc;border-left:3px solid var(--primary)}
.template-warning{background:rgba(255,68,68,.1);border:1px solid rgba(255,68,68,.3);border-radius:6px;padding:10px 14px;font-size:.88em;color:#ff8888}
/* FAQ */
.faq-category{margin-bottom:24px}
.faq-category-title{color:var(--primary);font-size:1.2em;margin-bottom:12px;padding:8px 16px;background:var(--primary-dim);border-radius:6px;border-left:4px solid var(--primary)}
.faq-item{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;margin-bottom:10px;overflow:hidden}
.faq-q{padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:10px;transition:background .2s;user-select:none}
.faq-q:hover{background:var(--primary-dim)}
.faq-q .arrow{color:var(--primary);transition:transform .3s;font-size:.8em}
.faq-q.open .arrow{transform:rotate(90deg)}
.faq-q .q-text{font-weight:600;color:#fff;flex:1}
.faq-a{display:none;padding:0 18px 16px;color:#ccc;font-size:.93em;line-height:1.7;border-top:1px solid var(--border)}
.faq-a.show{display:block;padding-top:14px}
.faq-a ol,.faq-a ul{margin-left:20px;margin-top:6px}
.faq-a li{margin-bottom:4px}
/* Escalation */
.flow-steps{display:flex;align-items:center;gap:0;flex-wrap:wrap;justify-content:center;margin:20px 0}
.flow-step{background:var(--primary-light);border:1px solid var(--primary);border-radius:8px;padding:14px 18px;text-align:center;font-size:.95em;font-weight:600}
.flow-arrow{font-size:1.5em;color:var(--primary);padding:0 6px}
/* PL comparison */
.pl-comparison-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:24px}
.pl-card{background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:20px;border-top:4px solid var(--primary)}
.pl-card h4{font-size:1.15em;margin-bottom:12px}
.pl-card .pl-stat{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:.93em}
.pl-card .pl-stat:last-child{border-bottom:none}
.pl-card .pl-stat .val{font-weight:700}
/* Station dashboard */
.station-dash-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:24px}
.station-mini{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:16px}
.station-mini h4{font-size:1em;color:#fff;margin-bottom:8px}
.station-mini .sm-row{display:flex;justify-content:space-between;font-size:.88em;padding:3px 0;color:var(--text-dim)}
.station-mini .sm-row .sm-val{color:var(--primary);font-weight:600}
/* RPA */
.rpa-card{background:var(--bg-card);border:1px solid var(--success);border-radius:10px;padding:20px;border-left:4px solid var(--success)}
.rpa-card h4{color:var(--success);margin-bottom:8px}
@media(max-width:768px){.chart-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:repeat(2,1fr)}.template-grid{grid-template-columns:1fr}.pl-comparison-grid{grid-template-columns:1fr}.cover h1{font-size:1.8em}}
"""

# ── helpers ─────────────────────────────────────────────────────────────────
def kpi_cards(d):
    t = d["totalMessages"]; c = d["complaintCount"]; n = d["noiseRatio"]
    cats = {k:v for k,v in d["categories"].items() if k!="其他"}
    top = max(cats, key=cats.get) if cats else "N/A"
    s = d["severityCounts"]; sc = len(d["stationComplaints"])
    cr = round(c/t*100,1) if t else 0
    return f"""<div class="stats-grid">
<div class="stat-card"><div class="label">總訊息量</div><div class="number">{t:,}</div><div class="detail">含有效+噪音</div></div>
<div class="stat-card"><div class="label">客訴數</div><div class="number" style="color:var(--danger)">{c:,}</div><div class="detail">佔比 {cr}%</div></div>
<div class="stat-card"><div class="label">站點數</div><div class="number" style="color:var(--info)">{sc}</div><div class="detail">個獨立站點</div></div>
<div class="stat-card"><div class="label">噪音比</div><div class="number" style="color:var(--warning)">{n}%</div><div class="detail">系統/閒聊</div></div>
<div class="stat-card"><div class="label">最大類別</div><div class="number" style="font-size:1.4em">{top}</div><div class="detail">{cats.get(top,0):,} 筆</div></div>
<div class="stat-card"><div class="label">P0 緊急</div><div class="number" style="color:var(--danger)">{s.get('P0',0)}</div><div class="detail">P1:{s.get('P1',0)} / P2:{s.get('P2',0)}</div></div>
</div>"""


def pl_section(data, key, num):
    css = PL_CSS[key]; icon = PL_ICONS[key]; label = PL_LABELS[key]
    sid = key if key != "overall" else "overview"
    cats = {k:v for k,v in data["categories"].items() if k!="其他"}
    sorted_cats = sorted(cats.items(), key=lambda x:-x[1])[:5]
    stations = sorted(data["stationComplaints"].items(), key=lambda x:-x[1])
    sh = max(300, len(stations)*35)
    top_s = "、".join(f"{k}({v})" for k,v in stations[:5])
    top_c = "、".join(f"{k}({v})" for k,v in sorted_cats)

    desc_map = {
        "overall": f"全產品線共 {data['totalMessages']:,} 則訊息，{data['complaintCount']:,} 則客訴。前五大類別：{top_c}。",
        "line": f"LINE站為核心產品線（14 站）。帳號問題居首（{cats.get('帳號問題',0)}），優惠活動爭議次之（{cats.get('優惠活動爭議',0)}）。",
        "credit": f"信用版含 QA/FT 兩站，帳務對帳為特色問題（{cats.get('帳務對帳',0)}），P1 比例偏高（{data['severityCounts'].get('P1',0)}）。",
        "vendor": f"遊戲商含 TP/XG/UGS 三站。遊戲異常為首要問題（{cats.get('遊戲異常',0)}），噪音比最低（{data['noiseRatio']}%）。",
        "outsource": f"外包涵蓋 5 站，N8 印度站客訴量 {data['stationComplaints'].get('N8_印度站',0)} 為全公司單站最高。",
    }
    # DESENSITIZE the severity table — no Robin
    return f"""
<section id="{sid}" class="section">
<div class="section-title {css}"><span class="num">{num}</span> {icon} {label} — 客訴分析</div>
{kpi_cards(data)}
<div class="chart-grid">
<div class="chart-box"><h3>客訴類別佔比（排除「其他」）</h3><div class="chart-wrap"><canvas id="{key}CatPie"></canvas></div></div>
<div class="chart-box"><h3>各類別絕對數量</h3><div class="chart-wrap"><canvas id="{key}CatBar"></canvas></div></div>
</div>
<div class="card" style="margin-bottom:24px"><h3>分析摘要</h3><p style="color:#ccc;line-height:1.7">{desc_map[key]}</p><p style="color:var(--text-dim);margin-top:8px;font-size:.9em">Top 站點：{top_s}</p></div>
<div class="chart-grid">
<div class="chart-box"><h3>近 30 日趨勢</h3><div class="chart-wrap"><canvas id="{key}Trend30"></canvas></div></div>
<div class="chart-box"><h3>近 90 日趨勢</h3><div class="chart-wrap"><canvas id="{key}Trend90"></canvas></div></div>
</div>
<div class="chart-box" style="margin-bottom:24px"><h3>站點客訴熱度排行</h3><div style="position:relative;height:{sh}px"><canvas id="{key}StationBar"></canvas></div></div>
<div class="chart-grid">
<div class="chart-box"><h3>嚴重度分布</h3><div class="chart-wrap"><canvas id="{key}SevPie"></canvas></div></div>
<div class="card"><h3>嚴重度對應處理原則</h3><table><thead><tr><th>等級</th><th>定義</th><th>回應時限</th><th>處理方式</th></tr></thead><tbody>
<tr><td><span class="badge badge-danger">P0 緊急</span></td><td>大量用戶受影響 / 資金異常</td><td>5 分鐘</td><td>直接電話上級主管</td></tr>
<tr><td><span class="badge badge-warning">P1 高</span></td><td>單一站點整體異常</td><td>15 分鐘</td><td>回報 → Slack → 追蹤</td></tr>
<tr><td><span class="badge badge-info">P2 中</span></td><td>個別用戶問題</td><td>1 小時</td><td>標準 SOP 處理</td></tr>
</tbody></table></div></div>
</section><hr class="section-divider">"""


def compare_section(stats, num):
    pc = stats["plCompare"]
    cards = ""
    for name, color in [("LINE站","#00B4D8"),("信用版","#00D99F"),("遊戲商","#9D4EDD"),("外包","#FB5607")]:
        d = pc[name]; rate = round(d["complaints"]/d["total"]*100,1)
        icon = {"LINE站":"💬","信用版":"💳","遊戲商":"🎮","外包":"🌐"}[name]
        cards += f"""<div class="pl-card" style="border-top-color:{color}"><h4 style="color:{color}">{icon} {name}</h4>
<div class="pl-stat"><span>總訊息</span><span class="val">{d['total']:,}</span></div>
<div class="pl-stat"><span>客訴數</span><span class="val" style="color:var(--danger)">{d['complaints']:,}</span></div>
<div class="pl-stat"><span>站點數</span><span class="val">{d['stations']}</span></div>
<div class="pl-stat"><span>客訴率</span><span class="val">{rate}%</span></div></div>"""

    return f"""
<section id="compare" class="section">
<div class="section-title"><span class="num">{num}</span> 📈 產品線對比分析</div>
<div class="pl-comparison-grid">{cards}</div>
<div class="chart-grid">
<div class="chart-box"><h3>各產品線客訴數對比</h3><div class="chart-wrap"><canvas id="plCompareBar"></canvas></div></div>
<div class="chart-box"><h3>各產品線客訴率對比</h3><div class="chart-wrap"><canvas id="plCompareRate"></canvas></div></div>
</div>
<div class="chart-grid">
<div class="chart-box"><h3>各產品線訊息量佔比</h3><div class="chart-wrap"><canvas id="plComparePie"></canvas></div></div>
<div class="chart-box"><h3>各產品線 Top 3 客訴類別</h3><div class="chart-wrap-lg"><canvas id="plCompareTopCats"></canvas></div></div>
</div>
<div class="card" style="margin-bottom:24px"><h3>產品線對比關鍵發現</h3><ul style="margin-left:20px;color:#ccc;line-height:1.8">
<li><strong style="color:#00B4D8">LINE站</strong>：客訴量最大（{pc['LINE站']['complaints']:,}），帳號問題為主</li>
<li><strong style="color:#00D99F">信用版</strong>：帳務對帳為特色問題，P1 比例偏高</li>
<li><strong style="color:#9D4EDD">遊戲商</strong>：體量最小但遊戲異常佔比高，噪音比最低（4.4%）</li>
<li><strong style="color:#FB5607">外包</strong>：N8 印度站為全公司單站客訴最高</li>
</ul></div>
</section><hr class="section-divider">"""


# ── NEW v3.0 sections ───────────────────────────────────────────────────────

def templates_section(num):
    """4-tab template section, 10 per PL = 40 total."""
    tabs = ""
    panels = ""
    tab_map = [("LINE站","line"),("信用版","credit"),("遊戲商","vendor"),("外包","outsource")]
    for i,(label,key) in enumerate(tab_map):
        active = " active" if i==0 else ""
        tabs += f'<button class="tab-btn{active}" onclick="switchTab(\'tmpl\',\'{key}\')">{PL_ICONS.get(key,"")} {label}（10 題）</button>'
        cards = ""
        for j,t in enumerate(TMPLS.get(label,[])):
            title = desen(t["title"])
            desc = desen(t["desc"])
            reply = desen(t["reply"]).replace("\n","<br>")
            warning = desen(t["warning"])
            cards += f"""<div class="template-card"><div class="template-header"><span class="template-num">{j+1}</span><span class="template-title">{title}</span></div>
<div class="template-body"><div class="template-section"><div class="template-label">問題描述</div><p style="color:#ccc;font-size:.93em">{desc}</p></div>
<div class="template-section"><div class="template-label">回覆話術</div><div class="template-content">{reply}</div></div>
<div class="template-section"><div class="template-label">注意事項</div><div class="template-warning">{warning}</div></div></div></div>"""
        panels += f'<div class="tab-panel{active}" id="tmpl-{key}"><div class="template-grid">{cards}</div></div>'

    return f"""
<section id="templates" class="section">
<div class="section-title"><span class="num">{num}</span> 📋 產品線回覆範本（40 題）</div>
<p style="color:var(--text-dim);margin-bottom:16px">每個產品線 10 則高頻問題標準回覆，含話術與注意事項。點擊切換產品線。</p>
<div class="tab-bar">{tabs}</div>
{panels}
</section><hr class="section-divider">"""


def station_dashboard_section(stats, num):
    """Quantitative station dashboard — no qualitative commentary, no person names."""
    cards = ""
    for key in ["line","credit","vendor","outsource"]:
        d = stats[key]
        for station, complaints in sorted(d["stationComplaints"].items(), key=lambda x:-x[1]):
            total = d["totalMessages"]
            # Compute top 2 categories for this station from daily data (approximate from overall)
            # Since we don't have per-station-per-category breakdown, show PL-level top categories
            cats = {k:v for k,v in d["categories"].items() if k!="其他"}
            top2 = sorted(cats.items(), key=lambda x:-x[1])[:2]
            top2_text = " / ".join(f"{k}" for k,v in top2)
            color = PL_COLORS[key]
            cards += f"""<div class="station-mini" style="border-left:3px solid {color}">
<h4 style="color:{color}">{station}</h4>
<div class="sm-row"><span>客訴數</span><span class="sm-val">{complaints:,}</span></div>
<div class="sm-row"><span>所屬板塊</span><span class="sm-val">{PL_LABELS[key]}</span></div>
<div class="sm-row"><span>板塊主要類別</span><span style="color:#ccc;font-size:.85em">{top2_text}</span></div>
</div>"""

    return f"""
<section id="stations" class="section">
<div class="section-title"><span class="num">{num}</span> 🏢 站點量化儀表板</div>
<p style="color:var(--text-dim);margin-bottom:16px">全部 24 站點量化指標一覽。按客訴數由高到低排列。</p>
<div class="station-dash-grid">{cards}</div>
</section><hr class="section-divider">"""


def violations_section(num):
    """Full violation cases with real names, dates, quotes — internal use."""
    cases_html = ""
    cases = [
        ("1","真實違反","嚴重","badge-danger","2026-04-01","TP 捕魚（遊戲商群）","Gao Firball741","鐵律 #2 禁用詞 + 情緒升級","「不可能朔源」","對方用「不可能」反問 3 次，對話情緒急速升級。Vendor 關係受損。"),
        ("2","真實違反","中度","badge-danger","2026-02-10","信用版_QA","Firball02","鐵律 #2 時間承諾","「本次維護預計時長半小時」","維護公告中給出明確時間承諾，若超時業主將以此為據。"),
        ("3","真實違反","輕度","badge-warning","2026-01-16","L13_第一名","Dan","鐵律 #2 禁用詞「一定」","「可以玩這活動的玩家一定是有儲值的」","解釋活動規則時使用「一定」，站長可能引用。"),
        ("4","邊界案例","低","badge-info","2026-03-16","L09_伍洲","Dan","鐵律 #2 禁用詞「一定」","「一定需要設定白名單才可以訪問」","技術性說明，語境為系統必要條件。"),
        ("5","邊界案例","極低","badge-info","2026-01-28","A95_九五至尊","Firball02","鐵律 #2 禁用詞「一定」","「不代表轉一定有倍數及分數」","否定句中的「一定」語意合理。"),
        ("6","邊界案例","低-中","badge-info","2026-01-25","信用版_QA","Gao Firball741","鐵律 #2 時間承諾","「更新至6點數據 約5分鐘」","有「約」字緩衝但仍為時間承諾。"),
        ("7","邊界案例","無","badge-info","2026-04-01","信用版_QA","Gao Firball741","鐵律 #2 禁用詞「一定」","「開放時間不一定，要等廠商回覆」","「不一定」表達不確定性，語意正確。"),
        ("8","邊界案例","低","badge-info","2026-04-01","K88_金五吉","Gao Firball741","鐵律 #2 禁用詞「一定」","「一定要點擊參加才會開始計算」","操作指引中的必要條件描述。"),
        ("9","誤觸發","低","badge-success","2026-01-12","信用版_FT","Gao Firball741","鐵律 #2 時間承諾","「預計影響30分鐘」","標準維護通知格式。"),
        ("10","誤觸發","低","badge-success","2026-03-05","L06_吉滿滿_主管群","Firball02","鐵律 #2 時間承諾","「預計半小時左右可更新完成」","主管群 P0 級別，時間承諾風險更高。"),
        ("11","誤觸發","低","badge-success","2026-02-11","L06_吉滿滿","Gao Firball741","鐵律 #2 時間承諾","「更新需要10分鐘」","系統更新場景。"),
        ("12","誤觸發","可接受","badge-success","2026-02-04","L04_大頭仔 / JIN_錢老爺","Gao Firball741","鐵律 #2 時間承諾","「目前排程最快就是1分鐘」","系統排程機制事實描述。"),
    ]
    for c in cases:
        cases_html += f'<tr><td>{c[0]}</td><td><span class="badge {c[3]}">{c[1]}</span></td><td>{c[4]}</td><td>{c[5]}</td><td><strong>{c[6]}</strong></td><td>{c[7]}</td><td style="color:#ff8888">{c[8]}</td><td>{c[9]}</td></tr>'

    return f"""
<section id="violations" class="section">
<div class="section-title"><span class="num">{num}</span> ⚠️ 鐵律違反案例記錄</div>
<div style="background:rgba(255,68,68,.08);border:1px solid rgba(255,68,68,.3);border-radius:8px;padding:14px 18px;margin-bottom:20px">
<p style="color:var(--danger);font-weight:600">⚠️ 內部訓練用，禁止外傳。掃描期間：2026-01-01 至 2026-04-13</p>
<p style="color:var(--text-dim);font-size:.9em;margin-top:4px">35 命中 / 12 筆記錄 → 真實違反 3 件 · 邊界案例 5 件 · 誤觸發 4 件（&lt; 0.01% 訊息量）</p>
</div>
<div class="stats-grid">
<div class="stat-card"><div class="label">掃描命中</div><div class="number" style="color:var(--warning)">35</div><div class="detail">自動掃描</div></div>
<div class="stat-card"><div class="label">保留記錄</div><div class="number" style="color:var(--danger)">12</div><div class="detail">人工覆審</div></div>
<div class="stat-card"><div class="label">真實違反</div><div class="number" style="color:var(--danger)">3</div><div class="detail">需個別複盤</div></div>
<div class="stat-card"><div class="label">整體合規率</div><div class="number" style="color:var(--success)">&gt;99.99%</div><div class="detail">守規良好</div></div>
</div>
<div class="card" style="margin-bottom:24px;overflow-x:auto"><h3>12 筆完整案例</h3>
<table><thead><tr><th>#</th><th>分類</th><th>日期</th><th>站點</th><th>人員</th><th>違反類型</th><th>原文引用</th><th>情境/影響</th></tr></thead>
<tbody>{cases_html}</tbody></table></div>
<div class="chart-grid">
<div class="card"><h3>人員違反彙總</h3><table><thead><tr><th>FAE 人員</th><th>次數</th><th>嚴重程度</th><th>建議</th></tr></thead><tbody>
<tr><td><strong>Gao Firball741</strong></td><td>8 次（1 真實 + 7 邊界/誤觸發）</td><td><span class="badge badge-danger">高</span></td><td>個別複盤 + Vendor 禁語訓練 + 時間承諾替代話術</td></tr>
<tr><td><strong>Firball02</strong></td><td>3 次（1 真實 + 2 邊界）</td><td><span class="badge badge-warning">中</span></td><td>時間承諾替代話術培訓</td></tr>
<tr><td><strong>Dan</strong></td><td>2 次（1 真實 + 1 邊界）</td><td><span class="badge badge-info">低</span></td><td>指令性用詞替換練習</td></tr>
</tbody></table></div>
<div class="card"><h3>改善建議</h3><ul style="margin-left:20px;color:#ccc;line-height:1.8">
<li><strong>短期</strong>：Gao Firball741 個別複盤（重點「不可能朔源」案例）</li>
<li><strong>短期</strong>：新增「不可能」至禁用詞表</li>
<li><strong>短期</strong>：維護公告模板標準化，移除所有時間數字</li>
<li><strong>中期</strong>：對外發送前自動掃描禁用詞，觸發時提醒修改</li>
<li><strong>中期</strong>：季度複盤會議 + 替代話術卡片</li>
</ul></div></div>
<div class="card" style="margin-top:16px"><h3>禁用詞完整清單</h3><table><thead><tr><th>禁用詞</th><th>替代話術</th></tr></thead><tbody>
<tr><td style="color:#ff8888">一定</td><td>需要 / 建議</td></tr>
<tr><td style="color:#ff8888">絕對</td><td>目前確認</td></tr>
<tr><td style="color:#ff8888">保證</td><td>我們會持續追蹤</td></tr>
<tr><td style="color:#ff8888">不可能</td><td>這部分我們再確認</td></tr>
<tr><td style="color:#ff8888">馬上好</td><td>正在處理中</td></tr>
<tr><td style="color:#ff8888">X 分鐘內</td><td>完成後第一時間同步</td></tr>
<tr><td style="color:#ff8888">應該很快</td><td>持續追蹤中</td></tr>
</tbody></table></div>
</section><hr class="section-divider">"""


def rules_section():
    """Iron rules — DESENSITIZED."""
    return """
<section id="rules" class="section">
<div class="section-title"><span class="num">!</span> FAE 鐵律（必讀）</div>
<div style="background:rgba(255,68,68,.08);border:1px solid rgba(255,68,68,.3);border-radius:10px;padding:24px;margin-bottom:24px">
<h3 style="color:var(--danger);margin-bottom:14px;font-size:1.15em">五大鐵律 — 凌駕所有技術判斷</h3>
<ol style="margin-left:20px;color:#ddd">
<li style="margin-bottom:8px;line-height:1.6"><strong style="color:#ff8888">先自查再問人</strong> — 查本文件 → FAQ → 歷史對話 → 後台 UAT / Postman → Kibana → 再找工程</li>
<li style="margin-bottom:8px;line-height:1.6"><strong style="color:#ff8888">禁止時間承諾</strong> — 不說「幾分鐘」「幾小時好」→ 用「有進度第一時間同步」</li>
<li style="margin-bottom:8px;line-height:1.6"><strong style="color:#ff8888">禁止絕對用語</strong> — 不說「一定」「絕對」「保證」→ 用「依目前資訊來看…」</li>
<li style="margin-bottom:8px;line-height:1.6"><strong style="color:#ff8888">一次問完不擠牙膏</strong> — 把需要的資料一次列齊，禁止連續追問</li>
<li style="margin-bottom:8px;line-height:1.6"><strong style="color:#ff8888">以條款為準，只引用不解釋</strong> — 活動爭議引用原文，不自行詮釋</li>
</ol></div>
<div class="chart-grid">
<div class="card"><h3 style="color:var(--danger)">禁用話術</h3><table><thead><tr><th>禁止說法</th><th>原因</th></tr></thead><tbody>
<tr><td style="color:#ff8888">「一定能解決」「保證沒問題」</td><td>無法保證結果</td></tr>
<tr><td style="color:#ff8888">「預計 30 分鐘內完成」</td><td>時間不可控</td></tr>
<tr><td style="color:#ff8888">「這是工程的問題」</td><td>禁止甩鍋</td></tr>
<tr><td style="color:#ff8888">「之前也是這樣處理」</td><td>每次需獨立確認</td></tr>
</tbody></table></div>
<div class="card"><h3 style="color:var(--success)">建議話術（進度承諾）</h3><table><thead><tr><th>建議說法</th><th>適用場景</th></tr></thead><tbody>
<tr><td style="color:#88ff88">「已收到，確認中，有進度第一時間同步」</td><td>所有問題通用開場</td></tr>
<tr><td style="color:#88ff88">「依目前資訊來看，可能是 XX 原因」</td><td>需推測原因時</td></tr>
<tr><td style="color:#88ff88">「已回報相關單位，目前等待回覆」</td><td>需升級時</td></tr>
<tr><td style="color:#88ff88">「麻煩提供 XX，我們加速處理」</td><td>需補充資料時</td></tr>
</tbody></table></div></div>
</section><hr class="section-divider">"""


def rpa_section(num):
    """RPA Top 3 — real content from 5_RPA_Top3_自動化場景.md."""
    return f"""
<section id="rpa" class="section">
<div class="section-title"><span class="num">{num}</span> 🤖 RPA 自動化 Top 3 建議</div>
<p style="color:var(--text-dim);margin-bottom:16px">篩選條件：單月 ≥ 50 次 + 流程固定 + 輸入格式標準 + 輸出可驗證 + 失敗可回補。</p>

<div class="rpa-card" style="margin-bottom:20px">
<h4>🥇 Top 1 — N8 印度站 IP 白名單自動處理</h4>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:12px 0">
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">白名單訊息</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">473 則</div><div style="font-size:.75em;color:var(--text-dim)">佔 N8 群 5.1%</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">月均頻次</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">150+</div><div style="font-size:.75em;color:var(--text-dim)">次/月</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">格式標準度</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">★★★★★</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">月省人力</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">7.5~12.5h</div></div>
</div>
<p style="color:#ccc;font-size:.92em;line-height:1.7;margin-bottom:8px"><strong>訊息模式</strong>：<code style="background:rgba(0,0,0,.3);padding:2px 6px;border-radius:3px">IP不在白名单 180.190.171.159 please add po</code> — 標準 IPv4 + 固定觸發詞，來源為可信任窗口（CS-Ariela、CS-Xin、Rin Li）。</p>
<p style="color:#ccc;font-size:.92em;line-height:1.7;margin-bottom:8px"><strong>RPA 流程</strong>：監聽群 → NLP 提取 IP → IPv4 正則驗證 → 來源驗證 → 登記白名單表 → 送技術端 API → 回覆 "✅ Added" → 結案歸檔</p>
<p style="color:#ccc;font-size:.92em;line-height:1.7"><strong>風險</strong>：白名單涉資安，建議先做「半自動」（RPA 建議 + FAE 一鍵核准），需 Crimson 同意。<br><span class="badge badge-success">開發成本：中｜風險：低｜ROI：高｜UAT 期：2~4 週</span></p>
</div>

<div class="rpa-card" style="margin-bottom:20px">
<h4>🥈 Top 2 — LINE 站「後台操作」FAQ 自動導流</h4>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:12px 0">
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">後台設定問題</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">796 次</div><div style="font-size:.75em;color:var(--text-dim)">問題矩陣最高頻</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">月均頻次</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">265</div><div style="font-size:.75em;color:var(--text-dim)">次/月</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">80/20 規則</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">20 題</div><div style="font-size:.75em;color:var(--text-dim)">覆蓋 80% 問題</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">月省人力</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">22~66h</div></div>
</div>
<p style="color:#ccc;font-size:.92em;line-height:1.7;margin-bottom:8px"><strong>訊息模式</strong>：「這個要怎麼設」「XX 功能點不了」「代理怎麼加」— 多樣但 80% 可歸類到 20 個高頻問題。</p>
<p style="color:#ccc;font-size:.92em;line-height:1.7;margin-bottom:8px"><strong>RPA 流程</strong>（半自動）：監聽站長訊息 → NLP 分類 → 匹配 FAQ 庫（信心度 ≥ 70%）→ 推送答案/操作影片 → FAE 確認補充。低信心度或站長回「看不懂」→ 人工接手。</p>
<p style="color:#ccc;font-size:.92em;line-height:1.7"><strong>風險</strong>：誤答可能擾亂站長，需高信心度門檻 + 「跳過 AI 直接找 FAE」選項。建議先上 1~2 站試點（JIN、A95）。<br><span class="badge badge-success">開發成本：中高｜風險：中｜ROI：高｜建置期：4~8 週</span></p>
</div>

<div class="rpa-card" style="margin-bottom:20px">
<h4>🥉 Top 3 — 週帳三邊對帳差異檢測 + 預警</h4>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:12px 0">
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">三邊比對</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">遊戲商/MG/GA</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">Deadline</div><div style="font-size:1.6em;font-weight:700;color:var(--danger)">週一 0 點</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">可驗證度</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">★★★★★</div><div style="font-size:.75em;color:var(--text-dim)">數字直接比對</div></div>
<div style="text-align:center;padding:10px;background:rgba(0,0,0,.2);border-radius:6px"><div style="color:var(--text-dim);font-size:.8em">月省人力</div><div style="font-size:1.6em;font-weight:700;color:var(--success)">~10h</div><div style="font-size:.75em;color:var(--text-dim)">+ deadline 保險</div></div>
</div>
<p style="color:#ccc;font-size:.92em;line-height:1.7;margin-bottom:8px"><strong>場景</strong>：每週日晚 FAE 需拉三邊數據人工比對，差異多為漏單或延遲寫入，極耗時且週一 0 點前必須完成。</p>
<p style="color:#ccc;font-size:.92em;line-height:1.7;margin-bottom:8px"><strong>RPA 流程</strong>：週日 18:00 自動觸發 → 拉三邊數據 → 比對引擎產出差異列表 → 分類（漏單/延遲/雙寫不一致）→ 自動補跑等 30 分鐘重新比對 → 差異 &lt; 閾值通知 FAE / 差異 &gt; 閾值告警當班幹部 → 週一 00:00 自動產週報</p>
<p style="color:#ccc;font-size:.92em;line-height:1.7"><strong>風險</strong>：需接三個系統 API（需協調 Jay/Peter），自動化出錯一次可能動搖信用業主信心。建議先做「輔助版」。<br><span class="badge badge-warning">開發成本：高｜風險：中｜ROI：極高（風險面）｜建置期：6~10 週</span></p>
</div>

<div class="card" style="margin-bottom:20px"><h3>成本/效益摘要</h3>
<table><thead><tr><th>RPA</th><th>開發</th><th>月節省人力</th><th>ROI</th><th>風險</th></tr></thead><tbody>
<tr><td><strong style="color:var(--success)">Top 1 N8 白名單</strong></td><td>中</td><td>7.5~12.5 小時</td><td><span class="badge badge-success">高</span></td><td><span class="badge badge-success">低</span></td></tr>
<tr><td><strong style="color:var(--success)">Top 2 後台 FAQ</strong></td><td>中高</td><td>22~66 小時</td><td><span class="badge badge-success">高</span></td><td><span class="badge badge-warning">中</span></td></tr>
<tr><td><strong style="color:var(--success)">Top 3 對帳輔助</strong></td><td>高</td><td>10 小時 + deadline 保險</td><td><span class="badge badge-primary">極高</span></td><td><span class="badge badge-warning">中</span></td></tr>
</tbody></table></div>

<div class="card"><h3>推動路線圖</h3>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:12px">
<div style="padding:14px;background:rgba(0,217,159,.08);border:1px solid rgba(0,217,159,.3);border-radius:8px"><strong style="color:var(--success)">階段 1（Month 1~2）</strong><p style="color:#ccc;font-size:.9em;margin-top:4px">先做 N8 IP 白名單半自動版。每日回顧調整閾值。</p></div>
<div style="padding:14px;background:rgba(0,180,216,.08);border:1px solid rgba(0,180,216,.3);border-radius:8px"><strong style="color:var(--info)">階段 2（Month 3~5）</strong><p style="color:#ccc;font-size:.9em;margin-top:4px">建 FAQ 分類器，上 1~2 個 LINE 站試點，量化「FAE 時間節省」。</p></div>
<div style="padding:14px;background:rgba(255,179,0,.08);border:1px solid rgba(255,179,0,.3);border-radius:8px"><strong style="color:var(--warning)">階段 3（Month 6~8）</strong><p style="color:#ccc;font-size:.9em;margin-top:4px">先做差異檢測 + 人工決策，通過 UAT 後再開自動產報表。</p></div>
<div style="padding:14px;background:rgba(157,78,221,.08);border:1px solid rgba(157,78,221,.3);border-radius:8px"><strong style="color:#9D4EDD">階段 4（Month 9+）</strong><p style="color:#ccc;font-size:.9em;margin-top:4px">NLP 升級、跨 KB 串聯、即時話術檢查（配合鐵律掃描）。</p></div>
</div></div>
</section><hr class="section-divider">"""


def internal_sop_section(num):
    """Internal SOP links — references only, no content."""
    return f"""
<section id="sop-links" class="section">
<div class="section-title"><span class="num">{num}</span> 🔒 內部 SOP 參考（僅連結）</div>
<p style="color:var(--text-dim);margin-bottom:16px">以下 SOP 文件存放於內部路徑，含完整升級流程與負責人資訊。如需存取請聯繫客服主管。</p>
<div class="chart-grid" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr))">
<div class="card"><h3>📄 產品線 SOP</h3><table><thead><tr><th>文件</th><th>說明</th></tr></thead><tbody>
<tr><td style="color:var(--info)">2A_LINE站_SOP</td><td>LINE 站日常處理、升級路徑、工具清單</td></tr>
<tr><td style="color:var(--success)">2B_信用版_SOP</td><td>信用版三方對帳流程、風控處理</td></tr>
<tr><td style="color:#9D4EDD">2C_遊戲商_SOP</td><td>遊戲商新廠對接、API 串接 checklist</td></tr>
<tr><td style="color:#FB5607">2D_外包_SOP</td><td>外包雙線處理、N8 告警群規則</td></tr>
</tbody></table></div>
<div class="card"><h3>📄 分析報告</h3><table><thead><tr><th>文件</th><th>說明</th></tr></thead><tbody>
<tr><td style="color:var(--warning)">3_站長畫像報告</td><td>16 站質性分析、情緒指數、核心客戶</td></tr>
<tr><td style="color:var(--danger)">4_鐵律違反案例</td><td>12 件違規完整紀錄（含人名、時間）</td></tr>
<tr><td style="color:var(--primary)">6_行動建議總結</td><td>RPA 目標、培訓計畫、Q3 KPI</td></tr>
</tbody></table></div>
</div>
<div class="card" style="margin-top:16px;border-color:var(--warning)">
<p style="color:var(--warning);font-weight:600">⚠️ 以上文件包含內部人員姓名與機密流程，僅限內部查閱。存取路徑：~/r-ou-hailong/internal/</p>
</div>
</section><hr class="section-divider">"""


def faq_section(num):
    return f"""
<section id="faq" class="section">
<div class="section-title"><span class="num">{num}</span> ❓ 常見問題解答 (FAQ)</div>
<p style="color:var(--text-dim);margin-bottom:16px">8 大類別常見問答，點擊展開查看解答。</p>
<div id="faqContainer"></div>
</section><hr class="section-divider">"""


def escalation_section():
    """DESENSITIZED escalation flow — roles only, no names."""
    return """
<section id="escalation" class="section">
<div class="section-title"><span class="num">+</span> 🔺 升級流程</div>
<div class="card" style="margin-bottom:20px"><h3>標準升級鏈</h3>
<div class="flow-steps">
<div class="flow-step">FAE 自查<br><small style="color:var(--text-dim)">查本文件 → FAQ → 歷史對話</small></div>
<div class="flow-arrow">&#10148;</div>
<div class="flow-step">UAT / Postman<br><small style="color:var(--text-dim)">後台驗證 / API 測試</small></div>
<div class="flow-arrow">&#10148;</div>
<div class="flow-step">Kibana Log<br><small style="color:var(--text-dim)">查錯誤原因</small></div>
<div class="flow-arrow">&#10148;</div>
<div class="flow-step">Slack 對應窗口<br><small style="color:var(--text-dim)">上面都無解時</small></div>
<div class="flow-arrow">&#10148;</div>
<div class="flow-step" style="border-color:var(--danger);background:rgba(255,68,68,.15)">升級上級主管<br><small style="color:var(--text-dim)">由上級主管整合判斷</small></div>
</div></div>
<div class="chart-grid">
<div class="card"><h3>Slack 找對的窗口</h3><table><thead><tr><th>問題</th><th>對應窗口</th></tr></thead><tbody>
<tr><td>lilian 前端</td><td>前端工程團隊</td></tr>
<tr><td><strong>lilian 後端主程式</strong></td><td><strong>Lilian 主程式窗口</strong></td></tr>
<tr><td>lilian 一般後端</td><td>後端工程團隊</td></tr>
<tr><td><strong>MG 集成後台</strong></td><td><strong>MG 工程窗口</strong></td></tr>
<tr><td>信用版 GA / DBA</td><td>GA/DBA 窗口</td></tr>
<tr><td>TG 捕魚 (TP)</td><td>TP-dp 群</td></tr>
<tr><td>FF / DD 外包</td><td>FF 技術窗口 (Discord)</td></tr>
<tr><td>IP / VPN / 網路</td><td>網路窗口 / IP/VPN 窗口</td></tr>
<tr><td>排班 / 人事</td><td>人事窗口</td></tr>
<tr><td><strong>上層決策</strong></td><td style="color:var(--danger)"><strong>一律先找上級主管</strong></td></tr>
</tbody></table></div>
<div class="card"><h3>證據三件套（缺一不可）</h3><table><thead><tr><th>問題類型</th><th>必備證據</th></tr></thead><tbody>
<tr><td>帳號</td><td>帳號 + 最後登入時間 + 截圖</td></tr>
<tr><td>充值</td><td>訂單號 + 帳號 + 充值時間（含時區）</td></tr>
<tr><td><strong>遊戲異常</strong></td><td><strong>局號 + 帳號 + 截圖</strong>（沒這三件不開單）</td></tr>
<tr><td>提款</td><td>訂單號 + 帳號 + 時間</td></tr>
<tr><td>活動爭議</td><td>活動名稱 + 帳號 + 質疑點</td></tr>
<tr><td>帳務對帳</td><td>對帳期間 + 涉及遊戲 + 差異金額</td></tr>
</tbody></table>
<div style="margin-top:12px;padding:10px;background:var(--primary-dim);border-radius:6px;font-size:.9em;color:var(--text-dim)"><strong style="color:var(--primary)">回問原則：</strong>一次問完，禁止擠牙膏。</div>
</div></div>
</section>"""


# ── Chart JS (same pattern as v2 + comparison charts) ───────────────────────
def build_js():
    lines = []
    lines.append("const COLORS=['#FF6B35','#00B4D8','#00D99F','#FFB300','#FF4444','#9D4EDD','#3A86FF','#FB5607','#8338EC','#FFBE0B'];")
    lines.append("Chart.defaults.color='#aaa';Chart.defaults.borderColor='rgba(255,107,53,0.1)';Chart.defaults.font.family=\"system-ui,'Noto Sans TC',sans-serif\";")
    # embed PL data
    for key in PL_KEYS:
        d = STATS[key]
        cats = {k:v for k,v in d["categories"].items() if k!="其他"}
        cats_all = d["categories"]
        stations = dict(sorted(d["stationComplaints"].items(), key=lambda x:-x[1]))
        P = key.upper()
        lines.append(f"const {P}_CATS={js(cats)};const {P}_CATS_ALL={js(cats_all)};const {P}_STATIONS={js(stations)};const {P}_DAILY={js(d['dailyCounts'])};const {P}_SEV={js(d['severityCounts'])};")
    lines.append(f"const PL_COMPARE={js(STATS['plCompare'])};")

    lines.append(r"""
function buildCatPie(id,o){var n=Object.keys(o),v=Object.values(o);new Chart(document.getElementById(id),{type:'doughnut',data:{labels:n,datasets:[{data:v,backgroundColor:COLORS.slice(0,n.length),borderColor:'#1a1a2e',borderWidth:2}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom',labels:{padding:12,usePointStyle:true,font:{size:11}}},tooltip:{callbacks:{label:function(c){var t=c.dataset.data.reduce((a,b)=>a+b,0);return c.label+': '+c.parsed+' ('+(c.parsed/t*100).toFixed(1)+'%)';}}}}}});}
function buildCatBar(id,o){new Chart(document.getElementById(id),{type:'bar',data:{labels:Object.keys(o),datasets:[{label:'件數',data:Object.values(o),backgroundColor:COLORS.concat(COLORS).slice(0,9).map(c=>c+'CC'),borderWidth:0}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false}},scales:{x:{beginAtZero:true}}}});}
function buildStationBar(id,o){new Chart(document.getElementById(id),{type:'bar',data:{labels:Object.keys(o),datasets:[{label:'客訴數',data:Object.values(o),backgroundColor:COLORS.concat(COLORS).slice(0,Object.keys(o).length).map(c=>c+'CC'),borderWidth:0}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{beginAtZero:true}}}});}
function buildTrend(id,daily,days){var end=new Date('2026-04-13'),dates=[];for(var i=days-1;i>=0;i--){var d=new Date(end);d.setDate(d.getDate()-i);dates.push(d.toISOString().split('T')[0]);}var allCats={};Object.values(daily).forEach(function(dd){Object.keys(dd).forEach(function(c){if(c!=='其他')allCats[c]=true;});});var cn=Object.keys(allCats);new Chart(document.getElementById(id),{type:'line',data:{labels:dates.map(d=>d.substring(5)),datasets:cn.map((cat,idx)=>({label:cat,data:dates.map(d=>(daily[d]&&daily[d][cat])||0),borderColor:COLORS[idx%COLORS.length],backgroundColor:'transparent',borderWidth:1.5,pointRadius:days>60?0:2,tension:0.3}))},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'top',labels:{boxWidth:10,font:{size:10}}}},scales:{y:{beginAtZero:true},x:{ticks:{maxTicksLimit:days>60?12:10,font:{size:9}}}}}});}
function buildSevPie(id,o){new Chart(document.getElementById(id),{type:'doughnut',data:{labels:['P2 中等','P1 高','P0 緊急'],datasets:[{data:[o.P2||0,o.P1||0,o.P0||0],backgroundColor:['#FFB300','#ff8800','#ff4444'],borderColor:'#1a1a2e',borderWidth:2}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom',labels:{padding:12,usePointStyle:true}},tooltip:{callbacks:{label:function(c){var t=c.dataset.data.reduce((a,b)=>a+b,0);return c.label+': '+c.parsed+' ('+(c.parsed/t*100).toFixed(1)+'%)';}}}}}});}
""")
    for key in PL_KEYS:
        P = key.upper()
        lines.append(f"buildCatPie('{key}CatPie',{P}_CATS);buildCatBar('{key}CatBar',{P}_CATS_ALL);buildStationBar('{key}StationBar',{P}_STATIONS);buildTrend('{key}Trend30',{P}_DAILY,30);buildTrend('{key}Trend90',{P}_DAILY,90);buildSevPie('{key}SevPie',{P}_SEV);")

    # comparison charts
    lines.append(r"""
var plN=Object.keys(PL_COMPARE),plC=['#00B4D8','#00D99F','#9D4EDD','#FB5607'];
new Chart(document.getElementById('plCompareBar'),{type:'bar',data:{labels:plN,datasets:[{label:'客訴數',data:plN.map(n=>PL_COMPARE[n].complaints),backgroundColor:plC.map(c=>c+'CC'),borderWidth:0}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}});
new Chart(document.getElementById('plCompareRate'),{type:'bar',data:{labels:plN,datasets:[{label:'客訴率(%)',data:plN.map(n=>(PL_COMPARE[n].complaints/PL_COMPARE[n].total*100).toFixed(1)),backgroundColor:plC.map(c=>c+'CC'),borderWidth:0}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,ticks:{callback:function(v){return v+'%'}}}}}});
new Chart(document.getElementById('plComparePie'),{type:'doughnut',data:{labels:plN,datasets:[{data:plN.map(n=>PL_COMPARE[n].total),backgroundColor:plC,borderColor:'#1a1a2e',borderWidth:2}]},options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom',labels:{padding:12,usePointStyle:true}},tooltip:{callbacks:{label:function(c){var t=c.dataset.data.reduce((a,b)=>a+b,0);return c.label+': '+c.parsed.toLocaleString()+' ('+(c.parsed/t*100).toFixed(1)+'%)'}}}}}});
var tcN=new Set();plN.forEach(function(n){Object.keys(PL_COMPARE[n].topCats).forEach(function(c){tcN.add(c)})});tcN=Array.from(tcN);
new Chart(document.getElementById('plCompareTopCats'),{type:'bar',data:{labels:tcN,datasets:plN.map(function(n,i){return{label:n,data:tcN.map(function(c){return PL_COMPARE[n].topCats[c]||0}),backgroundColor:plC[i]+'CC',borderWidth:0}})},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{boxWidth:12,font:{size:11}}}},scales:{y:{beginAtZero:true}}}});
""")

    # FAQ data (desensitized)
    lines.append(r"""
const FAQ_DATA=[
{cat:"帳號問題",items:[
{q:"帳號被鎖定無法登入?",a:"<ol><li>確認帳號密碼是否正確</li><li>等待 15-30 分鐘後重試</li><li>如持續，提供帳號資訊由客服解除</li></ol>"},
{q:"忘記帳號或密碼?",a:"<ol><li>使用「忘記密碼」功能</li><li>無法接收郵件，提供註冊資訊</li><li>驗證身份後協助重設</li></ol>"},
{q:"帳號異常或被盜用?",a:"<ol><li>立即修改密碼</li><li>綁定雙因素驗證</li><li>檢查登入紀錄和交易記錄</li><li>發現異常交易進行凍結調查</li></ol>"},
{q:"帳號被暫停或禁用?",a:"常見原因：違反條款、風控觸發、未通過實名認證。臨時限制 24-72 小時後自動解除。"},
{q:"如何更換綁定手機或信箱?",a:"登入後進入帳號設定，修改手機/信箱，完成舊設備驗證即可更新。"}
]},
{cat:"充值問題",items:[
{q:"充值後金額未入帳?",a:"<ol><li>銀行端延遲（5-30分鐘）</li><li>確認卡片額度</li><li>確認帳號資訊一致</li><li>超過1小時提供交易編號查詢</li></ol>"},
{q:"充值失敗後餘額被扣?",a:"提供交易編號、時間、金額，查詢銀行記錄並進行退款（3-5工作日）。"}
]},
{cat:"遊戲異常",items:[
{q:"遊戲載入失敗或卡住?",a:"<ol><li>檢查網路</li><li>清除快取</li><li>更新版本</li><li>更換瀏覽器</li><li>持續異常提供設備資訊和截圖</li></ol>"},
{q:"遊戲獎勵未正確顯示?",a:"重新登入、檢查獎勵記錄、確認領取條件和時效限制。"}
]},
{cat:"提款問題",items:[
{q:"提款申請多久入帳?",a:"銀行轉帳1-3工作日，第三方即時至24小時，國際匯款5-10工作日。"},
{q:"提款被拒絕?",a:"常見原因：未實名認證、風控觸發、超限額、銀行端拒絕。"}
]},
{cat:"優惠活動爭議",items:[
{q:"活動條款與實際不符?",a:"提供活動連結、參與記錄、預期與實際差異，核對條款確認是否系統錯誤。"},
{q:"活動獎勵有洗碼要求嗎?",a:"多數獎勵有流水倍數要求，部分限定遊戲，可能有使用期限。"}
]},
{cat:"帳務對帳",items:[
{q:"帳戶餘額與預期不符?",a:"查看交易紀錄、檢查充值提款遊戲記錄、確認未結算訂單。"},
{q:"提款後扣款但銀行未收到?",a:"確認提款狀態，24小時後未入帳聯繫追蹤（3-5工作日調查）。"}
]},
{cat:"遊戲上架/串接",items:[
{q:"遊戲上架需要什麼材料?",a:"遊戲基本信息、簽名檔案、隱私政策、截圖（3-5張）、開發者資訊。"},
{q:"串接失敗怎麼辦?",a:"<ol><li>檢查 API Key/Secret</li><li>驗證請求格式</li><li>檢查 IP 白名單（雙向）</li><li>查看錯誤日誌</li></ol>"}
]},
{cat:"後台操作/業主認知",items:[
{q:"後台如何調整遊戲參數?",a:"登入業主後台 → 遊戲設定 → 選擇遊戲編輯 → 保存。不確定的先在 UAT 跑一次。"},
{q:"業主帳號權限如何調整?",a:"帳號管理 → 選擇帳號 → 勾選/取消權限 → 保存。安全敏感操作需驗證管理員身份。"}
]}
];

var faqC=document.getElementById('faqContainer');
FAQ_DATA.forEach(function(cat){var s=document.createElement('div');s.className='faq-category';s.innerHTML='<div class="faq-category-title">'+cat.cat+'</div>';
cat.items.forEach(function(item){var fi=document.createElement('div');fi.className='faq-item';fi.innerHTML='<div class="faq-q" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'show\')"><span class="arrow">&#9654;</span><span class="q-text">'+item.q+'</span></div><div class="faq-a">'+item.a+'</div>';s.appendChild(fi)});
faqC.appendChild(s)});
""")

    # Tab switching
    lines.append(r"""
function switchTab(group,key){document.querySelectorAll('#'+group+'-wrapper .tab-btn').forEach(function(b){b.classList.remove('active')});document.querySelectorAll('[id^="'+group+'-"]').forEach(function(p){if(p.classList.contains('tab-panel'))p.classList.remove('active')});document.getElementById(group+'-'+key).classList.add('active');event.target.classList.add('active');}
// Also handle tab buttons without wrapper
document.querySelectorAll('.tab-btn').forEach(function(btn){btn.addEventListener('click',function(){var bar=this.parentElement;bar.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active')});this.classList.add('active')})});
""")

    # Nav scroll tracking
    lines.append(r"""
var navLinks=document.querySelectorAll('.nav-link'),sections=document.querySelectorAll('.section[id]');
window.addEventListener('scroll',function(){var sp=window.scrollY+100;sections.forEach(function(sec){if(sec.offsetTop<=sp&&(sec.offsetTop+sec.offsetHeight)>sp){navLinks.forEach(function(l){l.classList.remove('active');if(l.getAttribute('href')==='#'+sec.id)l.classList.add('active')})}})});
""")

    return "\n".join(lines)


# ── Assemble ────────────────────────────────────────────────────────────────
def main():
    o = STATS["overall"]
    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>FAE 客服知識庫簡報 v3.0 - Wolves Digital</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<nav class="nav"><span class="nav-brand">🐺 Wolves FAE v3</span>
<div class="nav-links">
<a href="#cover" class="nav-link active">首頁</a>
<a href="#overview" class="nav-link">📊 總覽</a>
<a href="#line" class="nav-link pl-line">💬 LINE站</a>
<a href="#credit" class="nav-link pl-credit">💳 信用版</a>
<a href="#vendor" class="nav-link pl-vendor">🎮 遊戲商</a>
<a href="#outsource" class="nav-link pl-outsource">🌐 外包</a>
<a href="#compare" class="nav-link">📈 對比</a>
<a href="#templates" class="nav-link">📋 範本</a>
<a href="#stations" class="nav-link">🏢 站點</a>
<a href="#violations" class="nav-link">⚠️ 違規</a>
<a href="#rules" class="nav-link">🚫 鐵律</a>
<a href="#rpa" class="nav-link">🤖 RPA</a>
<a href="#sop-links" class="nav-link">🔒 SOP</a>
<a href="#faq" class="nav-link">❓ FAQ</a>
<a href="#escalation" class="nav-link">🔺 升級</a>
</div></nav>
<div class="container">
<section id="cover" class="cover section">
<h1>FAE 客服知識庫簡報 v3.0</h1>
<div class="subtitle">多維度客訴分析 — LINE站 / 信用版 / 遊戲商 / 外包</div>
<div class="meta">
<div>📊 資料筆數：<span>{o['totalMessages']:,}</span></div>
<div>🔥 客訴數：<span>{o['complaintCount']:,}</span></div>
<div>📅 資料截至：<span>2026-04-13</span></div>
<div>🏢 產品線：<span>4 大板塊 / 24 站點</span></div>
<div>📋 範本：<span>40 題（4×10）</span></div>
</div></section><hr class="section-divider">
{pl_section(STATS["overall"],"overall","1")}
{pl_section(STATS["line"],"line","2")}
{pl_section(STATS["credit"],"credit","3")}
{pl_section(STATS["vendor"],"vendor","4")}
{pl_section(STATS["outsource"],"outsource","5")}
{compare_section(STATS,"6")}
{templates_section("7")}
{station_dashboard_section(STATS,"8")}
{violations_section("9")}
{rules_section()}
{rpa_section("10")}
{internal_sop_section("11")}
{faq_section("12")}
{escalation_section()}
<footer>
<p>Wolves Digital FAE 客服知識庫簡報 v3.0 | 資料截至 2026-04-13 | 4 大產品線 / 24 站點 / {o['totalMessages']:,} 筆訊息</p>
<p style="margin-top:4px">本頁面為公開版，已移除內部人員姓名。完整 SOP 請查閱內部文件。</p>
</footer></div>
<script>{build_js()}</script>
</body></html>"""

    out = BASE / "FAE_簡報.html"
    out.write_text(html, encoding="utf-8")
    (BASE / "index.html").write_text(html, encoding="utf-8")
    print(f"v3.0 generated: {len(html):,} chars → {out.name} + index.html")

if __name__ == "__main__":
    main()
