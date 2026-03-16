/**
 * Damacai 4D Results Scraper
 * Fetches historical 4D results from Damacai
 */

const axios = require('axios');
const fs = require('fs');

class DamacaiScraper {
    constructor() {
        this.baseURL = 'https://www.damacai.com.my';
        this.session = axios.create({
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.damacai.com.my/'
            },
            timeout: 10000
        });
        this.results = [];
    }

    /**
     * Format date for API: DD/MM/YYYY
     */
    formatDate(date) {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        return `${day}/${month}/${year}`;
    }

    /**
     * Format date for JS: YYYY-MM-DD
     */
    formatDateISO(date) {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        return `${year}-${month}-${day}`;
    }

    /**
     * Try to fetch results for a specific date
     */
    async fetchDate(dateStr) {
        try {
            // Try different potential endpoints
            const endpoints = [
                `/umbraco/api/ResultApi/GetResultByDate?date=${encodeURIComponent(dateStr)}`,
                `/api/results?date=${encodeURIComponent(dateStr)}`,
                `/callpassresult?pastdate=${dateStr.replace(/\//g, '')}`
            ];

            for (const endpoint of endpoints) {
                try {
                    console.log(`  Trying endpoint: ${endpoint}`);
                    const response = await this.session.get(`${this.baseURL}${endpoint}`);
                    
                    if (response.data) {
                        console.log(`  ✓ Got response from ${endpoint}`);
                        return this.parseResult(response.data, dateStr);
                    }
                } catch (e) {
                    // Continue to next endpoint
                }
            }

            return null;
        } catch (error) {
            return null;
        }
    }

    /**
     * Parse result data from various formats
     */
    parseResult(data, dateStr) {
        try {
            // Handle different API response formats
            let result = null;

            if (typeof data === 'string') {
                // Try to parse as JSON
                try {
                    data = JSON.parse(data);
                } catch (e) {
                    // Not JSON, try regex extraction
                    const match = data.match(/(\d{4})/g);
                    if (match) {
                        return {
                            date: dateStr,
                            first_prize: match[0] || null,
                            second_prize: match[1] || null,
                            third_prize: match[2] || null
                        };
                    }
                }
            }

            if (typeof data === 'object') {
                // Common API response formats
                result = {
                    date: dateStr,
                    first_prize: data.p1 || data.firstPrize || data['1st'] || null,
                    second_prize: data.p2 || data.secondPrize || data['2nd'] || null,
                    third_prize: data.p3 || data.thirdPrize || data['3rd'] || null
                };
            }

            return result;
        } catch (error) {
            return null;
        }
    }

    /**
     * Scrape a date range
     */
    async scrapeRange(startDate, endDate) {
        const results = [];
        let current = new Date(startDate);
        const end = new Date(endDate);

        console.log(`Scraping from ${this.formatDate(startDate)} to ${this.formatDate(endDate)}...\n`);

        while (current <= end) {
            const dateStr = this.formatDate(current);
            console.log(`Fetching: ${dateStr}`);
            
            const result = await this.fetchDate(dateStr);
            
            if (result && result.first_prize) {
                results.push(result);
                console.log(`  ✓ 1st Prize: ${result.first_prize}\n`);
            } else {
                console.log(`  ✗ No result\n`);
            }

            // Be nice to the server
            await this.sleep(1000);
            
            // Move to next day
            current.setDate(current.getDate() + 1);
        }

        return results;
    }

    /**
     * Scrape last N days
     */
    async scrapeLastNDays(days) {
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - days);
        
        return this.scrapeRange(start, end);
    }

    /**
     * Sleep helper
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Save results to JSON
     */
    saveToJSON(results, filename = 'damacai_results.json') {
        fs.writeFileSync(filename, JSON.stringify(results, null, 2));
        console.log(`Saved ${results.length} results to ${filename}`);
    }

    /**
     * Save results to JS for website
     */
    saveToJS(results, filename = 'damacai_data.js') {
        let js = `// Damacai 4D First Prize Results\n`;
        js += `// Auto-generated on ${new Date().toISOString()}\n\n`;
        js += `const damacaiData = [\n`;
        
        results.forEach(r => {
            if (r.first_prize) {
                const isoDate = this.formatDateISO(r.date.split('/').reverse().join('-'));
                js += `    { date: '${isoDate}', number: '${r.first_prize}' },\n`;
            }
        });
        
        js += `];\n\n`;
        js += `// Create lookup map\n`;
        js += `const numberMap = new Map();\n`;
        js += `damacaiData.forEach(draw => {\n`;
        js += `    if (!numberMap.has(draw.number)) {\n`;
        js += `        numberMap.set(draw.number, []);\n`;
        js += `    }\n`;
        js += `    numberMap.get(draw.number).push(draw);\n`;
        js += `});\n`;

        fs.writeFileSync(filename, js);
        console.log(`Saved ${results.length} results to ${filename}`);
    }
}


