import urllib.request, re

DATA_FILE = r'C:\Users\samul\.openclaw\workspace\damacai-checker\damacai_full.json'
JS_DATA_FILE = r'C:\Users\samul\.openclaw\workspace\damacai-checker\damacai_data.js'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

def parse_damacai_results(html, date):
    results = {'date': date, 'damacai': {'1st': None, '2nd': None, '3rd': None}}
    damacai_match = re.search(r'Damacai 1\+3D([\s\S]*?)(?=Magnum|SportsToto|Singapore|$)', html, re.IGNORECASE)
    if not damacai_match:
        return None
    section = damacai_match.group(1)
    rtn_row = re.search(r'<tr><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td><td class="rtn">(\d{4})</td></tr>', section)
    if rtn_row:
        results['damacai']['1st'] = rtn_row.group(1)
        results['damacai']['2nd'] = rtn_row.group(2)
        results['damacai']['3rd'] = rtn_row.group(3)
    if results['damacai']['1st'] and results['damacai']['2nd'] and results['damacai']['3rd']:
        return results
    return None

# Test on a few dates
for date in ['2014-01-04', '2014-05-21', '2022-09-28']:
    html = fetch(f'https://www.4dmoon.com/past-results/{date}')
    result = parse_damacai_results(html, date)
    if result:
        print(f"{date}: 1st={result['damacai']['1st']}, 2nd={result['damacai']['2nd']}, 3rd={result['damacai']['3rd']}")
    else:
        print(f"{date}: No results")
