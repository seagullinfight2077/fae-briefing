#!/usr/bin/env python3
"""Generate multi-dimensional FAE briefing HTML from all_stats.json."""

import json
import html as htmlmod
from pathlib import Path

BASE_DIR = Path(__file__).parent
STATS_FILE = BASE_DIR / "all_stats.json"
OUTPUT_FILE = BASE_DIR / "FAE_簡報.html"
INDEX_FILE = BASE_DIR / "index.html"

COLORS_JS = "['#FF6B35','#00B4D8','#00D99F','#FFB300','#FF4444','#9D4EDD','#3A86FF','#FB5607','#8338EC','#FFBE0B']"

PL_META = {
    "overall": {"icon": "📊", "color": "#FF6B35", "title": "整體總覽"},
    "line":    {"icon": "💬", "color": "#00B4D8", "title": "LINE站"},
    "credit":  {"icon": "💳", "color": "#00D99F", "title": "信用版"},
    "vendor":  {"icon": "🎮", "color": "#9D4EDD", "title": "遊戲商"},
    "outsource": {"icon": "🌐", "color": "#FB5607", "title": "外包"},
}

PL_COMPARE_COLORS = {
    "LINE站": "#00B4D8",
    "信用版": "#00D99F",
    "遊戲商": "#9D4EDD",
    "外包":   "#FB5607",
}


def load_stats():
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def js_obj(d):
    """Convert a Python dict to a JS object literal string."""
    return json.dumps(d, ensure_ascii=False)


# ─── CSS ────────────────────────────────────────────────────────────────────
CSS = r"""
:root {
    --primary: #FF6B35;
    --primary-light: rgba(255, 107, 53, 0.15);
    --primary-dim: rgba(255, 107, 53, 0.08);
    --bg-dark: #1a1a2e;
    --bg-card: rgba(30, 40, 60, 0.85);
    --text: #e8e8e8;
    --text-dim: #aaa;
    --border: rgba(255, 107, 53, 0.2);
    --success: #00D99F;
    --warning: #FFB300;
    --danger: #ff4444;
    --info: #00B4D8;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: system-ui, 'Noto Sans TC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.6;
}

/* Navigation */
.nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
    background: rgba(26, 26, 46, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 2px solid var(--primary);
    padding: 0 20px;
    display: flex; align-items: center; height: 56px;
}
.nav-brand { font-weight: 700; font-size: 1.1em; color: var(--primary); margin-right: 30px; white-space: nowrap; }
.nav-links { display: flex; gap: 4px; overflow-x: auto; scrollbar-width: none; }
.nav-links::-webkit-scrollbar { display: none; }
.nav-link {
    padding: 8px 16px; color: var(--text-dim); text-decoration: none;
    border-radius: 6px; font-size: 0.9em; white-space: nowrap; transition: all 0.2s;
}
.nav-link:hover, .nav-link.active { color: #fff; background: var(--primary-light); }
.nav-link.pl-line { border-left: 3px solid #00B4D8; }
.nav-link.pl-credit { border-left: 3px solid #00D99F; }
.nav-link.pl-vendor { border-left: 3px solid #9D4EDD; }
.nav-link.pl-outsource { border-left: 3px solid #FB5607; }

/* Container */
.container { max-width: 1400px; margin: 0 auto; padding: 76px 24px 40px; }

/* Cover */
.cover { text-align: center; padding: 60px 20px; margin-bottom: 40px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; }
.cover h1 { font-size: 2.8em; color: #fff; margin-bottom: 12px; text-shadow: 0 2px 20px rgba(255, 107, 53, 0.3); }
.cover .subtitle { font-size: 1.3em; color: var(--primary); margin-bottom: 20px; }
.cover .meta { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; color: var(--text-dim); font-size: 0.95em; }
.cover .meta span { color: var(--primary); font-weight: 600; }

/* Sections */
.section { margin-bottom: 40px; scroll-margin-top: 70px; }
.section-title {
    display: flex; align-items: center; gap: 12px;
    font-size: 1.6em; color: #fff;
    margin-bottom: 20px; padding-bottom: 12px;
    border-bottom: 2px solid var(--primary);
}
.section-title .num {
    background: var(--primary); color: var(--bg-dark);
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7em; font-weight: 700; flex-shrink: 0;
}

/* PL colored section titles */
.section-title.pl-line { border-bottom-color: #00B4D8; }
.section-title.pl-line .num { background: #00B4D8; }
.section-title.pl-credit { border-bottom-color: #00D99F; }
.section-title.pl-credit .num { background: #00D99F; }
.section-title.pl-vendor { border-bottom-color: #9D4EDD; }
.section-title.pl-vendor .num { background: #9D4EDD; }
.section-title.pl-outsource { border-bottom-color: #FB5607; }
.section-title.pl-outsource .num { background: #FB5607; }

/* Cards */
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 24px; backdrop-filter: blur(10px); transition: all 0.3s; }
.card:hover { border-color: var(--primary); box-shadow: 0 8px 30px rgba(255, 107, 53, 0.15); }
.card h3 { color: var(--primary); margin-bottom: 12px; font-size: 1.15em; }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; text-align: center; }
.stat-card .label { color: var(--text-dim); font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.stat-card .number { font-size: 2.2em; font-weight: 700; color: var(--primary); line-height: 1.1; }
.stat-card .detail { color: var(--text-dim); font-size: 0.85em; margin-top: 4px; }

/* Chart Layout */
.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 20px; margin-bottom: 24px; }
.chart-box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; position: relative; }
.chart-box h3 { color: #fff; margin-bottom: 12px; font-size: 1.05em; }
.chart-wrap { position: relative; height: 350px; }
.chart-wrap-sm { position: relative; height: 300px; }
.chart-wrap-lg { position: relative; height: 450px; }

/* Top items */
.issue-list { list-style: none; }
.issue-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; margin-bottom: 6px; background: var(--primary-dim); border-left: 3px solid var(--primary); border-radius: 6px; transition: all 0.2s; }
.issue-item:hover { background: var(--primary-light); transform: translateX(4px); }
.issue-rank { font-weight: 700; color: var(--primary); font-size: 1.1em; min-width: 28px; }
.issue-name { flex: 1; color: #ddd; font-size: 0.95em; }
.issue-count { background: var(--primary); color: var(--bg-dark); padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85em; }

/* Tables */
table { width: 100%; border-collapse: collapse; }
thead { background: var(--primary-light); }
th { padding: 14px 16px; text-align: left; color: var(--primary); font-weight: 600; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid var(--primary); }
td { padding: 12px 16px; border-bottom: 1px solid var(--border); color: #ddd; font-size: 0.93em; }
tbody tr:hover { background: var(--primary-dim); }

/* Badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 4px; font-weight: 600; font-size: 0.82em; }
.badge-danger { background: var(--danger); color: #fff; }
.badge-warning { background: var(--warning); color: #000; }
.badge-info { background: var(--info); color: #fff; }
.badge-success { background: var(--success); color: #000; }
.badge-primary { background: var(--primary); color: var(--bg-dark); }

/* Template Cards */
.template-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
.template-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.template-header { background: var(--primary-light); padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
.template-num { background: var(--primary); color: var(--bg-dark); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9em; flex-shrink: 0; }
.template-title { color: #fff; font-weight: 600; font-size: 1.05em; }
.template-body { padding: 20px; }
.template-section { margin-bottom: 14px; }
.template-section:last-child { margin-bottom: 0; }
.template-label { color: var(--primary); font-weight: 600; font-size: 0.85em; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }
.template-content { background: rgba(0, 0, 0, 0.2); border-radius: 6px; padding: 12px 16px; font-size: 0.92em; line-height: 1.7; color: #ccc; border-left: 3px solid var(--primary); }
.template-warning { background: rgba(255, 68, 68, 0.1); border: 1px solid rgba(255, 68, 68, 0.3); border-radius: 6px; padding: 10px 14px; font-size: 0.88em; color: #ff8888; }

/* FAQ Section */
.faq-category { margin-bottom: 24px; }
.faq-category-title { color: var(--primary); font-size: 1.2em; margin-bottom: 12px; padding: 8px 16px; background: var(--primary-dim); border-radius: 6px; border-left: 4px solid var(--primary); }
.faq-item { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 10px; overflow: hidden; }
.faq-q { padding: 14px 18px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s; user-select: none; }
.faq-q:hover { background: var(--primary-dim); }
.faq-q .arrow { color: var(--primary); transition: transform 0.3s; font-size: 0.8em; }
.faq-q.open .arrow { transform: rotate(90deg); }
.faq-q .q-text { font-weight: 600; color: #fff; flex: 1; }
.faq-a { display: none; padding: 0 18px 16px; color: #ccc; font-size: 0.93em; line-height: 1.7; border-top: 1px solid var(--border); }
.faq-a.show { display: block; padding-top: 14px; }
.faq-a ol, .faq-a ul { margin-left: 20px; margin-top: 6px; }
.faq-a li { margin-bottom: 4px; }

/* Key Rules Box */
.rules-box { background: rgba(255, 68, 68, 0.08); border: 1px solid rgba(255, 68, 68, 0.3); border-radius: 10px; padding: 24px; margin-bottom: 24px; }
.rules-box h3 { color: var(--danger); margin-bottom: 14px; font-size: 1.15em; }
.rules-box ol { margin-left: 20px; color: #ddd; }
.rules-box li { margin-bottom: 8px; line-height: 1.6; }
.rules-box strong { color: #ff8888; }

/* Escalation Flow */
.flow-steps { display: flex; align-items: center; gap: 0; flex-wrap: wrap; justify-content: center; margin: 20px 0; }
.flow-step { background: var(--primary-light); border: 1px solid var(--primary); border-radius: 8px; padding: 14px 18px; text-align: center; font-size: 0.95em; font-weight: 600; }
.flow-arrow { font-size: 1.5em; color: var(--primary); padding: 0 6px; }

/* Product-line comparison cards */
.pl-comparison-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
.pl-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; border-top: 4px solid var(--primary); }
.pl-card h4 { font-size: 1.15em; margin-bottom: 12px; }
.pl-card .pl-stat { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--border); font-size: 0.93em; }
.pl-card .pl-stat:last-child { border-bottom: none; }
.pl-card .pl-stat .val { font-weight: 700; }

/* Section divider */
.section-divider { border: none; border-top: 1px solid var(--border); margin: 50px 0 40px; }

footer { text-align: center; padding: 30px; color: var(--text-dim); font-size: 0.85em; border-top: 1px solid var(--border); margin-top: 40px; }

@media (max-width: 768px) {
    .chart-grid { grid-template-columns: 1fr; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .template-grid { grid-template-columns: 1fr; }
    .pl-comparison-grid { grid-template-columns: 1fr; }
    .cover h1 { font-size: 1.8em; }
}
"""


