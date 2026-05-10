"""
Toto Scraper with Playwright
Scrapes latest results using browser automation from homepage
"""

import asyncio
import os
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toto_full.json")
JS_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toto_data.js")
BASE_URL = "https://www.4dmoon.com/"

async def fetch_with_browser(url):
    """Fetch page using Playwright browser"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(3000)
        content = await page.content()
        await browser.close()
        return content

def parse_toto(html, date):
    """Parse Sports Toto 4D results from HTML"""
    results = {
        'date': date,
        'toto': {'1st': None, '2nd': None, '3rd': None}
    }
    
    # Find Toto section
    toto_pos = html.find('SportsToto 4D')
    if toto_pos < 0:
        return None
    
    # Find next section
    next_pos = html.find('SportsToto Fireball', toto_pos)
    section = html[toto_pos:next_pos] if next_pos > 0 else html[toto_pos:toto_pos+3000]
    
    # Extract by div IDs: TP1, TP2, TP3
    m1 = re.search(r'id="TP1">(\d{4})<', section)
    m2 = re.search(r'id="TP2">(\d{4})<', section)
    m3 = re.search(r'id="TP3">(\d{4})<', section)
    
    if m1 and m2 and m3:
        results['toto']['1st'] = m1.group(1)
        results['toto']['2nd'] = m2.group(1)
        results['toto']['3rd'] = m3.group(1)
        return results
    
    return None

def load_existing_data():
    """Load existing data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'draws': [], 'last_updated': None}

def save_data(data):
    """Save data to JSON file"""
    data['last_updated'] = datetime.now().isoformat()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    js_data = {
        'last_updated': data['last_updated'],
        'draws': data['draws']
    }
    js_content = f"// Sports Toto 4D Full Results\n// Last updated: {data['last_updated']}\n// Total draws: {len(data['draws'])}\n\nconst toto_data = {json.dumps(js_data, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = toto_data;\n}}"
    with open(JS_DATA_FILE, 'w') as f:
        f.write(js_content)

def check_number(num, data=None):
    """Check if number won in any prize"""
    if data is None:
        data = load_existing_data()
    
    matches = {'1st': [], '2nd': [], '3rd': []}
    for draw in data.get('draws', []):
        d = draw.get('toto', {})
        for prize in ['1st', '2nd', '3rd']:
            if d.get(prize) == num:
                matches[prize].append(draw['date'])
    return matches

async def scrape_latest_async():
    """Scrape latest results from homepage (shows current live draw)"""
    print(f"Fetching latest from {BASE_URL}...")
    
    html = await fetch_with_browser(BASE_URL)
    if not html:
        print("  Failed to fetch page")
        return None
    
    # Extract date from page
    date_match = re.search(r'SportsToto 4D[^)]+\) (\d{2})-([A-Za-z]+)-(\d{4})', html)
    if date_match:
        month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        month = month_map.get(date_match.group(2), '01')
        date_str = f"{date_match.group(3)}-{month}-{date_match.group(1)}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    results = parse_toto(html, date_str)
    if results:
        print(f"  [OK] {date_str}: 1st={results['toto']['1st']}, 2nd={results['toto']['2nd']}, 3rd={results['toto']['3rd']}")
        return results
    else:
        print(f"  No Toto results found")
        return None

def scrape_latest():
    """Sync wrapper for scrape_latest_async"""
    return asyncio.run(scrape_latest_async())

def scrape_date(date_str):
    """Scrape results for a specific date"""
    url = f"{BASE_URL}past-results/{date_str}"
    print(f"Fetching: {url}")
    return asyncio.run(fetch_with_browser(url))

if __name__ == "__main__":
    print("=== Sports Toto Latest Scraper (Playwright) ===\n")
    result = scrape_latest()
    if result:
        print(f"\nLatest Toto results: {result}")