/**
 * Damacai Auto-Updater
 * Checks for and adds latest results to the database
 * Run this daily to keep data current
 */

const https = require('https');
const fs = require('fs');

const DATA_FILE = 'damacai_historical.json';
const PROGRESS_FILE = 'scrape_progress.json';

function fetch(url) {
    return new Promise((resolve, reject) => {
        https.get(url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
            timeout: 15000
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function scrapeDate(dateStr) {
    const url = `https://www.4dmoon.com/past-results/${dateStr}`;
    
    try {
        const html = await fetch(url);
        const damacaiMatch = html.match(/Damacai 1\+3D([\s\S]*?)(?=Magnum 4D|Singapore 4D|SportsToto|$)/i);
        
        if (!damacaiMatch) return null;
        
        const section = damacaiMatch[1];
        const numbers = section.match(/>(\d{4})</g);
        
        if (numbers && numbers.length >= 3) {
            const prizes = numbers.slice(0, 3).map(n => n.replace(/[><]/g, ''));
            return {
                date: dateStr,
                first_prize: prizes[0],
                second_prize: prizes[1],
                third_prize: prizes[2]
            };
        }
        return null;
    } catch (e) {
        return null;
    }
}

function getMissingDates(existingDates) {
    const missing = [];
    const today = new Date();
    
    // Check last 14 days for any new results
    for (let i = 0; i < 14; i++) {
        const d = new Date(today);
        d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0];
        
        if (!existingDates.includes(dateStr)) {
            missing.push(dateStr);
        }
    }
    
    return missing.reverse(); // Oldest first
}

async function updateDatabase() {
    console.log('🔄 Damacai Auto-Updater');
    console.log('========================');
    
    // Load existing data
    let existingData = [];
    let existingDates = [];
    
    if (fs.existsSync(DATA_FILE)) {
        existingData = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
        existingDates = existingData.map(d => d.date);
        console.log(`📊 Loaded ${existingData.length} existing results`);
    }
    
    // Find missing dates
    const toCheck = getMissingDates(existingDates);
    
    if (toCheck.length === 0) {
        console.log('✅ Database is up to date!');
        return;
    }
    
    console.log(`🔍 Checking ${toCheck.length} dates for new results...\n`);
    
    const newResults = [];
    
    for (const dateStr of toCheck) {
        process.stdout.write(`  ${dateStr}... `);
        
        const result = await scrapeDate(dateStr);
        
        if (result && result.first_prize) {
            newResults.push(result);
            console.log(`✓ ${result.first_prize}`);
        } else {
            console.log('✗');
        }
        
        // Small delay
        await new Promise(r => setTimeout(r, 300));
    }
    
    if (newResults.length > 0) {
        // Merge and sort
        const allData = [...existingData, ...newResults];
        allData.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // Save JSON
        fs.writeFileSync(DATA_FILE, JSON.stringify(allData, null, 2));
        
        // Save JS for website
        const jsData = allData.map(r => ({ date: r.date, number: r.first_prize }));
        const jsContent = `// Damacai 4D Results - Auto-updated
// Total draws: ${jsData.length}
// Last updated: ${new Date().toISOString().split('T')[0]}

const damacaiData = ${JSON.stringify(jsData, null, 4)};

const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) numberMap.set(draw.number, []);
    numberMap.get(draw.number).push(draw);
});
`;
        fs.writeFileSync('damacai_historical.js', jsContent);
        
        // Update progress file if exists
        if (fs.existsSync(PROGRESS_FILE)) {
            const progress = JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf8'));
            newResults.forEach(r => {
                if (!progress.completed.includes(r.date)) {
                    progress.completed.push(r.date);
                    progress.results.push(r);
                }
            });
            fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
        }
        
        console.log(`\n✅ Added ${newResults.length} new results!`);
        console.log(`📁 Total database: ${allData.length} draws`);
    } else {
        console.log('\n✅ No new results found');
    }
    
    console.log('\n========================');
    console.log('Update complete!');
}

// Run updater
updateDatabase().catch(console.error);
