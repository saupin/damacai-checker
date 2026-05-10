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
        
        // Wait for tables to render
        await sleep(2000);
        
        // Use page.evaluate to extract data from the DOM
        const result = await page.evaluate(() => {
            // Find all tables
            const tables = document.querySelectorAll('table');
            
            for (const table of tables) {
                const text = table.textContent || '';
                
                // Look for table with "1st Prize" and "2nd Prize" and "3rd Prize"
                if (text.includes('1st Prize') && text.includes('2nd Prize') && text.includes('3rd Prize')) {
                    // Get all 4-digit numbers from this table
                    const nums = text.match(/(\d{4})/g);
                    if (nums && nums.length >= 3) {
                        // First 3 should be 1st, 2nd, 3rd
                        return {
                            first: nums[0],
                            second: nums[1],
                            third: nums[2]
                        };
                    }
                }
            }
            return null;
        });
        
        if (!result) {
            await page.close();
            return null;
        }
        
        // Get Special/Starter numbers
        const starters = await page.evaluate(() => {
            const tables = document.querySelectorAll('table');
            for (const table of tables) {
                const text = table.textContent || '';
                if (text.includes('Special') && !text.includes('1st Prize')) {
                    const nums = text.match(/(\d{4})/g);
                    if (nums) return nums.slice(0, 10);
                }
            }
            return [];
        });
        
        // Get Consolation numbers
        const consolation = await page.evaluate(() => {
            const tables = document.querySelectorAll('table');
            for (const table of tables) {
                const text = table.textContent || '';
                if (text.includes('Consolation') && !text.includes('Special')) {
                    const nums = text.match(/(\d{4})/g);
                    if (nums) return nums.slice(0, 10);
                }
            }
            return [];
        });
        
        const data = {
            date: dateStr,
            first_prize: result.first,
            second_prize: result.second,
            third_prize: result.third,
            starters: starters,
            consolation: consolation
        };
        
        console.log(`  ✓ ${dateStr}: 1st=${data.first_prize}, starters=${starters.length}, consolation=${consolation.length}`);
        await page.close();
        return data;
        
    } catch (e) {
        console.log(`  Error: ${e.message}`);
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
        
        // Skip if already has starters
        const exists = historical.find(h => h.date === dateStr && h.starters && h.starters.length > 0);
        if (exists) {
            console.log(`✗ ${dateStr}... already has starters`);
            continue;
        }
        
        // Skip non-draw days
        const day = date.getDay();
        if (day !== 3 && day !== 6 && day !== 0) {
            console.log(`✗ ${dateStr}... no draw`);
            continue;
        }
        
        const result = await scrapeDate(browser, dateStr);
        
        if (result) {
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
        
        await sleep(300);
    }
    
    await browser.close();
    
    fs.writeFileSync('./damacai_historical.json', JSON.stringify(historical, null, 2));
    console.log(`\n✓ Saved ${results.length} results`);
    
    return results;
}

// Main
(async () => {
    console.log('==================================================');
    console.log('4D Moon Scraper (Puppeteer - DOM Version)');
    console.log('==================================================');
    
    const results = await scrapeRange(400);
    
    console.log(`\nTotal new results: ${results.length}`);
})();