# ─── TEMPLATES & FAQ DATA (carried over from original) ──────────────────────
TEMPLATES_JS = r"""
const TEMPLATES = [
    {
        title: "後台設定問題",
        desc: "站長/業主對後台參數設定不熟悉，如活動設定、遊戲參數調整、權限管理等。",
        reply: "請稍等，立即為您查詢中\n\n關於後台設定，麻煩提供：\n1. 您要操作的功能名稱\n2. 目前看到的畫面截圖\n3. 您期望的設定結果\n\n收到後我們會核對設定方式，確認後同步操作步驟給您。如有需要，也可以在 UAT 環境先跑一次確認。",
        warning: "不憑記憶答後台操作，一律先查後台手冊或 UAT 驗證。站長說「之前都這樣」需確認哪個版本/哪個站，多為版本差異。活動規則變更需找 PM 阿丹，FAE 不可自決。"
    },
    {
        title: "遊戲上架 / ICON 問題",
        desc: "遊戲上架審核進度、ICON 素材缺失或錯誤、上架後顯示異常等。",
        reply: "請稍等，立即為您查詢中\n\n遊戲上架進度我們正在確認，為了加速處理，麻煩確認：\n1. 遊戲名稱及遊戲商\n2. 預期上架時間\n3. 是否已提供完整 ICON 素材\n\n收到後我們會檢查 MG 後台上架狀態，有進度第一時間同步。",
        warning: "ICON 素材先查 Google Drive，沒有再找遊戲商。上線前必須通過 4 項檢查：語系、賠率限紅、注單回傳、可下注。巴西 M03 案例 3000 張 ICON 耗時 80 小時，為 RPA 首要攻破點。"
    },
    {
        title: "活動領取失敗",
        desc: "玩家參加活動後獎勵未發放、領取條件不明、活動條款與實際不符等。",
        reply: "請稍等，立即為您查詢中\n\n為了快速定位活動問題，麻煩提供：\n1. 活動名稱或活動頁面連結\n2. 受影響的玩家帳號\n3. 具體的質疑點（預期 vs 實際獲得）\n\n收到後我們會核對活動條款和玩家行為紀錄，確認後同步結果給您。",
        warning: "以條款為準，只引用不解釋。站長要改活動規則需找 PM 阿丹。禁止說「保證補發」「一定能領」。確認為系統錯誤才進行補發。"
    },
    {
        title: "金流通道問題",
        desc: "充值未入帳、金流通道關閉、USDT 鏈別錯誤、退款處理等。",
        reply: "請稍等，立即為您查詢中\n\n為了精準定位金流問題，麻煩提供：\n1. 訂單號\n2. 充值帳號\n3. 充值時間（含時區）\n\n收到後我們會核對訂單狀態，確認後同步處理進度給您。",
        warning: "金流判斷四步驟必跑：(1) 訂單在我方有沒有 (2) 收到金流商 callback 沒 (3) 金流商後台狀態 (4) 金額/鏈別/通道匹配。跑完才找當班幹部 → Robin 確認。通道整個關閉需通知所有站長。"
    },
    {
        title: "維護 / 更新通知",
        desc: "系統維護時間確認、更新後異常、維護延長等。",
        reply: "請稍等，立即為您查詢中\n\n目前相關維護/更新狀況我們正在跟相關單位確認，有進度第一時間同步給您。\n\n如維護期間有緊急問題，請隨時告知，我們會優先處理。",
        warning: "維護時間不能給精確數字（除非 100% 確定）。禁止說「預計 30 分鐘」「馬上好」。用進度承諾：「有進度第一時間同步」。"
    },
    {
        title: "公會 / 代理設定",
        desc: "公會建立、代理佣金設定、代理架構調整、層級權限問題。",
        reply: "請稍等，立即為您查詢中\n\n關於公會/代理設定，麻煩提供：\n1. 需要調整的功能（公會設立/佣金比例/層級調整）\n2. 目前後台的截圖\n3. 期望的設定結果\n\n收到後我們會確認設定方式，有結果立即回覆。",
        warning: "涉及佣金調整需確認業主授權層級。不同站台版本可能設定方式不同，先確認版本再回答。"
    },
    {
        title: "首儲 / 續儲優惠設定",
        desc: "首儲優惠門檻設定、續儲贈送比例、活動疊加規則等。",
        reply: "請稍等，立即為您查詢中\n\n為了確認優惠設定，麻煩提供：\n1. 活動類型（首儲/續儲/其他）\n2. 目前的設定截圖\n3. 期望調整的內容\n\n收到後我們會在 UAT 先驗證設定邏輯，確認無誤後同步操作方式給您。",
        warning: "優惠設定先在 UAT 跑一次驗證，不能直接在 PROD 操作。活動規則修改權限在 PM 阿丹，FAE 不可自行決定。"
    },
    {
        title: "注單未回傳",
        desc: "遊戲結束後注單未顯示、遊戲商注單與平台不一致、補單需求等。",
        reply: "請稍等，立即為您查詢中\n\n為了快速定位注單問題，麻煩提供：\n1. 局號\n2. 玩家帳號\n3. 遊戲名稱及錯誤截圖\n\n收到後我們會查詢 MG 後台及遊戲商注單紀錄，確認後同步處理結果。",
        warning: "注單三件套缺一不開單：局號 + 帳號 + 截圖。多人同時注單未回傳 = 比照 S 級 + 立刻電話 Robin。注單未回傳需雙線查：工程 + 遊戲商。禁止跳過三邊比對直接補單。"
    },
    {
        title: "串接 API 問題",
        desc: "API 認證失敗、請求格式錯誤、IP 白名單問題、callback 未收到等。",
        reply: "請稍等，立即為您查詢中\n\n為了診斷 API 串接問題，麻煩提供：\n1. API 端點及請求方式\n2. 錯誤代碼或回應訊息\n3. 您方的 IP 地址（確認白名單）\n\n收到後我們會檢查 API 設定及 log，有結果第一時間回覆。",
        warning: "先確認 API Key / Secret 是否正確、IP 白名單是否已加（雙向）。callback 沒進需查對應金流商。IP/VPN/網路問題找 alex / RayLin。"
    },
    {
        title: "遊戲進不去 / 閃退",
        desc: "遊戲載入失敗、遊戲中閃退或崩潰、特定遊戲無法啟動等。",
        reply: "請稍等，立即為您查詢中\n\n遊戲異常問題，麻煩先確認：\n1. 受影響的遊戲名稱\n2. 玩家帳號（2-3 個樣本）\n3. 發生時間及錯誤截圖\n\n收到後我們會查詢遊戲狀態，有進度立即同步。\n\n同時建議先嘗試：清除快取重新登入、更換瀏覽器、確認網路穩定。",
        warning: "先區分是客端問題還是伺服器問題。5 分鐘內多人同遊戲異常 = S 級。記錄用戶設備環境（系統/版本/型號）。自家後台先自查再回應。"
    }
];
"""

