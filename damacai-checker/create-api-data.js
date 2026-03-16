const fs = require('fs');

// Read the historical data
const jsonData = JSON.parse(fs.readFileSync('./damacai_historical.json', 'utf8'));

// Group by number
const numberMap = {};
jsonData.forEach(draw => {
  const num = draw.first_prize;
  if (!numberMap[num]) {
    numberMap[num] = [];
  }
  numberMap[num].push(draw.date);
});

// Create API data
const apiData = {};
for (const [number, dates] of Object.entries(numberMap)) {
  apiData[number] = dates;
}

fs.writeFileSync('./api/data.json', JSON.stringify(apiData));
console.log(`✓ Created api/data.json with ${Object.keys(apiData).length} numbers`);
