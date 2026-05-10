"""Debug Magnum parsing"""
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
        
        # Find sections
        damacai_pos = content.find('Damacai 1+3D')
        magnum_pos = content.find('Magnum 4D')
        toto_pos = content.find('SportsToto 4D')
        
        print(f"Damacai pos: {damacai_pos}")
        print(f"Magnum pos: {magnum_pos}")
        print(f"Toto pos: {toto_pos}")
        
        if magnum_pos > 0:
            end = toto_pos if toto_pos > 0 else magnum_pos + 3000
            section = content[magnum_pos:end]
            print(f"\nMagnum section (first 500 chars):\n{section[:500]}")
            
            rtn_match = re.search(r'1st.*?(\d{4}).*?2nd.*?(\d{4}).*?3rd.*?(\d{4})', section, re.DOTALL)
            if rtn_match:
                print(f"\nFound: 1st={rtn_match.group(1)}, 2nd={rtn_match.group(2)}, 3rd={rtn_match.group(3)}")
            else:
                print("\nNo match found")

asyncio.run(debug())