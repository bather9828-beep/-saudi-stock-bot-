import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import json
import time
import warnings
from datetime import datetime, timedelta, timezone
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8945885655:AAGRrJHgsIL9f62ZuXJcmyCKyHVI-fNF2VU')
CHAT_ID = os.environ.get('CHAT_ID', '208377256')

DEFAULT_STOCKS = ['2222.SR', '1120.SR', '2010.SR', '1180.SR', '7010.SR', '2030.SR', '1150.SR', '2380.SR', '2280.SR', '2090.SR']

STOCK_NAMES = {
    '2222.SR': 'أرامكو', '1120.SR': 'الراجحي', '2010.SR': 'سابك',
    '1180.SR': 'الأهلي', '7010.SR': 'STC', '2030.SR': 'سابك للمغذيات',
    '1150.SR': 'الإنماء', '2380.SR': 'معادن', '2280.SR': 'المراعي', '2090.SR': 'جرير'
}

PROCESSED_FILE = 'processed_messages.json'
SETTINGS_FILE = 'bot_settings.json'

def load_json(fn, default=None):
    if default is None: default = {}
    try:
        with open(fn, 'r', encoding='utf-8') as f: return json.load(f)
    except: return default

def save_json(fn, data):
    with open(fn, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)

def get_settings():
    defaults = {'capital': 50000, 'risk_percent': 2.0, 'rsi_threshold': 35}
    settings = load_json(SETTINGS_FILE, defaults)
    for key in defaults:
        if key not in settings: settings[key] = defaults[key]
    return settings

def send_telegram(msg, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": parse_mode}, timeout=10)
        return True
    except: return False

def get_bot_id():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
        response = requests.get(url, timeout=5).json()
        if response.get('ok'): return response['result']['id']
    except: pass
    return None

# ✅ الحل: حفظ قائمة كاملة من الرسائل المعالجة
def get_processed_ids():
    data = load_json(PROCESSED_FILE, {'processed': [], 'date': ''})
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if data.get('date') != today:
        data = {'processed': [], 'date': today}
        save_json(PROCESSED_FILE, data)
    return data.get('processed', [])

def add_processed_id(update_id):
    data = load_json(PROCESSED_FILE, {'processed': [], 'date': ''})
    if update_id not in data['processed']:
        data['processed'].append(update_id)
        if len(data['processed']) > 1000:
            data['processed'] = data['processed'][-500:]
        save_json(PROCESSED_FILE, data)

def analyze_stock(symbol):
    try:
        data = yf.Ticker(symbol).history(period='1mo', interval='1d')
        if len(data) < 20: return None
        price = float(data['Close'].iloc[-1])
        prev = float(data['Close'].iloc[-2])
        change = ((price - prev) / prev) * 100
        return {'symbol': symbol, 'price': round(price, 2), 'change': round(change, 2)}
    except: return None

def handle_commands():
    print("💬 بدء معالجة الأوامر...")
    bot_id = get_bot_id()
    print(f"🤖 Bot ID: {bot_id}")
    
    # ✅ قراءة كل الرسائل (offset=0)
    processed_ids = get_processed_ids()
    print(f"📋 عدد الرسائل المعالجة: {len(processed_ids)}")
    
    url_base = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    
    try:
        # قراءة آخر 100 رسالة
        url = f"{url_base}/getUpdates?offset=0&limit=100&timeout=5"
        print(f"📡 الاتصال...")
        response = requests.get(url, timeout=10).json()
        
        if not response.get('ok'):
            print("❌ فشل الاتصال")
            return
        
        updates = response.get('result', [])
        print(f"📨 عدد التحديثات: {len(updates)}")
        
        if not updates:
            print("📭 لا رسائل")
            return
        
        settings = get_settings()
        processed = 0
        skipped = 0
        
        for update in updates:
            update_id = update['update_id']
            
            # تخطي الرسائل المعالجة مسبقاً
            if update_id in processed_ids:
                continue
            
            message = update.get('message', {})
            if not message:
                add_processed_id(update_id)
                continue
            
            # تجاهل رسائل البوت نفسه
            sender = message.get('from', {})
            if sender.get('is_bot', False) or (bot_id and sender.get('id') == bot_id):
                print(f"🤖 تخطي رسالة من البوت")
                add_processed_id(update_id)
                skipped += 1
                continue
            
            text = message.get('text', '').strip()
            chat_id = str(message.get('chat', {}).get('id', ''))
            
            print(f"💬 رسالة: {text[:50]}")
            
            if chat_id != CHAT_ID:
                print(f"⚠️ Chat ID غير مطابق")
                add_processed_id(update_id)
                skipped += 1
                continue
            
            # الرد على الرسالة
            if text == '/help':
                send_telegram(" <b>أوامر البوت:</b>\n/help - الأوامر\n/stock 2222 - تحليل سهم\n/settings - الإعدادات")
            elif text.startswith('/stock '):
                sym = text.split()[1].upper()
                if not sym.endswith('.SR'): sym = sym + '.SR'
                result = analyze_stock(sym)
                if result:
                    name = STOCK_NAMES.get(result['symbol'], result['symbol'])
                    send_telegram(f"📊 <b>{name} ({result['symbol'].replace('.SR', '')}):</b>\n💰 {result['price']} ر.س\n {result['change']:+.2f}%")
                else:
                    send_telegram(f"❌ لا بيانات لـ {sym}")
            elif text == '/settings':
                settings = get_settings()
                send_telegram(f"⚙️ <b>الإعدادات:</b>\n💰 الميزانية: {settings['capital']} ر.س\n⚠️ المخاطرة: {settings['risk_percent']}%\n🧠 RSI: {settings['rsi_threshold']}")
            else:
                send_telegram(f"🤔 لم أفهم. جرب: /help")
            
            add_processed_id(update_id)
            processed += 1
            print(f"✅ تمت المعالجة: {update_id}")
        
        print(f"✅ تمت معالجة {processed}، تخطي {skipped}")
        
    except Exception as e:
        print(f" خطأ: {e}")

def run_scan():
    print("🎯 بدء الفحص...")
    settings = get_settings()
    
    msg = f"📊 <b>فحص السوق السعودي 🇦</b>\n"
    msg += f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n"
    msg += f" الميزانية: {settings['capital']} ر.س\n\n"
    
    results = []
    for sym in DEFAULT_STOCKS:
        result = analyze_stock(sym)
        if result:
            results.append(result)
    
    if results:
        results.sort(key=lambda x: x['change'], reverse=True)
        msg += f"<b>🏆 أفضل 3:</b>\n\n"
        for r in results[:3]:
            name = STOCK_NAMES.get(r['symbol'], r['symbol'])
            msg += f"📌 <b>{name} ({r['symbol'].replace('.SR', '')})</b>\n"
            msg += f"💰 {r['price']} ر.س ({r['change']:+.2f}%)\n\n"
        
        send_telegram(msg)
        print(f"✅ تم إرسال التقرير")
    else:
        print("❌ لا بيانات")

if __name__ == '__main__':
    print("🚀 بدء البوت...")
    print("1️⃣ الأوامر...")
    handle_commands()
    print("2️⃣ الفحص...")
    run_scan()
    print("✅ انتهى")
