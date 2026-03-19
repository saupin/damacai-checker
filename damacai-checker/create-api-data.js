const fs = require('fs');

// Read the historical data
const jsonData = JSON.parse(fs.readFileSync('./damacai_historical.json', 'utf8'));

// Group by number - include ALL prizes
const numberMap = {};
jsonData.forEach(draw => {
  // Add all prize categories
  const allNumbers = [
    draw.first_prize,
    draw.second_prize,
    draw.third_prize,
    ...(draw.starters || []),
    ...(draw.consolation || [])
  ];
  
  allNumbers.forEach(num => {
    if (num) {
      if (!numberMap[num]) {
        numberMap[num] = [];
      }
      numberMap[num].push(draw.date);
    }
  });
});

// Create API data
const apiData = {};
for (const [number, dates] of Object.entries(numberMap)) {
  apiData[number] = dates;
}

fs.writeFileSync('./api/data.json', JSON.stringify(apiData));
console.log(`✓ Created api/data.json with ${Object.keys(apiData).length} numbers`);
