import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import json
import time
import warnings
from datetime import datetime, timedelta, timezone
import pytz
warnings.filterwarnings('ignore')

# --- إعدادات البوت ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8815214541:AAHpNRe1yFeMcDQCQ6U8KQz1h49Un8cZ3ZI')
CHAT_ID = os.environ.get('CHAT_ID', '208377256')

# --- قوائم الأسهم ---
DEFAULT_STOCKS = ['2222.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR', '2030.SR', '1150.SR', '2380.SR', '2280.SR', '2090.SR']
ALL_SA_STOCKS = ['2222 0, '.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR', '2030.SR', '1150.SR', '2380.SR', '2280.SR', '2090.SR', '1211.SR', '2060.SR', '4001.SR', '4030.SR', '6010.SR', '8010.SR', '1010.SR', '1020.SR', '1030.SR', '1050.SR', '1060.SR', '1140.SR', '1201.SR', '1210.SR', '2001.SR', '2020.SR', '2040.SR', '2050.SR', '2060.SR', '2070.SR', '2080.SR', '2090.SR', '2100.SR', '2110.SR', '2120.SR', '2130.SR', '2140.SR', '2150.SR', '2160.SR', '2170.SR', '2180.SR', '2190.SR', '2200.SR', '2210.SR', '2220.SR', '2230.SR', '2240.SR', '2250.SR', '2260.SR', '2270.SR', '2290.SR', '2300.SR', '2310.SR', '2320.SR', '2330.SR', '2340.SR', '2350.SR', '2360.SR', '2370.SR', '2390.SR', '4002.SR', '4003.SR', '4004.SR', '4005.SR', '4006.SR', '4007.SR', '4008.SR', '4009.SR', '4010.SR', '4011.SR', '4012.SR', '4013.SR', '4014.SR', '4015.SR', '4016.SR', '4017.SR', '4018.SR', '4019.SR', '4020.SR', '4031.SR', '4040.SR', '4050.SR', '4060.SR', '4061.SR', '4062.SR', '4063.SR', '6020.SR', '6030.SR', '6040.SR', '6050.SR', '6060.SR', '6070.SR', '6080.SR', '7020.SR', '7030.SR', '7040.SR', '7050.SR', '7060.SR', '7070.SR', '7080.SR', '8020.SR', '8030.SR', '8040.SR', '8050.SR', '8060.SR', '8070.SR', '8080.SR', '^TASI.SR']

STOCK_NAMES = {'2222.SR': 'أرامكو', '1120.SR': 'الراجحي', '2010.SR': 'سابك', '1180.SR': 'الأهلي', '7010.SR': 'STC', '2030.SR': 'سابك للمغذيات', '1150.SR': 'الإنماء', '2380.SR': 'معادن', '2280.SR': 'المراعي', '2090.SR': 'جرير', '1211.SR': 'معادن', '2060.SR': 'كيان السعودية', '4001.SR': 'دار الأركان', '4030.SR': 'ريت الراجحي', '6010.SR': 'Bupa العربية', '8010.SR': 'مصرف الإنماء', '1010.SR': 'الرياض للتعمير', '1020.SR': 'أسمنت الشرقية', '1030.SR': 'أسمنت الجنوبية', '1050.SR': 'أسمنت المدينة', '1060.SR': 'أسمنت القصيم', '1140.SR': 'البنك الفرنسي', '1201.SR': 'تكامل', '1210.SR': 'سابكو', '2001.SR': 'شمس', '2020.SR': 'سابك للمعادن', '2040.SR': 'سبكيم', '2050.SR': 'الصحراء', '2070.SR': 'التصنيع', '2080.SR': 'العجين', '2100.SR': 'الزامل', '2110.SR': 'ساكو', '2120.SR': 'المراعي', '2130.SR': 'هرفي', '2140.SR': 'نادك', '2150.SR': 'البابطين', '2160.SR': 'التصنيع', '2170.SR': 'الصرايعي', '2180.SR': 'غازكو', '2190.SR': 'أمنيات', '2200.SR': 'معادن ألمنيوم', '2210.SR': 'أمنيات', '2220.SR': 'أمنيات', '2230.SR': 'أمنيات', '2240.SR': 'ملاث', '2250.SR': 'التعاونية', '2260.SR': 'بوبا العربية', '2270.SR': 'مدجلف', '2290.SR': 'اتحاد الخليج', '2300.SR': 'الأهلي تكافل', '2310.SR': 'الراجحي تكافل', '2320.SR': 'ولاء', '2330.SR': 'سلامة', '2340.SR': 'اتحاد اتصالات', '2350.SR': 'زين', '2360.SR': 'أثير', '2370.SR': 'الحلول', '2390.SR': 'أثير', '4002.SR': 'الأحساء', '4003.SR': 'جبل عمر', '4004.SR': 'مكة للإنشاء', '4005.SR': 'إعمار المدينة', '4006.SR': 'دار الأركان', '4007.SR': 'جبل عمر', '4008.SR': 'عسير', '4009.SR': 'الأندلس', '4010.SR': 'طيبة', '4011.SR': 'مكة للإنشاء', '4012.SR': 'الأحساء', '4013.SR': 'جبل عمر', '4014.SR': 'إعمار المدينة', '4015.SR': 'دار الأركان', '4016.SR': 'طيبة', '4017.SR': 'عسير', '4018.SR': 'الأندلس', '4019.SR': 'مكة للإنشاء', '4020.SR': 'جبل عمر', '4031.SR': 'ريت الراجحي', '4040.SR': 'جدوى ريت', '4050.SR': 'الإنماء ريت', '4060.SR': 'الرياض ريت', '4061.SR': 'الأهلي ريت', '4062.SR': 'البلاد ريت', '4low_volume': 063.SR': 'الإنماء ريت', '6020.SR': 'بوبا العربية', '6030.SR': 'التعاونية', '6040, 'weak0.SR': 'مدجلف_trend': ', '6050.SR': 'اتحاد الخليج', '6060, 'wrong0.SR': 'ملاث', '6070.SR': 'سلامة', '6080.SR': 'ولاء',_macd':  '7020.SR': '0}
   ساكو', '703 for pred in recent0.SR': 'هرفي', '7040.SR': 'نادك', '7050.SR': ':
        tryالبابطين', '706:
            data0.SR': = yf.Ticker(pred['symbol']).history(period='1d', interval 'الصرايعي', '7070.SR': 'التصنيع', '7080.SR': 'غازكو', '8020.SR': 'أمنيات', '8030.SR': 'أمنيات', '8040.SR': 'أمنيات', '8050.SR': 'أمنيات', '8060.SR': 'ملاث', '8070.SR': 'التعاونية', '8080.SR': 'بوبا العربية', '^TASI.SR': 'مؤشر تاسي'}

PROCESSED_FILE, LEARNING_FILE, SETTINGS_FILE, NEWS_FILE, WATCHLIST_FILE, ALERTS_FILE, PORTFOLIO_FILE = 'processed.json', 'learning_data.json', 'bot_settings.json', 'news_cache.json', 'watchlist.json', 'price_alerts.json', 'portfolio.json'

def load_json(fn, default=None):
    if default is None: default = {}
    try:
        with open(fn, 'r', encoding='utf-8') as f: return json.load(f)
    except: return default

def save_json(fn, data):
    with open(fn, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)

def get_settings():
    defaults = {'capital': 50000, 'risk_percent': 2.0, 'rsi_threshold': 35, 'accuracy_score': 0, 'total_predictions': 0, 'correct_predictions': 0, 'last_adjustment': None, 'last_fast_learning': None, 'mistake_patterns': {'high_rsi': 0, 'low_volume': 0, 'weak_trend': 0, 'wrong_macd': 0}}
    settings = load_json(SETTINGS_FILE, defaults)
    for key in defaults:
        if key not in settings: settings[key] = defaults[key]
    return settings

def get_watchlist():
    data = load_json(WATCHLIST_FILE, {'stocks': DEFAULT_STOCKS.copy()})
    if 'stocks' not in data: data['stocks'] = DEFAULT_STOCKS.copy()
    return data['stocks']

def add_to_watchlist(symbol):
    symbol = symbol.upper() + ('' if symbol.upper().endswith('.SR') else '.SR')
    if symbol not in ALL_SA_STOCKS: return False, f"❌ {symbol} غير موجود"
    data = load_json(WATCHLIST_FILE, {'stocks': DEFAULT_STOCKS.copy()})
    if 'stocks' not in data: data['stocks'] = DEFAULT_STOCKS.copy()
    if symbol not in data['stocks']:
        data['stocks'].append(symbol)
        save_json(WATCHLIST_FILE, data)
        return True, f"✅ تمت إضافة {STOCK_NAMES.get(symbol, symbol)} ({symbol.replace('.SR', '')})"
    return False, f"⚠️ {symbol} موجود بالفعل"

def remove_from_watchlist(symbol):
    symbol = symbol.upper() + ('' if symbol.upper().endswith('.SR') else '.SR')
    data = load_json(WATCHLIST_FILE, {'stocks': DEFAULT_STOCKS.copy()})
    if 'stocks' not in data: data['stocks'] = DEFAULT_STOCKS.copy()
    if symbol in data['stocks']:
        data['stocks'].remove(symbol)
        save_json(WATCHLIST_FILE, data)
        return True, f"✅ تمت إزالة {symbol}"
    return False, f"⚠️ {symbol} غير موجود"

def send_telegram(msg, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        if len(msg) > 4000:
            for i in range(0, len(msg), 4000):
                requests.post(url, json={"chat_id": CHAT_ID, "text": msg[i:i+4000], "parse_mode": parse_mode}, timeout=10)
                time.sleep(0.5)
            return True
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": parse_mode}, timeout=10)
        return True
    except: return False

def get_bot_id():
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe", timeout=5).json()
        return r['result']['id'] if r.get('ok') else None
    except: return None

def get_processed():
    data = load_json(PROCESSED_FILE, {'processed': [], 'date': ''})
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if data.get('date') != today:
        data = {'processed': [], 'date': today}
        save_json(PROCESSED_FILE, data)
    return data.get('processed', [])

def add_processed(uid):
    data = load_json(PROCESSED_FILE, {'processed': [], 'date': ''})
    if uid not in data['processed']:
        data['processed'].append(uid)
        if len(data['processed']) > 500: data['processed'] = data['processed'][-250:]
        save_json(PROCESSED_FILE, data)

def get_current_time():
    saudi_tz = timezone(timedelta(hours=3))
    now = datetime.now(timezone.utc).astimezone(saudi_tz)
    return {'saudi': now.strftime('%Y-%m-%d %H:%M:%S'), 'saudi_short': now.strftime('%H:%M'), 'date': now.strftime('%Y-%m-%d'), 'hour': now.hour, 'minute': now.minute}

def get_market_status():
    try:
        saudi_tz = timezone(timedelta(hours=3))
        now = datetime.now(timezone.utc).astimezone(saudi_tz)
        day = now.weekday()
        mins = now.hour * 60 + now.minute
        days_ar = {0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء', 3: 'الخميس', 4: 'الجمعة', 5: 'السبت', 6: 'الأحد'}
        if day in [4, 5]: return {'status': 'مغلق', 'emoji': '🔴', 'reason': 'عطلة نهاية الأسبوع', 'next_open': 'الأحد 10:00 صباحاً', 'day': days_ar[day]}
        if mins < 600: return {'status': 'مغلق', 'emoji': '🔴', 'reason': 'قبل الافتتاح', 'next_open': '10:00 صباحاً', 'day': days_ar[day]}
        elif mins < 900: return {'status': 'مفتوح', 'emoji': '🟢', 'reason': 'جلسة التداول نشطة', 'next_open': 'جاري التداول', 'day': days_ar[day]}
        else: return {'status': 'مغلق', 'emoji': '🔴', 'reason': 'بعد الإغلاق', 'next_open': 'غداً 10:00 صباحاً', 'day': days_ar[day]}
    except: return {'status': 'غير معروف', 'emoji': '⚪', 'reason': 'خطأ', 'next_open': 'غير معروف', 'day': ''}

def get_tasi_index():
    try:
        data = yf.Ticker('^TASI.SR').history(period='5d')
        if len(data) > 0:
            c, p = float(data['Close'].iloc[-1]), float(data['Close'].iloc[-2])
            return {'price': round(c, 2), 'change': round(((c - p) / p) * 100, 2)}
    except: pass
    return None

def get_vix():
    try:
        data = yf.Ticker('^VIX').history(period='5d')
        if len(data) > 0:
            c = float(data['Close'].iloc[-1])
            if c < 15: return {'value': round(c, 2), 'level': 'منخفض', 'emoji': '🟢'}
            elif c < 20: return {'value': round(c, 2), 'level': 'معتدل', 'emoji': '🟡'}
            elif c < 30: return {'value': round(c, 2), 'level': 'مرتفع', 'emoji': '🟠'}
            else: return {'value': round(c, 2), 'level': 'مرتفع جداً', 'emoji': '🔴'}
    except: pass
    return None

def get_fear_greed_index():
    try:
        indicators = {}
        vix = get_vix()
        if vix: indicators['vix'] = 80 if vix['value'] < 15 else 60 if vix['value'] < 20 else 40 if vix['value'] < 30 else 20
        tasi = get_tasi_index()
        if tasi: indicators['tasi'] = 80 if tasi['change'] > 2 else 65 if tasi['change'] > 1 else 50 if tasi['change'] > -1 else 35 if tasi['change'] > -2 else 20
        adv, dec = 0, 0
        for sym in DEFAULT_STOCKS[:10]:
            try:
                d = yf.Ticker(sym).history(period='2d')
                if len(d) >= 2:
                    if float(d['Close'].iloc[-1]) > float(d['Close'].iloc[-2]): adv += 1
                    elif float(d['Close'].iloc[-1]) < float(d['Close'].iloc[-2]): dec += 1
            except: continue
        if adv + dec > 0: indicators['breadth'] = int((adv / (adv + dec)) * 100)
        if indicators:
            score = round(sum(indicators.values()) / len(indicators), 1)
            if score >= 75: return {'score': score, 'label': 'طمع شديد', 'emoji': '🟢', 'advice': '⚠️ كن حذراً، السوق قد يكون مبالغاً فيه'}
            elif score >= 60: return {'score': score, 'label': 'طمع', 'emoji': '🟢', 'advice': '✅ اتجاه صعودي، ابحث عن فرص'}
            elif score >= 40: return {'score': score, 'label': 'محايد', 'emoji': '🟡', 'advice': '⚖️ السوق متوازن'}
            elif score >= 25: return {'score': score, 'label': 'خوف', 'emoji': '🟠', 'advice': '🔍 ابحث عن فرص شراء'}
            else: return {'score': score, 'label': 'خوف شديد', 'emoji': '🔴', 'advice': '💰 فرص شراء ممتازة!'}
    except: pass
    return None

def fast_learning():
    settings = get_settings()
    learning_data = load_json(LEARNING_FILE, {'predictions': []})
    if not learning_data.get('predictions'): return
    now = datetime.now(timezone.utc)
    last_fast = settings.get('last_fast_learning')
    if last_fast:
        try:
            if (now - datetime.fromisoformat(last_fast)).total_seconds() < 3600: return
        except: pass
    recent = [p for p in learning_data['predictions'] if p.get('timestamp', '') >= (now - timedelta(hours=6)).strftime('%Y-%m-%d %H')]
    if not recent:
        settings['last_fast_learning'] = now.isoformat()
        save_json(SETTINGS_FILE, settings)
        return
    correct, wrong, mistakes = 0, 0, {'high_rsi': 0, 'low_volume': 0, 'weak_trend': 0, 'wrong='1h')
            if len(data) < 2: continue
            change = ((_macd': float0}
   (data['Close']. for pred in recent:
        try:
            data = yf.Ticker(pred['symbol']).history(period='iloc[-1]) - pred['price']) / pred['price']) * 1001d', interval='1h')
            if len(data) < 2: continue
            change = ((float(data['Close'].iloc[-1]) - pred['price
            if pred']) / pred['price']) * 100
            if pred['action'] ==['action'] == 'buy':
 'buy':
                if change >                if change > 0.5 0.5: correct += : correct += 1
                else1
                else:
                    wrong:
                    wrong += 1
 += 1
                    if pred.get('rsi                    if pred.get('rsi', 50', 50) > 40:) > 40: mistakes['high_r mistakes['high_rsi'] += 1
                   si'] += 1
                    if pred.get(' if pred.get('volume_ratio', volume_ratio', 1) < 1) < 1.2:1.2: mistakes['low_volume mistakes['low_volume'] += 1
                   '] += 1
                    if pred.get('adx', if pred.get('adx', 0)  0) < 25:< 25: mistakes['weak_t mistakes['weak_trend'] += 1
rend'] += 1
                    if pred.get                    if pred.get('macd',('macd', 0)  0) < 0: mistakes['wrong_mac< 0: mistakes['wrong_macd'] += 1
d'] += 1
            else:
            else:
                if change                 if change < -0.5< -0.5: correct += 1
: correct += 1
                else: wrong                else: wrong += 1
 += 1
        except: continue        except: continue
    total =
    total = correct + wrong
 correct + wrong
    if total >    if total > 0:
 0:
        settings['total        settings['total_predictions'] += total
        settings_predictions'] += total
        settings['correct_predictions']['correct_predictions'] += correct
        += correct
        settings[' settings['accuracy_score'] =accuracy_score'] = round(settings[' round(settings['correct_predictions'] /correct_predictions'] / settings['total_predictions'], settings['total_predictions 2)
        for k in'], 2)
        for k in mistakes: settings['mistake_patterns mistakes: settings['mistake_patterns'][k] +='][k] += mistakes[k]
 mistakes[k]
        rsi =        rsi = settings['rsi settings['rsi_threshold']
       _threshold']
        if mistakes['high if mistakes['high_rsi'] > max_rsi'] > max(mistakes.get(mistakes.get('low_volume', 0('low_volume', 0), mistakes.get('weak), mistakes.get('weak_trend', _trend', 0)) and r0)) and rsi > 2si > 25:
           5:
            settings['rsi settings['rsi_threshold'] = max_threshold'] = max(25(25, rsi -, rsi - 2)
 2)
            send_telegram            send_telegram(f"(f"🧠 تعلم سريع:🧠 تعلم سريع: {mistakes['high {mistakes['high_rsi']} أ_rsi']} أخطاء RSI. Rخطاء RSI. RSI: {rsi}SI: {rsi}→{settings['rsi_threshold→{settings['rsi_threshold']}. الدقة']}. الدقة: {settings['accuracy_score: {settings['accuracy_score']*100}%']*100}%")
        settings")
        settings['last['last_fast_learning'] =_fast_learning'] = now.iso now.isoformat()
       format()
        save_json(SETTINGS save_json(SETTINGS_FILE, settings)_FILE, settings)

def get_daily

def get_daily_news():
   _news():
    news_cache news_cache = load_json(NEWS = load_json(NEWS_FILE, {'last_FILE, {'last_update': None, 'news':_update': None, 'news': []})
    []})
    today = datetime.now(timezone.utc today = datetime.now(timezone.utc).strftime('%Y-%).strftime('%Y-%m-%d')m-%d')
    if news
    if news_cache.get('last_cache.get('last_update') == today: return_update') == today: return news_cache['news news_cache['news']
    items']
    items = []
    for sym in = []
    for sym in ['222 ['2222.SR',2.SR', '1120 '1120.SR', '201.SR', '2010.SR',0.SR', '7010 '7010.SR', '.SR', '2382380.SR']:0.SR']:
        try:
           
        try:
            for item in y for item in yf.Ticker(symf.Ticker(sym).news[:3]:
).news[:3]:
                t, p                t, p = item.get(' = item.get('title', ''), item.get('publishertitle', ''), item.get('publisher', '')
               ', '')
                if t and p if t and p: items.append({'symbol':: items.append({'symbol': sym, 'title sym, 'title': t, '': t, 'publisher': p, 'time':publisher': p, 'time': datetime.fromtimestamp(item datetime.fromtimestamp(item.get('providerPublish.get('providerPublishTime', 0)).strftimeTime', 0)).strftime('%H:%M')})('%H:%M')})
        except:
        except: continue
    save continue
    save_json(NEWS_FILE_json(NEWS_FILE, {'last_update': today, {'last_update': today, 'news': items[:, 'news': items[:15]})
   15]})
    return items[:15] return items[:15]

def send_daily

def send_daily_news_report_news_report():
    news():
    news = get_daily_news = get_daily_news()
    if()
    if not news: return
    time not news: return
    time_info = get_current_info = get_current_time()
   _time()
    tasi = get tasi = get_tasi_index()_tasi_index()
    msg =
    msg = f" f"📰 <b>📰 <b>تقرير الأخبار اليتقرير الأخبار اليومي - السوق السعوديومي - السوق السعودي</b>\n</b>\n📅 {time📅 {time_info['saudi_info['saudi']}\n\n']}\n\n"
    if tasi:"
    if tasi: msg += f" msg += f"📊 <b📊 <b>مؤشر>مؤشر تاسي ( تاسي (TASI):TASI):</b> {tasi['</b> {tasi['price']} ({tprice']} ({tasi['change']:+asi['change']:+.2f}%.2f}%)\n\n")\n\n"
    by_sym = {}
    by_sym = {}
    for item in news
    for item in news: by_sym.setdefault: by_sym.setdefault(item['symbol'],(item['symbol'], []).append(item)
    []).append(item)
    for sym, items for sym, items in by_sym.items in by_sym.items():
        msg():
        msg += f"📌 <b>{ += f"📌 <b>{STOCK_NAMES.getSTOCK_NAMES.get(sym, sym)} ({(sym, sym)} ({sym.replace('.SRsym.replace('.SR', '')}):', '')}):</b>\n"
</b>\n"
        for item in        for item in items[:2]: items[:2]: msg += f" msg += f"• {item['title• {item['title']}\n  ']}\n   📰 {item 📰 {item['publisher']} |['publisher']} | ⏰ {item ⏰ {item['time']}\['time']}\n\n"
   n\n"
    send_telegram(msg send_telegram(msg)

def calculate)

def calculate_obv(data):
    try_obv(data):
    try: return float((np: return float((np.sign(data['Close'].diff.sign(data['Close'].diff()) * data['Volume']).()) * data['Volume']).fillna(0).fillna(0).cumsum().iloc[-1])cumsum().iloc[-1]) > float((np > float((np.sign(data['Close.sign(data['Close'].diff()) * data['Volume'].diff()) * data['Volume']).fillna(0']).fillna(0).).cumsum().rollingcumsum().rolling(20).(20).mean().iloc[-mean().iloc[-1])
    except1])
    except: return False

: return False

def calculate_adx(data,def calculate_adx(data, period=14 period=14):
    try):
    try:
        h, l,:
        h, l, c = data[' c = data['High'], data['High'], data['Low'], data['Close']Low'], data['Close']
        pdm
        pdm, ndm =, ndm = h.diff(), l h.diff(), l.diff()
       .diff()
        pdm[pdm pdm[pdm < 0], < 0], ndm[ndm ndm[ndm > 0] > 0] = 0, = 0, 0
        tr = pd 0
        tr = pd.concat([h -.concat([h - l, (h l, (h - c.shift()).abs - c.shift()).abs(), (l -(), (l - c.shift()).abs c.shift()).abs()], axis=1).max()], axis=1).max(axis=1)(axis=1)
        atr = tr.rolling
        atr = tr.rolling(period).mean()
        pd(period).mean()
        pdi, ndi = i, ndi = 100 *100 * (pdm. (pdm.rolling(period).meanrolling(period).mean() / atr), 10() / atr), 100 * (nd0 * (ndm.rolling(periodm.rolling(period).mean() /).mean() / atr)
        atr)
        return float((1 return float((100 * ((00 * ((pdi -pdi - ndi).abs ndi).abs() / (pdi +() / (pdi + ndi))).rolling ndi))).rolling(period).mean().iloc[-1(period).mean().iloc[-1]) if not pd]) if not pdi.empty else 0
i.empty else 0
    except: return    except: return 0

def 0

def calculate_bollinger(data calculate_bollinger(data, period=20, std, period=20, std_dev=2):_dev=2):
    try:
    try:
        sma,
        sma, std = data[' std = data['Close'].rollingClose'].rolling(period).mean(), data(period).mean(), data['Close'].rolling['Close'].rolling(period).std()
       (period).std()
        upper, lower = upper, lower = sma + (std sma + (std * std_dev), sma * std_dev), sma - (std * - (std * std_dev)
 std_dev)
        current        current = float(data['Close'].iloc = float(data['Close'].iloc[-1])
[-1])
        u_val, l        u_val, l_val, s_val_val, s_val = float(upper.iloc = float(upper.iloc[-1]), float[-1]), float(lower.iloc[-1]), float(lower.iloc[-1]), float(sma.iloc[-(sma.iloc[-1])1])
        percent_b
        percent_b = (current = (current - l_val) - l_val) / ( / (u_val - lu_val - l_val) if (u_val -_val) if (u_val - l_val) != l_val) != 0 else  0 else 0.5
0.5
        signal = '        signal = 'مباع زائدمباع زائد (فرصة شراء)' (فرصة شراء)' if current <= l if current <= l_val * 1_val * 1.01 else.01 else 'مُشر 'مُشرى زائد (ى زائد (فرصة بيع)'فرصة بيع)' if current >= u if current >= u_val * 0_val * 0.99 else.99 else 'تحت المتوسط 'تحت المتوسط' if current < s_val else' if current < s_val else 'فوق المتوسط 'فوق المتوسط'
        return {'upper'
        return {'upper': round(u_val, ': round(u_val, 2), 'middle2), 'middle': round(s_val': round(s_val, 2),, 2), 'lower': round 'lower': round(l_val, (l_val, 2), 'percent_b': round2), 'percent_b': round(percent_b, (percent_b, 2), 'signal': signal2), 'signal': signal}
    except}
    except: return None

: return None

def detect_golden_deathdef detect_golden_death_cross(data):
    try_cross(data):
    try:
        if len(data):
        if len(data) < 20 < 200: return None
       0: return None
        ma50, ma50, ma200 ma200 = data['Close'].rolling = data['Close'].rolling(50).(50).mean(), data['mean(), data['Close'].rollingClose'].rolling(200(200).mean()
).mean()
        c50, c        c50, c200,200, p50, p50, p200 p200 = float(ma5 = float(ma50.iloc[-10.iloc[-1]), float]), float(ma20(ma200.iloc[-1]), float0.iloc[-1]), float(ma50(ma50.iloc[-2]), float.iloc[-2]), float(ma20(ma200.iloc[-20.iloc[-2])])
        if p50 
        if p50 < p200< p200 and c50 > and c50 > c200 c200: return {'type':: return {'type': 'golden', ' 'golden', 'signal': 'signal': '🌟 تقاط🌟 تقاطع ذهبي -ع ذهبي - إشارة شراء قوية جداً إشارة شراء قوية جداً'}
        elif p50'}
        elif p50 > p200 > p200 and c50  and c50 < c200< c200: return {'type': ': return {'type': 'death', 'signaldeath', 'signal': '💀 تق': '💀 تقاطع ميت -اطع ميت - إشارة بيع قوية'} إشارة بيع قوية'}
        elif c
        elif c50 > c50 > c200:200: return {'type': 'bull return {'type': 'bullish', 'signalish', 'signal': '': '📈 اتجاه صعودي📈 اتجاه صعودي (MA50 (MA50 فوق MA20 فوق MA200)'}
       0)'}
        else: return {' else: return {'type': 'type': 'bearish', 'bearish', 'signal': 'signal': '📉 اتجاه ه📉 اتجاه هبوطي (MAبوطي (MA50 تحت MA50 تحت MA200)'}
    except:200)'}
    except: return None

def return None

def detect_patterns(data):
 detect_patterns(data):
    patterns = []    patterns = []
    try:
    try:
        if len
        if len(data)(data) < 3: < 3: return patterns
        return patterns
        o, c, o, c, h, l = h, l = data['Open']. data['Open'].iloc[-1],iloc[-1], data['Close']. data['Close'].iloc[-1], data['High'].ilociloc[-1], data['High'].iloc[-1], data['Low[-1], data['Low'].iloc[-1'].iloc[-1]
        body]
        body = abs(c - = abs(c - o)
        o)
        if min(o, if min(o, c) - l c) - l > body *  > body * 2 and h -2 and h - max(o, c max(o, c) < body * 0.) < body * 0.5 and c > o:5 and c > o: patterns.append(" patterns.append("🔨 مطر🔨 مطرقة")
       قة")
        if c > o if c > o and data['Close and data['Close'].iloc[-2'].iloc[-2] < data['Open'].iloc] < data['Open'].iloc[-2] and[-2] and c > c > data['Open'].iloc[-2 data['Open'].iloc[-2] and o ] and o < data['Close< data['Close'].iloc[-2]:'].iloc[-2]: patterns.append(" patterns.append("📈 ابتلاعية📈 ابتلاعية")
        if body")
        if body < (h - < (h - l) * 0.1 l) * 0.1: patterns.append(": patterns.append("⚖️ د⚖️ دوجي")
   وجي")
    except: pass
 except: pass
    return patterns

    return patterns

def explain_recommendation(result):def explain_recommendation(result):
    score =
    score = result['score'] result['score']
    exp =
    exp = ["🌟  ["🌟 <b>صفقة<b>صفقة قوية جداً:</b قوية جداً:</b> إشارات متعددة> إشارات متعددة!" if score >= 6 else!" if score >= 6 else "✅ <b> "✅ <b>شراء قوي:شراء قوي:</b> معظم المؤ</b> معظم المؤشرات إيجابية."شرات إيجابية." if score >= 5 else if score >= 5 else "🟡 "🟡 <b>ش <b>شراء:</b>راء:</b> مؤشرات إيجابية مؤشرات إيجابية." if score >= 4." if score >= 4 else "👀 else "👀 <b>م <b>مراقبة:</b>راقبة:</b> يحتاج تأكيد." if score يحتاج تأكيد." if score >= 3 else >= 3 else "🔴 "🔴 <b>ت <b>تجنب:</b>جنب:</b> مؤشرات سلبية مؤشرات سلبية.", "\n.", "\n📝 <b>📝 <b>التفصيل:التفصيل:</b>"]
    for r in result['</b>"]
    for r in result['reasons']:
       reasons']:
        if 'RSI if 'RSI منخفض جداً' in r: exp.append(f منخفض جداً' in r: exp.append(f"• {r"• {r} → مباع} → مباع بشكل زائد") بشكل زائد")
        elif '
        elif 'RSRSI منخفض' inI منخفض' in r: exp.append r: exp.append(f"• {r(f"• {r} → اقتر} → اقتراب من الشراءاب من الشراء")
        elif 'ف")
        elif 'فوق المتوسط' in r:وق المتوسط' in r: exp.append(f" exp.append(f"• {r}• {r} → اتجاه صعودي → اتجاه صعودي")
        elif 'ت")
        elif 'تحت المتوسط' in r:حت المتوسط' in r: exp.append(f" exp.append(f"• {r}• {r} → اتجاه هبوط → اتجاه هبوطي")
       ي")
        elif 'MACD' in r: exp.append(f elif 'MACD' in r: exp.append(f"• {r} → زخم"• {r} → زخم صعودي")
        elif 'حجم صعودي")
        elif 'حجم' in r: exp' in r: exp.append(f"•.append(f"• {r} → {r} → اهتمام كبير")
        اهتمام كبير")
        elif 'ADX' elif 'ADX' in r: exp in r: exp.append(f"•.append(f"• {r} → {r} → اتجاه قوي")
        اتجاه قوي")
        elif 'OBV elif 'OBV' in r: exp.append(f' in r: exp.append(f"• {r"• {r} → تراكم} → تراكم مؤسساتي")
 مؤسساتي")
               else: exp.append else: exp.append(f"•(f"• {r}")
    {r}")
    return "\n". return "\n".join(exp)

defjoin(exp)

def learn_from_predictions(): learn_from_predictions():
    settings =
    settings = get_settings()
 get_settings()
    learning_data =    learning_data = load_json(LE load_json(LEARNING_FILE, {'ARNING_FILE, {'predictions': []})predictions': []})
    if not
    if not learning_data.get(' learning_data.get('predictions'): return
predictions'): return
    yesterday = (datetime.now(time    yesterday = (datetime.now(timezone.utc) -zone.utc) - timedelta(days=1 timedelta(days=1)).strftime('%Y)).strftime('%Y-%m-%d')-%m-%d')
    preds =
    preds = [p for p [p for p in learning_data[' in learning_data['predictions'] if p.get('predictions'] if p.get('date') == yesterday]
   date') == yesterday]
    if not preds: if not preds: return
    return
    correct, wrong = correct, wrong = 0,  0, 0
    for0
    for pred in preds: pred in preds:
        try:
           
        try:
            data = yf data = yf.Ticker(pred['.Ticker(pred['symbol']).history(periodsymbol']).history(period='2d',='2d', interval='1d interval='1d')
            if len')
            if len(data) < (data) < 2: continue
2: continue
            change = ((            change = ((float(data['Closefloat(data['Close'].iloc[-1'].iloc[-1]) - pred[']) - pred['price']) / predprice']) / pred['price']) * 10['price']) * 100
            if (pred0
            if (pred['action'] ==['action'] == 'buy' and 'buy' and change > 0 change > 0) or (pred) or (pred['action'] !=['action'] != 'buy' and 'buy' and change < 0): change < 0 correct += 1): correct += 1
            else: wrong
            else: wrong += 1
        except: continue += 1
        except: continue
    total =
    total = correct + wrong
 correct + wrong
    if total >    if total > 0:
 0:
        settings['total        settings['total_predictions'] += total
        settings_predictions'] += total
        settings['correct_predictions']['correct_predictions'] += correct
        settings += correct
        settings['accuracy_score']['accuracy_score'] = round(settings[' = round(settings['correct_predictions'] /correct_predictions'] / settings['total_predictions'], settings['total_predictions'], 2)
        rsi 2)
        rsi = settings['rs = settings['rsi_threshold']
i_threshold']
        if settings['        if settings['accuracy_score'] accuracy_score'] < 0.4< 0.45 and rsi > 5 and rsi > 25:
25:
            settings['rs            settings['rsi_threshold'] =i_threshold'] = max(25 max(25, rsi -, rsi - 3)
 3)
            send_telegram            send_telegram(f"(f"🧠 تحسين! الدقة: {settings🧠 تحسين! الدقة: {settings['accuracy_score']*10['accuracy_score']*100}%. R0}%. RSI: {rsi}SI: {rsi}→{settings['rsi_threshold']}→{settings['rsi_threshold']}")
        elif")
        elif settings['accuracy settings['accuracy_score'] > 0._score'] > 0.70 and rsi < 70 and rsi < 45:
            settings['rs45:
            settings['rsi_threshold'] =i_threshold'] = min(45 min(45, rsi +, rsi + 2)
 2)
                       send_telegram(f send_telegram(f"📈"📈 تحسين! الدقة تحسين! الدقة: {settings[': {settings['accuracy_score']*10accuracy_score']*100}%. R0}%. RSI: {rsSI: {rsi}→{i}→{settings['rsi_threshold']}settings['rsi_threshold']}")
        settings")
        settings['last['last_adjustment'] = yesterday_adjustment'] = yesterday
        save_json
        save_json(SETTINGS_FILE, settings(SETTINGS_FILE, settings)
        learning)
        learning_data['predictions']_data['predictions'] = [p for = [p for p in learning_data p in learning_data['predictions'] if['predictions'] if p.get('date p.get('date') >= (datetime') >= (datetime.now(time.now(timezone.utc) -zone.utc) - timedelta(days=7 timedelta(days=7)).strftime('%Y-%)).strftime('%Y-%m-%d')]m-%d')]
        save_json(LE
        save_json(LEARNING_FILE, learningARNING_FILE, learning_data)

def_data)

def get_alerts(): get_alerts(): return load_json(AL return load_json(ALERTS_FILE, {'ERTS_FILE, {'alerts': []})alerts': []})
def save_alerts(data
def save_alerts(data): save_json(AL): save_json(ALERTS_FILE, data)

def add_price_alert(symbol,ERTS_FILE, data)

def add_price_alert(symbol, target_price, alert_type=' target_price, alert_type='above'):
   above'):
    symbol = symbol.upper symbol = symbol.upper() + ('' if symbol.upper() + ('' if symbol.upper().endswith('.().endswith('.SR') else '.SR') else '.SR')
   SR')
    data = get_alert data = get_alerts()
    if 's()
    if 'alerts' not inalerts' not in data: data[' data: data['alerts'] = []
    foralerts'] = []
    for alert in data[' alert in data['alerts']:
       alerts']:
        if alert['symbol if alert['symbol'] == symbol and'] == symbol and alert['target'] == alert['target'] == target_price: return target_price: return False, f" False, f"⚠️ التن⚠️ التنبيه موجود بالفعل"
   بيه موجود بالفعل"
    data['alerts']. data['alerts'].append({'symbol': symbolappend({'symbol': symbol, 'target':, 'target': target_price, ' target_price, 'type': alert_typetype': alert_type, 'created, 'created': datetime.now(time': datetime.now(timezone.utc).strftimezone.utc).strftime('%Y-%m-%('%Y-%m-%d %H:%d %H:%M'), 'triggered':M'), 'triggered': False})
    save False})
    save_alerts(data)_alerts(data)
    return True, f"
    return True, f"✅ تم إضافة تنبيه: {ST✅ تم إضافة تنبيه: {STOCK_NAMES.get(symbolOCK_NAMES.get(symbol, symbol)} {', symbol)} {'فوق' ifفوق' if alert_type == 'above' else alert_type == 'above' else 'تحت'} 'تحت'} {target_price} ر {target_price} ر.س"

def.س"

def remove_price_alert(symbol remove_price_alert(symbol):
    symbol =):
    symbol = symbol.upper() + symbol.upper() + ('' if symbol ('' if symbol.upper().endswith.upper().endswith('.SR') else '.('.SR') else '.SR')
   SR')
    data = get_alert data = get_alerts()
   s()
    if 'alerts' not if 'alerts' not in data: return in data: return False, " False, "❌ لا توجد تن❌ لا توجد تنبيهات"
   بيهات"
    initial = len(data['alerts initial = len(data['alerts'])
    data['alerts'])
    data['alerts'] = [a for a'] = [a for a in data['alerts in data['alerts'] if a['symbol']'] if a['symbol'] != symbol]
    if != symbol]
    if len(data['alerts len(data['alerts']) == initial: return False']) == initial: return False, f", f"⚠️ لا⚠️ لا يوجد تنبيه ل يوجد تنبيه لـ {symbol}"ـ {symbol}"
    save_alert
    save_alerts(data)
   s(data)
    return True, f return True, f"✅ تم حذف"✅ تم حذف تنبيهات { تنبيهات {symbol}"

def checksymbol}"

def check_price_alerts():_price_alerts():
    data =
    data = get_alerts() get_alerts()
    if 'alerts'
    if 'alerts' not in data or not in data or not data['alerts not data['alerts']: return
    triggered =']: return
    triggered = []
    for []
    for alert in data[' alert in data['alerts']:
       alerts']:
        if alert.get(' if alert.get('triggered'): continuetriggered'): continue
        try:
        try:
            hist = yf.T
            hist = yf.Ticker(alert['symbolicker(alert['symbol']).history(period='2d')']).history(period='2d')
            if len
            if len(hist) < (hist) < 1: continue
1: continue
            current = float            current = float(hist['Close'].(hist['Close'].iloc[-1])iloc[-1])
            if (alert['
            if (alert['type'] == 'type'] == 'above' and currentabove' and current >= alert['target >= alert['target']) or (alert['type']) or (alert['type'] == 'below'] == 'below' and current <= alert' and current <= alert['target']):
               ['target']):
                alert['triggered alert['triggered'] = True
                triggered.append'] = True
                triggered.append(alert)
               (alert)
                send_telegram(f" send_telegram(f"🔔 🔔 <b>تنبيه<b>تنبيه سعر!</b>\ سعر!</b>\n\nn\n📌 {STOCK_NAMES.get(alert📌 {STOCK_NAMES.get(alert['symbol'], alert['symbol['symbol'], alert['symbol'])} ({alert'])} ({alert['symbol'].replace('.SR['symbol'].replace('.SR', '')})\', '')})\n💰 السعر الحاليn💰 السعر الحالي: {current:.: {current:.2f} ر2f} ر.س\n.س\n🎯 الهدف:🎯 الهدف: {alert['target {alert['target']:.2f']:.2f}} ر.س\n ر.س\n⏰ {⏰ {datetime.now(timezone.utcdatetime.now(timezone.utc).strftime('%H:%).strftime('%H:%M UTC')}")M UTC')}")
        except: continue

        except: continue
    if triggered:    if triggered: save_alerts(data save_alerts(data)

def get_portfolio)

def get_portfolio(): return load_json(PORT(): return load_json(PORTFOLIO_FILEFOLIO_FILE, {'positions': []}), {'positions': []})
def save_portfolio(data):
def save_portfolio(data): save_json(PORTFOLIO_FILE save_json(PORTFOLIO_FILE, data)

def, data)

def add_position(symbol, shares, price add_position(symbol, shares, price, action='buy, action='buy'):
    symbol = symbol.upper'):
    symbol = symbol.upper() + ('' if symbol() + ('' if symbol.upper().endswith.upper().endswith('.SR') else '.('.SR') else '.SR')
   SR')
    data = get_portfolio data = get_portfolio()
    if 'positions'()
    if 'positions' not in data: not in data: data['positions'] data['positions'] = []
    if action = []
    if action == 'buy': == 'buy':
        found = False

        found = False
        for pos in        for pos in data['positions']: data['positions']:
            if pos
            if pos['symbol'] ==['symbol'] == symbol:
                symbol:
                total = pos[' total = pos['shares'] + sharesshares'] + shares
               
                pos['shares'] = total
 pos['shares'] = total
                pos['avg                pos['avg_price'] = round(((_price'] = round(((pos['shares'] - sharespos['shares'] - shares) * pos[') * pos['avg_price'] + sharesavg_price'] + shares * price) / total * price) / total, 2), 2)
                pos['
                pos['last_update'] =last_update'] = datetime.now(timezone datetime.now(timezone.utc).strftime('%Y-%.utc).strftime('%Y-%m-%d')m-%d')
                found = True

                found = True
                break
        if not                break
        if not found:
            found:
            data['positions'].append data['positions'].append({'symbol': symbol({'symbol': symbol, 'shares':, 'shares': shares, 'avg_price shares, 'avg_price': round(price, 2': round(price, 2), 'buy_date), 'buy_date': datetime.now(timezone.utc': datetime.now(timezone.utc).strftime('%Y).strftime('%Y-%-%m-%d'),m-%d'), 'last_update': 'last_update': datetime.now(timezone datetime.now(timezone.utc).strftime('%.utc).strftime('%Y-%m-%d')Y-%m-%d')})
        save_portfolio(data)
       })
        save_portfolio(data)
        return True, f"✅ return True, f"✅ تم شراء {shares تم شراء {shares} سهم من {} سهم من {STOCK_NAMES.get(symbolSTOCK_NAMES.get(symbol, symbol)} بسعر, symbol)} بسعر {price} ر {price} ر.س"
.س"
    elif action ==    elif action == 'sell':
 'sell':
               for pos in data for pos in data['positions']:
['positions']:
            if pos['            if pos['symbol'] == symbolsymbol'] == symbol:
                if pos['shares:
                if pos['shares'] < shares: return'] < shares: return False, f" False, f"❌ لا تملك❌ لا تملك {shares} سهم، {shares} سهم، لديك {pos['shares لديك {pos['shares']} فقط"
               ']} فقط"
                profit = (price profit = (price - pos['avg_price']) - pos['avg_price']) * shares
                pos[' * shares
                pos['shares'] -= sharesshares'] -= shares
                if pos
                if pos['shares'] ==['shares'] == 0: data 0: data['positions'].remove['positions'].remove(pos)
               (pos)
                save_portfolio(data)
                save_portfolio(data)
                return True, f"✅ return True, f"✅ تم بيع {shares} تم بيع {shares} سهم من {STOCK_NAMES سهم من {STOCK_NAMES.get(symbol, symbol.get(symbol, symbol)}\n)}\n💵 الربح:💵 الربح: {profit:.2f} {profit:.2f} ر.س" ر.س"
        return False, f
        return False, f"❌ لا ت"❌ لا تملك {symbol}"ملك {symbol}"

def update_position

def update_position_price(symbol, new_price):_price(symbol, new_price):
    symbol =
    symbol = symbol.upper() + symbol.upper() + ('' if symbol ('' if symbol.upper().endswith.upper().endswith('.SR') else '.('.SR') else '.SR')
   SR')
    data = get_portfolio data = get_portfolio()
    if()
    if 'positions' not 'positions' not in data or not data['positions in data or not data['positions']: return False, "']: return False, "❌ المحفظة فار❌ المحفظة فارغة"
   غة"
    for pos in data for pos in data['positions']:
['positions']:
        if pos['        if pos['symbol'] == symbolsymbol'] == symbol:
            old:
            old = pos['avg = pos['avg_price']
           _price']
            pos['avg_price'] pos['avg_price'] = round(new_price, 2 = round(new_price, 2)
            pos[')
            pos['last_update'] =last_update'] = datetime.now(timezone datetime.now(timezone.utc).strftime('%.utc).strftime('%Y-%m-%Y-%m-%d')
           d')
            save_portfolio(data)
            save_portfolio(data)
            return True, f"✅ return True, f"✅ تم تحديث سعر {ST تم تحديث سعر {STOCK_NAMES.get(symbol, symbolOCK_NAMES.get(symbol, symbol)}\nمن)}\nمن: {old:.: {old:.2f} ر2f} ر.س\nإ.س\nإلى: {new_priceلى: {new_price:.2f}:.2f} ر.س" ر.س"
    return False
    return False, f", f"❌ لا تملك❌ لا تملك {symbol} في {symbol} في المحفظة" المحفظة"

def export_portfolio

def export_portfolio():
    data = get_portfolio():
    data = get_portfolio()
    if()
    if 'positions' not 'positions' not in data or not in data or not data data['positions']: return "['positions']: return "📊 <b📊 <b>المحفظة>المحفظة فارغة</b فارغة</b>\n\nلا>\n\nلا توجد صفقات للت توجد صفقات للتصدير."
   صدير."
    msg = f" msg = f"📊 📊 <b>تقرير<b>تقرير المحفظة الكامل المحفظة الكامل - السوق السعودي - السوق السعودي</b>\n</b>\n📅 {datetime📅 {datetime.now(timezone.utc.now(timezone.utc).strftime('%Y-%).strftime('%Y-%m-%d %m-%d %H:%M')H:%M')}\n\n━━━━━━━━}\n\n━━━━━━━━━━━━━━━━━━\n"━━━━━━━━━━\n"
    total_inv
    total_inv, total_cur, total, total_cur, total_prof = 0, _prof = 0, 0, 00, 0
    for i, pos
    for i, pos in enumerate(data['positions'], in enumerate(data['positions'], 1):
 1):
        try:
        try:
            hist = y            hist = yf.Ticker(posf.Ticker(pos['symbol']).history['symbol']).history(period='2d')(period='2d')
            if len
            if len(hist) < (hist) < 1: continue
1: continue
            cur_price =            cur_price = float(hist['Close float(hist['Close'].iloc[-1'].iloc[-1])
            inv])
            inv = pos['shares'] = pos['shares'] * pos['avg * pos['avg_price']
           _price']
            cur = pos['shares'] * cur = pos['shares'] * cur_price
            cur_price
            prof = cur - inv
            prof = cur - inv
            pct = (prof pct = (prof / inv) * 1 / inv) * 100 if inv > 000 if inv > 0 else 0
            else 0
            total_inv += inv
            total total_inv += inv
            total_cur += cur
_cur += cur
            total_prof +=            total_prof += prof
            name prof
            name = STOCK_NAMES.get = STOCK_NAMES.get(pos['symbol'], pos(pos['symbol'], pos['symbol'])
           ['symbol'])
            emoji = ' emoji = '🟢' if🟢' if prof >= 0 prof >= 0 else ' else '🔴'
           🔴'
            msg += f" msg += f"<b>#{i}.<b>#{i}. {name} ({pos {name} ({pos['symbol'].replace('.SR['symbol'].replace('.SR', '')})', '')})</b>\n•</b>\n• 📅 الش 📅 الشراء: {posراء: {pos['buy_date']}\['buy_date']}\n• 🔢n• 🔢 العدد: {pos العدد: {pos['shares']}\['shares']}\n• 💰n• 💰 الدخول: الدخول: {pos['avg {pos['avg_price']:.2f}_price']:.2f} ر.س\n ر.س\n• 📊 الحالي• 📊 الحالي: {cur_price:.: {cur_price:.2f} ر2f} ر.س\n•.س\n• 💵 القيمة: 💵 القيمة: {cur:.2f {cur:.2f} ر.س} ر.س\n• {emoji}\n• {emoji} الربح: { الربح: {prof:.2f}prof:.2f} ر.س ({ ر.س ({pct:+.2fpct:+.2f}%)\n━━━━━━━━}%)\n━━━━━━━━━━━━━━━━━━\n━━━━━━━━━━\n"
        except: continue
"
        except: continue
    pct_total = (total    pct_total = (total_prof / total_inv_prof / total_inv) * 10) * 100 if total_inv0 if total_inv > 0 else  > 0 else 0
    emoji = '0
    emoji = '🟢' if🟢' if total_prof >= 0 else total_prof >= 0 else '🔴 '🔴'
    msg += f'
    msg"\n📊 <b> += f"\n📊 <b>الملخص الكليالملخص الكلي:</b>\n:</b>\n💰 الاستثمار: {total💰 الاستثمار: {total_inv:.2f}_inv:.2f} ر.س\n ر.س\n💵 القيمة الحالية💵 القيمة الحالية: {total_cur: {total_cur:.2f}:.2f} ر.س\n ر.س\n{emoji} <b{emoji} <b>إجمالي الرب>إجمالي الربح/الخسارةح/الخسارة: {total_prof:.: {total_prof:.2f} ر2f} ر.س ({pct.س ({pct_total:+.2f}_total:+.2f}%)</b>\%)</b>\n\nn\n📈 <b>📈 <b>إحصائياتإحصائيات:</b>\n•:</b>\n• عدد الأسهم: {len عدد الأسهم: {len(data['positions'])(data['positions'])}\n• آخر}\n• آخر تحديث: {datetime تحديث: {datetime.now(timezone.utc.now(timezone.utc).strftime('%Y).strftime('%Y-%m-%d %-%m-%d %H:%M UTCH:%M UTC')}"
   ')}"
    return msg

def return msg

def get_portfolio_summary():
    get_portfolio_summary():
    data = get_portfolio data = get_portfolio()
    if 'positions'()
    if 'positions' not in data or not data not in data or not data['positions']: return['positions']: return "📊 "📊 <b>الم <b>المحفظة فارغةحفظة فارغة</b>\n\n</b>\n\nاستخدم: /استخدم: /buy 22buy 2222 122 10 0 35"
35"
    msg = "    msg = "📊 📊 <b>ملخص<b>ملخص المحفظة - المحفظة - السوق السعودي</b السوق السعودي</b>\n\n"
    total_inv,>\n\n"
    total_inv, total_cur, total total_cur, total_prof = 0_prof = 0, 0, , 0, 0
    for pos in data0
    for pos in data['positions']:
['positions']:
        try:
        try:
            hist = y            hist = yf.Ticker(posf.Ticker(pos['symbol']).history['symbol']).history(period='2d')(period='2d')
            if len(hist) < 1:
            if len(hist) < 1: continue
            cur_price = continue
            cur_price = float(hist['Close'].iloc[- float(hist['Close'].iloc[-1])
           1])
            inv = pos['shares'] inv = pos['shares'] * pos['avg * pos['avg_price']
           _price']
            cur = pos['shares cur = pos['shares'] * cur_price
           '] * cur_price
            prof = cur - inv
 prof = cur - inv
            pct = (prof            pct = (prof / inv) * 1 / inv) * 100 if inv > 000 if inv > 0 else 0
            else 0
            total_inv += inv total_inv += inv
            total_cur += cur

            total_cur += cur
            total_prof +=            total_prof += prof
            name = STOCK_NAMES prof
            name = STOCK_NAMES.get(pos['symbol'], pos.get(pos['symbol'], pos['symbol'])
           ['symbol'])
            emoji = ' emoji = '🟢' if🟢' if prof prof >= 0 else >= 0 else '🔴 '🔴'
            msg += f"📌 <b>{name} ({pos['symbol'].'
            msg += f"📌 <b>{name} ({pos['symbol'].replace('.SR',replace('.SR', '') '')})</b>\})</b>\n• العدد:n• العدد: {pos['shares {pos['shares']} | الشراء']} | الشراء: {pos['avg: {pos['avg_price']:.2f}_price']:.2f} | الحالي: { | الحالي: {curcur_price:.2f_price:.2f}\n• {}\n• {emoji} الربحemoji} الربح: {prof:.: {prof:.2f} ر2f} ر.س ({p.س ({pct:+ct:+.2f}%.2f}%)\n\n")\n\n"
        except: continue
        except: continue
    pct_total = (total
    pct_total = (total_prof / total_inv) *_prof / total_inv) * 100 100 if total_inv > if total_inv > 0 else 0
    0 else 0
    emoji = ' emoji = '🟢' if🟢' if total_prof >= 0 else total_prof >= 0 else '🔴 '🔴'
    msg += f'
    msg += f"━━━━━━━━━━━━━━━"━━━━━━━━━━━━━━━\n💰\n💰 الاستثمار: {total_inv الاستثمار: {total_inv:.2f}:.2f} ر.س | ر.س | 💵 القيمة: 💵 القيمة: {total_cur:. {total_cur:.2f} ر2f} ر.س\n{emoji.س\n{emoji} <b>} <b>إجمالي الربحإجمالي الربح: {total_prof: {total_prof:.2f}:.2f} ر.س ({ ر.س ({pct_total:+pct_total:+.2f}.2f}%)</b>"%)</b>"
    return msg
    return msg

def calculate_risk_reward(symbol, entry, sl

def calculate_risk_reward(symbol, entry, sl, tp):
, tp):
    try:
           try:
        hist = yf hist = yf.Ticker(symbol).history.Ticker(symbol).history(period='2d')(period='2d')
        current = float(hist['
        current = float(hist['Close'].iloc[-Close'].iloc[-1])
       1])
        risk, reward = risk, reward = abs(entry - sl abs(entry - sl), abs(tp -), abs(tp - entry)
        entry)
        rr = reward / rr = reward / risk if risk > 0 risk if risk > 0 else 0
        else 0
        delta = hist['Close'].diff delta = hist['Close'].diff()
        gain()
        gain = delta.where(delta = delta.where(delta > 0, > 0, 0).rolling 0).rolling(14).(14).mean()
       mean()
        loss = (-delta loss = (-delta.where(delta < 0.where(delta < 0, 0)).rolling, 0)).rolling(14).(14).mean()
       mean()
        rsi = float rsi = float(100(100 - (10 - (100 / (1 + (0 / (1 + (gain / loss).ilocgain / loss).[-1])))
iloc[-1])))
               msg = f" msg = f"📊 📊 <b>حاسبة<b>حاسبة المخاطرة - المخاطرة - السوق السعودي</b السوق السعودي</b>\n\n>\n\n📌 السهم📌 السهم: {STOCK: {STOCK_NAMES_NAMES.get(symbol, symbol.get(symbol, symbol)} ({symbol.replace('.SR',)} ({symbol.replace('.SR', '')})\n '')})\n💰 الحالي: {current:.2f}💰 الحالي: {current:.2f} ر.س | ر.س | 🎯 الدخ 🎯 الدخول: {entryول: {entry:.2f}:.2f} ر.س\n ر.س\n🛡️ وقف🛡️ وقف الخسارة: {sl الخسارة: {sl:.2f}:.2f} ر.س | ر.س | 🎯 الهدف 🎯 الهدف: {tp:.: {tp:.2f} ر2f} ر.س\n\n.س\n\n⚖️⚖️ <b>الم <b>المخاطرة/خاطرة/العائد:</b>العائد:</b> 1:{rr 1:{rr:.2f}\:.2f}\n💵 المخn💵 المخاطرة: {اطرة: {riskrisk:.2f}:.2f} ر.س | ر.س | 💰 العائد 💰 العائد: {reward:.: {reward:.2f} ر2f} ر.س\n\n.س\n\n"
        msg"
        msg += " += "🌟 صفقة ممتازة🌟 صفقة ممتازة!" if rr >= 3!" if rr >= 3 else "✅ صفقة else "✅ صفقة جيدة" if rr >= 2 جيدة" if rr >= 2 else " else "🟡 صفقة مقبولة🟡 صفقة مقبولة" if rr >= 1." if rr >= 1.5 else "5 else "🔴 صفقة ضعيفة🔴 صفقة ضعيفة"
        msg"
        msg += f"\n += f"\n📊 RSI📊 RSI: {rsi:.: {rsi:.1f}"
       1f}"
        return msg
    return msg
    except Exception as e: return except Exception as e: return f"❌ f"❌ خطأ: {str(e)} خطأ: {str(e)}"

def get"

def get_top_top_movers():
    movers_movers():
    movers = {'gainers = {'gainers': [], 'los': [], 'losers': [], 'ers': [], 'most_active': []}
   most_active': []}
    for sym in DEFAULT for sym in DEFAULT_STOCKS + ALL_STOCKS + ALL_SA_STOCKS[:_SA_STOCKS[:30]:
       30]:
        try:
            try:
            hist = yf hist = yf.Ticker(sym)..Ticker(sym).history(period='2d')history(period='2d')
            if len
            if len(hist) < (hist) < 2: continue
2: continue
            c, p            c, p = float(hist['Close = float(hist['Close'].iloc[-1'].iloc[-1]), float(hist[']), float(hist['Close'].iloc[-Close'].iloc[-2])
           2])
            change = ((c - p) change = ((c - p) / p) * / p) * 100 100
            vol_ratio
            vol_ratio = float(hist['Volume = float(hist['Volume'].iloc[-1'].iloc[-1]) / float(hist]) / float(hist['Volume'].rolling(20['Volume'].rolling(20).mean().iloc[-).mean().iloc[-1]) if float1]) if float(hist['Volume'].(hist['Volume'].rolling(20rolling(20).mean().iloc[-).mean().iloc[-1]) > 0 else1]) > 0 else 1
            1
            movers['gainers movers['gainers'].append({'symbol'].append({'symbol': sym, '': sym, 'name': STOCK_NAMESname': STOCK_NAMES.get(sym, sym.get(sym, sym), 'change': round(change), 'change': round(change, 2), 'price': round, 2), 'price': round(c, 2(c, 2), 'volume_ratio': round), 'volume_ratio': round(vol_ratio, (vol_ratio, 2)})
           2)})
            movers['losers movers['losers'].append({'symbol'].append({'symbol': sym, 'name':': sym, 'name': STOCK_NAMES.get(sym STOCK_NAMES.get(sym, sym), 'change, sym), 'change': round(change, 2),': round(change, 2), 'price': round(c 'price': round(c, 2),, 2), 'volume_ratio': 'volume_ratio': round(vol_ratio, 2 round(vol_ratio, 2)})
            movers['most)})
            movers['most_active'].append({'_active'].append({'symbol': sym, 'namesymbol': sym, 'name': STOCK_NAMES.get(sym': STOCK_NAMES.get(sym, sym), 'change, sym), 'change': round(change, 2),': round(change, 2), 'volume_ratio': round(vol 'volume_ratio': round(vol_ratio, 2_ratio, 2)})
        except: continue
)})
        except: continue
    movers['g    movers['gainers'].sort(key=lambda xainers'].sort(key=lambda x: x['change: x['change'], reverse=True)'], reverse=True)
    movers['
    movers['losers'].sortlosers'].sort(key=lambda x: x['(key=lambda x: x['change'])
    movers['change'])
    movers['most_active'].sortmost_active'].sort(key=lambda x:(key=lambda x: x x['volume_ratio'],['volume_ratio'], reverse=True)
 reverse=True)
    return movers

    return movers

def analyze_sectors():
def analyze_sectors():
    sectors = {'    sectors = {'22222222.SR': 'ال.SR': 'الطاقة', '112طاقة', '1120.SR':0.SR': 'البنوك 'البنوك', '2010.S', '2010.SR': 'الR': 'البتروكيمابتروكيماويات', '701ويات', '7010.SR':0.SR': 'الاتصالات', 'الاتصالات', '228 '2280.SR':0.SR': 'الزراعة 'الزراعة', '20', '2090.SR':90.SR': 'التجزئة', 'التجزئة', '238 '2380.SR':0.SR': 'التعدين 'التعدين', '400', '4001.SR':1.SR': 'العقارات 'العقارات', '1180', '1180.SR': 'ال.SR': 'البنوك', 'بنوك', '11501150.SR': 'ال.SR': 'البنوك'}
    resultsبنوك'}
    results = []
    = []
    for symbol, name in sectors for symbol, name in sectors.items():
       .items():
        try:
            try:
            data = yf.Ticker(symbol data = yf.Ticker(symbol).history(period='5d')).history(period='5d')
            if len(data)
            if len(data) >= 2: >= 2:
                c, p =
                c, float(data['Close p = float(data['Close'].iloc[-1'].iloc[-1]), float(data[']), float(data['Close'].iloc[-2])Close'].iloc[-2])
                change =
                change = ((c - p ((c - p) / p)) / p) * 1 * 100
                week_data =00
                week_data = yf.Ticker yf.Ticker(symbol).history(period(symbol).history(period='7d')='7d')
                week_change
                week_change = ((c - = ((c - float(week_data float(week_data['Close'].iloc['Close'].iloc[0])) / float[0])) / float(week_data['(week_data['Close'].iloc[0]))Close'].iloc[0])) * 10 * 100 if len(week_data0 if len(week_data) >= 2 else) >= 2 else change
                results.append({'symbol change
                results.append({'symbol': symbol, 'name':': symbol, 'name': name, 'change name, 'change': round(change, 2': round(change, 2), 'week_change': round(week_change, 2), 'price': round(c, 2)})
        except: continue
    results.sort(key=lambda x: x['change'], reverse=True)
    return results

), 'week_change': round(week_change, 2), 'price': round(c, 2)})
        except: continue
    results.sort(key=lambda x: x['change'], reverse=True)
    return results

def analyze_stock(symbol, settingsdef analyze_stock(symbol, settings):
    try):
    try:
        data:
        data = yf.T = yf.Ticker(symbol).historyicker(symbol).history(period='6mo(period='6mo', interval='1', interval='1d')d')
        if len
        if len(data) < (data) < 50: return50: return None
        price None
        price = float(data[' = float(data['CloseClose'].iloc[-1'].iloc[-1])
        prev])
        prev = float(data[' = float(data['Close'].iloc[-2Close'].iloc[-2])
        change =])
        change = ((price - prev ((price - prev)) / prev) * / prev) * 100
        sma = float(data['Close'].rolling(50). 100
        sma = float(data['Close'].rolling(50).mean().iloc[-1])mean().iloc[-1])
        delta =
        delta = data[' data['Close'].diff()
        gain = delta.where(delta > 0, 0).rollingClose'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).(14).mean()
       mean()
        loss = (-delta loss = (-delta.where(delta < .where(delta < 00, 0))., 0)).rolling(14rolling(14).mean()
        r).mean()
        rsi = float(si = float(100 -100 - (100 (100 / (1 + / (1 + (gain / loss (gain / loss).iloc[-1).iloc[-1])))
        mac])))
        macd = float(datad = float(data['Close'].ew['Close'].ewm(span=1m(span=12,2, adjust=False).mean adjust=False).mean().iloc[-1().iloc[-1] - data['Close'].ew] - data['Close'].ewm(span=2m(span=266, adjust=False)., adjust=False).mean().iloc[-mean().iloc[-1])1])
        vol =
        vol = float(data['Volume float(data['Volume'].iloc[-1'].iloc[-1])
        avg])
        avg_vol = float(data_vol = float(data['Volume'].rolling['Volume'].rolling(20).(20).mean().iloc[-mean().iloc[-1])
        vol_ratio1])
        vol_ratio = vol / avg_vol = vol / avg_vol if avg_vol > if avg_vol >  0 else 10 else 1
        adx
        adx = calculate_adx(data = calculate_adx(data)
        obv = calculate_ob)
        obv = calculate_obv(data)
       v(data)
        patterns = detect_patterns patterns = detect_patterns(data)
        tr(data)
        tr = pd.concat([ = pd.concat([data['High'] - datadata['High'] - data['Low'], (['Low'], (data['High']data['High'] - data['Close - data['Close'].shift(1'].shift(1)).abs(), (data['Low)).abs(), (data['Low'] - data['Close'].shift'] - data['Close'].shift(1)).abs()],(1)).abs()], axis=1). axis=1).max(axis=1)max(axis=1)
        atr =
        atr = tr.rolling( tr.rolling(14).mean().14).mean().iloc[-1]
       iloc[-1]
        sl = round(price sl = round(price - (atr * 1 - (atr * 1.5), .5), 2)
       2)
        t1 = round(price + (atr * 2), 2)
        t2 = t1 = round(price + (atr * 2), 2)
        t2 = round(price + (atr * round(price + (atr * 3), 2)
        risk_amt = settings['capital'] 3), 2)
        risk_amt = settings['capital'] * settings['risk * settings['risk_percent'] / 100_percent'] / 100
        pos_size
        pos_size = int(risk_amt / = int(risk_amt / (price - sl (price - sl)) if price > sl and sl)) if price > sl and sl > 0 else > 0 else 0
        0
        score, reasons = score, reasons = 0, [] 0, []
        rsi
        rsi_th = settings.get_th = settings.get('rsi_threshold', ('rsi_threshold', 35)
35)
        if rsi        if rsi < rsi_th < rsi_th: score += : score += 22; reasons.append(f; reasons.append(f""📉 RSI📉 RSI منخفض جداً ({rsi:. منخفض جداً ({rsi:.1f})")1f})")
        elif rsi
        elif r < rsi_thsi < rsi_th + 10 + 10: score += 1; reasons.append(f: score += 1; reasons.append(f"📉 R"📉 RSI منخفض ({rsi:.SI منخفض ({rsi:.1f})")1f})")
        if price
        if price > sma > sma: score += : score += 1; reasons.append("1; reasons.append("📈 السعر فوق📈 السعر فوق المتوسط")
        المتوسط")
        else: reasons.append(" else: reasons.append("📉 السعر تحت المتوسط")
        if macd > 0: score📉 السعر تحت += 1; المتوسط")
        if macd > 0: score += 1; reasons.append("✅ reasons.append("✅ MACD إيجابي MACD إيجابي")
        if")
        if vol_ratio > 1.5 vol_ratio > 1.5: score += : score += 1; reasons.append(f"1; reasons.append(f"💪 حجم عالي ({vol_ratio:.💪 حجم عالي ({vol_ratio:.1f}x1f}x)")
        if adx >)")
        if adx > 25: 25: score += 1 score += 1; reasons.append(f; reasons.append(f"💪 AD"💪 ADX قوي ({adx:.X قوي ({adx:.1f})")1f})")
        if obv: score
        if obv += 1; reasons.append("🏦 تراكم OBV")
        if patterns: score += len(patterns); reasons.extend(patterns)
        bb = calculate_boll: score += 1;inger(data)
        reasons.append("🏦 تراكم OBV")
        if patterns: score += len(patterns); reasons.extend(patterns)
        bb = calculate_bollinger(data)
        if bb and (' if bb and ('مباع زائدمباع زائد' in bb['signal'] or' in bb['signal'] or 'فرصة شراء' in 'فرصة شراء' in bb['signal']): bb['signal']):
            score +=
            score += 1; reasons 1; reasons.append(f".append(f"📊 {bb📊 {bb['signal']}")['signal']}")
        cross =
        cross = detect_golden_death detect_golden_death_cross(data)
       _cross(data)
        if cross:
 if cross:
            if cross['            if cross['type'] == 'type'] == 'golden': scoregolden': score += 2; += 2; reasons.append(cross reasons.append(cross['signal'])
           ['signal'])
            elif cross['type'] elif cross['type'] == 'death': score == 'death': score -= 2; -= 2; reasons.append(cross[' reasons.append(cross['signal'])
           signal'])
            else: reasons.append(cross[' else: reasons.appendsignal'])
        rec, conf = ("🌟 صفقة قوية جداً", "عالية جداً") if score >= 6 else ("✅ شراء قوي", "ع(cross['signal'])
        rec, conf = ("🌟 صفقة قوية جداً", "عالية جداً") if score >= 6 else ("✅ شراء قوي", "عالية") if scoreالية") if score >= >= 5 else (" 5 else ("🟡 شراء", "متوسطة") if score >= 4 else ("👀 مراقبة", "منخفضة") if score >= 3 else ("🔴 تجنب", "ضعيفة")
       🟡 شراء", "متوسطة") if score >= 4 else ("👀 مراقبة", "منخفضة") if score >= 3 else ("🔴 تجنب", "ضعيفة")
        rr = round((t rr = round((t1 - price)1 - price) / (price / (price - sl), 2) if - sl), 2) if sl > 0 sl > 0 else 0
 else 0
               return {'symbol': symbol, return {'symbol': symbol, 'price': price 'price': price, 'change':, 'change': round(change, 2), round(change, 2), 'rsi': 'rsi': round(rsi, round(rsi, 1), ' 1), 'macd': roundmacd': round(macd, 2),(macd, 2), 'adx': round 'adx': round(adx, (adx, 1), 'volume1), 'volume_ratio': round(vol_ratio, _ratio': round(vol_ratio, 2), 'score2), 'score': score, 'recommend': score, 'recommendation': rec, 'confidence':ation': rec, 'confidence': conf, 'reason conf, 'reasons': reasons, 'stop_losss': reasons, 'stop_loss': sl, 'target1': sl, 'target1': t1,': t1, 'target2': t2 'target2': t2, 'pos_size':, 'pos_size': pos_size, ' pos_size, 'total_inv': roundtotal_inv': round(pos_size * price(pos_size * price, 2),, 2), 'risk_amt': 'risk_amt': round(risk_amt round(risk_amt, 2), ', 2), 'risk_reward': rrrisk_reward': rr, 'timestamp':, 'timestamp': datetime.now(timezone datetime.now(timezone.utc).strftime('%Y-%.utc).strftime('%Y-%m-%d %m-%d %H'), 'bollinger': bbH'), 'bollinger': bb, 'cross':, 'cross': cross}
    cross}
    except Exception as e:
 except Exception as e:
        print(f"خط        print(f"خطأ في {symbolأ في {symbol}: {e}")}: {e}")
        return None

def
        return None

def find_affordable_stocks find_affordable_stocks(settings, max_results=10(settings, max_results=10):
    capital):
    capital = settings['capital = settings['capital']
    risk_amt = capital * settings['risk']
    risk_amt = capital * settings['risk_percent'] / _percent'] / 100
    affordable = []
    for sym in DEFAULT_STOCKS + ALL_SA_STOCKS[:100
    affordable = []
    for sym in DEFAULT_STOCKS + ALL_SA_STOCKS[:30]:
30]:
        try:
            data = yf.Ticker(sym).history(period='5d', interval='1d')
            if        try:
            data = yf.Ticker(sym).history(period='5d', interval='1d')
            if len(data)  len(data) < 3: continue
            price = float(data['Close< 3: continue
            price = float(data['Close'].iloc[-1'].iloc[-1])
            pos])
            pos = = min(int(capital min(int(capital / price), int / price), int(risk_amt / (price *(risk_amt / (price * 0.0 0.02)))
           2)))
            if pos >=  if pos >= 10:
                delta = data['Close'].10:
                delta = data['Close'].diff()
               diff()
                gain = delta.where gain = delta.where(delta > 0(delta > 0, 0).rolling(14).mean()
                loss = (-delta, 0).rolling(14).mean()
                loss = (-delta.where(delta < .where(delta < 0, 00, 0)).rolling(14).mean()
                rsi = float(100 - (100 / (1 + (gain / loss).)).rolling(14).mean()
                rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1])))iloc[-1]))) if len(gain) > 0 else 50
                affordable.append({'symbol': sym, 'name': STOCK if len(gain) > 0 else 50
                affordable.append({'symbol': sym, 'name': STOCK_NAMES.get(sym,_NAMES.get(sym, sym), 'price sym), 'price': price, 'change':': price, 'change': round(((price - float(data round(((price -['Close'].iloc float(data['Close'].iloc[-2])) / float[-2])) / float(data['Close'].(data['Close'].iloc[-2]))iloc[-2])) * 10 * 100, 20, 2),), 'rsi': 'rsi': round(rsi, round(rsi, 1), 'position_size': pos, 'total_investment': round(pos * price, 2)})
        except: continue
    affordable.sort 1), 'position_size': pos, 'total_investment': round(pos * price, 2)})
        except: continue
    affordable.sort(key=lambda x: x['(key=lambda x: x['price'])
   price'])
    return affordable[:max return affordable[:max_results]

def_results]

def generate_weekly_report generate_weekly_report():
    settings =():
    settings get_settings()
 = get_settings()
    learning_data = load_json(LEARNING_FILE, {'predictions': []})    learning_data = load_json(LEARNING_FILE, {'predictions': []})
    week_
    week_ago = (datetime.now(timeago = (datetime.now(timezone.utc) -zone.utc) - timedelta(days=7 timedelta(days=7)).strftime('%Y-%)).strftime('%Y-%m-%d')m-%d')
    week_predictions
    week_predictions = [p for p = [p for p in learning_data.get in learning_data.get('predictions', []) if p.get('('predictions', []) if p.get('date', '') >= weekdate', '') >=_ago]
    sectors = analyze_sectors()
 week_ago]
    sectors = analyze_sectors()
    movers = get    movers = get_top_movers()_top_movers()
    tasi
    tasi = get_tasi = get_tasi_index()
   _index()
    msg = f" msg = f"📊 📊 <b>التقرير الأسبوعي -<b>التقرير الأسبوعي - السوق السعودي</b السوق السعودي</b>\n>\n📅 الأسبوع📅 الأسبوع المنتهي: {datetime المنتهي: {.now(timezone.utcdatetime.now(timezone.utc).strftime('%Y-%).strftime('%Y-%m-%d')m-%d')}\n\n━━━━━━━━}\n\n━━━━━━━━━━━━━━━\━━━━━━━\n🧠n🧠 <b>أ <b>أداء البوت:داء البوت:</b>\n•</b>\n• الدقة العامة: الدقة العامة: {settings['accuracy {settings['accuracy_score']*100}%_score']*100}%\n• توقع\n• توقعات هذا الأسبات هذا الأسبوع: {lenوع: {len(week_predictions)}\(week_predictions)}\n• إجمالي التn• إجمالي التوقعات: {وقعات: {settingssettings['total_predictions']}\n• الت['total_predictions']}\n• التوقعات الصحيحة: {settings['correctوقعات الصحيحة: {settings['correct_predictions']}\n\n_predictions']}\n\n"
    if tasi:"
    if msg += f" tasi: msg += f"📈 📈 <b>مؤشر تاسي (TASI):<b>مؤشر تاسي (TASI):</b> {t</b> {tasi['asi['price']} ({tprice']} ({tasi['changeasi['change']:+.2f}%)\n\n"']:+.2f}%)\n\n"
    if sectors:

    if sectors:
        msg += f        msg += f"🏢"🏢 <b>أ <b>أفضل 3 قطفضل 3 قطاعات:</b>\n"اعات:</b>\n"
        for s in sectors
        for s in sectors[:3]: msg[:3]: msg += f"{'🟢' if s['change'] > 0 else '🔴'} += f"{'🟢' if s['change'] > 0 else '🔴'} {s['name']}: {s['change']:+.2f}% {s['name']}: {s['change']:+.2f}%\n"
        msg += f"\\n"
n🔴        <b>أسوأ 3 قطاعات:</b>\n"
        for s in sectors[-3:]: msg += f"{' msg += f"\n🔴 <b>أسوأ 3 قطاعات:</b>\n"
        for s in sectors[-3:]:🟢' if msg += f" s['change']{'🟢' if > s['change'] > 0 else ' 0 else '🔴'} {🔴'} {s['name']s['name']}: {s['change}: {s['change']:+.2f}%']:+.2f}%\n\n"\n\n"
    if movers
    if movers['g['gainers'][:3]:ainers'][:3]:
        msg += f
        msg += f"🚀"🚀 <b>أ <b>أفضل 3 أسفضل 3 أسهم رابحةهم رابحة:</b>\n:</b>\n"
       "
        for m in movers for m in movers['gainers']['gainers'][:3]: msg += f"[:3]: msg += f"🟢 {🟢 {m['m['name']}: {name']}: {m['m['change']:+.2f}%change']:+.2f}%\n"
    if movers['los\n"
    if movers['losers'][:3]:ers'][:3]:
        msg +=
        msg += f f"\n"\n📉 <b>📉 <b>أسوأ 3 أسأسوأ 3هم خاسرة أسهم خاسرة:</b>\n:</b>\n"
       "
        for m in movers for m in movers['losers['losers'][:3]:'][:3]: msg += f" msg += f"🔴 {m🔴 {m['name']}:['name']}: {m['change'] {m['change']:+.2f:+.2f}%\n"
   }%\n"
    msg += f"\n━━━
