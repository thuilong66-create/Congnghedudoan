#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIP PRO ULTIMATE AI 6.0 — 1 THUẬT TOÁN DU ĐOÁN DUY NHẤT (Unified Engine)"""
import os, time, json, threading, logging
from functools import wraps
from datetime import datetime
from flask import Flask, request, redirect, url_for, session, flash, abort, jsonify
from database import (PACKAGES, BANK_INFO, register_user, login_user, get_user, check_key,
    activate_key, create_key, create_deposit, get_user_deposits, get_pending,
    approve_deposit, reject_deposit, get_all_users, get_all_keys, stats,
    deduct_balance, add_key_to_user, get_user_keys)
from api_client import (TOOLS_CONFIG, GAME_IMAGES, LOGO_URL, QR_ZALOPAY,
    get_tool_data, get_bcr_data, tools_by_group, TOOL_WEB_LINKS, WIDGET_CHAR_IMG)
from algorithms import du_doan_tx, du_doan_bcr, du_doan_md5, du_doan_pro

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vippro_ultimate_ai6_secret_2026')

# ══════════════════════════════════════
# CSS
# ══════════════════════════════════════
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Orbitron:wght@500;700;900&family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{background:#050a14;color:#f0ece3;font-family:'Inter',sans-serif;min-height:100vh;line-height:1.6;position:relative;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;z-index:-2;
  background:radial-gradient(ellipse 80% 50% at 15% 20%,rgba(125,211,252,0.06),transparent 60%),
  radial-gradient(ellipse 60% 40% at 85% 80%,rgba(255,51,85,0.04),transparent 50%),
  radial-gradient(ellipse 50% 50% at 50% 50%,rgba(0,255,170,0.03),transparent 60%)}
