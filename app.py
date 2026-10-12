#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VIP PRO ULTIMATE AI 6.0 — 1 THUẬT TOÁN DU ĐOÁN DUY NHẤT (Unified Engine)"""
import os, time
from functools import wraps
from datetime import datetime
from flask import Flask, request, redirect, url_for, session, flash, abort, jsonify
from database import (PACKAGES, BANK_INFO, register_user, login_user, get_user, check_key,
    activate_key, create_key, create_deposit, get_user_deposits, get_pending,
    approve_deposit, reject_deposit, get_all_users, get_all_keys, stats)
from api_client import (TOOLS_CONFIG, GAME_IMAGES, LOGO_URL, QR_ZALOPAY,
    get_tool_data, get_bcr_data, tools_by_group, TOOL_WEB_LINKS, WIDGET_CHAR_IMG)
from algorithms import du_doan_tx, du_doan_bcr, du_doan_md5

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vippro_ultimate_ai6_secret_2026')

# ══════════════════════════════════════
# CSS
# ══════════════════════════════════════
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#050510;color:#e2e8f0;font-family:-apple-system,system-ui,'Segoe UI',sans-serif;min-height:100vh;line-height:1.6}
body::before{content:'';position:fixed;inset:0;z-index:-1;
  background:radial-gradient(ellipse 80% 50% at 15% 20%,rgba(99,102,241,0.08),transparent 60%),
  radial-gradient(ellipse 60% 40% at 85% 80%,rgba(244,63,94,0.06),transparent 50%),
  radial-gradient(ellipse 50% 50% at 50% 50%,rgba(139,92,246,0.04),transparent 60%)}
