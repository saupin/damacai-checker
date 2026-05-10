import urllib.request, re

req = urllib.request.Request('https://www.4dmoon.com/past-results/2014-01-04', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

# Find Magnum section
start = html.find('Magnum 4D<br>')
end = html.find('SportsToto 4D<br>')
section = html[start:end] if end > 0 else html[start:start+5000]

print('Section length:', len(section))

# Show around 1st Prize
idx = section.find('1st Prize')
print('Around 1st Prize:')
print(repr(section[idx:idx+300]))
