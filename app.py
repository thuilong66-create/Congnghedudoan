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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Design tokens ── */
:root{
  --gold:#ffd700;--gold-2:#f0c040;--gold-dim:rgba(255,215,0,.1);--gold-glow:rgba(255,215,0,.28);
  --rose:#ff3355;--rose-dim:rgba(255,51,85,.12);
  --green:#00ffaa;--green-dim:rgba(0,255,170,.12);
  --blue:#00aaff;--blue-dim:rgba(0,170,255,.12);
  --purple:#818cf8;
  --bg:#06060a;--surface:rgba(12,12,18,.92);--surface-2:rgba(20,20,30,.7);
  --border:rgba(255,215,0,.1);--border-h:rgba(255,215,0,.42);
  --text:#eceae2;--text-2:#888899;--text-3:#3d3d50;
  --r:16px;--r-sm:10px;--r-xs:7px;
  --shadow-gold:0 0 24px rgba(255,215,0,.18);
  --trans:.22s cubic-bezier(.4,0,.2,1);
}

/* ── Reset & base ── */
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;
  min-height:100vh;line-height:1.6;overflow-x:hidden;position:relative}
body::before{content:'';position:fixed;inset:0;z-index:-2;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 45% at 10% 15%,rgba(255,215,0,.055),transparent 55%),
    radial-gradient(ellipse 55% 38% at 88% 85%,rgba(255,51,85,.04),transparent 50%),
    radial-gradient(ellipse 45% 45% at 52% 52%,rgba(0,255,170,.025),transparent 58%)}
body::after{content:'';position:fixed;top:0;left:0;right:0;height:2px;z-index:9998;pointer-events:none;
  background:linear-gradient(90deg,transparent 0%,var(--gold) 50%,transparent 100%);
  background-size:220% 100%;animation:scanLine 5s linear infinite;opacity:.5}
@keyframes scanLine{0%{background-position:220% 0}100%{background-position:-220% 0}}

/* ── Sparkles ── */
.sparkle{position:fixed;width:3px;height:3px;background:var(--gold);border-radius:50%;
  pointer-events:none;z-index:1;box-shadow:0 0 5px var(--gold),0 0 10px rgba(255,215,0,.45);
  animation:sparkleUp linear infinite;opacity:0}
@keyframes sparkleUp{0%{transform:translateY(100vh) rotate(0deg);opacity:0}8%{opacity:.7}
  88%{opacity:.5}100%{transform:translateY(-8vh) rotate(360deg);opacity:0}}

