/**
 * 4D Moon Scraper - Gets Damacai results
 * Scrapes both homepage (today) and past results pages
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

async function scrapeHomepage() {
    // Try to get today's results from homepage
    try {
        const html = await fetch('https://www.4dmoon.com/');
        
        // Look for Damacai section and extract numbers
        // Pattern: Look for 4-digit numbers near "Damacai" or "1+3D"
        const damacaiMatch = html.match(/Damacai[\s\S]{0,500}(\d{4})[\s\S]{0,100}(\d{4})[\s\S]{0,100}(\d{4})/i);
        
        if (damacaiMatch) {
            const today = new Date().toISOString().split('T')[0];
            return {
                date: today,
                first_prize: damacaiMatch[1],
                second_prize: damacaiMatch[2],
                third_prize: damacaiMatch[3]
            };
        }
        
        return null;
    } catch (e) {
        return null;
    }
}

async function scrapePastResult(dateStr) {
    // Get results from past results page - this works reliably
    const url = `https://www.4dmoon.com/past-results/${dateStr}`;
    
    try {
        const html = await fetch(url);
        
        // Find Damacai 1+3D section
        const damacaiMatch = html.match(/Damacai 1\+3D([\s\S]*?)(?=Magnum 4D|Singapore 4D|SportsToto|$)/i);
        
        if (!damacaiMatch) return null;
        
        const section = damacaiMatch[1];
        
        // Extract the first 3 four-digit numbers (1st, 2nd, 3rd prizes)
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
        
        const result = await scrapePastResult(dateStr);
        
        if (result && result.first_prize) {
            results.push(result);
            console.log(`✓ ${result.first_prize}`);
        } else {
            console.log('✗');
        }
        
        await sleep(300); // Be nice to server
    }
    
    return results;
}

function saveResults(results) {
    // Save as JS for website
    const jsData = results.map(r => ({ date: r.date, number: r.first_prize }));
    
    const jsContent = `// Damacai 4D Results - Scraped from 4dmoon.com
// Last updated: ${formatDate(new Date())}

const damacaiData = ${JSON.stringify(jsData, null, 4)};

// Build lookup map
const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) {
        numberMap.set(draw.number, []);
    }
    numberMap.get(draw.number).push(draw);
});
`;
    
    fs.writeFileSync('damacai_data.js', jsContent);
    console.log(`\n✓ Saved ${results.length} results to damacai_data.js`);
    
    // Also save as JSON
    fs.writeFileSync('damacai_results.json', JSON.stringify(results, null, 2));
    console.log('✓ Saved to damacai_results.json');
}

async function main() {
    console.log('='.repeat(50));
    console.log('4D Moon Scraper');
    console.log('='.repeat(50));
    console.log();
    
    // Scrape past results
    const results = await scrapeRange(60);
    
    if (results.length > 0) {
        saveResults(results);
        
        console.log('\n' + '='.repeat(50));
        console.log('Recent results:');
        results.slice(0, 5).forEach(r => {
            console.log(`  ${r.date}: ${r.first_prize}`);
        });
        console.log('='.repeat(50));
    } else {
        console.log('\nNo results found.');
    }
}

// Run scraper
main().catch(console.error);
