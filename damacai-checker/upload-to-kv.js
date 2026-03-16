const fs = require('fs');
const { createClient } = require('@vercel/kv');

async function uploadData() {
  // Read the historical data
  const jsonData = JSON.parse(fs.readFileSync('./damacai_historical.json', 'utf8'));
  
  console.log(`Uploading ${jsonData.length} results to Vercel KV...`);
  
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
  
  // This would need actual KV credentials to work
  // For now, we'll create a local JSON that can be imported
  
  fs.writeFileSync('./kv_data.json', JSON.stringify(numberMap, null, 2));
  console.log('✓ Created kv_data.json for import');
  console.log('');
  console.log('To upload to Vercel KV:');
  console.log('1. Go to https://vercel.com/dashboard');
  console.log('2. Select your project → Storage → Create KV Database');
  console.log('3. Use the Vercel dashboard to bulk import kv_data.json');
}

uploadData().catch(console.error);
