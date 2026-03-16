#!/usr/bin/env python3
"""
Damacai 4D Results Scraper
Scrapes historical 4D results from Damacai website
"""

import requests
import json
import re
from datetime import datetime, timedelta
from time import sleep

class DamacaiScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.damacai.com.my/'
        })
        self.base_url = "https://www.damacai.com.my"
        self.results = []
    
    def get_draw_result(self, date_str):
        """
        Fetch results for a specific date
        date_str format: DD/MM/YYYY (e.g., "25/02/2026")
        """
        try:
            # Try the winning information endpoint
            url = f"{self.base_url}/did-i-win/"
            
            # First get the page to establish session
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Try to find embedded JSON data
                html = response.text
                
                # Look for draw data in the HTML
                # Pattern for 1st prize: typically a 4-digit number
                patterns = {
                    'first_prize': r'1st\s*Prize.*?>(\d{4})<',
                    'second_prize': r'2nd\s*Prize.*?>(\d{4})<',
                    'third_prize': r'3rd\s*Prize.*?>(\d{4})<',
                }
                
                result = {
                    'date': date_str,
                    'first_prize': None,
                    'second_prize': None,
                    'third_prize': None,
                    'starters': [],
                    'consolations': []
                }
                
                # Extract prizes
                for prize_type, pattern in patterns.items():
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        result[prize_type] = match.group(1)
                
                # Look for starter prizes (10 numbers)
                starter_matches = re.findall(r'(\d{4})\s*</span>\s*<span[^>]*class="[^"]*prize-number', html)
                if starter_matches:
                    result['starters'] = starter_matches[:10]
                
                # Extract all 4-digit numbers that appear to be results
                all_numbers = re.findall(r'>(\d{4})<', html)
                
                if result['first_prize']:
                    print(f"✓ Found results for {date_str}: 1st Prize = {result['first_prize']}")
                    return result
                else:
                    print(f"✗ No draw on {date_str}")
                    return None
                    
        except Exception as e:
            print(f"Error fetching {date_str}: {e}")
            return None
        
        return None
    
    def scrape_date_range(self, start_date, end_date):
        """
        Scrape results for a date range
        """
        current = start_date
        results = []
        
        while current <= end_date:
            date_str = current.strftime("%d/%m/%Y")
            result = self.get_draw_result(date_str)
            
            if result and result['first_prize']:
                results.append(result)
            
            # Be nice to the server - wait between requests
            sleep(1)
            
            current += timedelta(days=1)
        
        return results
    
    def scrape_sample_data(self):
        """
        Scrape a sample of recent results for testing
        """
        print("Scraping sample Damacai 4D results...")
        
        # Try last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        results = self.scrape_date_range(start_date, end_date)
        
        print(f"\nScraped {len(results)} draw results")
        return results
    
    def save_to_json(self, results, filename="damacai_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Saved to {filename}")
    
    def save_to_js(self, results, filename="damacai_data.js"):
        """Save results in JavaScript format for the website"""
        js_content = "// Damacai 4D First Prize Results\n"
        js_content += "// Format: { date: 'YYYY-MM-DD', number: 'XXXX' }\n\n"
        js_content += "const damacaiData = [\n"
        
        for result in results:
            if result['first_prize']:
                # Convert date format from DD/MM/YYYY to YYYY-MM-DD
                date_parts = result['date'].split('/')
                iso_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                js_content += f"    {{ date: '{iso_date}', number: '{result['first_prize']}' }},\n"
        
        js_content += "];\n\n"
        js_content += "// Create lookup map for fast searching\n"
        js_content += "const numberMap = new Map();\n"
        js_content += "damacaiData.forEach(draw => {\n"
        js_content += "    if (!numberMap.has(draw.number)) {\n"
        js_content += "        numberMap.set(draw.number, []);\n"
        js_content += "    }\n"
        js_content += "    numberMap.get(draw.number).push(draw);\n"
        js_content += "});\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"Saved to {filename}")


def alternative_scrape_from_free_source():
    """
    Alternative: Scrape from a free 4D results API or website
    """
    print("Attempting to fetch from alternative sources...")
    
    results = []
    
    # Try free4d.com or similar (these are commonly available)
    sources = [
        "https://free4d.com/",
        "https://4d2u.com/",
    ]
    
    for source in sources:
        try:
            print(f"Trying {source}...")
            response = requests.get(source, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Successfully accessed {source}")
                # Parse logic would go here
                break
        except Exception as e:
            print(f"✗ Failed to access {source}: {e}")
    
    return results


def create_manual_entry_template():
    """
    Create a template for manual data entry
    """
    template = """// Damacai 4D First Prize Results - MANUAL ENTRY
// Add your results here in this format:

const damacaiData = [
    // Example entries (replace with real data from Damacai):
    { date: '2024-12-28', number: '4821' },
    { date: '2024-12-25', number: '7395' },
    { date: '2024-12-21', number: '1567' },
    // Add more entries...
];

// To get real historical data:
// 1. Visit: https://www.damacai.com.my/past-draw-result/
// 2. Select dates and copy the 1st Prize numbers
// 3. Add them above in the format: { date: 'YYYY-MM-DD', number: 'XXXX' }

// Create lookup map for fast searching
const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) {
        numberMap.set(draw.number, []);
    }
    numberMap.get(draw.number).push(draw);
});
"""
    
    with open("damacai_data_manual.js", "w") as f:
        f.write(template)
    print("Created manual entry template: damacai_data_manual.js")


if __name__ == "__main__":
    print("=" * 50)
    print("Damacai 4D Results Scraper")
    print("=" * 50)
    
    # Create scraper instance
    scraper = DamacaiScraper()
    
    # Try to scrape sample data
    results = scraper.scrape_sample_data()
    
    if results:
        # Save in different formats
        scraper.save_to_json(results)
        scraper.save_to_js(results)
    else:
        print("\n⚠ Could not scrape automatically.")
        print("\nAlternative options:")
        print("1. Try alternative sources...")
        alternative_scrape_from_free_source()
        
        print("\n2. Create manual entry template...")
        create_manual_entry_template()
        
        print("\n3. Manual scraping instructions:")
        print("   - Visit: https://www.damacai.com.my/past-draw-result/")
        print("   - Select historical dates")
        print("   - Copy the 1st Prize numbers")
        print("   - Add them to damacai_data_manual.js")
    
    print("\n" + "=" * 50)
    print("Done!")
