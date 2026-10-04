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
DEFAULT_STOCKS = [
    '2222.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR',
    '2030.SR', '1150.SR', '2380.SR', '2280.SR', '2090.SR'
]

ALL_SA_STOCKS = [
    '2222.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR',
    '2030.SR', '1150.SR', '2380.SR', '2280.SR', '2090.SR',
    '1211.SR', '2060.SR', '4001.SR', '4030.SR', '6010.SR',
    '8010.SR', '1010.SR', '1020.SR', '1030.SR', '1050.SR',
    '1060.SR', '1140.SR', '1201.SR', '1210.SR', '2001.SR',
    '2020.SR', '2040.SR', '2050.SR', '2060.SR', '2070.SR',
    '2080.SR', '2100.SR', '2110.SR', '2120.SR', '2130.SR',
    '2140.SR', '2150.SR', '2160.SR', '2170.SR', '2180.SR',
    '2190.SR', '2200.SR', '2210.SR', '2220.SR', '2230.SR',
    '2240.SR', '2250.SR', '2260.SR', '2270.SR', '2290.SR',
    '2300.SR', '2310.SR', '2320.SR', '2330.SR', '2340.SR',
    '2350.SR', '2360.SR', '2370.SR', '2390.SR', '4002.SR',
    '4003.SR', '4004.SR', '4005.SR', '4006.SR', '4007.SR',
    '4008.SR', '4009.SR', '4010.SR', '4011.SR', '4012.SR',
    '4013.SR', '4014.SR', '4015.SR', '4016.SR', '4017.SR',
    '4018.SR', '4019.SR', '4020.SR', '4031.SR', '4040.SR',
    '4050.SR', '4060.SR', '4061.SR', '4062.SR', '4063.SR',
    '6020.SR', '6030.SR', '6040.SR', '6050.SR', '6060.SR',
    '6070.SR', '6080.SR', '7020.SR', '7030.SR', '7040.SR',
    '7050.SR', '7060.SR', '7070.SR', '7080.SR', '8020.SR',
    '8030.SR', '8040.SR', '8050.SR', '8060.SR', '8070.SR',
    '8080.SR', '^TASI.SR'
]

STOCK_NAMES = {
    '2222.SR': 'أرامكو', '1120.SR': 'الراجحي', '2010.SR': 'سابك',
    '1180.SR': 'الأهلي', '7010.SR': 'STC', '2030.SR': 'سابك للمغذيات',
    '1150.SR': 'الإنماء', '2380.SR': 'معادن', '2280.SR': 'المراعي',
    '2090.SR': 'جرير', '1211.SR': 'معادن', '2060.SR': 'كيان السعودية',
    '4001.SR': 'دار الأركان', '4030.SR': 'ريت الراجحي', '6010.SR': 'Bupa العربية',
    '8010.SR': 'مصرف الإنماء', '1010.SR': 'الرياض للتعمير',
    '1020.SR': 'أسمنت الشرقية', '1030.SR': 'أسمنت الجنوبية',
    '1050.SR': 'أسمنت المدينة', '1060.SR': 'أسمنت القصيم',
    '1140.SR': 'البنك الفرنسي', '1201.SR': 'تكامل', '1210.SR': 'سابكو',
    '2001.SR': 'شمس', '2020.SR': 'سابك للمعادن', '2040.SR': 'سبكيم',
    '2050.SR': 'الصحراء', '2070.SR': 'التصنيع', '2080.SR': 'العجين',
    '2100.SR': 'الزامل', '2110.SR': 'ساكو', '2120.SR': 'المراعي',
    '2130.SR': 'هرفي', '2140.SR': 'نادك', '2150.SR': 'البابطين',
    '2160.SR': 'التصنيع', '2170.SR': 'الصرايعي', '2180.SR': 'غازكو',
    '2190.SR': 'أمنيات', '2200.SR': 'معادن ألمنيوم', '2210.SR': 'أمنيات',
    '2220.SR': 'أمنيات', '2230.SR': 'أمنيات', '2240.SR': 'ملاث',
    '2250.SR': 'التعاونية', '2260.SR': 'بوبا العربية', '2270.SR': 'مدجلف',
    '2290.SR': 'اتحاد الخليج', '2300.SR': 'الأهلي تكافل',
    '2310.SR': 'الراجحي تكافل', '2320.SR': 'ولاء', '2330.SR': 'سلامة',
    '2340.SR': 'اتحاد اتصالات', '2350.SR': 'زين', '2360.SR': 'أثير',
    '2370.SR': 'الحلول', '2390.SR': 'أثير', '4002.SR': 'الأحساء',
    '4003.SR': 'جبل عمر', '4004.SR': 'مكة للإنشاء',
    '4005.SR': 'إعمار المدينة', '4006.SR': 'دار الأركان',
    '4007.SR': 'جبل عمر', '4008.SR': 'عسير', '4009.SR': 'الأندلس',
    '4010.SR': 'طيبة', '4011.SR': 'مكة للإنشاء', '4012.SR': 'الأحساء',
    '4013.SR': 'جبل عمر', '4014.SR': 'إعمار المدينة',
    '4015.SR': 'دار الأركان', '4016.SR': 'طيبة', '4017.SR': 'عسير',
    '4018.SR': 'الأندلس', '4019.SR': 'مكة للإنشاء', '4020.SR': 'جبل عمر',
    '4031.SR': 'ريت الراجحي', '4040.SR': 'جدوى ريت',
    '4050.SR': 'الإنماء ريت', '4060.SR': 'الرياض ريت',
    '4061.SR': 'الأهلي ريت', '4062.SR': 'البلاد ريت',
    '4063.SR': 'الإنماء ريت', '6020.SR': 'بوبا العربية',
    '6030.SR': 'التعاونية', '6040.SR': 'مدجلف', '6050.SR': 'اتحاد الخليج',
    '6060.SR': 'ملاث', '6070.SR': 'سلامة', '6080.SR': 'ولاء',
    '7020.SR': 'ساكو', '7030.SR': 'هرفي', '7040.SR': 'نادك',
    '7050.SR': 'البابطين', '7060.SR': 'الصرايعي', '7070.SR': 'التصنيع',
    '7080.SR': 'غازكو', '8020.SR': 'أمنيات', '8030.SR': 'أمنيات',
    '8040.SR': 'أمنيات', '8050.SR': 'أمنيات', '8060.SR': 'ملاث',
    '8070.SR': 'التعاونية', '8080.SR': 'بوبا العربية',
    '^TASI.SR': 'مؤشر تاسي'
}

PROCESSED_FILE = 'processed.json'
LEARNING_FILE = 'learning_data.json'
SETTINGS_FILE = 'bot_settings.json'
NEWS_FILE = 'news_cache.json'
WATCHLIST_FILE = 'watchlist.json'
ALERTS_FILE = 'price_alerts.json'
PORTFOLIO_FILE = 'portfolio.json'

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
    symbol = symbol.upper()
    if not symbol.endswith('.SR'): symbol = symbol + '.SR'
    if symbol not in ALL_SA_STOCKS: return False, f"❌ {symbol} غير موجود"
    data = load_json(WATCHLIST_FILE, {'stocks': DEFAULT_STOCKS.copy()})
    if 'stocks' not in data: data['stocks'] = DEFAULT_STOCKS.copy()
    if symbol not in data['stocks']:
        data['stocks'].append(symbol)
        save_json(WATCHLIST_FILE, data)
        return True, f"✅ تمت إضافة {STOCK_NAMES.get(symbol, symbol)} ({symbol.replace('.SR', '')})"
    return False, f"⚠️ {symbol} موجود بالفعل"