FAQ_JS = r"""
const FAQ_DATA = [
    { cat: "帳號問題", items: [
        { q: "帳號被鎖定無法登入，該怎麼辦?", a: "帳號被鎖定通常是因為登入失敗次數過多或觸發安全機制。建議：<ol><li>確認輸入的帳號及密碼是否正確</li><li>等待 15-30 分鐘後重新嘗試</li><li>如問題持續，提供帳號資訊由客服進行解除</li></ol>" },
        { q: "忘記帳號或密碼，如何重設?", a: "提供以下重設方式：<ol><li>使用「忘記密碼」功能，系統將寄送重設連結至註冊信箱或綁定手機</li><li>如無法接收郵件，提供註冊時的相關資訊（真名、身份驗證碼等）</li><li>驗證身份後協助重設密碼</li></ol>" },
        { q: "帳號顯示異常或被盜用?", a: "安全處理步驟：<ol><li>立即修改密碼（含大小寫字母、數字、符號）</li><li>綁定雙因素驗證</li><li>檢查最近的登入紀錄和交易記錄</li><li>如發現異常交易，將進行凍結及調查</li></ol>" },
        { q: "帳號被暫停或禁用?", a: "常見原因：<ol><li>違反服務條款（如重複洗碼、異常行為）</li><li>風控機制觸發的臨時限制</li><li>未通過實名認證</li></ol>臨時限制通常 24-72 小時後自動解除；永久禁用需經理級審查。" },
        { q: "如何更換綁定的手機或信箱?", a: "在帳戶設定中更新：<ol><li>登入後進入「帳號設定」</li><li>點選「修改手機」或「修改信箱」</li><li>系統寄送驗證碼到原手機或信箱，完成驗證即可更新</li></ol>" }
    ]},
    { cat: "充值問題", items: [
        { q: "充值後金額未入帳?", a: "可能原因：<ol><li><strong>銀行端延遲</strong> - 通常 5-30 分鐘內會入帳</li><li><strong>銀行卡額度不足</strong> - 確認卡片額度</li><li><strong>帳號資訊不符</strong> - 確保帳號與銀行卡資訊一致</li><li>超過 1 小時未入帳，提供交易編號進行查詢</li></ol>" },
        { q: "充值失敗後餘額被扣?", a: "處理方式：<ol><li>提供交易編號、充值時間、金額</li><li>提供銀行帳戶資訊（最後 4 碼）</li><li>查詢銀行交易記錄並進行退款</li></ol>通常退款需要 3-5 個工作日。" }
    ]},
    { cat: "遊戲異常", items: [
        { q: "遊戲載入失敗或卡住?", a: "解決步驟：<ol><li>檢查網路連線是否穩定</li><li>清除瀏覽器或應用快取</li><li>更新到最新版本</li><li>更換瀏覽器嘗試</li><li>如持續異常，提供設備資訊和錯誤截圖</li></ol>" },
        { q: "遊戲獎勵或積分未正確顯示?", a: "排查步驟：<ol><li>重新登出再登入</li><li>檢查獎勵記錄頁面</li><li>確認是否達成領取條件</li><li>確認是否有時效限制</li></ol>確認遺漏後會手動補發。" }
    ]},
    { cat: "提款問題", items: [
        { q: "提款申請多久會入帳?", a: "取決於方式：<ol><li><strong>銀行轉帳</strong> - 通常 1-3 個工作日</li><li><strong>第三方支付</strong> - 即時至 24 小時</li><li><strong>國際匯款</strong> - 5-10 個工作日</li></ol>超過預期時間需要銀行端追蹤。" },
        { q: "提款被拒絕?", a: "常見原因：<ol><li>帳號未完成實名認證</li><li>安全檢查或風控觸發</li><li>超過每日/月提款限額</li><li>銀行端拒絕</li><li>未達提款條件</li></ol>" }
    ]},
    { cat: "優惠活動爭議", items: [
        { q: "活動條款與實際獎勵不符?", a: "解決流程：<ol><li>提供活動連結或名稱</li><li>提供參與記錄（時間、金額）</li><li>說明預期與實際差異</li><li>核對活動條款確認是否有系統錯誤</li></ol>確認為平台錯誤才進行補發。" },
        { q: "活動獎勵有洗碼要求嗎?", a: "使用限制：<ol><li>大多數獎勵有流水倍數要求（如 5 倍）</li><li>某些獎勵限定特定遊戲</li><li>部分不可與其他優惠疊加</li><li>獎勵可能有使用期限</li></ol>" }
    ]},
    { cat: "帳務對帳", items: [
        { q: "帳戶餘額與預期不符?", a: "查詢流程：<ol><li>查看「交易紀錄」或「帳務明細」</li><li>檢查近期充值、提款、遊戲輸贏記錄</li><li>確認是否有未結算訂單或未領取獎勵</li><li>進行完整帳務核對</li></ol>" },
        { q: "提款後帳戶扣款但銀行未收到?", a: "處理方式：<ol><li>確認提款申請狀態</li><li>檢查銀行帳戶（可能延遲）</li><li>24 小時後未入帳，聯繫追蹤</li><li>需要 3-5 個工作日完成調查</li></ol>" }
    ]},
    { cat: "遊戲上架/串接", items: [
        { q: "遊戲上架需要什麼材料?", a: "基本材料：<ol><li>遊戲基本信息（名稱、版本號）</li><li>遊戲檔案（簽名版本）</li><li>隱私政策和服務條款</li><li>遊戲截圖（至少 3-5 張）</li><li>開發者資訊</li></ol>" },
        { q: "串接失敗怎麼辦?", a: "診斷步驟：<ol><li>檢查 API Key / Secret 配置</li><li>驗證請求格式是否符合文檔</li><li>檢查 IP 白名單（雙向）</li><li>查看錯誤日誌</li><li>提供錯誤代碼可加速排查</li></ol>" }
    ]},
    { cat: "後台操作/業主認知", items: [
        { q: "後台如何調整遊戲參數?", a: "標準流程：<ol><li>登入業主後台（需管理員權限）</li><li>進入「遊戲設定」或「遊戲參數」</li><li>選擇遊戲，編輯參數</li><li>保存並確認變更已應用</li></ol>不確定的設定先在 UAT 環境跑一次。" },
        { q: "業主帳號權限如何調整?", a: "管理步驟：<ol><li>進入「帳號管理」或「權限設定」</li><li>選擇要編輯的帳號</li><li>勾選/取消權限</li><li>保存變更</li></ol>涉及安全敏感操作需驗證管理員身份。" }
    ]}
];
"""

