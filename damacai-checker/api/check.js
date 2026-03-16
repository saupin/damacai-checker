const data = require('./data.json');

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
  
  if (dates && dates.length > 0) {
    return res.status(200).json({
      found: true,
      number: number,
      count: dates.length,
      dates: dates
    });
  } else {
    return res.status(200).json({
      found: false,
      number: number
    });
  }
};
