/**
 * Damacai Draw Results Checker
 * Stores user's 4D numbers and checks against latest draw
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, 'my_numbers.json');

// ============ NUMBER MANAGEMENT ============

function loadNumbers() {
    if (!fs.existsSync(DATA_FILE)) {
        return [];
    }
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data).numbers || [];
    } catch {
        return [];
    }
}

function saveNumbers(numbers) {
    fs.writeFileSync(DATA_FILE, JSON.stringify({ numbers }, null, 2));
}

function addNumber(num) {
    const numbers = loadNumbers();
    if (numbers.length >= 10) {
        console.log('❌ Maximum 10 numbers allowed!');
        return false;
    }
    if (!/^\d{4}$/.test(num)) {
        console.log('❌ Must be exactly 4 digits!');
        return false;
    }
    if (numbers.includes(num)) {
        console.log(`❌ ${num} already in your list!`);
        return false;
    }
    numbers.push(num);
    saveNumbers(numbers);
    console.log(`✅ Added ${num} (${numbers.length}/10 numbers)`);
    return true;
}

function removeNumber(num) {
    const numbers = loadNumbers();
    const idx = numbers.indexOf(num);
    if (idx === -1) {
        console.log(`❌ ${num} not in your list!`);
        return false;
    }
    numbers.splice(idx, 1);
    saveNumbers(numbers);
    console.log(`🗑️ Removed ${num} (${numbers.length}/10 numbers)`);
    return true;
}

function listNumbers() {
    const numbers = loadNumbers();
    if (numbers.length === 0) {
        console.log('📝 No numbers saved yet!');
    } else {
        console.log(`\n📝 Your ${numbers.length}/10 numbers:`);
        numbers.forEach((n, i) => console.log(`   ${i + 1}. ${n}`));
    }
    return numbers;
}

function clearNumbers() {
    saveNumbers([]);
    console.log('🗑️ All numbers cleared!');
}

// ============ FETCH RESULTS ============

function fetch(url) {
    return new Promise((resolve, reject) => {
        https.get(url, { timeout: 15000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

async function getLatestDraw() {
    for (let i = 0; i < 7; i++) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0];
        const url = `https://www.4dmoon.com/past-results/${dateStr}`;
        console.log(`Checking ${url}...`);
        
        try {
            const html = await fetch(url);
            
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

// ============ SIMULATION ============

function simulateDraw() {
    const pad = (n) => String(n).padStart(4, '0');
    
    // Generate random but realistic 4D numbers
    const simulate = () => pad(Math.floor(Math.random() * 10000));
    
    return {
        date: new Date().toISOString().split('T')[0],
        first: simulate(),
        second: simulate(),
        third: simulate(),
        source: 'SIMULATED'
    };
}

// ============ MAIN COMMANDS ============

async function checkResults(simulated = false) {
    const numbers = loadNumbers();
    if (numbers.length === 0) {
        console.log('📝 No numbers saved! Add numbers first:');
        console.log('   node check-draw.js add 1234');
        return;
    }
    
    console.log(simulated ? '\n=== SIMULATED DRAW TEST ===' : '\n=== Damacai Results Checker ===');
    listNumbers();
    
    const result = simulated ? simulateDraw() : await getLatestDraw();
    
    if (result) {
        console.log(`\n📅 Draw: ${result.date} (${result.source})`);
        console.log(`🎯 1st: ${result.first} | 2nd: ${result.second} | 3rd: ${result.third}`);
        console.log('\n=== Your Results ===');
        
        let matches = [];
        numbers.forEach(num => {
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
            console.log('❌ No matches.');
        } else {
            console.log('\n🎊 WON: ' + JSON.stringify(matches));
        }
    } else {
        console.log('Could not find draw results.');
    }
}

// ============ CLI ============

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'add' && args[1]) {
    addNumber(args[1]);
} else if (cmd === 'remove' && args[1]) {
    removeNumber(args[1]);
} else if (cmd === 'list') {
    listNumbers();
} else if (cmd === 'clear') {
    clearNumbers();
} else if (cmd === 'simulate') {
    checkResults(true).catch(console.error);
} else {
    checkResults(false).catch(console.error);
}