VIOLATIONS_JS = r"""
const VIOLATIONS = [
    {type:"禁用詞「一定」",station:"L13_第一名",from:"Dan",date:"2026-01-16",text:"可以玩這活動的玩家一定是有儲值的"},
    {type:"時間承諾",station:"信用版_QA",from:"Gao Firball741",date:"2026-01-25",text:"更新至6點數據 約5分鐘"},
    {type:"禁用詞「一定」",station:"A95_九五至尊",from:"Firball02",date:"2026-01-28",text:"不代表轉一定有倍數及分數"},
    {type:"時間承諾",station:"信用版_QA",from:"Firball02",date:"2026-02-10",text:"本次維護預計時長半小時"},
    {type:"禁用詞「一定」",station:"信用版_QA",from:"Gao Firball741",date:"2026-04-01",text:"開放時間不一定，要等廠商回覆"},
    {type:"禁用詞「一定」",station:"K88_金五吉",from:"Gao Firball741",date:"2026-04-01",text:"一定要點擊參加才會開始計算"},
    {type:"時間承諾",station:"信用版_FT",from:"Gao Firball741",date:"2026-01-12",text:"預計影響30分鐘"},
    {type:"時間承諾",station:"L06_主管群",from:"Firball02",date:"2026-03-05",text:"預計半小時左右可更新完成"},
    {type:"時間承諾",station:"L06_吉滿滿",from:"Gao Firball741",date:"2026-02-11",text:"更新需要10分鐘"},
    {type:"禁用詞「一定」",station:"L09_伍洲",from:"Dan",date:"2026-03-16",text:"一定需要設定白名單才可以訪問"},
    {type:"時間承諾",station:"L04_大頭仔",from:"Gao Firball741",date:"2026-02-04",text:"目前排程最快就是1分鐘"},
    {type:"時間承諾",station:"JIN_錢老爺",from:"Gao Firball741",date:"2026-03-19",text:"已完成 1分鐘後刷新生效"}
];
"""


