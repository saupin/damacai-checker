const puppeteer = require('puppeteer');
const fs = require('fs');

// Load existing data
let historical = [];
try {
    historical = JSON.parse(fs.readFileSync('./damacai_historical.json', 'utf8'));
} catch (e) {
    console.log('Starting fresh');
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function scrapeDate(browser, dateStr) {
    const page = await browser.newPage();
    
    try {
        await page.goto(`https://www.4dmoon.com/past-results/${dateStr}`, {
            waitUntil: 'networkidle2',
            timeout: 20000
        });
        
        // Wait a bit for JS to render
        await sleep(2000);
        
        const content = await page.content();
        
        // Look for prize numbers - find 1st Prize section
        const prizeMatch = content.match(/1st\s*Prize[\s\S]*?<table[\s\S]*?>[\s\S]*?(\d{4})[\s\S]*?(\d{4})[\s\S]*?(\d{4})/i);
        
        if (!prizeMatch) {
            await page.close();
            return null;
        }
        
        // Find Special (Starter) numbers
        const specialMatch = content.match(/Special[\s\S]*?<table[^>]*>([\s\S]*?)<\/table>/i);
        let starters = [];
        if (specialMatch) {
            const nums = specialMatch[1].match(/(\d{4})/g);
            if (nums) starters = nums.slice(0, 10);
        }
        
        // Find Consolation numbers
        const consolationMatch = content.match(/Consolation[\s\S]*?<table[^>]*>([\s\S]*?)<\/table>/i);
        let consolation = [];
        if (consolationMatch) {
            const nums = consolationMatch[1].match(/(\d{4})/g);
            if (nums) consolation = nums.slice(0, 10);
        }
        
        const result = {
            date: dateStr,
            first_prize: prizeMatch[1],
            second_prize: prizeMatch[2],
            third_prize: prizeMatch[3],
            starters: starters,
            consolation: consolation
        };
        
        console.log(`  ✓ ${dateStr}: 1st=${result.first_prize}, starters=${starters.length}, consolation=${consolation.length}`);
        await page.close();
        return result;
        
    } catch (e) {
        await page.close();
        return null;
    }
}

async function scrapeRange(days = 365) {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const results = [];
    const today = new Date();
    let lastDate = null;
    
    for (let i = 0; i < days; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = formatDate(date);
        
        if (dateStr === lastDate) continue;
        lastDate = dateStr;
        
        // Skip if already in database with starters
        const exists = historical.find(h => h.date === dateStr && h.starters && h.starters.length > 0);
        if (exists) {
            console.log(`✗ ${dateStr}... already has starters`);
            continue;
        }
        
        // Skip if date has no draw (Wed/Sat/Sun only)
        const day = date.getDay();
        if (day !== 3 && day !== 6 && day !== 0) { // Wed=3, Sat=6, Sun=0
            console.log(`✗ ${dateStr}... no draw (${['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][day]})`);
            continue;
        }
        
        const result = await scrapeDate(browser, dateStr);
        
        if (result) {
            // Update existing or add new
            const idx = historical.findIndex(h => h.date === dateStr);
            if (idx >= 0) {
                historical[idx] = result;
            } else {
                historical.unshift(result);
            }
            results.push(result);
            console.log(`✓ ${dateStr}... ${result.first_prize}`);
        } else {
            console.log(`✗ ${dateStr}... no result`);
        }
        
        // Small delay
        await sleep(300);
    }
    
    await browser.close();
    
    // Save
    fs.writeFileSync('./damacai_historical.json', JSON.stringify(historical, null, 2));
    console.log(`\n✓ Saved ${results.length} results`);
    
    return results;
}

// Main
(async () => {
    console.log('==================================================');
    console.log('4D Moon Scraper (Puppeteer - Fixed)');
    console.log('==================================================');
    
    // Scrape 2025 only for now
    const results = await scrapeRange(400);
    
    console.log(`\nTotal new results: ${results.length}`);
})();
