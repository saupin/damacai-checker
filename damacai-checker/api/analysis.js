const data = require('./data.json');

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const numbers = Object.keys(data);
  
  // Calculate frequency
  const freq = {};
  numbers.forEach(n => {
    freq[n] = data[n].length;
  });
  
  // Sort by frequency
  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1]);
  
  // Get all dates
  const allDates = [];
  numbers.forEach(num => {
    if (data[num] && Array.isArray(data[num])) {
      data[num].forEach(d => allDates.push(d));
    }
  });
  const uniqueDates = [...new Set(allDates)].sort().reverse();
  
  // Last digit frequency
  const lastDigits = {};
  numbers.forEach(n => {
    const ld = n[3];
    lastDigits[ld] = (lastDigits[ld] || 0) + 1;
  });
  
  // First digit frequency  
  const firstDigits = {};
  numbers.forEach(n => {
    const fd = n[0];
    firstDigits[fd] = (firstDigits[fd] || 0) + 1;
  });
  
  // Pattern analysis
  let consecutive = 0, sumUnder10 = 0, sumOver30 = 0;
  numbers.forEach(n => {
    let hasConsec = false;
    let sum = 0;
    for(let i=0; i<n.length; i++) {
      sum += parseInt(n[i]);
      if(i < n.length-1 && parseInt(n[i+1]) === parseInt(n[i])+1) hasConsec = true;
    }
    if(hasConsec) consecutive++;
    if(sum < 10) sumUnder10++;
    if(sum > 30) sumOver30++;
  });
  
  const hot20 = sorted.slice(0, 20).map(item => ({ number: item[0], count: item[1] }));
  const firstHot3 = Object.entries(firstDigits).sort((a,b) => b[1]-a[1]).slice(0,3).map(item => item[0]);
  const lastHot3 = Object.entries(lastDigits).sort((a,b) => b[1]-a[1]).slice(0,3).map(item => item[0]);
  
  res.status(200).json({
    hotNumbers: hot20,
    totalNumbers: numbers.length,
    totalDraws: uniqueDates.length,
    lastDraw: uniqueDates[0],
    firstDigitHot: firstHot3,
    lastDigitHot: lastHot3,
    patterns: {
      consecutive: Math.round(consecutive / numbers.length * 100),
      sumUnder10: Math.round(sumUnder10 / numbers.length * 100),
      sumOver30: Math.round(sumOver30 / numbers.length * 100)
    }
  });
};
