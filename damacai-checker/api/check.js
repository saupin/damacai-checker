const data = require('./data.json');
const historical = require('../damacai_historical.json');

module.exports = (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  const { number } = req.query;
  
  if (!number || number.length !== 4) {
    return res.status(400).json({ error: 'Please provide a 4-digit number' });
  }
  
  const dates = data[number];
  
  if (!dates || dates.length === 0) {
    return res.status(200).json({
      found: false,
      number: number
    });
  }
  
  // Find which prize(s) won
  const prizes = [];
  dates.forEach(date => {
    const entry = historical.find(h => h.date === date);
    if (entry) {
      if (entry.first_prize === number) prizes.push({ date, prize: '1st' });
      else if (entry.second_prize === number) prizes.push({ date, prize: '2nd' });
      else if (entry.third_prize === number) prizes.push({ date, prize: '3rd' });
      else if (entry.starters && entry.starters.includes(number)) prizes.push({ date, prize: 'Starter' });
      else if (entry.consolation && entry.consolation.includes(number)) prizes.push({ date, prize: 'Consolation' });
    }
  });
  
  const prizeCounts = {
    '1st': prizes.filter(p => p.prize === '1st').length,
    '2nd': prizes.filter(p => p.prize === '2nd').length,
    '3rd': prizes.filter(p => p.prize === '3rd').length,
    'Starter': prizes.filter(p => p.prize === 'Starter').length,
    'Consolation': prizes.filter(p => p.prize === 'Consolation').length
  };
  
  return res.status(200).json({
    found: true,
    number: number,
    total: prizes.length,
    prizes: prizeCounts,
    details: prizes.slice(0, 30)
  });
};
