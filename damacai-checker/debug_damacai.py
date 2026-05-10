"""Debug Damacai parsing"""
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
        
        # Find Damacai section
        damacai_pos = content.find('Damacai 1+3D')
        magnum_pos = content.find('Magnum 4D', damacai_pos)
        section = content[damacai_pos:magnum_pos]
        print(f"Damacai section (first 1000 chars):\n{section[:1000]}")
        
        # Look for div IDs
        ids = re.findall(r'id="([^"]+)">(\d{4})<', section)
        print(f"\nFound IDs with 4-digit numbers: {ids}")

asyncio.run(debug())