# ─── HTML Section Builders ─────────────────────────────────────────────────
def build_kpi_cards(data, pl_key):
    """Build KPI stat cards for a product line."""
    total = data["totalMessages"]
    complaints = data["complaintCount"]
    noise = data["noiseRatio"]
    cats = data["categories"]
    cat_no_other = {k: v for k, v in cats.items() if k != "其他"}
    top_cat = max(cat_no_other, key=cat_no_other.get) if cat_no_other else "N/A"
    stations = data["stationComplaints"]
    station_count = len(stations)
    sev = data["severityCounts"]
    complaint_rate = round(complaints / total * 100, 1) if total > 0 else 0

    return f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="label">總訊息量</div>
            <div class="number">{total:,}</div>
            <div class="detail">含有效 + 噪音</div>
        </div>
        <div class="stat-card">
            <div class="label">客訴數</div>
            <div class="number" style="color: var(--danger);">{complaints:,}</div>
            <div class="detail">佔比 {complaint_rate}%</div>
        </div>
        <div class="stat-card">
            <div class="label">站點數</div>
            <div class="number" style="color: var(--info);">{station_count}</div>
            <div class="detail">個獨立站點/群</div>
        </div>
        <div class="stat-card">
            <div class="label">噪音比</div>
            <div class="number" style="color: var(--warning);">{noise}%</div>
            <div class="detail">系統/閒聊訊息</div>
        </div>
        <div class="stat-card">
            <div class="label">最大類別</div>
            <div class="number" style="font-size:1.4em;">{top_cat}</div>
            <div class="detail">{cat_no_other.get(top_cat, 0):,} 筆</div>
        </div>
        <div class="stat-card">
            <div class="label">P0 緊急</div>
            <div class="number" style="color: var(--danger);">{sev.get('P0', 0)}</div>
            <div class="detail">P1: {sev.get('P1', 0)} / P2: {sev.get('P2', 0)}</div>
        </div>
    </div>
    """


def build_pl_section(data, pl_key, section_num):
    """Build a complete product-line analysis section."""
    meta = PL_META[pl_key]
    css_class = f"pl-{pl_key}" if pl_key != "overall" else ""
    icon = meta["icon"]
    title = meta["title"]

    cats = data["categories"]
    cat_no_other = {k: v for k, v in cats.items() if k != "其他"}
    stations = data["stationComplaints"]
    daily = data["dailyCounts"]
    severity = data["severityCounts"]

    # Top categories for text description
    sorted_cats = sorted(cat_no_other.items(), key=lambda x: -x[1])[:5]
    top_cats_text = "、".join(f"{k}({v})" for k, v in sorted_cats)

    # Sorted stations
    sorted_stations = sorted(stations.items(), key=lambda x: -x[1])
    top_stations_text = "、".join(f"{k}({v})" for k, v in sorted_stations[:5])

    # Station height
    station_count = len(sorted_stations)
    station_chart_h = max(300, station_count * 35)

    # Section ID
    section_id = pl_key if pl_key != "overall" else "overview"

    kpi_html = build_kpi_cards(data, pl_key)

    # Category description card
    if pl_key == "overall":
        cat_desc = f"全產品線共 {data['totalMessages']:,} 則訊息，其中 {data['complaintCount']:,} 則為客訴相關。前五大類別：{top_cats_text}。"
    elif pl_key == "line":
        cat_desc = f"LINE站為核心產品線，涵蓋 14 個站點。帳號問題居首（{cat_no_other.get('帳號問題', 0)}），其次為優惠活動爭議（{cat_no_other.get('優惠活動爭議', 0)}）。"
    elif pl_key == "credit":
        cat_desc = f"信用版包含 QA 及 FT 兩站，帳務對帳為特色問題（{cat_no_other.get('帳務對帳', 0)}），反映信用版業務性質。P1 高嚴重度比例偏高（{severity.get('P1', 0)}）。"
    elif pl_key == "vendor":
        cat_desc = f"遊戲商包含 TP 捕魚、XG Super、UGS 捕魚。遊戲異常為首要問題（{cat_no_other.get('遊戲異常', 0)}），噪音比最低（{data['noiseRatio']}%），問題品質高。"
    elif pl_key == "outsource":
        cat_desc = f"外包涵蓋 N8 印度站（最大量）、FF 外包技術、巨星等 5 站。N8 印度站客訴量 {stations.get('N8_印度站', 0)} 為全公司單站最高，需重點關注。"
    else:
        cat_desc = ""

    return f"""
    <section id="{section_id}" class="section">
        <div class="section-title {css_class}"><span class="num">{section_num}</span> {icon} {title} — 客訴分析</div>

        {kpi_html}

        <div class="chart-grid">
            <div class="chart-box">
                <h3>客訴類別佔比（排除「其他」）</h3>
                <div class="chart-wrap"><canvas id="{pl_key}CatPie"></canvas></div>
            </div>
            <div class="chart-box">
                <h3>各類別絕對數量</h3>
                <div class="chart-wrap"><canvas id="{pl_key}CatBar"></canvas></div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 24px;">
            <h3>分析摘要</h3>
            <p style="color:#ccc;line-height:1.7;">{cat_desc}</p>
            <p style="color:var(--text-dim);margin-top:8px;font-size:0.9em;">Top 5 站點：{top_stations_text}</p>
        </div>

        <div class="chart-grid">
            <div class="chart-box">
                <h3>近 30 日趨勢</h3>
                <div class="chart-wrap"><canvas id="{pl_key}Trend30"></canvas></div>
            </div>
            <div class="chart-box">
                <h3>近 90 日趨勢</h3>
                <div class="chart-wrap"><canvas id="{pl_key}Trend90"></canvas></div>
            </div>
        </div>

        <div class="chart-box" style="margin-bottom: 24px;">
            <h3>站點客訴熱度排行</h3>
            <div style="position:relative;height:{station_chart_h}px;"><canvas id="{pl_key}StationBar"></canvas></div>
        </div>

        <div class="chart-grid">
            <div class="chart-box">
                <h3>嚴重度分布</h3>
                <div class="chart-wrap"><canvas id="{pl_key}SevPie"></canvas></div>
            </div>
            <div class="card">
                <h3>嚴重度對應處理原則</h3>
                <table>
                    <thead><tr><th>等級</th><th>定義</th><th>回應時限</th><th>處理方式</th></tr></thead>
                    <tbody>
                        <tr><td><span class="badge badge-danger">P0 緊急</span></td><td>大量用戶受影響 / 資金異常</td><td>5 分鐘</td><td>直接電話 Robin</td></tr>
                        <tr><td><span class="badge badge-warning">P1 高</span></td><td>單一站點整體異常</td><td>15 分鐘</td><td>回報 → Slack → 追蹤</td></tr>
                        <tr><td><span class="badge badge-info">P2 中</span></td><td>個別用戶問題</td><td>1 小時</td><td>標準 SOP 處理</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>
    <hr class="section-divider">
    """


def build_comparison_section(stats, num):
    """Build the cross-product-line comparison section."""
    pl_compare = stats["plCompare"]

    return f"""
    <section id="compare" class="section">
        <div class="section-title"><span class="num">{num}</span> 📈 產品線對比分析</div>

        <div class="pl-comparison-grid">
            <div class="pl-card" style="border-top-color: #00B4D8;">
                <h4 style="color: #00B4D8;">💬 LINE站</h4>
                <div class="pl-stat"><span>總訊息</span><span class="val">{pl_compare['LINE站']['total']:,}</span></div>
                <div class="pl-stat"><span>客訴數</span><span class="val" style="color:var(--danger)">{pl_compare['LINE站']['complaints']:,}</span></div>
                <div class="pl-stat"><span>站點數</span><span class="val">{pl_compare['LINE站']['stations']}</span></div>
                <div class="pl-stat"><span>客訴率</span><span class="val">{round(pl_compare['LINE站']['complaints']/pl_compare['LINE站']['total']*100,1)}%</span></div>
            </div>
            <div class="pl-card" style="border-top-color: #00D99F;">
                <h4 style="color: #00D99F;">💳 信用版</h4>
                <div class="pl-stat"><span>總訊息</span><span class="val">{pl_compare['信用版']['total']:,}</span></div>
                <div class="pl-stat"><span>客訴數</span><span class="val" style="color:var(--danger)">{pl_compare['信用版']['complaints']:,}</span></div>
                <div class="pl-stat"><span>站點數</span><span class="val">{pl_compare['信用版']['stations']}</span></div>
                <div class="pl-stat"><span>客訴率</span><span class="val">{round(pl_compare['信用版']['complaints']/pl_compare['信用版']['total']*100,1)}%</span></div>
            </div>
            <div class="pl-card" style="border-top-color: #9D4EDD;">
                <h4 style="color: #9D4EDD;">🎮 遊戲商</h4>
                <div class="pl-stat"><span>總訊息</span><span class="val">{pl_compare['遊戲商']['total']:,}</span></div>
                <div class="pl-stat"><span>客訴數</span><span class="val" style="color:var(--danger)">{pl_compare['遊戲商']['complaints']:,}</span></div>
                <div class="pl-stat"><span>站點數</span><span class="val">{pl_compare['遊戲商']['stations']}</span></div>
                <div class="pl-stat"><span>客訴率</span><span class="val">{round(pl_compare['遊戲商']['complaints']/pl_compare['遊戲商']['total']*100,1)}%</span></div>
            </div>
            <div class="pl-card" style="border-top-color: #FB5607;">
                <h4 style="color: #FB5607;">🌐 外包</h4>
                <div class="pl-stat"><span>總訊息</span><span class="val">{pl_compare['外包']['total']:,}</span></div>
                <div class="pl-stat"><span>客訴數</span><span class="val" style="color:var(--danger)">{pl_compare['外包']['complaints']:,}</span></div>
                <div class="pl-stat"><span>站點數</span><span class="val">{pl_compare['外包']['stations']}</span></div>
                <div class="pl-stat"><span>客訴率</span><span class="val">{round(pl_compare['外包']['complaints']/pl_compare['外包']['total']*100,1)}%</span></div>
            </div>
        </div>

        <div class="chart-grid">
            <div class="chart-box">
                <h3>各產品線客訴數對比</h3>
                <div class="chart-wrap"><canvas id="plCompareBar"></canvas></div>
            </div>
            <div class="chart-box">
                <h3>各產品線客訴率對比</h3>
                <div class="chart-wrap"><canvas id="plCompareRate"></canvas></div>
            </div>
        </div>

        <div class="chart-grid">
            <div class="chart-box">
                <h3>各產品線訊息量佔比</h3>
                <div class="chart-wrap"><canvas id="plComparePie"></canvas></div>
            </div>
            <div class="chart-box">
                <h3>各產品線 Top 3 客訴類別</h3>
                <div class="chart-wrap-lg"><canvas id="plCompareTopCats"></canvas></div>
            </div>
        </div>

        <div class="card" style="margin-bottom:24px;">
            <h3>產品線對比關鍵發現</h3>
            <ul style="margin-left:20px;color:#ccc;line-height:1.8;">
                <li><strong style="color:#00B4D8;">LINE站</strong>：客訴量最大（{pl_compare['LINE站']['complaints']:,}），帳號問題為主，需加強帳號相關自助功能</li>
                <li><strong style="color:#00D99F;">信用版</strong>：帳務對帳為特色問題，P1 比例偏高，需專人跟進帳務類客訴</li>
                <li><strong style="color:#9D4EDD;">遊戲商</strong>：體量最小但遊戲異常佔比高，噪音比最低（4.4%），問題品質精準</li>
                <li><strong style="color:#FB5607;">外包</strong>：N8 印度站為全公司單站客訴最高，需建立專屬 SOP</li>
            </ul>
        </div>
    </section>
    <hr class="section-divider">
    """


def build_rules_section(num):
    return f"""
    <section id="rules" class="section">
        <div class="section-title"><span class="num">!</span> FAE 鐵律（必讀）</div>
        <div class="rules-box">
            <h3>五大鐵律 — 凌駕所有技術判斷</h3>
            <ol>
                <li><strong>先自查再問人</strong> — 查本文件 → FAQ → 歷史對話 → 後台 UAT / Postman → Kibana → 再找工程</li>
                <li><strong>禁止時間承諾</strong> — 不說「幾分鐘」「幾小時好」→ 用「有進度第一時間同步」</li>
                <li><strong>禁止絕對用語</strong> — 不說「一定」「絕對」「保證」→ 用「依目前資訊來看…」</li>
                <li><strong>一次問完不擠牙膏</strong> — 把需要的資料一次列齊，禁止連續追問</li>
                <li><strong>以條款為準，只引用不解釋</strong> — 活動爭議引用原文，不自行詮釋</li>
            </ol>
        </div>
        <div class="chart-grid">
            <div class="card">
                <h3 style="color: var(--danger);">禁用話術</h3>
                <table>
                    <thead><tr><th>禁止說法</th><th>原因</th></tr></thead>
                    <tbody>
                        <tr><td style="color:#ff8888;">「一定能解決」「保證沒問題」</td><td>無法保證結果</td></tr>
                        <tr><td style="color:#ff8888;">「預計 30 分鐘內完成」</td><td>時間不可控</td></tr>
                        <tr><td style="color:#ff8888;">「這是工程的問題」</td><td>禁止甩鍋</td></tr>
                        <tr><td style="color:#ff8888;">「之前也是這樣處理」</td><td>每次需獨立確認</td></tr>
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h3 style="color: var(--success);">建議話術（進度承諾）</h3>
                <table>
                    <thead><tr><th>建議說法</th><th>適用場景</th></tr></thead>
                    <tbody>
                        <tr><td style="color:#88ff88;">「已收到，確認中，有進度第一時間同步」</td><td>所有問題的通用開場</td></tr>
                        <tr><td style="color:#88ff88;">「依目前資訊來看，可能是 XX 原因」</td><td>需推測原因時</td></tr>
                        <tr><td style="color:#88ff88;">「已回報相關單位，目前等待回覆」</td><td>需升級時</td></tr>
                        <tr><td style="color:#88ff88;">「麻煩提供 XX，我們加速處理」</td><td>需補充資料時</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="card" style="margin-top:20px;">
            <h3>鐵律違反案例（實際紀錄）</h3>
            <table>
                <thead><tr><th>違規類型</th><th>站點</th><th>人員</th><th>日期</th><th>內容</th></tr></thead>
                <tbody id="violationsBody"></tbody>
            </table>
        </div>
    </section>
    <hr class="section-divider">
    """


def build_templates_section(num):
    return f"""
    <section id="templates" class="section">
        <div class="section-title"><span class="num">{num}</span> 十大高頻問題標準回覆範本</div>
        <p style="color:var(--text-dim);margin-bottom:16px;">基於客訴分析得出的 Top 10 高頻問題，每則包含標準回覆話術及注意事項。</p>
        <div class="template-grid" id="templateGrid"></div>
    </section>
    <hr class="section-divider">
    """


def build_faq_section(num):
    return f"""
    <section id="faq" class="section">
        <div class="section-title"><span class="num">{num}</span> 常見問題解答 (FAQ)</div>
        <p style="color:var(--text-dim);margin-bottom:16px;">8 大類別常見問答，可點擊展開查看解答。</p>
        <div id="faqContainer"></div>
    </section>
    <hr class="section-divider">
    """


def build_escalation_section():
    return """
    <section id="escalation" class="section">
        <div class="section-title"><span class="num">+</span> 升級流程與找對的人</div>
        <div class="card" style="margin-bottom: 20px;">
            <h3>標準升級鏈</h3>
            <div class="flow-steps">
                <div class="flow-step">FAE 自查<br><small style="color:var(--text-dim)">查本文件 → FAQ → 歷史對話</small></div>
                <div class="flow-arrow">&#10148;</div>
                <div class="flow-step">UAT / Postman<br><small style="color:var(--text-dim)">後台驗證 / API 測試</small></div>
                <div class="flow-arrow">&#10148;</div>
                <div class="flow-step">Kibana Log<br><small style="color:var(--text-dim)">查錯誤原因</small></div>
                <div class="flow-arrow">&#10148;</div>
                <div class="flow-step">Slack 對應工程<br><small style="color:var(--text-dim)">上面都無解時</small></div>
                <div class="flow-arrow">&#10148;</div>
                <div class="flow-step" style="border-color: var(--danger); background: rgba(255,68,68,0.15);">升級 Robin<br><small style="color:var(--text-dim)">一切由 Robin 整合判斷</small></div>
            </div>
        </div>
        <div class="chart-grid">
            <div class="card">
                <h3>Slack 找對的人</h3>
                <table>
                    <thead><tr><th>問題</th><th>找誰</th></tr></thead>
                    <tbody>
                        <tr><td>lilian 前端</td><td>David / Dobi / Ludde</td></tr>
                        <tr><td><strong>lilian 後端主程式</strong></td><td><strong>Peter</strong></td></tr>
                        <tr><td>lilian 一般後端</td><td>Jerry / James / frank / Ada</td></tr>
                        <tr><td><strong>MG 集成後台</strong></td><td><strong>Jay</strong></td></tr>
                        <tr><td>信用版 GA / DBA</td><td>johnson</td></tr>
                        <tr><td>TG 捕魚 (TP)</td><td>TP-dp 群</td></tr>
                        <tr><td>FF / DD 外包</td><td>FF 技術窗口 (Discord)</td></tr>
                        <tr><td>IP / VPN / 網路</td><td>alex / RayLin</td></tr>
                        <tr><td>排班 / 人事</td><td>Laura</td></tr>
                        <tr><td><strong>上層決策</strong></td><td style="color: var(--danger);"><strong>一律先找 Robin</strong></td></tr>
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h3>證據三件套（缺一不可）</h3>
                <table>
                    <thead><tr><th>問題類型</th><th>必備證據</th></tr></thead>
                    <tbody>
                        <tr><td>帳號</td><td>帳號 + 最後登入時間 + 截圖</td></tr>
                        <tr><td>充值</td><td>訂單號 + 帳號 + 充值時間（含時區）</td></tr>
                        <tr><td><strong>遊戲異常</strong></td><td><strong>局號 + 帳號 + 截圖</strong>（沒這三件不開單）</td></tr>
                        <tr><td>提款</td><td>訂單號 + 帳號 + 時間</td></tr>
                        <tr><td>活動爭議</td><td>活動名稱 + 帳號 + 質疑點</td></tr>
                        <tr><td>帳務對帳</td><td>對帳期間 + 涉及遊戲 + 差異金額</td></tr>
                    </tbody>
                </table>
                <div style="margin-top: 12px; padding: 10px; background: var(--primary-dim); border-radius: 6px; font-size: 0.9em; color: var(--text-dim);">
                    <strong style="color: var(--primary);">回問原則：</strong>一次問完，禁止擠牙膏。
                </div>
            </div>
        </div>
    </section>
    """


# ─── JS Chart Rendering ────────────────────────────────────────────────────
def build_chart_js(stats):
    """Build the Chart.js rendering code."""
    lines = []
    lines.append(f"const COLORS = {COLORS_JS};")
    lines.append("Chart.defaults.color = '#aaa';")
    lines.append("Chart.defaults.borderColor = 'rgba(255,107,53,0.1)';")
    lines.append("Chart.defaults.font.family = \"system-ui,'Noto Sans TC',sans-serif\";")
    lines.append("")

    # Embed all data
    for pl_key in ["overall", "line", "credit", "vendor", "outsource"]:
        d = stats[pl_key]
        cats = d["categories"]
        cats_no_other = {k: v for k, v in cats.items() if k != "其他"}
        stations = dict(sorted(d["stationComplaints"].items(), key=lambda x: -x[1]))
        daily = d["dailyCounts"]
        severity = d["severityCounts"]

        prefix = pl_key.upper()
        lines.append(f"const {prefix}_CATS = {js_obj(cats_no_other)};")
        lines.append(f"const {prefix}_CATS_ALL = {js_obj(cats)};")
        lines.append(f"const {prefix}_STATIONS = {js_obj(stations)};")
        lines.append(f"const {prefix}_DAILY = {js_obj(daily)};")
        lines.append(f"const {prefix}_SEV = {js_obj(severity)};")
        lines.append("")

    # Comparison data
    lines.append(f"const PL_COMPARE = {js_obj(stats['plCompare'])};")
    lines.append("")

    # Generic chart builders
    lines.append(r"""
