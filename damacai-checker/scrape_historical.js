/**
 * 4D Moon Historical Scraper
 * Scrapes Damacai results from 2014 to present
 * Saves progress to resume if interrupted
 */

const https = require('https');
const fs = require('fs');

// Configuration
const START_YEAR = 2006;
const END_YEAR = 2026;
const DELAY_MS = 300; // Delay between requests
const PROGRESS_FILE = 'scrape_progress.json';
const OUTPUT_FILE = 'damacai_historical.json';

// Load progress
let progress = { completed: [], results: [] };
if (fs.existsSync(PROGRESS_FILE)) {
    progress = JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf8'));
    console.log(`Loaded progress: ${progress.results.length} results already scraped`);
}

function fetch(url) {
    return new Promise((resolve, reject) => {
        https.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout: 15000
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function scrapeDate(dateStr) {
    const url = `https://www.4dmoon.com/past-results/${dateStr}`;
    
    try {
        const html = await fetch(url);
        
        // Find Damacai 1+3D section
        const damacaiMatch = html.match(/Damacai 1\+3D([\s\S]*?)(?=Magnum 4D|Singapore 4D|SportsToto|$)/i);
        
        if (!damacaiMatch) return null;
        
        const section = damacaiMatch[1];
        
        // Extract draw info
        const drawInfo = section.match(/(#\d+\/\d+)/)?.[1] || '';
        
        // Extract all 4-digit numbers
        const numbers = section.match(/>(\d{4})</g);
        
        if (numbers && numbers.length >= 3) {
            const prizes = numbers.slice(0, 3).map(n => n.replace(/[><]/g, ''));
            return {
                date: dateStr,
                first_prize: prizes[0],
                second_prize: prizes[1],
                third_prize: prizes[2],
                draw_info: drawInfo
            };
        }
        
        return null;
    } catch (e) {
        return null;
    }
}

function getDatesRange() {
    const dates = [];
    const start = new Date(`${START_YEAR}-01-01`);
    const end = new Date();
    
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        dates.push(d.toISOString().split('T')[0]);
    }
    
    return dates;
}

function saveProgress() {
    fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
}

function saveResults() {
    // Sort by date descending
    const sorted = progress.results.sort((a, b) => 
        new Date(b.date) - new Date(a.date)
    );
    
    // Save as JSON
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(sorted, null, 2));
    
    // Save as JS for website
    const jsData = sorted.map(r => ({ date: r.date, number: r.first_prize }));
    
    const jsContent = `// Damacai 4D Results - Historical Data (2014-${END_YEAR})
// Scraped from 4dmoon.com
// Total draws: ${jsData.length}
// Last updated: ${new Date().toISOString().split('T')[0]}

const damacaiData = ${JSON.stringify(jsData, null, 4)};

// Build lookup map
const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) {
        numberMap.set(draw.number, []);
    }
    numberMap.get(draw.number).push(draw);
});

console.log('Loaded', damacaiData.length, 'historical Damacai results');
`;
    
    fs.writeFileSync('damacai_historical.js', jsContent);
    
    return { json: sorted.length, js: jsData.length };
}

async function scrapeAll() {
    const allDates = getDatesRange();
    const total = allDates.length;
    const remaining = allDates.filter(d => !progress.completed.includes(d));
    
    console.log('='.repeat(60));
    console.log('4D Moon Historical Scraper');
    console.log('='.repeat(60));
    console.log(`Date range: ${START_YEAR} to ${END_YEAR}`);
    console.log(`Total dates: ${total}`);
    console.log(`Already scraped: ${progress.completed.length}`);
    console.log(`Remaining: ${remaining.length}`);
    console.log('='.repeat(60));
    console.log();
    
    if (remaining.length === 0) {
        console.log('All dates already scraped!');
        const counts = saveResults();
        console.log(`\n✓ Saved ${counts.js} results to damacai_historical.js`);
        return;
    }
    
    let successCount = 0;
    let failCount = 0;
    let consecutiveFails = 0;
    
    for (let i = 0; i < remaining.length; i++) {
        const dateStr = remaining[i];
        const currentNum = progress.completed.length + i + 1;
        const percent = ((currentNum / total) * 100).toFixed(1);
        
        process.stdout.write(`[${currentNum}/${total} ${percent}%] ${dateStr}... `);
        
        const result = await scrapeDate(dateStr);
        
        if (result && result.first_prize) {
            progress.results.push(result);
            successCount++;
            consecutiveFails = 0;
            console.log(`✓ ${result.first_prize}`);
        } else {
            failCount++;
            consecutiveFails++;
            console.log('✗');
        }
        
        progress.completed.push(dateStr);
        
        // Save progress every 50 dates
        if (i % 50 === 0) {
            saveProgress();
            console.log(`  💾 Progress saved (${progress.results.length} results)`);
        }
        
        // Pause if too many consecutive failures (possible rate limit)
        if (consecutiveFails >= 10) {
            console.log('\n⚠ Too many consecutive failures. Waiting 30 seconds...');
            await sleep(30000);
            consecutiveFails = 0;
        }
        
        // Normal delay
        await sleep(DELAY_MS);
    }
    
    // Final save
    saveProgress();
    const counts = saveResults();
    
    console.log();
    console.log('='.repeat(60));
    console.log('Scraping Complete!');
    console.log('='.repeat(60));
    console.log(`Total dates checked: ${remaining.length}`);
    console.log(`Results found: ${successCount}`);
    console.log(`No draw on date: ${failCount}`);
    console.log(`Total in database: ${counts.js} results`);
    console.log();
    console.log('Files saved:');
    console.log(`  - ${OUTPUT_FILE}`);
    console.log(`  - damacai_historical.js`);
    console.log(`  - ${PROGRESS_FILE}`);
    console.log('='.repeat(60));
}

// Handle interruption
process.on('SIGINT', () => {
    console.log('\n\nInterrupted! Saving progress...');
    saveProgress();
    console.log(`Progress saved to ${PROGRESS_FILE}`);
    console.log(`Resume anytime by running: node scrape_historical.js`);
    process.exit(0);
});

// Run
scrapeAll().catch(err => {
    console.error('Error:', err);
    saveProgress();
    process.exit(1);
});
