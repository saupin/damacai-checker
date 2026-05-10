"""
Quick fix: Convert old damacai_full.json format to correct 3rd prize format.
Old format: '3rd': ['5859', '0542', '3186', '9403'] (array)
New format: '3rd': '5859' (single string, first element only)
"""
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "damacai_full.json")
JS_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "damacai_data.js")

print("Loading data...")
with open(DATA_FILE, 'r') as f:
    data = json.load(f)

fixed_count = 0
already_correct = 0

for draw in data['draws']:
    dam = draw['damacai']
    old_3rd = dam.get('3rd')
    
    # Check if 3rd is already a string (correct format)
    if isinstance(old_3rd, str):
        already_correct += 1
    elif isinstance(old_3rd, list) and len(old_3rd) > 0:
        # Convert first element to string
        dam['3rd'] = old_3rd[0]
        fixed_count += 1
    elif old_3rd is None:
        already_correct += 1

print(f"Total draws: {len(data['draws'])}")
print(f"Already correct (3rd is string): {already_correct}")
print(f"Fixed (converted array to string): {fixed_count}")

# Save fixed JSON
data['last_updated'] = '2026-05-05'
with open(DATA_FILE, 'w') as f:
    json.dump(data, f, indent=2)

# Regenerate JS file
print("\nRegenerating damacai_data.js...")
js_data = {}
for draw in data.get('draws', []):
    d = draw['date']
    
    n1 = draw['damacai']['1st']
    if n1:
        if n1 not in js_data:
            js_data[n1] = {'1st': [], '2nd': [], '3rd': []}
        js_data[n1]['1st'].append(d)
    
    n2 = draw['damacai']['2nd']
    if n2:
        if n2 not in js_data:
            js_data[n2] = {'1st': [], '2nd': [], '3rd': []}
        js_data[n2]['2nd'].append(d)
    
    n3 = draw['damacai'].get('3rd')
    if n3:
        if n3 not in js_data:
            js_data[n3] = {'1st': [], '2nd': [], '3rd': []}
        js_data[n3]['3rd'].append(d)

# Sort dates for each number
for num in js_data:
    for prize in js_data[num]:
        js_data[num][prize].sort(reverse=True)

from datetime import datetime
js_content = f"// Damacai 1+3D Full Results\n// Last updated: {datetime.now().isoformat()}\n// Total draws: {len(data['draws'])}\n\nconst damacai_data = {json.dumps(js_data, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = damacai_data;\n}}"

with open(JS_DATA_FILE, 'w') as f:
    f.write(js_content)

print(f"Done! Fixed {fixed_count} records, {already_correct} were already correct")
print(f"JS file regenerated with {len(js_data)} unique numbers")
