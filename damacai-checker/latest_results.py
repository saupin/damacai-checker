"""
Show Latest Draw Results
Displays the most recent draw results for all 3 lotteries

Usage:
    python latest_results.py
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime

WORKSPACE = r'C:\Users\samul\.openclaw\workspace\damacai-checker'
sys.path.insert(0, WORKSPACE)

BASE_URL = "https://www.4dmoon.com/past-results/"

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except:
        return None

def get_last_draw_date():
    """Get the most recent date that likely had a draw"""
    today = datetime.now()
    # Draw days: Wed, Sat, Sun
    draw_days = ['Wednesday', 'Saturday', 'Sunday']
    
    # Check last 7 days
    from datetime import timedelta
    for i in range(1, 8):
        check = today - timedelta(days=i)
        if check.strftime('%A') in draw_days:
            return check.strftime('%Y-%m-%d')
    return today.strftime('%Y-%m-%d')

def parse_damacai(html):
    rtn = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', html)
    if rtn:
        return {'1st': rtn.group(1), '2nd': rtn.group(2), '3rd': rtn.group(3)}
    return None

def parse_toto(html):
    toto_match = re.search(r'SportsToto 4D([\s\S]*?)(?=Magnum|Damacai|$)', html)
    if toto_match:
        section = toto_match.group(1)
        rtn = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
        if rtn:
            return {'1st': rtn.group(1), '2nd': rtn.group(2), '3rd': rtn.group(3)}
    return None

def parse_magnum(html):
    start = html.find('Magnum 4D<br>')
    if start != -1:
        end = html.find('SportsToto 4D<br>')
        section = html[start:end] if end > 0 else html[start:start+5000]
        rtn = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
        if rtn:
            return {'1st': rtn.group(1), '2nd': rtn.group(2), '3rd': rtn.group(3)}
    return None

def main():
    print("\n=== LATEST DRAW RESULTS ===\n")
    
    last_date = get_last_draw_date()
    print(f"Fetching results for {last_date}...\n")
    
    html = fetch(f"{BASE_URL}{last_date}")
    
    if not html:
        print("Could not fetch page. Try again later.")
        return
    
    # Parse all 3
    dmacai = parse_damacai(html)
    toto = parse_toto(html)
    magnum = parse_magnum(html)
    
    print(f"Date: {last_date}\n")
    
    if dmacai:
        print(f"DAMACAI:")
        print(f"  1st Prize: {dmacai['1st']}")
        print(f"  2nd Prize: {dmacai['2nd']}")
        print(f"  3rd Prize: {dmacai['3rd']}")
    else:
        print("DAMACAI: No results")
    
    print()
    
    if toto:
        print(f"SPORTS TOTO:")
        print(f"  1st Prize: {toto['1st']}")
        print(f"  2nd Prize: {toto['2nd']}")
        print(f"  3rd Prize: {toto['3rd']}")
    else:
        print("SPORTS TOTO: No results")
    
    print()
    
    if magnum:
        print(f"MAGNUM 4D:")
        print(f"  1st Prize: {magnum['1st']}")
        print(f"  2nd Prize: {magnum['2nd']}")
        print(f"  3rd Prize: {magnum['3rd']}")
    else:
        print("MAGNUM 4D: No results")
    
    print()

if __name__ == "__main__":
    main()