def remove_from_watchlist(symbol):
    symbol = symbol.upper()
    if not symbol.endswith('.SR'): symbol = symbol + '.SR'
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
        if day in [4, 5]: return {'status': 'مغلق', 'emoji': '', 'reason': 'عطلة نهاية الأسبوع', 'next_open': 'الأحد 10:00 صباحاً', 'day': days_ar[day]}
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
            if c < 15: return {'value': round(c, 2), 'level': 'منخفض', 'emoji': ''}
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
            if score >= 75: return {'score': score, 'label': 'طمع شديد', 'emoji': '', 'advice': '⚠️ كن حذراً، السوق قد يكون مبالغاً فيه'}
            elif score >= 60: return {'score': score, 'label': 'طمع', 'emoji': '🟢', 'advice': '✅ اتجاه صعودي، ابحث عن فرص'}
            elif score >= 40: return {'score': score, 'label': 'محايد', 'emoji': '', 'advice': '⚖️ السوق متوازن'}
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
    correct, wrong, mistakes = 0, 0, {'high_rsi': 0, 'low_volume': 0, 'weak_trend': 0, 'wrong_macd': 0}
    for pred in recent:
        try:
            data = yf.Ticker(pred['symbol']).history(period='1d', interval='1h')
            if len(data) < 2: continue
            change = ((float(data['Close'].iloc[-1]) - pred['price']) / pred['price']) * 100
            if pred['action'] == 'buy':
                if change > 0.5: correct += 1
                else:
                    wrong += 1
                    if pred.get('rsi', 50) > 40: mistakes['high_rsi'] += 1
                    if pred.get('volume_ratio', 1) < 1.2: mistakes['low_volume'] += 1
                    if pred.get('adx', 0) < 25: mistakes['weak_trend'] += 1
                    if pred.get('macd', 0) < 0: mistakes['wrong_macd'] += 1
            else:
                if change < -0.5: correct += 1
                else: wrong += 1
        except: continue
    total = correct + wrong
    if total > 0:
        settings['total_predictions'] += total
        settings['correct_predictions'] += correct
        settings['accuracy_score'] = round(settings['correct_predictions'] / settings['total_predictions'], 2)
        for k in mistakes: settings['mistake_patterns'][k] += mistakes[k]
        rsi = settings['rsi_threshold']
        if mistakes['high_rsi'] > max(mistakes.get('low_volume', 0), mistakes.get('weak_trend', 0)) and rsi > 25:
            settings['rsi_threshold'] = max(25, rsi - 2)
            send_telegram(f"🧠 تعلم سريع: {mistakes['high_rsi']} أخطاء RSI. RSI: {rsi}→{settings['rsi_threshold']}. الدقة: {settings['accuracy_score']*100}%")
        settings['last_fast_learning'] = now.isoformat()
        save_json(SETTINGS_FILE, settings)

