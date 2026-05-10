"""Debug Toto parsing"""
import asyncio
import re
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.4dmoon.com/", timeout=30000)
        await page.wait_for_timeout(3000)
        content = await page.content()
        await browser.close()
        
        # Find Toto section
        toto_pos = content.find('SportsToto 4D')
        if toto_pos > 0:
            # Find next section
            next_pos = content.find('SportsToto Fireball', toto_pos)
            section = content[toto_pos:next_pos if next_pos > 0 else toto_pos + 3000]
            print(f"Toto section (first 1000 chars):\n{section[:1000]}")
            
            # Look for div IDs
            ids = re.findall(r'id="([^"]+)">(\d{4})<', section)
            print(f"\nFound IDs with 4-digit numbers: {ids[:15]}")

asyncio.run(debug())