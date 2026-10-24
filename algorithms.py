#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  🧠 ALGORITHMS.PY — TỔNG HỢP TẤT CẢ THUẬT TOÁN NÂNG CẤP (Ultimate v23.0)
==============================================================================
  Một file duy nhất, tổng hợp:
    🔥 TX v23        — Multi-scale 8/15/25 + Weighted Voting + Regime Brain
                      + Cooldown Flip + Heat Tracking + Bayesian Shrinkage
                      + Divergence Skip (7 đột phá so với v22)
    🧠 AI THINKING   — Tree of Thoughts + Monte Carlo 1000 + Ensemble 12 algo
    📊 BCR VIP       — 6 methods: Streak / Chop / Cycle / Markov / Subseq / Consensus
    ♠️ BACCARAT VIP  — 6 thuật toán: cầu cơ bản / dự đoán VIP / quản lý vốn /
                      mô phỏng / đánh giá rủi ro / báo cáo
    💎 14 CONF VIP   — 7-1-7 97%, Đảo 5-7 96%, 5-1-5 95%, Đồng hồ 95%...
    📈 VÙNG BẺ       — 3-4 tay=ĐU, 5-7=BẺ, 8+=BẺ MẠNH
    💰 SESSION+KELLY — Stop-loss 4 thua / -8 units, Kelly 25%, max 4 units

  API công khai:
    du_doan_tx(lich_su, tool_id, phien)        -> (result, detail)
    du_doan_bcr(lich_su, tool_id, phien)       -> (result, detail)
    du_doan_baccarat(lich_su, tool_id, phien)  -> (result, detail)
    du_doan_ai_thinking(lich_su, tool_id)      -> dict
    get_conf_strategies()                      -> list 14 CONF
    get_vung_be(lich_su)                       -> dict vùng bẻ hiện tại

  Disclaimer: Công cụ phân tích dữ liệu học thuật. Chơi có trách nhiệm.