def get_daily_news():
    news_cache = load_json(NEWS_FILE, {'last_update': None, 'news': []})
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if news_cache.get('last_update') == today: return news_cache['news']
    items = []
    for sym in ['2222.SR', '1120.SR', '2010.SR', '7010.SR', '2380.SR']:
        try:
            for item in yf.Ticker(sym).news[:3]:
                t, p = item.get('title', ''), item.get('publisher', '')
                if t and p: items.append({'symbol': sym, 'title': t, 'publisher': p, 'time': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%H:%M')})
        except: continue
    save_json(NEWS_FILE, {'last_update': today, 'news': items[:15]})
    return items[:15]

def send_daily_news_report():
    news = get_daily_news()
    if not news: return
    time_info = get_current_time()
    tasi = get_tasi_index()
    msg = f" <b>تقرير الأخبار اليومي - السوق السعودي</b>\n📅 {time_info['saudi']}\n\n"
    if tasi: msg += f"📊 <b>مؤشر تاسي (TASI):</b> {tasi['price']} ({tasi['change']:+.2f}%)\n\n"
    by_sym = {}
    for item in news: by_sym.setdefault(item['symbol'], []).append(item)
    for sym, items in by_sym.items():
        msg += f"📌 <b>{STOCK_NAMES.get(sym, sym)} ({sym.replace('.SR', '')}):</b>\n"
        for item in items[:2]: msg += f"• {item['title']}\n   📰 {item['publisher']} | ⏰ {item['time']}\n\n"
    send_telegram(msg)

def calculate_obv(data):
    try: return float((np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum().iloc[-1]) > float((np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum().rolling(20).mean().iloc[-1])
    except: return False

def calculate_adx(data, period=14):
    try:
        h, l, c = data['High'], data['Low'], data['Close']
        pdm, ndm = h.diff(), l.diff()
        pdm[pdm < 0], ndm[ndm > 0] = 0, 0
        tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        pdi, ndi = 100 * (pdm.rolling(period).mean() / atr), 100 * (ndm.rolling(period).mean() / atr)
        return float((100 * ((pdi - ndi).abs() / (pdi + ndi))).rolling(period).mean().iloc[-1]) if not pdi.empty else 0
    except: return 0

def calculate_bollinger(data, period=20, std_dev=2):
    try:
        sma, std = data['Close'].rolling(period).mean(), data['Close'].rolling(period).std()
        upper, lower = sma + (std * std_dev), sma - (std * std_dev)
        current = float(data['Close'].iloc[-1])
        u_val, l_val, s_val = float(upper.iloc[-1]), float(lower.iloc[-1]), float(sma.iloc[-1])
        percent_b = (current - l_val) / (u_val - l_val) if (u_val - l_val) != 0 else 0.5
        signal = 'مباع زائد (فرصة شراء)' if current <= l_val * 1.01 else 'مُشرى زائد (فرصة بيع)' if current >= u_val * 0.99 else 'تحت المتوسط' if current < s_val else 'فوق المتوسط'
        return {'upper': round(u_val, 2), 'middle': round(s_val, 2), 'lower': round(l_val, 2), 'percent_b': round(percent_b, 2), 'signal': signal}
    except: return None

def detect_golden_death_cross(data):
    try:
        if len(data) < 200: return None
        ma50, ma200 = data['Close'].rolling(50).mean(), data['Close'].rolling(200).mean()
        c50, c200, p50, p200 = float(ma50.iloc[-1]), float(ma200.iloc[-1]), float(ma50.iloc[-2]), float(ma200.iloc[-2])
        if p50 < p200 and c50 > c200: return {'type': 'golden', 'signal': '🌟 تقاطع ذهبي - إشارة شراء قوية جداً'}
        elif p50 > p200 and c50 < c200: return {'type': 'death', 'signal': '💀 تقاطع ميت - إشارة بيع قوية'}
        elif c50 > c200: return {'type': 'bullish', 'signal': '📈 اتجاه صعودي (MA50 فوق MA200)'}
        else: return {'type': 'bearish', 'signal': '📉 اتجاه هبوطي (MA50 تحت MA200)'}
    except: return None

def detect_patterns(data):
    patterns = []
    try:
        if len(data) < 3: return patterns
        o, c, h, l = data['Open'].iloc[-1], data['Close'].iloc[-1], data['High'].iloc[-1], data['Low'].iloc[-1]
        body = abs(c - o)
        if min(o, c) - l > body * 2 and h - max(o, c) < body * 0.5 and c > o: patterns.append(" مطرقة")
        if c > o and data['Close'].iloc[-2] < data['Open'].iloc[-2] and c > data['Open'].iloc[-2] and o < data['Close'].iloc[-2]: patterns.append("📈 ابتلاعية")
        if body < (h - l) * 0.1: patterns.append("⚖️ دوجي")
    except: pass
    return patterns

def explain_recommendation(result):
    score = result['score']
    exp = ["🌟 <b>صفقة قوية جداً:</b> إشارات متعددة!" if score >= 6 else "✅ <b>شراء قوي:</b> معظم المؤشرات إيجابية." if score >= 5 else "🟡 <b>شراء:</b> مؤشرات إيجابية." if score >= 4 else "👀 <b>مراقبة:</b> يحتاج تأكيد." if score >= 3 else "🔴 <b>تجنب:</b> مؤشرات سلبية.", "\n <b>التفصيل:</b>"]
    for r in result['reasons']:
        if 'RSI منخفض جداً' in r: exp.append(f"• {r} → مباع بشكل زائد")
        elif 'RSI منخفض' in r: exp.append(f"• {r} → اقتراب من الشراء")
        elif 'فوق المتوسط' in r: exp.append(f"• {r} → اتجاه صعودي")
        elif 'تحت المتوسط' in r: exp.append(f"• {r} → اتجاه هبوطي")
        elif 'MACD' in r: exp.append(f"• {r} → زخم صعودي")
        elif 'حجم' in r: exp.append(f"• {r} → اهتمام كبير")
        elif 'ADX' in r: exp.append(f"• {r} → اتجاه قوي")
        elif 'OBV' in r: exp.append(f"• {r} → تراكم مؤسساتي")
        else: exp.append(f"• {r}")
    return "\n".join(exp)

def learn_from_predictions():
    settings = get_settings()
    learning_data = load_json(LEARNING_FILE, {'predictions': []})
    if not learning_data.get('predictions'): return
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    preds = [p for p in learning_data['predictions'] if p.get('date') == yesterday]
    if not preds: return
    correct, wrong = 0, 0
    for pred in preds:
        try:
            data = yf.Ticker(pred['symbol']).history(period='2d', interval='1d')
            if len(data) < 2: continue
            change = ((float(data['Close'].iloc[-1]) - pred['price']) / pred['price']) * 100
            if (pred['action'] == 'buy' and change > 0) or (pred['action'] != 'buy' and change < 0): correct += 1
            else: wrong += 1
        except: continue
    total = correct + wrong
    if total > 0:
        settings['total_predictions'] += total
        settings['correct_predictions'] += correct
        settings['accuracy_score'] = round(settings['correct_predictions'] / settings['total_predictions'], 2)
        rsi = settings['rsi_threshold']
        if settings['accuracy_score'] < 0.45 and rsi > 25:
            settings['rsi_threshold'] = max(25, rsi - 3)
            send_telegram(f"🧠 تحسين! الدقة: {settings['accuracy_score']*100}%. RSI: {rsi}→{settings['rsi_threshold']}")
        elif settings['accuracy_score'] > 0.70 and rsi < 45:
            settings['rsi_threshold'] = min(45, rsi + 2)
            send_telegram(f"📈 تحسين! الدقة: {settings['accuracy_score']*100}%. RSI: {rsi}→{settings['rsi_threshold']}")
        settings['last_adjustment'] = yesterday
        save_json(SETTINGS_FILE, settings)
        learning_data['predictions'] = [p for p in learning_data['predictions'] if p.get('date') >= (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')]
        save_json(LEARNING_FILE, learning_data)

def get_alerts(): return load_json(ALERTS_FILE, {'alerts': []})
def save_alerts(data): save_json(ALERTS_FILE, data)

def add_price_alert(symbol, target_price, alert_type='above'):
    symbol = symbol.upper()
    if not symbol.endswith('.SR'): symbol = symbol + '.SR'
    data = get_alerts()
    if 'alerts' not in data: data['alerts'] = []
    for alert in data['alerts']:
        if alert['symbol'] == symbol and alert['target'] == target_price: return False, f"️ التنبيه موجود بالفعل"
    data['alerts'].append({'symbol': symbol, 'target': target_price, 'type': alert_type, 'created': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'), 'triggered': False})
    save_alerts(data)
    return True, f"✅ تم إضافة تنبيه: {STOCK_NAMES.get(symbol, symbol)} {'فوق' if alert_type == 'above' else 'تحت'} {target_price} ر.س"

def remove_price_alert(symbol):
    symbol = symbol.upper()
    if not symbol.endswith('.SR'): symbol = symbol + '.SR'
    data = get_alerts()
    if 'alerts' not in data: return False, "❌ لا توجد تنبيهات"
    initial = len(data['alerts'])
    data['alerts'] = [a for a in data['alerts'] if a['symbol'] != symbol]
    if len(data['alerts']) == initial: return False, f"⚠️ لا يوجد تنبيه لـ {symbol}"
    save_alerts(data)
    return True, f"✅ تم حذف تنبيهات {symbol}"

def check_price_alerts():
    data = get_alerts()
    if 'alerts' not in data or not data['alerts']: return
    triggered = []
    for alert in data['alerts']:
        if alert.get('triggered'): continue
        try:
            hist = yf.Ticker(alert['symbol']).history(period='2d')
            if len(hist) < 1: continue
            current = float(hist['Close'].iloc[-1])
            if (alert['type'] == 'above' and current >= alert['target']) or (alert['type'] == 'below' and current <= alert['target']):
                alert['triggered'] = True
                triggered.append(alert)
                send_telegram(f"🔔 <b>تنبيه سعر!</b>\n\n {STOCK_NAMES.get(alert['symbol'], alert['symbol'])} ({alert['symbol'].replace('.SR', '')})\n💰 السعر الحالي: {current:.2f} ر.س\n🎯 الهدف: {alert['target']:.2f} ر.س\n⏰ {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
        except: continue
    if triggered: save_alerts(data)

def get_portfolio(): return load_json(PORTFOLIO_FILE, {'positions': []})
def save_portfolio(data): save_json(PORTFOLIO_FILE, data)

def add_position(symbol, shares, price, action='buy'):
    symbol = symbol.upper()
    if not symbol.endswith('.SR'): symbol = symbol + '.SR'
    data = get_portfolio()
    if 'positions' not in data: data['positions'] = []
    if action == 'buy':
        found = False
        for pos in data['positions']:
            if pos['symbol'] == symbol:
                total = pos['shares'] + shares
                pos['shares'] = total
                pos['avg_price'] = round(((pos['shares'] - shares) * pos['avg_price'] + shares * price) / total, 2)
                pos['last_update'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                found = True
                break
        if not found:
            data['positions'].append({'symbol': symbol, 'shares': shares, 'avg_price': round(price, 2), 'buy_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'), 'last_update': datetime.now(timezone.utc).strftime('%Y-%m-%d')})
        save_portfolio(data)
        return True, f"✅ تم شراء {shares} سهم من {STOCK_NAMES.get(symbol, symbol)} بسعر {price} ر.س"
    elif action == 'sell':
        for pos in data['positions']:
            if pos['symbol'] == symbol:
                if pos['shares'] < shares: return False, f"❌ لا تملك {shares} سهم، لديك {pos['shares']} فقط"
                profit = (price - pos['avg_price']) * shares
                pos['shares'] -= shares
                if pos['shares'] == 0: data['positions'].remove(pos)
                save_portfolio(data)
                return True, f"✅ تم بيع {shares} سهم من {STOCK_NAMES.get(symbol, symbol)}\n💵 الربح: {profit:.2f} ر.س"
        return False, f"❌ لا تملك {symbol}"

def update_position_price(symbol, new_price):
    symbol = symbol.upper()
    if not symbol.endswith('.SR'): symbol = symbol + '.SR'
    data = get_portfolio()
    if 'positions' not in data or not data['positions']: return False, "❌ المحفظة فارغة"
    for pos in data['positions']:
        if pos['symbol'] == symbol:
            old = pos['avg_price']
            pos['avg_price'] = round(new_price, 2)
            pos['last_update'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            save_portfolio(data)
            return True, f"✅ تم تحديث سعر {STOCK_NAMES.get(symbol, symbol)}\nمن: {old:.2f} ر.س\nإلى: {new_price:.2f} ر.س"
    return False, f" لا تملك {symbol} في المحفظة"

def export_portfolio():
    data = get_portfolio()
    if 'positions' not in data or not data['positions']: return "📊 <b>المحفظة فارغة</b>\n\nلا توجد صفقات للتصدير."
    msg = f" <b>تقرير المحفظة الكامل - السوق السعودي</b>\n📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n\n━━━━━━━━━━━━━━━━━━\n"
    total_inv, total_cur, total_prof = 0, 0, 0
    for i, pos in enumerate(data['positions'], 1):
        try:
            hist = yf.Ticker(pos['symbol']).history(period='2d')
            if len(hist) < 1: continue
            cur_price = float(hist['Close'].iloc[-1])
            inv = pos['shares'] * pos['avg_price']
            cur = pos['shares'] * cur_price
            prof = cur - inv
            pct = (prof / inv) * 100 if inv > 0 else 0
            total_inv += inv
            total_cur += cur
            total_prof += prof
            name = STOCK_NAMES.get(pos['symbol'], pos['symbol'])
            emoji = '🟢' if prof >= 0 else ''
            msg += f"<b>#{i}. {name} ({pos['symbol'].replace('.SR', '')})</b>\n• 📅 الشراء: {pos['buy_date']}\n• 🔢 العدد: {pos['shares']}\n• 💰 الدخول: {pos['avg_price']:.2f} ر.س\n•  الحالي: {cur_price:.2f} ر.س\n• 💵 القيمة: {cur:.2f} ر.س\n• {emoji} الربح: {prof:.2f} ر.س ({pct:+.2f}%)\n━━━━━━━━━━━━━━━━━━\n"
        except: continue
    pct_total = (total_prof / total_inv) * 100 if total_inv > 0 else 0
    emoji = '🟢' if total_prof >= 0 else '🔴'
    msg += f"\n📊 <b>الملخص الكلي:</b>\n💰 الاستثمار: {total_inv:.2f} ر.س\n💵 القيمة الحالية: {total_cur:.2f} ر.س\n{emoji} <b>إجمالي الربح/الخسارة: {total_prof:.2f} ر.س ({pct_total:+.2f}%)</b>\n\n📈 <b>إحصائيات:</b>\n• عدد الأسهم: {len(data['positions'])}\n• آخر تحديث: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    return msg

def get_portfolio_summary():
    data = get_portfolio()
    if 'positions' not in data or not data['positions']: return "📊 <b>المحفظة فارغة</b>\n\nاستخدم: /buy 2222 10 35"
    msg = "📊 <b>ملخص المحفظة - السوق السعودي</b>\n\n"
    total_inv, total_cur, total_prof = 0, 0, 0
    for pos in data['positions']:
        try:
            hist = yf.Ticker(pos['symbol']).history(period='2d')
            if len(hist) < 1: continue
            cur_price = float(hist['Close'].iloc[-1])
            inv = pos['shares'] * pos['avg_price']
            cur = pos['shares'] * cur_price
            prof = cur - inv
            pct = (prof / inv) * 100 if inv > 0 else 0
            total_inv += inv
            total_cur += cur
            total_prof += prof
            name = STOCK_NAMES.get(pos['symbol'], pos['symbol'])
            emoji = '🟢' if prof >= 0 else '🔴'
            msg += f"📌 <b>{name} ({pos['symbol'].replace('.SR', '')})</b>\n• العدد: {pos['shares']} | الشراء: {pos['avg_price']:.2f} | الحالي: {cur_price:.2f}\n• {emoji} الربح: {prof:.2f} ر.س ({pct:+.2f}%)\n\n"
        except: continue
    pct_total = (total_prof / total_inv) * 100 if total_inv > 0 else 0
    emoji = '🟢' if total_prof >= 0 else '🔴'
    msg += f"━━━━━━━━━━━━━━━\n💰 الاستثمار: {total_inv:.2f} ر.س | 💵 القيمة: {total_cur:.2f} ر.س\n{emoji} <b>إجمالي الربح: {total_prof:.2f} ر.س ({pct_total:+.2f}%)</b>"
    return msg

def calculate_risk_reward(symbol, entry, sl, tp):
    try:
        hist = yf.Ticker(symbol).history(period='2d')
        current = float(hist['Close'].iloc[-1])
        risk, reward = abs(entry - sl), abs(tp - entry)
        rr = reward / risk if risk > 0 else 0
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1])))
        msg = f"📊 <b>حاسبة المخاطرة - السوق السعودي</b>\n\n📌 السهم: {STOCK_NAMES.get(symbol, symbol)} ({symbol.replace('.SR', '')})\n💰 الحالي: {current:.2f} ر.س | 🎯 الدخول: {entry:.2f} ر.س\n️ وقف الخسارة: {sl:.2f} ر.س | 🎯 الهدف: {tp:.2f} ر.س\n\n⚖️ <b>المخاطرة/العائد:</b> 1:{rr:.2f}\n💵 المخاطرة: {risk:.2f} ر.س | 💰 العائد: {reward:.2f} ر.س\n\n"
        msg += "🌟 صفقة ممتازة!" if rr >= 3 else "✅ صفقة جيدة" if rr >= 2 else "🟡 صفقة مقبولة" if rr >= 1.5 else "🔴 صفقة ضعيفة"
        msg += f"\n📊 RSI: {rsi:.1f}"
        return msg
    except Exception as e: return f" خطأ: {str(e)}"

def get_top_movers():
    movers = {'gainers': [], 'losers': [], 'most_active': []}
    for sym in DEFAULT_STOCKS + ALL_SA_STOCKS[:30]:
        try:
            hist = yf.Ticker(sym).history(period='2d')
            if len(hist) < 2: continue
            c, p = float(hist['Close'].iloc[-1]), float(hist['Close'].iloc[-2])
            change = ((c - p) / p) * 100
            vol_ratio = float(hist['Volume'].iloc[-1]) / float(hist['Volume'].rolling(20).mean().iloc[-1]) if float(hist['Volume'].rolling(20).mean().iloc[-1]) > 0 else 1
            movers['gainers'].append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'change': round(change, 2), 'price': round(c, 2), 'volume_ratio': round(vol_ratio, 2)})
            movers['losers'].append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'change': round(change, 2), 'price': round(c, 2), 'volume_ratio': round(vol_ratio, 2)})
            movers['most_active'].append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'change': round(change, 2), 'volume_ratio': round(vol_ratio, 2)})
        except: continue
    movers['gainers'].sort(key=lambda x: x['change'], reverse=True)
    movers['losers'].sort(key=lambda x: x['change'])
    movers['most_active'].sort(key=lambda x: x['volume_ratio'], reverse=True)
    return movers

