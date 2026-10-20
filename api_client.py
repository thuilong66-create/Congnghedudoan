#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 API CLIENT MODULE - VIP PRO WEB v6.0 ULTIMATE
50+ Tool Tài Xỉu + Baccarat — API mới nhất
(Mở rộng từ 21 tool gốc: thêm 789club, F8bet, New88, Jun88, Hi88, 388bet,
 King88, M88, V9bet, FB88, 12bet, Tiger88, Red88, Go88, VK789, FV88...)
"""
import time
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()

# ═══════════════════════════════════════════════
# API KEY dùng chung (kwinstore platform)
# ═══════════════════════════════════════════════
_KW_KEY = "6cd333eb6f42c778fb6ecbfd6fe8f14337f376d8b7fca424"

def _kw(slug, game):
    return f"https://kwinstore.com/{slug}/{game}/history/{_KW_KEY}"

# ═══════════════════════════════════════════════
# CẤU HÌNH 50+ TOOL TÀI XỈU
#   loai: TX (hũ/thường), MD5, SICBO
# ═══════════════════════════════════════════════
TOOLS_CONFIG = {
    'lc79_hu':    {'name':'LC79 Hũ',     'full_name':'LC79 - Tài Xỉu Hũ',     'nhom':'LC79',    'loai':'TX',  'api_url':'https://wtx.tele68.com/v1/tx/lite-sessions',       'parser':'tele68'},
    'lc79_md5':   {'name':'LC79 MD5',    'full_name':'LC79 - Tài Xỉu MD5',    'nhom':'LC79',    'loai':'MD5', 'api_url':'https://wtxmd52.tele68.com/v1/txmd5/sessions', 'parser':'tele68'},
    'betvip_tx':  {'name':'BETVIP',      'full_name':'BETVIP - Tài Xỉu',      'nhom':'BETVIP',  'loai':'TX',  'api_url':'https://wtx.macminim6.online/v1/tx/lite-sessions', 'parser':'tele68'},
    'sunwin_tx':  {'name':'Sunwin',      'full_name':'Sunwin - Tài Xỉu',      'nhom':'SUNWIN',  'loai':'TX',  'api_url':'wss://websocket.gmwin.io/wsbinary', 'parser':'sunwin_ws'},
}

# API Baccarat (60+ bàn)
BCR_API = "https://bcf-ayt4.onrender.com/sexy/all"

# Ảnh game — nhóm mới dùng lại ảnh có sẵn (an toàn, không 404)
GAME_IMAGES = {
    '68GB': 'https://i.ibb.co/S4TPspjJ/IMG-20260826-135222.jpg',
    'B52': 'https://i.ibb.co/BKtFRs37/IMG-20260826-135320.jpg',
    'HITCLUB': 'https://i.ibb.co/tPz9XrTP/IMG-20260826-135320.jpg',
    'MAX789': 'https://i.ibb.co/pvgWwHpK/IMG-20260826-135430.jpg',
    'RIKVIP': 'https://i.ibb.co/FLtmQzZJ/IMG-20260902-100653.jpg',
    'SUMCLUB': 'https://i.ibb.co/Q7vN703F/IMG-20260826-135405.jpg',
    'SUNWIN': 'https://i.ibb.co/1YKqJ9nB/IMG-20260826-135238.jpg',
    'LC79': 'https://i.ibb.co/4nbt6wLY/IMG-20260826-135300.jpg',
    'BETVIP': 'https://i.ibb.co/JRFTSvTP/IMG-20260826-135405.jpg',
    'BACCARAT': 'https://i.ibb.co/4gfQdx5t/Screenshot-2026-09-02-10-06-23-248-com-coccoc-trinhduyet.jpg',
    # Nhóm mới — map lại ảnh có sẵn theo sắc thái
    '789CLUB': 'https://i.ibb.co/S4TPspjJ/IMG-20260826-135222.jpg',
    'F8BET':   'https://i.ibb.co/BKtFRs37/IMG-20260826-135320.jpg',
    'NEW88':   'https://i.ibb.co/vxWppsF4/IMG-20260826-135300.jpg',
    'JUN88':   'https://i.ibb.co/Q7vN703F/IMG-20260826-135405.jpg',
    'HI88':    'https://i.ibb.co/FLtmQzZJ/IMG-20260902-100653.jpg',
    '388BET':  'https://i.ibb.co/S4TPspjJ/IMG-20260826-135222.jpg',
    'KING88':  'https://i.ibb.co/BKtFRs37/IMG-20260826-135320.jpg',
    'M88':     'https://i.ibb.co/vxWppsF4/IMG-20260826-135300.jpg',
    'V9BET':   'https://i.ibb.co/Q7vN703F/IMG-20260826-135405.jpg',
    'FB88':    'https://i.ibb.co/FLtmQzZJ/IMG-20260902-100653.jpg',
    '12BET':   'https://i.ibb.co/21g113nY/IMG-20260826-135238.jpg',
    'TIGER88': 'https://i.ibb.co/v68R7XYG/IMG-20260826-135348.jpg',
    'RED88':   'https://i.ibb.co/S4TPspjJ/IMG-20260826-135222.jpg',
    'GO88':    'https://i.ibb.co/BKtFRs37/IMG-20260826-135320.jpg',
    'VK789':   'https://i.ibb.co/vxWppsF4/IMG-20260826-135300.jpg',
    'FV88':    'https://i.ibb.co/Q7vN703F/IMG-20260826-135405.jpg',
}

LOGO_URL = "https://i.ibb.co/Pz6sRwMk/IMG-20261019-091158-458.jpg"
QR_ZALOPAY = "https://i.postimg.cc/Y0KbjzYx/IMG-20260826-140021.jpg"

# Link web chính thức của từng tool (click widget → mở web)
TOOL_WEB_LINKS = {
    'LC79': 'https://lc79.bet',
    'BETVIP': 'https://play.betvip.land/?utm_source=betvip.fit&utm_campaign=betvip.fit&utm_medium=betvip.fit&utm_term=betvip.fit',
    'SUNWIN': 'https://sun.win',
}
# Ảnh nhân vật widget con dự đoán bay
WIDGET_CHAR_IMG = "data:image/png;base64,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"

NHOM_TOOL = list(dict.fromkeys(cfg['nhom'] for cfg in TOOLS_CONFIG.values()))

# Cache
API_CACHE = {}
CACHE_TTL = 3

# ═══════════════════════════════════════════════
# PARSERS
# ═══════════════════════════════════════════════
def kq_to_char(r):
    if not r: return ''
    s = str(r).upper()
    if 'TAI' in s or s=='T' or 'TÀI' in s or 'BIG' in s or '大' in s: return 'T'
    if 'XIU' in s or s=='X' or 'XỈU' in s or 'SMALL' in s or '小' in s: return 'X'
    return ''

def find_list(obj):
    for k in ['data','Data','result','Result','list','List','items','Items',
              'history','History','sessions','Sessions','records','Records']:
        if k in obj:
            v=obj[k]
            if isinstance(v, list): return v
            if isinstance(v, dict):
                for k2 in ['list','List','items','Items','data','Data']:
                    if k2 in v and isinstance(v[k2], list): return v[k2]
    if 'data' in obj and isinstance(obj['data'], dict):
        return [obj['data']]
    for v in obj.values():
        if isinstance(v, list): return v
    return None

def parse_kwinstore(raw):
    arr = raw if isinstance(raw, list) else (find_list(raw) or [])
    out = []
    for p in arr:
        if not isinstance(p, dict): continue
        kq = ''
        for k in ['result','Result','kết quả','ket_qua','ketqua','kq','KQ','outcome','Outcome',
                  'type','Type','value','Value','big_small','tai_xiu','resultTruyenThong']:
            if k in p and p[k]:
                val = str(p[k])
                if val.lower() in ('đang chạy','đã có kết quả','pending','running','finished'): continue
                kq = val; break
        if not kq:
            d1=d2=d3=None
            for t1,t2,t3 in [('d1','d2','d3'),('xuc_xac_1','xuc_xac_2','xuc_xac_3'),
                            ('dice1','dice2','dice3'),('Dice1','Dice2','Dice3')]:
                if t1 in p and t2 in p and t3 in p:
                    d1,d2,d3=p.get(t1),p.get(t2),p.get(t3); break
            if d1 is None:
                for k in ['dices','Dices','dice','Dice','results','Results']:
                    if k in p and isinstance(p[k], list) and len(p[k])>=3:
                        d1,d2,d3=p[k][0],p[k][1],p[k][2]; break
            if d1 is not None:
                try:
                    tong=int(d1)+int(d2)+int(d3)
                    kq='TAI' if tong>10 else 'XIU'
                except: pass
        mp=''
        for k in ['session','Session','id','Id','ID','_id','round','Round','phiên','phien',
                  'code','Code','num','Num','number','Number','index','Index','gameNum']:
            if k in p and p[k]: mp=str(p[k]); break
        c=kq_to_char(kq)
        if c in ('T','X'):
            out.append({'ma_phien':mp,'ket_qua':c,'ket_qua_text':str(kq or '')})
    out.reverse()
    return out

def parse_kwinstore_sicbo(raw):
    arr = raw if isinstance(raw, list) else (find_list(raw) or [])
    out = []
    for p in arr:
        if not isinstance(p, dict): continue
        diem=None
        for k in ['score','Score','total','Total','sum','Sum','tong','Tong']:
            if k in p and p[k] is not None:
                try: diem=int(p[k]); break
                except: pass
        kq=''
        if diem is not None:
            if 4<=diem<=10: kq='XIU'
            elif 11<=diem<=17: kq='TAI'
            else: continue
        else:
            for k in ['result','Result','kq','KQ','outcome','Outcome','ket_qua','kết quả']:
                if k in p and p[k]: kq=p[k]; break
            if not kq:
                d1=d2=d3=None
                for t1,t2,t3 in [('d1','d2','d3'),('xuc_xac_1','xuc_xac_2','xuc_xac_3')]:
                    if t1 in p and t2 in p and t3 in p:
                        d1,d2,d3=p.get(t1),p.get(t2),p.get(t3); break
                if d1 is None:
                    for k in ['dices','Dices','faces','Faces','facesList','keyR']:
                        if k in p:
                            v=p[k]
                            if isinstance(v, list) and len(v)>=3:
                                d1,d2,d3=v[0],v[1],v[2]; break
                            if isinstance(v, str) and '-' in v:
                                try:
                                    parts=list(map(int,v.split('-')))
                                    if len(parts)>=3: d1,d2,d3=parts[0],parts[1],parts[2]; break
                                except: pass
                if d1 is not None:
                    try:
                        tong=int(d1)+int(d2)+int(d3)
                        if 4<=tong<=10: kq='XIU'
                        elif 11<=tong<=17: kq='TAI'
                        else: continue
                    except: pass
        mp=''
        for k in ['session','Session','id','Id','ID','round','Round','phiên','phien',
                  'gameNum','GameNum','code','Code']:
            if k in p and p[k]: mp=str(p[k]); break
        if mp.upper().startswith('S'): mp=mp[1:]
        c=kq_to_char(kq)
        if c in ('T','X'):
            ph={'ma_phien':mp,'ket_qua':c,'ket_qua_text':str(kq or '')}
            if diem is not None: ph['diem']=diem
            out.append(ph)
    out.reverse()
    return out

def parse_tele68(raw):
    arr = raw if isinstance(raw, list) else []
    if isinstance(raw, dict):
        if 'sessions' in raw and isinstance(raw['sessions'],list): arr=raw['sessions']
        elif 'data' in raw and isinstance(raw['data'],list): arr=raw['data']
        elif 'list' in raw and isinstance(raw['list'],list): arr=raw['list']
        else: arr=find_list(raw) or []
    out = []
    for p in arr:
        if not isinstance(p, dict): continue
        kq=''
        for k in ['result','big_small','tai_xiu','outcome','value','type','resultTruyenThong']:
            if k in p and p[k] is not None: kq=p[k]; break
        if not kq and 'total' in p and p['total'] is not None:
            try: kq='TAI' if int(p['total'])>10 else 'XIU'
            except: pass
        if not kq and 'dices' in p and isinstance(p['dices'], list) and len(p['dices'])>=3:
            try:
                tong=int(p['dices'][0])+int(p['dices'][1])+int(p['dices'][2])
                kq='TAI' if tong>10 else 'XIU'
            except: pass
        mp=''
        for k in ['id','session','session_id','round','code','number','num','_id']:
            if k in p and p[k] is not None: mp=str(p[k]); break
        c=kq_to_char(kq)
        if c in ('T','X'):
            out.append({'ma_phien':mp,'ket_qua':c,'ket_qua_text':str(kq or '')})
    out.reverse()
    return out

def parse_sunwin_ws(raw):
    # raw la list history tu websocket (da decode)
    out = []
    if isinstance(raw, list):
        for p in raw:
            if not isinstance(p, dict): continue
            kq = ''
            for k in ['result','big_small','tai_xiu','resultTruyenThong','diceResult']:
                if k in p and p[k]: kq = str(p[k]); break
            mp = str(p.get('id','') or p.get('session','') or p.get('round',''))
            c = kq_to_char(kq)
            if c in ('T','X'): out.append({'ma_phien':mp,'ket_qua':c,'ket_qua_text':kq})
    out.reverse()
    return out

def _fetch_sunwin_ws():
    """Best-effort: lay lich su Sunwin qua websocket MsgPack. Can msgpack + websocket-client."""
    try:
        import websocket, json, time
        try:
            import msgpack
        except ImportError:
            return None
        TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJnZW5kZXIiOjAsImNhblZpZXdTdGF0IjpmYWxzZSwiZGlzcGxheU5hbWUiOiJhbmhsYXRpZW5kYXRhb3giLCJib3QiOjAsImlzTWVyY2hhbnQiOmZhbHNlLCJ2ZXJpZmllZEJhbmtBY2NvdW50IjpmYWxzZSwicGxheUV2ZW50TG9iYnkiOmZhbHNlLCJjdXN0b21lcklkIjozNjI0NzAwNTAsImFmZklkIjoiR0VNV0lOIiwiYmFubmVkIjpmYWxzZSwiYnJhbmQiOiJnZW0iLCJlbWFpbCI6IiIsInRpbWVzdGFtcCI6MTc4NjYxNDkxNTM0MywibG9ja0dhbWVzIjpbXSwiYW1vdW50IjowLCJsb2NrQ2hhdCI6ZmFsc2UsInBob25lVmVyaWZpZWQiOmZhbHNlLCJpcEFkZHJlc3MiOiIxNC4yNDcuMTY1LjcxIiwibXV0ZSI6ZmFsc2UsImF2YXRhciI6Imh0dHBzOi8vaW1hZ2VzLnN3aW5zaG9wLm5ldC9pbWFnZXMvYXZhdGFyL2F2YXRhcl8wOS5wbmciLCJwbGF0Zm9ybUlkIjo0LCJ1c2VySWQiOiIwMDQ3NGE5MS01NmUwLTRmOWEtODA1MC0yOTEyMDgyOGY2ZTYiLCJlbWFpbFZlcmlmaWVkIjpudWxsLCJyZWdUaW1lIjoxNzg2NjE0OTE1MzM0LCJwaG9uZSI6IiIsImRlcG9zaXQiOmZhbHNlLCJ1c2VybmFtZSI6IkdNX2U0NDRyNjV0Zzd5dWhpIn0.wzzXHCn0iZl8P51m7mRrhwzhzvrPMFoAYv1VWXSM9yY"
        url = "wss://websocket.gmwin.io/wsbinary?token=" + TOKEN
        ws = websocket.create_connection(url, timeout=15, header=["User-Agent: Mozilla/5.0", "Origin: https://web.gemwin.rsvp"])
        # Gui initial messages (MsgPack)
        info = {"ipAddress":"14.247.165.71","wsToken":TOKEN,"locale":"vi","userId":"00474a91-56e0-4f9a-8050-29120828f6e6","username":"GM_e444r65te7yuhi","timestamp":int(time.time()*1000)}
        ws.send_binary(msgpack.packb([1,"MiniGame","GM_56dtybiuijn","",{"info":json.dumps(info),"signature":"PLACEHOLDER"}]))
        ws.send_binary(msgpack.packb([6,"MiniGame","taixiuPlugin",{"cmd":1005}]))
        ws.send_binary(msgpack.packb([6,"MiniGame","lobbyPlugin",{"cmd":10001}]))
        history = []
        for _ in range(15):
            try:
                data = ws.recv()
                if isinstance(data, bytes):
                    msg = msgpack.unpackb(data, raw=False)
                    # Tim history trong message
                    def find_hist(o):
                        if isinstance(o, list) and o and isinstance(o[0], dict):
                            if any('result' in str(x) or 'tai' in str(x).lower() for x in o[:2]): return o
                        if isinstance(o, dict):
                            for v in o.values():
                                r = find_hist(v)
                                if r: return r
                        if isinstance(o, list):
                            for v in o:
                                r = find_hist(v)
                                if r: return r
                        return None
                    h = find_hist(msg)
                    if h and len(h) >= 5:
                        history = h; break
            except Exception:
                continue
        ws.close()
        return history if history else None
    except Exception:
        return None

PARSERS = {'kwinstore': parse_kwinstore, 'kwinstore_sicbo': parse_kwinstore_sicbo, 'tele68': parse_tele68, 'sunwin_ws': parse_sunwin_ws}

# ═══════════════════════════════════════════════
# API CALLS
# ═══════════════════════════════════════════════
def call_api(url, timeout=20):
    try:
        h={'Accept':'application/json','Cache-Control':'no-cache',
           'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        if 'kwinstore.com' in url:
            h['Origin']='https://kwinstore.com'; h['Referer']='https://kwinstore.com/'
        r=requests.get(url, timeout=timeout, headers=h, verify=False)
        if r.status_code==200: return r.json()
        return None
    except:
        return None

def get_tool_data(tid):
    if tid not in TOOLS_CONFIG: return None
    cfg=TOOLS_CONFIG[tid]
    now=time.time()
    if tid in API_CACHE and now-API_CACHE[tid]['time']<CACHE_TTL:
        return API_CACHE[tid]['data']
    if cfg.get('parser') == 'sunwin_ws':
        raw = _fetch_sunwin_ws()
    else:
        raw=call_api(cfg['api_url'])
    pf=PARSERS.get(cfg['parser'], parse_kwinstore)
    ph=pf(raw) if raw else []
    ls=[p['ket_qua'] for p in ph]
    pc=ph[-1]['ma_phien'] if ph else ''
    res={'tool_id':tid,'name':cfg['name'],'full_name':cfg['full_name'],
         'nhom':cfg['nhom'],'loai':cfg['loai'],'lich_su':ls,
         'cac_phien':ph,'phien':pc,'so_phien':len(ph)}
    API_CACHE[tid]={'time':now,'data':res}
    return res

def get_bcr_data():
    now=time.time()
    cache_key='_bcr_all'
    if cache_key in API_CACHE and now-API_CACHE[cache_key]['time']<CACHE_TTL:
        return API_CACHE[cache_key]['data']
    try:
        raw=call_api(BCR_API, timeout=15)
        if not raw: return None
        tables=[]
        for item in raw:
            ban=item.get('ban','')
            cau=item.get('cau','')
            kq=item.get('ket_qua','')
            phien=item.get('phien',0)
            gio=item.get('time','')
            history=list(kq.upper())
            if not cau:
                pb=[c for c in history if c in ('P','B')]
                if len(pb)>=5:
                    dao=sum(1 for i in range(1,len(pb)) if pb[i]!=pb[i-1])
                    if dao/(len(pb)-1)>=0.7: cau='Cầu đảo'
                    else: cau='Cầu bình thường'
                else: cau='Chưa rõ'
            tables.append({'ban':ban,'cau':cau,'history':history,'phien':phien,'gio':gio,'so_phien':len(history)})
        def sort_key(b):
            ban=b['ban']
            try:
                if ban.startswith('C'): return (100,int(ban[1:]))
                return (0,int(ban))
            except: return (50,0)
        tables.sort(key=sort_key)
        API_CACHE[cache_key]={'time':now,'data':tables}
        return tables
    except:
        return None

def tools_by_group():
    g={}
    for tid,cfg in TOOLS_CONFIG.items():
        n=cfg['nhom']
        if n not in g: g[n]=[]
        g[n].append({'id':tid,'name':cfg['name'],'full_name':cfg['full_name'],'loai':cfg['loai']})
    return g
