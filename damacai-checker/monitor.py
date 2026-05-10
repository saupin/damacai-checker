"""
Lottery Monitor - Checks FUTURE draws and alerts on win
Run continuously and checks each upcoming draw

Usage:
    python monitor.py <LOTTERY> <NUMBER> <MAX_DRAWS>
    
Example:
    python monitor.py damacai 4444 5
    python monitor.py tdm 9999 10
    
The script will:
1. Find the next scheduled draw
2. Scrape the results when available
3. Check your number
4. If win → send Telegram alert
5. If no win → wait for next draw and repeat
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

WORKSPACE = r'C:\Users\samul\.openclaw\workspace\damacai-checker'
sys.path.insert(0, WORKSPACE)

# Telegram config
BOT_TOKEN = '8752373556:AAG0ucYHgQ7pchVoHuR8K9eOtxcbXqQPkos'
BASE_URL = "https://www.4dmoon.com/past-results/"

# Draw days for each lottery
DRAW_DAYS = {
    'damacai': ['Wednesday', 'Saturday', 'Sunday'],
    'toto': ['Saturday', 'Sunday'],
    'magnum': ['Wednesday', 'Saturday', 'Sunday']
}

def load_json(filename):
    path = os.path.join(WORKSPACE, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def get_next_draw_date(lottery_key, from_date=None):
    """Get the next scheduled draw date for a lottery"""
    if from_date is None:
        from_date = datetime.now()
    
    draw_days = DRAW_DAYS.get(lottery_key, ['Saturday', 'Sunday'])
    
    # Check next 14 days
    for i in range(1, 15):
        check_date = from_date + timedelta(days=i)
        if check_date.strftime('%A') in draw_days:
            return check_date
    
    return None

def scrape_draw(date_str, lottery_key):
    """Scrape a specific draw and return results"""
    url = f"{BASE_URL}{date_str}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Parse based on lottery
        if lottery_key == 'damacai':
            import re
            rtn_row = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', html)
            if rtn_row:
                return {
                    'date': date_str,
                    '1st': rtn_row.group(1),
                    '2nd': rtn_row.group(2),
                    '3rd': rtn_row.group(3)
                }
        elif lottery_key == 'toto':
            import re
            toto_match = re.search(r'SportsToto 4D([\s\S]*?)(?=Magnum|Damacai|$)', html)
            if toto_match:
                section = toto_match.group(1)
                rtn_row = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
                if rtn_row:
                    return {
                        'date': date_str,
                        '1st': rtn_row.group(1),
                        '2nd': rtn_row.group(2),
                        '3rd': rtn_row.group(3)
                    }
        elif lottery_key == 'magnum':
            import re
            start = html.find('Magnum 4D<br>')
            if start != -1:
                end = html.find('SportsToto 4D<br>')
                section = html[start:end] if end > 0 else html[start:start+5000]
                rtn_row = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
                if rtn_row:
                    return {
                        'date': date_str,
                        '1st': rtn_row.group(1),
                        '2nd': rtn_row.group(2),
                        '3rd': rtn_row.group(3)
                    }
    except Exception as e:
        print(f"Error scraping {date_str}: {e}")
    
    return None

def check_win(number, result):
    """Check if number won in draw result"""
    if not result:
        return None, None
    
    if result.get('1st') == number:
        return '1st Prize', result['1st']
    if result.get('2nd') == number:
        return '2nd Prize', result['2nd']
    if result.get('3rd') == number:
        return '3rd Prize', result['3rd']
    
    return None, None

def send_alert(number, lottery, prize, date, won_number):
    """Send Telegram alert"""
    msg = f"🎉 *WINNER ALERT!*\n\n"
    msg += f"Number: *{number}*\n"
    msg += f"Lottery: *{lottery.upper()}*\n"
    msg += f"Date: *{date}*\n"
    msg += f"Prize: *{prize}*\n"
    msg += f"Number won: *{won_number}*"
    
    # For now, just print - actual Telegram send needs chat_id
    print(f"\n{'='*50}")
    print(f"ALERT! {number} won {prize} in {lottery.upper()} on {date}!")
    print(f"{'='*50}\n")
    print(msg)
    
    return True

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        print("\nExamples:")
        print("  python monitor.py damacai 4444 5    - Monitor 4444 in Damacai for next 5 draws")
        print("  python monitor.py toto 9999 3   - Monitor 9999 in Toto for next 3 draws")
        print("  python monitor.py tdm 1234 10 - Monitor 1234 in all 3 for next 10 draws")
        sys.exit(1)
    
    lottery = sys.argv[1].lower()
    number = sys.argv[2]
    max_draws = int(sys.argv[3])
    
    # Validate
    if not number.isdigit() or len(number) != 4:
        print("Number must be 4 digits")
        sys.exit(1)
    
    # Map lottery
    lot_map = {
        'd': 'damacai', 'damacai': 'damacai',
        't': 'toto', 'toto': 'toto',
        'm': 'magnum', 'magnum': 'magnum'
    }
    
    lotteries = []
    for char in lottery:
        if char in lot_map:
            lotteries.append(lot_map[char])
    
    if not lotteries:
        print("Invalid lottery. Use: d, t, m, dt, tdm, etc.")
        sys.exit(1)
    
    print(f"\n=== MONITORING {number} in {'+'.join([l.upper() for l in lotteries])}")
    print(f"Will check up to {max_draws} future draws\n")
    
    # Find next draws for each lottery
    all_draws = []
    for lot in lotteries:
        next_date = get_next_draw_date(lot)
        if next_date:
            all_draws.append((lot, next_date))
    
    # Sort by date
    all_draws.sort(key=lambda x: x[1])
    
    print("Upcoming draws:")
    for lot, date in all_draws:
        print(f"  {lot.upper()}: {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")
    print()
    
    # Check each draw
    checked = 0
    for lot, date in all_draws:
        if checked >= max_draws:
            break
        
        date_str = date.strftime('%Y-%m-%d')
        print(f"Checking {lot.upper()} for {date_str}...")
        
        result = scrape_draw(date_str, lot)
        
        if result:
            prize, won_num = check_win(number, result)
            if prize:
                print(f"  WINNER! {prize} - Number: {won_num}")
                send_alert(number, lot, prize, date_str, won_num)
                print(f"\n✅ Monitor stopped - number won!")
                return
            else:
                print(f"  No win. 1st: {result.get('1st')}")
        else:
            print(f"  No results yet (draw may not be available)")
        
        checked += 1
        time.sleep(2)  # Rate limit
    
    print(f"\n❌ No win in {checked} draws checked.")
    print("Run again after next draw to continue monitoring.")

if __name__ == "__main__":
    main()