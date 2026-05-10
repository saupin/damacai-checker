"""
Scheduled Lottery Checker
Runs after each draw to update DB and alert if you win

Usage:
    python check_scheduled.py
    
Add to Windows Task Scheduler to run on:
    - Tuesday 9:00 PM (special draws)
    - Wednesday 9:00 PM
    - Saturday 9:00 PM
    - Sunday 9:00 PM

Or run manually anytime to check latest draws
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime

WORKSPACE = r'C:\Users\samul\.openclaw\workspace\damacai-checker'
sys.path.insert(0, WORKSPACE)

BOT_TOKEN = '8752373556:AAG0ucYHgQ7pchVoHuR8K9eOtxcbXqQPkos'
BASE_URL = "https://www.4dmoon.com/past-results/"

def load_json(filename):
    path = os.path.join(WORKSPACE, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_json(data, filename):
    path = os.path.join(WORKSPACE, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Fetch error: {e}")
        return None

def parse_damacai(html, date):
    import re
    result = {'date': date, 'damacai': {'1st': None, '2nd': None, '3rd': None}}
    rtn = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', html)
    if rtn:
        result['damacai']['1st'] = rtn.group(1)
        result['damacai']['2nd'] = rtn.group(2)
        result['damacai']['3rd'] = rtn.group(3)
        return result
    return None

def parse_toto(html, date):
    import re
    result = {'date': date, 'toto': {'1st': None, '2nd': None, '3rd': None}}
    toto_match = re.search(r'SportsToto 4D([\s\S]*?)(?=Magnum|Damacai|$)', html)
    if toto_match:
        section = toto_match.group(1)
        rtn = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
        if rtn:
            result['toto']['1st'] = rtn.group(1)
            result['toto']['2nd'] = rtn.group(2)
            result['toto']['3rd'] = rtn.group(3)
            return result
    return None

def parse_magnum(html, date):
    import re
    result = {'date': date, 'magnum': {'1st': None, '2nd': None, '3rd': None}}
    start = html.find('Magnum 4D<br>')
    if start != -1:
        end = html.find('SportsToto 4D<br>')
        section = html[start:end] if end > 0 else html[start:start+5000]
        rtn = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
        if rtn:
            result['magnum']['1st'] = rtn.group(1)
            result['magnum']['2nd'] = rtn.group(2)
            result['magnum']['3rd'] = rtn.group(3)
            return result
    return None

def check_number_in_draw(number, draw_data):
    """Check if number won in draw"""
    for lottery in ['damacai', 'toto', 'magnum']:
        data = draw_data.get(lottery, {})
        if not data:
            continue
        for prize in ['1st', '2nd', '3rd']:
            if data.get(prize) == number:
                return lottery, prize, data[prize]
    return None, None, None

def send_telegram(msg):
    """Send alert via Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        'chat_id': CHAT_ID,
        'text': msg,
        'parse_mode': 'Markdown'
    })
    try:
        req = urllib.request.Request(url, data=data.encode(), method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode()).get('ok')
    except:
        return False

def main():
    global CHAT_ID
    
    print("\n=== SCHEDULED LOTTERY CHECK ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load your numbers
    config = load_json('my_numbers.json')
    if not config:
        print("No my_numbers.json found!")
        return
    
    numbers = config.get('numbers', [])
    CHAT_ID = config.get('chat_id')
    
    if not numbers:
        print("No numbers to check!")
        return
    
    if not CHAT_ID:
        print("No chat_id configured in my_numbers.json!")
        return
    
    print(f"Monitoring {len(numbers)} numbers...")
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\nScraping {today}...")
    
    html = fetch(f"{BASE_URL}{today}")
    if not html:
        print("No results yet for today")
        return
    
    # Parse all 3 lotteries
    draws = []
    d = parse_damacai(html, today)
    if d:
        draws.append(d)
        print(f"  Damacai: {d['damacai']['1st']}")
    t = parse_toto(html, today)
    if t:
        draws.append(t)
        print(f"  Toto: {t['toto']['1st']}")
    m = parse_magnum(html, today)
    if m:
        draws.append(m)
        print(f"  Magnum: {m['magnum']['1st']}")
    
    if not draws:
        print("No draws found for today")
        return
    
    # Update databases
    for draw in draws:
        lottery = list(draw.keys())[1]  # 'damacai', 'toto', or 'magnum'
        data = load_json(f"{lottery}_full.json")
        if not data:
            continue
        
        existing_dates = {d['date'] for d in data.get('draws', [])}
        if today not in existing_dates:
            data['draws'].insert(0, draw)
            save_json(data, f"{lottery}_full.json")
            print(f"  Updated {lottery} database")
    
    # Check each number (expand ranges)
    wins = []
    for item in numbers:
        num = item['num']
        active_lotteries = item.get('lotteries', ['damacai', 'toto', 'magnum'])
        
        # Expand range if needed
        if '-' in num and 'is_range' in item:
            try:
                start, end = num.split('-')
                start, end = int(start), int(end)
                check_nums = [f"{i:04d}" for i in range(start, end + 1)]
            except:
                check_nums = [num]
        else:
            check_nums = [num]
        
        for number in check_nums:
            for draw in draws:
                lottery = list(draw.keys())[1]
                if lottery not in active_lotteries:
                    continue
                
                lot, prize, won_num = check_number_in_draw(number, draw)
                if won_num:
                    wins.append(f"{number} won {prize} in {lot.upper()} on {today}! Number: {won_num}")
    
    # Send alerts
    if wins:
        msg = "🎉 *LOTTERY WINNER!*\n\n"
        for w in wins:
            msg += f"{w}\n"
        print(f"\n*** WINNERS! ***\n{msg}")
        send_telegram(msg)
    else:
        print(f"\nNo wins today. Better luck next draw!")
        send_telegram(f"No wins today. Checked {len(numbers)} numbers in {len(draws)} draws.")

if __name__ == "__main__":
    CHAT_ID = None  # Will be loaded from config
    main()