const fs = require('fs');
const { createClient } = require('@vercel/kv');

async function importData() {
  // Check if KV_REST_API_URL is set
  if (!process.env.KV_REST_API_URL) {
    console.log('⚠️  KV_REST_API_URL not found in environment');
    console.log('Make sure to:');
    console.log('1. Link your project: npx vercel link');
    console.log('2. Pull env vars: npx vercel env pull');
    console.log('');
    console.log('Or manually set KV_REST_API_URL and KV_REST_API_TOKEN');
    return;
  }
  
  const kv = createClient({
    url: process.env.KV_REST_API_URL,
    token: process.env.KV_REST_API_TOKEN,
  });
  
  // Read the prepared data
  const kvData = JSON.parse(fs.readFileSync('./kv-import-data.json', 'utf8'));
  
  console.log(`Importing ${kvData.length} numbers to Vercel KV...`);
  
  let success = 0;
  let failed = 0;
  
  for (const item of kvData) {
    try {
      // Store as list
      await kv.rpush(item.key, ...item.value);
      success++;
      process.stdout.write(`\rProgress: ${success}/${kvData.length}`);
    } catch (error) {
      failed++;
      console.error(`\nFailed to import ${item.key}:`, error.message);
    }
  }
  
  console.log('');
  console.log('');
  console.log('✓ Import complete!');
  console.log(`  Success: ${success}`);
  console.log(`  Failed: ${failed}`);
}

importData().catch(console.error);