// Generic chart builders
function buildCatPie(canvasId, catsObj) {
    var names = Object.keys(catsObj);
    var vals = Object.values(catsObj);
    new Chart(document.getElementById(canvasId), {
        type: 'doughnut',
        data: { labels: names, datasets: [{ data: vals, backgroundColor: COLORS.slice(0, names.length), borderColor: '#1a1a2e', borderWidth: 2 }] },
        options: {
            responsive: true, maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true, font: { size: 11 } } },
                tooltip: { callbacks: { label: function(ctx) { var t = ctx.dataset.data.reduce((a,b)=>a+b,0); return ctx.label+': '+ctx.parsed+' ('+(ctx.parsed/t*100).toFixed(1)+'%)'; } } }
            }
        }
    });
}

function buildCatBar(canvasId, catsAllObj) {
    new Chart(document.getElementById(canvasId), {
        type: 'bar',
        data: { labels: Object.keys(catsAllObj), datasets: [{ label: '件數', data: Object.values(catsAllObj), backgroundColor: COLORS.concat(COLORS).slice(0, 9).map(c => c + 'CC'), borderWidth: 0 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } }
    });
}

function buildStationBar(canvasId, stationsObj) {
    new Chart(document.getElementById(canvasId), {
        type: 'bar',
        data: { labels: Object.keys(stationsObj), datasets: [{ label: '客訴數', data: Object.values(stationsObj), backgroundColor: COLORS.concat(COLORS).slice(0, Object.keys(stationsObj).length).map(c => c+'CC'), borderWidth: 0 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } }
    });
}

function buildTrend(canvasId, dailyObj, days) {
    var end = new Date('2026-04-13'), dates = [];
    for (var i = days-1; i >= 0; i--) { var d = new Date(end); d.setDate(d.getDate()-i); dates.push(d.toISOString().split('T')[0]); }
    var allCats = {};
    Object.values(dailyObj).forEach(function(dayData) { Object.keys(dayData).forEach(function(c) { if(c !== '其他') allCats[c] = true; }); });
    var catNames = Object.keys(allCats);
    new Chart(document.getElementById(canvasId), {
        type: 'line',
        data: {
            labels: dates.map(d => d.substring(5)),
            datasets: catNames.map((cat, idx) => ({
                label: cat,
                data: dates.map(d => (dailyObj[d] && dailyObj[d][cat]) || 0),
                borderColor: COLORS[idx % COLORS.length],
                backgroundColor: 'transparent',
                borderWidth: 1.5,
                pointRadius: days > 60 ? 0 : 2,
                tension: 0.3
            }))
        },
        options: {
            responsive: true, maintainAspectRatio: true,
            plugins: { legend: { position: 'top', labels: { boxWidth: 10, font: { size: 10 } } } },
            scales: { y: { beginAtZero: true }, x: { ticks: { maxTicksLimit: days > 60 ? 12 : 10, font: { size: 9 } } } }
        }
    });
}

function buildSevPie(canvasId, sevObj) {
    new Chart(document.getElementById(canvasId), {
        type: 'doughnut',
        data: { labels: ['P2 中等','P1 高','P0 緊急'], datasets: [{ data: [sevObj.P2||0, sevObj.P1||0, sevObj.P0||0], backgroundColor: ['#FFB300','#ff8800','#ff4444'], borderColor: '#1a1a2e', borderWidth: 2 }] },
        options: {
            responsive: true, maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true } },
                tooltip: { callbacks: { label: function(ctx) { var t = ctx.dataset.data.reduce((a,b)=>a+b,0); return ctx.label+': '+ctx.parsed+' ('+(ctx.parsed/t*100).toFixed(1)+'%)'; } } }
            }
        }
    });
}
""")

    # Build charts for each PL
    for pl_key in ["overall", "line", "credit", "vendor", "outsource"]:
        prefix = pl_key.upper()
        lines.append(f"// === {PL_META[pl_key]['title']} charts ===")
        lines.append(f"buildCatPie('{pl_key}CatPie', {prefix}_CATS);")
        lines.append(f"buildCatBar('{pl_key}CatBar', {prefix}_CATS_ALL);")
        lines.append(f"buildStationBar('{pl_key}StationBar', {prefix}_STATIONS);")
        lines.append(f"buildTrend('{pl_key}Trend30', {prefix}_DAILY, 30);")
        lines.append(f"buildTrend('{pl_key}Trend90', {prefix}_DAILY, 90);")
        lines.append(f"buildSevPie('{pl_key}SevPie', {prefix}_SEV);")
        lines.append("")

    # Comparison charts
    lines.append(r"""
