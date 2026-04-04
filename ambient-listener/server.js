import express from 'express';
import multer from 'multer';
import { createWriteStream, unlinkSync, existsSync } from 'fs';
import { join, basename } from 'path';
import { pipeline } from 'stream/promises';
import os from 'os';
import https from 'https';
import http from 'http';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3456;

// Configuration - use environment variables or defaults
const WHISPER_API_KEY = process.env.WHISPER_API_KEY || '';
const SUMMARIZER_API_KEY = process.env.SUMMARIZER_API_KEY || process.env.KIMI_API_KEY || '';
const SUMMARIZER_BASE_URL = process.env.SUMMARIZER_BASE_URL || 'https://api.moonshot.ai/v1';
const SUMMARIZER_MODEL = process.env.SUMMARIZER_MODEL || 'moonshot/kimi-k2.5';

// Serve static files (including the shortcut image)
app.use(express.static('public'));

// Configure multer for audio file uploads
const storage = multer.diskStorage({
  destination: os.tmpdir(),
  filename: (req, file, cb) => {
    const ext = file.originalname.split('.').pop() || 'm4a';
    cb(null, `ambient-audio-${Date.now()}.${ext}`);
  }
});
const upload = multer({ 
  storage,
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB max
});

// Health check
app.get('/', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'Ambient Listener API',
    endpoints: {
      POST: '/transcribe - Upload audio for transcription and summarization',
      GET: '/shortcut - Get iOS Shortcut instructions'
    }
  });
});

// iOS Shortcut instructions
app.get('/shortcut', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>Ambient Listener - iOS Shortcut Setup</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; }
    h1 { color: #333; }
    code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }
    pre { background: #2d2d2d; color: #fff; padding: 15px; border-radius: 8px; overflow-x: auto; }
    .step { margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }
    .warning { background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; }
  </style>
</head>
<body>
  <h1>🎙️ Ambient Listener - iOS Shortcut Setup</h1>
  
  <div class="warning">
    <strong>⚠️ Important:</strong> This API must be accessible from your iPhone. 
    Use a tool like <code>ngrok</code> or <code>localtunnel</code> to expose it.
  </div>
  
  <h2>Setup Instructions</h2>
  
  <div class="step">
    <h3>Step 1: Expose this server</h3>
    <p>On your PC, run:</p>
    <pre>npx localtunnel --port 3456</pre>
    <p>Copy the URL (e.g., https://your-name.loca.lt)</p>
  </div>
  
  <div class="step">
    <h3>Step 2: Set API Keys (Optional)</h3>
    <p>Create a <code>.env</code> file or set environment variables:</p>
    <pre>
WHISPER_API_KEY=your-openai-api-key
KIMI_API_KEY=your-kimi-api-key
SUMMARIZER_BASE_URL=https://api.moonshot.ai/v1
SUMMARIZER_MODEL=moonshot/kimi-k2.5
    </pre>
  </div>
  
  <div class="step">
    <h3>Step 3: Build the iOS Shortcut</h3>
    <ol>
      <li>Open the <strong>Shortcuts</strong> app on your iPhone</li>
      <li>Tap <strong>+</strong> to create a new shortcut</li>
      <li>Add action: <strong>Record Audio</strong></li>
      <li>Add action: <strong>Set Variable</strong> - name it <code>RecordedAudio</code></li>
      <li>Add action: <strong>Get Contents of URL</strong>
        <ul>
          <li>Method: <code>POST</code></li>
          <li>URL: <code>https://YOUR-TUNNEL-URL/transcribe</code></li>
          <li>Headers: <code>Content-Type</code> = <code>multipart/form-data</code></li>
          <li>Field: <code>audio</code> = <code>RecordedAudio</code></li>
        </ul>
      </li>
      <li>Add action: <strong>Get Dictionary from Input</strong></li>
      <li>Add action: <strong>Text</strong> - Use <code>Dictionary.text</code></li>
      <li>Add action: <strong>Show Result</strong></li>
    </ol>
  </div>
  
  <div class="step">
    <h3>Step 4: Test!</h3>
    <p>Run the shortcut and speak. You should get a transcription and summary back!</p>
  </div>
  
  <h2>API Response Format</h2>
  <pre>
{
  "success": true,
  "transcription": "the spoken words...",
  "summary": "a brief summary of what was said...",
  "language": "en",
  "duration": 5.2
}
  </pre>
</body>
</html>
  `);
});

// Main transcription endpoint
app.post('/transcribe', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, error: 'No audio file provided' });
    }

    const audioPath = req.file.path;
    const audioUrl = `file://${audioPath}`;

    console.log(`[${new Date().toISOString()}] Processing: ${req.file.originalname}`);

    // If no Whisper key, return mock transcription for testing
    if (!WHISPER_API_KEY) {
      // Clean up
      try { unlinkSync(audioPath); } catch (e) {}
      
      return res.json({
        success: true,
        transcription: "[Transcription would appear here - set WHISPER_API_KEY to enable]",
        summary: "[Summary would appear here - set SUMMARIZER_API_KEY to enable]",
        mock: true,
        message: "Set WHISPER_API_KEY and SUMMARIZER_API_KEY environment variables to enable real transcription"
      });
    }

    // Step 1: Transcribe with Whisper
    const transcription = await transcribeWithWhisper(audioPath, WHISPER_API_KEY);
    
    // Step 2: Summarize with AI
    let summary = "[Enable SUMMARIZER_API_KEY for summary]";
    if (SUMMARIZER_API_KEY && transcription) {
      summary = await summarizeText(transcription);
    }

    // Clean up audio file
    try { unlinkSync(audioPath); } catch (e) {}

    res.json({
      success: true,
      transcription,
      summary,
      mock: false
    });

  } catch (error) {
    console.error('Error processing audio:', error);
    
    // Clean up on error
    if (req.file?.path && existsSync(req.file.path)) {
      try { unlinkSync(req.file.path); } catch (e) {}
    }
    
    res.status(500).json({ 
      success: false, 
      error: error.message || 'Failed to process audio' 
    });
  }
});