def analyze_sectors():
    sectors = {'2222.SR': 'الطاقة', '1120.SR': 'البنوك', '2010.SR': 'البتروكيماويات', '7010.SR': 'الاتصالات', '2280.SR': 'الزراعة', '2090.SR': 'التجزئة', '2380.SR': 'التعدين', '4001.SR': 'العقارات', '1180.SR': 'البنوك', '1150.SR': 'البنوك'}
    results = []
    for symbol, name in sectors.items():
        try:
            data = yf.Ticker(symbol).history(period='5d')
            if len(data) >= 2:
                c, p = float(data['Close'].iloc[-1]), float(data['Close'].iloc[-2])
                change = ((c - p) / p) * 100
                week_data = yf.Ticker(symbol).history(period='7d')
                week_change = ((c - float(week_data['Close'].iloc[0])) / float(week_data['Close'].iloc[0])) * 100 if len(week_data) >= 2 else change
                results.append({'symbol': symbol, 'name': name, 'change': round(change, 2), 'week_change': round(week_change, 2), 'price': round(c, 2)})
        except: continue
    results.sort(key=lambda x: x['change'], reverse=True)
    return results

def analyze_stock(symbol, settings):
    try:
        data = yf.Ticker(symbol).history(period='6mo', interval='1d')
        if len(data) < 50: return None
        price = float(data['Close'].iloc[-1])
        prev = float(data['Close'].iloc[-2])
        change = ((price - prev) / prev) * 100
        sma = float(data['Close'].rolling(50).mean().iloc[-1])
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1])))
        macd = float(data['Close'].ewm(span=12, adjust=False).mean().iloc[-1] - data['Close'].ewm(span=26, adjust=False).mean().iloc[-1])
        vol = float(data['Volume'].iloc[-1])
        avg_vol = float(data['Volume'].rolling(20).mean().iloc[-1])
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1
        adx = calculate_adx(data)
        obv = calculate_obv(data)
        patterns = detect_patterns(data)
        tr = pd.concat([data['High'] - data['Low'], (data['High'] - data['Close'].shift(1)).abs(), (data['Low'] - data['Close'].shift(1)).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        sl = round(price - (atr * 1.5), 2)
        t1 = round(price + (atr * 2), 2)
        t2 = round(price + (atr * 3), 2)
        risk_amt = settings['capital'] * settings['risk_percent'] / 100
        pos_size = int(risk_amt / (price - sl)) if price > sl and sl > 0 else 0
        score, reasons = 0, []
        rsi_th = settings.get('rsi_threshold', 35)
        if rsi < rsi_th: score += 2; reasons.append(f"📉 RSI منخفض جداً ({rsi:.1f})")
        elif rsi < rsi_th + 10: score += 1; reasons.append(f"📉 RSI منخفض ({rsi:.1f})")
        if price > sma: score += 1; reasons.append("📈 السعر فوق المتوسط")
        else: reasons.append(" السعر تحت المتوسط")
        if macd > 0: score += 1; reasons.append("✅ MACD إيجابي")
        if vol_ratio > 1.5: score += 1; reasons.append(f"💪 حجم عالي ({vol_ratio:.1f}x)")
        if adx > 25: score += 1; reasons.append(f"💪 ADX قوي ({adx:.1f})")
        if obv: score += 1; reasons.append(" تراكم OBV")
        if patterns: score += len(patterns); reasons.extend(patterns)
        bb = calculate_bollinger(data)
        if bb and ('مباع زائد' in bb['signal'] or 'فرصة شراء' in bb['signal']):
            score += 1; reasons.append(f" {bb['signal']}")
        cross = detect_golden_death_cross(data)
        if cross:
            if cross['type'] == 'golden': score += 2; reasons.append(cross['signal'])
            elif cross['type'] == 'death': score -= 2; reasons.append(cross['signal'])
            else: reasons.append(cross['signal'])
        rec, conf = ("🌟 صفقة قوية جداً", "عالية جداً") if score >= 6 else ("✅ شراء قوي", "عالية") if score >= 5 else ("🟡 شراء", "متوسطة") if score >= 4 else ("👀 مراقبة", "منخفضة") if score >= 3 else (" تجنب", "ضعيفة")
        rr = round((t1 - price) / (price - sl), 2) if sl > 0 else 0
        return {'symbol': symbol, 'price': price, 'change': round(change, 2), 'rsi': round(rsi, 1), 'macd': round(macd, 2), 'adx': round(adx, 1), 'volume_ratio': round(vol_ratio, 2), 'score': score, 'recommendation': rec, 'confidence': conf, 'reasons': reasons, 'stop_loss': sl, 'target1': t1, 'target2': t2, 'pos_size': pos_size, 'total_inv': round(pos_size * price, 2), 'risk_amt': round(risk_amt, 2), 'risk_reward': rr, 'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H'), 'bollinger': bb, 'cross': cross}
    except Exception as e:
        print(f"خطأ في {symbol}: {e}")
        return None

def find_affordable_stocks(settings, max_results=10):
    capital = settings['capital']
    risk_amt = capital * settings['risk_percent'] / 100
    affordable = []
    for sym in DEFAULT_STOCKS + ALL_SA_STOCKS[:30]:
        try:
            data = yf.Ticker(sym).history(period='5d', interval='1d')
            if len(data) < 3: continue
            price = float(data['Close'].iloc[-1])
            pos = min(int(capital / price), int(risk_amt / (price * 0.02)))
            if pos >= 10:
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1]))) if len(gain) > 0 else 50
                affordable.append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'price': price, 'change': round(((price - float(data['Close'].iloc[-2])) / float(data['Close'].iloc[-2])) * 100, 2), 'rsi': round(rsi, 1), 'position_size': pos, 'total_investment': round(pos * price, 2)})
        except: continue
    affordable.sort(key=lambda x: x['price'])
    return affordable[:max_results]