// === Product Line Comparison Charts ===
var plNames = Object.keys(PL_COMPARE);
var plColors = ['#00B4D8','#00D99F','#9D4EDD','#FB5607'];

new Chart(document.getElementById('plCompareBar'), {
    type: 'bar',
    data: { labels: plNames, datasets: [{ label: '客訴數', data: plNames.map(n => PL_COMPARE[n].complaints), backgroundColor: plColors.map(c => c+'CC'), borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
});

new Chart(document.getElementById('plCompareRate'), {
    type: 'bar',
    data: { labels: plNames, datasets: [{ label: '客訴率 (%)', data: plNames.map(n => (PL_COMPARE[n].complaints/PL_COMPARE[n].total*100).toFixed(1)), backgroundColor: plColors.map(c => c+'CC'), borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { callback: function(v) { return v+'%'; } } } } }
});

new Chart(document.getElementById('plComparePie'), {
    type: 'doughnut',
    data: { labels: plNames, datasets: [{ data: plNames.map(n => PL_COMPARE[n].total), backgroundColor: plColors, borderColor: '#1a1a2e', borderWidth: 2 }] },
    options: {
        responsive: true, maintainAspectRatio: true,
        plugins: {
            legend: { position: 'bottom', labels: { padding: 12, usePointStyle: true } },
            tooltip: { callbacks: { label: function(ctx) { var t = ctx.dataset.data.reduce((a,b)=>a+b,0); return ctx.label+': '+ctx.parsed.toLocaleString()+' ('+(ctx.parsed/t*100).toFixed(1)+'%)'; } } }
        }
    }
});

// Top 3 categories per PL (grouped bar)
var topCatNames = new Set();
plNames.forEach(function(n) { Object.keys(PL_COMPARE[n].topCats).forEach(function(c) { topCatNames.add(c); }); });
topCatNames = Array.from(topCatNames);

new Chart(document.getElementById('plCompareTopCats'), {
    type: 'bar',
    data: {
        labels: topCatNames,
        datasets: plNames.map(function(n, i) {
            return { label: n, data: topCatNames.map(function(c) { return PL_COMPARE[n].topCats[c] || 0; }), backgroundColor: plColors[i]+'CC', borderWidth: 0 };
        })
    },
    options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } },
        scales: { y: { beginAtZero: true } }
    }
});
""")

    # Violations, Templates, FAQ rendering (carried over)
    lines.append(VIOLATIONS_JS)
    lines.append(r"""