async function transcribeWithWhisper(audioPath, apiKey) {
  return new Promise((resolve, reject) => {
    const boundary = `----FormBoundary${Date.now()}`;
    
    const audioData = require('fs').readFileSync(audioPath);
    
    // Build multipart form data manually
    const header = `--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="audio.m4a"\r\nContent-Type: audio/mp4\r\n\r\n`;
    const footer = `\r\n--${boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\nwhisper-1`;
    
    const body = Buffer.concat([
      Buffer.from(header),
      audioData,
      Buffer.from(footer),
      Buffer.from(`\r\n--${boundary}--\r\n`)
    ]);

    const options = {
      hostname: 'api.openai.com',
      path: '/v1/audio/transcriptions',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.error) {
            reject(new Error(result.error.message));
          } else {
            resolve(result.text || '');
          }
        } catch (e) {
          reject(new Error(`Failed to parse Whisper response: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function summarizeText(text) {
  if (!text || text.length < 10) return "No speech detected";
  
  const model = SUMMARIZER_MODEL.includes('/') ? SUMMARIZER_MODEL : `moonshot/${SUMMARIZER_MODEL}`;
  
  return new Promise((resolve, reject) => {
    const requestBody = {
      model: model,
      messages: [
        {
          role: 'system',
          content: 'You are a helpful assistant that summarizes conversations. Provide a brief 2-3 sentence summary of what was said, noting the main topics and any key points discussed.'
        },
        {
          role: 'user', 
          content: `Please summarize this transcription:\n\n${text}`
        }
      ]
    };

    const body = JSON.stringify(requestBody);
    const url = new URL(SUMMARIZER_BASE_URL + '/chat/completions');
    
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SUMMARIZER_API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const req = (url.protocol === 'https:' ? https : http).request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.error) {
            resolve(`[Summary error: ${result.error.message}]`);
          } else {
            resolve(result.choices?.[0]?.message?.content || 'No summary generated');
          }
        } catch (e) {
          resolve(`[Summary parse error: ${e.message}]`);
        }
      });
    });

    req.on('error', (e) => resolve(`[Summary request failed: ${e.message}]`));
    req.write(body);
    req.end();
  });
}

app.listen(PORT, () => {
  console.log(`🎙️ Ambient Listener API running on http://localhost:${PORT}`);
  console.log(`📱 iOS Shortcut setup: http://localhost:${PORT}/shortcut`);
  console.log('');
  console.log('To expose to iPhone, use localtunnel or ngrok:');
  console.log(`  npx localtunnel --port ${PORT}`);
});