def generate_weekly_report():
    settings = get_settings()
    learning_data = load_json(LEARNING_FILE, {'predictions': []})
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
    week_predictions = [p for p in learning_data.get('predictions', []) if p.get('date', '') >= week_ago]
    sectors = analyze_sectors()
    movers = get_top_movers()
    tasi = get_tasi_index()
    msg = f"📊 <b>التقرير الأسبوعي - السوق السعودي</b>\n📅 الأسبوع المنتهي: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n━━━━━━━━━━━━━━━\n🧠 <b>أداء البوت:</b>\n• الدقة العامة: {settings['accuracy_score']*100}%\n• توقعات هذا الأسبوع: {len(week_predictions)}\n• إجمالي التوقعات: {settings['total_predictions']}\n• التوقعات الصحيحة: {settings['correct_predictions']}\n\n"
    if tasi: msg += f"📈 <b>مؤشر تاسي (TASI):</b> {tasi['price']} ({tasi['change']:+.2f}%)\n\n"
    if sectors:
        msg += f" <b>أفضل 3 قطاعات:</b>\n"
        for s in sectors[:3]: msg += f"{'🟢' if s['change'] > 0 else '🔴'} {s['name']}: {s['change']:+.2f}%\n"
        msg += f"\n🔴 <b>أسوأ 3 قطاعات:</b>\n"
        for s in sectors[-3:]: msg += f"{'' if s['change'] > 0 else '🔴'} {s['name']}: {s['change']:+.2f}%\n\n"
    if movers['gainers'][:3]:
        msg += f"🚀 <b>أفضل 3 أسهم رابحة:</b>\n"
        for m in movers['gainers'][:3]: msg += f"🟢 {m['name']}: {m['change']:+.2f}%\n"
    if movers['losers'][:3]:
        msg += f"\n <b>أسوأ 3 أسهم خاسرة:</b>\n"
        for m in movers['losers'][:3]: msg += f"🔴 {m['name']}: {m['change']:+.2f}%\n"
    msg += f"\n━━━━━━━━━━━━━━━\n <b>التوصيات:</b>\n"
    vix = get_vix()
    if vix: msg += f"• VIX العالمي: {vix['value']} ({vix['level']})\n"
    fg = get_fear_greed_index()
    if fg: msg += f"• مؤشر الخوف والطمع: {fg['score']} ({fg['label']})\n• {fg['advice']}\n"
    return msg

