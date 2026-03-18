const express = require('express');
const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, X-Anthropic-Key, X-Apollo-Key, X-Hunter-Key');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'Legacy Workforce AI CSO' });
});

app.post('/anthropic', async (req, res) => {
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': req.headers['x-anthropic-key'],
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/apollo/health', async (req, res) => {
  try {
    const response = await fetch('https://api.apollo.io/api/v1/auth/health', {
      headers: { 'X-Api-Key': req.headers['x-apollo-key'], 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/apollo/search', async (req, res) => {
  try {
    const apolloKey = (req.headers['x-apollo-key'] || '').trim();
    console.log('Apollo key length:', apolloKey.length, '| first 8:', apolloKey.substring(0, 8));
    const response = await fetch('https://api.apollo.io/api/v1/mixed_people/api_search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'X-Api-Key': apolloKey
      },
      body: JSON.stringify(req.body)
    });
    const rawText = await response.text();
    console.log('Apollo status:', response.status, '| preview:', rawText.substring(0, 120));
    try {
      const data = JSON.parse(rawText);
      res.json(data);
    } catch (parseErr) {
      // Apollo returned non-JSON (e.g. "Invalid access token")
      res.json({ error: rawText, people: [], total_entries: 0 });
    }
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/apollo/enrich', async (req, res) => {
  try {
    const response = await fetch('https://api.apollo.io/api/v1/people/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Api-Key': req.headers['x-apollo-key'] },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/hunter/account', async (req, res) => {
  try {
    const response = await fetch('https://api.hunter.io/v2/account?api_key=' + req.headers['x-hunter-key']);
    const data = await response.json();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/hunter/find', async (req, res) => {
  try {
    const { first_name, last_name, company } = req.query;
    const url = `https://api.hunter.io/v2/email-finder?api_key=${req.headers['x-hunter-key']}&first_name=${first_name}&last_name=${last_name}&company=${company}`;
    const response = await fetch(url);
    const data = await response.json();
    res.json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Legacy CSO proxy running on port ' + PORT));
