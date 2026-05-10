"""
Damacai 4D Checker - Python Script
Usage: python dmc_checker.py 9999
Or import as module: from dmc_checker import check_number
"""

import json
import os
import sys
from datetime import datetime

# Path to damacai_data.js (convert to JSON for Python)
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(DATA_DIR, "damacai_data.json")
JS_DATA_FILE = os.path.join(DATA_DIR, "damacai_data.js")

# Load data from JSON (or convert from JS if needed)
def load_data():
    # Try JSON first
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    
    # Try to convert from JS file
    if os.path.exists(JS_DATA_FILE):
        return convert_js_to_json(JS_DATA_FILE)
    
    return None

def convert_js_to_json(js_file):
    """Convert damacai_data.js format to JSON"""
    with open(js_file, 'r') as f:
        content = f.read()
    
    # Extract array from: const damacaiData = [ ... ];
    start = content.find('[')
    end = content.rfind(']') + 1
    
    if start == -1 or end == 0:
        return None
    
    array_str = content[start:end]
    
    # Parse manually - format is: { date: 'YYYY-MM-DD', number: 'XXXX' }
    results = []
    entries = array_str.split('},')
    
    for entry in entries:
        entry = entry.strip().strip('{}')
        if not entry:
            continue
        
        date_part = entry.split("date:")[1].split(",")[0].strip().strip("'\"")
        num_part = entry.split("number:")[1].strip().strip("'\"")
        
        results.append({
            "date": date_part,
            "number": num_part,
            "source": "damacai"
        })
    
    # Save as JSON for future use
    with open(DATA_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def check_number(num):
    """Check if a 4D number won in any prize position"""
    if not num or len(num) != 4 or not num.isdigit():
        return {"error": "Please provide a valid 4-digit number (e.g., 9999)"}
    
    data = load_data()
    
    if not data:
        return {"error": "No data found! Please update damacai_data.js or damacai_data.json"}
    
    # Search all draws
    matches = []
    for draw in data:
        if draw.get("number") == num:
            matches.append({
                "date": draw.get("date", "unknown"),
                "number": draw.get("number"),
                "position": draw.get("position", "unknown")
            })
    
    result = {
        "query": num,
        "total_matches": len(matches),
        "draws": matches
    }
    
    if len(matches) > 0:
        result["message"] = f"🎉 FOUND! {num} won {len(matches)} time(s)!"
    else:
        result["message"] = f"❌ {num} has never won 1st Prize in Damacai"
    
    return result

def format_response(result):
    """Format result for display (Telegram-friendly)"""
    if "error" in result:
        return f"⚠️ {result['error']}"
    
    lines = []
    lines.append(f"🔍 *Checking: {result['query']}*")
    lines.append("")
    
    if result["total_matches"] == 0:
        lines.append(f"❌ No 1st Prize wins found")
        lines.append("")
        lines.append(f"Checked {len(result['draws']) if 'draws' in result else 'all'} historical draws")
    else:
        lines.append(f"🎉 *FOUND {result['total_matches']}x!* 🎉")
        lines.append("")
        for m in result["draws"]:
            lines.append(f"📅 {m['date']}")
            lines.append(f"🔢 {m['number']}")
            if "position" in m:
                lines.append(f"🏆 {m['position']}")
            lines.append("")
    
    return "\n".join(lines)

# Run from command line
if __name__ == "__main__":
    if len(sys.argv) > 1:
        num = sys.argv[1]
        result = check_number(num)
        print(format_response(result))
    else:
        print("Usage: python dmc_checker.py 9999")
        print("       python dmc_checker.py --checkall  (verify data file exists)")
        print("       python dmc_checker.py --stats     (show data stats)")
        
        # Show stats
        data = load_data()
        if data:
            print(f"\n📊 Data Stats:")
            print(f"   Total draws: {len(data)}")
            print(f"   Data file: {DATA_FILE}")
        else:
            print("\n⚠️ No data file found!")
            print(f"   Create {DATA_FILE} or {JS_DATA_FILE}")