body::after{content:'';position:fixed;top:0;left:0;right:0;height:2px;z-index:9998;pointer-events:none;
  background:linear-gradient(90deg,transparent,#7dd3fc,transparent);background-size:200% 100%;
  animation:scanMove 4s linear infinite;opacity:.6}
@keyframes scanMove{0%{background-position:200% 0}100%{background-position:-200% 0}}
.sparkle{position:fixed;width:4px;height:4px;background:#7dd3fc;border-radius:50%;pointer-events:none;z-index:1;
  box-shadow:0 0 6px #7dd3fc,0 0 12px rgba(125,211,252,.5);animation:sparkleUp linear infinite;opacity:0}
@keyframes sparkleUp{0%{transform:translateY(100vh) rotate(0deg);opacity:0}10%{opacity:.8}90%{opacity:.6}100%{transform:translateY(-10vh) rotate(360deg);opacity:0}}
a{color:#7dd3fc;text-decoration:none}a:hover{color:#bbf7d0;text-shadow:0 0 10px rgba(125,211,252,.5)}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px 40px;position:relative;z-index:2}
.card{background:rgba(10,10,10,0.90);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border:1px solid rgba(125,211,252,0.12);border-radius:18px;padding:24px;transition:all .3s;margin-bottom:16px}
.card:hover{border-color:rgba(125,211,252,0.45);box-shadow:0 8px 32px rgba(125,211,252,0.12),0 0 20px rgba(125,211,252,0.05);transform:translateY(-2px)}
.glow-card{position:relative;overflow:hidden;background:rgba(10,10,10,0.92);border-radius:20px;padding:28px;margin-bottom:16px}
.glow-card::before{content:'';position:absolute;inset:-2px;border-radius:20px;
  background:linear-gradient(45deg,#7dd3fc,#34d399,#ff3355,#00ffaa,#7dd3fc);
  background-size:300% 300%;animation:borderGlow 5s ease infinite;z-index:-1}
@keyframes borderGlow{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.pred-ball{width:140px;height:140px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:3.5rem;font-weight:900;position:relative;margin:0 auto;
  font-family:'Orbitron',sans-serif}
.pred-ball::after{content:'';position:absolute;inset:-8px;border-radius:50%;
  border:2px solid #7dd3fc;opacity:.4;animation:ringPulse 2s infinite}
.pred-ball::before{content:'';position:absolute;inset:-16px;border-radius:50%;
  border:1px solid #7dd3fc;opacity:.2;animation:ringPulse 2s .5s infinite}
@keyframes ringPulse{0%,100%{transform:scale(1);opacity:.3}50%{transform:scale(1.08);opacity:.6}}
.c-tai{background:linear-gradient(135deg,#ff3355,#cc1133);color:#fff;text-shadow:0 0 20px rgba(255,51,85,.6),0 0 40px rgba(255,51,85,.3)}
.c-xiu{background:linear-gradient(135deg,#00ffaa,#00cc88);color:#050a14;text-shadow:0 0 20px rgba(0,255,170,.6)}
.c-player{background:linear-gradient(135deg,#00aaff,#0077cc);color:#fff;text-shadow:0 0 20px rgba(0,170,255,.6)}
.c-banker{background:linear-gradient(135deg,#ff3355,#cc1133);color:#fff;text-shadow:0 0 20px rgba(255,51,85,.6)}
.btn{padding:10px 24px;border-radius:12px;font-weight:700;font-size:14px;border:1px solid rgba(125,211,252,.3);cursor:pointer;
  transition:all .25s;display:inline-flex;align-items:center;gap:6px;text-decoration:none;background:rgba(125,211,252,.05);color:#7dd3fc}
.btn:active{transform:scale(.97)}
.btn-primary{background:linear-gradient(135deg,#7dd3fc,#4ade80);color:#050a14;border-color:#7dd3fc;
  box-shadow:0 4px 16px rgba(125,211,252,.3),0 0 20px rgba(125,211,252,.15);font-weight:900}
.btn-primary:hover{box-shadow:0 6px 28px rgba(125,211,252,.5),0 0 30px rgba(125,211,252,.3);transform:translateY(-1px);color:#050a14}
.btn-rose{background:linear-gradient(135deg,#ff3355,#cc1133);color:#fff;border-color:#ff3355}
.btn-green{background:linear-gradient(135deg,#00ffaa,#00cc88);color:#050a14;border-color:#00ffaa;font-weight:900}
.btn-ghost{background:rgba(125,211,252,.04);color:#aaa;border:1px solid rgba(125,211,252,.15)}
.btn-ghost:hover{background:rgba(125,211,252,.12);color:#7dd3fc;border-color:rgba(125,211,252,.4)}
.btn-sm{padding:6px 14px;font-size:12px;border-radius:8px}
input,select{width:100%;padding:12px 16px;background:rgba(125,211,252,.03);border:1px solid rgba(125,211,252,.2);
  border-radius:12px;color:#f0ece3;font-size:14px;outline:none;transition:border .2s,box-shadow .2s;margin-bottom:12px;font-family:'Inter',sans-serif}
input:focus,select:focus{border-color:#7dd3fc;box-shadow:0 0 0 3px rgba(125,211,252,.15)}
label{display:block;font-size:12px;color:#888899;margin-bottom:4px;font-weight:600;letter-spacing:.5px}
table{width:100%;border-collapse:collapse;font-size:12px}
th{padding:10px 12px;background:rgba(125,211,252,.08);color:#7dd3fc;font-size:10px;text-transform:uppercase;
  letter-spacing:1px;border-bottom:1px solid rgba(125,211,252,.3);text-align:left;font-family:'Orbitron',sans-serif}
td{padding:8px 12px;border-bottom:1px solid rgba(125,211,252,.05);color:#d0ccc0}
tr:hover{background:rgba(125,211,252,.04)}
.badge{font-size:9px;font-weight:800;padding:3px 8px;border-radius:6px;letter-spacing:.5px;display:inline-block;font-family:'Orbitron',sans-serif}
.badge-vip{background:linear-gradient(135deg,#7dd3fc,#4ade80);color:#050a14;box-shadow:0 0 10px rgba(125,211,252,.4)}
.badge-ai{background:linear-gradient(135deg,#00ffaa,#00cc88);color:#050a14}
.badge-ultimate{background:linear-gradient(135deg,#7dd3fc,#ff3355);color:#050a14}
.badge-tx{background:rgba(255,51,85,.12);color:#ff5577;border:1px solid rgba(255,51,85,.3)}
.badge-md5{background:rgba(0,255,170,.12);color:#00ffaa;border:1px solid rgba(0,255,170,.3)}
.badge-sicbo{background:rgba(0,170,255,.12);color:#00aaff;border:1px solid rgba(0,170,255,.3)}
.badge-p{background:rgba(0,170,255,.15);color:#00aaff}.badge-b{background:rgba(255,51,85,.15);color:#ff5577}
.hball{width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:800;flex-shrink:0;margin:2px;font-family:'Orbitron',sans-serif}
.grid{display:grid;gap:16px}.g2{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.g3{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.gcard{cursor:pointer;position:relative;overflow:hidden}
.gcard img{width:100%;height:160px;object-fit:cover;border-radius:16px 16px 0 0;display:block}
.gcard:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(125,211,252,.15)}
.flash{padding:12px 16px;border-radius:12px;font-size:13px;margin-bottom:12px;border:1px solid}
.flash-s{background:rgba(0,255,170,.08);border-color:rgba(0,255,170,.3);color:#00ffaa}
.flash-e{background:rgba(255,51,85,.08);border-color:rgba(255,51,85,.3);color:#ff5577}
.flash-w{background:rgba(125,211,252,.08);border-color:rgba(125,211,252,.3);color:#7dd3fc}
.conf-ring{position:relative;width:80px;height:80px;display:inline-block}
.nav{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;flex-wrap:wrap;gap:10px;
  border-bottom:1px solid rgba(125,211,252,.15);margin-bottom:24px;background:rgba(5,5,5,.8);backdrop-filter:blur(10px);
  position:relative}
.nav::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#7dd3fc,transparent);opacity:.6}
@media(max-width:768px){.g2,.g3{grid-template-columns:1fr}.nav{flex-direction:column;align-items:stretch}
  .pred-ball{width:110px;height:110px;font-size:2.8rem}.hero-t{font-size:2.2rem!important}}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.fade{animation:fadeIn .4s ease}
.mono{font-family:'JetBrains Mono',monospace}
.sbar{height:6px;border-radius:3px;background:rgba(125,211,252,.06);overflow:hidden}
.sbar-fill{height:100%;border-radius:3px;transition:width .5s;box-shadow:0 0 8px currentColor}
.tc{text-align:center}.tr{text-align:right}.flex{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.mb8{margin-bottom:8px}.mb16{margin-bottom:16px}.mt8{margin-top:8px}.mt16{margin-top:16px}
.fs12{font-size:12px}.fs10{font-size:10px}.c-dim{color:#666677}.c-grn{color:#00ffaa}.c-red{color:#ff5577}
.hero-t{font-size:4rem;font-weight:900;background:linear-gradient(135deg,#7dd3fc,#bbf7d0,#ff3355,#7dd3fc);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1;font-family:'Playfair Display',serif;
  text-shadow:0 0 40px rgba(125,211,252,.2)}
.engine-tag{display:inline-block;margin-top:10px;padding:6px 14px;border-radius:999px;
  background:linear-gradient(135deg,rgba(125,211,252,.15),rgba(0,255,170,.1));
  border:1px solid rgba(125,211,252,.4);color:#7dd3fc;font-size:11px;font-weight:800;letter-spacing:1px;
  font-family:'Orbitron',sans-serif;box-shadow:0 0 15px rgba(125,211,252,.15)}
footer{text-align:center;padding:32px 16px;color:#555566;font-size:11px;border-top:1px solid rgba(125,211,252,.08);margin-top:40px;font-family:'JetBrains Mono',monospace}
"""

# ══════════════════════════════════════
# HELPERS
# ══════════════════════════════════════
def get_sess_user():
    uid = session.get('user_id')
    if not uid: return None
    return get_user(uid)

def require_login(f):
    @wraps(f)
    def w(*a, **kw):
        if not session.get('user_id'): flash('Vui long dang nhap','error'); return redirect(url_for('login'))
        return f(*a, **kw)
    return w

def require_admin(f):
    @wraps(f)
    def w(*a, **kw):
        u = get_sess_user()
        if not u or not u.get('is_admin'): abort(403)
        return f(*a, **kw)
    return w

def require_key(f):
    @wraps(f)
    def w(*a, **kw):
        uid = session.get('user_id')
        if not uid: flash('Vui long dang nhap','error'); return redirect(url_for('login'))
        u = get_sess_user()
        if u and u.get('is_admin'): return f(*a, **kw)
        if not check_key(uid): flash('Ban can kich hoat key de su dung','warning'); return redirect(url_for('activate_key_page'))
        return f(*a, **kw)
    return w

def nav_html(user):
    left = '<a href="/" style="font-size:20px;font-weight:900;background:linear-gradient(135deg,#7dd3fc,#bbf7d0,#ff3355);-webkit-background-clip:text;-webkit-text-fill-color:transparent">VIP PRO ULTIMATE</a>'
    right = ''
    if user:
        name = user.get('full_name') or user.get('username','')
        bal = f"{user.get('balance',0):,}d"
        kst = '<span class="badge badge-vip">VIP</span>' if check_key(user.get('user_id')) else '<span class="badge badge-tx">FREE</span>'
        links = '<a href="/home" class="btn btn-ghost btn-sm">Tools</a> <a href="/baccarat" class="btn btn-ghost btn-sm">BCR</a> <a href="/shop" class="btn btn-primary btn-sm">Mua Key</a> <a href="/my-keys" class="btn btn-ghost btn-sm">Key cua toi</a>'
        if user.get('is_admin'): links += ' <a href="/admin" class="btn btn-ghost btn-sm">Admin</a>'
        right = f'{links} <span class="fs12 c-dim">{name} | {bal} {kst}</span> <a href="/logout" class="btn btn-ghost btn-sm">Thoat</a>'
    else:
        right = '<a href="/login" class="btn btn-primary btn-sm">Dang nhap</a> <a href="/register" class="btn btn-ghost btn-sm">Dang ky</a>'
    return f'<nav class="nav">{left}<div class="flex">{right}</div></nav>'

def page(title, body, user=None):
    fl = ''
    msgs = session.pop('_flashes', []) if '_flashes' in session else []
    for cat, msg in msgs:
        cls = 'flash-s' if cat == 'success' else ('flash-e' if cat == 'error' else 'flash-w')
        fl += f'<div class="flash {cls}">{msg}</div>'
    return f'''<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - VIP PRO ULTIMATE AI 6.0</title><style>{CSS}</style></head>
<body><div id="sparkles"></div><script>(function(){{var c=document.getElementById("sparkles");for(var i=0;i<15;i++){{var s=document.createElement("div");s.className="sparkle";s.style.left=Math.random()*100+"vw";s.style.animationDuration=(15+Math.random()*10)+"s";s.style.animationDelay=(Math.random()*15)+"s";var sz=(2+Math.random()*4);s.style.width=sz+"px";s.style.height=sz+"px";c.appendChild(s)}}}})();</script>{nav_html(user)}<div class="wrap fade">{fl}{body}</div>
<footer>VIP PRO ULTIMATE AI 6.0 &copy; 2026 | 1 THUAT TOAN DU DOAN DUY NHAT — Fusion Bayesian + Neural AI (FIFA-AI Layer) | {len(TOOLS_CONFIG)}+ Tools TX + 60+ Ban Baccarat</footer></body></html>'''

def conf_ring(value, color='#6366f1'):
    v = max(0, min(100, value))
    r = 36; c = 2 * 3.14159 * r; off = c * (1 - v / 100)
    return f'''<div class="conf-ring"><svg width="80" height="80" viewBox="0 0 80 80">
<circle cx="40" cy="40" r="{r}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="6"/>
<circle cx="40" cy="40" r="{r}" fill="none" stroke="{color}" stroke-width="6"
  stroke-dasharray="{c}" stroke-dashoffset="{off}" stroke-linecap="round" transform="rotate(-90 40 40)"/>
<text x="40" y="44" text-anchor="middle" fill="{color}" font-size="16" font-weight="900">{v:.0f}%</text>
</svg></div>'''

def hist_balls(history, mx=30):
    h = ''
    for c in history[-mx:]:
        cu = str(c).upper()
        if cu == 'T': h += '<span class="hball c-tai">T</span>'
        elif cu == 'X': h += '<span class="hball c-xiu">X</span>'
        elif cu == 'P': h += '<span class="hball c-player">P</span>'
        elif cu == 'B': h += '<span class="hball c-banker">B</span>'
        else: h += f'<span class="hball" style="background:rgba(255,255,255,.08);color:#64748b">{cu}</span>'
    return h

def loai_badge(loai):
    m = {'TX': 'badge-tx', 'MD5': 'badge-md5', 'SICBO': 'badge-sicbo'}
    return f'<span class="badge {m.get(loai,"badge-tx")}">{loai}</span>'

def fmt_price(p):
    return f"{p:,}d" if p else "0d"


# ══════════════════════════════════════
# LỊCH SỬ DỰ ĐOÁN (chỉ admin xem)
# ══════════════════════════════════════
PRED_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prediction_log.json')
_pred_cache = None

def _pred_load():
    global _pred_cache
    if _pred_cache is not None:
        return _pred_cache
    try:
        with open(PRED_LOG_FILE, 'r', encoding='utf-8') as f:
            _pred_cache = json.load(f)
    except Exception:
        _pred_cache = []
    return _pred_cache

def _pred_save(data):
    global _pred_cache
    _pred_cache = data
    try:
        with open(PRED_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data[-2000:], f, ensure_ascii=False)
    except Exception:
        pass

def log_prediction(tool_id, phien, predicted, dtc=0):
    """Ghi lai du doan cho 1 phien (chi ghi 1 lan moi tool+phien). predicted='T'/'X'."""
    try:
        phien_int = int(str(phien).strip())
    except (ValueError, TypeError):
        return
    data = _pred_load()
    key = (tool_id, phien_int)
    for e in data:
        if (e.get('tool_id'), e.get('phien')) == key:
            return  # da ghi roi
    cfg = TOOLS_CONFIG.get(tool_id, {})
    data.append({
        'tool_id': tool_id,
        'tool_name': cfg.get('name', tool_id),
        'phien': phien_int,
        'predicted': predicted,
        'actual': None,
        'correct': None,
        'dtc': dtc,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })
    _pred_save(data)

def update_predictions():
    """Cap nhat ket qua thuc te cho cac du doan chua co ket qua (lay tu API)."""
    data = _pred_load()
    changed = False
    # Group pending by tool
    pending_by_tool = {}
    for e in data:
        if e.get('actual') is None:
            pending_by_tool.setdefault(e['tool_id'], []).append(e)
    for tid, entries in pending_by_tool.items():
        try:
            d = get_tool_data(tid)
            if not d or not d.get('cac_phien'):
                continue
            # Map phien -> ket qua
            ph_map = {}
            for p in d['cac_phien']:
                mp = p.get('ma_phien', '')
                try:
                    mp_int = int(str(mp).strip())
                    ph_map[mp_int] = p.get('ket_qua', '')  # 'T' or 'X'
                except (ValueError, TypeError):
                    continue
            for e in entries:
                act = ph_map.get(e['phien'])
                if act in ('T', 'X'):
                    e['actual'] = act
                    e['correct'] = (act == e['predicted'])
                    changed = True
        except Exception:
            continue
    if changed:
        _pred_save(data)
    return data

def prediction_stats(tool_id=None):
    data = _pred_load()
    if tool_id:
        data = [e for e in data if e.get('tool_id') == tool_id]
    done = [e for e in data if e.get('correct') is not None]
    correct = sum(1 for e in done if e['correct'])
    wrong = len(done) - correct
    pending = len(data) - len(done)
    wr = round(correct / len(done) * 100, 1) if done else 0.0
    return {'total': len(data), 'done': len(done), 'correct': correct,
            'wrong': wrong, 'pending': pending, 'win_rate': wr}


# ══════════════════════════════════════
# BACKGROUND WORKER — tự động dự đoán liên tục (không cần user mở web)
# ══════════════════════════════════════
_worker_started = False
_worker_lock = threading.Lock()

def prediction_worker():
    """Quét tất cả tool mỗi 45s: lấy dữ liệu, dự đoán, ghi log. Cũng tự đối chiếu kết quả."""
    log = logging.getLogger("pred_worker")
    log.info("Background prediction worker started")
    while True:
        try:
            # 1) Ghi du doan cho tat ca tool
            for tid in list(TOOLS_CONFIG.keys()):
                try:
                    d = get_tool_data(tid)
                    if not d or not d.get('lich_su'):
                        continue
                    dd, _ = du_doan_pro(d['lich_su'], tid)
                    if not dd:
                        continue
                    pred_char = 'T' if dd.get('du_doan') == 'T' else 'X'
                    phien_raw = str(d.get('phien', ''))
                    try:
                        next_phien = int(phien_raw.strip()) + 1
                        log_prediction(tid, next_phien, pred_char, dd.get('do_tin_cay', 0))
                    except (ValueError, TypeError):
                        pass
                    time.sleep(1.5)  # tranh goi API qua day
                except Exception as e:
                    log.debug("Worker loi tool %s: %s", tid, e)
            # 2) Doi chieu ket qua thuc te cho cac du doan cho
            try:
                update_predictions()
            except Exception as e:
                log.debug("Worker update ket qua loi: %s", e)
            log.info("Worker quet xong vong, nghi 45s")
            time.sleep(45)
        except Exception as e:
            log.error("Worker loop loi: %s", e)
            time.sleep(60)

def start_prediction_worker():
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        # log_prediction khong trung (kiem tra tool+phien) nen duplicate worker cung khong sao
        t = threading.Thread(target=prediction_worker, daemon=True, name="PredictionWorker")
        t.start()
        _worker_started = True
        logging.getLogger("pred_worker").info("Da khoi dong background prediction worker")

# Khoi dong worker khi module duoc nap
try:
    start_prediction_worker()
except Exception:
    pass

# ══════════════════════════════════════
# ROUTES
# ══════════════════════════════════════
@app.route('/')
def landing():
    u = get_sess_user()
    groups = tools_by_group()
    n_tools = len(TOOLS_CONFIG)
    body = f'''<div class="tc" style="padding:60px 0 40px">
<div class="hero-t">VIP PRO ULTIMATE AI 6.0</div>
<div class="engine-tag">⚡ 1 THUẬT TOÁN DU ĐOÁN DUY NHẤT — FUSION BAYESIAN + NEURAL AI</div>
<p style="color:#94a3b8;font-size:18px;margin-top:12px">Toàn bộ thuật toán VIP được dồn vào 1 engine thống nhất</p>
<p style="color:#64748b;font-size:14px;margin-top:6px">Tích hợp công thức BCR + tầng FIFA-AI Neural | Tài Xỉu + Baccarat</p>
<div class="flex mt16" style="justify-content:center">
<a href="/home" class="btn btn-primary" style="font-size:16px;padding:14px 36px">Bat dau su dung</a>
<a href="/register" class="btn btn-ghost" style="font-size:16px;padding:14px 36px">Dang ky mien phi</a>
</div></div>
<div class="grid g3">
<div class="card tc"><div style="font-size:36px;margin-bottom:8px">60+</div>
<div style="color:#818cf8;font-weight:700">Ban Baccarat</div>
<div class="fs12 c-dim mt8">Theo doi truc tiep 60+ ban BCR</div></div>
<div class="card tc"><div style="font-size:36px;margin-bottom:8px">1</div>
<div style="color:#22c55e;font-weight:700">Ultimate Engine</div>
<div class="fs12 c-dim mt8">1 thuat toan thong nhat — fusion 4 lop</div></div>
<div class="card tc"><div style="font-size:36px;margin-bottom:8px">{n_tools}</div>
<div style="color:#a78bfa;font-weight:700">Tool Phan Tich</div>
<div class="fs12 c-dim mt8">{n_tools} tool tu {len(groups)} nha cai</div></div>
</div>'''
    return page('Trang chu', body, u)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
        if not u or not p:
            flash('Vui long nhap day du thong tin', 'error')
            return redirect(url_for('login'))
        ok, res = login_user(u, p)
        if ok:
            session['user_id'] = res.get('user_id')
            session['username'] = res.get('username')
            session['is_admin'] = res.get('is_admin', False)
            flash('Dang nhap thanh cong', 'success')
            return redirect(url_for('home'))
        flash(str(res), 'error')
        return redirect(url_for('login'))
    body = '''<div style="max-width:400px;margin:60px auto"><div class="card">
<h2 class="tc mb16" style="color:#818cf8">Dang Nhap</h2>
<form method="post"><label>Ten dang nhap</label><input name="username" required>
<label>Mat khau</label><input type="password" name="password" required>
<button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:8px">Dang nhap</button>
</form><p class="tc mt16 fs12 c-dim">Chua co tai khoan? <a href="/register">Dang ky</a></p>
</div></div>'''
    return page('Dang nhap', body)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '')
        fn = request.form.get('full_name', '').strip()
        if not u or not p:
            flash('Vui long nhap day du thong tin', 'error')
            return redirect(url_for('register'))
        if len(u) < 3 or len(p) < 4:
            flash('Ten dang nhap >= 3 ky tu, mat khau >= 4 ky tu', 'error')
            return redirect(url_for('register'))
        ok, msg = register_user(u, p, fn)
        if ok:
            flash('Dang ky thanh cong! Hay dang nhap', 'success')
            return redirect(url_for('login'))
        flash(msg, 'error')
        return redirect(url_for('register'))
    body = '''<div style="max-width:400px;margin:60px auto"><div class="card">
<h2 class="tc mb16" style="color:#818cf8">Dang Ky</h2>
<form method="post"><label>Ten dang nhap</label><input name="username" required>
<label>Ho ten</label><input name="full_name" placeholder="(Tuy chon)">
<label>Mat khau</label><input type="password" name="password" required>
<button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:8px">Dang ky</button>
</form><p class="tc mt16 fs12 c-dim">Da co tai khoan? <a href="/login">Dang nhap</a></p>
</div></div>'''
    return page('Dang ky', body)

@app.route('/logout')
def logout():
    session.clear()
    flash('Da dang xuat', 'success')
    return redirect(url_for('landing'))

@app.route('/home')
@require_login
def home():
    u = get_sess_user()
    groups = tools_by_group()
    body = '<h2 class="mb16" style="color:#e2e8f0">Chon Tool — an vao la vao web game</h2><div class="grid g2">'
    for nhom, tools in groups.items():
        img = GAME_IMAGES.get(nhom, '')
        tlist = ''
        for t in tools:
            play_link = f'/play/{t["id"]}' if nhom in TOOL_WEB_LINKS else f'/tool/{t["id"]}'
            tlist += f'<a href="{play_link}" class="flex mb8" style="padding:6px 10px;border-radius:10px;background:rgba(255,255,255,.03)">' \
                     f'<span style="flex:1;color:#e2e8f0;font-size:13px;font-weight:600">{t["name"]}</span>{loai_badge(t["loai"])}</a>'
        web_btn = ''
        if nhom in TOOL_WEB_LINKS:
            web_btn = f'<a href="{TOOL_WEB_LINKS[nhom]}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="width:100%;justify-content:center;margin-top:10px">Vao web {nhom}</a>'
        body += f'''<div class="card gcard" style="padding:0;overflow:hidden">
<img src="{img}" alt="{nhom}" onerror="this.style.display='none'">
<div style="padding:16px"><div class="flex mb8"><span style="font-weight:800;font-size:16px;color:#fff">{nhom}</span>
<span class="badge badge-ai">{len(tools)} tools</span></div>{tlist}{web_btn}</div></div>'''
    body += f'''<div class="card gcard" style="padding:0;overflow:hidden">
<img src="{GAME_IMAGES.get('BACCARAT','')}" alt="BCR" onerror="this.style.display='none'">
<div style="padding:16px"><div class="flex mb8"><span style="font-weight:800;font-size:16px;color:#fff">BACCARAT</span>
<span class="badge badge-vip">60+ BAN</span></div>
<a href="/baccarat" class="btn btn-rose btn-sm" style="width:100%;justify-content:center">Xem Baccarat</a>
</div></div>'''
    body += '</div>'
    return page('Tools', body, u)

# ══════════════════════════════════════
# WIDGET CON DỰ ĐOÁN BAY + KÉO ĐƯỢC
# ══════════════════════════════════════
def pred_widget(tool_id, cfg, phien, pred_label, dtc, is_bcr=False):
    """Widget nổi: ảnh nhân vật + panel trắng (tên tool, mã phiên, dự đoán).
    TX có nút 3 gạch ☰ chuyển Hũ/MD5. Click tên tool → mở web chính thức."""
    try:
        phien = str(int(str(phien).strip()) + 1)
    except (ValueError, TypeError):
        pass
    nhom = cfg.get('nhom', '')
    web_link = TOOL_WEB_LINKS.get(nhom, '')
    tool_img = GAME_IMAGES.get(nhom, '')
    tool_img_tag = f'<img src="{tool_img}" style="width:34px;height:34px;border-radius:8px;object-fit:cover;border:1px solid #7dd3fc;box-shadow:0 0 8px #7dd3fc88">' if tool_img else ''
    tool_name = cfg.get('full_name') or cfg.get('name', 'Tool')
    # Đối tác Hũ <-> MD5
    hu_id = md5_id = None
    if '_hu' in tool_id:
        hu_id = tool_id; md5_id = tool_id.replace('_hu', '_md5')
    elif '_md5' in tool_id:
        md5_id = tool_id; hu_id = tool_id.replace('_md5', '_hu')
    elif '_tx' in tool_id:
        hu_id = tool_id; md5_id = tool_id.replace('_tx', '_md5')
    show_menu = (not is_bcr) and hu_id in TOOLS_CONFIG and md5_id in TOOLS_CONFIG
    pred_color = '#ff3355' if pred_label.upper().startswith(('T','B')) else '#00ffaa'
    name_html = f'<a href="{web_link}" target="_blank" style="color:#111;text-decoration:none">{tool_name}</a>' if web_link else tool_name
    menu_html = ''
    if show_menu:
        menu_html = f'''<button class="pw-menu" id="pwMenuBtn" onclick="document.getElementById('pwDropdown').classList.toggle('show')">☰</button>
        <div class="pw-dropdown" id="pwDropdown">
          <a href="/tool/{hu_id}">🎲 TX Hũ</a>
          <a href="/tool/{md5_id}">🔐 TX MD5</a>
        </div>'''
    return f'''
<style>
.pred-widget{{position:fixed;right:14px;top:12%;z-index:9999;display:flex;flex-direction:row;align-items:center;cursor:grab;user-select:none;touch-action:none;animation:pwIn .5s ease}}
@keyframes pwIn{{from{{opacity:0;transform:translateX(40px)}}to{{opacity:1;transform:none}}}}
.pred-widget:active{{cursor:grabbing}}
.pw-char{{width:86px;height:86px;object-fit:contain;filter:drop-shadow(0 0 14px #00e5ffaa);cursor:pointer;z-index:2;margin-right:8px}}
@keyframes pwBlink{{0%,90%,100%{{transform:scaleY(1)}}93%{{transform:scaleY(0.12)}}}}
.pw-panel{{position:relative;background:rgba(10,14,28,0.55);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);color:#e2e8f0;border:2px solid;border-image:linear-gradient(90deg,#c4b5fd 50%,#93c5fd 50%) 1;border-radius:0;padding:12px 12px;min-width:150px;text-align:left;
  box-shadow:0 0 18px #818cf866,0 0 40px #60a5fa44;font-family:-apple-system,system-ui,sans-serif}}
.pw-brand{{font-size:8px;font-weight:900;color:#93c5fd;letter-spacing:2px;text-transform:uppercase;text-align:left;margin-bottom:2px}}
.pw-toolname{{font-size:9px;font-weight:700;color:#c4b5fd;text-align:left;letter-spacing:1px;margin-bottom:2px}}
.pw-toolname a{{color:#c4b5fd;text-decoration:none}}
.pw-session{{font-size:11px;color:#ffffff;margin-bottom:6px;letter-spacing:1px;text-align:left}}
.pw-session b{{color:#ffffff;font-size:13px;font-weight:800}}
.pw-pred{{font-size:36px;font-weight:900;color:#ff3355;text-shadow:0 0 12px #ff3355,0 0 24px #ff335588;letter-spacing:2px;line-height:1.1;margin:6px 0;text-align:left}}
.pw-bar{{width:100%;height:6px;background:#0a1628;border-radius:0;overflow:hidden;margin:6px 0 4px;border:1px solid #00e5ff44}}
.pw-bar-fill{{height:100%;background:linear-gradient(90deg,#00e5ff,#00ffaa);border-radius:0;box-shadow:0 0 8px #00e5ff}}
.pw-conf{{font-size:10px;color:#93c5fd;font-weight:700;letter-spacing:1px;text-align:left;margin-top:4px}}
.pw-menu{{position:absolute;top:-14px;right:-14px;background:#070b16;border:2px solid #00e5ff;border-radius:3px;width:30px;height:30px;cursor:pointer;font-size:14px;line-height:1;color:#00e5ff;z-index:6;box-shadow:0 0 10px #00e5ff88}}
.pw-dropdown{{display:none;position:absolute;top:20px;right:-8px;background:#070b16;border:1px solid #00e5ff;border-radius:3px;overflow:hidden;box-shadow:0 6px 20px rgba(0,229,255,.4);z-index:2}}
.pw-dropdown.show{{display:block}}
.pw-dropdown a{{display:block;padding:8px 14px;color:#a8f0ff;font-size:12px;text-decoration:none;border-bottom:1px solid #00e5ff33}}
.pw-dropdown a:hover{{background:#00e5ff33;color:#00e5ff}}
</style>
<div class="pred-widget" id="predWidget">
  <img src="{WIDGET_CHAR_IMG}" class="pw-char" alt="pred" onclick="var p=document.getElementById('pwPanel');p.style.display=(p.style.display==='none')?'block':'none'" title="An/Hien ket qua">
  <div class="pw-panel" id="pwPanel">
    <span onclick="document.getElementById('predWidget').style.display='none';document.getElementById('pwShow').style.display='flex'" style="position:absolute;top:4px;left:6px;cursor:pointer;color:#00e5ff;font-size:13px;font-weight:900;z-index:5;line-height:1">✕</span>
    {menu_html}
    <div class="pw-brand">TOOL HƯNG 24/7</div>
    <div class="pw-toolname">{name_html}</div>
    <div class="pw-session">PHIEN: #<b id="pwPhien">{phien}</b></div>
    <div style="display:flex;align-items:center;justify-content:flex-start;gap:10px;margin:6px 0">{tool_img_tag}<div class="pw-pred" id="pwPred" style="margin:0">{pred_label}</div></div>
    <div class="pw-bar"><div class="pw-bar-fill" id="pwBar" style="width:{dtc}%"></div></div>
    <div class="pw-conf" id="pwConf">TIN CAY: {dtc}%</div>
  </div>
</div>
<div id="pwShow" onclick="this.style.display='none';document.getElementById('predWidget').style.display='flex'" style="display:none;position:fixed;right:18px;top:32%;z-index:9999;background:#00e5ff;color:#070b16;border-radius:50%;width:46px;height:46px;align-items:center;justify-content:center;cursor:pointer;font-size:22px;box-shadow:0 0 15px #00e5ff">🤖</div>
<script>
(function(){{
  var w=document.getElementById('predWidget'),drag=false,sx=0,sy=0;
  function down(e){{var t=e.touches?e.touches[0]:e; if(e.target.tagName==='A'||e.target.tagName==='BUTTON')return; drag=true; sx=t.clientX-w.offsetLeft; sy=t.clientY-w.offsetTop; e.preventDefault();}}
  function move(e){{if(!drag)return; var t=e.touches?e.touches[0]:e; w.style.left=(t.clientX-sx)+'px'; w.style.top=(t.clientY-sy)+'px'; w.style.right='auto'; if(e.touches)e.preventDefault();}}
  function up(){{drag=false;}}
  w.addEventListener('mousedown',down); w.addEventListener('touchstart',down,{{passive:false}});
  document.addEventListener('mousemove',move); document.addEventListener('touchmove',move,{{passive:false}});
  document.addEventListener('mouseup',up); document.addEventListener('touchend',up);
}})();
</script>'''


# ══════════════════════════════════════
# PLAY — nhúng web game vào trong tool (web trong tool) + robot dự đoán nổi
# ══════════════════════════════════════
@app.route('/api/pred/<tool_id>')
@require_login
def api_pred(tool_id):
    """JSON cập nhật nhanh dự đoán (dùng cho /play mỗi 2s, không reload iframe)."""
    if tool_id not in TOOLS_CONFIG:
        return {'pred': '?', 'dtc': 0, 'phien': '—'}
    data = get_tool_data(tool_id)
    if not data or not data.get('lich_su'):
        return {'pred': '?', 'dtc': 0, 'phien': '—'}
    dd, _ = du_doan_pro(data['lich_su'], tool_id)
    pred = 'TAI' if dd.get('du_doan') == 'T' else 'XIU'
    _p = str(data.get('phien', '—'))
    try: _p = str(int(_p) + 1)
    except: pass
    # Ghi log du doan (cho admin xem lich su dung/sai)
    try:
        log_prediction(tool_id, int(_p), 'T' if pred == 'TAI' else 'X', dd.get('do_tin_cay', 0))
    except Exception:
        pass
    return {'pred': pred, 'dtc': dd.get('do_tin_cay', 0), 'phien': _p}


@app.route('/play/<tool_id>')
@require_login
@require_key
def play_tool(tool_id):
    if tool_id not in TOOLS_CONFIG:
        return redirect('/home')
    cfg = TOOLS_CONFIG[tool_id]
    web = TOOL_WEB_LINKS.get(cfg.get('nhom', ''))
    if not web:
        return redirect(f'/tool/{tool_id}')
    data = get_tool_data(tool_id)
    phien = '—'; pred_label = '—'; dtc = 0
    if data and data.get('lich_su'):
        dd, _ = du_doan_pro(data['lich_su'], tool_id)
        if dd:
            pred_label = 'TAI' if dd.get('du_doan') == 'T' else 'XIU'
            dtc = dd.get('do_tin_cay', 0)
            phien = str(data.get('phien', '—'))
    # ── Robot nang cao: menu ☰ chon TAT CA tool (lc79, hit, max789, sunwin...) ──
    groups_p = tools_by_group()
    all_tools_p = [t for ts in groups_p.values() for t in ts]
    def _mi(tid, tname):
        bg = '#c4b5fd44' if tid == tool_id else 'transparent'
        return ('<a href="javascript:void(0)" onclick="selectTool(\'%s\');document.getElementById(\'hrDropdown\').classList.remove(\'show\')" '
                'style="display:block;padding:8px 14px;color:#e2e8f0;font-size:12px;text-decoration:none;border-bottom:1px solid #c4b5fd33;background:%s">%s</a>') % (tid, bg, tname)
    menu_items_p = ''.join(_mi(t['id'], t['name']) for t in all_tools_p)
    radial_items_p = ''.join(
        '<div class=\"radial-item\" data-tid=\"%s\" onclick=\"selectTool(\'%s\');toggleRadial()\">%s</div>'
        % (t['id'], t['id'], t['name'].replace(' ','<br>'))
        for t in all_tools_p)
    pcolor = '#ff3355' if pred_label in ('TAI','BANKER') else '#00ffaa'
    nhom_p = cfg.get('nhom', '')
    web_link_p = TOOL_WEB_LINKS.get(nhom_p, '')
    tool_img_p = GAME_IMAGES.get(nhom_p, '')
    name_html_p = ('<a href="%s" target="_blank" style="color:#86efac;text-decoration:none">%s</a>' % (web_link_p, cfg.get('full_name','Tool'))) if web_link_p else cfg.get('full_name','Tool')
    tool_imgs_js = '{' + ','.join('"%s":"%s"' % (t['id'], GAME_IMAGES.get(t.get('nhom',''),'')) for t in all_tools_p) + '}'
    tool_web_js = '{' + ','.join('"%s":"%s"' % (t['id'], TOOL_WEB_LINKS.get(t.get('nhom',''),'')) for t in all_tools_p) + '}'
    tool_names_js = '{' + ','.join('"%s":"%s"' % (t['id'], t.get('full_name','')) for t in all_tools_p) + '}'
    widget = f'''
<style>
@keyframes hrIn{{from{{opacity:0;transform:translateX(40px)}}to{{opacity:1;transform:none}}}}
@keyframes hrBlink{{0%,90%,100%{{transform:scaleY(1)}}93%{{transform:scaleY(0.12)}}}}
.home-robot{{position:fixed;right:14px;top:18%;z-index:9999;display:flex;flex-direction:row-reverse;align-items:center;cursor:grab;user-select:none;touch-action:none;animation:hrIn .5s ease}}
.home-robot:active{{cursor:grabbing}}
.hr-panel{{position:relative;background:rgba(10,14,28,0.55);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);color:#e2e8f0;border-radius:0;padding:12px 14px;min-width:200px;margin-right:8px;text-align:left;border:2px solid;border-image:linear-gradient(90deg,#c4b5fd 50%,#93c5fd 50%) 1;box-shadow:0 0 18px #818cf866,0 0 40px #60a5fa44;font-family:sans-serif}}
.hr-brand{{font-size:8px;font-weight:900;color:#93c5fd;letter-spacing:2px;text-transform:uppercase;text-align:left;margin-bottom:2px}}
.hr-menu{{position:absolute;top:-14px;left:-14px;background:#070b16;border:2px solid #00e5ff;border-radius:3px;width:30px;height:30px;cursor:pointer;font-size:15px;line-height:1;color:#00e5ff;z-index:6;box-shadow:0 0 10px #00e5ff88}}
.hr-dropdown{{display:none;position:absolute;top:20px;left:-8px;background:#070b16;border:1px solid #00e5ff;border-radius:3px;overflow:hidden;box-shadow:0 6px 20px rgba(0,229,255,.4);z-index:5;max-height:320px;overflow-y:auto;min-width:150px}}
.hr-dropdown.show{{display:block}}
.hr-dropdown a:hover{{background:#c4b5fd55!important;color:#c4b5fd}}
.hr-title{{font-size:9px;font-weight:700;color:#c4b5fd;text-align:left;letter-spacing:1px;margin-bottom:2px}}
.hr-title a{{color:#c4b5fd;text-decoration:none}}
.hr-sub{{font-size:11px;color:#ffffff;margin-bottom:4px;letter-spacing:1px;text-align:left}}
.hr-sub b{{color:#ffffff;font-size:13px;font-weight:800}}
.hr-pred{{font-size:36px;font-weight:900;letter-spacing:2px;line-height:1.1;text-shadow:0 0 12px #ff3355;color:#ff3355;text-align:left}}
.hr-bar{{width:100%;height:6px;background:#0a1628;border-radius:0;overflow:hidden;margin:6px 0 4px;border:1px solid #00e5ff44}}
.hr-bar-fill{{height:100%;background:linear-gradient(90deg,#00e5ff,#00ffaa);border-radius:0;box-shadow:0 0 8px #00e5ff}}
.hr-conf{{font-size:10px;color:#93c5fd;font-weight:700;margin-top:4px;letter-spacing:1px;text-align:left}}
.hr-char{{width:78px;height:78px;object-fit:contain;filter:drop-shadow(0 0 14px #00e5ffaa);cursor:pointer;margin-right:8px}}
.hr-close{{position:absolute;top:4px;right:8px;cursor:pointer;color:#00e5ff;font-size:14px;font-weight:900;z-index:5;line-height:1}}
#robotShow{{display:none;position:fixed;right:18px;top:20%;z-index:9999;background:#00e5ff;color:#070b16;border-radius:50%;width:46px;height:46px;align-items:center;justify-content:center;cursor:pointer;font-size:22px;box-shadow:0 0 15px #00e5ff}}
.tool-v2-btn{{position:fixed;right:14px;bottom:14px;z-index:10000;background:linear-gradient(135deg,#00e5ff,#00ffaa);color:#070b16;border:none;border-radius:20px;padding:8px 16px;font-size:12px;font-weight:900;letter-spacing:1px;cursor:pointer;box-shadow:0 0 15px #00e5ffaa;transition:all .2s}}
.tool-v2-btn.active{{background:linear-gradient(135deg,#ff4d6d,#ff9f43);color:#fff;box-shadow:0 0 15px #ff4d6daa;animation:v2Pulse 1s infinite}}
.mini-tool-btn{{position:fixed;left:14px;bottom:80px;z-index:10002;width:104px;height:104px;cursor:grab;user-select:none;touch-action:none;animation:miniIn .5s ease}}
.mini-tool-btn:active{{cursor:grabbing}}
.mini-tool-btn img{{width:104px;height:104px;object-fit:contain;filter:drop-shadow(0 0 14px #7dd3fc);animation:miniPulse 2.5s ease-in-out infinite}}
.mini-tool-btn.active img{{animation:miniSpin .6s ease; filter:drop-shadow(0 0 20px #86efac)}}
@keyframes miniSpin{{from{{transform:rotate(0deg) scale(1)}}50%{{transform:rotate(180deg) scale(1.15)}}to{{transform:rotate(360deg) scale(1)}}}}
.radial-menu{{position:fixed;z-index:10001;pointer-events:none}}
.radial-item{{position:absolute;left:0;top:0;width:58px;height:58px;border-radius:50%;background:linear-gradient(135deg,#071020,#0a1a2e);border:2px solid #7dd3fc;color:#bae6fd;font-size:9px;font-weight:800;display:flex;align-items:center;justify-content:center;text-align:center;cursor:pointer;transform:translate(-50%,-50%) scale(0);transition:transform .45s cubic-bezier(.34,1.56,.64,1), opacity .3s;opacity:0;box-shadow:0 0 12px #7dd3fc88;line-height:1.1;padding:2px;pointer-events:auto}}
.radial-item.show{{opacity:1}}
.radial-item:hover{{border-color:#86efac;color:#bbf7d0;box-shadow:0 0 16px #86efacaa}}
@keyframes miniIn{{from{{opacity:0;transform:scale(.5)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes miniPulse{{0%,100%{{filter:drop-shadow(0 0 10px #c4b5fd)}}50%{{filter:drop-shadow(0 0 20px #93c5fd)}}}}

@keyframes v2Pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.06)}}}}
.analyzing-text{{color:#888!important;font-size:16px!important;letter-spacing:2px;animation:blinkText 1s infinite}}
@keyframes blinkText{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.v2-badge{{display:inline-block;background:#ff4d6d;color:#fff;font-size:9px;font-weight:900;padding:2px 6px;border-radius:6px;margin-left:4px;letter-spacing:1px}}
</style>
<div class="home-robot" id="homeRobot">
  <div class="hr-panel" id="hrPanel">
    <div class="hr-dropdown" id="hrDropdown">{menu_items_p}</div>
    <span class="hr-close" onclick="document.getElementById('homeRobot').style.display='none';document.getElementById('robotShow').style.display='flex'">✕</span>
    <div class="hr-brand">TOOL HƯNG 24/7</div>
    <div class="hr-title" id="hrName">{name_html_p}</div>
    <div class="hr-sub">PHIEN: <b id="hrPhien">#{phien}</b></div>
    <div style="display:flex;align-items:center;justify-content:flex-start;gap:10px;margin:6px 0">
      <img id="hrToolImg" src="{tool_img_p}" style="width:32px;height:32px;border-radius:8px;object-fit:cover;border:1px solid #00e5ff;box-shadow:0 0 8px #00e5ff88" onerror="this.style.display='none'">
      <div class="hr-pred" id="hrPred" style="color:{pcolor}">{pred_label}</div>
    </div>
    <div class="hr-bar"><div class="hr-bar-fill" id="hrBar" style="width:{dtc}%"></div></div>
    <div class="hr-conf" id="hrConf">TIN CAY: {dtc}%</div>
  </div>
  <img src="{WIDGET_CHAR_IMG}" class="hr-char" alt="robot" onclick="var p=document.getElementById('hrPanel');p.style.display=(p.style.display==='none')?'block':'none'" title="An/Hien ket qua">
</div>
<div id="robotShow" onclick="this.style.display='none';document.getElementById('homeRobot').style.display='flex'">🤖</div>
<button class="tool-v2-btn" id="toolV2Btn" onclick="toggleV2()">TOOL V2</button>
<div class="mini-tool-btn" id="miniToolBtn" onclick="toggleRadial()" title="Chon tool"><img src="data:image/png;base64,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"></div>
<div class="radial-menu" id="radialMenu">{radial_items_p}</div>
<script>
var currentTool = "{tool_id}";
var lastPhien = "";
var analyzing = false;
var v2mode = false;
var TOOL_IMGS = {tool_imgs_js};
var TOOL_WEB = {tool_web_js};
var TOOL_NAMES = {tool_names_js};
function invPred(p){{ if(p==='TAI')return 'XIU'; if(p==='XIU')return 'TAI'; if(p==='PLAYER')return 'BANKER'; if(p==='BANKER')return 'PLAYER'; return p; }}
function toggleV2(){{ v2mode=!v2mode; var b=document.getElementById('toolV2Btn'); if(b){{ b.classList.toggle('active',v2mode); b.textContent=v2mode?'V2: DAO':'TOOL V2'; }} if(currentTool) selectTool(currentTool); }}
function selectTool(id){{
  currentTool = id;
  document.getElementById('hrDropdown').classList.remove('show');
  fetch('/api/pred/'+id).then(function(r){{return r.json()}}).then(function(d){{
    if(d.pred && d.pred!=='?'){{
      if(lastPhien && d.phien!==lastPhien && !analyzing){{
        analyzing=true;
        var hp=document.getElementById('hrPred'); hp.textContent='DANG PHAN TICH...'; hp.className='hr-pred analyzing-text';
        document.getElementById('hrConf').textContent='DANG CAP NHAT...';
        setTimeout(function(){{ analyzing=false; if(currentTool) selectTool(currentTool); }}, 5000);
      }}
      lastPhien = d.phien;
      if(analyzing){{ return; }}
      var hp2=document.getElementById('hrPred'); hp2.className='hr-pred';
      document.getElementById('hrPhien').textContent = d.phien;
      var showPred = v2mode ? invPred(d.pred) : d.pred;
      var p=document.getElementById('hrPred'); p.textContent=showPred + (v2mode?' [V2]':'');
      p.style.color = (showPred==='TAI'||showPred==='BANKER')?'#ff3355':'#00ffaa';
      document.getElementById('hrConf').textContent='TIN CAY: '+d.dtc+'%';
      var hb=document.getElementById('hrBar'); if(hb) hb.style.width=d.dtc+'%';
      var nm = TOOL_NAMES[id]||id;
      var wl = TOOL_WEB[id];
      document.getElementById('hrName').innerHTML = wl ? '<a href="'+wl+'" target="_blank" style="color:#86efac;text-decoration:none">'+nm+'</a>' : nm;
      var img=document.getElementById('hrToolImg'); var im=TOOL_IMGS[id]; if(im){{img.src=im;img.style.display='block';}}
      document.querySelectorAll('#hrDropdown a').forEach(function(a){{a.style.background='transparent';}});
    }}
  }}).catch(function(){{}});
}}
setInterval(function(){{ if(currentTool) selectTool(currentTool); }}, 2000);
(function(){{var w=document.getElementById('homeRobot'),d=false,sx=0,sy=0;
function dn(e){{var t=e.touches?e.touches[0]:e;if(e.target.tagName==='A'||e.target.tagName==='BUTTON')return;d=true;sx=t.clientX-w.offsetLeft;sy=t.clientY-w.offsetTop;e.preventDefault();}}
function mv(e){{if(!d)return;var t=e.touches?e.touches[0]:e;w.style.left=(t.clientX-sx)+'px';w.style.top=(t.clientY-sy)+'px';w.style.right='auto';if(e.touches)e.preventDefault();}}
function up(){{d=false;}}
w.addEventListener('mousedown',dn);w.addEventListener('touchstart',dn,{{passive:false}});
document.addEventListener('mousemove',mv);document.addEventListener('touchmove',mv,{{passive:false}});
document.addEventListener('mouseup',up);document.addEventListener('touchend',up);}})();

function toggleRadial(){{
  var btn=document.getElementById('miniToolBtn');
  var menu=document.getElementById('radialMenu');
  var items=menu.querySelectorAll('.radial-item');
  var rect=btn.getBoundingClientRect();
  menu.style.left=(rect.left+rect.width/2)+'px'; menu.style.top=(rect.top+rect.height/2)+'px';
  var open=!btn.classList.contains('active');
  btn.classList.toggle('active', open);
  var n=items.length, R=118;
  for(var i=0;i<n;i++){{
    var ang=(i/n)*Math.PI*2 - Math.PI/2;
    var x=Math.cos(ang)*R, y=Math.sin(ang)*R;
    var it=items[i];
    if(open){{ it.classList.add('show'); (function(el,xx,yy,idx){{setTimeout(function(){{el.style.transform='translate(calc(-50% + '+xx+'px), calc(-50% + '+yy+'px)) scale(1)';}}, idx*60);}})(it,x,y,i); }}
    else {{ it.classList.remove('show'); it.style.transform='translate(-50%,-50%) scale(0)'; }}
  }}
}}
(function(){{var m=document.getElementById('miniToolBtn'),d=false,sx=0,sy=0,moved=false;
function dn(e){{var t=e.touches?e.touches[0]:e;d=true;moved=false;sx=t.clientX-m.offsetLeft;sy=t.clientY-m.offsetTop;e.preventDefault();}}
function mv(e){{if(!d)return;var t=e.touches?e.touches[0]:e;m.style.left=(t.clientX-sx)+'px';m.style.top=(t.clientY-sy)+'px';m.style.right='auto';m.style.bottom='auto';moved=true;if(e.touches)e.preventDefault();}}
function up(e){{d=false;}}
m.addEventListener('mousedown',dn);m.addEventListener('touchstart',dn,{{passive:false}});
document.addEventListener('mousemove',mv);document.addEventListener('touchmove',mv,{{passive:false}});
document.addEventListener('mouseup',up);document.addEventListener('touchend',up);}})();
</script>'''
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['name']} — VIP PRO</title><style>body{{margin:0;background:#071020}}</style></head><body>
<div style="position:fixed;top:0;left:0;right:0;height:38px;background:#071020;z-index:10000;display:flex;align-items:center;padding:0 10px;gap:10px;border-bottom:2px solid #7dd3fc">
<a href="/home" style="color:#7dd3fc;font-size:13px;text-decoration:none;font-weight:700">← Home</a>
<span style="color:#86efac;font-size:13px;font-weight:800;flex:1;text-align:center">{cfg['full_name']}</span>
<a href="{web}" target="_blank" rel="noopener" style="color:#7dd3fc;font-size:12px;text-decoration:none;font-weight:700">Mở tab mới ↗</a>
</div>
<iframe src="{web}" style="position:fixed;top:38px;left:0;width:100%;height:calc(100% - 38px);border:0;z-index:1;background:#fff"></iframe>
{widget}
<script><!-- auto-refresh handled by robot widget --></script>
</body></html>'''


@app.route('/tool/<tool_id>')
@require_login
@require_key
def tool_detail(tool_id):
    u = get_sess_user()
    if tool_id not in TOOLS_CONFIG:
        flash('Tool khong ton tai', 'error')
        return redirect(url_for('home'))
    cfg = TOOLS_CONFIG[tool_id]
    data = get_tool_data(tool_id)
    if not data:
        body = f'<div class="card tc"><h3>Khong lay duoc du lieu cho {cfg.get("full_name","")}</h3><a href="/home" class="btn btn-ghost mt16">Quay lai</a></div>'
        return page(cfg.get('name','Tool'), body, u)
    ls = data.get('lich_su', [])
    dd, patterns = du_doan_pro(ls, tool_id)
    body = f'<div class="flex mb16"><a href="/home" class="btn btn-ghost btn-sm">Quay lai</a>' \
           f'<h2 style="flex:1;color:#fff">{cfg.get("full_name","")}</h2>{loai_badge(cfg.get("loai","TX"))}</div>'
    if dd:
        pred = dd.get('du_doan', '?')
        dtc = dd.get('do_tin_cay', 0)
        dt = dd.get('diem_tai', 0)
        dx = dd.get('diem_xiu', 0)
        st = dd.get('so_thuat_toan_tai', 0)
        sx = dd.get('so_thuat_toan_xiu', 0)
        vt = dd.get('vip_tai', 0)
        vx = dd.get('vip_xiu', 0)
        at = dd.get('ai_tai', 0)
        ax = dd.get('ai_xiu', 0)
        mn = dd.get('thuat_toan_manh_nhat', {})
        bcls = 'c-tai' if pred == 'T' else 'c-xiu'
        plabel = 'TAI' if pred == 'T' else 'XIU'
        ring_color = '#ff3355' if pred == 'T' else '#00ffaa'
        body += f'''<div class="glow-card"><div class="tc">
<div class="pred-ball {bcls}">{plabel}</div>
<div class="engine-tag">ULTIMATE ENGINE v6.0 — 1 THUẬT TOÁN | XS TÀI {dd.get("xac_suat_tai",0.5)*100:.1f}%</div>
<div class="mt16 flex" style="justify-content:center;gap:20px">
{conf_ring(dtc, ring_color)}
<div style="text-align:left"><div class="fs12 c-dim">Do tin cay</div>
<div style="font-size:28px;font-weight:900;color:{ring_color}">{dtc}%</div>
<div class="fs12 c-dim">{dd.get("tong_mau",0)} tin hieu fusion</div></div></div>'''
        if dd.get('la_vip'): body += ' <span class="badge badge-vip">VIP</span>'
        if dd.get('la_ai'): body += ' <span class="badge badge-ai">AI</span>'
        body += ' <span class="badge badge-ultimate">ULTIMATE</span>'
        t_pct = (dt / (dt + dx) * 100) if (dt + dx) > 0 else 50
        body += f'''<div class="grid g2 mt16">
<div class="card" style="border-color:rgba(244,63,94,.2)"><div class="flex"><span style="color:#f43f5e;font-weight:800">TAI</span>
<span class="tr" style="flex:1;color:#f43f5e;font-size:20px;font-weight:900">{dt}</span></div>
<div class="sbar mt8"><div class="sbar-fill" style="width:{t_pct:.0f}%;background:linear-gradient(90deg,#ff3355,#cc1133)"></div></div>
<div class="fs10 c-dim mt8">{st} tin hieu | {vt} VIP | {at} AI</div></div>
<div class="card" style="border-color:rgba(99,102,241,.2)"><div class="flex"><span style="color:#6366f1;font-weight:800">XIU</span>
<span class="tr" style="flex:1;color:#6366f1;font-size:20px;font-weight:900">{dx}</span></div>
<div class="sbar mt8"><div class="sbar-fill" style="width:{100-t_pct:.0f}%;background:linear-gradient(90deg,#00ffaa,#00cc88)"></div></div>
<div class="fs10 c-dim mt8">{sx} tin hieu | {vx} VIP | {ax} AI</div></div></div>'''
        if mn:
            body += f'<div class="card mt8" style="border-color:rgba(251,191,36,.2)"><div class="fs10 c-dim">Tin hieu manh nhat (trong Ultimate Engine)</div>' \
                    f'<div style="color:#fbbf24;font-weight:800;font-size:14px">{mn.get("ten","")}</div>' \
                    f'<div class="fs10 c-dim">Do tin cay: {mn.get("do_tin_cay",0)}% | Du doan: {mn.get("ket_tiep","?")}</div></div>'
        body += pred_widget(tool_id, cfg,
            data.get('phien') or data.get('ma_phien') or data.get('session') or data.get('last_id') or '—',
            plabel, dtc)
        body += '</div>'
    else:
        body += '<div class="card tc"><span class="c-dim">Chua du du lieu de du doan (can >= 3 phien)</span></div>'
    body += f'<div class="card"><div class="fs12 c-dim mb8">Lich su ({len(ls)} phien)</div><div class="flex" style="flex-wrap:wrap">{hist_balls(ls)}</div></div>'
    if patterns:
        body += '<div class="card" style="overflow-x:auto"><div class="fs12 c-dim mb8">Chi tiet tin hieu trong Ultimate Engine</div><table><tr><th>Tin hieu</th><th>Du doan</th><th>Do tin cay</th><th>Loai</th></tr>'
        for p in patterns[:20]:
            kt = p.get('ket_tiep', '?')
            kc = 'c-red' if kt == 'T' else 'c-grn' if kt == 'X' else ''
            tags = ''
            if p.get('la_vip'): tags += ' <span class="badge badge-vip">VIP</span>'
            if p.get('la_ai'): tags += ' <span class="badge badge-ai">AI</span>'
            body += f'<tr><td>{p.get("ten","")}</td><td class="{kc}" style="font-weight:800">{kt}</td><td>{p.get("do_tin_cay",0)}%</td><td>{tags}</td></tr>'
        body += '</table></div>'
    body += '<script>setTimeout(()=>location.reload(),2000)</script>'
    return page(cfg.get('name', 'Tool'), body, u)

@app.route('/baccarat')
@require_login
@require_key
def baccarat():
    u = get_sess_user()
    tables = get_bcr_data()
    body = '<div class="flex mb16"><a href="/home" class="btn btn-ghost btn-sm">Quay lai</a>' \
           '<h2 style="flex:1;color:#fff">Baccarat Live</h2></div>'
    if not tables:
        body += '<div class="card tc c-dim">Khong lay duoc du lieu Baccarat</div>'
    else:
        body += f'<div class="fs12 c-dim mb16">{len(tables)} ban dang hoat dong</div><div class="grid g3">'
        for t in tables:
            ban = t.get('ban', '?')
            cau = t.get('cau', '')
            hist = t.get('history', [])
            sp = t.get('so_phien', 0)
            body += f'''<a href="/baccarat/{ban}" class="card gcard" style="text-decoration:none">
<div class="flex mb8"><span style="font-weight:800;color:#fff;font-size:16px">Ban {ban}</span>
<span class="badge badge-ai">{sp}P</span></div>
<div class="fs10 c-dim mb8">{cau}</div>
<div class="flex" style="flex-wrap:wrap">{hist_balls(hist, 15)}</div></a>'''
        body += '</div>'
    body += '<script>setTimeout(()=>location.reload(),2000)</script>'
    return page('Baccarat', body, u)

@app.route('/baccarat/<ban>')
@require_login
@require_key
def baccarat_detail(ban):
    u = get_sess_user()
    tables = get_bcr_data()
    tbl = None
    if tables:
        for t in tables:
            if str(t.get('ban', '')) == str(ban):
                tbl = t; break
    if not tbl:
        flash('Khong tim thay ban', 'error')
        return redirect(url_for('baccarat'))
    hist = tbl.get('history', [])
    dd, patterns = du_doan_bcr(hist)
    body = f'<div class="flex mb16"><a href="/baccarat" class="btn btn-ghost btn-sm">Quay lai</a>' \
           f'<h2 style="flex:1;color:#fff">Ban {ban}</h2></div>'
    if dd:
        pred = dd.get('du_doan', '?')
        dtc = dd.get('do_tin_cay', 0)
        dp = dd.get('diem_p', 0)
        db = dd.get('diem_b', 0)
        sp = dd.get('so_p', 0)
        sb = dd.get('so_b', 0)
        bcls = 'c-player' if pred == 'P' else 'c-banker'
        plabel = 'PLAYER' if pred == 'P' else 'BANKER'
        ring_color = '#00aaff' if pred == 'P' else '#ff3355'
        body += f'''<div class="glow-card"><div class="tc">
<div class="pred-ball {bcls}">{pred}</div>
<div style="font-size:14px;color:#94a3b8;margin-top:10px;font-weight:700">{plabel}</div>
<div class="engine-tag">ULTIMATE ENGINE v6.0 — 1 THUẬT TOÁN | XS PLAYER {dd.get("xac_suat_player",0.5)*100:.1f}%</div>
<div style="margin-top:6px;font-size:13px;color:#fbbf24;font-weight:800">Phieu: P:{sp} | B:{sb}</div>
<div class="mt16 flex" style="justify-content:center;gap:20px">
{conf_ring(dtc, ring_color)}
<div style="text-align:left"><div class="fs12 c-dim">Do tin cay</div>
<div style="font-size:28px;font-weight:900;color:{ring_color}">{dtc}%</div>
<div class="fs12 c-dim">{dd.get("tong_mau",0)} tin hieu fusion</div></div></div>'''
        if dd.get('la_vip'): body += ' <span class="badge badge-vip">VIP</span>'
        if dd.get('la_ai'): body += ' <span class="badge badge-ai">AI</span>'
        body += ' <span class="badge badge-ultimate">ULTIMATE</span>'
        p_pct = (dp / (dp + db) * 100) if (dp + db) > 0 else 50
        body += f'''<div class="grid g2 mt16">
<div class="card" style="border-color:rgba(59,130,246,.2)"><div class="flex"><span style="color:#3b82f6;font-weight:800">PLAYER</span>
<span class="tr" style="flex:1;color:#3b82f6;font-size:20px;font-weight:900">{dp}</span></div>
<div class="sbar mt8"><div class="sbar-fill" style="width:{p_pct:.0f}%;background:linear-gradient(90deg,#00aaff,#0077cc)"></div></div>
<div class="fs10 c-dim mt8">{sp} tin hieu</div></div>
<div class="card" style="border-color:rgba(244,63,94,.2)"><div class="flex"><span style="color:#f43f5e;font-weight:800">BANKER</span>
<span class="tr" style="flex:1;color:#f43f5e;font-size:20px;font-weight:900">{db}</span></div>
<div class="sbar mt8"><div class="sbar-fill" style="width:{100-p_pct:.0f}%;background:linear-gradient(90deg,#ff3355,#cc1133)"></div></div>
<div class="fs10 c-dim mt8">{sb} tin hieu</div></div></div>'''
        mn = dd.get('thuat_toan_manh_nhat', {})
        if mn:
            body += f'<div class="card mt8" style="border-color:rgba(251,191,36,.2)"><div class="fs10 c-dim">Tin hieu manh nhat (trong Ultimate Engine)</div>' \
                    f'<div style="color:#fbbf24;font-weight:800">{mn.get("ten","")}</div></div>'
        body += pred_widget('bcr_%s' % ban,
            {'name': 'BCR', 'full_name': 'BACCARAT — Bàn %s' % ban, 'nhom': 'BACCARAT'},
            ban, plabel, dtc, is_bcr=True)
        body += '</div>'
    else:
        body += '<div class="card tc c-dim">Chua du du lieu de du doan</div>'
    body += f'<div class="card"><div class="fs12 c-dim mb8">Lich su ({len(hist)} phien)</div>' \
            f'<div class="flex" style="flex-wrap:wrap">{hist_balls(hist)}</div></div>'
    if patterns:
        body += '<div class="card" style="overflow-x:auto"><div class="fs12 c-dim mb8">Chi tiet tin hieu trong Ultimate Engine</div><table><tr><th>Tin hieu</th><th>Du doan</th><th>Do tin cay</th><th>Loai</th></tr>'
        for p in patterns[:20]:
            kt = p.get('ket_tiep', '?')
            kc = 'color:#3b82f6' if kt == 'P' else 'color:#f43f5e' if kt == 'B' else ''
            tags = ''
            if p.get('la_vip'): tags += ' <span class="badge badge-vip">VIP</span>'
            if p.get('la_ai'): tags += ' <span class="badge badge-ai">AI</span>'
            body += f'<tr><td>{p.get("ten","")}</td><td style="{kc};font-weight:800">{kt}</td><td>{p.get("do_tin_cay",0)}%</td><td>{tags}</td></tr>'
        body += '</table></div>'
    body += '<script>setTimeout(()=>location.reload(),2000)</script>'
    return page(f'BCR Ban {ban}', body, u)


@app.route('/admin/predictions')
@require_login
@require_admin
def admin_predictions():
    u = get_sess_user()
    # Cap nhat ket qua thuc te truoc khi hien thi
    update_predictions()
    data = _pred_load()
    filter_tool = request.args.get('tool', '')
    if filter_tool:
        data = [e for e in data if e.get('tool_id') == filter_tool]
    data = sorted(data, key=lambda e: (e.get('phien', 0), e.get('created_at', '')), reverse=True)[:200]
    st = prediction_stats(filter_tool or None)
    # Tool filter links
    tool_links = '<a href="/admin/predictions" class="btn btn-sm %s">Tat ca</a>' % ('btn-primary' if not filter_tool else 'btn-ghost')
    for tid in TOOLS_CONFIG:
        cls = 'btn-primary' if filter_tool == tid else 'btn-ghost'
        tool_links += ' <a href="/admin/predictions?tool=%s" class="btn btn-sm %s">%s</a>' % (tid, cls, TOOLS_CONFIG[tid]['name'])
    body = '<div class="flex mb16"><a href="/admin" class="btn btn-ghost btn-sm">← Admin</a>' \
           '<h2 style="flex:1;color:#7dd3fc;font-family:Orbitron">LỊCH SỬ DỰ ĐOÁN</h2></div>'
    body += '<div class="grid g3 mb16">'
    body += f'<div class="card tc"><div style="font-size:28px;font-weight:900;color:#7dd3fc;font-family:Orbitron">{st["done"]}</div><div class="fs12 c-dim">Da co ket qua</div></div>'
    body += f'<div class="card tc"><div style="font-size:28px;font-weight:900;color:#00ffaa;font-family:Orbitron">{st["correct"]} / {st["wrong"]}</div><div class="fs12 c-dim">Dung / Sai</div></div>'
    body += f'<div class="card tc"><div style="font-size:28px;font-weight:900;color:#ff3355;font-family:Orbitron">{st["win_rate"]}%</div><div class="fs12 c-dim">Ty le dung | Cho: {st["pending"]}</div></div>'
    body += '</div>'
    body += f'<div class="card mb16"><div class="fs12 c-dim mb8">Loc theo tool</div><div class="flex">{tool_links}</div></div>'
    if not data:
        body += '<div class="card tc c-dim">Chua co du lieu du doan nao. Mo 1 tool va cho 2-3 phien de co du lieu.</div>'
    else:
        body += '<div class="card" style="overflow-x:auto"><table><tr><th>Tool</th><th>Phien</th><th>Du doan</th><th>Thuc te</th><th>Ket qua</th><th>Do tin cay</th><th>Thoi gian</th></tr>'
        for e in data:
            pred_lbl = 'TAI' if e.get('predicted') == 'T' else 'XIU'
            pred_cls = 'color:#ff3355;font-weight:900' if e.get('predicted') == 'T' else 'color:#00ffaa;font-weight:900'
            if e.get('actual') is None:
                act_lbl = 'CHO...'; act_cls = 'color:#888899'
                res_lbl = '<span class="badge" style="background:rgba(125,211,252,.15);color:#7dd3fc">CHO</span>'
            else:
                act_lbl = 'TAI' if e.get('actual') == 'T' else 'XIU'
                act_cls = 'color:#ff3355' if e.get('actual') == 'T' else 'color:#00ffaa'
                if e.get('correct'):
                    res_lbl = '<span class="badge" style="background:rgba(0,255,170,.2);color:#00ffaa;border:1px solid #00ffaa">✓ DUNG</span>'
                else:
                    res_lbl = '<span class="badge" style="background:rgba(255,51,85,.2);color:#ff3355;border:1px solid #ff3355">✗ SAI</span>'
            body += f'<tr><td style="color:#7dd3fc;font-weight:700">{e.get("tool_name","")}</td>' \
                    f'<td class="mono">#{e.get("phien","")}</td>' \
                    f'<td style="{pred_cls}">{pred_lbl}</td>' \
                    f'<td style="{act_cls};font-weight:700">{act_lbl}</td>' \
                    f'<td>{res_lbl}</td>' \
                    f'<td class="mono">{e.get("dtc",0)}%</td>' \
                    f'<td class="fs10 c-dim">{e.get("created_at","")}</td></tr>'
        body += '</table></div>'
    return page('Lich su du doan', body, u)


@app.route('/shop', methods=['GET', 'POST'])
@require_login
def shop():
    u = get_sess_user()
    uid = session.get('user_id')
    bal = u.get('balance', 0) if u else 0
    if request.method == 'POST':
        pkg_id = request.form.get('package', '')
        pkg = PACKAGES.get(pkg_id)
        if not pkg:
            flash('Goi key khong hop le', 'error')
            return redirect(url_for('shop'))
        if bal < pkg['price']:
            flash('So du khong du (%s). Vui long nap them.' % fmt_price(pkg['price'] - bal), 'error')
            return redirect(url_for('shop'))
        # Tru tien + tao key + active luon
        new_bal = deduct_balance(uid, pkg['price'])
        key_code, expires = create_key(pkg_id, uid)
        add_key_to_user(uid, key_code, pkg['name'], expires)
        flash('Mua key thanh cong! KEY: %s (het han %s)' % (key_code, str(expires)[:16]), 'success')
        return redirect(url_for('my_keys'))
    body = '<div class="flex mb16"><a href="/home" class="btn btn-ghost btn-sm">← Home</a>' \
           '<h2 style="flex:1;color:#7dd3fc;font-family:Orbitron">CỬA HÀNG KEY VIP</h2></div>'
    body += f'<div class="card tc mb16"><div class="fs12 c-dim">So du hien tai</div>' \
            f'<div style="font-size:36px;font-weight:900;color:#7dd3fc;font-family:Orbitron;text-shadow:0 0 20px rgba(125,211,252,.4)">{fmt_price(bal)}</div>' \
            f'<a href="/payment" class="btn btn-primary btn-sm mt8">+ Nap them tien</a></div>'
    body += '<div class="grid g2">'
    for pid, pkg in PACKAGES.items():
        du = bal >= pkg['price']
        btn_cls = 'btn-green' if du else 'btn-ghost'
        btn_txt = 'Mua ngay (du tien)' if du else 'Khong du tien'
        disabled = '' if du else 'disabled onclick="return false" style="opacity:.4;cursor:not-allowed"'
        body += f'''<div class="card" style="border-color:rgba(125,211,252,.3)">
<div class="flex mb8"><span style="font-weight:800;color:#7dd3fc;font-size:18px;font-family:Orbitron">{pkg["name"]}</span>
<span class="badge badge-vip">{pkg["days"]} ngay</span></div>
<div style="font-size:28px;font-weight:900;color:#fff;margin:12px 0;font-family:Orbitron">{fmt_price(pkg["price"])}</div>
<form method="post"><input type="hidden" name="package" value="{pid}">
<button type="submit" class="btn {btn_cls}" style="width:100%;justify-content:center" {disabled}>{btn_txt}</button>
</form></div>'''
    body += '</div>'
    body += '<div class="card mt16"><div class="fs12 c-dim">Sau khi mua thanh cong, KEY se duoc kich hoat LUON tai khoan va luu o muc <a href="/my-keys">Key cua toi</a>.</div></div>'
    return page('Cua hang Key', body, u)

# ══════════════════════════════════════
# PAYMENT & KEY
# ══════════════════════════════════════
@app.route('/payment')
@require_login
def payment():
    u = get_sess_user()
    body = '<div class="flex mb16"><h2 style="flex:1;color:#7dd3fc;font-family:Orbitron">MUA KEY VIP PRO</h2><a href="/shop" class="btn btn-green btn-sm">→ Mua bang SO DU (da nap)</a></div><div class="grid g2">'
    for pid, pkg in PACKAGES.items():
        body += f'''<div class="card"><div class="flex mb8"><span style="font-weight:800;color:#fff">{pkg["name"]}</span>
<span class="badge badge-vip">{pkg["days"]} ngay</span></div>
<div style="font-size:24px;font-weight:900;color:#fbbf24;margin:12px 0">{fmt_price(pkg["price"])}</div>
<a href="/deposit?pkg={pid}" class="btn btn-primary btn-sm" style="width:100%;justify-content:center">Mua ngay</a></div>'''
    body += '</div>'
    uid = session.get('user_id')
    deps = get_user_deposits(uid)
    if deps:
        body += '<div class="card mt16"><div class="fs12 c-dim mb8">Lich su nap tien</div><table><tr><th>Ma CK</th><th>So tien</th><th>Trang thai</th><th>Ngay</th></tr>'
        for d in deps[:10]:
            st_cls = 'c-grn' if d.get('status') == 'approved' else ('c-red' if d.get('status') == 'rejected' else 'color:#fbbf24')
            st_txt = 'Da duyet' if d.get('status') == 'approved' else ('Tu choi' if d.get('status') == 'rejected' else 'Cho duyet')
            body += f'<tr><td class="mono">{d.get("transfer_code","")}</td><td>{fmt_price(d.get("amount",0))}</td><td style="{st_cls};font-weight:700">{st_txt}</td><td class="fs10 c-dim">{d.get("created_at","")[:16]}</td></tr>'
        body += '</table></div>'
    return page('Mua Key', body, u)

@app.route('/deposit', methods=['GET', 'POST'])
@require_login
def deposit():
    u = get_sess_user()
    uid = session.get('user_id')
    if request.method == 'POST':
        pkg_id = request.form.get('package', '')
        pkg = PACKAGES.get(pkg_id)
        if not pkg:
            flash('Goi khong hop le', 'error')
            return redirect(url_for('payment'))
        did, tc = create_deposit(uid, pkg['price'], pkg_id)
        flash(f'Tao lenh nap thanh cong! Ma CK: {tc}', 'success')
        return redirect(url_for('deposit_qr', did=did))
    pkg_id = request.args.get('pkg', '')
    pkg = PACKAGES.get(pkg_id)
    if not pkg:
        flash('Goi khong hop le', 'error')
        return redirect(url_for('payment'))
    body = f'''<div style="max-width:500px;margin:0 auto"><div class="card">
<h2 class="tc mb16" style="color:#fff">Xac nhan nap tien</h2>
<div class="tc mb16"><div class="fs12 c-dim">Goi da chon</div>
<div style="font-size:20px;font-weight:900;color:#fbbf24">{pkg["name"]} - {fmt_price(pkg["price"])}</div></div>
<form method="post"><input type="hidden" name="package" value="{pkg_id}">
<button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">Tao lenh nap</button>
</form><a href="/payment" class="btn btn-ghost btn-sm mt16" style="width:100%;justify-content:center">Quay lai</a>
</div></div>'''
    return page('Nap tien', body, u)

@app.route('/deposit/qr/<int:did>')
@require_login
def deposit_qr(did):
    u = get_sess_user()
    deps = get_user_deposits(session.get('user_id'))
    dep = None
    for d in deps:
        if d.get('deposit_id') == did:
            dep = d; break
    if not dep:
        flash('Khong tim thay lenh nap', 'error')
        return redirect(url_for('payment'))
    tc = dep.get('transfer_code', '')
    amt = dep.get('amount', 0)
    body = f'''<div style="max-width:500px;margin:0 auto"><div class="glow-card tc">
<h2 class="mb16" style="color:#fff">Chuyen khoan</h2>
<img src="{QR_ZALOPAY}" style="width:220px;border-radius:12px;margin-bottom:16px" onerror="this.style.display='none'">
<div class="card" style="text-align:left">
<div class="mb8"><span class="fs12 c-dim">So tien:</span> <span style="color:#00ffaa;font-weight:900;font-size:20px;font-family:Orbitron">{fmt_price(amt)}</span></div>
<div class="mb8"><span class="fs12 c-dim">Ma CK:</span> <span class="mono" style="color:#7dd3fc;font-weight:900;font-size:18px">{tc}</span></div>
<div><span class="fs12 c-dim">Noi dung CK:</span> <span class="mono" style="color:#ff3355;font-weight:900;font-size:18px">{tc}</span></div></div>
<p class="fs12 c-dim mt16">Vui long chuyen khoan dung noi dung. Admin se duyet trong 5-15 phut.</p>
<a href="/payment" class="btn btn-ghost mt16">Quay lai</a></div></div>'''
    return page('Chuyen khoan', body, u)

@app.route('/activate-key', methods=['GET', 'POST'])
@require_login
def activate_key_page():
    u = get_sess_user()
    uid = session.get('user_id')
    if request.method == 'POST':
        kv = request.form.get('key_value', '').strip()
        if not kv:
            flash('Vui long nhap key', 'error')
            return redirect(url_for('activate_key_page'))
        ok, msg = activate_key(uid, kv)
        if ok: flash('Kich hoat key thanh cong!', 'success')
        else: flash(msg, 'error')
        return redirect(url_for('activate_key_page'))
    ck = check_key(uid)
    key_info = ''
    if ck:
        exp = ck.get('expires_at', '')[:16]
        key_info = f'<div class="card mb16" style="border-color:rgba(34,197,94,.3)"><div class="flex"><span class="badge badge-vip">DANG HOAT DONG</span>' \
                   f'<span class="c-grn" style="font-weight:700">{ck.get("package_name","")}</span></div>' \
                   f'<div class="fs12 c-dim mt8">Key: <span class="mono">{ck.get("key_value","")}</span> | Het han: {exp}</div></div>'
    body = f'''<div style="max-width:450px;margin:0 auto"><h2 class="tc mb16" style="color:#fff">Kich hoat Key</h2>{key_info}
<div class="card"><form method="post"><label>Nhap key</label><input name="key_value" placeholder="VD: ABC123" required>
<button type="submit" class="btn btn-primary" style="width:100%;justify-content:center">Kich hoat</button></form></div>
<div class="tc mt16"><a href="/payment" class="btn btn-ghost btn-sm">Mua key moi</a></div></div>'''
    return page('Kich hoat Key', body, u)

@app.route('/my-keys')
@require_login
def my_keys():
    u = get_sess_user()
    uid = session.get('user_id')
    ck = check_key(uid)
    kh = u.get('keys_history', []) if u else []
    body = '<h2 class="mb16" style="color:#fff">Key cua toi</h2>'
    if ck:
        body += f'<div class="card" style="border-color:rgba(34,197,94,.3)"><span class="badge badge-vip">ACTIVE</span> ' \
                f'<span class="mono" style="color:#fbbf24;font-weight:700">{ck.get("key_value","")}</span> ' \
                f'<span class="c-dim fs12">| {ck.get("package_name","")} | Het han: {ck.get("expires_at","")[:16]}</span></div>'
    if kh:
        body += '<div class="card" style="overflow-x:auto"><table><tr><th>Key</th><th>Goi</th><th>Ngay KH</th><th>Het han</th></tr>'
        for k in reversed(kh[-10:]):
            body += f'<tr><td class="mono">{k.get("key_value","")}</td><td>{k.get("package_type","")}</td>' \
                    f'<td class="fs10">{k.get("activated_at","")[:16]}</td><td class="fs10">{k.get("expires_at","")[:16]}</td></tr>'
        body += '</table></div>'
    else:
        body += '<div class="card tc c-dim">Chua co key nao</div>'
    return page('Key cua toi', body, u)

# ══════════════════════════════════════
# ADMIN
# ══════════════════════════════════════
@app.route('/admin')
@require_login
@require_admin
def admin():
    u = get_sess_user()
    s = stats()
    body = f'''<h2 class="mb16" style="color:#fff">Admin Dashboard</h2>
<div class="grid g3">
<div class="card tc"><div style="font-size:28px;font-weight:900;color:#818cf8">{s.get("total_users",0)}</div><div class="fs12 c-dim">Thanh vien</div></div>
<div class="card tc"><div style="font-size:28px;font-weight:900;color:#4ade80">{s.get("active_keys",0)}</div><div class="fs12 c-dim">Key hoat dong</div></div>
<div class="card tc"><div style="font-size:28px;font-weight:900;color:#fbbf24">{s.get("pending_deposits",0)}</div><div class="fs12 c-dim">Cho duyet</div></div>
<div class="card tc"><div style="font-size:28px;font-weight:900;color:#f43f5e">{fmt_price(s.get("total_amount",0))}</div><div class="fs12 c-dim">Tong nap</div></div>
</div>
<div class="flex mt16"><a href="/admin/users" class="btn btn-primary btn-sm">Thanh vien</a>
<a href="/admin/keys" class="btn btn-ghost btn-sm">Keys</a>
<a href="/admin/deposits" class="btn btn-ghost btn-sm">Nap tien</a>
<a href="/admin/create-key" class="btn btn-ghost btn-sm">Tao Key</a>
<a href="/admin/predictions" class="btn btn-green btn-sm">Lich su du doan</a></div>'''
    return page('Admin', body, u)

@app.route('/admin/users')
@require_login
@require_admin
def admin_users():
    u = get_sess_user()
    users = get_all_users()
    body = '<div class="flex mb16"><a href="/admin" class="btn btn-ghost btn-sm">Quay lai</a><h2 style="flex:1;color:#fff">Thanh vien</h2></div>'
    body += '<div class="card" style="overflow-x:auto"><table><tr><th>ID</th><th>Username</th><th>Ho ten</th><th>So du</th><th>Admin</th><th>Ngay tao</th></tr>'
    for usr in users:
        adm = '<span class="badge badge-vip">ADMIN</span>' if usr.get('is_admin') else ''
        body += f'<tr><td>{usr.get("user_id","")}</td><td style="font-weight:700;color:#fff">{usr.get("username","")}</td>' \
                f'<td>{usr.get("full_name","")}</td><td style="color:#4ade80">{fmt_price(usr.get("balance",0))}</td>' \
                f'<td>{adm}</td><td class="fs10 c-dim">{usr.get("created_at","")[:16]}</td></tr>'
    body += '</table></div>'
    return page('Thanh vien', body, u)

@app.route('/admin/keys')
@require_login
@require_admin
def admin_keys():
    u = get_sess_user()
    keys = get_all_keys()
    body = '<div class="flex mb16"><a href="/admin" class="btn btn-ghost btn-sm">Quay lai</a><h2 style="flex:1;color:#fff">Keys</h2>' \
           '<a href="/admin/create-key" class="btn btn-primary btn-sm">Tao Key</a></div>'
    body += '<div class="card" style="overflow-x:auto"><table><tr><th>Key</th><th>Goi</th><th>User</th><th>Active</th><th>Het han</th></tr>'
    for k in reversed(keys[-30:]):
        act = '<span class="c-grn" style="font-weight:700">Co</span>' if k.get('is_active') else '<span class="c-dim">Khong</span>'
        body += f'<tr><td class="mono" style="color:#fbbf24;font-weight:700">{k.get("key_value","")}</td>' \
                f'<td>{k.get("package_name","")}</td><td>{k.get("user_id","--")}</td><td>{act}</td>' \
                f'<td class="fs10 c-dim">{k.get("expires_at","")[:16]}</td></tr>'
    body += '</table></div>'
    return page('Keys', body, u)

@app.route('/admin/create-key', methods=['GET', 'POST'])
@require_login
@require_admin
def admin_create_key():
    u = get_sess_user()
    if request.method == 'POST':
        pkg = request.form.get('package', '')
        if pkg not in PACKAGES:
            flash('Goi khong hop le', 'error')
            return redirect(url_for('admin_create_key'))
        result = create_key(pkg)
        if result:
            kv, exp = result
            flash(f'Tao key thanh cong: {kv} (het han: {exp[:16]})', 'success')
        else:
            flash('Loi tao key', 'error')
        return redirect(url_for('admin_create_key'))
    body = '''<div style="max-width:450px;margin:0 auto"><div class="flex mb16"><a href="/admin" class="btn btn-ghost btn-sm">Quay lai</a>
<h2 style="flex:1;color:#fff">Tao Key Moi</h2></div><div class="card">
<form method="post"><label>Chon goi</label><select name="package">'''
    for pid, pkg in PACKAGES.items():
        body += f'<option value="{pid}">{pkg["name"]} - {fmt_price(pkg["price"])}</option>'
    body += '''</select><button type="submit" class="btn btn-primary mt8" style="width:100%;justify-content:center">Tao Key</button></form></div></div>'''
    return page('Tao Key', body, u)

@app.route('/admin/deposits')
@require_login
@require_admin
def admin_deposits():
    u = get_sess_user()
    pending = get_pending()
    body = '<div class="flex mb16"><a href="/admin" class="btn btn-ghost btn-sm">Quay lai</a><h2 style="flex:1;color:#fff">Nap tien cho duyet</h2></div>'
    if not pending:
        body += '<div class="card tc c-dim">Khong co lenh nap nao dang cho</div>'
    else:
        body += '<div class="card" style="overflow-x:auto"><table><tr><th>ID</th><th>User</th><th>So tien</th><th>Ma CK</th><th>Ngay</th><th>Hanh dong</th></tr>'
        for d in pending:
            body += f'<tr><td>{d.get("deposit_id","")}</td><td>{d.get("user_id","")}</td>' \
                    f'<td style="color:#4ade80;font-weight:700">{fmt_price(d.get("amount",0))}</td>' \
                    f'<td class="mono">{d.get("transfer_code","")}</td><td class="fs10">{d.get("created_at","")[:16]}</td>' \
                    f'<td><a href="/admin/approve/{d.get("deposit_id","")}" class="btn btn-green btn-sm">Duyet</a> ' \
                    f'<a href="/admin/reject/{d.get("deposit_id","")}" class="btn btn-rose btn-sm">Tu choi</a></td></tr>'
        body += '</table></div>'
    return page('Nap tien', body, u)

@app.route('/admin/approve/<int:did>')
@require_login
@require_admin
def admin_approve(did):
    ok, msg = approve_deposit(did)
    if ok: flash(msg, 'success')
    else: flash(msg, 'error')
    return redirect(url_for('admin_deposits'))

@app.route('/admin/reject/<int:did>')
@require_login
@require_admin
def admin_reject(did):
    ok, msg = reject_deposit(did)
    if ok: flash(msg, 'success')
    else: flash(msg, 'error')
    return redirect(url_for('admin_deposits'))

# ══════════════════════════════════════
# ERRORS
# ══════════════════════════════════════
@app.errorhandler(403)
def e403(e):
    return page('403', '<div class="tc" style="padding:80px 0"><div style="font-size:64px;font-weight:900;color:#f43f5e">403</div><p class="c-dim mt8">Khong co quyen truy cap</p><a href="/" class="btn btn-ghost mt16">Trang chu</a></div>'), 403

@app.errorhandler(404)
def e404(e):
    return page('404', '<div class="tc" style="padding:80px 0"><div style="font-size:64px;font-weight:900;color:#818cf8">404</div><p class="c-dim mt8">Trang khong ton tai</p><a href="/" class="btn btn-ghost mt16">Trang chu</a></div>'), 404

@app.errorhandler(500)
def e500(e):
    return page('500', '<div class="tc" style="padding:80px 0"><div style="font-size:64px;font-weight:900;color:#fbbf24">500</div><p class="c-dim mt8">Loi he thong</p><a href="/" class="btn btn-ghost mt16">Trang chu</a></div>'), 500

# ══════════════════════════════════════
# TOOL NHẬP MÃ MD5 — phân tích hash → dự đoán Tài/Xỉu
# ══════════════════════════════════════
@app.route('/md5', methods=['GET', 'POST'])
@require_key
def md5_tool():
    user = get_sess_user()
    result = None
    err = None
    md5_val = ''
    if request.method == 'POST':
        md5_val = request.form.get('md5', '').strip()
        r = du_doan_md5(md5_val)
        if 'error' in r:
            err = r['error']
        else:
            result = r
    body = '<div class="glow-card"><div class="tc">'
    body += '<div class="hero-t" style="font-size:2.2rem">MD5 ANALYZER</div>'
    body += '<div class="engine-tag">DEEP HASH SCAN · 4 CỤM 8 HEX · ENTROPY · XOR-FOLD · MARKOV</div></div></div>'
    body += '<div class="card"><form method="post">'
    body += '<label>NHẬP MÃ MD5 (32 ký tự hex):</label>'
    body += '<input name="md5" value="%s" placeholder="vd: d41d8cd98f00b204e9800998ecf8427e" style="font-family:monospace;text-transform:lowercase" maxlength="32" required>' % md5_val
    body += '<button class="btn btn-primary" type="submit">⚡ PHÂN TÍCH & DỰ ĐOÁN</button></form>'
    if err:
        body += '<div class="flash flash-e mt16">%s</div>' % err
    if result:
        cls = 'c-tai' if result['du_doan'] == 'T' else 'c-xiu'
        lbl = 'TÀI' if result['du_doan'] == 'T' else 'XỈU'
        body += '<div class="card mt16 tc">'
        body += '<div class="pred-ball %s">%s</div>' % (cls, lbl)
        body += '<div style="margin-top:14px;font-size:13px">Độ tin cậy: <b style="color:#7dd3fc">%.1f%%</b></div>' % result['do_tin_cay']
        body += '<div class="sbar mt8"><div class="sbar-fill" style="width:%.1f%%;background:linear-gradient(90deg,#8b5cf6,#7dd3fc)"></div></div>' % result['do_tin_cay']
        body += '<div class="flex mt16" style="justify-content:center;gap:24px;font-size:12px">'
        body += '<span>TÀI: <b style="color:#f87171">%.1f%%</b></span>' % result['tai_pct']
        body += '<span>XỈU: <b style="color:#60a5fa">%.1f%%</b></span>' % result['xiu_pct']
        body += '</div>'
        m = result['metrics']
        body += '<table class="mt16"><tr><th>CHỈ SỐ</th><th>GIÁ TRỊ</th></tr>'
        body += '<tr><td>Entropy</td><td class="mono">%s</td></tr>' % m['entropy']
        body += '<tr><td>Deep score</td><td class="mono">%s</td></tr>' % m['deep']
        body += '<tr><td>ViLong bit-entropy</td><td class="mono">%s</td></tr>' % m['vilong']
        body += '<tr><td>Python-standard Tài%%</td><td class="mono">%s%%</td></tr>' % m['py_tai_pct']
        body += '<tr><td>XOR all bytes</td><td class="mono">%s</td></tr>' % m['xor']
        body += '<tr><td>Tổng hex</td><td class="mono">%s</td></tr>' % m['hex_sum']
        body += '</table></div>'
    body += '</div>'
    return page('MD5 Analyzer', body, user)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