// Violations table
var vBody = document.getElementById('violationsBody');
VIOLATIONS.forEach(function(v) {
    var typeClass = v.type.includes('時間') ? 'badge-warning' : 'badge-danger';
    var row = document.createElement('tr');
    row.innerHTML = '<td><span class="badge '+typeClass+'">'+v.type+'</span></td><td>'+v.station+'</td><td>'+v.from+'</td><td>'+v.date+'</td><td style="max-width:300px;color:#ccc;">'+v.text+'</td>';
    vBody.appendChild(row);
});
""")

    lines.append(TEMPLATES_JS)
    lines.append(r"""
// Templates rendering
var tGrid = document.getElementById('templateGrid');
TEMPLATES.forEach(function(t, idx) {
    var card = document.createElement('div');
    card.className = 'template-card';
    card.innerHTML = '<div class="template-header"><span class="template-num">'+(idx+1)+'</span><span class="template-title">'+t.title+'</span></div>'
        + '<div class="template-body">'
        + '<div class="template-section"><div class="template-label">問題描述</div><p style="color:#ccc;font-size:0.93em;">'+t.desc+'</p></div>'
        + '<div class="template-section"><div class="template-label">回覆話術</div><div class="template-content">'+t.reply.replace(/\n/g,'<br>')+'</div></div>'
        + '<div class="template-section"><div class="template-label">注意事項</div><div class="template-warning">'+t.warning+'</div></div>'
        + '</div>';
    tGrid.appendChild(card);
});
""")

    lines.append(FAQ_JS)
    lines.append(r"""
// FAQ rendering
var faqContainer = document.getElementById('faqContainer');
FAQ_DATA.forEach(function(cat) {
    var section = document.createElement('div');
    section.className = 'faq-category';
    section.innerHTML = '<div class="faq-category-title">'+cat.cat+'</div>';
    cat.items.forEach(function(item) {
        var faqItem = document.createElement('div');
        faqItem.className = 'faq-item';
        faqItem.innerHTML = '<div class="faq-q" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'show\');">'
            + '<span class="arrow">&#9654;</span><span class="q-text">'+item.q+'</span></div>'
            + '<div class="faq-a">'+item.a+'</div>';
        section.appendChild(faqItem);
    });
    faqContainer.appendChild(section);
});
""")

    # Nav active state
    lines.append(r"""
// Nav active state
var navLinks = document.querySelectorAll('.nav-link');
var sections = document.querySelectorAll('.section[id]');
window.addEventListener('scroll', function() {
    var scrollPos = window.scrollY + 100;
    sections.forEach(function(section) {
        if (section.offsetTop <= scrollPos && (section.offsetTop + section.offsetHeight) > scrollPos) {
            navLinks.forEach(function(link) {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + section.id) link.classList.add('active');
            });
        }
    });
});
""")

    return "\n".join(lines)


def generate_html(stats):
    """Generate the complete HTML file."""
    overall = stats["overall"]

    html_parts = []

    html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAE 客服知識庫簡報 - Wolves Digital</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
    <style>{CSS}</style>
</head>
<body>

<nav class="nav">
    <span class="nav-brand">🐺 Wolves FAE</span>
    <div class="nav-links">
        <a href="#cover" class="nav-link active">首頁</a>
        <a href="#overview" class="nav-link">📊 總覽</a>
        <a href="#line" class="nav-link pl-line">💬 LINE站</a>
        <a href="#credit" class="nav-link pl-credit">💳 信用版</a>
        <a href="#vendor" class="nav-link pl-vendor">🎮 遊戲商</a>
        <a href="#outsource" class="nav-link pl-outsource">🌐 外包</a>
        <a href="#compare" class="nav-link">📈 對比</a>
        <a href="#rules" class="nav-link">⚠️ 鐵律</a>
        <a href="#templates" class="nav-link">📋 範本</a>
        <a href="#faq" class="nav-link">❓ FAQ</a>
        <a href="#escalation" class="nav-link">🔺 升級</a>
    </div>
</nav>

<div class="container">

    <section id="cover" class="cover section">
        <h1>FAE 客服知識庫簡報</h1>
        <div class="subtitle">多維度客訴分析 — LINE站 / 信用版 / 遊戲商 / 外包</div>
        <div class="meta">
            <div>📊 資料筆數：<span>{overall['totalMessages']:,}</span></div>
            <div>🔥 客訴數：<span>{overall['complaintCount']:,}</span></div>
            <div>📅 資料截至：<span>2026-04-13</span></div>
            <div>🏢 產品線：<span>4 大板塊 / 24 站點</span></div>
        </div>
    </section>

    <hr class="section-divider">
""")

    # Overall section (num 1)
    html_parts.append(build_pl_section(stats["overall"], "overall", "1"))

    # LINE站 section (num 2)
    html_parts.append(build_pl_section(stats["line"], "line", "2"))

    # 信用版 section (num 3)
    html_parts.append(build_pl_section(stats["credit"], "credit", "3"))

    # 遊戲商 section (num 4)
    html_parts.append(build_pl_section(stats["vendor"], "vendor", "4"))

    # 外包 section (num 5)
    html_parts.append(build_pl_section(stats["outsource"], "outsource", "5"))

    # Comparison section (num 6)
    html_parts.append(build_comparison_section(stats, "6"))

    # Rules section
    html_parts.append(build_rules_section("!"))

    # Templates section (num 7)
    html_parts.append(build_templates_section("7"))

    # FAQ section (num 8)
    html_parts.append(build_faq_section("8"))

    # Escalation section
    html_parts.append(build_escalation_section())

    # Footer
    html_parts.append(f"""
    <footer>
        <p>Wolves Digital FAE 客服知識庫簡報 v2.0 | 資料截至 2026-04-13 | 4 大產品線 / 24 站點 / {overall['totalMessages']:,} 筆訊息</p>
        <p style="margin-top: 4px;">含 LINE站(14) / 信用版(2) / 遊戲商(3) / 外包(5) 完整分析 | 更新週期：每月</p>
    </footer>

</div>

<script>
{build_chart_js(stats)}
</script>
</body>
</html>
""")

    return "\n".join(html_parts)


def main():
    stats = load_stats()
    html_content = generate_html(stats)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated: {OUTPUT_FILE} ({len(html_content):,} chars)")

    # Also copy to index.html for GitHub Pages
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Copied to: {INDEX_FILE}")


if __name__ == "__main__":
    main()
