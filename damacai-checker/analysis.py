"""
Lottery Draw Analysis Script
Analyzes draw results for Damacai, Toto, and Magnum

Usage: python analysis.py
"""

import json
import os
import re
from datetime import datetime
from collections import Counter, defaultdict

WORKSPACE = r'C:\Users\samul\.openclaw\workspace\damacai-checker'

def load_json(filename):
    path = os.path.join(WORKSPACE, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def analyze_lottery(name, data_file, key_name):
    """Analyze a single lottery"""
    print(f"\n{'='*60}")
    print(f"  {name.upper()} ANALYSIS")
    print(f"{'='*60}")
    
    data = load_json(data_file)
    if not data or not data.get('draws'):
        print(f"No data found for {name}")
        return
    
    draws = data['draws']
    print(f"\n[==] Overview:")
    print(f"   Total draws: {len(draws):,}")
    print(f"   Date range: {draws[-1]['date']} to {draws[0]['date']}")
    
    # Collect all 1st prize numbers
    first_nums = []
    for draw in draws:
        lottery_data = draw.get(key_name, {})
        if lottery_data:
            n1 = lottery_data.get('1st')
            if n1:
                first_nums.append(n1)
    
    # First digit analysis
    first_digits = [n[0] for n in first_nums if n]
    print(f"\n[#] First Digit Frequency (1st Prize):")
    first_counter = Counter(first_digits)
    for digit in sorted(first_counter.keys()):
        count = first_counter[digit]
        pct = count / len(first_digits) * 100
        bar = '#' * int(pct / 2)
        print(f"   {digit}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Last digit analysis
    last_digits = [n[-1] for n in first_nums if n]
    print(f"\n[#] Last Digit Frequency (1st Prize):")
    last_counter = Counter(last_digits)
    for digit in sorted(last_counter.keys()):
        count = last_counter[digit]
        pct = count / len(last_digits) * 100
        bar = '#' * int(pct / 2)
        print(f"   {digit}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Number frequency analysis
    print(f"\n[>] Most Common 1st Prize Numbers:")
    num_counter = Counter(first_nums)
    for num, count in num_counter.most_common(10):
        print(f"   {num}: {count} times")
    
    # Pairs analysis (1st prize)
    print(f"\n[=] Most Common First 2 Digits (1st Prize):")
    first_two = [n[:2] for n in first_nums if n and len(n) >= 2]
    pair_counter = Counter(first_two)
    for pair, count in pair_counter.most_common(10):
        pct = count / len(first_two) * 100
        print(f"   {pair}: {count} times ({pct:.1f}%)")
    
    # Sum of digits analysis
    print(f"\n[+] Digit Sum Distribution (1st Prize):")
    sums = [sum(int(d) for d in n) for n in first_nums if n]
    sum_counter = Counter(sums)
    for s in sorted(sum_counter.keys()):
        count = sum_counter[s]
        pct = count / len(sums) * 100
        bar = '#' * int(pct)
        print(f"   Sum {s:2d}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Draw day analysis
    print(f"\n[@] Draw Day Distribution:")
    day_counter = Counter()
    for draw in draws:
        try:
            d = datetime.strptime(draw['date'], '%Y-%m-%d')
            day_counter[d.strftime('%A')] += 1
        except:
            pass
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        count = day_counter.get(day, 0)
        pct = count / len(draws) * 100 if len(draws) > 0 else 0
        bar = '#' * int(pct / 2)
        print(f"   {day[:3]}: {count:4d} ({pct:5.1f}%) {bar}")
    
    # Consecutive numbers check
    print(f"\n[~] Consecutive Number Patterns in 1st Prize:")
    consecutive = 0
    for n in first_nums:
        if n:
            digits = [int(d) for d in n]
            diffs = [abs(digits[i] - digits[i+1]) for i in range(3)]
            if max(diffs) <= 1:
                consecutive += 1
    pct = consecutive / len(first_nums) * 100 if first_nums else 0
    print(f"   Numbers with adjacent digits differing by 1 or less: {consecutive} ({pct:.1f}%)")
    
    # Same digit repeating
    print(f"\n[@] All Same Digit Numbers (1st Prize):")
    repeating = [n for n in first_nums if n and len(set(n)) == 1]
    for n in repeating:
        print(f"   {n}")
    if not repeating:
        print(f"   (none)")
    
    # Range of years analysis
    print(f"\n[*] Draws Per Year:")
    year_counter = Counter()
    for draw in draws:
        try:
            d = datetime.strptime(draw['date'], '%Y-%m-%d')
            year_counter[d.year] += 1
        except:
            pass
    for year in sorted(year_counter.keys()):
        count = year_counter[year]
        bar = '#' * int(count / 50)
        print(f"   {year}: {count:4d} {bar}")

def main():
    print("\n" + "="*60)
    print("  LOTTERY DRAW ANALYSIS - MALAYSIA 4D")
    print("="*60)
    
    analyze_lottery("Damacai", "damacai_full.json", "damacai")
    analyze_lottery("Sports Toto", "toto_full.json", "toto")
    analyze_lottery("Magnum", "magnum_full.json", "magnum")
    
    print(f"\n{'='*60}")
    print("  ANALYSIS COMPLETE")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()