/**
 * Alternative: Scrape from cached/sample data
 */
function createSampleData() {
    const sampleData = [
        { date: '2024-12-28', number: '4821' },
        { date: '2024-12-25', number: '7395' },
        { date: '2024-12-21', number: '1567' },
        { date: '2024-12-18', number: '9823' },
        { date: '2024-12-14', number: '4056' },
        { date: '2024-12-11', number: '2189' },
        { date: '2024-12-07', number: '6742' },
        { date: '2024-12-04', number: '8391' },
        { date: '2024-11-30', number: '5620' },
        { date: '2024-11-27', number: '9473' },
        { date: '2024-11-23', number: '3158' },
        { date: '2024-11-20', number: '7804' },
        { date: '2024-11-16', number: '1287' },
        { date: '2024-11-13', number: '6539' },
        { date: '2024-11-09', number: '4961' },
        { date: '2024-11-06', number: '8025' },
        { date: '2024-11-02', number: '3748' },
        { date: '2024-10-30', number: '9156' },
        { date: '2024-10-26', number: '2473' },
        { date: '2024-10-23', number: '6810' },
    ];

    let js = `// Damacai 4D First Prize Results - SAMPLE DATA\n`;
    js += `// Replace with real data from https://www.damacai.com.my/past-draw-result/\n\n`;
    js += `const damacaiData = ${JSON.stringify(sampleData, null, 4)};\n\n`;
    js += `// Create lookup map\n`;
    js += `const numberMap = new Map();\n`;
    js += `damacaiData.forEach(draw => {\n`;
    js += `    if (!numberMap.has(draw.number)) {\n`;
    js += `        numberMap.set(draw.number, []);\n`;
    js += `    }\n`;
    js += `    numberMap.get(draw.number).push(draw);\n`;
    js += `});\n`;

    fs.writeFileSync('damacai_data_sample.js', js);
    console.log('Created sample data file: damacai_data_sample.js');
    return sampleData;
}


/**
 * Main execution
 */
async function main() {
    console.log('='.repeat(50));
    console.log('Damacai 4D Results Scraper');
    console.log('='.repeat(50));
    console.log();

    const scraper = new DamacaiScraper();

    // Try to scrape last 7 days
    console.log('Attempting to scrape recent results...\n');
    const results = await scraper.scrapeLastNDays(7);

    if (results.length > 0) {
        console.log(`\n✓ Successfully scraped ${results.length} results`);
        scraper.saveToJSON(results);
        scraper.saveToJS(results);
    } else {
        console.log('\n✗ Automatic scraping failed.');
        console.log('\nPossible reasons:');
        console.log('  - Website requires JavaScript rendering');
        console.log('  - API endpoints have changed');
        console.log('  - Rate limiting or blocking');
        console.log('\nCreating sample data instead...\n');
        
        createSampleData();
        
        console.log('\nTo get real data:');
        console.log('  1. Visit: https://www.damacai.com.my/past-draw-result/');
        console.log('  2. Manually collect 1st Prize numbers');
        console.log('  3. Update damacai_data_sample.js with real data');
    }

    console.log();
    console.log('='.repeat(50));
    console.log('Done!');
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { DamacaiScraper, createSampleData };