def handle_chat(text):
    text_lower = text.lower().strip()
    settings = get_settings()
    if any(w in text_lower for w in ['حالة السوق', 'market status', 'السوق مفتوح', 'market open', 'تداول']):
        status = get_market_status()
        return f"{status['emoji']} <b>حالة السوق السعودي:</b> {status['status']}\n📅 اليوم: {status.get('day', '')}\n📝 {status['reason']}\n🕐 التالي: {status['next_open']}"
    if any(w in text_lower for w in ['خوف وطمع', 'fear greed', 'fgi']):
        fg = get_fear_greed_index()
        return f"{fg['emoji']} <b>مؤشر الخوف والطمع:</b> {fg['score']}\n📊 الحالة: {fg['label']}\n💡 {fg['advice']}" if fg else "❌ لا يمكن حساب المؤشر"
    if any(w in text_lower for w in ['تاسي', 'tasi', 'مؤشر السوق']):
        tasi = get_tasi_index()
        return f"📊 <b>مؤشر تاسي (TASI):</b>\n💰 {tasi['price']}\n {tasi['change']:+.2f}%" if tasi else "❌ لا بيانات"
    if any(w in text_lower for w in ['قطاعات', 'sectors', 'القطاعات']):
        sectors = analyze_sectors()
        return f"🏢 <b>أداء القطاعات اليوم:</b>\n\n" + "\n".join([f"{'🟢' if s['change'] > 0 else '🔴'} <b>{s['name']}</b>: {s['change']:+.2f}%" for s in sectors]) if sectors else "❌ لا بيانات"
    if any(w in text_lower for w in ['top movers', 'أفضل الأسهم', 'الرابحين', 'الأسهم النشطة']):
        movers = get_top_movers()
        msg = "🚀 <b>أفضل 5 أسهم رابحة:</b>\n\n" + "\n".join([f" {m['name']}: {m['change']:+.2f}% ({m['price']} ر.س)" for m in movers['gainers'][:5]])
        msg += f"\n\n <b>أسوأ 5 أسهم خاسرة:</b>\n\n" + "\n".join([f"🔴 {m['name']}: {m['change']:+.2f}% ({m['price']} ر.س)" for m in movers['losers'][:5]])
        return msg
    for stock in DEFAULT_STOCKS + ALL_SA_STOCKS:
        stock_code = stock.replace('.SR', '')
        if stock_code in text_lower or stock.lower() in text_lower:
            result = analyze_stock(stock, settings)
            if result:
                name = STOCK_NAMES.get(stock, stock)
                msg = f"📊 <b>تحليل {name} ({stock_code}):</b>\n\n💰 السعر: {result['price']} ر.س ({result['change']:+.2f}%)\n📈 RSI: {result['rsi']} | MACD: {result['macd']} | ADX: {result['adx']}\n🎯 {result['recommendation']} ({result['confidence']})\n⭐ النقاط: {result['score']}/10\n\n"
                msg += explain_recommendation(result) + "\n\n"
                msg += f"<b>💰 الخطة:</b>\n• العدد: {result['pos_size']} سهم\n• الاستثمار: {result['total_inv']} ر.س\n• المخاطرة: {result['risk_amt']} ر.س\n️ SL: {result['stop_loss']} ر.س\n🎯 T1: {result['target1']} ر.س\n🎯 T2: {result['target2']} ر.س\n️ R/R: {result['risk_reward']}:1\n"
                if result.get('bollinger'):
                    bb = result['bollinger']
                    msg += f"\n📊 <b>Bollinger Bands:</b>\n• العلوي: {bb['upper']} ر.س\n• الأوسط: {bb['middle']} ر.س\n• السفلي: {bb['lower']} ر.س\n• %B: {bb['percent_b']}\n• الإشارة: {bb['signal']}\n"
                return msg
            return f"❌ لا بيانات لـ {stock_code}"
    if any(w in text_lower for w in ['اسهم رخيصة', 'رخيصة', 'cheap', 'affordable', 'ميزانيتي', 'budget', 'أسهم مناسبة']):
        affordable = find_affordable_stocks(settings)
        if affordable:
            msg = f"💰 <b>أسهم لميزانيتك ({settings['capital']} ر.س):</b>\n\nيمكنك شراء 10 أسهم على الأقل:\n\n"
            for s in affordable: msg += f"📌 <b>{s['name']} ({s['symbol'].replace('.SR', '')})</b>\n💰 {s['price']} ر.س ({s['change']:+.2f}%)\n📊 RSI: {s['rsi']}\n {s['position_size']} سهم\n💵 {s['total_investment']} ر.س\n\n"
            return msg
        return "❌ لا أسهم مناسبة"
    if any(w in text_lower for w in ['اخبار', 'news', 'أخبار السوق']):
        news = get_daily_news()
        if news:
            msg = "📰 <b>آخر أخبار السوق السعودي:</b>\n\n"
            for item in news[:5]: msg += f"📌 <b>{STOCK_NAMES.get(item['symbol'], item['symbol'])} ({item['symbol'].replace('.SR', '')}):</b> {item['title']}\n📰 {item['publisher']} | ⏰ {item['time']}\n\n"
            return msg
        return " لا أخبار"
    if any(w in text_lower for w in ['vix', 'الخوف', 'مؤشر الخوف']):
        vix = get_vix()
        return f"😱 <b>VIX (مؤشر الخوف العالمي):</b> {vix['emoji']} {vix['value']} - {vix['level']}" if vix else "❌ لا VIX"
    if any(w in text_lower for w in ['rsi', 'ما هو rsi', 'شرح rsi']):
        return "📊 <b>مؤشر RSI:</b>\n📉 <30: مباع زائد (فرصة شراء)\n📈 >70: مشتري زائد (قد ينخفض)\n⚖️ 30-70: منطقة محايدة\n\n🤖 البوت يستخدم RSI < 35 كإشارة شراء."
    if any(w in text_lower for w in ['مرحبا', 'هلا', 'hi', 'hello', 'السلام']):
        return "👋 أهلاً! 🇸 بوت تحليل الأسهم السعودية (تداول)\n\nيمكنني:\n• تحليل أي سهم سعودي\n• تتبع محفظتك\n• تنبيهات الأسعار\n• مؤشر تاسي والخوف والطمع\n\nجرب: 2222 (أرامكو), 1120 (الراجحي), /help"
    if any(w in text_lower for w in ['شكر', 'thanks', 'ممتاز', 'جزاك']):
        return "😊 العفو! هل تريد تحليل سهم أو لديك سؤال آخر؟"
    if any(w in text_lower for w in ['دقة', 'accuracy', 'اداء', 'أداء']):
        return f"🎯 <b>أداء البوت:</b>\n🎯 الدقة: {settings['accuracy_score']*100}%\n✅ {settings['correct_predictions']}/{settings['total_predictions']}\n⚙️ RSI: {settings['rsi_threshold']}"
    return "🤔 لم أفهم تماماً.\n\nجرب:\n• رمز سهم: 2222, 1120, 2010\n• أسهم رخيصة\n• حالة السوق\n• تاسي\n• /help للأوامر"

