const data = require('./data.json');

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  
  const numbers = Object.keys(data);
  const allDates = [];
  
  // Collect all dates
  numbers.forEach(num => {
    if (data[num] && Array.isArray(data[num])) {
      data[num].forEach(d => allDates.push(d));
    }
  });
  
  // Get unique dates and sort
  const uniqueDates = [...new Set(allDates)].sort().reverse();
  
  // Count frequency
  const freq = {};
  numbers.forEach(num => {
    freq[num] = data[num].length;
  });
  
  // Top 5 hot numbers
  const topHot = Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([num, count]) => num + ' (' + count + 'x)');
  
  res.status(200).json({
    totalNumbers: numbers.length.toLocaleString(),
    totalDraws: uniqueDates.length.toLocaleString(),
    lastDraw: uniqueDates[0] || 'N/A',
    topHotNumbers: topHot.join(', ')
  });
};
