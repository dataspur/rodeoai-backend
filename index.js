import express from 'express';
import fetch from 'node-fetch';

const app = express();
app.use(express.json());

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') res.sendStatus(204);
  else next();
});

const MODELS = {
  scamper: "Scamper (Fast) 🐎",
  "gold buckle": "Gold Buckle 🏅",
  bodacious: "Bodacious 🐂"
};

app.post('/chat', async (req, res) => {
  const { message, model } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are ${MODELS[model] || MODELS.scamper}, an expert rodeo coach. Provide concise, expert rodeo advice.`,
          },
          { role: 'user', content: message },
        ],
        max_tokens: 300,
        temperature: 0.7,
      }),
    });

    const data = await response.json();
    res.json({
      reply: data.choices[0].message.content,
      model: model || 'scamper',
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'RodeoAI backend live' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`RodeoAI backend running on port ${PORT}`));
