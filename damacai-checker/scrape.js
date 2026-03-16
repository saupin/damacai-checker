/**
 * 4D Moon Scraper - No dependencies version
 * Uses Node.js built-in https module
 */

const https = require('https');
const fs = require('fs');

function fetch(url) {
    return new Promise((resolve, reject) => {
        https.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout: 10000
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function scrape4DMoon(dateStr) {
    const url = `https://www.4dmoon.com/past-results/${dateStr}`;
    
    try {
        const html = await fetch(url);
        
        // Find Damacai section
        const damacaiMatch = html.match(/Damacai 1\+3D([\s\S]*?)(?=Magnum 4D|Singapore 4D|$)/i);
        
        if (!damacaiMatch) {
            console.log(`  No Damacai data for ${dateStr}`);
            return null;
        }
        
        const section = damacaiMatch[1];
        
        // Extract draw info
        const drawInfo = section.match(/(#\d+\/\d+)/)?.[1] || '';
        
        // Extract all 4-digit numbers from the section
        const numbers = section.match(/>(\d{4})</g);
        
        if (numbers && numbers.length >= 3) {
            // First 3 numbers are 1st, 2nd, 3rd prizes
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
        
    } catch (error) {
        console.log(`  Error: ${error.message}`);
        return null;
    }
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function scrapeRange(days = 30) {
    const results = [];
    const today = new Date();
    
    console.log(`Scraping ${days} days from 4dmoon.com...\n`);
    
    for (let i = 0; i < days; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = formatDate(date);
        
        process.stdout.write(`${dateStr}... `);
        
        const result = await scrape4DMoon(dateStr);
        
        if (result && result.first_prize) {
            results.push(result);
            console.log(`✓ ${result.first_prize}`);
        } else {
            console.log('✗');
        }
        
        // Be nice to the server
        await sleep(500);
    }
    
    return results;
}

function saveAsJS(results, filename = 'damacai_data.js') {
    const jsData = results
        .filter(r => r.first_prize)
        .map(r => ({ date: r.date, number: r.first_prize }));
    
    const jsContent = `// Damacai 4D First Prize Results
// Scraped from 4dmoon.com on ${formatDate(new Date())}

const damacaiData = ${JSON.stringify(jsData, null, 4)};

// Create lookup map
const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) {
        numberMap.set(draw.number, []);
    }
    numberMap.get(draw.number).push(draw);
});
`;
    
    fs.writeFileSync(filename, jsContent);
    console.log(`\n✓ Saved ${jsData.length} results to ${filename}`);
}

async function main() {
    console.log('='.repeat(50));
    console.log('4D Moon Damacai Scraper (No dependencies)');
    console.log('='.repeat(50));
    console.log();
    
    const results = await scrapeRange(30);
    
    if (results.length > 0) {
        console.log(`\nTotal results: ${results.length}`);
        
        // Save as JSON
        fs.writeFileSync('damacai_results.json', JSON.stringify(results, null, 2));
        console.log('✓ Saved to damacai_results.json');
        
        // Save as JS
        saveAsJS(results);
        
        console.log('\n📋 Next steps:');
        console.log('  1. Copy damacai_data.js contents');
        console.log('  2. Paste into index.html to replace sample data');
    } else {
        console.log('\nNo results found.');
    }
    
    console.log();
    console.log('='.repeat(50));
}

main().catch(console.error);
