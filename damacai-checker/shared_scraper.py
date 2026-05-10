"""
Shared Playwright browser for faster scraping
Keeps browser open between calls
"""

import asyncio
import os
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "https://www.4dmoon.com/"

# Global browser instance
_browser = None
_playwright = None

async def get_browser():
    """Get or create shared browser instance"""
    global _browser, _playwright
    if _playwright is None:
        _playwright = await async_playwright().start()
    if _browser is None:
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser

async def fetch_with_browser(url):
    """Fetch page using shared Playwright browser"""
    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(url, timeout=30000)
    await page.wait_for_timeout(2000)  # Reduced wait time
    content = await page.content()
    await page.close()
    return content

async def close_browser():
    """Close the shared browser"""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None

def parse_damacai(html, date):
    """Parse Damacai 1+3D results from HTML"""
    results = {
        'date': date,
        'damacai': {'1st': None, '2nd': None, '3rd': None}
    }
    
    damacai_pos = html.find('Damacai 1+3D')
    if damacai_pos < 0:
        return None
    
    next_pos = html.find('Magnum 4D', damacai_pos)
    section = html[damacai_pos:next_pos] if next_pos > 0 else html[damacai_pos:damacai_pos+3000]
    
    m1 = re.search(r'id="DP1">(\d{4})<', section)
    m2 = re.search(r'id="DP2">(\d{4})<', section)
    m3 = re.search(r'id="DP3">(\d{4})<', section)
    
    if m1 and m2 and m3:
        results['damacai']['1st'] = m1.group(1)
        results['damacai']['2nd'] = m2.group(1)
        results['damacai']['3rd'] = m3.group(1)
        return results
    
    return None

def parse_toto(html, date):
    """Parse Sports Toto 4D results from HTML"""
    results = {
        'date': date,
        'toto': {'1st': None, '2nd': None, '3rd': None}
    }
    
    toto_pos = html.find('SportsToto 4D')
    if toto_pos < 0:
        return None
    
    next_pos = html.find('SportsToto Fireball', toto_pos)
    section = html[toto_pos:next_pos] if next_pos > 0 else html[toto_pos:toto_pos+3000]
    
    m1 = re.search(r'id="TP1">(\d{4})<', section)
    m2 = re.search(r'id="TP2">(\d{4})<', section)
    m3 = re.search(r'id="TP3">(\d{4})<', section)
    
    if m1 and m2 and m3:
        results['toto']['1st'] = m1.group(1)
        results['toto']['2nd'] = m2.group(1)
        results['toto']['3rd'] = m3.group(1)
        return results
    
    return None

def parse_magnum(html, date):
    """Parse Magnum 4D results from HTML"""
    results = {
        'date': date,
        'magnum': {'1st': None, '2nd': None, '3rd': None}
    }
    
    damacai_pos = html.find('Damacai 1+3D')
    magnum_pos = html.find('Magnum 4D', damacai_pos + 100) if damacai_pos > 0 else html.find('Magnum 4D')
    
    if magnum_pos > 0 and magnum_pos > damacai_pos:
        toto_start = html.find('SportsToto 4D', magnum_pos)
        section = html[magnum_pos:toto_start] if toto_start > 0 else html[magnum_pos:magnum_pos+3000]
        
        m1 = re.search(r'id="MP1">(\d{4})<', section)
        m2 = re.search(r'id="MP2">(\d{4})<', section)
        m3 = re.search(r'id="MP3">(\d{4})<', section)
        
        if m1 and m2 and m3:
            results['magnum']['1st'] = m1.group(1)
            results['magnum']['2nd'] = m2.group(1)
            results['magnum']['3rd'] = m3.group(1)
            return results
    
    return None

async def scrape_all_async():
    """Scrape all 3 lotteries in one browser session"""
    print("Fetching all results with shared browser...")
    
    html = await fetch_with_browser(BASE_URL)
    if not html:
        return None, None, None
    
    # Extract date from page
    date_match = re.search(r'Damacai 1\+3D[^)]+\) (\d{2})-([A-Za-z]+)-(\d{4})', html)
    if date_match:
        month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                     'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        month = month_map.get(date_match.group(2), '01')
        date_str = f"{date_match.group(3)}-{month}-{date_match.group(1)}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    dmc = parse_damacai(html, date_str)
    tot = parse_toto(html, date_str)
    mag = parse_magnum(html, date_str)
    
    if dmc:
        print(f"  Damacai: {dmc['damacai']['1st']}")
    if tot:
        print(f"  Toto: {tot['toto']['1st']}")
    if mag:
        print(f"  Magnum: {mag['magnum']['1st']}")
    
    return dmc, tot, mag

# Sync wrappers
def scrape_all():
    return asyncio.run(scrape_all_async())

def scrape_damacai_latest():
    dmc, _, _ = scrape_all()
    return dmc

def scrape_toto_latest():
    _, tot, _ = scrape_all()
    return tot

def scrape_magnum_latest():
    _, _, mag = scrape_all()
    return mag

if __name__ == "__main__":
    print("=== Fast Scraper Test ===\n")
    import time
    start = time.time()
    dmc, tot, mag = scrape_all()
    print(f"\nTime: {time.time() - start:.2f}s")
    print(f"Damacai: {dmc}")
    print(f"Toto: {tot}")
    print(f"Magnum: {mag}")