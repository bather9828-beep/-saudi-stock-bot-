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

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8945885655:AAGRrJHgsIL9f62ZuXJcmyCKyHVI-fNF2VU')
CHAT_ID = os.environ.get('CHAT_ID', '208377256')

DEFAULT_STOCKS = ['2222.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR', '2030.SR', '1150.SR', '2380.SR', '2280.SR', '2090.SR']

ALL_SA_STOCKS = [
    '2222.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR', '2030.SR', '1150.SR', '2380.SR',
    '2280.SR', '2090.SR', '1211.SR', '2060.SR', '4001.SR', '4030.SR', '6010.SR', '8010.SR',
    '1010.SR', '1020.SR', '1030.SR', '1050.SR', '1060.SR', '1140.SR', '1201.SR', '1210.SR',
    '2001.SR', '2020.SR', '2040.SR', '2050.SR', '2060.SR', '2070.SR', '2080.SR', '2090.SR',
    '2100.SR', '2110.SR', '2120.SR', '2130.SR', '2140.SR', '2150.SR', '2160.SR', '2170.SR',
    '2180.SR', '2190.SR', '2200.SR', '2210.SR', '2220.SR', '2230.SR', '2240.SR', '2250.SR',
    '2260.SR', '2270.SR', '2290.SR', '2300.SR', '2310.SR', '2320.SR', '2330.SR', '2340.SR',
    '2350.SR', '2360.SR', '2370.SR', '2390.SR', '4002.SR', '4003.SR', '4004.SR', '4005.SR',
    '4006.SR', '4007.SR', '4008.SR', '4009.SR', '4010.SR', '4011.SR', '4012.SR', '4013.SR',
    '4014.SR', '4015.SR', '4016.SR', '4017.SR', '4018.SR', '4019.SR', '4020.SR', '4031.SR',
    '4040.SR', '4050.SR', '4060.SR', '4061.SR', '4062.SR', '4063.SR', '6020.SR', '6030.SR',
    '6040.SR', '6050.SR', '6060.SR', '6070.SR', '6080.SR', '7020.SR', '7030.SR', '7040.SR',
    '7050.SR', '7060.SR', '7070.SR', '7080.SR', '8020.SR', '8030.SR', '8040.SR', '8050.SR',
    '8060.SR', '8070.SR', '8080.SR', '^TASI.SR'
]

STOCK_NAMES = {
    '2222.SR': 'أرامكو السعودية', '1120.SR': 'مصرف الراجحي', '2010.SR': 'سابك',
    '1180.SR': 'البنك الأهلي السعودي', '7010.SR': 'STC الاتصالات', '2030.SR': 'سابك للمغذيات',
    '1150.SR': 'مصرف الإنماء', '2380.SR': 'معادن', '2280.SR': 'المراعي', '2090.SR': 'جرير',
    '1211.SR': 'معادن', '2060.SR': 'كيان السعودية', '4001.SR': 'دار الأركان',
    '4030.SR': 'ريت الراجحي', '6010.SR': 'Bupa العربية', '8010.SR': 'مصرف الإنماء',
    '1010.SR': 'الرياض للتعمير', '1020.SR': 'أسمنت الشرقية', '1030.SR': 'أسمنت الجنوبية',
    '1050.SR': 'أسمنت المدينة', '1060.SR': 'أسمنت القصيم', '1140.SR': 'البنك الفرنسي',
    '1201.SR': 'تكامل', '1210.SR': 'سابكو', '2001.SR': 'شمس',
    '2020.SR': 'سابك للمعادن', '2040.SR': 'سبكيم', '2050.SR': 'الصحراء',
    '2070.SR': 'التصنيع', '2080.SR': 'العجين', '2100.SR': 'الزامل',
    '2110.SR': 'ساكو', '2120.SR': 'المراعي', '2130.SR': 'هرفي',
    '2140.SR': 'نادك', '2150.SR': 'البابطين', '2160.SR': 'التصنيع',
    '2170.SR': 'الصرايعي', '2180.SR': 'غازكو', '2190.SR': 'أمنيات',
    '2200.SR': 'معادن ألمنيوم', '2210.SR': 'أمنيات', '2220.SR': 'أمنيات',
    '2230.SR': 'أمنيات', '2240.SR': 'ملاث', '2250.SR': 'التعاونية',
    '2260.SR': 'بوبا العربية', '2270.SR': 'مدجلف', '2290.SR': 'اتحاد الخليج',
    '2300.SR': 'الأهلي تكافل', '2310.SR': 'الراجحي تكافل', '2320.SR': 'ولاء',
    '2330.SR': 'سلامة', '2340.SR': 'اتحاد اتصالات', '2350.SR': 'زين',
    '2360.SR': 'أثير', '2370.SR': 'الحلول', '2390.SR': 'أثير',
    '4002.SR': 'الأحساء', '4003.SR': 'جبل عمر', '4004.SR': 'مكة للإنشاء',
    '4005.SR': 'إعمار المدينة', '4006.SR': 'دار الأركان', '4007.SR': 'جبل عمر',
    '4008.SR': 'عسير', '4009.SR': 'الأندلس', '4010.SR': 'طيبة',
    '4011.SR': 'مكة للإنشاء', '4012.SR': 'الأحساء', '4013.SR': 'جبل عمر',
    '4014.SR': 'إعمار المدينة', '4015.SR': 'دار الأركان', '4016.SR': 'طيبة',
    '4017.SR': 'عسير', '4018.SR': 'الأندلس', '4019.SR': 'مكة للإنشاء',
    '4020.SR': 'جبل عمر', '4031.SR': 'ريت الراجحي', '4040.SR': 'جدوى ريت',
    '4050.SR': 'الإنماء ريت', '4060.SR': 'الرياض ريت', '4061.SR': 'الأهلي ريت',
    '4062.SR': 'البلاد ريت', '4063.SR': 'الإنماء ريت', '6020.SR': 'بوبا العربية',
    '6030.SR': 'التعاونية', '6040.SR': 'مدجلف', '6050.SR': 'اتحاد الخليج',
    '6060.SR': 'ملاث', '6070.SR': 'سلامة', '6080.SR': 'ولاء',
    '7020.SR': 'ساكو', '7030.SR': 'هرفي', '7040.SR': 'نادك',
    '7050.SR': 'البابطين', '7060.SR': 'الصرايعي', '7070.SR': 'التصنيع',
    '7080.SR': 'غازكو', '8020.SR': 'أمنيات', '8030.SR': 'أمنيات',
    '8040.SR': 'أمنيات', '8050.SR': 'أمنيات', '8060.SR': 'ملاث',
    '8070.SR': 'التعاونية', '8080.SR': 'بوبا العربية', '^TASI.SR': 'مؤشر تاسي'
}

