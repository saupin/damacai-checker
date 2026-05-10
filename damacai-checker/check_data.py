import json

data = json.load(open(r'C:\Users\samul\.openclaw\workspace\damacai-checker\damacai_full.json'))
print(f"Total draws: {len(data['draws'])}")

# Check 2014 draws
draws_2014 = [d for d in data['draws'] if d['date'].startswith('2014')]
print(f"\n2014 draws: {len(draws_2014)}")

# Check a sample draw
for d in draws_2014[:3]:
    print(f"  {d['date']}: 1st={d['damacai'].get('1st')}, 2nd={d['damacai'].get('2nd')}, 3rd={d['damacai'].get('3rd')}")

# Check structure of first few draws
print("\n--- Checking if special/consolation exist ---")
for d in data['draws'][:3]:
    dam = d['damacai']
    has_special = 'special' in dam and dam['special']
    has_cons = 'consolation' in dam and dam['consolation']
    print(f"  {d['date']}: special={has_special}, consolation={has_cons}")
