// Simplified Ambient Listener - uses URL-encoded audio for serverless compatibility
import express from 'express';

const app = express();
app.use(express.json({ limit: '10mb' }));

const WHISPER_API_KEY = process.env.WHISPER_API_KEY || '';
const SUMMARIZER_API_KEY = process.env.SUMMARIZER_API_KEY || process.env.KIMI_API_KEY || '';
const SUMMARIZER_BASE_URL = process.env.SUMMARIZER_BASE_URL || 'https://api.moonshot.ai/v1';
const SUMMARIZER_MODEL = process.env.SUMMARIZER_MODEL || 'kimi-k2.5';

app.get('/', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'Ambient Listener API',
    version: '1.0.0'
  });
});

app.post('/summarize', async (req, res) => {
  try {
    const { transcription } = req.body;
    
    if (!transcription) {
      return res.status(400).json({ success: false, error: 'No transcription provided' });
    }

    console.log(`[${new Date().toISOString()}] Processing transcription (${transcription.length} chars)`);

    let summary = "Summary not available";
    
    if (SUMMARIZER_API_KEY) {
      try {
        const model = SUMMARIZER_MODEL.includes('/') ? SUMMARIZER_MODEL : `moonshot/${SUMMARIZER_MODEL}`;
        
        const response = await fetch(`${SUMMARIZER_BASE_URL}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${SUMMARIZER_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: model,
            messages: [
              {
                role: 'system',
                content: 'You are a helpful assistant that summarizes conversations. Provide a brief 2-3 sentence summary of what was said, noting the main topics and any key points discussed. Respond in the same language as the conversation.'
              },
              {
                role: 'user',
                content: `Please summarize this transcription:\n\n${transcription}`
              }
            ]
          })
        });

        const data = await response.json();
        if (data.error) {
          summary = `Summary error: ${data.error.message}`;
        } else {
          summary = data.choices?.[0]?.message?.content || 'No summary generated';
        }
      } catch (e) {
        summary = `Summary failed: ${e.message}`;
      }
    } else {
      summary = "[Set SUMMARIZER_API_KEY to enable summary]";
    }

    res.json({
      success: true,
      transcription,
      summary,
      mock: !SUMMARIZER_API_KEY
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Whisper transcription proxy
app.post('/transcribe', async (req, res) => {
  try {
    const { audio_data, format } = req.body;
    
    if (!audio_data) {
      return res.status(400).json({ success: false, error: 'No audio data provided' });
    }

    if (!WHISPER_API_KEY) {
      return res.json({
        success: true,
        transcription: "[Set WHISPER_API_KEY to enable transcription]",
        summary: "[Set SUMMARIZER_API_KEY to enable summary]",
        mock: true
      });
    }

    // Decode base64 audio
    const audioBuffer = Buffer.from(audio_data, 'base64');
    
    // Create form data for Whisper
    const formData = new FormData();
    formData.append('file', new Blob([audioBuffer]), `audio.${format || 'm4a'}`);
    formData.append('model', 'whisper-1');
    formData.append('response_format', 'text');

    const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${WHISPER_API_KEY}`
      },
      body: formData
    });

    const data = await response.json();
    
    if (data.error) {
      return res.status(400).json({ success: false, error: data.error.message });
    }

    const transcription = data.text || '';

    // Auto-summarize if we have a summarizer
    let summary = "[Set SUMMARIZER_API_KEY to enable summary]";
    if (SUMMARIZER_API_KEY && transcription) {
      try {
        const model = SUMMARIZER_MODEL.includes('/') ? SUMMARIZER_MODEL : `moonshot/${SUMMARIZER_MODEL}`;
        
        const summaryResponse = await fetch(`${SUMMARIZER_BASE_URL}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${SUMMARIZER_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: model,
            messages: [
              {
                role: 'system',
                content: 'You are a helpful assistant that summarizes conversations. Provide a brief 2-3 sentence summary of what was said, noting the main topics and any key points discussed. Respond in the same language as the conversation.'
              },
              {
                role: 'user',
                content: `Please summarize this transcription:\n\n${transcription}`
              }
            ]
          })
        });

        const summaryData = await summaryResponse.json();
        summary = summaryData.choices?.[0]?.message?.content || 'No summary generated';
      } catch (e) {
        summary = `Summary failed: ${e.message}`;
      }
    }

    res.json({
      success: true,
      transcription,
      summary,
      mock: false
    });

  } catch (error) {
    console.error('Transcription error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

export default app;
