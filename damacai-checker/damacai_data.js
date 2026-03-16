// Damacai 4D Results - Scraped from 4dmoon.com
// Last updated: 2026-03-15

const damacaiData = [
    {
        "date": "2026-03-14",
        "number": "1994"
    },
    {
        "date": "2026-03-11",
        "number": "9638"
    },
    {
        "date": "2026-03-08",
        "number": "1790"
    },
    {
        "date": "2026-03-07",
        "number": "6064"
    },
    {
        "date": "2026-03-04",
        "number": "7498"
    },
    {
        "date": "2026-03-01",
        "number": "7372"
    },
    {
        "date": "2026-02-28",
        "number": "3955"
    },
    {
        "date": "2026-02-25",
        "number": "7238"
    },
    {
        "date": "2026-02-22",
        "number": "7470"
    },
    {
        "date": "2026-02-21",
        "number": "3236"
    },
    {
        "date": "2026-02-18",
        "number": "2262"
    },
    {
        "date": "2026-02-17",
        "number": "6475"
    },
    {
        "date": "2026-02-15",
        "number": "3033"
    },
    {
        "date": "2026-02-14",
        "number": "5991"
    },
    {
        "date": "2026-02-11",
        "number": "5194"
    },
    {
        "date": "2026-02-10",
        "number": "8242"
    },
    {
        "date": "2026-02-08",
        "number": "0686"
    },
    {
        "date": "2026-02-07",
        "number": "1198"
    },
    {
        "date": "2026-02-04",
        "number": "0083"
    },
    {
        "date": "2026-02-01",
        "number": "0571"
    },
    {
        "date": "2026-01-31",
        "number": "4427"
    },
    {
        "date": "2026-01-28",
        "number": "2496"
    },
    {
        "date": "2026-01-27",
        "number": "0645"
    },
    {
        "date": "2026-01-25",
        "number": "7116"
    },
    {
        "date": "2026-01-24",
        "number": "7776"
    },
    {
        "date": "2026-01-21",
        "number": "0073"
    },
    {
        "date": "2026-01-18",
        "number": "5794"
    },
    {
        "date": "2026-01-17",
        "number": "6272"
    }
];

// Build lookup map
const numberMap = new Map();
damacaiData.forEach(draw => {
    if (!numberMap.has(draw.number)) {
        numberMap.set(draw.number, []);
    }
    numberMap.get(draw.number).push(draw);
});
