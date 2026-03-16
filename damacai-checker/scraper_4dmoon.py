#!/usr/bin/env python3
"""
4D Moon Scraper - Fetches Damacai results from 4dmoon.com
"""

import requests
import re
import json
from datetime import datetime, timedelta
from time import sleep

def scrape_4dmoon(date_str):
    """
    Scrape Damacai results from 4dmoon.com for a specific date
    date_str format: YYYY-MM-DD (e.g., "2026-02-01")
    """
    url = f"https://www.4dmoon.com/past-results/{date_str}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html = response.text
        
        # Extract Damacai section
        damacai_match = re.search(
            r'Damacai 1\+3D.*?(?=Magnum 4D|Singapore 4D|$)',
            html,
            re.DOTALL | re.IGNORECASE
        )
        
        if not damacai_match:
            print(f"No Damacai data found for {date_str}")
            return None
        
        damacai_section = damacai_match.group(0)
        
        # Extract prizes - looking for 4-digit numbers after prize labels
        # Pattern: 1st Prize, 2nd Prize, 3rd Prize followed by numbers
        prizes = {}
        
        # Extract 1st Prize (usually the first 4-digit number after "1st Prize")
        first_prize = re.search(r'1st\s*Prize\s*(\d{4})', damacai_section, re.IGNORECASE)
        if first_prize:
            prizes['first'] = first_prize.group(1)
        
        # Extract 2nd Prize
        second_prize = re.search(r'2nd\s*Prize\s*(\d{4})', damacai_section, re.IGNORECASE)
        if second_prize:
            prizes['second'] = second_prize.group(1)
        
        # Extract 3rd Prize
        third_prize = re.search(r'3rd\s*Prize\s*(\d{4})', damacai_section, re.IGNORECASE)
        if third_prize:
            prizes['third'] = third_prize.group(1)
        
        # Alternative: find all 4-digit numbers in sequence after prize labels
        if not prizes.get('first'):
            # Look for pattern like "1st Prize2nd Prize3rd Prize" followed by 3 numbers
            all_prizes = re.findall(r'>(\d{4})<', damacai_section)
            if len(all_prizes) >= 3:
                prizes['first'] = all_prizes[0]
                prizes['second'] = all_prizes[1]
                prizes['third'] = all_prizes[2]
        
        if prizes.get('first'):
            return {
                'date': date_str,
                'first_prize': prizes.get('first'),
                'second_prize': prizes.get('second'),
                'third_prize': prizes.get('third'),
                'draw_info': re.search(r'(#\d+/\d+)', damacai_section).group(1) if re.search(r'(#\d+/\d+)', damacai_section) else ''
            }
        
        return None
        
    except Exception as e:
        print(f"Error scraping {date_str}: {e}")
        return None


def scrape_range(start_date, days=30):
    """
    Scrape results for a range of dates
    """
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    
    print(f"Scraping {days} days starting from {start_date}...\n")
    
    for i in range(days):
        date_str = current.strftime('%Y-%m-%d')
        print(f"Fetching {date_str}...", end=' ')
        
        result = scrape_4dmoon(date_str)
        
        if result and result['first_prize']:
            results.append(result)
            print(f"✓ 1st Prize: {result['first_prize']}")
        else:
            print("✗ No data")
        
        # Be nice to the server
        sleep(0.5)
        
        # Move to previous day
        current -= timedelta(days=1)
    
    return results


def save_as_js(results, filename='damacai_data.js'):
    """Save results in JavaScript format for the website"""
    js_data = []
    for r in results:
        if r['first_prize']:
            js_data.append({
                'date': r['date'],
                'number': r['first_prize']
            })
    
    js_content = "// Damacai 4D First Prize Results\\n"
    js_content += f"// Scraped from 4dmoon.com on {datetime.now().strftime('%Y-%m-%d')}\\n\\n"
    js_content += "const damacaiData = " + json.dumps(js_data, indent=4) + ";\\n\\n"
    js_content += """// Create lookup map
const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) {
        numberMap.set(draw.number, []);
    }
    numberMap.get(draw.number).push(draw);
});
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\\n✓ Saved {len(js_data)} results to {filename}")


def main():
    print("=" * 50)
    print("4D Moon Damacai Scraper")
    print("=" * 50)
    print()
    
    # Scrape last 60 days
    today = datetime.now().strftime('%Y-%m-%d')
    results = scrape_range(today, days=60)
    
    if results:
        print(f"\\nTotal results found: {len(results)}")
        
        # Save as JSON
        with open('damacai_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("✓ Saved to damacai_results.json")
        
        # Save as JavaScript
        save_as_js(results)
    else:
        print("\\nNo results found.")
    
    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
