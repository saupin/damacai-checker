# Damacai 4D First Prize Checker

A simple web application to check if a 4-digit number has ever won First Prize in Damacai 4D draws.

## Files

- `index.html` - The main web application
- `damacai_data.js` - Historical 4D results database (you need to create/update this)
- `scraper.py` - Python scraper for fetching results
- `scraper.js` - Node.js scraper for fetching results

## Quick Start

1. **Open the website:**
   ```
   Open index.html in your web browser
   ```

2. **Get real historical data:**
   
   Since Damacai's website uses JavaScript to load results dynamically, automatic scraping may not work. Here are your options:

### Option A: Manual Data Entry (Recommended)

1. Visit: https://www.damacai.com.my/past-draw-result/
2. Select historical dates from the calendar
3. Copy the 1st Prize numbers
4. Edit `damacai_data.js` and add entries in this format:
   ```javascript
   { date: '2024-12-28', number: '4821' },
   ```

### Option B: Use the Python Scraper

```bash
# Install requests if not already installed
pip install requests

# Run the scraper
python scraper.py
```

### Option C: Use the Node.js Scraper

```bash
# Install dependencies
npm install

# Run the scraper
npm run scrape
# or
node scraper.js
```

## Data Format

The `damacai_data.js` file should contain an array of objects with this structure:

```javascript
const damacaiData = [
    { date: '2024-12-28', number: '4821' },
    { date: '2024-12-25', number: '7395' },
    { date: '2024-12-21', number: '1567' },
    // ... more entries
];
```

## Features

- ✓ Check if a 4-digit number won First Prize
- ✓ Shows all dates the number won (if multiple)
- ✓ Clean, mobile-friendly interface
- ✓ Fast search with pre-built lookup map
- ✓ Works offline once loaded

## How It Works

1. The website loads the `damacaiData` array from `damacai_data.js`
2. It creates a lookup map for fast searching
3. When you enter a number, it checks the map instantly
4. Results are displayed with all winning dates

## Updating Data

To add new results:

1. Go to https://www.damacai.com.my/past-draw-result/
2. Find the latest draw results
3. Add a new entry to `damacaiData` array in `damacai_data.js`:
   ```javascript
   { date: 'YYYY-MM-DD', number: 'XXXX' },
   ```
4. Save and refresh the website

## Notes

- The website includes sample data for demonstration
- Replace with real data for accurate results
- Draws are typically on Wednesday, Saturday, and Sunday
- Special draws may occur on Tuesdays

## License

Free to use and modify.