a{color:#818cf8;text-decoration:none}a:hover{color:#a5b4fc}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px 40px}
.card{background:rgba(10,10,25,0.88);backdrop-filter:blur(24px);border:1px solid rgba(99,102,241,0.12);
  border-radius:18px;padding:24px;transition:all .3s;margin-bottom:16px}
.card:hover{border-color:rgba(99,102,241,0.3);box-shadow:0 8px 32px rgba(99,102,241,0.1);transform:translateY(-2px)}
.glow-card{position:relative;overflow:hidden;background:rgba(10,10,25,0.92);border-radius:20px;padding:28px;margin-bottom:16px}
.glow-card::before{content:'';position:absolute;inset:-2px;border-radius:20px;
  background:linear-gradient(45deg,#6366f1,#8b5cf6,#f43f5e,#fbbf24,#6366f1);
  background-size:300% 300%;animation:borderGlow 4s ease infinite;z-index:-1}
@keyframes borderGlow{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.pred-ball{width:140px;height:140px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:3.5rem;font-weight:900;position:relative;margin:0 auto}
.pred-ball::after{content:'';position:absolute;inset:-8px;border-radius:50%;
  border:2px solid currentColor;opacity:.3;animation:ringPulse 2s infinite}
.pred-ball::before{content:'';position:absolute;inset:-16px;border-radius:50%;
  border:1px solid currentColor;opacity:.15;animation:ringPulse 2s .5s infinite}
@keyframes ringPulse{0%,100%{transform:scale(1);opacity:.3}50%{transform:scale(1.08);opacity:.6}}
.c-tai{background:linear-gradient(135deg,#f43f5e,#e11d48);color:#fff;text-shadow:0 0 20px rgba(244,63,94,.5)}
.c-xiu{background:linear-gradient(135deg,#6366f1,#4f46e5);color:#fff;text-shadow:0 0 20px rgba(99,102,241,.5)}
.c-player{background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;text-shadow:0 0 20px rgba(59,130,246,.5)}
.c-banker{background:linear-gradient(135deg,#f43f5e,#dc2626);color:#fff;text-shadow:0 0 20px rgba(244,63,94,.5)}
.btn{padding:10px 24px;border-radius:12px;font-weight:700;font-size:14px;border:none;cursor:pointer;
  transition:all .2s;display:inline-flex;align-items:center;gap:6px;text-decoration:none}
.btn:active{transform:scale(.97)}
.btn-primary{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;box-shadow:0 4px 16px rgba(99,102,241,.3)}
.btn-primary:hover{box-shadow:0 6px 24px rgba(99,102,241,.5);transform:translateY(-1px)}
.btn-rose{background:linear-gradient(135deg,#f43f5e,#e11d48);color:#fff}
.btn-green{background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff}
.btn-ghost{background:rgba(255,255,255,.05);color:#94a3b8;border:1px solid rgba(255,255,255,.1)}
.btn-ghost:hover{background:rgba(255,255,255,.1)}
.btn-sm{padding:6px 14px;font-size:12px;border-radius:8px}
input,select{width:100%;padding:12px 16px;background:rgba(255,255,255,.04);border:1px solid rgba(99,102,241,.15);
  border-radius:12px;color:#e2e8f0;font-size:14px;outline:none;transition:border .2s;margin-bottom:12px}
input:focus,select:focus{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.15)}
label{display:block;font-size:12px;color:#94a3b8;margin-bottom:4px;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:12px}
th{padding:10px 12px;background:rgba(99,102,241,.08);color:#818cf8;font-size:10px;text-transform:uppercase;
  letter-spacing:.8px;border-bottom:1px solid rgba(99,102,241,.2);text-align:left}
td{padding:8px 12px;border-bottom:1px solid rgba(255,255,255,.03)}
tr:hover{background:rgba(99,102,241,.04)}
.badge{font-size:9px;font-weight:800;padding:3px 8px;border-radius:6px;letter-spacing:.5px;display:inline-block}
.badge-vip{background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#000}
.badge-ai{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}
.badge-ultimate{background:linear-gradient(135deg,#22c55e,#0ea5e9);color:#fff}
.badge-tx{background:rgba(244,63,94,.15);color:#f43f5e;border:1px solid rgba(244,63,94,.2)}
.badge-md5{background:rgba(139,92,246,.15);color:#a78bfa;border:1px solid rgba(139,92,246,.2)}
.badge-sicbo{background:rgba(59,130,246,.15);color:#60a5fa;border:1px solid rgba(59,130,246,.2)}
.badge-p{background:rgba(59,130,246,.15);color:#60a5fa}.badge-b{background:rgba(244,63,94,.15);color:#f43f5e}
.hball{width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:800;flex-shrink:0;margin:2px}
.grid{display:grid;gap:16px}.g2{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.g3{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.gcard{cursor:pointer;position:relative;overflow:hidden}
.gcard img{width:100%;height:160px;object-fit:cover;border-radius:16px 16px 0 0;display:block}
.gcard:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(99,102,241,.15)}
.flash{padding:12px 16px;border-radius:12px;font-size:13px;margin-bottom:12px}
.flash-s{background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.3);color:#4ade80}
.flash-e{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.3);color:#f87171}
.flash-w{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.3);color:#fbbf24}
.conf-ring{position:relative;width:80px;height:80px;display:inline-block}
.nav{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;flex-wrap:wrap;gap:10px;
  border-bottom:1px solid rgba(99,102,241,.1);margin-bottom:24px}
@media(max-width:768px){.g2,.g3{grid-template-columns:1fr}.nav{flex-direction:column;align-items:stretch}
  .pred-ball{width:110px;height:110px;font-size:2.8rem}.hero-t{font-size:2.2rem!important}}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.fade{animation:fadeIn .4s ease}
.mono{font-family:'SF Mono','Fira Code','Courier New',monospace}
.sbar{height:6px;border-radius:3px;background:rgba(255,255,255,.06);overflow:hidden}
.sbar-fill{height:100%;border-radius:3px;transition:width .5s}
.tc{text-align:center}.tr{text-align:right}.flex{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.mb8{margin-bottom:8px}.mb16{margin-bottom:16px}.mt8{margin-top:8px}.mt16{margin-top:16px}
.fs12{font-size:12px}.fs10{font-size:10px}.c-dim{color:#64748b}.c-grn{color:#4ade80}.c-red{color:#f87171}
.hero-t{font-size:4rem;font-weight:900;background:linear-gradient(135deg,#22c55e,#0ea5e9,#8b5cf6,#f43f5e);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1}
.engine-tag{display:inline-block;margin-top:10px;padding:6px 14px;border-radius:999px;
  background:linear-gradient(135deg,rgba(34,197,94,.15),rgba(14,165,233,.15));
  border:1px solid rgba(34,197,94,.3);color:#4ade80;font-size:11px;font-weight:800;letter-spacing:.5px}
footer{text-align:center;padding:32px 16px;color:#475569;font-size:11px;border-top:1px solid rgba(99,102,241,.08);margin-top:40px}
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
    left = '<a href="/" style="font-size:20px;font-weight:900;background:linear-gradient(135deg,#22c55e,#0ea5e9,#f43f5e);-webkit-background-clip:text;-webkit-text-fill-color:transparent">VIP PRO ULTIMATE</a>'
    right = ''
    if user:
        name = user.get('full_name') or user.get('username','')
        bal = f"{user.get('balance',0):,}d"
        kst = '<span class="badge badge-vip">VIP</span>' if check_key(user.get('user_id')) else '<span class="badge badge-tx">FREE</span>'
        links = '<a href="/home" class="btn btn-ghost btn-sm">Tools</a> <a href="/baccarat" class="btn btn-ghost btn-sm">BCR</a> <a href="/md5" class="btn btn-ghost btn-sm">MD5</a>'
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
<body>{nav_html(user)}<div class="wrap fade">{fl}{body}</div>
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
    all_tools = [t for ts in groups.values() for t in ts]
    sel = request.args.get('tool') or (all_tools[0]['id'] if all_tools else None)
    sel_name = 'VIP ROBOT'; pred_txt = '—'; conf_txt = '?'; phien_txt = '—'
    if sel and sel in TOOLS_CONFIG:
        d = get_tool_data(sel)
        if d and d.get('lich_su'):
            dd, _ = du_doan_tx(d['lich_su'])
            if dd:
                sel_name = TOOLS_CONFIG[sel]['full_name']
                pred_txt = 'TAI' if dd.get('du_doan') == 'T' else 'XIU'
                conf_txt = str(dd.get('do_tin_cay', 0))
                phien_txt = str(d.get('phien', '—'))
    pred_color = '#f43f5e' if pred_txt == 'TAI' else '#6366f1'
    pills = ''.join(
        '<a href="/home?tool=%s" style="display:inline-block;padding:2px 6px;margin:2px 2px 0 0;border-radius:6px;background:%s;color:#0f172a;font-size:9px;text-decoration:none">%s</a>'
        % (t['id'], '#22d3ee55' if t['id'] == sel else '#f1f5f9', t['name'][:10])
        for t in all_tools)
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
            web_btn = f'<a href="{TOOL_WEB_LINKS[nhom]}" target="_blank" rel="noopener" class="btn btn-primary btn-sm" style="width:100%;justify-content:center;margin-top:10px">🌐 Vào web {nhom}</a>'
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
    # Widget robot luôn hiện trên trang chủ (kéo được)
    body += f'''
<style>
@keyframes hrIn{{from{{opacity:0;transform:translateX(40px)}}to{{opacity:1;transform:none}}}}
@keyframes hrFloat{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
.home-robot{{position:fixed;right:18px;bottom:30px;z-index:9999;display:flex;align-items:center;cursor:grab;user-select:none;touch-action:none;animation:hrIn .5s ease}}
.home-robot .hr-panel{{background:#fff;color:#111;border-radius:14px;padding:10px 14px;min-width:180px;margin-right:8px;box-shadow:0 8px 30px rgba(0,0,0,.45),0 0 0 2px #22d3ee;font-family:sans-serif}}
.home-robot .hr-title{{font-size:12px;font-weight:800;color:#0f172a}}
.home-robot .hr-sub{{font-size:10px;color:#64748b;margin-top:2px}}
.home-robot img{{width:64px;height:64px;object-fit:contain;filter:drop-shadow(0 0 10px #22d3ee88);animation:hrFloat 3s ease-in-out infinite;pointer-events:none}}
</style>
<div class="home-robot" id="homeRobot">
  <div class="hr-panel" style="position:relative">
    <span onclick="document.getElementById('homeRobot').style.display='none';document.getElementById('robotShow').style.display='flex'" style="position:absolute;top:4px;right:8px;cursor:pointer;color:#94a3b8;font-size:15px;font-weight:900;line-height:1;z-index:5">✕</span>
    <div class="hr-title">{sel_name}</div>
    <div class="hr-sub">PHIEN: <b style="color:#0f172a">#{phien_txt}</b></div>
    <div style="font-size:18px;font-weight:900;color:{pred_color};margin-top:4px;text-shadow:0 0 8px {pred_color}55">{pred_txt} <span style="font-size:11px;color:#64748b;font-weight:700">{conf_txt}%</span></div>
    <div style="margin-top:6px;border-top:1px solid #e2e8f0;padding-top:4px">{pills}</div>
  </div>
  <img src="{WIDGET_CHAR_IMG}" alt="robot">
</div>
<div id="robotShow" onclick="this.style.display='none';document.getElementById('homeRobot').style.display='flex'" style="display:none;position:fixed;right:18px;bottom:30px;z-index:9999;background:#22d3ee;color:#0f172a;border-radius:50%;width:46px;height:46px;align-items:center;justify-content:center;cursor:pointer;font-size:22px;box-shadow:0 4px 15px rgba(0,0,0,.4)">🤖</div>
<script>
(function(){{var w=document.getElementById('homeRobot'),d=false,sx=0,sy=0;
function dn(e){{var t=e.touches?e.touches[0]:e;if(e.target.tagName==='A')return;d=true;sx=t.clientX-w.offsetLeft;sy=t.clientY-w.offsetTop;e.preventDefault();}}
function mv(e){{if(!d)return;var t=e.touches?e.touches[0]:e;w.style.left=(t.clientX-sx)+'px';w.style.top=(t.clientY-sy)+'px';w.style.right='auto';w.style.bottom='auto';if(e.touches)e.preventDefault();}}
function up(){{d=false;}}
w.addEventListener('mousedown',dn);w.addEventListener('touchstart',dn,{{passive:false}});
document.addEventListener('mousemove',mv);document.addEventListener('touchmove',mv,{{passive:false}});
document.addEventListener('mouseup',up);document.addEventListener('touchend',up);}})();
</script>'''
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
    tool_img_tag = f'<img src="{tool_img}" style="width:34px;height:34px;border-radius:8px;object-fit:cover;border:1px solid #ff4fd8;box-shadow:0 0 8px #ff4fd888">' if tool_img else ''
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
    pred_color = '#f43f5e' if pred_label.upper().startswith(('T', 'BANKER')) else '#6366f1'
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
.pred-widget{{position:fixed;right:14px;top:12%;z-index:9999;display:flex;flex-direction:row-reverse;align-items:center;cursor:grab;user-select:none;touch-action:none;animation:pwIn .5s ease}}
@keyframes pwIn{{from{{opacity:0;transform:translateX(40px)}}to{{opacity:1;transform:none}}}}
.pred-widget:active{{cursor:grabbing}}
.pw-char{{width:86px;height:86px;object-fit:contain;filter:drop-shadow(0 0 14px #ff4fd8aa);animation:pwFloat 3s ease-in-out infinite;pointer-events:none;margin-left:6px;z-index:2}}
@keyframes pwFloat{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
.pw-panel{{position:relative;background:linear-gradient(160deg,#1a0b2e,#2d1b4e);color:#fff;border:2px solid #ff4fd8;border-radius:14px;padding:12px 10px;min-width:108px;text-align:center;
  box-shadow:0 0 18px #ff4fd8,0 0 40px #ff4fd866,inset 0 0 18px #ff4fd822;font-family:-apple-system,system-ui,sans-serif}}
.pw-toolname{{font-size:10px;font-weight:800;color:#ffd166;border-bottom:1px solid #ff4fd844;padding-bottom:5px;margin-bottom:5px}}
.pw-toolname a{{color:#ffd166;text-decoration:none}}
.pw-session{{font-size:10px;color:#22d3ee;margin-bottom:6px}}
.pw-session b{{color:#ffd166;font-size:12px}}
.pw-pred{{font-size:30px;font-weight:900;color:{pred_color};text-shadow:0 0 12px {pred_color},0 0 24px {pred_color}88;letter-spacing:2px;line-height:1.1;margin:4px 0}}
.pw-conf{{font-size:10px;color:#22d3ee;font-weight:700}}
.pw-menu{{position:absolute;top:-14px;right:-14px;background:#0a0a0a;border:2px solid #ff4fd8;border-radius:8px;width:30px;height:30px;cursor:pointer;font-size:14px;line-height:1;color:#22d3ee;z-index:6;box-shadow:0 0 10px #ff4fd888}}
.pw-dropdown{{display:none;position:absolute;top:20px;right:-8px;background:#1a0b2e;border:1px solid #ff4fd8;border-radius:8px;overflow:hidden;box-shadow:0 6px 20px rgba(255,79,216,.4);z-index:2}}
.pw-dropdown.show{{display:block}}
.pw-dropdown a{{display:block;padding:8px 14px;color:#fff;font-size:12px;text-decoration:none;border-bottom:1px solid #ff4fd833}}
.pw-dropdown a:hover{{background:#ff4fd833;color:#ffd166}}
</style>
<div class="pred-widget" id="predWidget">
  <img src="{WIDGET_CHAR_IMG}" class="pw-char" alt="pred">
  <div class="pw-panel">
    <span onclick="document.getElementById('predWidget').style.display='none';document.getElementById('pwShow').style.display='flex'" style="position:absolute;top:4px;left:6px;cursor:pointer;color:#ff4fd8;font-size:13px;font-weight:900;z-index:5;line-height:1">✕</span>
    {menu_html}
    <div class="pw-toolname">{name_html}</div>
    <div class="pw-session">#<b id="pwPhien">{phien}</b></div>
    <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin:4px 0">{tool_img_tag}<div class="pw-pred" id="pwPred" style="margin:0">{pred_label}</div></div>
    <div class="pw-conf" id="pwConf">DO TIN CAY: {dtc}%</div>
  </div>
</div>
<div id="pwShow" onclick="this.style.display='none';document.getElementById('predWidget').style.display='flex'" style="display:none;position:fixed;right:18px;top:32%;z-index:9999;background:#22d3ee;color:#0f172a;border-radius:50%;width:46px;height:46px;align-items:center;justify-content:center;cursor:pointer;font-size:22px;box-shadow:0 4px 15px rgba(0,0,0,.4)">🤖</div>
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
    dd, _ = du_doan_tx(data['lich_su'])
    pred = 'TAI' if dd.get('du_doan') == 'T' else 'XIU'
    _p = str(data.get('phien', '—'))
    try: _p = str(int(_p) + 1)
    except: pass
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
        dd, _ = du_doan_tx(data['lich_su'])
        if dd:
            pred_label = 'TAI' if dd.get('du_doan') == 'T' else 'XIU'
            dtc = dd.get('do_tin_cay', 0)
            phien = str(data.get('phien', '—'))
    widget = pred_widget(tool_id, cfg, phien, pred_label, dtc)
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['name']} — VIP PRO</title><style>body{{margin:0;background:#0a0a19}}</style></head><body>
<div style="position:fixed;top:0;left:0;right:0;height:38px;background:#0a0a19;z-index:10000;display:flex;align-items:center;padding:0 10px;gap:10px;border-bottom:2px solid #ff4fd8">
<a href="/home" style="color:#22d3ee;font-size:13px;text-decoration:none;font-weight:700">← Home</a>
<span style="color:#ffd166;font-size:13px;font-weight:800;flex:1;text-align:center">{cfg['full_name']}</span>
<a href="{web}" target="_blank" rel="noopener" style="color:#22d3ee;font-size:12px;text-decoration:none;font-weight:700">Mở tab mới ↗</a>
</div>
<iframe src="{web}" style="position:fixed;top:38px;left:0;width:100%;height:calc(100% - 38px);border:0;z-index:1;background:#fff"></iframe>
{widget}
<script>
setInterval(function(){{
  fetch('/api/pred/{tool_id}').then(function(r){{return r.json()}}).then(function(d){{
    if(d.pred && d.pred!=='?'){{
      var pf=document.getElementById('pwPhien'); if(pf) pf.textContent=d.phien;
      var p=document.getElementById('pwPred'); if(p){{p.textContent=d.pred; p.style.color=(d.pred==='TAI')?'#f43f5e':'#6366f1';}}
      var c=document.getElementById('pwConf'); if(c) c.textContent='DO TIN CAY: '+d.dtc+'%';
    }}
  }}).catch(function(){{}});
}}, 2000);
</script>
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
    dd, patterns = du_doan_tx(ls)
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
        ring_color = '#f43f5e' if pred == 'T' else '#6366f1'
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
<div class="sbar mt8"><div class="sbar-fill" style="width:{t_pct:.0f}%;background:linear-gradient(90deg,#f43f5e,#e11d48)"></div></div>
<div class="fs10 c-dim mt8">{st} tin hieu | {vt} VIP | {at} AI</div></div>
<div class="card" style="border-color:rgba(99,102,241,.2)"><div class="flex"><span style="color:#6366f1;font-weight:800">XIU</span>
<span class="tr" style="flex:1;color:#6366f1;font-size:20px;font-weight:900">{dx}</span></div>
<div class="sbar mt8"><div class="sbar-fill" style="width:{100-t_pct:.0f}%;background:linear-gradient(90deg,#6366f1,#4f46e5)"></div></div>
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
        ring_color = '#3b82f6' if pred == 'P' else '#f43f5e'
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
<div class="sbar mt8"><div class="sbar-fill" style="width:{p_pct:.0f}%;background:linear-gradient(90deg,#3b82f6,#2563eb)"></div></div>
<div class="fs10 c-dim mt8">{sp} tin hieu</div></div>
<div class="card" style="border-color:rgba(244,63,94,.2)"><div class="flex"><span style="color:#f43f5e;font-weight:800">BANKER</span>
<span class="tr" style="flex:1;color:#f43f5e;font-size:20px;font-weight:900">{db}</span></div>
<div class="sbar mt8"><div class="sbar-fill" style="width:{100-p_pct:.0f}%;background:linear-gradient(90deg,#f43f5e,#dc2626)"></div></div>
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

# ══════════════════════════════════════
# PAYMENT & KEY
# ══════════════════════════════════════
@app.route('/payment')
@require_login
def payment():
    u = get_sess_user()
    body = '<h2 class="mb16" style="color:#fff">Mua Key VIP PRO</h2><div class="grid g2">'
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
<div class="card" style="text-align:left"><div class="mb8"><span class="fs12 c-dim">Ngan hang:</span> <span style="color:#fff;font-weight:700">{BANK_INFO.get("bank_name","")}</span></div>
<div class="mb8"><span class="fs12 c-dim">So TK:</span> <span class="mono" style="color:#fbbf24;font-weight:700;font-size:18px">{BANK_INFO.get("account_number","")}</span></div>
<div class="mb8"><span class="fs12 c-dim">Chu TK:</span> <span style="color:#fff;font-weight:700">{BANK_INFO.get("account_name","")}</span></div>
<div class="mb8"><span class="fs12 c-dim">So tien:</span> <span style="color:#4ade80;font-weight:900;font-size:18px">{fmt_price(amt)}</span></div>
<div><span class="fs12 c-dim">Noi dung CK:</span> <span class="mono" style="color:#f43f5e;font-weight:900;font-size:18px">{tc}</span></div></div>
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
<a href="/admin/create-key" class="btn btn-ghost btn-sm">Tao Key</a></div>'''
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
        body += '<div style="margin-top:14px;font-size:13px">Độ tin cậy: <b style="color:#22d3ee">%.1f%%</b></div>' % result['do_tin_cay']
        body += '<div class="sbar mt8"><div class="sbar-fill" style="width:%.1f%%;background:linear-gradient(90deg,#8b5cf6,#22d3ee)"></div></div>' % result['do_tin_cay']
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
