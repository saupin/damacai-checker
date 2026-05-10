"""
Lottery Win Checker with Telegram Alert
Checks if a number won in recent draws and sends alert via Telegram

Usage:
    python check_win.py <LOTTERY> <NUMBER> <TIMES>
    
    LOTTERY: damacai, toto, or magnum (or d, t, m)
    NUMBER:  4-digit number (e.g., 4444)
    TIMES:   Number of recent draws to check (e.g., 10)
    
Example:
    python check_win.py damacai 4444 10
    python check_win.py toto 9999 5
    python check_win.py magnum 1234 20
"""

import sys
import os
import json
from datetime import datetime

WORKSPACE = r'C:\Users\samul\.openclaw\workspace\damacai-checker'
sys.path.insert(0, WORKSPACE)

# Telegram config
BOT_TOKEN = '8752373556:AAG0ucYHgQ7pchVoHuR8K9eOtxcbXqQPkos'
CHAT_ID = None  # Will be auto-detected on first run

def load_json(filename):
    path = os.path.join(WORKSPACE, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def get_lottery_key(lottery):
    """Map lottery name to data key"""
    mapping = {
        'damacai': 'damacai', 'dama': 'damacai', 'd': 'damacai',
        'toto': 'toto', 't': 'toto',
        'magnum': 'magnum', 'm': 'magnum'
    }
    return mapping.get(lottery.lower())

def check_number_in_draws(number, draws, lottery_key):
    """Check if number won in any of the draws"""
    wins = []
    for draw in draws:
        data = draw.get(lottery_key, {})
        if not data:
            continue
        
        prize_won = None
        prize_type = None
        
        n1 = data.get('1st')
        n2 = data.get('2nd')
        n3 = data.get('3rd')
        
        if n1 == number:
            prize_won = n1
            prize_type = '1st Prize'
        elif n2 == number:
            prize_won = n2
            prize_type = '2nd Prize'
        elif isinstance(n3, list):
            if number in n3:
                prize_won = number
                prize_type = '3rd Prize'
        elif n3 == number:
            prize_won = n3
            prize_type = '3rd Prize'
        
        if prize_won:
            wins.append({
                'date': draw['date'],
                'prize': prize_type,
                'number': prize_won
            })
    
    return wins

def send_telegram_message(message):
    """Send message via Telegram bot"""
    import urllib.request
    import urllib.parse
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    })
    
    req = urllib.request.Request(url, data=data.encode(), method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get('ok', False)
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

def get_chat_id():
    """Get chat ID from bot updates"""
    import urllib.request
    import json
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode())
            if result.get('ok') and result.get('result'):
                return result['result'][0]['message']['chat']['id']
    except:
        pass
    return None

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    lottery = sys.argv[1]
    number = sys.argv[2]
    times = int(sys.argv[3])
    
    # Validate number
    if not number.isdigit() or len(number) != 4:
        print("Error: Number must be 4 digits")
        sys.exit(1)
    
    # Get lottery key
    lottery_key = get_lottery_key(lottery)
    if not lottery_key:
        print("Error: Lottery must be damacai, toto, or magnum")
        sys.exit(1)
    
    # Load data
    data_file = f"{lottery_key}_full.json"
    data = load_json(data_file)
    
    if not data or not data.get('draws'):
        print(f"No data found for {lottery_key}")
        sys.exit(1)
    
    draws = data['draws']
    
    # Take only last X draws
    draws_to_check = draws[:times]
    
    print(f"Checking {number} in {lottery_key.upper()} - Last {len(draws_to_check)} draws...")
    print(f"Date range: {draws_to_check[-1]['date']} to {draws_to_check[0]['date']}")
    print()
    
    # Check for wins
    wins = check_number_in_draws(number, draws_to_check, lottery_key)
    
    if wins:
        print(f"*** WINNER! ***")
        for win in wins:
            print(f"  {win['date']} - {win['prize']} - Number: {win['number']}")
        
        # Prepare Telegram message
        msg = f"🎉 *WINNER ALERT!*\n\n"
        msg += f"Number: *{number}*\n"
        msg += f"Lottery: {lottery_key.upper()}\n\n"
        for win in wins:
            msg += f"📅 {win['date']} - {win['prize']}\n"
        
        # Auto-detect chat ID if not set
        global CHAT_ID
        if CHAT_ID is None:
            CHAT_ID = get_chat_id()
            if CHAT_ID is None:
                print("Could not detect chat ID. Make sure you've sent a message to the bot first.")
                print("Alert message:")
                print(msg)
                return
        
        print(f"\nSending Telegram alert...")
        if send_telegram_message(msg):
            print("Alert sent!")
        else:
            print("Failed to send alert")
    else:
        print(f"No wins in last {len(draws_to_check)} draws")
        print(f"Last draw checked: {draws_to_check[0]['date']}")
        
        # Show what the 1st prize was in last few draws
        print(f"\nLast 3 draws 1st prize:")
        for d in draws_to_check[:3]:
            data = d.get(lottery_key, {})
            if data:
                print(f"  {d['date']}: {data.get('1st', 'N/A')}")

if __name__ == "__main__":
    main()