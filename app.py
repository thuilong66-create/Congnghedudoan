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
    deduct_balance, add_key_to_user, get_user_keys, record_user_ip, get_user_by_id, get_user_by_username)
import urllib.request as _urlreq
import json as _jsonloc
from api_client import (TOOLS_CONFIG, GAME_IMAGES, LOGO_URL, QR_ZALOPAY,
    get_tool_data, get_bcr_data, tools_by_group, TOOL_WEB_LINKS, WIDGET_CHAR_IMG)
from algorithms import du_doan_tx, du_doan_bcr, du_doan_md5, du_doan_pro

def _client_ip():
    xf = request.headers.get('X-Forwarded-For', '')
    if xf:
        return xf.split(',')[0].strip()
    return request.remote_addr or '0.0.0.0'

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
            try:
                record_user_ip(res.get('user_id'), _client_ip())
            except Exception:
                pass
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
            try:
                _u = get_user_by_username(u)
                if _u:
                    record_user_ip(_u.get('user_id'), _client_ip())
            except Exception:
                pass
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
    pcolor = '#ff3355' if pred_label in ('TAI','BANKER') else '#00ffaa'
    nhom_p = cfg.get('nhom', '')
    web_link_p = TOOL_WEB_LINKS.get(nhom_p, '')
    tool_img_p = GAME_IMAGES.get(nhom_p, '')
    name_html_p = ('<a href="%s" target="_blank" style="color:#86efac;text-decoration:none">%s</a>' % (web_link_p, cfg.get('full_name','Tool'))) if web_link_p else cfg.get('full_name','Tool')
    tool_imgs_js = '{' + ','.join('"%s":"%s"' % (t['id'], GAME_IMAGES.get(t.get('nhom',''),'')) for t in all_tools_p) + '}'
    tool_web_js = '{' + ','.join('"%s":"%s"' % (t['id'], TOOL_WEB_LINKS.get(t.get('nhom',''),'')) for t in all_tools_p) + '}'
    tool_groups_js = '{' + ','.join('"%s":[%s]' % (t['id'], ','.join('"%s"'%x['id'] for x in groups_p.get(t.get('nhom',''), [t]))) for t in all_tools_p) + '}'
    tool_names_js = '{' + ','.join('"%s":"%s"' % (t['id'], t.get('full_name','')) for t in all_tools_p) + '}'
    widget = f'''
<style>
@keyframes hrIn{{from{{opacity:0;transform:translateX(40px)}}to{{opacity:1;transform:none}}}}
@keyframes hrBlink{{0%,90%,100%{{transform:scaleY(1)}}93%{{transform:scaleY(0.12)}}}}
.home-robot{{position:fixed;right:14px;top:18%;z-index:9999;display:flex;flex-direction:row-reverse;align-items:center;cursor:grab;user-select:none;touch-action:none;animation:hrIn .5s ease}}
.home-robot:active{{cursor:grabbing}}
.hr-panel{{position:relative;color:#f5f3ff;padding:14px 12px;min-width:180px;max-width:240px;margin-right:8px;text-align:left;font-family:sans-serif;
background:linear-gradient(rgba(8,6,20,0.72),rgba(8,6,20,0.72)) padding-box,linear-gradient(135deg,#ff4dd2,#c4b5fd,#ff4dd2,#7dd3fc) border-box;
border:2.5px solid transparent;
backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
clip-path:polygon(14px 0,calc(100% - 14px) 0,100% 14px,100% calc(100% - 14px),calc(100% - 14px) 100%,14px 100%,0 calc(100% - 14px),0 14px);
filter:drop-shadow(0 0 10px #ff4dd2aa) drop-shadow(0 0 28px #c4b5fd77);
animation:neonPulse 2.2s ease-in-out infinite}}
@keyframes neonPulse{{0%,100%{{filter:drop-shadow(0 0 8px #ff4dd299) drop-shadow(0 0 22px #c4b5fd66)}}50%{{filter:drop-shadow(0 0 18px #ff80e0cc) drop-shadow(0 0 40px #e9d5ff99)}}}}
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
.hr-tool-card{{padding:8px 0;border-bottom:1px solid #7dd3fc33}}
.hr-tool-card:last-child{{border-bottom:none}}
.hr-tool-name{{font-size:10px;font-weight:800;color:#86efac;letter-spacing:1px;text-align:left;margin-bottom:2px}}
.pred-ring{{display:inline-flex;align-items:center;justify-content:center;width:56px;height:56px;border-radius:50%;border:2px solid #7dd3fc;box-shadow:0 0 14px #7dd3fcaa,inset 0 0 10px #7dd3fc55;margin:6px 0;animation:ringPulse 2s ease-in-out infinite}}
@keyframes ringPulse{{0%,100%{{box-shadow:0 0 10px #7dd3fc88,inset 0 0 8px #7dd3fc44}}50%{{box-shadow:0 0 22px #7dd3fcee,inset 0 0 14px #7dd3fc77}}}}
.hr-multi{{max-height:340px;overflow-y:auto}}
.hr-char{{width:60px;height:60px;object-fit:contain;filter:drop-shadow(0 0 14px #00e5ffaa);cursor:pointer;margin-right:8px}}
.hr-close{{position:absolute;top:4px;right:8px;cursor:pointer;color:#00e5ff;font-size:14px;font-weight:900;z-index:5;line-height:1}}
#robotShow{{display:none;position:fixed;right:18px;top:20%;z-index:9999;background:#00e5ff;color:#070b16;border-radius:50%;width:46px;height:46px;align-items:center;justify-content:center;cursor:pointer;font-size:22px;box-shadow:0 0 15px #00e5ff}}
.tool-v2-btn{{position:fixed;right:14px;bottom:14px;z-index:10000;background:linear-gradient(135deg,#00e5ff,#00ffaa);color:#070b16;border:none;border-radius:20px;padding:8px 16px;font-size:12px;font-weight:900;letter-spacing:1px;cursor:pointer;box-shadow:0 0 15px #00e5ffaa;transition:all .2s}}
.tool-v2-btn.active{{background:linear-gradient(135deg,#ff4d6d,#ff9f43);color:#fff;box-shadow:0 0 15px #ff4d6daa;animation:v2Pulse 1s infinite}}

@keyframes v2Pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.06)}}}}
.analyzing-text{{color:#888!important;font-size:16px!important;letter-spacing:2px;animation:blinkText 1s infinite}}
@keyframes blinkText{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.v2-badge{{display:inline-block;background:#ff4d6d;color:#fff;font-size:9px;font-weight:900;padding:2px 6px;border-radius:6px;margin-left:4px;letter-spacing:1px}}
</style>
<div class="home-robot" id="homeRobot">
  <div class="hr-panel" id="hrPanel">
    <div class="hr-dropdown" id="hrDropdown">{menu_items_p}</div>
    <span class="hr-close" onclick="document.getElementById('homeRobot').style.display='none';document.getElementById('robotShow').style.display='flex'">✕</span>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px"><img src="data:image/png;base64,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" style="width:34px;height:34px;object-fit:contain;filter:drop-shadow(0 0 6px #7dd3fc)"><div class="hr-brand" style="margin:0">TOOL HƯNG 24/7</div></div>
    <div class="hr-title" id="hrName">{name_html_p}</div>
    <div class="hr-multi" id="hrMulti"></div>
  </div>
  <img src="{WIDGET_CHAR_IMG}" class="hr-char" alt="robot" onclick="var p=document.getElementById('hrPanel');p.style.display=(p.style.display==='none')?'block':'none'" title="An/Hien ket qua">
</div>
<div id="robotShow" onclick="this.style.display='none';document.getElementById('homeRobot').style.display='flex'">🤖</div>
<button class="tool-v2-btn" id="toolV2Btn" onclick="toggleV2()">TOOL V2</button>
<script>
var currentTool = "{tool_id}";
var lastPhien = "";
var analyzing = false;
var v2mode = false;
var TOOL_IMGS = {tool_imgs_js};
var TOOL_WEB = {tool_web_js};
var TOOL_NAMES = {tool_names_js};
var TOOL_GROUPS = {tool_groups_js};
function invPred(p){{ if(p==='TAI')return 'XIU'; if(p==='XIU')return 'TAI'; if(p==='PLAYER')return 'BANKER'; if(p==='BANKER')return 'PLAYER'; return p; }}
function toggleV2(){{ v2mode=!v2mode; var b=document.getElementById('toolV2Btn'); if(b){{ b.classList.toggle('active',v2mode); b.textContent=v2mode?'V2: DAO':'TOOL V2'; }} if(currentTool) selectTool(currentTool); }}
function selectTool(id){{
  currentTool = id;
  document.getElementById('hrDropdown').classList.remove('show');
  var group = TOOL_GROUPS[id] || [id];
  var container = document.getElementById('hrMulti');
  var nm = TOOL_NAMES[id]||id; var wl = TOOL_WEB[id];
  document.getElementById('hrName').innerHTML = wl ? '<a href="'+wl+'" target="_blank" style="color:#86efac;text-decoration:none">'+nm+'</a>' : nm;
  group.forEach(function(tid){{
    fetch('/api/pred/'+tid).then(function(r){{return r.json()}}).then(function(d){{
      if(!d.pred || d.pred==='?') return;
      var card = document.getElementById('card_'+tid);
      if(!card){{ card = document.createElement('div'); card.id='card_'+tid; card.className='hr-tool-card'; container.appendChild(card); }}
      var showPred = v2mode ? invPred(d.pred) : d.pred;
      var col = (showPred==='TAI'||showPred==='BANKER')?'#ff3355':'#00ffaa';
      var tname = TOOL_NAMES[tid]||tid;
      card.innerHTML = '<div class="hr-tool-name">'+tname+'</div>'
        + '<div class="hr-sub">PHIEN: <b>#'+d.phien+'</b></div>'
        + '<div style="display:flex;align-items:center;gap:10px"><div class="pred-ring"><span style="font-size:22px;font-weight:900;letter-spacing:1px;color:'+col+';text-shadow:0 0 10px '+col+'">'+showPred+'</span></div>'+(v2mode?'<span class="v2-badge">V2</span>':'')+'</div>'
        + '<div class="hr-bar"><div class="hr-bar-fill" style="width:'+d.dtc+'%"></div></div>'
        + '<div class="hr-conf">TIN CAY: '+d.dtc+'%</div>';
    }}).catch(function(){{}});
  }});
  Array.prototype.forEach.call(container.children, function(c){{
    var tid = c.id.replace('card_','');
    if(group.indexOf(tid)<0) c.remove();
  }});
}}
if(currentTool) selectTool(currentTool);
setInterval(function(){{ if(currentTool) selectTool(currentTool); }}, 2000);
(function(){{var w=document.getElementById('homeRobot'),d=false,sx=0,sy=0;
function dn(e){{var t=e.touches?e.touches[0]:e;if(e.target.tagName==='A'||e.target.tagName==='BUTTON')return;d=true;sx=t.clientX-w.offsetLeft;sy=t.clientY-w.offsetTop;e.preventDefault();}}
function mv(e){{if(!d)return;var t=e.touches?e.touches[0]:e;w.style.left=(t.clientX-sx)+'px';w.style.top=(t.clientY-sy)+'px';w.style.right='auto';if(e.touches)e.preventDefault();}}
function up(){{d=false;}}
w.addEventListener('mousedown',dn);w.addEventListener('touchstart',dn,{{passive:false}});
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
    body += '<div class="card" style="overflow-x:auto"><table><tr><th>ID</th><th>Username</th><th>Ho ten</th><th>So du</th><th>IP cuoi</th><th>Vi tri</th><th>Admin</th><th>Ngay tao</th></tr>'
    for usr in users:
        adm = '<span class="badge badge-vip">ADMIN</span>' if usr.get('is_admin') else ''
        body += f'<tr><td>{usr.get("user_id","")}</td><td style="font-weight:700;color:#fff">{usr.get("username","")}</td>' \
                f'<td>{usr.get("full_name","")}</td><td style="color:#4ade80">{fmt_price(usr.get("balance",0))}</td>' \
                f'<td style="font-size:10px;color:#7dd3fc">{usr.get("last_ip","-")}</td>' \
                f'<td><a href="/admin/location/{usr.get("user_id","")}" class="btn btn-ghost btn-sm" style="font-size:10px;padding:4px 8px">Ban do</a></td>' \
                f'<td>{adm}</td><td class="fs10 c-dim">{usr.get("created_at","")[:16]}</td></tr>'
    body += '</table></div>'
    return page('Thanh vien', body, u)

@app.route('/admin/location/<uid>')
@require_login
@require_admin
def admin_location(uid):
    u = get_sess_user()
    usr = get_user_by_id(uid)
    if not usr:
        flash('Khong tim thay user', 'error')
        return redirect(url_for('admin_users'))
    ip = usr.get('last_ip', '')
    info = {}
    map_html = ''
    if ip and ip not in ('0.0.0.0', '127.0.0.1'):
        try:
            url = 'http://ip-api.com/json/' + ip + '?fields=status,country,regionName,city,district,zip,lat,lon,isp,org,query,timezone'
            req = _urlreq.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with _urlreq.urlopen(req, timeout=8) as r:
                info = _jsonloc.loads(r.read().decode('utf-8'))
        except Exception as e:
            info = {'status': 'fail', 'message': str(e)}
        if info.get('status') == 'success':
            lat = info.get('lat', 0); lon = info.get('lon', 0)
            bbox = '%f,%f,%f,%f' % (lon-0.02, lat-0.02, lon+0.02, lat+0.02)
            map_html = '<iframe width="100%" height="420" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox=' + bbox + '&layer=mapnik&marker=' + str(lat) + '%2C' + str(lon) + '" style="border:2px solid #7dd3fc;border-radius:10px;margin-top:12px"></iframe>'
    body = '<div class="flex mb16"><a href="/admin/users" class="btn btn-ghost btn-sm">Quay lai</a><h2 style="flex:1;color:#fff">Vi tri tai khoan: ' + str(usr.get('username','')) + '</h2></div>'
    body += '<div class="card"><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:13px">'
    rows = [('Username', usr.get('username','')), ('Ho ten', usr.get('full_name','')), ('IP', ip or '-'),
            ('Quoc gia', info.get('country','-')), ('Tinh/Thanh', info.get('regionName','-')),
            ('Quan/Huyen', info.get('district','') or info.get('city','-')), ('Ma buu chinh', info.get('zip','-')),
            ('Nha mang (ISP)', info.get('isp','-')), ('To chuc', info.get('org','-')),
            ('Timezone', info.get('timezone','-')), ('Toa do', (str(info.get('lat','-')) + ', ' + str(info.get('lon','-'))) if info.get('lat') else '-'),
            ('Lan dang nhap cuoi', usr.get('last_login_at','-')[:16])]
    for k, v in rows:
        body += '<div style="color:#86efac;font-weight:700">' + str(k) + '</div><div style="color:#e2e8f0;word-break:break-all">' + str(v) + '</div>'
    body += '</div>' + map_html + '</div>'
    if usr.get('login_ips'):
        body += '<div class="card" style="margin-top:14px"><h3 style="color:#7dd3fc;margin-bottom:8px">Lich su IP (10 gan nhat)</h3><table><tr><th>IP</th><th>Thoi gian</th></tr>'
        for e in reversed(usr.get('login_ips', [])):
            body += '<tr><td style="color:#7dd3fc">' + str(e.get('ip','')) + '</td><td class="fs10 c-dim">' + str(e.get('time',''))[:16] + '</td></tr>'
        body += '</table></div>'
    return page('Vi tri user', body, u)

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