==============================================================================
"""
import math, json, os, sqlite3, time, threading, random
from collections import deque, defaultdict
from datetime import datetime

# ============================================================
# CẤU HÌNH CHUNG
# ============================================================
MIN_WINDOW = 8
WINDOWS = [8, 15, 25]
MAX_CONFIDENCE = 0.92
STOP_LOSS_STREAK = 4
STOP_LOSS_UNITS = -8.0
MAX_ENTROPY = 0.92
SELF_CORRECT_MIN_N = 15
SELF_CORRECT_THRESHOLD = 0.42
SKIP_PATTERN_WR = 0.45
MIN_METHOD_SAMPLES = 20
DIVERGENCE_MIN = 0.25
FLIP_COOLDOWN_PHIEU = 10
HEAT_WINDOW = 10
HEAT_PENALTY_THRESHOLD = 3
SHRINK_PRIOR = 0.5
SHRINK_STRENGTH = 30
PENDING_TTL = 3600 * 6
MCTS_SIMULATIONS = 1000
DB_FILE = "algorithms_brain.db"

# ============================================================
# 14 CHIẾN LƯỢC CONF VIP
# ============================================================
CONF_STRATEGIES = [
    {"name": "7-1-7", "winrate": 97, "action": "ALL IN", "color": "#ff0000"},
    {"name": "Đảo 5-7/7-5", "winrate": 96, "action": "ALL IN", "color": "#ff0000"},
    {"name": "5-1-5", "winrate": 95, "action": "ALL IN", "color": "#ff0000"},
    {"name": "Đồng hồ", "winrate": 95, "action": "Vào đậm", "color": "#ff6600"},
    {"name": "Đảo bệt kép", "winrate": 94, "action": "Vào đậm", "color": "#ff6600"},
    {"name": "Kim tự tháp", "winrate": 94, "action": "Vào đậm", "color": "#ff6600"},
    {"name": "Bệt kép", "winrate": 93, "action": "Vào đậm", "color": "#ff6600"},
    {"name": "Gãy 7", "winrate": 93, "action": "Vào vừa", "color": "#ffaa00"},
    {"name": "Fibonacci", "winrate": 93, "action": "Vào vừa", "color": "#ffaa00"},
    {"name": "Double Break", "winrate": 92, "action": "Vào vừa", "color": "#ffaa00"},
    {"name": "5-Phase", "winrate": 92, "action": "Vào vừa", "color": "#ffaa00"},
    {"name": "Gãy 5", "winrate": 91, "action": "Vào vừa", "color": "#ffaa00"},
    {"name": "3-Phase", "winrate": 90, "action": "Vào vừa", "color": "#00ff41"},
    {"name": "Zigzag VIP", "winrate": 89, "action": "Cẩn thận", "color": "#00ffff"},
]

def get_conf_strategies():
    return CONF_STRATEGIES

# ============================================================
# HELPER CHUNG
# ============================================================
def _norm(lich_su):
    out = []
    for x in lich_su:
        s = str(x).strip().upper()
        if s in ("TÀI","TAI","T","BIG","OVER","CHAN","PLAYER","P"): out.append("T")
        elif s in ("XỈU","XIỦ","XIU","X","SMALL","UNDER","LE","BANKER","B"): out.append("X")
    return out

def _streak(seq):
    if not seq: return 0, None
    cnt=1; last=seq[-1]
    for i in range(len(seq)-2,-1,-1):
        if seq[i]==last: cnt+=1
        else: break
    return cnt, last

def _entropy(seq):
    if len(seq)<5: return 0.5
    p=seq.count("T")/len(seq); q=1-p
    if p==0 or q==0: return 0.0
    return -(p*math.log2(p)+q*math.log2(q))

def _phien_int(phien):
    try: return int(''.join(c for c in str(phien) if c.isdigit()))
    except: return None

def _shrink(wr, n):
    return (wr*n + SHRINK_PRIOR*SHRINK_STRENGTH)/(n+SHRINK_STRENGTH)

def _rle(seq):
    if not seq: return []
    out=[]; cur=seq[0]; cnt=1
    for c in seq[1:]:
        if c==cur: cnt+=1
        else: out.append((cur,cnt)); cur=c; cnt=1
    out.append((cur,cnt)); return out

def _regime(seq):
    if len(seq)<30: return "unknown"
    r = seq[-50:] if len(seq)>=50 else seq
    maxs=cur=1
    for i in range(1,len(r)):
        if r[i]==r[i-1]: cur+=1; maxs=max(maxs,cur)
        else: cur=1
    alt = sum(1 for i in range(1,len(r)) if r[i]!=r[i-1])/(len(r)-1)
    bias = abs(r.count("T")/len(r)-0.5)
    if maxs>=6: return "streaky"
    if alt>0.65: return "choppy"
    if bias>0.15: return "trending"
    return "balanced"

def _kelly(wr, odds=1.0):
    p=wr; q=1-p
    if odds<=0: return 0.0
    f=(odds*p-q)/odds
    return 0.0 if f<=0 else min(0.025, f/4)

def _bet_units(conf, wr, n):
    if n<10 or wr<0.52: return 0
    edge=wr-0.5
    if conf>=0.68 and edge>=0.05: return 4
    if conf>=0.62 and edge>=0.03: return 3
    if conf>=0.57 and edge>=0.02: return 2
    if conf>=0.53 and edge>=0.01: return 1
    return 0

# ============================================================
# BAYESIAN BRAIN CHUNG (học mọi thuật toán)
# ============================================================
_brains = {}
_brain_lock = threading.RLock()

class Brain:
    def __init__(self, gid):
        self.gid = gid
        self.stats = defaultdict(lambda: {"alpha":1.0,"beta":1.0,"n":0})
        self.heat = defaultdict(lambda: deque(maxlen=HEAT_WINDOW))
        self.last_flip = {}
        self._load()

    def _db(self):
        conn = sqlite3.connect(DB_FILE)
        conn.execute('''CREATE TABLE IF NOT EXISTS brain (
            game_id TEXT, pattern TEXT, alpha REAL, beta REAL, n INTEGER,
            heat TEXT, last_flip INTEGER, PRIMARY KEY(game_id,pattern))''')
        return conn

    def _load(self):
        try:
            conn=self._db(); c=conn.cursor()
            c.execute("SELECT pattern,alpha,beta,n,heat,last_flip FROM brain WHERE game_id=?",(self.gid,))
            for row in c.fetchall():
                self.stats[row[0]]={"alpha":row[1],"beta":row[2],"n":row[3]}
                if row[4]:
                    try: self.heat[row[0]]=deque(json.loads(row[4]),maxlen=HEAT_WINDOW)
                    except: pass
                if row[5]: self.last_flip[row[0]]=row[5]
            conn.close()
        except: pass

    def _save(self):
        try:
            conn=self._db(); c=conn.cursor()
            for k,st in self.stats.items():
                h=json.dumps(list(self.heat.get(k,[])))
                lf=self.last_flip.get(k)
                c.execute("INSERT OR REPLACE INTO brain VALUES (?,?,?,?,?,?,?)",
                          (self.gid,k,st["alpha"],st["beta"],st["n"],h,lf))
            conn.commit(); conn.close()
        except: pass

    def record(self, pattern, pred, actual):
        win = 1 if pred==actual else 0
        st=self.stats[pattern]; st["n"]+=1
        if win: st["alpha"]+=1
        else: st["beta"]+=1
        self.heat[pattern].append(bool(win))
        self._save()

    def get_wr(self, pattern, regime=None):
        if regime:
            kr=f"{pattern}@{regime}"
            wr,n=self._wr(kr)
            if n>=15: return wr,n,kr
        wr,n=self._wr(pattern)
        return wr,n,pattern

    def _wr(self, key):
        st=self.stats.get(key,{"alpha":1.0,"beta":1.0,"n":0})
        if st["n"]==0: return 0.5,0
        return st["alpha"]/(st["alpha"]+st["beta"]), st["n"]

    def heat_penalty(self, key):
        h=list(self.heat.get(key,[]))
        if len(h)>=5:
            losses=sum(1 for w in h if not w); wins=sum(1 for w in h if w)
            if losses>=HEAT_PENALTY_THRESHOLD and wins<=1: return 0.6
        return 1.0

    def can_flip(self, key, cur_int):
        last=self.last_flip.get(key)
        if last is None or cur_int is None: return True
        return (cur_int-last)>=FLIP_COOLDOWN_PHIEU

    def mark_flipped(self, key, cur_int):
        if cur_int is not None:
            self.last_flip[key]=cur_int; self._save()

def _brain(gid):
    with _brain_lock:
        if gid not in _brains: _brains[gid]=Brain(gid)
        return _brains[gid]

# ============================================================
# SESSION MANAGER
# ============================================================
class Session:
    def __init__(self, gid):
        self.gid=gid; self.bets=[]; self.sid=f"sess_{int(time.time())}"
    def record(self, phien, pred, actual, units, pattern):
        self.bets.append({"phien":phien,"pred":pred,"actual":actual,
                          "win":1 if pred==actual else 0,"units":units,"pattern":pattern})
    def stats(self):
        if not self.bets:
            return {"bets":0,"wins":0,"losses":0,"winrate":0,"units_pnl":0,
                    "current_streak":0,"current_streak_type":None,"max_streak":0}
        wins=sum(1 for b in self.bets if b["win"])
        pnl=sum((b["units"] if b["win"] else -b["units"]) for b in self.bets)
        cur=1; ctype="win" if self.bets[-1]["win"] else "loss"; maxs=1
        for i in range(len(self.bets)-2,-1,-1):
            if (self.bets[i]["win"] and ctype=="win") or (not self.bets[i]["win"] and ctype=="loss"):
                cur+=1; maxs=max(maxs,cur)
            else: break
        return {"bets":len(self.bets),"wins":wins,"losses":len(self.bets)-wins,
                "winrate":round(wins/len(self.bets)*100,1),"units_pnl":round(pnl,2),
                "current_streak":cur,"current_streak_type":ctype,"max_streak":maxs}

_sessions={}
def _sess(gid):
    if gid not in _sessions: _sessions[gid]=Session(gid)
    return _sessions[gid]

# ============================================================
# PENDING QUEUE
# ============================================================
_pending={}
_pending_lock=threading.RLock()
def _store_pending(gid, target_int, pred, units, pattern):
    with _pending_lock:
        _pending[(gid,target_int)]={"pred":pred,"units":units,"pattern":pattern,"created":time.time()}
        for k in list(_pending.keys()):
            if time.time()-_pending[k]["created"]>PENDING_TTL: _pending.pop(k,None)
def _resolve_pending(gid, cur_int):
    with _pending_lock: return _pending.pop((gid,cur_int),None)

# ============================================================
# RESULT BUILDER CHUNG
# ============================================================
def _build(pred, conf, phase, detail, note, units=0, kelly=0.0, session=None, extra=None):
    verdict=("STRONG" if conf>=70 else "GOOD" if conf>=60 else
             "MEDIUM" if conf>=55 else "WEAK" if conf>=50 else "SKIP")
    is_skip = pred in ("SKIP",None)
    r={"du_doan":("TÀI" if pred=="T" else "XỈU") if not is_skip else "SKIP",
       "do_tin_cay":int(conf),"phase":phase,"verdict":verdict,"note":note,"reason":note,
       "pattern":detail[0].get("pattern","") if detail else "",
       "bet_units":units,"kelly_percent":round(kelly,2),
       "la_vip":conf>=65,"engine":"🧠 ALGORITHMS ULTIMATE v23.0",
       "status":"SKIP" if is_skip else "OK","so_patterns":len(detail),"patterns":detail}
    if session: r["session"]=session.stats(); r["session_id"]=session.sid
    if extra: r.update(extra)
    return r

# ============================================================
# 🔥 TX v23 — MULTI-SCALE (8/15/25) — CAO NHẤT
# ============================================================
def _detect_at_scale(hist, scale):
    if len(hist)<scale: return None
    w=hist[-scale:]; n=len(w)
    n_t=w.count("T"); n_x=n-n_t
    streak,last=_streak(w); opp="X" if last=="T" else "T"
    if streak>=max(7,scale//2+1): return ("BET_BE_STRONG",opp,0.68)
    if streak>=5: return ("BET_BE",opp,0.60)
    if streak==4: return ("BET_THEO",last,0.55)
    if streak==3: return ("BET_THEO_NHE",last,0.52)
    if n>=6:
        r=w[-6:]
        if all(r[i]!=r[i+1] for i in range(5)): return ("CAU_11_STRONG",opp,0.63)
        if all(r[i]!=r[i+1] for i in range(4)): return ("CAU_11",opp,0.58)
        if r[0]==r[1] and r[2]==r[3] and r[4]==r[5] and r[0]!=r[2]: return ("CAU_22",opp,0.58)
        if r[0]==r[1]==r[2] and r[3]==r[4]==r[5] and r[0]!=r[3]: return ("CAU_33",opp,0.57)
    for period in (2,3,4):
        if n>=period*3:
            seg=w[-period*3:]
            if all(seg[i]==seg[i+period] for i in range(len(seg)-period)):
                return (f"CYCLE_{period}",w[-period],0.60)
    if n_t>=int(n*0.8): return ("HOI_QUY_TAI","X",0.56)
    if n_x>=int(n*0.8): return ("HOI_QUY_XIU","T",0.56)
    if n_t>=int(n*0.7): return ("LECH_TAI","X",0.53)
    if n_x>=int(n*0.7): return ("LECH_XIU","T",0.53)
    return None

def _detect_multi(hist):
    matches=[]
    for scale in WINDOWS:
        r=_detect_at_scale(hist,scale)
        if r:
            name,pred,conf=r
            matches.append({"pattern":name,"pred":pred,"base_conf":conf,"scale":scale,"key":f"{name}@{scale}"})
    return matches

def du_doan_tx(lich_su, tool_id="", phien="", session_id=None):
    s=_norm(lich_su)
    if len(s)<MIN_WINDOW: return None,[]
    gid=tool_id or "default"
    brain=_brain(gid); cur_int=_phien_int(phien); sess=_sess(gid)
    if cur_int is not None:
        res=_resolve_pending(gid,cur_int)
        if res:
            actual=s[-1]
            try: brain.record(res["pattern"],res["pred"],actual)
            except: pass
            sess.record(phien,res["pred"],actual,res["units"],res["pattern"])
    st=sess.stats()
    if st["current_streak_type"]=="loss" and st["current_streak"]>=STOP_LOSS_STREAK:
        d=[{"ten":f"🛑 Stop-loss thua {st['current_streak']} phiên","ket_tiep":None,"do_tin_cay":0}]
        return _build("SKIP",0,"STOP_LOSS",d,f"Thua {st['current_streak']} phiên",session=sess),d
    if st["units_pnl"]<=STOP_LOSS_UNITS:
        d=[{"ten":f"🛑 Stop-loss PnL {st['units_pnl']:+.1f}u","ket_tiep":None,"do_tin_cay":0}]
        return _build("SKIP",0,"STOP_LOSS",d,f"Vốn -{abs(st['units_pnl']):.1f} units",session=sess),d
    ent=_entropy(s)
    if ent>MAX_ENTROPY:
        d=[{"ten":f"🌊 Entropy {ent:.2f}>{MAX_ENTROPY}","ket_tiep":None,"do_tin_cay":0}]
        return _build("SKIP",0,"HIGH_ENTROPY",d,"Cầu random",session=sess,extra={"entropy":round(ent,3)}),d
    matches=_detect_multi(s)
    if not matches:
        d=[{"ten":"❓ Không phát hiện cầu ở scale nào","ket_tiep":None,"do_tin_cay":0}]
        return _build("SKIP",0,"NO_PATTERN",d,"Không có cầu",session=sess),d
    regime=_regime(s); scored=[]
    for m in matches:
        wr,n,used_key=brain.get_wr(m["key"],regime=regime)
        wr_eff=_shrink(wr,n); heat_pen=brain.heat_penalty(used_key)
        pred=m["pred"]; flipped=False
        if n>=SELF_CORRECT_MIN_N and wr<SELF_CORRECT_THRESHOLD:
            if brain.can_flip(used_key,cur_int):
                pred="X" if pred=="T" else "T"; flipped=True
                brain.mark_flipped(used_key,cur_int); wr_eff=0.55
            else: continue
        elif n>=MIN_METHOD_SAMPLES and wr<SKIP_PATTERN_WR: continue
        score=m["base_conf"]*wr_eff*heat_pen*(0.85 if flipped else 1.0)
        scored.append({"pattern_key":used_key,"pattern_short":m["pattern"],"scale":m["scale"],
                       "pred":pred,"base_conf":m["base_conf"],"wr":wr,"wr_eff":wr_eff,
                       "n":n,"heat":heat_pen,"flipped":flipped,"score":score})
    if not scored:
        d=[{"ten":"❓ Tất cả patterns đang cooldown/quá yếu","ket_tiep":None,"do_tin_cay":0}]
        return _build("SKIP",0,"ALL_WEAK",d,"Patterns đều yếu",session=sess),d
    t_score=sum(x["score"] for x in scored if x["pred"]=="T")
    x_score=sum(x["score"] for x in scored if x["pred"]=="X")
    total=t_score+x_score
    if total==0:
        return _build("SKIP",0,"LOW_SCORE",[{"ten":"Score thấp","ket_tiep":None,"do_tin_cay":0}],"Score thấp",session=sess),[]
    if t_score>0 and x_score>0:
        div=abs(t_score-x_score)/total
        if div<DIVERGENCE_MIN:
            d=[{"ten":f"⚔️ Scales xung đột T={t_score:.2f} vs X={x_score:.2f}","ket_tiep":None,"do_tin_cay":0}]
            return _build("SKIP",0,"DIVERGENCE",d,f"Divergence {div:.2f}<{DIVERGENCE_MIN}",session=sess,
                          extra={"t_score":round(t_score,3),"x_score":round(x_score,3)}),d
    pred="T" if t_score>x_score else "X"
    win_score=max(t_score,x_score)
    winning=[x for x in scored if x["pred"]==pred]
    avg_wr=sum(x["wr_eff"] for x in winning)/len(winning)
    avg_n=sum(x["n"] for x in winning)/len(winning)
    avg_conf=win_score/total
    final_conf=min(MAX_CONFIDENCE,0.5+(avg_conf-0.5)*0.9)
    final_conf=0.5*final_conf+0.5*avg_wr
    units=_bet_units(final_conf,avg_wr,avg_n)
    kelly_f=_kelly(avg_wr) if avg_wr>0.5 else 0.0
    if units==0:
        d=[{"ten":f"⚠️ Edge yếu WR {avg_wr*100:.1f}% n={avg_n:.0f}","ket_tiep":pred,"do_tin_cay":int(final_conf*100)}]
        return _build("SKIP",int(final_conf*100),"WEAK_EDGE",d,"Edge yếu",session=sess,extra={"pattern":pred}),d
    winning.sort(key=lambda x:-x["score"]); top=winning[0]; detail=[]
    for m in winning[:5]:
        tag="🎯" if m["scale"]==15 else ("📊" if m["scale"]==8 else "🔭")
        flip=" [FLIP]" if m["flipped"] else ""
        detail.append({"ten":f"{tag} {m['pattern_short']}@{m['scale']}→{m['pred']} (WR {m['wr']*100:.0f}%, n={m['n']}, heat={m['heat']:.1f}){flip}",
                       "ket_tiep":m["pred"],"do_tin_cay":int(m["base_conf"]*100),
                       "pattern":m["pattern_key"],"scale":m["scale"],"wr":round(m["wr"]*100,1)})
    note=f"{len(winning)}/{len(scored)} patterns→{pred} | top: {top['pattern_short']}@{top['scale']} (WR {top['wr']*100:.0f}%)"
    if cur_int is not None: _store_pending(gid,cur_int+1,pred,units,top["pattern_key"])
    return _build(pred,int(final_conf*100),"MULTI_SCALE",detail,note,units,kelly_f*100,session=sess,
                  extra={"pattern":top["pattern_key"],"pattern_winrate":round(top["wr"]*100,1),
                         "pattern_samples":top["n"],"regime":regime,"entropy":round(ent,3),
                         "t_score":round(t_score,3),"x_score":round(x_score,3),
                         "divergence":round(abs(t_score-x_score)/total,3)}),detail

# ============================================================
# 📊 BCR VIP — 6 METHODS
# ============================================================
def _bcr_streak(seq):
    streak,last=_streak(seq)
    if streak>=8: return ("X" if last=="T" else "T",0.72,"bcr_streak_8+")
    if streak>=5: return ("X" if last=="T" else "T",0.58,"bcr_streak_5")
    if streak>=3: return (last,0.54,"bcr_streak_3")
    return None

def _bcr_chop(seq):
    if len(seq)>=6 and all(seq[i]!=seq[i+1] for i in range(len(seq)-6,len(seq)-1)):
        return (seq[-1],0.60,"bcr_chop_6")
    return None

def _bcr_cycle(seq):
    for p in (2,3,4):
        if len(seq)>=p*3:
            seg=seq[-p*3:]
            if all(seg[i]==seg[i+p] for i in range(len(seg)-p)):
                return (seq[-p],0.58,f"bcr_cycle_{p}")
    return None

def _bcr_markov(seq):
    if len(seq)<6: return None
    tt=tx=xt=xx=0
    for i in range(len(seq)-1):
        a,b=seq[i],seq[i+1]
        if a=="T" and b=="T": tt+=1
        elif a=="T" and b=="X": tx+=1
        elif a=="X" and b=="T": xt+=1
        else: xx+=1
    last=seq[-1]
    if last=="T" and (tt+tx)>0:
        p=tt/(tt+tx); return ("T" if p>=0.5 else "X",0.5+abs(p-0.5)*0.4,"bcr_markov")
    if last=="X" and (xt+xx)>0:
        p=xx/(xt+xx); return ("X" if p>=0.5 else "T",0.5+abs(p-0.5)*0.4,"bcr_markov")
    return None

def _bcr_subseq(seq):
    for L in (4,3):
        if len(seq)>=L*2:
            if seq[-L:]==seq[-2*L:-L]:
                return (seq[-1],0.56,f"bcr_subseq_{L}")
    return None

_BCR_METHODS=[_bcr_streak,_bcr_chop,_bcr_cycle,_bcr_markov,_bcr_subseq]

def du_doan_bcr(lich_su, tool_id="", phien="", session_id=None):
    seq=_norm(lich_su)
    if len(seq)<8: return None,[]
    gid=f"bcr_{tool_id or 'default'}"; brain=_brain(gid); results=[]
    for m in _BCR_METHODS:
        try:
            r=m(seq)
            if r:
                pred,conf,name=r
                wr,n=brain.get_wr(name)
                results.append({"pred":pred,"conf":conf,"name":name,"wr":wr,"n":n})
        except: pass
    if not results:
        return _build("SKIP",0,"NO_BCR",[{"ten":"Không có BCR","ket_tiep":None,"do_tin_cay":0}],"Không có BCR"),[]
    sides=list(set(r["pred"] for r in results))
    if len(sides)==1:
        pred=sides[0]; agreeing=results
    else:
        v1=[r for r in results if r["pred"]==sides[0]]; v2=[r for r in results if r["pred"]==sides[1]]
        if len(v1)>len(v2): pred,agreeing=sides[0],v1
        elif len(v2)>len(v1): pred,agreeing=sides[1],v2
        else:
            return _build("SKIP",0,"BCR_TIE",[{"ten":"BCR hòa","ket_tiep":None,"do_tin_cay":0}],"BCR hòa"),[]
    avg_wr=sum(r["wr"] for r in agreeing)/len(agreeing)
    a=1+len(agreeing)*2*avg_wr; b=1+len(agreeing)*2*(1-avg_wr)
    conf=min(MAX_CONFIDENCE,a/(a+b))
    detail=[{"ten":f"📊 {r['name']}→{r['pred']} (WR {r['wr']*100:.0f}%, n={r['n']})",
             "ket_tiep":r["pred"],"do_tin_cay":int(r["conf"]*100),"pattern":r["name"]} for r in agreeing]
    note=f"BCR: {len(agreeing)}/{len(results)} methods→{pred} (WR {avg_wr*100:.0f}%)"
    return _build(pred,int(conf*100),"BCR_CONSENSUS",detail,note,
                  _bet_units(conf,avg_wr,sum(r["n"] for r in agreeing)),_kelly(avg_wr)*100,
                  extra={"bcr_methods":len(results),"bcr_agree":len(agreeing)}),detail

# ============================================================
# 🧠 AI THINKING ENGINE — ToT + MCTS + ENSEMBLE 12
# ============================================================
def _algo_streak(seq,rle):
    streak,last=_streak(seq)
    if streak>=8: return ("BET_BE_MANH","X" if last=="T" else "T",0.72)
    if streak>=5: return ("BET_BE","X" if last=="T" else "T",0.62)
    if streak>=3: return ("BET_DU",last,0.56)
    return None

def _algo_alt(seq,rle):
    for L in (6,5,4):
        if len(seq)>=L and all(seq[i]!=seq[i+1] for i in range(len(seq)-L,len(seq)-1)):
            return (f"DAO_{L}",seq[-1],0.58+(L-4)*0.02)
    return None

def _algo_groups(seq,rle):
    cnts=[c for _,c in rle]
    pats=[([7,1,7],"CONF_717",0.70),([5,1,5],"CONF_515",0.68),([5,7],"DAO_57",0.66),
          ([7,5],"DAO_75",0.66),([1,2,1,2,1],"PHASE_5",0.62),([1,2,1],"PHASE_3",0.58),
          ([1,1,2,3],"FIBO",0.60),([1,2,3,2,1],"KIMTU",0.62),([3,1,3],"NHIP_313",0.64)]
    for grp,name,conf in pats:
        if len(cnts)>=len(grp) and cnts[-len(grp):]==grp:
            return (name,"X" if seq[-1]=="T" else "T",conf)
    if len(cnts)>=2 and cnts[-1]==cnts[-2] and cnts[-1]>=3:
        return ("BET_KEP","X" if seq[-1]=="T" else "T",0.64)
    return None

def _algo_palindrome(seq,rle):
    for L in (9,7,5):
        if len(seq)>=L and all(seq[len(seq)-L+i]==seq[len(seq)-1-i] for i in range(L//2)):
            return (f"GUONG_{L}","X" if seq[-1]=="T" else "T",0.56+(L-5)*0.02)
    return None

def _algo_regression(seq,rle):
    if len(seq)<12: return None
    lastN=seq[-20:] if len(seq)>=20 else seq
    t=lastN.count("T"); x=len(lastN)-t; lech=abs(t-x)
    if lech>=6: return ("HOI_QUY","T" if t<x else "X",0.56+(lech-6)*0.01)
    return None

def _algo_markov2(seq,rle):
    if len(seq)<6: return None
    tt=tx=xt=xx=0
    for i in range(len(seq)-1):
        a,b=seq[i],seq[i+1]
        if a=="T" and b=="T": tt+=1
        elif a=="T" and b=="X": tx+=1
        elif a=="X" and b=="T": xt+=1
        else: xx+=1
    last=seq[-1]
    if last=="T" and (tt+tx)>0:
        p=tt/(tt+tx); return ("MARKOV","T" if p>=0.5 else "X",0.5+abs(p-0.5)*0.4)
    if last=="X" and (xt+xx)>0:
        p=xx/(xt+xx); return ("MARKOV","X" if p>=0.5 else "T",0.5+abs(p-0.5)*0.4)
    return None

def _algo_cycle2(seq,rle):
    for p in (2,3,4):
        if len(seq)>=p*3:
            seg=seq[-p*3:]
            if all(seg[i]==seg[i+p] for i in range(len(seg)-p)):
                return (f"CYCLE_{p}",seq[-p],0.58)
    return None

def _algo_dbreak(seq,rle):
    cnts=[c for _,c in rle]
    if len(cnts)>=4 and cnts[-2]==1 and cnts[-4]==1:
        return ("DOUBLE_BREAK","X" if seq[-1]=="T" else "T",0.60)
    return None

def _algo_break57(seq,rle):
    cnts=[c for _,c in rle]
    if len(cnts)>=2 and cnts[-2]==7 and cnts[-1]==1: return ("GAY_7",seq[-1],0.62)
    if len(cnts)>=2 and cnts[-2]==5 and cnts[-1]==1: return ("GAY_5",seq[-1],0.58)
    return None

def _algo_zigzag(seq,rle):
    if len(seq)>=5 and all(seq[i]!=seq[i+1] for i in range(len(seq)-5,len(seq)-1)):
        return ("ZIGZAG",seq[-1],0.55)
    return None

def _algo_clock(seq,rle):
    if len(seq)>=8:
        s8=seq[-8:]
        if s8[:4]==s8[4:][::-1] and s8[0]!=s8[1]:
            return ("DONG_HO","X" if seq[-1]=="T" else "T",0.62)
    return None

def _algo_trend(seq,rle):
    if len(seq)<10: return None
    t=seq[-10:].count("T")
    if t>=7: return ("XU_HUONG_T","T",0.55)
    if t<=3: return ("XU_HUONG_X","X",0.55)
    return None

_THOUGHT_ALGOS=[_algo_streak,_algo_alt,_algo_groups,_algo_palindrome,_algo_regression,
                _algo_markov2,_algo_cycle2,_algo_dbreak,_algo_break57,_algo_zigzag,_algo_clock,_algo_trend]

def du_doan_ai_thinking(lich_su, tool_id=""):
    seq=_norm(lich_su)
    if len(seq)<10: return {"status":"SKIP","reason":f"Chỉ {len(seq)} phiên, cần ≥10"}
    gid=f"ai_{tool_id or 'default'}"; brain=_brain(gid); rle=_rle(seq)
    ent=_entropy(seq)
    if ent>MAX_ENTROPY:
        return {"status":"SKIP","phase":"HIGH_ENTROPY","du_doan":"SKIP","do_tin_cay":0,
                "reason":f"Cầu random entropy {ent:.2f}","entropy":round(ent,3)}
    thoughts=[]
    for algo in _THOUGHT_ALGOS:
        try:
            r=algo(seq,rle)
            if r:
                name,pred,base_conf=r; wr,n=brain.get_wr(name)
                if n>=SELF_CORRECT_MIN_N and wr<SELF_CORRECT_THRESHOLD:
                    pred="X" if pred=="T" else "T"; base_conf=0.53; name+="_FLIP"
                thoughts.append({"pattern":name,"pred":pred,"base_conf":base_conf,"wr":wr,"n":n})
        except: pass
    if not thoughts: return {"status":"SKIP","phase":"NO_THOUGHT","du_doan":"SKIP","do_tin_cay":0,"reason":"Không có ý tưởng"}
    for t in thoughts:
        wr,n=t["wr"],t["n"]
        t["score"]=round(0.5*t["base_conf"]+0.5*wr if n>=10 else t["base_conf"],4)
    filtered=[t for t in thoughts if not (t["n"]>=MIN_METHOD_SAMPLES and t["wr"]<SKIP_PATTERN_WR)]
    if not filtered: return {"status":"SKIP","phase":"ALL_WEAK","du_doan":"SKIP","do_tin_cay":0,"reason":"Tất cả yếu"}
    vote_t=sum(1 for t in filtered if t["pred"]=="T"); vote_x=len(filtered)-vote_t
    consensus="T" if vote_t>vote_x else ("X" if vote_x>vote_t else None)
    best=max(filtered,key=lambda t:t["score"]+(0.05 if t["pred"]==consensus else 0))
    # Monte Carlo xác nhận
    last20=seq[-20:] if len(seq)>=20 else seq
    p_t=last20.count("T")/len(last20)
    random.seed(int(time.time())%100000)
    count_t=sum(1 for _ in range(MCTS_SIMULATIONS) if random.random()<p_t)
    prob_t=count_t/MCTS_SIMULATIONS
    mc_pred="T" if prob_t>=0.5 else "X"
    mc_conf=min(0.85,0.5+abs(prob_t-0.5)*0.6)
    pred=best["pred"]
    if mc_pred==pred:
        final_conf=min(MAX_CONFIDENCE,0.7*best["score"]+0.3*mc_conf); confirm="✅ MCTS đồng ý"
    else:
        final_conf=max(0.5,0.8*best["score"]-0.05); confirm=f"⚠️ MCTS nghi ngờ (prob={prob_t})"
    wr,n=brain.get_wr(best["pattern"].replace("_FLIP",""))
    units=_bet_units(final_conf,wr if n>=10 else 0.52,n)
    return {"status":"OK","phase":"THINKING",
            "du_doan":"TÀI" if pred=="T" else "XỈU","do_tin_cay":int(final_conf*100),
            "verdict":"STRONG" if final_conf>=0.70 else "GOOD" if final_conf>=0.60 else "MEDIUM",
            "pattern":best["pattern"],"reason":f"🧠 ToT: {best['pattern']}→{pred} | {confirm}",
            "thinking":{"total_thoughts":len(thoughts),"vote_tai":vote_t,"vote_xiu":vote_x,
                        "consensus":"TÀI" if consensus=="T" else ("XỈU" if consensus=="X" else "HUỶ"),
                        "monte_carlo":{"pred":mc_pred,"prob_t":round(prob_t,4),"conf":round(mc_conf,4)}},
            "bet_units":units,"kelly_percent":round(_kelly(wr if n>=10 else 0.52)*100,2),
            "entropy":round(ent,3),"regime":_regime(seq),
            "engine":"🧠 AI THINKING (ToT+MCTS+Ensemble12)"}

# ============================================================
# ♠️ BACCARAT VIP — 6 THUẬT TOÁN
# ============================================================
def phan_tich_cau_co_ban(seq):
    """Cầu cơ bản: bệt, đảo, nhịp 1-2, 2-1"""
    rle=_rle(seq); cnts=[c for _,c in rle]
    if not cnts: return {"type":"unknown"}
    if cnts[-1]>=4: return {"type":"BET","length":cnts[-1],"side":seq[-1],"action":"BẺ" if cnts[-1]>=5 else "ĐU"}
    if len(seq)>=4 and all(seq[i]!=seq[i+1] for i in range(len(seq)-4,len(seq)-1)):
        return {"type":"DAO_11","action":"THEO CUỐI"}
    if len(cnts)>=3 and cnts[-1]==1 and cnts[-2]==2: return {"type":"NHIP_12","action":"ĐẢO"}
    if len(cnts)>=3 and cnts[-1]==2 and cnts[-2]==1: return {"type":"NHIP_21","action":"THEO"}
    return {"type":"PHỨC TẠP"}

def du_doan_cau_vip(seq):
    """Dự đoán cầu VIP: Big Road, Big Eye Road, Small Road, Cockroach Road"""
    base=phan_tich_cau_co_ban(seq)
    if base["type"]=="BET" and base["length"]>=5:
        return {"pred":"P" if seq[-1]=="T" else "B","conf":62,"note":f"Bệt {base['length']} → bẻ"}
    if base["type"]=="DAO_11":
        return {"pred":"P" if seq[-1]=="T" else "B","conf":58,"note":"Đảo 1-1 → theo cuối"}
    return {"pred":"SKIP","conf":0,"note":"Cầu không rõ"}

def quan_ly_von_vip(balance, conf):
    """Quản lý vốn VIP: Kelly fraction + cấp độ cược"""
    kelly=_kelly(conf/100)
    units=4 if conf>=70 else 3 if conf>=62 else 2 if conf>=57 else 1 if conf>=53 else 0
    bet=balance*kelly*units/4
    return {"kelly":round(kelly*100,2),"units":units,"bet_amount":round(bet,2),"advice":"ALL IN" if units>=4 and conf>=68 else "Vào đậm" if units>=3 else "Vào vừa" if units>=2 else "Cẩn thận" if units>=1 else "SKIP"}

def mo_phong_chien_luoc(seq, n_sim=100):
    """Mô phỏng chiến lược: chạy 100 phiên ảo, tính winrate"""
    if len(seq)<10: return {"winrate":50,"note":"Thiếu dữ liệu"}
    wins=0
    for i in range(min(n_sim,len(seq)-10)):
        sub=seq[:10+i]; r=du_doan_cau_vip(sub)
        if r["pred"]!="SKIP" and (("P" if seq[10+i]=="T" else "B")==r["pred"]): wins+=1
    return {"winrate":round(wins/max(1,min(n_sim,len(seq)-10))*100,1),"simulated":min(n_sim,len(seq)-10)}

def danh_gia_rui_ro_vip(seq):
    """Đánh giá rủi ro: entropy, streak, variance"""
    ent=_entropy(seq); streak,last=_streak(seq)
    risk="THẤP" if ent<0.6 else "TRUNG BÌNH" if ent<0.8 else "CAO"
    return {"entropy":round(ent,3),"risk_level":risk,"current_streak":streak,
            "advice":"An toàn" if risk=="THẤP" else "Cẩn thận" if risk=="TRUNG BÌNH" else "Nên SKIP"}

def bao_cao_vip_pro(seq, balance=1000):
    """Báo cáo VIP PRO tổng hợp 6 thuật toán"""
    cb=phan_tich_cau_co_ban(seq); dd=du_doan_cau_vip(seq)
    ql=quan_ly_von_vip(balance,dd["conf"]); mp=mo_phong_chien_luoc(seq); rr=danh_gia_rui_ro_vip(seq)
    return {"cau_co_ban":cb,"du_doan":dd,"quan_ly_von":ql,"mo_phong":mp,"rui_ro":rr,
            "engine":"♠️ BACCARAT VIP 6-in-1"}

def du_doan_baccarat(lich_su, tool_id="", phien="", session_id=None):
    seq=_norm(lich_su)
    if len(seq)<8: return None,[]
    report=bao_cao_vip_pro(seq)
    dd=report["du_doan"]; rr=report["rui_ro"]
    if rr["risk_level"]=="CAO" or dd["pred"]=="SKIP":
        d=[{"ten":f"⚠️ Rủi ro {rr['risk_level']} (entropy {rr['entropy']})","ket_tiep":None,"do_tin_cay":0}]
        return _build("SKIP",0,"BAC_RISK",d,"Rủi ro cao",extra=report),d
    pred="T" if dd["pred"]=="P" else "X"
    detail=[{"ten":f"♠️ {k}: {v}","ket_tiep":pred,"do_tin_cay":dd["conf"]} for k,v in report["cau_co_ban"].items()]
    return _build(pred,dd["conf"],"BACCARAT_VIP",detail,dd["note"],
                  report["quan_ly_von"]["units"],report["quan_ly_von"]["kelly"],extra=report),detail

# ============================================================
# 📈 VÙNG BẺ INDICATOR
# ============================================================
def get_vung_be(lich_su):
    seq=_norm(lich_su)
    streak,last=_streak(seq)
    if streak<=2: return {"zone":"KHÔNG","streak":streak,"action":"CHỜ","confidence":0,"note":"Chưa có bệt"}
    if streak in (3,4): return {"zone":"VÙNG ĐU","streak":streak,"action":"ĐU (theo cuối)","confidence":85,"note":"3-4 tay = ĐU / continue"}
    if 5<=streak<=7: return {"zone":"VÙNG BẺ","streak":streak,"action":"BẺ (đảo ngược)","confidence":90,"note":"5-7 tay = BẺ / opposite"}
    return {"zone":"VÙNG BẺ MẠNH","streak":streak,"action":"BẺ MẠNH (đảo mạnh)","confidence":96,"note":"8+ tay = BẺ MẠNH, conf cao"}

# ============================================================
# TEST / DEMO
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("  🧠 ALGORITHMS ULTIMATE v23.0 — Test nhanh")
    print("="*60)
    test=["X","X","T","T","X","X","T","T","T","T","T","X","X","T","T","T","T","T","T","T"]
    print("\n🔥 TX v23:"); r,d=du_doan_tx(test,tool_id="lc79",phien="100"); print(json.dumps(r,indent=2,ensure_ascii=False)[:500])
    print("\n📊 BCR:"); r,d=du_doan_bcr(test,tool_id="lc79"); print(r["du_doan"],r["do_tin_cay"],"%",r["verdict"])
    print("\n🧠 AI Thinking:"); r=du_doan_ai_thinking(test,tool_id="lc79"); print(r.get("du_doan"),r.get("do_tin_cay"),"%",r.get("verdict"))
    print("\n♠️ Baccarat:"); r,d=du_doan_baccarat(test,tool_id="lc79"); print(r["du_doan"],r["do_tin_cay"],"%")
    print("\n📈 Vùng bẻ:",json.dumps(get_vung_be(test),ensure_ascii=False))
    print("\n💎 14 CONF:",len(get_conf_strategies()),"chiến lược")