PROCESSED_FILE = 'processed_messages.json'
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
    if 'stocks' not in data:
        data['stocks'] = DEFAULT_STOCKS.copy()
        save_json(WATCHLIST_FILE, data)
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
        max_len = 4000
        if len(msg) > max_len:
            chunks = [msg[i:i+max_len] for i in range(0, len(msg), max_len)]
            for chunk in chunks:
                requests.post(url, json={"chat_id": CHAT_ID, "text": chunk, "parse_mode": parse_mode}, timeout=10)
                time.sleep(0.5)
            return True
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": parse_mode}, timeout=10)
        return True
    except: return False

def get_bot_info():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
        response = requests.get(url, timeout=5).json()
        if response.get('ok'): return response['result']
    except: pass
    return None

# ✅ الحل الصحيح: حفظ آخر update_id فعلياً
def get_last_processed_id():
    data = load_json(PROCESSED_FILE, {'last_id': 0, 'date': ''})
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if data.get('date') != today:
        data = {'last_id': 0, 'date': today}
        save_json(PROCESSED_FILE, data)
    return data.get('last_id', 0)

def save_last_processed_id(update_id):
    data = load_json(PROCESSED_FILE, {'last_id': 0, 'date': ''})
    data['last_id'] = update_id
    data['date'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    save_json(PROCESSED_FILE, data)

def get_current_time():
    utc_now = datetime.now(timezone.utc)
    saudi_tz = timezone(timedelta(hours=3))
    saudi_now = utc_now.astimezone(saudi_tz)
    return {
        'saudi': saudi_now.strftime('%Y-%m-%d %H:%M:%S (توقيت السعودية)'),
        'saudi_short': saudi_now.strftime('%H:%M'),
        'date': saudi_now.strftime('%Y-%m-%d'),
        'hour': saudi_now.hour,
        'minute': saudi_now.minute
    }

def get_market_status():
    try:
        utc_now = datetime.now(timezone.utc)
        saudi_tz = timezone(timedelta(hours=3))
        saudi_now = utc_now.astimezone(saudi_tz)
        day = saudi_now.weekday()
        time_minutes = saudi_now.hour * 60 + saudi_now.minute
        days_ar = {0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء', 3: 'الخميس', 4: 'الجمعة', 5: 'السبت', 6: 'الأحد'}
        current_day = days_ar.get(day, '')
        if day == 4: return {'status': 'مغلق', 'emoji': '🔴', 'reason': 'عطلة نهاية الأسبوع (الجمعة)', 'next_open': 'الأحد 10:00 صباحاً', 'day': current_day}
        if day == 5: return {'status': 'مغلق', 'emoji': '🔴', 'reason': 'عطلة نهاية الأسبوع (السبت)', 'next_open': 'الأحد 10:00 صباحاً', 'day': current_day}
        if time_minutes < 600: return {'status': 'مغلق', 'emoji': '', 'reason': 'قبل الافتتاح', 'next_open': '10:00 صباحاً', 'day': current_day}
        elif time_minutes < 900: return {'status': 'مفتوح', 'emoji': '🟢', 'reason': 'جلسة التداول نشطة (10:00 - 15:00)', 'next_open': 'جاري التداول', 'day': current_day}
        else: return {'status': 'مغلق', 'emoji': '🔴', 'reason': 'بعد الإغلاق', 'next_open': 'غداً 10:00 صباحاً', 'day': current_day}
    except:
        return {'status': 'غير معروف', 'emoji': '⚪', 'reason': 'خطأ', 'next_open': 'غير معروف', 'day': ''}

def get_tasi_index():
    try:
        tasi = yf.Ticker('^TASI.SR')
        data = tasi.history(period='5d')
        if len(data) > 0:
            current = float(data['Close'].iloc[-1])
            prev = float(data['Close'].iloc[-2])
            change = ((current - prev) / prev) * 100
            return {'price': round(current, 2), 'change': round(change, 2)}
    except: pass
    return None

def get_vix():
    try:
        vix = yf.Ticker('^VIX')
        data = vix.history(period='5d')
        if len(data) > 0:
            current = float(data['Close'].iloc[-1])
            if current < 15: return {'value': round(current, 2), 'level': 'منخفض', 'emoji': '🟢'}
            elif current < 20: return {'value': round(current, 2), 'level': 'معتدل', 'emoji': '🟡'}
            elif current < 30: return {'value': round(current, 2), 'level': 'مرتفع', 'emoji': '🟠'}
            else: return {'value': round(current, 2), 'level': 'مرتفع جداً', 'emoji': '🔴'}
    except: pass
    return None

def get_fear_greed_index():
    try:
        indicators = {}
        vix = get_vix()
        if vix:
            if vix['value'] < 15: indicators['vix'] = 80
            elif vix['value'] < 20: indicators['vix'] = 60
            elif vix['value'] < 30: indicators['vix'] = 40
            else: indicators['vix'] = 20
        tasi = get_tasi_index()
        if tasi:
            if tasi['change'] > 2: indicators['tasi'] = 80
            elif tasi['change'] > 1: indicators['tasi'] = 65
            elif tasi['change'] > -1: indicators['tasi'] = 50
            elif tasi['change'] > -2: indicators['tasi'] = 35
            else: indicators['tasi'] = 20
        advancers, decliners = 0, 0
        for sym in DEFAULT_STOCKS[:10]:
            try:
                d = yf.Ticker(sym).history(period='2d')
                if len(d) >= 2:
                    if float(d['Close'].iloc[-1]) > float(d['Close'].iloc[-2]): advancers += 1
                    elif float(d['Close'].iloc[-1]) < float(d['Close'].iloc[-2]): decliners += 1
            except: continue
        if advancers + decliners > 0:
            indicators['breadth'] = int((advancers / (advancers + decliners)) * 100)
        if indicators:
            score = round(sum(indicators.values()) / len(indicators), 1)
            if score >= 75: label, emoji, advice = 'طمع شديد', '', '⚠️ كن حذراً، السوق قد يكون مبالغاً فيه'
            elif score >= 60: label, emoji, advice = 'طمع', '🟢', '✅ اتجاه صعودي، ابحث عن فرص'
            elif score >= 40: label, emoji, advice = 'محايد', '🟡', '⚖️ السوق متوازن'
            elif score >= 25: label, emoji, advice = 'خوف', '🟠', '🔍 ابحث عن فرص شراء'
            else: label, emoji, advice = 'خوف شديد', '🔴', '💰 فرص شراء ممتازة!'
            return {'score': score, 'label': label, 'emoji': emoji, 'advice': advice}
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
    six_hours_ago = (now - timedelta(hours=6)).strftime('%Y-%m-%d %H')
    recent = [p for p in learning_data['predictions'] if p.get('timestamp', '') >= six_hours_ago]
    if not recent:
        settings['last_fast_learning'] = now.isoformat()
        save_json(SETTINGS_FILE, settings)
        return
    correct, wrong = 0, 0
    mistakes = {'high_rsi': 0, 'low_volume': 0, 'weak_trend': 0, 'wrong_macd': 0}
    for pred in recent:
        try:
            ticker = yf.Ticker(pred['symbol'])
            data = ticker.history(period='1d', interval='1h')
            if len(data) < 2: continue
            actual = float(data['Close'].iloc[-1])
            change = ((actual - pred['price']) / pred['price']) * 100
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
        elif mistakes['low_volume'] > 2:
            send_telegram(f"️ {mistakes['low_volume']} أخطاء حجم منخفض")
        elif mistakes['weak_trend'] > 2:
            send_telegram(f" {mistakes['weak_trend']} أخطاء اتجاه ضعيف")
        settings['last_fast_learning'] = now.isoformat()
        save_json(SETTINGS_FILE, settings)

def get_daily_news():
    news_cache = load_json(NEWS_FILE, {'last_update': None, 'news': []})
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if news_cache.get('last_update') == today: return news_cache['news']
    items = []
    for sym in ['2222.SR', '1120.SR', '2010.SR', '7010.SR', '2380.SR']:
        try:
            news = yf.Ticker(sym).news
            if news:
                for item in news[:3]:
                    t, p = item.get('title', ''), item.get('publisher', '')
                    if t and p:
                        items.append({'symbol': sym, 'title': t, 'publisher': p, 'time': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%H:%M')})
        except: continue
    save_json(NEWS_FILE, {'last_update': today, 'news': items[:15]})
    return items[:15]

def send_daily_news_report():
    news = get_daily_news()
    if not news: return
    time_info = get_current_time()
    tasi = get_tasi_index()
    msg = f"📰 <b>تقرير الأخبار اليومي - السوق السعودي</b>\n📅 {time_info['saudi']}\n\n"
    if tasi: msg += f"📊 <b>مؤشر تاسي (TASI):</b> {tasi['price']} ({tasi['change']:+.2f}%)\n\n"
    by_sym = {}
    for item in news:
        by_sym.setdefault(item['symbol'], []).append(item)
    for sym, items in by_sym.items():
        msg += f"📌 <b>{STOCK_NAMES.get(sym, sym)} ({sym.replace('.SR', '')}):</b>\n"
        for item in items[:2]: msg += f"• {item['title']}\n   📰 {item['publisher']} | ⏰ {item['time']}\n\n"
    send_telegram(msg)

def analyze_best_times(symbol):
    try:
        data = yf.download(symbol, period='3mo', interval='30m', progress=False)
        if len(data) < 100: return None
        data['hour'] = data.index.hour
        data['return'] = data['Close'].pct_change() * 100
        return [(int(h), round(float(v), 2)) for h, v in data.groupby('hour')['return'].mean().nlargest(3).items()]
    except: return None

def analyze_best_days(symbol):
    try:
        data = yf.download(symbol, period='6mo', interval='1d', progress=False)
        if len(data) < 100: return None
        data['day_of_week'] = data.index.dayofweek
        data['return'] = data['Close'].pct_change() * 100
        days = {0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء', 3: 'الخميس', 6: 'الأحد'}
        return [(days.get(int(d), d), round(float(v), 2)) for d, v in data.groupby('day_of_week')['return'].mean().nlargest(3).items()]
    except: return None

def calculate_obv(data):
    try:
        obv = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()
        return float(obv.iloc[-1]) > float(obv.rolling(20).mean().iloc[-1])
    except: return False

def calculate_adx(data, period=14):
    try:
        h, l, c = data['High'], data['Low'], data['Close']
        pdm = h.diff(); pdm[pdm < 0] = 0
        ndm = l.diff(); ndm[ndm > 0] = 0
        tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        pdi = 100 * (pdm.rolling(period).mean() / atr)
        ndi = 100 * (ndm.rolling(period).mean() / atr)
        dx = 100 * ((pdi - ndi).abs() / (pdi + ndi))
        adx = dx.rolling(period).mean()
        return float(adx.iloc[-1]) if not adx.empty else 0
    except: return 0

def calculate_bollinger(data, period=20, std_dev=2):
    try:
        sma = data['Close'].rolling(period).mean()
        std = data['Close'].rolling(period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        current = float(data['Close'].iloc[-1])
        upper_val, lower_val, sma_val = float(upper.iloc[-1]), float(lower.iloc[-1]), float(sma.iloc[-1])
        percent_b = (current - lower_val) / (upper_val - lower_val) if (upper_val - lower_val) != 0 else 0.5
        signal = 'محايد'
        if current <= lower_val * 1.01: signal = 'مباع زائد (فرصة شراء)'
        elif current >= upper_val * 0.99: signal = 'مُشرى زائد (فرصة بيع)'
        elif current < sma_val: signal = 'تحت المتوسط'
        else: signal = 'فوق المتوسط'
        return {'upper': round(upper_val, 2), 'middle': round(sma_val, 2), 'lower': round(lower_val, 2), 'percent_b': round(percent_b, 2), 'signal': signal}
    except: return None

def detect_golden_death_cross(data):
    try:
        if len(data) < 200: return None
        ma50, ma200 = data['Close'].rolling(50).mean(), data['Close'].rolling(200).mean()
        curr_50, curr_200 = float(ma50.iloc[-1]), float(ma200.iloc[-1])
        prev_50, prev_200 = float(ma50.iloc[-2]), float(ma200.iloc[-2])
        if prev_50 < prev_200 and curr_50 > curr_200: return {'type': 'golden', 'signal': '🌟 تقاطع ذهبي - إشارة شراء قوية جداً'}
        elif prev_50 > prev_200 and curr_50 < curr_200: return {'type': 'death', 'signal': '💀 تقاطع ميت - إشارة بيع قوية'}
        elif curr_50 > curr_200: return {'type': 'bullish', 'signal': ' اتجاه صعودي (MA50 فوق MA200)'}
        else: return {'type': 'bearish', 'signal': '📉 اتجاه هبوطي (MA50 تحت MA200)'}
    except: return None

def detect_patterns(data):
    patterns = []
    try:
        if len(data) < 3: return patterns
        o, c, h, l = data['Open'].iloc[-1], data['Close'].iloc[-1], data['High'].iloc[-1], data['Low'].iloc[-1]
        body = abs(c - o)
        if min(o, c) - l > body * 2 and h - max(o, c) < body * 0.5 and c > o: patterns.append("🔨 مطرقة")
        if c > o and data['Close'].iloc[-2] < data['Open'].iloc[-2] and c > data['Open'].iloc[-2] and o < data['Close'].iloc[-2]: patterns.append("📈 ابتلاعية")
        if body < (h - l) * 0.1: patterns.append("⚖️ دوجي")
    except: pass
    return patterns

def explain_recommendation(result):
    score = result['score']
    exp = []
    if score >= 6: exp.append("🌟 <b>صفقة قوية جداً:</b> إشارات متعددة!")
    elif score >= 5: exp.append("✅ <b>شراء قوي:</b> معظم المؤشرات إيجابية.")
    elif score >= 4: exp.append("🟡 <b>شراء:</b> مؤشرات إيجابية.")
    elif score >= 3: exp.append("👀 <b>مراقبة:</b> يحتاج تأكيد.")
    else: exp.append("🔴 <b>تجنب:</b> مؤشرات سلبية.")
    exp.append("\n📝 <b>التفصيل:</b>")
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
        if alert['symbol'] == symbol and alert['target'] == target_price:
            return False, f"️ التنبيه موجود بالفعل لـ {symbol}"
    data['alerts'].append({'symbol': symbol, 'target': target_price, 'type': alert_type, 'created': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'), 'triggered': False})
    save_alerts(data)
    type_ar = 'فوق' if alert_type == 'above' else 'تحت'
    return True, f"✅ تم إضافة تنبيه: {STOCK_NAMES.get(symbol, symbol)} {type_ar} {target_price} ر.س"

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
            t = yf.Ticker(alert['symbol'])
            hist = t.history(period='2d')
            if len(hist) < 1: continue
            current = float(hist['Close'].iloc[-1])
            if (alert['type'] == 'above' and current >= alert['target']) or (alert['type'] == 'below' and current <= alert['target']):
                alert['triggered'] = True
                triggered.append(alert)
                name = STOCK_NAMES.get(alert['symbol'], alert['symbol'])
                send_telegram(f"🔔 <b>تنبيه سعر!</b>\n\n📌 {name} ({alert['symbol'].replace('.SR', '')})\n💰 السعر الحالي: {current:.2f} ر.س\n🎯 الهدف: {alert['target']:.2f} ر.س\n {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
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
                total_shares = pos['shares'] + shares
                pos['shares'] = total_shares
                pos['avg_price'] = round(((pos['shares'] - shares) * pos['avg_price'] + shares * price) / total_shares, 2)
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
    if 'positions' not in data or not data['positions']:
        return False, "❌ المحفظة فارغة"
    for pos in data['positions']:
        if pos['symbol'] == symbol:
            old_price = pos['avg_price']
            pos['avg_price'] = round(new_price, 2)
            pos['last_update'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            save_portfolio(data)
            return True, f"✅ تم تحديث سعر {STOCK_NAMES.get(symbol, symbol)}\nمن: {old_price:.2f} ر.س\nإلى: {new_price:.2f} ر.س"
    return False, f"❌ لا تملك {symbol} في المحفظة"

def export_portfolio():
    data = get_portfolio()
    if 'positions' not in data or not data['positions']:
        return "📊 <b>المحفظة فارغة</b>\n\nلا توجد صفقات للتصدير."
    msg = f"📊 <b>تقرير المحفظة الكامل - السوق السعودي</b>\n"
    msg += f"📅 التاريخ: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    total_invested, total_current, total_profit = 0, 0, 0
    for i, pos in enumerate(data['positions'], 1):
        try:
            t = yf.Ticker(pos['symbol'])
            hist = t.history(period='2d')
            if len(hist) < 1: continue
            current_price = float(hist['Close'].iloc[-1])
            invested = pos['shares'] * pos['avg_price']
            current_value = pos['shares'] * current_price
            profit = current_value - invested
            profit_pct = (profit / invested) * 100 if invested > 0 else 0
            total_invested += invested
            total_current += current_value
            total_profit += profit
            name = STOCK_NAMES.get(pos['symbol'], pos['symbol'])
            emoji = '🟢' if profit >= 0 else '🔴'
            msg += f"<b>#{i}. {name} ({pos['symbol'].replace('.SR', '')})</b>\n"
            msg += f"•  تاريخ الشراء: {pos['buy_date']}\n"
            msg += f"• 🔢 عدد الأسهم: {pos['shares']}\n"
            msg += f"• 💰 سعر الدخول: {pos['avg_price']:.2f} ر.س\n"
            msg += f"•  السعر الحالي: {current_price:.2f} ر.س\n"
            msg += f"• 💵 القيمة الحالية: {current_value:.2f} ر.س\n"
            msg += f"• {emoji} الربح/الخسارة: {profit:.2f} ر.س ({profit_pct:+.2f}%)\n"
            msg += f"━━━━━━━━━━━━━━━━━━\n"
        except: continue
    total_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    emoji = '' if total_profit >= 0 else ''
    msg += f"\n <b>الملخص الكلي:</b>\n"
    msg += f"💰 إجمالي الاستثمار: {total_invested:.2f} ر.س\n"
    msg += f"💵 القيمة الحالية: {total_current:.2f} ر.س\n"
    msg += f"{emoji} <b>إجمالي الربح/الخسارة: {total_profit:.2f} ر.س ({total_pct:+.2f}%)</b>\n\n"
    msg += f"📈 <b>إحصائيات:</b>\n"
    msg += f"• عدد الأسهم في المحفظة: {len(data['positions'])}\n"
    msg += f"• آخر تحديث: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
    return msg

def get_portfolio_summary():
    data = get_portfolio()
    if 'positions' not in data or not data['positions']: return "📊 <b>المحفظة فارغة</b>\n\nاستخدم: /buy 2222 10 35"
    msg = f"📊 <b>ملخص المحفظة - السوق السعودي</b>\n\n"
    total_invested, total_current, total_profit = 0, 0, 0
    for pos in data['positions']:
        try:
            t = yf.Ticker(pos['symbol'])
            hist = t.history(period='2d')
            if len(hist) < 1: continue
            current_price = float(hist['Close'].iloc[-1])
            invested = pos['shares'] * pos['avg_price']
            current_value = pos['shares'] * current_price
            profit = current_value - invested
            profit_pct = (profit / invested) * 100 if invested > 0 else 0
            total_invested += invested
            total_current += current_value
            total_profit += profit
            name = STOCK_NAMES.get(pos['symbol'], pos['symbol'])
            emoji = '' if profit >= 0 else ''
            msg += f"📌 <b>{name} ({pos['symbol'].replace('.SR', '')})</b>\n• العدد: {pos['shares']} سهم\n• سعر الشراء: {pos['avg_price']:.2f} ر.س\n• السعر الحالي: {current_price:.2f} ر.س\n• {emoji} الربح: {profit:.2f} ر.س ({profit_pct:+.2f}%)\n\n"
        except: continue
    total_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    emoji = '' if total_profit >= 0 else ''
    msg += f"━━━━━━━━━━━━━━━\n💰 إجمالي الاستثمار: {total_invested:.2f} ر.س\n💵 القيمة الحالية: {total_current:.2f} ر.س\n{emoji} <b>إجمالي الربح: {total_profit:.2f} ر.س ({total_pct:+.2f}%)</b>"
    return msg

def calculate_risk_reward(symbol, entry, sl, tp):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period='2d')
        current = float(hist['Close'].iloc[-1])
        risk, reward = abs(entry - sl), abs(tp - entry)
        rr = reward / risk if risk > 0 else 0
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = float(100 - (100 / (1 + (gain / loss).iloc[-1])))
        msg = f"📊 <b>حاسبة المخاطرة - السوق السعودي</b>\n\n📌 السهم: {STOCK_NAMES.get(symbol, symbol)} ({symbol.replace('.SR', '')})\n💰 السعر الحالي: {current:.2f} ر.س\n🎯 نقطة الدخول: {entry:.2f} ر.س\n️ وقف الخسارة: {sl:.2f} ر.س\n🎯 الهدف: {tp:.2f} ر.س\n\n⚖️ <b>المخاطرة/العائد:</b> 1:{rr:.2f}\n💵 المخاطرة: {risk:.2f} ر.س\n💰 العائد المحتمل: {reward:.2f} ر.س\n\n"
        if rr >= 3: msg += "🌟 صفقة ممتازة!"
        elif rr >= 2: msg += "✅ صفقة جيدة"
        elif rr >= 1.5: msg += "🟡 صفقة مقبولة"
        else: msg += "🔴 صفقة ضعيفة"
        msg += f"\n RSI: {rsi:.1f}"
        return msg
    except Exception as e: return f"❌ خطأ: {str(e)}"

def get_top_movers():
    movers = {'gainers': [], 'losers': [], 'most_active': []}
    for sym in DEFAULT_STOCKS + ALL_SA_STOCKS[:30]:
        try:
            hist = yf.Ticker(sym).history(period='2d')
            if len(hist) < 2: continue
            current, prev = float(hist['Close'].iloc[-1]), float(hist['Close'].iloc[-2])
            change = ((current - prev) / prev) * 100
            vol_ratio = float(hist['Volume'].iloc[-1]) / float(hist['Volume'].rolling(20).mean().iloc[-1]) if float(hist['Volume'].rolling(20).mean().iloc[-1]) > 0 else 1
            movers['gainers'].append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'change': round(change, 2), 'price': round(current, 2), 'volume_ratio': round(vol_ratio, 2)})
            movers['losers'].append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'change': round(change, 2), 'price': round(current, 2), 'volume_ratio': round(vol_ratio, 2)})
            movers['most_active'].append({'symbol': sym, 'name': STOCK_NAMES.get(sym, sym), 'change': round(change, 2), 'volume_ratio': round(vol_ratio, 2)})
        except: continue
    movers['gainers'].sort(key=lambda x: x['change'], reverse=True)
    movers['losers'].sort(key=lambda x: x['change'])
    movers['most_active'].sort(key=lambda x: x['volume_ratio'], reverse=True)
    return movers

def analyze_sectors():
    sectors = {
        '2222.SR': 'الطاقة (أرامكو)', '1120.SR': 'البنوك (الراجحي)', '2010.SR': 'البتروكيماويات (سابك)',
        '7010.SR': 'الاتصالات (STC)', '2280.SR': 'الزراعة (المراعي)', '2090.SR': 'التجزئة (جرير)',
        '2380.SR': 'التعدين (معادن)', '4001.SR': 'العقارات (دار الأركان)', '1180.SR': 'البنوك (الأهلي)',
        '1150.SR': 'البنوك (الإنماء)'
    }
    results = []
    for symbol, name in sectors.items():
        try:
            t = yf.Ticker(symbol)
            data = t.history(period='5d')
            if len(data) >= 2:
                current = float(data['Close'].iloc[-1])
                prev = float(data['Close'].iloc[-2])
                change = ((current - prev) / prev) * 100
                week_data = t.history(period='7d')
                week_change = ((current - float(week_data['Close'].iloc[0])) / float(week_data['Close'].iloc[0])) * 100 if len(week_data) >= 2 else change
                results.append({'symbol': symbol, 'name': name, 'change': round(change, 2), 'week_change': round(week_change, 2), 'price': round(current, 2)})
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
        elif rsi < rsi_th + 10: score += 1; reasons.append(f" RSI منخفض ({rsi:.1f})")
        if price > sma: score += 1; reasons.append("📈 السعر فوق المتوسط")
        else: reasons.append("📉 السعر تحت المتوسط")
        if macd > 0: score += 1; reasons.append("✅ MACD إيجابي")
        if vol_ratio > 1.5: score += 1; reasons.append(f"💪 حجم عالي ({vol_ratio:.1f}x)")
        if adx > 25: score += 1; reasons.append(f"💪 ADX قوي ({adx:.1f})")
        if obv: score += 1; reasons.append("🏦 تراكم OBV")
        if patterns: score += len(patterns); reasons.extend(patterns)
        bb = calculate_bollinger(data)
        if bb:
            if 'مباع زائد' in bb['signal'] or 'فرصة شراء' in bb['signal']:
                score += 1
                reasons.append(f"📊 {bb['signal']}")
        cross = detect_golden_death_cross(data)
        if cross:
            if cross['type'] == 'golden': score += 2; reasons.append(cross['signal'])
            elif cross['type'] == 'death': score -= 2; reasons.append(cross['signal'])
            else: reasons.append(cross['signal'])
        if score >= 6: rec, conf = "🌟 صفقة قوية جداً", "عالية جداً"
        elif score >= 5: rec, conf = "✅ شراء قوي", "عالية"
        elif score >= 4: rec, conf = "🟡 شراء", "متوسطة"
        elif score >= 3: rec, conf = "👀 مراقبة", "منخفضة"
        else: rec, conf = " تجنب", "ضعيفة"
        rr = round((t1 - price) / (price - sl), 2) if sl > 0 else 0
        return {'symbol': symbol, 'price': price, 'change': round(change, 2), 'rsi': round(rsi, 1), 'macd': round(macd, 2), 'adx': round(adx, 1), 'volume_ratio': round(vol_ratio, 2), 'score': score, 'recommendation': rec, 'confidence': conf, 'reasons': reasons, 'stop_loss': sl, 'target1': t1, 'target2': t2, 'pos_size': pos_size, 'total_inv': round(pos_size * price, 2), 'risk_amt': round(risk_amt, 2), 'best_times': analyze_best_times(symbol), 'best_days': analyze_best_days(symbol), 'risk_reward': rr, 'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%d %H'), 'bollinger': bb, 'cross': cross}
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
    msg = f"📊 <b>التقرير الأسبوعي - السوق السعودي</b>\n📅 الأسبوع المنتهي: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
    msg += f"━━━━━━━━━━━━━━━\n🧠 <b>أداء البوت:</b>\n• الدقة العامة: {settings['accuracy_score']*100}%\n• توقعات هذا الأسبوع: {len(week_predictions)}\n• إجمالي التوقعات: {settings['total_predictions']}\n• التوقعات الصحيحة: {settings['correct_predictions']}\n\n"
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
        msg += f"\n📉 <b>أسوأ 3 أسهم خاسرة:</b>\n"
        for m in movers['losers'][:3]: msg += f"🔴 {m['name']}: {m['change']:+.2f}%\n"
    msg += f"\n━━━━━━━━━━━━━━━\n💡 <b>التوصيات:</b>\n"
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
        if fg: return f"{fg['emoji']} <b>مؤشر الخوف والطمع:</b> {fg['score']}\n📊 الحالة: {fg['label']}\n💡 {fg['advice']}"
        return "❌ لا يمكن حساب المؤشر"
    if any(w in text_lower for w in ['تاسي', 'tasi', 'مؤشر السوق']):
        tasi = get_tasi_index()
        if tasi: return f"📊 <b>مؤشر تاسي (TASI):</b>\n💰 {tasi['price']}\n📈 {tasi['change']:+.2f}%"
        return "❌ لا بيانات"
    if any(w in text_lower for w in ['قطاعات', 'sectors', 'القطاعات']):
        sectors = analyze_sectors()
        if sectors:
            msg = "🏢 <b>أداء القطاعات اليوم:</b>\n\n"
            for s in sectors: msg += f"{'🟢' if s['change'] > 0 else '🔴'} <b>{s['name']}</b>: {s['change']:+.2f}%\n"
            return msg
        return "❌ لا بيانات"
    if any(w in text_lower for w in ['top movers', 'أفضل الأسهم', 'الرابحين', 'الأسهم النشطة']):
        movers = get_top_movers()
        msg = "🚀 <b>أفضل 5 أسهم رابحة:</b>\n\n"
        for m in movers['gainers'][:5]: msg += f" {m['name']}: {m['change']:+.2f}% ({m['price']} ر.س)\n"
        msg += f"\n <b>أسوأ 5 أسهم خاسرة:</b>\n\n"
        for m in movers['losers'][:5]: msg += f"🔴 {m['name']}: {m['change']:+.2f}% ({m['price']} ر.س)\n"
        return msg
    for stock in DEFAULT_STOCKS + ALL_SA_STOCKS:
        stock_code = stock.replace('.SR', '')
        if stock_code in text_lower or stock.lower() in text_lower:
            result = analyze_stock(stock, settings)
            if result:
                name = STOCK_NAMES.get(stock, stock)
                msg = f"📊 <b>تحليل {name} ({stock_code}):</b>\n\n💰 السعر: {result['price']} ر.س ({result['change']:+.2f}%)\n📈 RSI: {result['rsi']} | MACD: {result['macd']} | ADX: {result['adx']}\n🎯 {result['recommendation']} ({result['confidence']})\n⭐ النقاط: {result['score']}/10\n\n"
                msg += explain_recommendation(result) + "\n\n"
                msg += f"<b>💰 الخطة:</b>\n• العدد: {result['pos_size']} سهم\n• الاستثمار: {result['total_inv']} ر.س\n• المخاطرة: {result['risk_amt']} ر.س\n🛡️ SL: {result['stop_loss']} ر.س\n🎯 T1: {result['target1']} ر.س\n🎯 T2: {result['target2']} ر.س\n️ R/R: {result['risk_reward']}:1\n"
                if result.get('best_times'): msg += f"\n⏰ أفضل وقت: {result['best_times'][0][0]}:00 (+{result['best_times'][0][1]}%)\n"
                if result.get('best_days'): msg += f"📅 أفضل يوم: {result['best_days'][0][0]} (+{result['best_days'][0][1]}%)\n"
                if result.get('bollinger'):
                    bb = result['bollinger']
                    msg += f"\n📊 <b>Bollinger Bands:</b>\n• العلوي: {bb['upper']} ر.س\n• الأوسط: {bb['middle']} ر.س\n• السفلي: {bb['lower']} ر.س\n• %B: {bb['percent_b']}\n• الإشارة: {bb['signal']}\n"
                return msg
            return f" لا بيانات لـ {stock_code}"
    if any(w in text_lower for w in ['اسهم رخيصة', 'رخيصة', 'cheap', 'affordable', 'ميزانيتي', 'budget', 'أسهم مناسبة']):
        affordable = find_affordable_stocks(settings)
        if affordable:
            msg = f"💰 <b>أسهم لميزانيتك ({settings['capital']} ر.س):</b>\n\nيمكنك شراء 10 أسهم على الأقل:\n\n"
            for s in affordable: msg += f"📌 <b>{s['name']} ({s['symbol'].replace('.SR', '')})</b>\n💰 {s['price']} ر.س ({s['change']:+.2f}%)\n📊 RSI: {s['rsi']}\n🔢 {s['position_size']} سهم\n💵 {s['total_investment']} ر.س\n\n"
            return msg
        return "❌ لا أسهم مناسبة"
    if any(w in text_lower for w in ['اخبار', 'news', 'أخبار السوق']):
        news = get_daily_news()
        if news:
            msg = "📰 <b>آخر أخبار السوق السعودي:</b>\n\n"
            for item in news[:5]: msg += f"📌 <b>{STOCK_NAMES.get(item['symbol'], item['symbol'])} ({item['symbol'].replace('.SR', '')}):</b> {item['title']}\n📰 {item['publisher']} |  {item['time']}\n\n"
            return msg
        return "📰 لا أخبار"
    if any(w in text_lower for w in ['vix', 'الخوف', 'مؤشر الخوف']):
        vix = get_vix()
        if vix: return f"😱 <b>VIX (مؤشر الخوف العالمي):</b> {vix['emoji']} {vix['value']} - {vix['level']}"
        return "❌ لا VIX"
    if any(w in text_lower for w in ['rsi', 'ما هو rsi', 'شرح rsi']):
        return "📊 <b>مؤشر RSI:</b>\n📉 <30: مباع زائد (فرصة شراء)\n📈 >70: مشتري زائد (قد ينخفض)\n⚖️ 30-70: منطقة محايدة\n\n🤖 البوت يستخدم RSI < 35 كإشارة شراء."
    if any(w in text_lower for w in ['مرحبا', 'هلا', 'hi', 'hello', 'السلام']):
        return "👋 أهلاً! 🇸🇦 بوت تحليل الأسهم السعودية (تداول)\n\nيمكنني:\n• تحليل أي سهم سعودي\n• تتبع محفظتك\n• تنبيهات الأسعار\n• مؤشر تاسي والخوف والطمع\n\nجرب: 2222 (أرامكو), 1120 (الراجحي), /help"
    if any(w in text_lower for w in ['شكر', 'thanks', 'ممتاز', 'جزاك']):
        return "😊 العفو! هل تريد تحليل سهم أو لديك سؤال آخر؟"
    if any(w in text_lower for w in ['دقة', 'accuracy', 'اداء', 'أداء']):
        return f"🎯 <b>أداء البوت:</b>\n🎯 الدقة: {settings['accuracy_score']*100}%\n✅ {settings['correct_predictions']}/{settings['total_predictions']}\n⚙️ RSI: {settings['rsi_threshold']}"
    return "🤔 لم أفهم تماماً.\n\nجرب:\n• رمز سهم: 2222, 1120, 2010\n• أسهم رخيصة\n• حالة السوق\n• تاسي\n• /help للأوامر"

def process_message(text, settings):
    text_lower = text.lower().strip()
    if text == '/settings':
        msg = f"⚙️ <b>إعدادات البوت - السوق السعودي:</b>\n💰 الميزانية: {settings['capital']} ر.س\n⚠️ المخاطرة: {settings['risk_percent']}%\n RSI: {settings['rsi_threshold']}\n🎯 الدقة: {settings['accuracy_score']*100}%\n📊 {settings['total_predictions']} توقع\n✅ {settings['correct_predictions']} صحيح\n\n<b>🧠 أنماط الأخطاء:</b>\n• RSI مرتفع: {settings['mistake_patterns'].get('high_rsi', 0)}\n• حجم منخفض: {settings['mistake_patterns'].get('low_volume', 0)}\n• اتجاه ضعيف: {settings['mistake_patterns'].get('weak_trend', 0)}\n• MACD خاطئ: {settings['mistake_patterns'].get('wrong_macd', 0)}"
        send_telegram(msg)
    elif text == '/help':
        msg = " <b>أوامر البوت - السوق السعودي 🇸🇦</b>\n\n📋 <b>الأساسية:</b>\n/settings - الإعدادات\n/status - حالة التعلم\n/stock [رمز] - تحليل سهم (مثال: /stock 2222)\n/affordable - أسهم لميزانيتك\n/news - أخبار السوق\n/vix - مؤشر الخوف العالمي\n/learn - مراجعة ذاتية\n\n💰 <b>الميزانية:</b>\n/capital [مبلغ] (مثال: /capital 50000)\n\n📌 <b>قائمة المراقبة:</b>\n/watchlist - عرض القائمة\n/watchlist add 2222 - إضافة سهم\n/watchlist remove 2222 - حذف سهم\n\n🔔 <b>التنبيهات:</b>\n/alert 2222 35 above - تنبيه فوق السعر\n/alert 1120 80 below - تنبيه تحت السعر\n/alerts - عرض التنبيهات\n/delalert 2222 - حذف التنبيه\n\n💼 <b>المحفظة:</b>\n/buy 2222 10 35 - شراء 10 أسهم بسعر 35\n/sell 2222 5 40 - بيع 5 أسهم بسعر 40\n/portfolio - ملخص المحفظة\n/update 2222 35.5 - تحديث سعر الدخول\n/export - تصدير تقرير المحفظة\n\n📊 <b>التحليل المتقدم:</b>\n/risk 2222 35 33 40 - حاسبة المخاطرة\n/weekly - التقرير الأسبوعي\n\n💬 <b>محادثة:</b>\nاكتب: 2222, 1120, تاسي, حالة السوق, أسهم رخيصة"
        send_telegram(msg)
    elif text == '/vix':
        vix = get_vix()
        if vix: send_telegram(f"😱 <b>VIX (مؤشر الخوف العالمي):</b> {vix['emoji']} {vix['value']} - {vix['level']}")
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
            msg = f"📊 <b>{name} ({code}):</b>\n💰 {result['price']} ر.س ({result['change']:+.2f}%)\n📈 RSI: {result['rsi']} | MACD: {result['macd']} | ADX: {result['adx']}\n🎯 {result['recommendation']} ({result['confidence']})\n⭐ {result['score']}/10\n\n"
            msg += explain_recommendation(result) + "\n\n"
            msg += f"<b>💰 الخطة:</b>\n• {result['pos_size']} سهم\n• {result['total_inv']} ر.س\n• مخاطرة: {result['risk_amt']} ر.س\n️ SL: {result['stop_loss']} ر.س\n🎯 T1: {result['target1']} ر.س\n🎯 T2: {result['target2']} ر.س\n️ R/R: {result['risk_reward']}:1\n"
            if result.get('best_times'): msg += f"\n⏰ {result['best_times'][0][0]}:00 (+{result['best_times'][0][1]}%)\n"
            if result.get('best_days'): msg += f"📅 {result['best_days'][0][0]} (+{result['best_days'][0][1]}%)\n"
            if result.get('bollinger'):
                bb = result['bollinger']
                msg += f"\n📊 <b>Bollinger Bands:</b>\n• العلوي: {bb['upper']} ر.س\n• الأوسط: {bb['middle']} ر.س\n• السفلي: {bb['lower']} ر.س\n• %B: {bb['percent_b']}\n• الإشارة: {bb['signal']}\n"
            if result.get('cross'): msg += f"\n{result['cross']['signal']}\n"
            send_telegram(msg)
        else: send_telegram(f" لا بيانات لـ {sym.replace('.SR', '')}")
    elif text == '/affordable':
        send_telegram("⏳ جاري البحث...")
        affordable = find_affordable_stocks(settings)
        if affordable:
            msg = f"💰 <b>أسهم لميزانيتك ({settings['capital']} ر.س):</b>\n\nيمكنك شراء 10 أسهم على الأقل:\n\n"
            for s in affordable: msg += f"📌 <b>{s['name']} ({s['symbol'].replace('.SR', '')})</b>\n💰 {s['price']} ر.س ({s['change']:+.2f}%)\n RSI: {s['rsi']}\n🔢 {s['position_size']} سهم\n💵 {s['total_investment']} ر.س\n\n"
            send_telegram(msg)
        else: send_telegram("❌ لا أسهم مناسبة")
    elif text == '/status':
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        preds = len([p for p in load_json(LEARNING_FILE, {'predictions': []}).get('predictions', []) if p.get('date') == today])
        send_telegram(f" <b>حالة التعلم:</b>\n الدقة: {settings['accuracy_score']*100}%\n⚙️ RSI: {settings['rsi_threshold']}\n📝 اليوم: {preds} توقع\n💡 يتعلم كل ساعة!")
    elif text == '/watchlist':
        watchlist = get_watchlist()
        msg = f"📌 <b>قائمة المراقبة ({len(watchlist)} سهم):</b>\n\n"
        for sym in watchlist: msg += f"• {STOCK_NAMES.get(sym, sym)} ({sym.replace('.SR', '')})\n"
        msg += f"\n<b>إدارة القائمة:</b>\n• إضافة: /watchlist add 2222\n• حذف: /watchlist remove 2222"
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
                alert_type = parts[3].lower()
                if alert_type in ['above', 'فوق', 'up']: alert_type = 'above'
                elif alert_type in ['below', 'تحت', 'down']: alert_type = 'below'
                else: send_telegram("❌ النوع يجب أن يكون 'above' أو 'below'"); return
                success, msg = add_price_alert(symbol, target, alert_type)
                send_telegram(msg)
            except: send_telegram("❌ استخدام: /alert 2222 35 above")
        else: send_telegram("❌ استخدام: /alert [رمز] [السعر] [above/below]\nمثال: /alert 2222 35 above")
    elif text_lower == '/alerts':
        data = get_alerts()
        if not data.get('alerts'): send_telegram("📭 لا توجد تنبيهات")
        else:
            msg = "🔔 <b>التنبيهات النشطة:</b>\n\n"
            for alert in data['alerts']:
                if not alert.get('triggered'):
                    name = STOCK_NAMES.get(alert['symbol'], alert['symbol'])
                    type_ar = 'فوق' if alert['type'] == 'above' else 'تحت'
                    msg += f" {name} ({alert['symbol'].replace('.SR', '')}) {type_ar} {alert['target']} ر.س\n"
            msg += f"\n💡 استخدام: /delalert 2222 لحذف التنبيه"
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
        except: send_telegram(" استخدام: /risk 2222 35 33 40\n(رمز، دخول، وقف، هدف)")
    elif text_lower == '/weekly' or any(w in text_lower for w in ['تقرير أسبوعي', 'weekly report']):
        send_telegram("⏳ جاري إنشاء التقرير الأسبوعي...")
        send_telegram(generate_weekly_report())
    elif text and not text.startswith('/'):
        resp = handle_chat(text)
        if resp: send_telegram(resp)

# ✅ الحل النهائي: معالجة الأوامر مع تجاهل رسائل البوت نفسه
def handle_commands():
    print(" بدء معالجة الأوامر...")
    
    # الحصول على Bot ID
    bot_info = get_bot_info()
    bot_id = bot_info['id'] if bot_info else None
    print(f"🤖 Bot ID: {bot_id}")
    
    last_id = get_last_processed_id()
    print(f"📋 آخر ID معالج: {last_id}")
    
    url_base = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    
    try:
        # قراءة التحديثات الجديدة فقط
        response = requests.get(f"{url_base}/getUpdates?offset={last_id + 1}&limit=100&timeout=5", timeout=10).json()
        
        if not response.get('ok'):
            print("❌ فشل الاتصال بـ Telegram")
            return
        
        updates = response.get('result', [])
        print(f"📨 عدد التحديثات: {len(updates)}")
        
        if not updates:
            print("📭 لا توجد رسائل جديدة")
            return
        
        settings = get_settings()
        processed = 0
        skipped_bot = 0
        skipped_other = 0
        max_id = last_id
        
        for update in updates:
            update_id = update['update_id']
            if update_id > max_id:
                max_id = update_id
            
            message = update.get('message', {})
            if not message:
                continue
            
            # 🔑 تجاهل رسائل البوت نفسه
            sender = message.get('from', {})
            if sender.get('is_bot', False) or (bot_id and sender.get('id') == bot_id):
                print(f"🤖 تخطي رسالة من البوت (ID: {update_id})")
                skipped_bot += 1
                continue
            
            text = message.get('text', '').strip()
            chat_id = str(message.get('chat', {}).get('id', ''))
            
            print(f"💬 رسالة من {chat_id}: {text[:50]}")
            
            if chat_id != CHAT_ID:
                print(f"️ Chat ID غير مطابق: {chat_id}")
                skipped_other += 1
                continue
            
            try:
                process_message(text, settings)
                processed += 1
                print(f"✅ تمت معالجة الرسالة {update_id}")
            except Exception as e:
                print(f"❌ خطأ في معالجة الرسالة: {e}")
        
        # حفظ آخر update_id
        save_last_processed_id(max_id)
        print(f"✅ تمت معالجة {processed} رسالة، تخطي {skipped_bot} بوت، {skipped_other} أخرى")
        print(f"✅ آخر ID: {max_id}")
        
    except Exception as e:
        print(f" خطأ في handle_commands: {e}")

def run_scan():
    print("🎯 بدء فحص السوق السعودي...")
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
        msg = f"📊 <b>فحص السوق السعودي 🇸🇦</b>\n {time_info['saudi']}\n الدقة: {settings['accuracy_score']*100}% | RSI: {settings['rsi_threshold']}\n💰 الميزانية: {settings['capital']} ر.س\n\n"
        if tasi: msg += f"📈 <b>مؤشر تاسي (TASI):</b> {tasi['price']} ({tasi['change']:+.2f}%)\n"
        if vix: msg += f"😱 VIX العالمي: {vix['emoji']} {vix['value']} - {vix['level']}\n"
        msg += f"\n<b>🏆 أفضل 3 فرص:</b>\n\n"
        for r in results[:3]:
            name = STOCK_NAMES.get(r['symbol'], r['symbol'])
            code = r['symbol'].replace('.SR', '')
            msg += f"📌 <b>{name} ({code})</b> ({r['change']:+.2f}%)\n💰 {r['price']} ر.س | RSI: {r['rsi']} | ADX: {r['adx']}\n{r['recommendation']} ({r['score']} نقاط)\n📝 {', '.join(r['reasons'])}\n🛡️ SL: {r['stop_loss']} ر.س | T1: {r['target1']} ر.س | T2: {r['target2']} ر.س\n⚖️ R/R: {r['risk_reward']}:1\n\n"
            msg += explain_recommendation(r) + "\n\n"
            if r.get('best_times'): msg += f"⏰ {r['best_times'][0][0]}:00 (+{r['best_times'][0][1]}%)\n"
            if r.get('best_days'): msg += f"📅 {r['best_days'][0][0]} (+{r['best_days'][0][1]}%)\n\n"
        if strong:
            msg += f"\n <b>فرص قوية جداً!</b>\n\n"
            for r in strong:
                name = STOCK_NAMES.get(r['symbol'], r['symbol'])
                code = r['symbol'].replace('.SR', '')
                msg += f"🔥 <b>{name} ({code})</b> - {r['recommendation']}\n💰 {r['price']} ر.س | RSI: {r['rsi']}\n⭐ {r['score']}/10\n🛡️ SL: {r['stop_loss']} ر.س | T1: {r['target1']} ر.س | T2: {r['target2']} ر.س\n⚖️ R/R: {r['risk_reward']}:1\n\n"
                msg += explain_recommendation(r) + "\n\n"
                if r.get('best_times'): msg += f"⏰ {r['best_times'][0][0]}:00\n"
                if r.get('best_days'): msg += f"📅 {r['best_days'][0][0]}\n"
                msg += f"💰 {r['pos_size']} سهم ({r['total_inv']} ر.س)\n\n"
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
