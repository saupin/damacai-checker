"""Test Playwright scraping of 4dmoon.com"""
import asyncio
from playwright.async_api import async_playwright
import re

async def test_scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to 4dmoon.com...")
        await page.goto("https://www.4dmoon.com/", timeout=30000)
        
        # Wait for content to load
        await page.wait_for_timeout(3000)
        
        # Get page content
        content = await page.content()
        print(f"Page loaded, length: {len(content)} chars")
        
        # Extract Damacai results
        dmacai_match = re.search(r'Damacai 1\+3D[^)]+\) (\d{2})-([A-Za-z]+)-(\d{4})', content)
        if dmacai_match:
            print(f"Damacai date found: {dmacai_match.group(0)}")
        
        # Look for 1st prize numbers
        rtn_match = re.search(r'1st.*?(\d{4}).*?2nd.*?(\d{4}).*?3rd.*?(\d{4})', content[:5000], re.DOTALL)
        if rtn_match:
            print(f"1st: {rtn_match.group(1)}, 2nd: {rtn_match.group(2)}, 3rd: {rtn_match.group(3)}")
        
        # Get text content
        text = await page.inner_text('body')
        print(f"\nText preview (first 2000 chars):\n{text[:2000]}")
        
        await browser.close()

asyncio.run(test_scrape())