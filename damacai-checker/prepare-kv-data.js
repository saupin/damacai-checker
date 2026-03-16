const fs = require('fs');

// Read the historical data
const jsonData = JSON.parse(fs.readFileSync('./damacai_historical.json', 'utf8'));

console.log(`Processing ${jsonData.length} results...`);

// Group by number
const numberMap = {};
jsonData.forEach(draw => {
  const num = draw.first_prize;
  if (!numberMap[num]) {
    numberMap[num] = [];
  }
  numberMap[num].push(draw.date);
});

console.log(`Found ${Object.keys(numberMap).length} unique numbers`);

// Create a JSON file for each number (for KV import)
const kvData = [];
for (const [number, dates] of Object.entries(numberMap)) {
  kvData.push({
    key: `number:${number}`,
    value: dates
  });
}

fs.writeFileSync('./kv-import-data.json', JSON.stringify(kvData, null, 2));
console.log('✓ Created kv-import-data.json');
console.log('');
console.log('Next steps:');
console.log('1. Install dependencies: npm install');
console.log('2. Run: npx vercel');
console.log('3. Go to Vercel Dashboard → Storage → Create KV Database');
console.log('4. Link KV to your project');
console.log('5. Run: node import-to-kv.js');
