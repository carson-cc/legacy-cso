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


app.post('/scrape/email', async (req, res) => {
  try {
    const { company, domain } = req.body;
    // Try common domain patterns
    const cleanName = company.toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+(inc|llc|corp|co|company|group|services|contracting|construction|electric|mechanical|hvac|plumbing|roofing|supply)\s*$/i, '')
      .trim()
      .replace(/\s+/g, '');
    const domains = domain ? [domain] : [
      cleanName + '.com',
      cleanName + 'hvac.com', 
      cleanName + 'plumbing.com',
      cleanName + 'electric.com',
      cleanName + 'construction.com',
    ];
    
    for (const d of domains.slice(0, 3)) {
      try {
        const r = await fetch('https://' + d, {
          signal: AbortSignal.timeout(5000),
          headers: { 'User-Agent': 'Mozilla/5.0' }
        });
        const html = await r.text();
        // Extract emails from page
        const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
        const found = [...new Set(html.match(emailRegex) || [])];
        // Filter out noreply, info spam, image files
        const clean = found.filter(e => 
          !e.includes('noreply') && 
          !e.includes('.png') && 
          !e.includes('.jpg') &&
          !e.includes('example.com') &&
          !e.includes('sentry') &&
          !e.includes('wix') &&
          e.length < 60
        );
        if (clean.length > 0) {
          return res.json({ email: clean[0], domain: d, all: clean.slice(0, 5) });
        }
      } catch(e) { continue; }
    }
    res.json({ email: null });
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/scrape-email', async (req, res) => {
  try {
    const { company, domain } = req.body;
    const searchQuery = encodeURIComponent(company + ' contact email');
    
    // Try common email patterns on company domain
    const emailsFound = [];
    
    if (domain) {
      // Try fetching contact page
      const urls = [
        'https://' + domain + '/contact',
        'https://' + domain + '/contact-us', 
        'https://' + domain + '/about',
        'https://' + domain
      ];
      
      for (const url of urls) {
        try {
          const response = await fetch(url, {
            headers: { 'User-Agent': 'Mozilla/5.0 (compatible; business inquiry)' },
            signal: AbortSignal.timeout(5000)
          });
          if (!response.ok) continue;
          const html = await response.text();
          
          // Extract emails from page
          const emailRegex = /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g;
          const found = html.match(emailRegex) || [];
          
          // Filter out generic/spam emails
          const filtered = found.filter(e => 
            !e.includes('example.') &&
            !e.includes('youremail') &&
            !e.includes('email@') &&
            !e.includes('@sentry') &&
            !e.includes('@google') &&
            !e.includes('@adobe') &&
            !e.includes('.png') &&
            !e.includes('.jpg') &&
            e.split('@')[1].includes('.')
          );
          
          if (filtered.length > 0) {
            // Prefer non-generic emails (info@, contact@ less preferred than name@)
            const personal = filtered.find(e => {
              const local = e.split('@')[0].toLowerCase();
              return !['info','contact','hello','admin','sales','support','team','office','mail'].includes(local);
            });
            emailsFound.push(...(personal ? [personal] : filtered.slice(0,1)));
            break;
          }
        } catch(e) { continue; }
      }
    }
    
    res.json({ emails: emailsFound, found: emailsFound.length > 0 });
  } catch (e) {
    res.status(500).json({ error: e.message, emails: [] });
  }
});

// Email send via SendGrid
app.post('/gmail/send', async (req, res) => {
  try {
    const { to, subject, body, gmailUser, sendgridKey } = req.body;
    const apiKey = sendgridKey || process.env.SENDGRID_API_KEY;
    
    console.log('SendGrid send to:', to, '| subject:', subject);
    
    const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        personalizations: [{ to: [{ email: to }] }],
        from: { email: gmailUser || 'carson@staffwithlegacy.com', name: 'Carson' },
        reply_to: { email: gmailUser || 'carson@staffwithlegacy.com', name: 'Carson' },
        subject: subject,
        content: [{ type: 'text/plain', value: body }]
      })
    });

    console.log('SendGrid status:', response.status);
    if (response.status === 202) {
      res.json({ success: true, messageId: 'sg-' + Date.now() });
    } else {
      const err = await response.text();
      console.log('SendGrid error:', err);
      res.json({ success: false, error: err, status: response.status });
    }
  } catch (e) {
    console.log('SendGrid error:', e.message);
    res.status(500).json({ success: false, error: e.message });
  }
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

// Bulk enrich — reveal emails for up to 10 people by Apollo ID
app.post('/apollo/bulk-enrich', async (req, res) => {
  try {
    const apolloKey = (req.headers['x-apollo-key'] || '').trim();
    const { details } = req.body;
    console.log('Bulk enrich:', details ? details.length : 0, 'people');
    const response = await fetch('https://api.apollo.io/api/v1/people/bulk_match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache', 'X-Api-Key': apolloKey },
      body: JSON.stringify({ details: details, reveal_personal_emails: false })
    });
    const rawText = await response.text();
    console.log('Bulk enrich status:', response.status, '| preview:', rawText.substring(0, 150));
    try { res.json(JSON.parse(rawText)); }
    catch(e) { res.json({ error: rawText, matches: [] }); }
  } catch (e) {
    res.status(500).json({ error: e.message, matches: [] });
  }
});
app.get('/hunter/domain', async (req, res) => {
  try {
    const key = (req.headers['x-hunter-key'] || '').trim();
    const domain = req.query.domain || '';
    const limit = req.query.limit || 5;
    const url = 'https://api.hunter.io/v2/domain-search?api_key=' + key + '&domain=' + encodeURIComponent(domain) + '&limit=' + limit;
    const response = await fetch(url);
    const rawText = await response.text();
    try { res.json(JSON.parse(rawText)); }
    catch(e) { res.json({ error: rawText, data: null }); }
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
