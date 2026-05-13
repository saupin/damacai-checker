"""
Damacai Scraper with Playwright
Scrapes latest results using browser automation from homepage
"""

import asyncio
import os
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "damacai_full.json")
JS_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "damacai_data.js")
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

def parse_damacai(html, date):
    """Parse Damacai 1+3D results from HTML"""
    results = {
        'date': date,
        'damacai': {'1st': None, '2nd': None, '3rd': None}
    }
    
    # Find Damacai section
    damacai_pos = html.find('Damacai 1+3D')
    if damacai_pos < 0:
        return None
    
    # Find next major lottery section
    next_pos = html.find('Magnum 4D', damacai_pos)
    section = html[damacai_pos:next_pos] if next_pos > 0 else html[damacai_pos:damacai_pos+3000]
    
    # Extract first 3 numbers (1st, 2nd, 3rd prizes) - they appear as >XXXX< in order
    numbers = re.findall(r'>(\d{4})<', section)
    
    if len(numbers) >= 3:
        results['damacai']['1st'] = numbers[0]
        results['damacai']['2nd'] = numbers[1]
        results['damacai']['3rd'] = numbers[2]
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
    js_content = f"// Damacai 1+3D Full Results\n// Last updated: {data['last_updated']}\n// Total draws: {len(data['draws'])}\n\nconst damacai_data = {json.dumps(js_data, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = damacai_data;\n}}"
    with open(JS_DATA_FILE, 'w') as f:
        f.write(js_content)

def check_number(num, data=None):
    """Check if number won in any prize"""
    if data is None:
        data = load_existing_data()
    
    matches = {'1st': [], '2nd': [], '3rd': []}
    for draw in data.get('draws', []):
        d = draw.get('damacai', {})
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
    date_match = re.search(r'Damacai 1\+3D[^)]+\) (\d{2})-([A-Za-z]+)-(\d{4})', html)
    if date_match:
        month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        month = month_map.get(date_match.group(2), '01')
        date_str = f"{date_match.group(3)}-{month}-{date_match.group(1)}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    results = parse_damacai(html, date_str)
    if results:
        print(f"  [OK] {date_str}: 1st={results['damacai']['1st']}, 2nd={results['damacai']['2nd']}, 3rd={results['damacai']['3rd']}")
        return results
    else:
        print(f"  No Damacai results found")
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
    print("=== Damacai Latest Scraper (Playwright) ===\n")
    result = scrape_latest()
    if result:
        print(f"\nLatest Damacai results: {result}")