def process_message(text, settings):
    text_lower = text.lower().strip()
    if text == '/settings':
        msg = f"⚙️ <b>إعدادات البوت - السوق السعودي:</b>\n الميزانية: {settings['capital']} ر.س\n⚠️ المخاطرة: {settings['risk_percent']}%\n🧠 RSI: {settings['rsi_threshold']}\n الدقة: {settings['accuracy_score']*100}%\n📊 {settings['total_predictions']} توقع\n✅ {settings['correct_predictions']} صحيح\n\n<b>🧠 أنماط الأخطاء:</b>\n• RSI مرتفع: {settings['mistake_patterns'].get('high_rsi', 0)}\n• حجم منخفض: {settings['mistake_patterns'].get('low_volume', 0)}\n• اتجاه ضعيف: {settings['mistake_patterns'].get('weak_trend', 0)}\n• MACD خاطئ: {settings['mistake_patterns'].get('wrong_macd', 0)}"
        send_telegram(msg)
    elif text == '/help':
        msg = "🤖 <b>أوامر البوت - السوق السعودي 🇸🇦</b>\n\n📋 <b>الأساسية:</b>\n/settings - الإعدادات\n/status - حالة التعلم\n/stock [رمز] - تحليل سهم (مثال: /stock 2222)\n/affordable - أسهم لميزانيتك\n/news - أخبار السوق\n/vix - مؤشر الخوف العالمي\n/learn - مراجعة ذاتية\n\n💰 <b>الميزانية:</b>\n/capital [مبلغ] (مثال: /capital 50000)\n\n📌 <b>قائمة المراقبة:</b>\n/watchlist - عرض القائمة\n/watchlist add 2222 - إضافة سهم\n/watchlist remove 2222 - حذف سهم\n\n🔔 <b>التنبيهات:</b>\n/alert 2222 35 above - تنبيه فوق السعر\n/alert 1120 80 below - تنبيه تحت السعر\n/alerts - عرض التنبيهات\n/delalert 2222 - حذف التنبيه\n\n💼 <b>المحفظة:</b>\n/buy 2222 10 35 - شراء 10 أسهم بسعر 35\n/sell 2222 5 40 - بيع 5 أسهم بسعر 40\n/portfolio - ملخص المحفظة\n/update 2222 35.5 - تحديث سعر الدخول\n/export - تصدير تقرير المحفظة\n\n📊 <b>التحليل المتقدم:</b>\n/risk 2222 35 33 40 - حاسبة المخاطرة\n/weekly - التقرير الأسبوعي\n\n💬 <b>محادثة:</b>\nاكتب: 2222, 1120, تاسي, حالة السوق, أسهم رخيصة"
        send_telegram(msg)
    elif text == '/vix':
        vix = get_vix()
        if vix: send_telegram(f" <b>VIX (مؤشر الخوف العالمي):</b> {vix['emoji']} {vix['value']} - {vix['level']}")
    elif text == '/learn':
        learn_from_predictions()
        send_telegram("✅ تمت المراجعة الذاتية!")
    elif text == '/news':
        send_telegram("⏳ جاري جلب الأخبار...")
        send_daily_news_report()
    elif text.startswith('/stock '):
        sym = text.split()[1].upper()
        if not sym.endswith('.SR'): sym = sym + '.SR'
        result = analyze_stock(sym, settings)
        if result:
            name = STOCK_NAMES.get(result['symbol'], result['symbol'])
            code = result['symbol'].replace('.SR', '')
            msg = f"📊 <b>{name} ({code}):</b>\n💰 {result['price']} ر.س ({result['change']:+.2f}%)\n RSI: {result['rsi']} | MACD: {result['macd']} | ADX: {result['adx']}\n🎯 {result['recommendation']} ({result['confidence']})\n⭐ {result['score']}/10\n\n"
            msg += explain_recommendation(result) + "\n\n"
            msg += f"<b>💰 الخطة:</b>\n• {result['pos_size']} سهم\n• {result['total_inv']} ر.س\n• مخاطرة: {result['risk_amt']} ر.س\n🛡️ SL: {result['stop_loss']} ر.س\n🎯 T1: {result['target1']} ر.س\n🎯 T2: {result['target2']} ر.س\n⚖️ R/R: {result['risk_reward']}:1\n"
            if result.get('bollinger'):
                bb = result['bollinger']
                msg += f"\n <b>Bollinger Bands:</b>\n• العلوي: {bb['upper']} ر.س\n• الأوسط: {bb['middle']} ر.س\n• السفلي: {bb['lower']} ر.س\n• %B: {bb['percent_b']}\n• الإشارة: {bb['signal']}\n"
            if result.get('cross'): msg += f"\n{result['cross']['signal']}\n"
            send_telegram(msg)
        else: send_telegram(f"❌ لا بيانات لـ {sym.replace('.SR', '')}")
    elif text == '/affordable':
        send_telegram("⏳ جاري البحث...")
        affordable = find_affordable_stocks(settings)
        if affordable:
            msg = f"💰 <b>أسهم لميزانيتك ({settings['capital']} ر.س):</b>\n\nيمكنك شراء 10 أسهم على الأقل:\n\n"
            for s in affordable: msg += f"📌 <b>{s['name']} ({s['symbol'].replace('.SR', '')})</b>\n💰 {s['price']} ر.س ({s['change']:+.2f}%)\n📊 RSI: {s['rsi']}\n🔢 {s['position_size']} سهم\n💵 {s['total_investment']} ر.س\n\n"
            send_telegram(msg)
        else: send_telegram("❌ لا أسهم مناسبة")
    elif text == '/status':
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        preds = len([p for p in load_json(LEARNING_FILE, {'predictions': []}).get('predictions', []) if p.get('date') == today])
        send_telegram(f"🧠 <b>حالة التعلم:</b>\n🎯 الدقة: {settings['accuracy_score']*100}%\n⚙️ RSI: {settings['rsi_threshold']}\n📝 اليوم: {preds} توقع\n💡 يتعلم كل ساعة!")
    elif text == '/watchlist':
        watchlist = get_watchlist()
        msg = f"📌 <b>قائمة المراقبة ({len(watchlist)} سهم):</b>\n\n" + "\n".join([f"• {STOCK_NAMES.get(sym, sym)} ({sym.replace('.SR', '')})" for sym in watchlist])
        msg += f"\n\n<b>إدارة القائمة:</b>\n• إضافة: /watchlist add 2222\n• حذف: /watchlist remove 2222"
        send_telegram(msg)
    elif text.startswith('/capital '):
        try:
            amount = float(text.split()[1])
            if amount < 1000: send_telegram("❌ الحد الأدنى 1000 ر.س")
            else:
                settings['capital'] = amount
                save_json(SETTINGS_FILE, settings)
                send_telegram(f"✅ تم تحديث الميزانية إلى {amount} ر.س\n\n💰 استخدم /affordable لرؤية الأسهم المناسبة!")
        except: send_telegram("❌ استخدام: /capital [المبلغ]\nمثال: /capital 50000")
    elif text_lower.startswith('/alert '):
        parts = text_lower.split()
        if len(parts) >= 4:
            try:
                symbol = parts[1].upper()
                if not symbol.endswith('.SR'): symbol = symbol + '.SR'
                target = float(parts[2])
                alert_type = 'above' if parts[3].lower() in ['above', 'فوق', 'up'] else 'below' if parts[3].lower() in ['below', 'تحت', 'down'] else None
                if not alert_type: send_telegram("❌ النوع يجب أن يكون 'above' أو 'below'"); return
                success, msg = add_price_alert(symbol, target, alert_type)
                send_telegram(msg)
            except: send_telegram("❌ استخدام: /alert 2222 35 above")
        else: send_telegram("❌ استخدام: /alert [رمز] [السعر] [above/below]\nمثال: /alert 2222 35 above")
    elif text_lower == '/alerts':
        data = get_alerts()
        if not data.get('alerts'): send_telegram(" لا توجد تنبيهات")
        else:
            msg = "🔔 <b>التنبيهات النشطة:</b>\n\n" + "\n".join([f"📌 {STOCK_NAMES.get(a['symbol'], a['symbol'])} ({a['symbol'].replace('.SR', '')}) {'فوق' if a['type'] == 'above' else 'تحت'} {a['target']} ر.س" for a in data['alerts'] if not a.get('triggered')])
            msg += f"\n\n💡 استخدام: /delalert 2222 لحذف التنبيه"
            send_telegram(msg)
    elif text_lower.startswith('/delalert '):
        sym = text_lower.split()[1].upper()
        if not sym.endswith('.SR'): sym = sym + '.SR'
        success, msg = remove_price_alert(sym)
        send_telegram(msg)
    elif text_lower == '/portfolio':
        send_telegram(get_portfolio_summary())
    elif text_lower.startswith('/buy '):
        try:
            parts = text_lower.split()
            sym = parts[1].upper()
            if not sym.endswith('.SR'): sym = sym + '.SR'
            success, msg = add_position(sym, int(parts[2]), float(parts[3]), 'buy')
            send_telegram(msg)
        except: send_telegram("❌ استخدام: /buy 2222 10 35\n(رمز السهم، العدد، السعر)")
    elif text_lower.startswith('/sell '):
        try:
            parts = text_lower.split()
            sym = parts[1].upper()
            if not sym.endswith('.SR'): sym = sym + '.SR'
            success, msg = add_position(sym, int(parts[2]), float(parts[3]), 'sell')
            send_telegram(msg)
        except: send_telegram("❌ استخدام: /sell 2222 5 40\n(رمز السهم، العدد، السعر)")
    elif text_lower.startswith('/update '):
        try:
            parts = text_lower.split()
            sym = parts[1].upper()
            if not sym.endswith('.SR'): sym = sym + '.SR'
            new_price = float(parts[2])
            success, msg = update_position_price(sym, new_price)
            send_telegram(msg)
        except: send_telegram("❌ استخدام: /update 2222 35.5\n(رمز السهم، السعر الجديد)")
    elif text_lower == '/export':
        send_telegram("⏳ جاري تصدير المحفظة...")
        send_telegram(export_portfolio())
    elif text_lower.startswith('/risk '):
        try:
            parts = text_lower.split()
            sym = parts[1].upper()
            if not sym.endswith('.SR'): sym = sym + '.SR'
            send_telegram(calculate_risk_reward(sym, float(parts[2]), float(parts[3]), float(parts[4])))
        except: send_telegram("❌ استخدام: /risk 2222 35 33 40\n(رمز، دخول، وقف، هدف)")
    elif text_lower == '/weekly' or any(w in text_lower for w in ['تقرير أسبوعي', 'weekly report']):
        send_telegram("⏳ جاري إنشاء التقرير الأسبوعي...")
        send_telegram(generate_weekly_report())
    elif text and not text.startswith('/'):
        resp = handle_chat(text)
        if resp: send_telegram(resp)