/* ── Links ── */
a{color:var(--gold);text-decoration:none;transition:color var(--trans),text-shadow var(--trans)}
a:hover{color:#fff5b0;text-shadow:0 0 8px rgba(255,215,0,.45)}

/* ── Layout ── */
.wrap{max-width:1100px;margin:0 auto;padding:0 18px 48px;position:relative;z-index:2}

/* ── Cards ── */
.card{background:var(--surface);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border:1px solid var(--border);border-radius:var(--r);padding:22px;
  transition:border-color var(--trans),box-shadow var(--trans),transform var(--trans);margin-bottom:16px}
.card:hover{border-color:var(--border-h);box-shadow:0 6px 28px rgba(255,215,0,.1),0 0 16px rgba(255,215,0,.04);transform:translateY(-2px)}

.glow-card{position:relative;overflow:hidden;background:var(--surface);border-radius:20px;padding:28px;margin-bottom:16px}
.glow-card::before{content:'';position:absolute;inset:-2px;border-radius:20px;z-index:-1;
  background:linear-gradient(45deg,var(--gold),var(--gold-2),var(--rose),var(--green),var(--gold));
  background-size:320% 320%;animation:borderGlow 5.5s ease infinite}
@keyframes borderGlow{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

/* ── Prediction balls ── */
.pred-ball{width:140px;height:140px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:3.2rem;font-weight:900;position:relative;margin:0 auto;
  font-family:'Orbitron',sans-serif}
.pred-ball::after{content:'';position:absolute;inset:-8px;border-radius:50%;
  border:2px solid currentColor;opacity:.35;animation:ringPulse 2s ease-in-out infinite}
.pred-ball::before{content:'';position:absolute;inset:-17px;border-radius:50%;
  border:1px solid currentColor;opacity:.18;animation:ringPulse 2s .6s ease-in-out infinite}
@keyframes ringPulse{0%,100%{transform:scale(1);opacity:.25}50%{transform:scale(1.07);opacity:.55}}

.c-tai{background:linear-gradient(135deg,#ff3355,#c4102e);color:#fff;text-shadow:0 0 18px rgba(255,51,85,.7)}
.c-xiu{background:linear-gradient(135deg,#00ffaa,#00b87a);color:#06060a;text-shadow:0 0 18px rgba(0,255,170,.7)}
.c-player{background:linear-gradient(135deg,#00aaff,#006fcc);color:#fff;text-shadow:0 0 18px rgba(0,170,255,.7)}
.c-banker{background:linear-gradient(135deg,#ff3355,#c4102e);color:#fff;text-shadow:0 0 18px rgba(255,51,85,.7)}

/* ── Buttons ── */
.btn{padding:9px 22px;border-radius:var(--r-sm);font-weight:700;font-size:14px;
  border:1px solid rgba(255,215,0,.28);cursor:pointer;transition:all var(--trans);
  display:inline-flex;align-items:center;gap:6px;text-decoration:none;
  background:rgba(255,215,0,.04);color:var(--gold);white-space:nowrap}
.btn:active{transform:scale(.96)}
.btn-primary{background:linear-gradient(135deg,var(--gold),var(--gold-2));color:#06060a;
  border-color:var(--gold);box-shadow:0 3px 14px rgba(255,215,0,.32);font-weight:900}
.btn-primary:hover{box-shadow:0 5px 24px rgba(255,215,0,.52);transform:translateY(-1px);color:#06060a}
.btn-rose{background:linear-gradient(135deg,var(--rose),#bb0f2a);color:#fff;border-color:var(--rose)}
.btn-rose:hover{box-shadow:0 4px 18px rgba(255,51,85,.4);transform:translateY(-1px);color:#fff}
.btn-green{background:linear-gradient(135deg,var(--green),#00b87a);color:#06060a;border-color:var(--green);font-weight:900}
.btn-green:hover{box-shadow:0 4px 18px rgba(0,255,170,.4);transform:translateY(-1px);color:#06060a}
.btn-ghost{background:transparent;color:var(--text-2);border:1px solid rgba(255,215,0,.12)}
.btn-ghost:hover{background:rgba(255,215,0,.08);color:var(--gold);border-color:rgba(255,215,0,.36)}
.btn-sm{padding:5px 13px;font-size:12px;border-radius:var(--r-xs)}

/* ── Forms ── */
input,select{width:100%;padding:11px 15px;background:rgba(255,215,0,.025);
  border:1px solid rgba(255,215,0,.18);border-radius:var(--r-sm);color:var(--text);
  font-size:14px;outline:none;transition:border var(--trans),box-shadow var(--trans);
  margin-bottom:12px;font-family:'Inter',sans-serif}
input:focus,select:focus{border-color:var(--gold);box-shadow:0 0 0 3px rgba(255,215,0,.13)}
select option{background:#111118;color:var(--text)}
label{display:block;font-size:11px;color:var(--text-2);margin-bottom:4px;
  font-weight:600;letter-spacing:.4px;text-transform:uppercase}

/* ── Tables ── */
table{width:100%;border-collapse:collapse;font-size:12px}
th{padding:10px 14px;background:rgba(255,215,0,.07);color:var(--gold);font-size:10px;
  letter-spacing:.8px;border-bottom:1px solid rgba(255,215,0,.22);text-align:left;
  font-family:'Orbitron',sans-serif;font-weight:700}
td{padding:9px 14px;border-bottom:1px solid rgba(255,215,0,.045);color:#ccc8be;
  transition:background var(--trans)}
tr:hover td{background:rgba(255,215,0,.035)}
tr:nth-child(even) td{background:rgba(255,255,255,.012)}

/* ── Badges ── */
.badge{font-size:9px;font-weight:800;padding:3px 8px;border-radius:var(--r-xs);
  letter-spacing:.4px;display:inline-block;font-family:'Orbitron',sans-serif;line-height:1.4}
.badge-vip{background:linear-gradient(135deg,var(--gold),var(--gold-2));color:#06060a;
  box-shadow:0 0 10px rgba(255,215,0,.38)}
.badge-ai{background:linear-gradient(135deg,var(--green),#00b87a);color:#06060a}
.badge-ultimate{background:linear-gradient(135deg,var(--gold),var(--rose));color:#06060a}
.badge-tx{background:var(--rose-dim);color:#ff7090;border:1px solid rgba(255,51,85,.28)}
.badge-md5{background:var(--green-dim);color:var(--green);border:1px solid rgba(0,255,170,.28)}
.badge-sicbo{background:var(--blue-dim);color:var(--blue);border:1px solid rgba(0,170,255,.28)}
.badge-p{background:var(--blue-dim);color:var(--blue)}
.badge-b{background:var(--rose-dim);color:#ff7090}

/* ── History balls ── */
.hball{width:27px;height:27px;border-radius:50%;display:inline-flex;align-items:center;
  justify-content:center;font-size:10px;font-weight:800;flex-shrink:0;margin:2px;
  font-family:'Orbitron',sans-serif}

/* ── Grid ── */
.grid{display:grid;gap:16px}
.g2{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.g3{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}

/* ── Game cards ── */
.gcard{cursor:pointer;position:relative;overflow:hidden;transition:transform var(--trans),box-shadow var(--trans)}
.gcard-thumb{position:relative;overflow:hidden}
.gcard-thumb img{width:100%;height:156px;object-fit:cover;display:block;
  transition:transform .4s ease;border-radius:var(--r) var(--r) 0 0}
.gcard-thumb::after{content:'';position:absolute;inset:0;
  background:linear-gradient(to bottom,transparent 40%,rgba(6,6,10,.85));pointer-events:none}
.gcard:hover{transform:translateY(-4px);box-shadow:0 14px 40px rgba(255,215,0,.14)}
.gcard:hover .gcard-thumb img{transform:scale(1.05)}

/* ── Tool item rows ── */
.tool-row{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:var(--r-xs);
  background:rgba(255,255,255,.025);transition:background var(--trans);margin-bottom:4px;
  text-decoration:none;color:var(--text);border:1px solid transparent}
.tool-row:hover{background:rgba(255,215,0,.06);border-color:rgba(255,215,0,.18);color:var(--text)}
.tool-row-name{flex:1;font-size:13px;font-weight:600;color:#ddd9d0}

/* ── Flash messages ── */
.flash{padding:11px 16px;border-radius:var(--r-sm);font-size:13px;margin-bottom:14px;border:1px solid}
.flash-s{background:rgba(0,255,170,.07);border-color:rgba(0,255,170,.28);color:var(--green)}
.flash-e{background:rgba(255,51,85,.07);border-color:rgba(255,51,85,.28);color:#ff7090}
.flash-w{background:rgba(255,215,0,.07);border-color:rgba(255,215,0,.28);color:var(--gold)}

/* ── Confidence ring ── */
.conf-ring{position:relative;width:80px;height:80px;display:inline-block}

/* ── Navbar ── */
.nav{display:flex;align-items:center;justify-content:space-between;
  padding:12px 24px;gap:12px;position:sticky;top:0;z-index:1000;
  background:rgba(6,6,10,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(255,215,0,.12)}
.nav::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,215,0,.5),transparent)}
.nav-logo{display:flex;align-items:center;gap:10px;text-decoration:none;flex-shrink:0}
.nav-logo-icon{width:32px;height:32px;border-radius:8px;
  background:linear-gradient(135deg,var(--gold),var(--gold-2));
  display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.nav-logo-text{font-family:'Orbitron',sans-serif;font-size:13px;font-weight:900;
  background:linear-gradient(135deg,var(--gold),#fff8d0,var(--rose));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:.5px}
.nav-links{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.nav-user{font-size:12px;color:var(--text-2);white-space:nowrap}

/* ── Progress / signal bars ── */
.sbar{height:5px;border-radius:3px;background:rgba(255,215,0,.05);overflow:hidden}
.sbar-fill{height:100%;border-radius:3px;transition:width .6s ease;box-shadow:0 0 6px currentColor}

/* ── Typography helpers ── */
.tc{text-align:center}.tr{text-align:right}
.flex{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.mb8{margin-bottom:8px}.mb16{margin-bottom:16px}.mt8{margin-top:8px}.mt16{margin-top:16px}
.fs12{font-size:12px}.fs10{font-size:10px}
.c-dim{color:var(--text-2)}.c-grn{color:var(--green)}.c-red{color:#ff7090}
.mono{font-family:'JetBrains Mono',monospace}

/* ── Hero text ── */
.hero-t{font-size:3.8rem;font-weight:900;line-height:1.1;font-family:'Orbitron',sans-serif;
  background:linear-gradient(135deg,var(--gold) 0%,#fff8c0 35%,var(--rose) 65%,var(--gold) 100%);
  background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:heroShimmer 6s linear infinite}
@keyframes heroShimmer{0%{background-position:0% center}100%{background-position:200% center}}

/* ── Engine tag ── */
.engine-tag{display:inline-flex;align-items:center;gap:6px;margin-top:10px;padding:5px 14px;
  border-radius:999px;background:linear-gradient(135deg,rgba(255,215,0,.12),rgba(0,255,170,.08));
  border:1px solid rgba(255,215,0,.35);color:var(--gold);font-size:10px;font-weight:800;
  letter-spacing:.8px;font-family:'Orbitron',sans-serif;box-shadow:0 0 14px rgba(255,215,0,.12)}

/* ── Stat cards (landing) ── */
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);
  padding:24px 20px;text-align:center;transition:border-color var(--trans),box-shadow var(--trans)}
.stat-card:hover{border-color:var(--border-h);box-shadow:var(--shadow-gold)}
.stat-num{font-size:2.6rem;font-weight:900;font-family:'Orbitron',sans-serif;
  background:linear-gradient(135deg,var(--gold),#fff8c0);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-label{font-size:12px;color:var(--text-2);font-weight:600;margin-top:4px;letter-spacing:.3px}
.stat-sub{font-size:11px;color:var(--text-3);margin-top:3px}

/* ── Feature strip (landing) ── */
.feat-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:28px 0}
.feat-item{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--r-sm);
  padding:18px 16px;display:flex;align-items:flex-start;gap:12px}
.feat-icon{width:36px;height:36px;border-radius:9px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:17px}
.feat-icon-gold{background:linear-gradient(135deg,rgba(255,215,0,.2),rgba(255,215,0,.06));border:1px solid rgba(255,215,0,.25)}
.feat-icon-green{background:linear-gradient(135deg,rgba(0,255,170,.2),rgba(0,255,170,.06));border:1px solid rgba(0,255,170,.25)}
.feat-icon-blue{background:linear-gradient(135deg,rgba(0,170,255,.2),rgba(0,170,255,.06));border:1px solid rgba(0,170,255,.25)}
.feat-body h4{font-size:13px;font-weight:700;color:var(--text);margin-bottom:3px}
.feat-body p{font-size:11px;color:var(--text-2);line-height:1.5}

/* ── Section heading ── */
.sec-head{display:flex;align-items:center;gap:10px;margin-bottom:18px}
.sec-head h2{font-size:18px;font-weight:800;color:var(--text)}
.sec-line{flex:1;height:1px;background:linear-gradient(90deg,rgba(255,215,0,.3),transparent)}

/* ── Animations ── */
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.fade{animation:fadeIn .38s ease both}

/* ── Responsive ── */
@media(max-width:768px){
  .g2,.g3,.feat-strip{grid-template-columns:1fr}
  .nav{flex-direction:column;align-items:stretch;padding:10px 14px}
  .nav-links{flex-wrap:wrap}
  .pred-ball{width:110px;height:110px;font-size:2.6rem}
  .hero-t{font-size:2rem}
  .stat-num{font-size:2rem}
  .feat-item{flex-direction:column;gap:8px}
}

/* ── Footer ── */
footer{text-align:center;padding:28px 16px;color:var(--text-3);font-size:11px;
  border-top:1px solid rgba(255,215,0,.07);margin-top:48px;
  font-family:'JetBrains Mono',monospace;line-height:2}
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
    logo = '''<a href="/" class="nav-logo">
      <div class="nav-logo-icon">⚡</div>
      <span class="nav-logo-text">VIP PRO ULTIMATE</span>
    </a>'''
    if user:
        name = user.get('full_name') or user.get('username','')
        bal = f"{user.get('balance',0):,}đ"
        kst = '<span class="badge badge-vip">VIP</span>' if check_key(user.get('user_id')) else '<span class="badge badge-tx">FREE</span>'
        links = ('<a href="/home" class="btn btn-ghost btn-sm">🎮 Tools</a>'
                 '<a href="/baccarat" class="btn btn-ghost btn-sm">♦ BCR</a>'
                 '<a href="/shop" class="btn btn-primary btn-sm">🔑 Mua Key</a>'
                 '<a href="/my-keys" class="btn btn-ghost btn-sm">Key</a>')
        if user.get('is_admin'): links += '<a href="/admin" class="btn btn-ghost btn-sm">⚙ Admin</a>'
        user_info = f'<span class="nav-user">{name} · {bal} {kst}</span>'
        right = f'<div class="nav-links">{links}{user_info}<a href="/logout" class="btn btn-ghost btn-sm">Thoát</a></div>'
    else:
        right = '<div class="nav-links"><a href="/login" class="btn btn-primary btn-sm">Đăng nhập</a><a href="/register" class="btn btn-ghost btn-sm">Đăng ký</a></div>'
    return f'<nav class="nav">{logo}{right}</nav>'

def page(title, body, user=None):
    fl = ''
    msgs = session.pop('_flashes', []) if '_flashes' in session else []
    for cat, msg in msgs:
        cls = 'flash-s' if cat == 'success' else ('flash-e' if cat == 'error' else 'flash-w')
        fl += f'<div class="flash {cls}">{msg}</div>'
    sparkle_js = '''(function(){
      var c=document.getElementById("sp");
      for(var i=0;i<12;i++){
        var s=document.createElement("div"); s.className="sparkle";
        s.style.left=Math.random()*100+"vw";
        s.style.animationDuration=(18+Math.random()*12)+"s";
        s.style.animationDelay=(Math.random()*18)+"s";
        var sz=2+Math.random()*3; s.style.width=sz+"px"; s.style.height=sz+"px";
        c.appendChild(s);
      }
    })();'''
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#06060a">
  <title>{title} — VIP PRO ULTIMATE AI 6.0</title>
  <style>{CSS}</style>
</head>
<body>
<div id="sp"></div>
<script>{sparkle_js}</script>
{nav_html(user)}
<div class="wrap fade">
  {fl}
  {body}
</div>
<footer>
  VIP PRO ULTIMATE AI 6.0 &copy; 2026<br>
  Fusion Bayesian · Neural AI · FIFA-AI Layer &nbsp;|&nbsp; {len(TOOLS_CONFIG)}+ Tools TX &nbsp;|&nbsp; 60+ Bàn Baccarat
</footer>
</body>
</html>'''

def conf_ring(value, color='#ffd700'):
    v = max(0, min(100, value))
    r = 34; c = 2 * 3.14159265 * r; off = c * (1 - v / 100)
    gid = f'cg{int(v)}'
    # pick second gradient stop based on color
    c2 = '#00ffaa' if color == '#00ffaa' else ('#00aaff' if color == '#00aaff' else '#ff3355')
    return f'''<div style="width:84px;height:84px;display:inline-block;position:relative">
<svg width="84" height="84" viewBox="0 0 84 84">
  <defs>
    <linearGradient id="{gid}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <circle cx="42" cy="42" r="{r}" fill="none" stroke="rgba(255,255,255,.04)" stroke-width="8"/>
  <circle cx="42" cy="42" r="{r}" fill="none" stroke="url(#{gid})" stroke-width="8"
    stroke-dasharray="{c:.2f}" stroke-dashoffset="{off:.2f}" stroke-linecap="round"
    transform="rotate(-90 42 42)" style="filter:drop-shadow(0 0 5px {color}88)"/>
  <text x="42" y="38" text-anchor="middle" fill="{color}" font-size="15"
    font-weight="900" font-family="Orbitron,sans-serif">{v:.0f}%</text>
  <text x="42" y="51" text-anchor="middle" fill="rgba(255,255,255,.3)"
    font-size="7.5" font-family="Orbitron,sans-serif" letter-spacing="1">TIN CẬY</text>
</svg>
</div>'''

def hist_balls(history, mx=30):
    h = ''
    sl = list(history[-mx:])
    n = len(sl)
    for i, c in enumerate(sl):
        cu = str(c).upper()
        # opacity: oldest → 0.28, newest → 1.0; last ball gets scale+ring
        op = 0.28 + (i / max(n - 1, 1)) * 0.72
        is_last = (i == n - 1)
        extra = f'opacity:{op:.2f};' + ('transform:scale(1.18);box-shadow:0 0 8px currentColor;' if is_last else '')
        if cu == 'T':
            h += f'<span class="hball c-tai" style="{extra}">T</span>'
        elif cu == 'X':
            h += f'<span class="hball c-xiu" style="{extra}">X</span>'
        elif cu == 'P':
            h += f'<span class="hball c-player" style="{extra}">P</span>'
        elif cu == 'B':
            h += f'<span class="hball c-banker" style="{extra}">B</span>'
        else:
            h += f'<span class="hball" style="background:rgba(255,255,255,.07);color:#555566;{extra}">{cu}</span>'
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
    n_groups = len(groups)
    cta_primary = '/home' if u else '/register'
    cta_label = '🚀 Vào ngay' if u else '🚀 Đăng ký miễn phí'
    body = f'''
<div style="padding:56px 0 36px;text-align:center">
  <div style="display:inline-flex;align-items:center;gap:8px;padding:5px 14px;border-radius:999px;
    background:rgba(255,215,0,.08);border:1px solid rgba(255,215,0,.25);margin-bottom:20px">
    <span style="font-size:10px;font-weight:800;color:#ffd700;letter-spacing:1px;font-family:'Orbitron',sans-serif">LIVE 24/7</span>
    <span style="width:6px;height:6px;border-radius:50%;background:#00ffaa;box-shadow:0 0 6px #00ffaa;display:inline-block;animation:ringPulse 1.5s infinite"></span>
  </div>
  <div class="hero-t">VIP PRO ULTIMATE<br>AI 6.0</div>
  <p style="color:#9090a8;font-size:16px;margin-top:16px;max-width:480px;margin-left:auto;margin-right:auto;line-height:1.7">
    Một engine duy nhất — Fusion Bayesian · Neural AI · FIFA-AI Layer.<br>Dự đoán Tài Xỉu và Baccarat theo thời gian thực.
  </p>
  <div style="display:flex;gap:12px;justify-content:center;margin-top:24px;flex-wrap:wrap">
    <a href="{cta_primary}" class="btn btn-primary" style="font-size:15px;padding:13px 32px">{cta_label}</a>
    <a href="/baccarat" class="btn btn-ghost" style="font-size:15px;padding:13px 32px">♦ Baccarat Live</a>
  </div>
</div>

<div class="grid g3" style="margin-bottom:28px">
  <div class="stat-card">
    <div class="stat-num">60+</div>
    <div class="stat-label">Bàn Baccarat</div>
    <div class="stat-sub">Theo dõi trực tiếp</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">1</div>
    <div class="stat-label">Ultimate Engine</div>
    <div class="stat-sub">Fusion 4 lớp AI</div>
  </div>
  <div class="stat-card">
    <div class="stat-num">{n_tools}</div>
    <div class="stat-label">Tool Phân Tích</div>
    <div class="stat-sub">{n_groups} nhà cái</div>
  </div>
</div>

<div class="feat-strip">
  <div class="feat-item">
    <div class="feat-icon feat-icon-gold">⚡</div>
    <div class="feat-body">
      <h4>Engine Thống Nhất</h4>
      <p>Bayesian + Neural AI + FIFA-AI Layer — toàn bộ trong 1 thuật toán duy nhất, không chia tách.</p>
    </div>
  </div>
  <div class="feat-item">
    <div class="feat-icon feat-icon-green">🔄</div>
    <div class="feat-body">
      <h4>Cập Nhật Liên Tục</h4>
      <p>Dữ liệu được refresh mỗi 2 giây. Robot nền tự động dự đoán và đối chiếu kết quả 24/7.</p>
    </div>
  </div>
  <div class="feat-item">
    <div class="feat-icon feat-icon-blue">📊</div>
    <div class="feat-body">
      <h4>Lịch Sử & Thống Kê</h4>
      <p>Admin theo dõi độ chính xác từng phiên, từng tool — minh bạch, kiểm chứng được.</p>
    </div>
  </div>
</div>
'''
    return page('Trang chủ', body, u)

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
    body = '''<div class="sec-head mb16">
  <h2>Chọn Game — Nhấn vào để mở tool</h2>
  <div class="sec-line"></div>
</div>
<div class="grid g2">'''
    for nhom, tools in groups.items():
        img = GAME_IMAGES.get(nhom, '')
        tlist = ''
        for t in tools:
            play_link = f'/play/{t["id"]}' if nhom in TOOL_WEB_LINKS else f'/tool/{t["id"]}'
            tlist += (f'<a href="{play_link}" class="tool-row">'
                      f'<span class="tool-row-name">{t["name"]}</span>'
                      f'{loai_badge(t["loai"])}</a>')
        web_btn = ''
        if nhom in TOOL_WEB_LINKS:
            web_btn = (f'<a href="{TOOL_WEB_LINKS[nhom]}" target="_blank" rel="noopener" '
                       f'class="btn btn-primary btn-sm" style="width:100%;justify-content:center;margin-top:10px">'
                       f'↗ Vào web {nhom}</a>')
        img_tag = f'<div class="gcard-thumb"><img src="{img}" alt="{nhom}" onerror="this.style.display=\'none\'"></div>' if img else ''
        body += f'''<div class="card gcard" style="padding:0;overflow:hidden">
{img_tag}
<div style="padding:16px">
  <div class="flex mb8">
    <span style="font-weight:800;font-size:15px;color:#eceae2;font-family:\'Orbitron\',sans-serif;letter-spacing:.3px">{nhom}</span>
    <span class="badge badge-ai">{len(tools)}</span>
  </div>
  {tlist}
  {web_btn}
</div></div>'''

    # BCR card
    bcr_img = GAME_IMAGES.get('BACCARAT', '')
    bcr_thumb = f'<div class="gcard-thumb"><img src="{bcr_img}" alt="BCR" onerror="this.style.display=\'none\'"></div>' if bcr_img else ''
    body += f'''<div class="card gcard" style="padding:0;overflow:hidden">
{bcr_thumb}
<div style="padding:16px">
  <div class="flex mb8">
    <span style="font-weight:800;font-size:15px;color:#eceae2;font-family:\'Orbitron\',sans-serif">BACCARAT</span>
    <span class="badge badge-vip">60+ BÀN</span>
  </div>
  <p style="font-size:12px;color:#666677;margin-bottom:12px">Theo dõi trực tiếp kết quả & dự đoán P/B</p>
  <a href="/baccarat" class="btn btn-rose btn-sm" style="width:100%;justify-content:center">♦ Vào Baccarat Live</a>
</div></div>'''

    body += '</div>'
    return page('Tools', body, u)

# ══════════════════════════════════════
# WIDGET CON DỰ ĐOÁN BAY + KÉO ĐƯỢC
# ══════════════════════════════════════
def pred_widget(tool_id, cfg, phien, pred_label, dtc, is_bcr=False):
    """Widget VIP nổi: gold theme, glass panel, drag được, menu đổi tool."""
    try:
        phien = str(int(str(phien).strip()) + 1)
    except (ValueError, TypeError):
        pass
    nhom = cfg.get('nhom', '')
    web_link = TOOL_WEB_LINKS.get(nhom, '')
    tool_name = cfg.get('full_name') or cfg.get('name', 'Tool')
    tool_name_link = f'<a href="{web_link}" target="_blank" style="color:#ffd700;text-decoration:none">{tool_name}</a>' if web_link else f'<span style="color:#ffd700">{tool_name}</span>'
    # pred color
    is_tai = pred_label in ('TAI', 'T', 'BANKER')
    pred_color = '#ff3355' if is_tai else '#00ffaa'
    pred_shadow = '#ff335588' if is_tai else '#00ffaa88'
    # Hũ <-> MD5 menu
    hu_id = md5_id = None
    if '_hu' in tool_id:    hu_id = tool_id;  md5_id = tool_id.replace('_hu', '_md5')
    elif '_md5' in tool_id: md5_id = tool_id; hu_id = tool_id.replace('_md5', '_hu')
    elif '_tx' in tool_id:  hu_id = tool_id;  md5_id = tool_id.replace('_tx', '_md5')
    show_menu = (not is_bcr) and hu_id in TOOLS_CONFIG and md5_id in TOOLS_CONFIG
    menu_html = ''
    if show_menu:
        menu_html = f'''
<button class="pwm-btn" id="pwmBtn" onclick="var d=document.getElementById('pwmDrop');d.style.display=d.style.display==='block'?'none':'block'">☰</button>
<div id="pwmDrop" style="display:none;position:absolute;top:0;right:38px;background:#0c0f1a;border:1px solid rgba(255,215,0,.35);border-radius:10px;overflow:hidden;box-shadow:0 8px 28px rgba(0,0,0,.6);z-index:10;min-width:130px">
  <a href="/tool/{hu_id}" style="display:flex;align-items:center;gap:8px;padding:9px 14px;color:#eceae2;font-size:12px;text-decoration:none;border-bottom:1px solid rgba(255,215,0,.1)">🎲 TX Hũ</a>
  <a href="/tool/{md5_id}" style="display:flex;align-items:center;gap:8px;padding:9px 14px;color:#eceae2;font-size:12px;text-decoration:none">🔐 TX MD5</a>
</div>'''
    return f'''
<style>
.pw-wrap{{position:fixed;right:16px;top:14%;z-index:9990;display:flex;align-items:flex-end;
  gap:0;cursor:grab;user-select:none;touch-action:none;
  animation:pwSlideIn .45s cubic-bezier(.22,1,.36,1) both}}
.pw-wrap:active{{cursor:grabbing}}
@keyframes pwSlideIn{{from{{opacity:0;transform:translateX(60px)}}to{{opacity:1;transform:none}}}}
.pw-char-wrap{{position:relative;width:68px;flex-shrink:0}}
.pw-char{{width:68px;height:68px;object-fit:contain;
  filter:drop-shadow(0 4px 16px rgba(255,215,0,.5));cursor:pointer;display:block}}
.pw-live{{position:absolute;bottom:2px;left:50%;transform:translateX(-50%);
  display:flex;align-items:center;gap:3px;background:rgba(6,6,10,.8);
  border:1px solid rgba(0,255,170,.4);border-radius:20px;padding:2px 6px}}
.pw-live-dot{{width:5px;height:5px;border-radius:50%;background:#00ffaa;
  box-shadow:0 0 5px #00ffaa;animation:livePulse 1.4s ease-in-out infinite}}
@keyframes livePulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.4;transform:scale(.75)}}}}
.pw-live-txt{{font-size:7px;color:#00ffaa;font-weight:800;letter-spacing:.5px;font-family:"Orbitron",sans-serif}}
.pw-panel{{position:relative;background:rgba(8,10,18,.88);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border:1px solid rgba(255,215,0,.32);border-radius:14px 14px 14px 4px;
  padding:14px 14px 12px;min-width:168px;
  box-shadow:0 0 0 1px rgba(255,215,0,.08),0 12px 40px rgba(0,0,0,.55),0 0 30px rgba(255,215,0,.08)}}
.pw-panel::before{{content:'';position:absolute;inset:-1px;border-radius:14px 14px 14px 4px;
  background:linear-gradient(135deg,rgba(255,215,0,.18),transparent 60%,rgba(0,255,170,.08));
  pointer-events:none;z-index:-1}}
.pw-close{{position:absolute;top:8px;right:8px;width:20px;height:20px;cursor:pointer;
  color:rgba(255,255,255,.35);font-size:14px;line-height:20px;text-align:center;
  border-radius:50%;transition:color .2s,background .2s}}
.pw-close:hover{{color:#fff;background:rgba(255,255,255,.1)}}
.pwm-btn{{position:absolute;top:8px;right:32px;width:20px;height:20px;cursor:pointer;
  color:rgba(255,215,0,.6);font-size:11px;line-height:20px;text-align:center;
  background:none;border:none;transition:color .2s}}
.pwm-btn:hover{{color:#ffd700}}
.pw-brand{{font-size:8px;font-weight:900;color:rgba(255,215,0,.5);letter-spacing:1.5px;
  font-family:"Orbitron",sans-serif;margin-bottom:4px}}
.pw-tool{{font-size:11px;font-weight:700;margin-bottom:8px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:140px}}
.pw-divider{{height:1px;background:linear-gradient(90deg,rgba(255,215,0,.25),transparent);margin:8px 0}}
.pw-session-lbl{{font-size:9px;color:rgba(255,255,255,.35);letter-spacing:.8px;font-family:"Orbitron",sans-serif}}
.pw-session-val{{font-size:14px;font-weight:900;color:#fff;font-family:"Orbitron",sans-serif;letter-spacing:.5px}}
.pw-pred-val{{font-size:32px;font-weight:900;letter-spacing:1px;line-height:1;
  font-family:"Orbitron",sans-serif;margin:10px 0 8px}}
.pw-bar-wrap{{height:4px;background:rgba(255,255,255,.06);border-radius:2px;overflow:hidden;margin-bottom:5px}}
.pw-bar-fill{{height:100%;border-radius:2px;transition:width .5s ease}}
.pw-dtc{{font-size:9px;font-weight:700;letter-spacing:.5px;font-family:"Orbitron",sans-serif}}
.pw-show-btn{{position:fixed;right:18px;top:26%;z-index:9990;width:44px;height:44px;
  border-radius:50%;background:linear-gradient(135deg,#ffd700,#e6b800);color:#06060a;
  font-size:20px;display:none;align-items:center;justify-content:center;cursor:pointer;
  box-shadow:0 4px 18px rgba(255,215,0,.45);border:none;
  animation:pwSlideIn .45s cubic-bezier(.22,1,.36,1) both}}
</style>
<div class="pw-wrap" id="pwWrap">
  <div class="pw-char-wrap" onclick="var p=document.getElementById('pwPanel');p.style.display=p.style.display==='none'?'block':'none'">
    <img src="{WIDGET_CHAR_IMG}" class="pw-char" alt="robot">
    <div class="pw-live"><span class="pw-live-dot"></span><span class="pw-live-txt">LIVE</span></div>
  </div>
  <div class="pw-panel" id="pwPanel">
    <span class="pw-close" onclick="document.getElementById('pwWrap').style.display='none';document.getElementById('pwShowBtn').style.display='flex'">✕</span>
    {menu_html}
    <div class="pw-brand">⚡ VIP PRO TOOL</div>
    <div class="pw-tool">{tool_name_link}</div>
    <div class="pw-divider"></div>
    <div class="pw-session-lbl">PHIÊN DỰ ĐOÁN</div>
    <div class="pw-session-val" id="pwPhien">#{phien}</div>
    <div class="pw-pred-val" id="pwPred" style="color:{pred_color};text-shadow:0 0 14px {pred_shadow}">{pred_label}</div>
    <div class="pw-bar-wrap"><div class="pw-bar-fill" id="pwBar"
      style="width:{dtc}%;background:linear-gradient(90deg,{pred_color},{pred_shadow.replace('88','')})"></div></div>
    <div class="pw-dtc" id="pwDtc" style="color:{pred_color}">TIN CẬY {dtc}%</div>
  </div>
</div>
<button class="pw-show-btn" id="pwShowBtn"
  onclick="this.style.display='none';document.getElementById('pwWrap').style.display='flex'">⚡</button>
<script>
(function(){{
  var w=document.getElementById('pwWrap'),d=false,sx=0,sy=0,moved=false;
  function dn(e){{
    var t=e.touches?e.touches[0]:e;
    if(e.target.tagName==='A'||e.target.tagName==='BUTTON'||e.target.tagName==='SPAN')return;
    d=true; moved=false;
    sx=t.clientX-w.getBoundingClientRect().left;
    sy=t.clientY-w.getBoundingClientRect().top;
    w.style.right='auto';
    w.style.left=w.getBoundingClientRect().left+'px';
    w.style.top=w.getBoundingClientRect().top+'px';
    if(e.touches)e.preventDefault();
  }}
  function mv(e){{
    if(!d)return; moved=true;
    var t=e.touches?e.touches[0]:e;
    w.style.left=(t.clientX-sx)+'px';
    w.style.top=(t.clientY-sy)+'px';
    if(e.touches)e.preventDefault();
  }}
  function up(){{d=false;}}
  w.addEventListener('mousedown',dn); w.addEventListener('touchstart',dn,{{passive:false}});
  document.addEventListener('mousemove',mv); document.addEventListener('touchmove',mv,{{passive:false}});
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
    pcolor = '#ff3355'
    nhom_p = cfg.get('nhom', '')
    web_link_p = TOOL_WEB_LINKS.get(nhom_p, '')
    tool_img_p = GAME_IMAGES.get(nhom_p, '')
    name_html_p = ('<a href="%s" target="_blank" style="color:#ffd166;text-decoration:none">%s</a>' % (web_link_p, cfg.get('full_name','Tool'))) if web_link_p else cfg.get('full_name','Tool')
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
.mini-tool-btn{{position:fixed;left:14px;bottom:80px;z-index:10001;width:84px;height:84px;cursor:grab;user-select:none;touch-action:none;animation:miniIn .5s ease}}
.mini-tool-btn:active{{cursor:grabbing}}
.mini-tool-btn img{{width:84px;height:84px;object-fit:contain;filter:drop-shadow(0 0 12px #c4b5fd);animation:miniPulse 2.5s ease-in-out infinite}}
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
<div class="mini-tool-btn" id="miniToolBtn" onclick="document.getElementById('hrDropdown').classList.toggle('show')" title="Chon tool"><img src="data:image/png;base64,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"></div>
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
      p.style.color = '#ff3355';
      document.getElementById('hrConf').textContent='TIN CAY: '+d.dtc+'%';
      var hb=document.getElementById('hrBar'); if(hb) hb.style.width=d.dtc+'%';
      var nm = TOOL_NAMES[id]||id;
      var wl = TOOL_WEB[id];
      document.getElementById('hrName').innerHTML = wl ? '<a href="'+wl+'" target="_blank" style="color:#ffd166;text-decoration:none">'+nm+'</a>' : nm;
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
<title>{cfg['name']} — VIP PRO</title><style>body{{margin:0;background:#0a0a19}}</style></head><body>
<div style="position:fixed;top:0;left:0;right:0;height:38px;background:#0a0a19;z-index:10000;display:flex;align-items:center;padding:0 10px;gap:10px;border-bottom:2px solid #ffd700">
<a href="/home" style="color:#ffd700;font-size:13px;text-decoration:none;font-weight:700">← Home</a>
<span style="color:#ffd166;font-size:13px;font-weight:800;flex:1;text-align:center">{cfg['full_name']}</span>
<a href="{web}" target="_blank" rel="noopener" style="color:#ffd700;font-size:12px;text-decoration:none;font-weight:700">Mở tab mới ↗</a>
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
        flash('Tool không tồn tại', 'error')
        return redirect(url_for('home'))
    cfg = TOOLS_CONFIG[tool_id]
    data = get_tool_data(tool_id)
    if not data:
        body = f'''<div class="card tc" style="padding:48px 24px">
          <div style="font-size:40px;margin-bottom:12px">📡</div>
          <h3 style="color:#888899;margin-bottom:16px">Không lấy được dữ liệu cho {cfg.get("full_name","")}</h3>
          <a href="/home" class="btn btn-ghost">← Quay lại</a>
        </div>'''
        return page(cfg.get('name','Tool'), body, u)

    ls = data.get('lich_su', [])
    dd, patterns = du_doan_pro(ls, tool_id)
    nhom = cfg.get('nhom','')
    web_link = TOOL_WEB_LINKS.get(nhom, '')
    tool_img = GAME_IMAGES.get(nhom, '')
    phien_raw = data.get('phien') or data.get('ma_phien') or '—'

    # ── Header ──────────────────────────────────
    web_btn = f'<a href="{web_link}" target="_blank" class="btn btn-ghost btn-sm">↗ Web</a>' if web_link else ''
    body = f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;flex-wrap:wrap">
  <a href="/home" class="btn btn-ghost btn-sm">← Home</a>
  {"<img src='"+tool_img+"' style='width:36px;height:36px;border-radius:9px;object-fit:cover;border:1px solid rgba(255,215,0,.3)' onerror='this.style.display=\"none\"'>" if tool_img else ""}
  <h2 style="flex:1;color:#eceae2;font-size:17px;font-weight:800">{cfg.get("full_name","")}</h2>
  {loai_badge(cfg.get("loai","TX"))}
  {web_btn}
</div>'''

    if dd:
        pred = dd.get('du_doan', '?')
        dtc  = dd.get('do_tin_cay', 0)
        dt   = dd.get('diem_tai', 0)
        dx   = dd.get('diem_xiu', 0)
        st   = dd.get('so_thuat_toan_tai', 0)
        sx_n = dd.get('so_thuat_toan_xiu', 0)
        vt   = dd.get('vip_tai', 0)
        vx   = dd.get('vip_xiu', 0)
        at   = dd.get('ai_tai', 0)
        ax   = dd.get('ai_xiu', 0)
        mn   = dd.get('thuat_toan_manh_nhat', {})
        bcls = 'c-tai' if pred == 'T' else 'c-xiu'
        plabel = 'TÀI' if pred == 'T' else 'XỈU'
        rc = '#ff3355' if pred == 'T' else '#00ffaa'
        rc_dim = 'rgba(255,51,85,.12)' if pred == 'T' else 'rgba(0,255,170,.12)'
        xs_tai = dd.get('xac_suat_tai', 0.5) * 100
        t_pct = (dt / (dt + dx) * 100) if (dt + dx) > 0 else 50

        badges = ''
        if dd.get('la_vip'):     badges += '<span class="badge badge-vip">VIP</span> '
        if dd.get('la_ai'):      badges += '<span class="badge badge-ai">AI</span> '
        badges += '<span class="badge badge-ultimate">ULTIMATE</span>'

        # ── Main prediction glow card ────────────────
        body += f'''<div class="glow-card" style="padding:28px 24px;margin-bottom:16px">

  <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">

    {{# Left: ball + label #}}
    <div style="flex-shrink:0;text-align:center">
      <div class="pred-ball {bcls}" style="width:120px;height:120px;font-size:2.6rem">{plabel}</div>
      <div style="margin-top:10px">{badges}</div>
    </div>

    {{# Right: ring + stats #}}
    <div style="flex:1;min-width:200px">
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
        {conf_ring(dtc, rc)}
        <div>
          <div style="font-size:11px;color:rgba(255,255,255,.35);letter-spacing:.6px;
            font-family:'Orbitron',sans-serif;margin-bottom:4px">ĐỘ TIN CẬY</div>
          <div style="font-size:2.2rem;font-weight:900;color:{rc};
            text-shadow:0 0 18px {rc}88;font-family:'Orbitron',sans-serif;line-height:1">{dtc}%</div>
          <div style="font-size:11px;color:rgba(255,255,255,.3);margin-top:4px">
            {dd.get("tong_mau",0)} tín hiệu fusion · XS Tài {xs_tai:.1f}%</div>
        </div>
      </div>
      <div class="engine-tag">⚡ ULTIMATE ENGINE v6.0 — 1 THUẬT TOÁN DUY NHẤT</div>
    </div>
  </div>

  {{# Score breakdown ─────────────────────────────── #}}
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px">
    <div style="background:rgba(255,51,85,.07);border:1px solid rgba(255,51,85,.22);
      border-radius:12px;padding:14px 16px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;font-weight:800;color:#ff7090">TÀI</span>
        <span style="font-size:22px;font-weight:900;color:#ff3355;font-family:'Orbitron',sans-serif">{dt}</span>
      </div>
      <div class="sbar"><div class="sbar-fill" style="width:{t_pct:.0f}%;background:linear-gradient(90deg,#ff3355,#ff7090);color:#ff3355"></div></div>
      <div style="font-size:10px;color:rgba(255,255,255,.3);margin-top:6px">{st} tín hiệu · {vt} VIP · {at} AI</div>
    </div>
    <div style="background:rgba(0,255,170,.06);border:1px solid rgba(0,255,170,.2);
      border-radius:12px;padding:14px 16px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;font-weight:800;color:#00ffaa">XỈU</span>
        <span style="font-size:22px;font-weight:900;color:#00ffaa;font-family:'Orbitron',sans-serif">{dx}</span>
      </div>
      <div class="sbar"><div class="sbar-fill" style="width:{100-t_pct:.0f}%;background:linear-gradient(90deg,#00ffaa,#00cc88);color:#00ffaa"></div></div>
      <div style="font-size:10px;color:rgba(255,255,255,.3);margin-top:6px">{sx_n} tín hiệu · {vx} VIP · {ax} AI</div>
    </div>
  </div>
</div>'''

        # ── Strongest signal ─────────────────────────
        if mn:
            mn_pred = mn.get('ket_tiep','?')
            mn_cls  = 'c-tai' if mn_pred=='T' else ('c-xiu' if mn_pred=='X' else '')
            mn_lbl  = 'TÀI' if mn_pred=='T' else ('XỈU' if mn_pred=='X' else mn_pred)
            body += f'''<div class="card" style="border-color:rgba(255,215,0,.22);padding:14px 18px;margin-bottom:16px;
              display:flex;align-items:center;gap:14px">
  <div style="flex-shrink:0">
    <div style="font-size:9px;color:rgba(255,215,0,.5);letter-spacing:1px;
      font-family:'Orbitron',sans-serif;margin-bottom:3px">TÍN HIỆU MẠNH NHẤT</div>
    <div style="font-size:14px;font-weight:800;color:#ffd700">{mn.get("ten","")}</div>
  </div>
  <div style="flex:1"></div>
  <div style="text-align:right">
    <div style="font-size:9px;color:rgba(255,255,255,.3);margin-bottom:2px">Dự đoán</div>
    <div class="badge {'badge-tx' if mn_pred=='T' else 'badge-md5'}" style="font-size:11px;padding:4px 10px">{mn_lbl}</div>
  </div>
  <div style="text-align:right">
    <div style="font-size:9px;color:rgba(255,255,255,.3);margin-bottom:2px">Tin cậy</div>
    <div style="font-size:16px;font-weight:900;color:#ffd700">{mn.get("do_tin_cay",0)}%</div>
  </div>
</div>'''

        # ── Floating widget ──────────────────────────
        body += pred_widget(tool_id, cfg, phien_raw, plabel, dtc)

    else:
        body += '''<div class="card tc" style="padding:40px 24px;margin-bottom:16px">
  <div style="font-size:36px;margin-bottom:12px">⏳</div>
  <p style="color:#888899;font-size:14px">Chưa đủ dữ liệu để dự đoán (cần ≥ 3 phiên)</p>
</div>'''

    # ── History strip ─────────────────────────────
    body += f'''<div class="card" style="margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
    <span style="font-size:11px;font-weight:700;color:rgba(255,255,255,.35);letter-spacing:.6px;
      font-family:'Orbitron',sans-serif">LỊCH SỬ</span>
    <span style="font-size:11px;color:rgba(255,255,255,.2)">{len(ls)} phiên</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:2px">{hist_balls(ls, 40)}</div>
</div>'''

    # ── Signal patterns table ─────────────────────
    if patterns:
        rows = ''
        for p in patterns[:20]:
            kt = p.get('ket_tiep','?')
            kt_lbl = 'TÀI' if kt=='T' else ('XỈU' if kt=='X' else kt)
            kt_color = '#ff7090' if kt=='T' else ('#00ffaa' if kt=='X' else '#888899')
            tags = ''
            if p.get('la_vip'): tags += '<span class="badge badge-vip">VIP</span> '
            if p.get('la_ai'):  tags += '<span class="badge badge-ai">AI</span>'
            rows += f'''<tr>
  <td style="color:#ccc8be">{p.get("ten","")}</td>
  <td style="color:{kt_color};font-weight:800;font-family:'Orbitron',sans-serif;font-size:11px">{kt_lbl}</td>
  <td style="color:#ffd700;font-weight:700">{p.get("do_tin_cay",0)}%</td>
  <td>{tags}</td>
</tr>'''
        body += f'''<div class="card" style="overflow-x:auto;margin-bottom:16px">
  <div style="font-size:11px;font-weight:700;color:rgba(255,255,255,.35);
    letter-spacing:.6px;font-family:'Orbitron',sans-serif;margin-bottom:12px">
    TÍN HIỆU TRONG ULTIMATE ENGINE ({len(patterns)})
  </div>
  <table><tr><th>Tín hiệu</th><th>Dự đoán</th><th>Tin cậy</th><th>Loại</th></tr>{rows}</table>
</div>'''

    # ── Auto-refresh countdown ───────────────────
    body += '''<script>
var _cnt=2;
var _ti=document.createElement('div');
_ti.style.cssText='position:fixed;bottom:16px;left:50%;transform:translateX(-50%);'+
  'background:rgba(8,10,18,.9);border:1px solid rgba(255,215,0,.2);border-radius:20px;'+
  'padding:5px 14px;font-size:11px;color:rgba(255,215,0,.6);font-family:Orbitron,sans-serif;'+
  'letter-spacing:.5px;z-index:8888;pointer-events:none';
document.body.appendChild(_ti);
(function tick(){
  _ti.textContent='⟳ CẬP NHẬT SAU '+_cnt+'s';
  if(_cnt<=0){ location.reload(); return; }
  _cnt--; setTimeout(tick,1000);
})();
</script>'''

    return page(cfg.get('name','Tool'), body, u)

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

    # ── Header ──────────────────────────────────
    bcr_img = GAME_IMAGES.get('BACCARAT', '')
    img_tag = f"<img src='{bcr_img}' style='width:36px;height:36px;border-radius:9px;object-fit:cover;border:1px solid rgba(255,215,0,.3)' onerror='this.style.display=\"none\"'>" if bcr_img else ''
    body = f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;flex-wrap:wrap">
  <a href="/baccarat" class="btn btn-ghost btn-sm">← BCR</a>
  {img_tag}
  <h2 style="flex:1;color:#eceae2;font-size:17px;font-weight:800">Baccarat — Bàn {ban}</h2>
  <span class="badge badge-vip">LIVE</span>
</div>'''

    if dd:
        pred    = dd.get('du_doan', '?')
        dtc     = dd.get('do_tin_cay', 0)
        dp      = dd.get('diem_p', 0)
        db_s    = dd.get('diem_b', 0)
        sp      = dd.get('so_p', 0)
        sb      = dd.get('so_b', 0)
        bcls    = 'c-player' if pred == 'P' else 'c-banker'
        plabel  = 'PLAYER' if pred == 'P' else 'BANKER'
        rc      = '#00aaff' if pred == 'P' else '#ff3355'
        xs_p    = dd.get('xac_suat_player', 0.5) * 100
        p_pct   = (dp / (dp + db_s) * 100) if (dp + db_s) > 0 else 50

        badges = ''
        if dd.get('la_vip'): badges += '<span class="badge badge-vip">VIP</span> '
        if dd.get('la_ai'):  badges += '<span class="badge badge-ai">AI</span> '
        badges += '<span class="badge badge-ultimate">ULTIMATE</span>'

        body += f'''<div class="glow-card" style="padding:28px 24px;margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
    <div style="flex-shrink:0;text-align:center">
      <div class="pred-ball {bcls}" style="width:120px;height:120px;font-size:2rem">{plabel}</div>
      <div style="margin-top:10px">{badges}</div>
    </div>
    <div style="flex:1;min-width:200px">
      <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px">
        {conf_ring(dtc, rc)}
        <div>
          <div style="font-size:11px;color:rgba(255,255,255,.35);letter-spacing:.6px;
            font-family:'Orbitron',sans-serif;margin-bottom:4px">ĐỘ TIN CẬY</div>
          <div style="font-size:2.2rem;font-weight:900;color:{rc};
            text-shadow:0 0 18px {rc}88;font-family:'Orbitron',sans-serif;line-height:1">{dtc}%</div>
          <div style="font-size:11px;color:rgba(255,255,255,.3);margin-top:4px">
            {dd.get("tong_mau",0)} tín hiệu · XS Player {xs_p:.1f}% · P:{sp} B:{sb}</div>
        </div>
      </div>
      <div class="engine-tag">⚡ ULTIMATE ENGINE v6.0 — 1 THUẬT TOÁN DUY NHẤT</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px">
    <div style="background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.22);border-radius:12px;padding:14px 16px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;font-weight:800;color:#5bc8ff">PLAYER</span>
        <span style="font-size:22px;font-weight:900;color:#00aaff;font-family:'Orbitron',sans-serif">{dp}</span>
      </div>
      <div class="sbar"><div class="sbar-fill" style="width:{p_pct:.0f}%;background:linear-gradient(90deg,#00aaff,#5bc8ff);color:#00aaff"></div></div>
      <div style="font-size:10px;color:rgba(255,255,255,.3);margin-top:6px">{sp} tín hiệu</div>
    </div>
    <div style="background:rgba(255,51,85,.07);border:1px solid rgba(255,51,85,.22);border-radius:12px;padding:14px 16px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
        <span style="font-size:13px;font-weight:800;color:#ff7090">BANKER</span>
        <span style="font-size:22px;font-weight:900;color:#ff3355;font-family:'Orbitron',sans-serif">{db_s}</span>
      </div>
      <div class="sbar"><div class="sbar-fill" style="width:{100-p_pct:.0f}%;background:linear-gradient(90deg,#ff3355,#ff7090);color:#ff3355"></div></div>
      <div style="font-size:10px;color:rgba(255,255,255,.3);margin-top:6px">{sb} tín hiệu</div>
    </div>
  </div>
</div>'''

        mn = dd.get('thuat_toan_manh_nhat', {})
        if mn:
            mn_pred = mn.get('ket_tiep','?')
            mn_color = '#5bc8ff' if mn_pred=='P' else ('#ff7090' if mn_pred=='B' else '#888899')
            body += f'''<div class="card" style="border-color:rgba(255,215,0,.22);padding:14px 18px;margin-bottom:16px;
              display:flex;align-items:center;gap:14px">
  <div style="flex-shrink:0">
    <div style="font-size:9px;color:rgba(255,215,0,.5);letter-spacing:1px;font-family:'Orbitron',sans-serif;margin-bottom:3px">TÍN HIỆU MẠNH NHẤT</div>
    <div style="font-size:14px;font-weight:800;color:#ffd700">{mn.get("ten","")}</div>
  </div>
  <div style="flex:1"></div>
  <div style="font-size:16px;font-weight:900;color:{mn_color};font-family:'Orbitron',sans-serif">{mn_pred}</div>
</div>'''

        body += pred_widget(f'bcr_{ban}',
            {'name':'BCR','full_name':f'BACCARAT — Bàn {ban}','nhom':'BACCARAT'},
            ban, plabel, dtc, is_bcr=True)

    else:
        body += '''<div class="card tc" style="padding:40px 24px;margin-bottom:16px">
  <div style="font-size:36px;margin-bottom:12px">⏳</div>
  <p style="color:#888899;font-size:14px">Chưa đủ dữ liệu để dự đoán</p>
</div>'''

    # ── History strip ─────────────────────────────
    body += f'''<div class="card" style="margin-bottom:16px">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
    <span style="font-size:11px;font-weight:700;color:rgba(255,255,255,.35);letter-spacing:.6px;
      font-family:'Orbitron',sans-serif">LỊCH SỬ</span>
    <span style="font-size:11px;color:rgba(255,255,255,.2)">{len(hist)} phiên</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:2px">{hist_balls(hist, 40)}</div>
</div>'''

    # ── Patterns table ───────────────────────────
    if patterns:
        rows = ''
        for p in patterns[:20]:
            kt = p.get('ket_tiep','?')
            kt_color = '#5bc8ff' if kt=='P' else ('#ff7090' if kt=='B' else '#888899')
            tags = ''
            if p.get('la_vip'): tags += '<span class="badge badge-vip">VIP</span> '
            if p.get('la_ai'):  tags += '<span class="badge badge-ai">AI</span>'
            rows += f'''<tr>
  <td style="color:#ccc8be">{p.get("ten","")}</td>
  <td style="color:{kt_color};font-weight:800;font-family:'Orbitron',sans-serif;font-size:11px">{kt}</td>
  <td style="color:#ffd700;font-weight:700">{p.get("do_tin_cay",0)}%</td>
  <td>{tags}</td>
</tr>'''
        body += f'''<div class="card" style="overflow-x:auto;margin-bottom:16px">
  <div style="font-size:11px;font-weight:700;color:rgba(255,255,255,.35);
    letter-spacing:.6px;font-family:'Orbitron',sans-serif;margin-bottom:12px">
    TÍN HIỆU TRONG ULTIMATE ENGINE ({len(patterns)})
  </div>
  <table><tr><th>Tín hiệu</th><th>Dự đoán</th><th>Tin cậy</th><th>Loại</th></tr>{rows}</table>
</div>'''

    body += '''<script>
var _cnt=2;
var _ti=document.createElement('div');
_ti.style.cssText='position:fixed;bottom:16px;left:50%;transform:translateX(-50%);'+
  'background:rgba(8,10,18,.9);border:1px solid rgba(255,215,0,.2);border-radius:20px;'+
  'padding:5px 14px;font-size:11px;color:rgba(255,215,0,.6);font-family:Orbitron,sans-serif;'+
  'letter-spacing:.5px;z-index:8888;pointer-events:none';
document.body.appendChild(_ti);
(function tick(){
  _ti.textContent='⟳ CẬP NHẬT SAU '+_cnt+'s';
  if(_cnt<=0){ location.reload(); return; }
  _cnt--; setTimeout(tick,1000);
})();
</script>'''

    return page(f'BCR Bàn {ban}', body, u)


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
           '<h2 style="flex:1;color:#ffd700;font-family:Orbitron">LỊCH SỬ DỰ ĐOÁN</h2></div>'
    body += '<div class="grid g3 mb16">'
    body += f'<div class="card tc"><div style="font-size:28px;font-weight:900;color:#ffd700;font-family:Orbitron">{st["done"]}</div><div class="fs12 c-dim">Da co ket qua</div></div>'
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
                res_lbl = '<span class="badge" style="background:rgba(255,215,0,.15);color:#ffd700">CHO</span>'
            else:
                act_lbl = 'TAI' if e.get('actual') == 'T' else 'XIU'
                act_cls = 'color:#ff3355' if e.get('actual') == 'T' else 'color:#00ffaa'
                if e.get('correct'):
                    res_lbl = '<span class="badge" style="background:rgba(0,255,170,.2);color:#00ffaa;border:1px solid #00ffaa">✓ DUNG</span>'
                else:
                    res_lbl = '<span class="badge" style="background:rgba(255,51,85,.2);color:#ff3355;border:1px solid #ff3355">✗ SAI</span>'
            body += f'<tr><td style="color:#ffd700;font-weight:700">{e.get("tool_name","")}</td>' \
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
           '<h2 style="flex:1;color:#ffd700;font-family:Orbitron">CỬA HÀNG KEY VIP</h2></div>'
    body += f'<div class="card tc mb16"><div class="fs12 c-dim">So du hien tai</div>' \
            f'<div style="font-size:36px;font-weight:900;color:#ffd700;font-family:Orbitron;text-shadow:0 0 20px rgba(255,215,0,.4)">{fmt_price(bal)}</div>' \
            f'<a href="/payment" class="btn btn-primary btn-sm mt8">+ Nap them tien</a></div>'
    body += '<div class="grid g2">'
    for pid, pkg in PACKAGES.items():
        du = bal >= pkg['price']
        btn_cls = 'btn-green' if du else 'btn-ghost'
        btn_txt = 'Mua ngay (du tien)' if du else 'Khong du tien'
        disabled = '' if du else 'disabled onclick="return false" style="opacity:.4;cursor:not-allowed"'
        body += f'''<div class="card" style="border-color:rgba(255,215,0,.3)">
<div class="flex mb8"><span style="font-weight:800;color:#ffd700;font-size:18px;font-family:Orbitron">{pkg["name"]}</span>
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
    body = '<div class="flex mb16"><h2 style="flex:1;color:#ffd700;font-family:Orbitron">MUA KEY VIP PRO</h2><a href="/shop" class="btn btn-green btn-sm">→ Mua bang SO DU (da nap)</a></div><div class="grid g2">'
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
<div class="mb8"><span class="fs12 c-dim">Ma CK:</span> <span class="mono" style="color:#ffd700;font-weight:900;font-size:18px">{tc}</span></div>
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
        body += '<div style="margin-top:14px;font-size:13px">Độ tin cậy: <b style="color:#ffd700">%.1f%%</b></div>' % result['do_tin_cay']
        body += '<div class="sbar mt8"><div class="sbar-fill" style="width:%.1f%%;background:linear-gradient(90deg,#8b5cf6,#ffd700)"></div></div>' % result['do_tin_cay']
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
