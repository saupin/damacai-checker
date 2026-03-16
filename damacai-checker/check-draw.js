/**
 * Damacai Draw Results Checker
 * Runs after draws to check results
 */

const https = require('https');

function fetch(url) {
    return new Promise((resolve, reject) => {
        https.get(url, { timeout: 15000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function getLatestDrawFromMainPage() {
    const url = 'https://www.4dmoon.com/';
    console.log(`Checking main page: ${url}...`);
    
    try {
        const html = await fetch(url);
        
        // Find Damacai section - look for the pattern on the main page
        const damacaiMatch = html.match(/Damacai 1\+3D[\s\S]*?1st Prize[\s\S]*?(\d{4})[\s\S]*?2nd[\s\S]*?(\d{4})[\s\S]*?3rd[\s\S]*?(\d{4})/i);
        
        if (damacaiMatch) {
            const today = new Date().toISOString().split('T')[0];
            return {
                date: today,
                first: damacaiMatch[1],
                second: damacaiMatch[2],
                third: damacaiMatch[3],
                source: 'main page'
            };
        }
    } catch (e) {
        console.log('Error checking main page:', e.message);
    }
    return null;
}

async function getLatestDraw() {
    // First try main page for today's results
    const mainPageResult = await getLatestDrawFromMainPage();
    if (mainPageResult) {
        return mainPageResult;
    }
    
    // Fallback: try last 7 days (draws are Wed, Sat, Sun, sometimes Tue)
    for (let i = 0; i < 7; i++) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0];
        const url = `https://www.4dmoon.com/past-results/${dateStr}`;
        console.log(`Checking ${url}...`);
        
        try {
            const html = await fetch(url);
            
            // Find Damacai section
            const match = html.match(/Damacai 1\+3D([\s\S]*?)(?=Magnum|SportsToto|$)/i);
            if (!match) continue;
            
            const section = match[1];
            const numbers = section.match(/>(\d{4})</g);
            
            if (numbers && numbers.length >= 3) {
                return {
                    date: dateStr,
                    first: numbers[0].replace(/[><]/g, ''),
                    second: numbers[1].replace(/[><]/g, ''),
                    third: numbers[2].replace(/[><]/g, ''),
                    source: `past results page`
                };
            }
        } catch (e) {
            console.log('Error:', e.message);
        }
    }
    return null;
}

// Our suggested numbers
const suggestedNumbers = [
    '0500', '5755', '5005', '7707', '0750',
    '0421', '8458', '2001', '8441', '4777',
    '2457', '2277', '1529', '7545', '7452'
];

async function main() {
    console.log('=== Damacai Results Checker ===\n');
    
    const result = await getLatestDraw();
    
    if (result) {
        console.log(`📅 Latest Draw: ${result.date} (from ${result.source || 'unknown'})`);
        console.log(`🎯 1st Prize: ${result.first}`);
        console.log(`🥈 2nd: ${result.second}`);
        console.log(`🥉 3rd: ${result.third}`);
        
        console.log('\n=== Checking your numbers ===');
        
        let matches = [];
        suggestedNumbers.forEach(num => {
            if (num === result.first) {
                console.log(`🎉 FIRST PRIZE: ${num} !!!`);
                matches.push({ num, prize: '1ST' });
            } else if (num === result.second) {
                console.log(`🥈 2nd Prize: ${num}`);
                matches.push({ num, prize: '2ND' });
            } else if (num === result.third) {
                console.log(`🥉 3rd Prize: ${num}`);
                matches.push({ num, prize: '3RD' });
            }
        });
        
        if (matches.length === 0) {
            console.log('\n❌ No matches this time. Better luck next draw!');
        }
        
        // Output for cron
        if (matches.length > 0) {
            console.log('\n🎊 WON: ' + JSON.stringify(matches));
        }
    } else {
        console.log('Could not find latest draw results');
    }
}

main().catch(console.error);
