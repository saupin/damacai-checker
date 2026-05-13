"""
Auto-scrape latest lottery results and update all data files
Run daily via cron/Task Scheduler
"""

import asyncio
import os
import sys
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

# Add damacai-checker to path for imports
BOT_DIR = r"C:\Users\samul\.openclaw\workspace\damacai-checker"
PWA_DIR = r"C:\Users\samul\.openclaw\workspace\lottery-pwa"

async def fetch_homepage():
    """Fetch 4dmoon.com homepage with Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.4dmoon.com/", timeout=30000)
        await page.wait_for_timeout(3000)
        content = await page.content()
        await browser.close()
        return content

def parse_section(html, start_marker, end_marker):
    """Extract first 3 numbers from a lottery section"""
    start_pos = html.find(start_marker)
    if start_pos < 0:
        return None
    
    # Find end marker (next lottery or end of page)
    if end_marker:
        end_pos = html.find(end_marker, start_pos + 100)
        section = html[start_pos:end_pos] if end_pos > 0 else html[start_pos:start_pos+5000]
    else:
        section = html[start_pos:start_pos+5000]
    
    # Extract first 3 >XXXX< patterns (1st, 2nd, 3rd prizes)
    numbers = re.findall(r'>(\d{4})<', section)
    if len(numbers) >= 3:
        return numbers[:3]
    return None

def extract_date(html):
    """Extract draw date from page"""
    match = re.search(r'Damacai 1\+3D[^)]+\) (\d{2})-([A-Za-z]+)-(\d{4})', html)
    if match:
        month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        month = month_map.get(match.group(2), '01')
        return f"{match.group(3)}-{month}-{match.group(1)}"
    return datetime.now().strftime('%Y-%m-%d')

async def main():
    print(f"[{datetime.now().isoformat()}] Starting auto-scrape...")
    
    # Fetch homepage
    html = await fetch_homepage()
    if not html:
        print("Failed to fetch page")
        return
    
    # Extract date
    date_str = extract_date(html)
    print(f"Draw date: {date_str}")
    
    results = {}
    
    # Parse each lottery
    damacai_nums = parse_section(html, 'Damacai 1+3D', 'Magnum 4D')
    if damacai_nums:
        results['damacai'] = {'1st': damacai_nums[0], '2nd': damacai_nums[1], '3rd': damacai_nums[2]}
        print(f"DaMaCai: {damacai_nums}")
    
    toto_nums = parse_section(html, 'SportsToto 4D', 'SportsToto Fireball')
    if toto_nums:
        results['toto'] = {'1st': toto_nums[0], '2nd': toto_nums[1], '3rd': toto_nums[2]}
        print(f"Toto: {toto_nums}")
    
    magnum_nums = parse_section(html, 'Magnum 4D', 'SportsToto 4D')
    if magnum_nums:
        results['magnum'] = {'1st': magnum_nums[0], '2nd': magnum_nums[1], '3rd': magnum_nums[2]}
        print(f"Magnum: {magnum_nums}")
    
    if not results:
        print("No results found!")
        return
    
    # Update bot data files
    for lottery, key in [('damacai', 'damacai'), ('toto', 'toto'), ('magnum', 'magnum')]:
        if lottery not in results:
            continue
        
        bot_file = os.path.join(BOT_DIR, f"{lottery}_full.json")
        if os.path.exists(bot_file):
            with open(bot_file, 'r') as f:
                data = json.load(f)
            
            # Check if already up to date
            if data['draws'] and data['draws'][0].get('date') == date_str:
                print(f"{lottery} already up to date")
                continue
            
            # Add new draw
            new_draw = {'date': date_str, lottery: results[lottery]}
            data['draws'].insert(0, new_draw)
            data['last_updated'] = datetime.now().isoformat()
            
            with open(bot_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Updated bot {lottery}")
    
    # Update PWA data files
    for lottery, key in [('damacai', 'damacai'), ('toto', 'toto'), ('magnum', 'magnum')]:
        if lottery not in results:
            continue
        
        pwa_file = os.path.join(PWA_DIR, "data", f"{lottery}_full.json")
        if os.path.exists(pwa_file):
            with open(pwa_file, 'r') as f:
                data = json.load(f)
            
            # Check if already up to date
            if data['draws'] and data['draws'][0].get('date') == date_str:
                print(f"PWA {lottery} already up to date")
                continue
            
            # Add new draw
            new_draw = {'date': date_str, **results[lottery]}
            data['draws'].insert(0, new_draw)
            
            with open(pwa_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Updated PWA {lottery}")
    
    print(f"[{datetime.now().isoformat()}] Auto-scrape complete!")

if __name__ == "__main__":
    asyncio.run(main())