def handle_commands():
    print("💬 بدء معالجة الأوامر...")
    bot_id = get_bot_id()
    print(f"🤖 Bot ID: {bot_id}")
    processed = get_processed()
    print(f"📋 الرسائل المعالجة: {len(processed)}")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset=0&limit=100&timeout=5"
        print("📡 الاتصال...")
        r = requests.get(url, timeout=10).json()
        if not r.get('ok'):
            print("❌ فشل الاتصال")
            return
        updates = r.get('result', [])
        print(f"📨 عدد التحديثات: {len(updates)}")
        if not updates:
            print("📭 لا رسائل")
            return
        settings = get_settings()
        count, skipped = 0, 0
        for update in updates:
            uid = update['update_id']
            if uid in processed: continue
            msg = update.get('message', {})
            if not msg:
                add_processed(uid)
                continue
            sender = msg.get('from', {})
            if sender.get('is_bot', False) or (bot_id and sender.get('id') == bot_id):
                print(f"🤖 تخطي رسالة بوت")
                add_processed(uid)
                skipped += 1
                continue
            text = msg.get('text', '').strip()
            chat_id = str(msg.get('chat', {}).get('id', ''))
            print(f"💬 رسالة: {text[:50]}")
            if chat_id != CHAT_ID:
                print(f"⚠️ Chat ID خاطئ: {chat_id}")
                add_processed(uid)
                skipped += 1
                continue
            try:
                process_message(text, settings)
                add_processed(uid)
                count += 1
                print(f"✅ تمت المعالجة: {uid}")
            except Exception as e:
                print(f" خطأ: {e}")
                add_processed(uid)
        print(f"✅ تمت معالجة {count}، تخطي {skipped}")
    except Exception as e:
        print(f"❌ خطأ: {e}")

def run_scan():
    print(" بدء فحص السوق السعودي...")
    settings = get_settings()
    watchlist = get_watchlist()
    learning_data = load_json(LEARNING_FILE, {'predictions': []})
    time_info = get_current_time()
    tasi = get_tasi_index()
    vix = get_vix()
    today = time_info['date']
    results, strong = [], []
    for sym in watchlist:
        try:
            result = analyze_stock(sym, settings)
            if result:
                results.append(result)
                learning_data['predictions'].append({'symbol': sym, 'price': result['price'], 'action': 'buy' if result['score'] >= 3 else 'avoid', 'rsi': result['rsi'], 'score': result['score'], 'volume_ratio': result.get('volume_ratio', 1), 'adx': result.get('adx', 0), 'macd': result.get('macd', 0), 'date': today, 'time': time_info['saudi_short'], 'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H')})
                if result['score'] >= 5: strong.append(result)
        except Exception as e: print(f"خطأ {sym}: {e}")
    save_json(LEARNING_FILE, learning_data)
    if results:
        results.sort(key=lambda x: x['score'], reverse=True)
        msg = f"📊 <b>فحص السوق السعودي 🇸🇦</b>\n📅 {time_info['saudi']}\n🧠 الدقة: {settings['accuracy_score']*100}% | RSI: {settings['rsi_threshold']}\n💰 الميزانية: {settings['capital']} ر.س\n\n"
        if tasi: msg += f"📈 <b>مؤشر تاسي (TASI):</b> {tasi['price']} ({tasi['change']:+.2f}%)\n"
        if vix: msg += f"😱 VIX العالمي: {vix['emoji']} {vix['value']} - {vix['level']}\n"
        msg += f"\n<b> أفضل 3 فرص:</b>\n\n"
        for r in results[:3]:
            name = STOCK_NAMES.get(r['symbol'], r['symbol'])
            code = r['symbol'].replace('.SR', '')
            msg += f"📌 <b>{name} ({code})</b> ({r['change']:+.2f}%)\n💰 {r['price']} ر.س | RSI: {r['rsi']} | ADX: {r['adx']}\n{r['recommendation']} ({r['score']} نقاط)\n📝 {', '.join(r['reasons'])}\n🛡️ SL: {r['stop_loss']} ر.س | T1: {r['target1']} ر.س | T2: {r['target2']} ر.س\n⚖️ R/R: {r['risk_reward']}:1\n\n"
            msg += explain_recommendation(r) + "\n\n"
        if strong:
            msg += f"\n <b>فرص قوية جداً!</b>\n\n"
            for r in strong:
                name = STOCK_NAMES.get(r['symbol'], r['symbol'])
                code = r['symbol'].replace('.SR', '')
                msg += f"🔥 <b>{name} ({code})</b> - {r['recommendation']}\n💰 {r['price']} ر.س | RSI: {r['rsi']}\n⭐ {r['score']}/10\n🛡️ SL: {r['stop_loss']} ر.س | T1: {r['target1']} ر.س | T2: {r['target2']} ر.س\n️ R/R: {r['risk_reward']}:1\n\n"
                msg += explain_recommendation(r) + "\n\n"
        send_telegram(msg)
        print(f"✅ تم إرسال التقرير ({len(strong)} فرصة قوية)")
    else: print("لا توجد بيانات")
    print("✅ انتهى الفحص")

if __name__ == '__main__':
    print("🚀 بدء بوت السوق السعودي 🇸🇦...")
    print("1️⃣ معالجة الأوامر...")
    handle_commands()
    now = datetime.now(timezone.utc)
    print("2️⃣ التعلم السريع...")
    fast_learning()
    print("🔔 فحص التنبيهات...")
    check_price_alerts()
    if now.hour == 10:
        print("3️⃣ المراجعة الذاتية...")
        learn_from_predictions()
    if now.hour == 9 and now.minute < 10:
        print("4️⃣ تقرير الأخبار...")
        send_daily_news_report()
    print("5️⃣ فحص السوق...")
    run_scan()
    print("✅ انتهى البوت")
