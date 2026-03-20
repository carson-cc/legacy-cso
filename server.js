const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, X-Anthropic-Key, X-Apollo-Key, X-Hunter-Key, X-SendGrid-Key');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// ── ENV VARS (all keys stored server-side — never exposed to browser) ──
const SENDGRID_KEY = process.env.SENDGRID_API_KEY;
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const APOLLO_KEY = process.env.APOLLO_API_KEY;
const FROM_EMAIL = process.env.FROM_EMAIL || 'carson@staffwithlegacy.com';
const CALENDLY_URL = 'https://calendly.com/carson-staffwithlegacy/30min';
const CRON_SECRET = process.env.CRON_KEY || 'legacy-cron-2024';
const CANSPAM_FOOTER = '\n\n---\nLegacy Workforce · 5730 Anita St, Dallas TX 75206\nUnsubscribe: reply STOP';

// ── PERSISTENT STORAGE ────────────────────────────────────────────
const DB_FILE = '/tmp/legacy_events.json';
function loadDB() {
  try { if (fs.existsSync(DB_FILE)) return JSON.parse(fs.readFileSync(DB_FILE, 'utf8')); } catch(e) {}
  return { events: [], contacts: {}, followupQueue: [], sentFollowups: [] };
}
function saveDB(db) {
  try { fs.writeFileSync(DB_FILE, JSON.stringify(db), 'utf8'); } catch(e) {}
}

// ── SENDGRID WEBHOOK ──────────────────────────────────────────────
app.post('/webhook/sendgrid', async (req, res) => {
  try {
    const events = Array.isArray(req.body) ? req.body : [req.body];
    const db = loadDB();
    for (const event of events) {
      const email = event.email;
      const type = event.event;
      const url = event.url || null;
      const ts = new Date().toISOString();
      console.log('SG webhook:', type, email, url || '');
      db.events.push({ email, type, url, ts, subject: event.subject || '' });
      if (!db.contacts[email]) db.contacts[email] = { email, opens: 0, clicks: 0, calendlyClick: false, booked: false, firstSentAt: ts };
      const c = db.contacts[email];
      if (type === 'open') { c.opens++; c.lastOpenAt = ts; }
      if (type === 'click') {
        c.clicks++; c.lastClickAt = ts;
        if (url && url.includes('calendly.com')) {
          c.calendlyClick = true; c.calendlyClickAt = ts;
          console.log('CALENDLY CLICK:', email);
        }
      }
      if (type === 'bounce' || type === 'spamreport') { c.bounced = true; }
      if (type === 'unsubscribe' || type === 'group_unsubscribe') {
        c.unsubscribed = true;
        c.unsubscribedAt = ts;
        // Remove all pending follow-ups for this person
        db.followupQueue = db.followupQueue.filter(f => f.email !== email);
        console.log('UNSUBSCRIBED:', email, '-- all follow-ups cancelled');
      }
      // Queue calendly-click-no-book follow-up (24 hours)
      const alreadyQueued = db.followupQueue.find(f => f.email === email && f.type === 'calendly_no_book');
      const alreadySent = db.sentFollowups.find(f => f.email === email && f.type === 'calendly_no_book');
      if (type === 'click' && url && url.includes('calendly.com') && !c.booked && !alreadyQueued && !alreadySent) {
        db.followupQueue.push({ email, type: 'calendly_no_book', sendAfter: new Date(Date.now() + 24*60*60*1000).toISOString(), name: c.name || email.split('@')[0], org: c.org || '', subject: event.subject || '' });
        console.log('Queued calendly follow-up for:', email);
      }
    }
    saveDB(db);
    res.status(200).json({ received: events.length });
  } catch(e) { console.log('Webhook error:', e.message); res.status(200).json({ error: e.message }); }
});

// ── CALENDLY WEBHOOK ──────────────────────────────────────────────
app.post('/webhook/calendly', async (req, res) => {
  try {
    const payload = req.body;
    const event = payload.event || payload.payload?.event_type?.name || 'booking';
    const invitee = payload.payload?.invitee || {};
    const email = invitee.email;
    const name = invitee.name || '';
    const startTime = payload.payload?.event?.start_time || '';
    console.log('Calendly webhook:', event, email, startTime);
    if (email && (event === 'invitee.created' || event.includes('created'))) {
      const db = loadDB();
      if (!db.contacts[email]) db.contacts[email] = { email };
      db.contacts[email].booked = true;
      db.contacts[email].bookedAt = new Date().toISOString();
      db.contacts[email].meetingTime = startTime;
      db.contacts[email].name = name;
      db.followupQueue = db.followupQueue.filter(f => !(f.email === email && f.type === 'calendly_no_book'));
      db.followupQueue.push({ email, type: 'booking_confirm', sendAfter: new Date().toISOString(), name, meetingTime: startTime });
      saveDB(db);
      console.log('Booking confirmed:', email, startTime);
    }
    res.status(200).json({ received: true });
  } catch(e) { console.log('Calendly webhook error:', e.message); res.status(200).json({ error: e.message }); }
});

// ── REGISTER SENT EMAIL ───────────────────────────────────────────
app.post('/track/sent', async (req, res) => {
  try {
    const { email, name, org, subject, track } = req.body;
    const db = loadDB();
    if (!db.contacts[email]) db.contacts[email] = { email };
    const c = db.contacts[email];
    c.name = name || c.name; c.org = org || c.org; c.track = track || c.track;
    c.subject = subject || c.subject; c.firstSentAt = c.firstSentAt || new Date().toISOString();
    c.opens = c.opens || 0; c.clicks = c.clicks || 0;
    const now = Date.now();
    if (!db.followupQueue.find(f => f.email === email && f.type === 'day3') && !db.sentFollowups.find(f => f.email === email && f.type === 'day3'))
      db.followupQueue.push({ email, name, org, track, type: 'day3', subject, sendAfter: new Date(now + 3*24*60*60*1000).toISOString() });
    if (!db.followupQueue.find(f => f.email === email && f.type === 'day7') && !db.sentFollowups.find(f => f.email === email && f.type === 'day7'))
      db.followupQueue.push({ email, name, org, track, type: 'day7', subject, sendAfter: new Date(now + 7*24*60*60*1000).toISOString() });
    saveDB(db);
    res.json({ success: true });
  } catch(e) { res.status(500).json({ error: e.message }); }
});

// ── CRON PROCESSOR (hit by cron-job.org every morning 8am CT) ────
app.post('/cron/process', async (req, res) => {
  const key = req.headers['x-cron-key'] || req.body?.cronKey;
  if (key !== CRON_SECRET) return res.status(401).json({ error: 'Unauthorized' });
  const db = loadDB();
  const now = new Date();
  const due = db.followupQueue.filter(f => new Date(f.sendAfter) <= now);
  console.log('Cron: processing', due.length, 'due follow-ups');
  if (!SENDGRID_KEY || !ANTHROPIC_KEY) return res.json({ error: 'Missing env vars SENDGRID_API_KEY or ANTHROPIC_API_KEY', due: due.length });
  const results = [];
  for (const item of due) {
    try {
      const contact = db.contacts[item.email] || {};
      if (contact.booked) { db.followupQueue = db.followupQueue.filter(f => !(f.email===item.email && f.type===item.type)); continue; }
      if (contact.bounced || contact.unsubscribed) {
        db.followupQueue = db.followupQueue.filter(f => f.email !== item.email);
        console.log('Skipping', item.email, '-- bounced or unsubscribed');
        continue;
      }
      const firstName = (item.name || item.email.split('@')[0]).split(' ')[0];
      let subject = '', body = '';
      if (item.type === 'calendly_no_book') {
        subject = 'Re: ' + (item.subject || 'connecting');
        body = firstName + ', wanted to follow up — looks like you had a chance to check us out. Happy to keep it to 15 minutes. Thursday or Friday work this week?\n\n' + CALENDLY_URL + '\n\nCarson · Legacy Workforce · staffwithlegacy.com' + CANSPAM_FOOTER;
      } else if (item.type === 'booking_confirm') {
        subject = 'Looking forward to our call';
        body = firstName + ', confirmed — looking forward to our conversation.\n\nTo make it worthwhile, a couple quick questions beforehand:\n1. What role are you trying to fill right now?\n2. How long has it been open?\n\nFeel free to reply here or just bring it to the call.\n\nCarson · Legacy Workforce · staffwithlegacy.com';
      } else if (item.type === 'day3') {
        const prompt = 'Write a 3-sentence follow-up cold email for Legacy Workforce (trades staffing). Prospect: ' + (item.name||'') + ' at ' + (item.org||'a trades company') + '. Day 3 — no reply yet. Angle: 3-month replacement guarantee removes all hiring risk, and we source through veteran transition programs. Start with their first name only. No questions. Soft close. Sign off: Carson';
        const aiRes = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01' }, body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 200, messages: [{ role: 'user', content: prompt }] }) });
        const aiData = await aiRes.json();
        body = (aiData.content?.[0]?.text || '') + '\n\n' + CALENDLY_URL + '\n\nCarson · Legacy Workforce · staffwithlegacy.com' + CANSPAM_FOOTER;
        subject = 'Re: ' + (item.subject || 'skilled trades hiring');
      } else if (item.type === 'day7') {
        const prompt = 'Write a 2-sentence final follow-up for Legacy Workforce. Prospect: ' + (item.name||'') + ' at ' + (item.org||'a trades company') + '. Last note — Liberty University and trade school pipeline gives access to trained candidates not on any job board. Graceful, no pressure. Sign off: Carson';
        const aiRes = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01' }, body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 150, messages: [{ role: 'user', content: prompt }] }) });
        const aiData = await aiRes.json();
        body = (aiData.content?.[0]?.text || '') + '\n\n' + CALENDLY_URL + '\n\nCarson · Legacy Workforce · staffwithlegacy.com' + CANSPAM_FOOTER;
        subject = 'Re: ' + (item.subject || 'one last thought');
      }
      if (!body) continue;
      const sgRes = await fetch('https://api.sendgrid.com/v3/mail/send', { method: 'POST', headers: { 'Authorization': 'Bearer ' + SENDGRID_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ personalizations: [{ to: [{ email: item.email }] }], from: { email: FROM_EMAIL, name: 'Carson' }, reply_to: { email: FROM_EMAIL, name: 'Carson' }, subject, content: [{ type: 'text/plain', value: body }] }) });
      if (sgRes.status === 202) {
        console.log('Auto follow-up sent:', item.type, '->', item.email);
        results.push({ email: item.email, type: item.type, sent: true });
        db.sentFollowups.push({ email: item.email, type: item.type, sentAt: now.toISOString() });
        db.followupQueue = db.followupQueue.filter(f => !(f.email===item.email && f.type===item.type));
      } else {
        const err = await sgRes.text();
        console.log('SG follow-up failed:', err.substring(0,100));
        results.push({ email: item.email, type: item.type, sent: false, error: err.substring(0,100) });
      }
    } catch(e) { console.log('Follow-up error:', item.email, e.message); results.push({ email: item.email, type: item.type, error: e.message }); }
  }
  saveDB(db);
  res.json({ processed: due.length, results, remaining: db.followupQueue.length });
});

// ── GET EVENTS (app reads this) ───────────────────────────────────
app.get('/events', (req, res) => {
  const db = loadDB();
  res.json({ contacts: db.contacts, followupQueue: db.followupQueue, sentFollowups: db.sentFollowups, recentEvents: db.events.slice(-100) });
});

// ── GMAIL SEND (uses env var key, falls back to passed key) ───────
app.post('/gmail/send', async (req, res) => {
  try {
    const { to, subject, body, gmailUser, sendgridKey } = req.body;
    const apiKey = SENDGRID_KEY || sendgridKey;
    console.log('SendGrid send to:', to, '| subject:', subject);
    const response = await fetch('https://api.sendgrid.com/v3/mail/send', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + apiKey, 'Content-Type': 'application/json' },
      body: JSON.stringify({ personalizations: [{ to: [{ email: to }] }], from: { email: gmailUser || FROM_EMAIL, name: 'Carson' }, reply_to: { email: gmailUser || FROM_EMAIL, name: 'Carson' }, subject, content: [{ type: 'text/plain', value: body }] })
    });
    console.log('SendGrid status:', response.status);
    if (response.status === 202) { res.json({ success: true, messageId: 'sg-' + Date.now() }); }
    else { const err = await response.text(); console.log('SendGrid error:', err); res.json({ success: false, error: err, status: response.status }); }
  } catch(e) { console.log('SendGrid error:', e.message); res.status(500).json({ success: false, error: e.message }); }
});

// ── ANTHROPIC PROXY ───────────────────────────────────────────────
app.post('/anthropic', async (req, res) => {
  try {
    const apiKey = ANTHROPIC_KEY || req.headers['x-anthropic-key'];
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify(req.body)
    });
    res.json(await response.json());
  } catch(e) { res.status(500).json({ error: e.message }); }
});

// ── APOLLO ────────────────────────────────────────────────────────
app.get('/apollo/health', async (req, res) => {
  try {
    const key = APOLLO_KEY || req.headers['x-apollo-key'];
    const response = await fetch('https://api.apollo.io/api/v1/auth/health', { headers: { 'X-Api-Key': key, 'Content-Type': 'application/json' } });
    res.json(await response.json());
  } catch(e) { res.status(500).json({ error: e.message }); }
});

app.post('/apollo/search', async (req, res) => {
  try {
    const apolloKey = (APOLLO_KEY || req.headers['x-apollo-key'] || '').trim();
    console.log('Apollo key length:', apolloKey.length, '| first 8:', apolloKey.substring(0, 8));
    const response = await fetch('https://api.apollo.io/api/v1/mixed_people/api_search', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache', 'X-Api-Key': apolloKey }, body: JSON.stringify(req.body) });
    const rawText = await response.text();
    console.log('Apollo status:', response.status, '| preview:', rawText.substring(0, 120));
    try { res.json(JSON.parse(rawText)); } catch(e) { res.json({ error: rawText, people: [], total_entries: 0 }); }
  } catch(e) { res.status(500).json({ error: e.message }); }
});

app.post('/apollo/enrich', async (req, res) => {
  try {
    const key = APOLLO_KEY || req.headers['x-apollo-key'];
    const response = await fetch('https://api.apollo.io/api/v1/people/match', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Api-Key': key }, body: JSON.stringify(req.body) });
    res.json(await response.json());
  } catch(e) { res.status(500).json({ error: e.message }); }
});

app.post('/apollo/bulk-enrich', async (req, res) => {
  try {
    const apolloKey = (APOLLO_KEY || req.headers['x-apollo-key'] || '').trim();
    const { details } = req.body;
    console.log('Bulk enrich:', details ? details.length : 0, 'people');
    const response = await fetch('https://api.apollo.io/api/v1/people/bulk_match', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache', 'X-Api-Key': apolloKey }, body: JSON.stringify({ details, reveal_personal_emails: false }) });
    const rawText = await response.text();
    console.log('Bulk enrich status:', response.status, '| preview:', rawText.substring(0, 150));
    try { res.json(JSON.parse(rawText)); } catch(e) { res.json({ error: rawText, matches: [] }); }
  } catch(e) { res.status(500).json({ error: e.message, matches: [] }); }
});

// ── HUNTER ────────────────────────────────────────────────────────
app.get('/hunter/domain', async (req, res) => {
  try {
    const key = req.headers['x-hunter-key'] || '';
    const url = 'https://api.hunter.io/v2/domain-search?api_key=' + key + '&domain=' + encodeURIComponent(req.query.domain || '') + '&limit=' + (req.query.limit || 5);
    const response = await fetch(url);
    const rawText = await response.text();
    try { res.json(JSON.parse(rawText)); } catch(e) { res.json({ error: rawText, data: null }); }
  } catch(e) { res.status(500).json({ error: e.message }); }
});

app.get('/hunter/account', async (req, res) => {
  try {
    const response = await fetch('https://api.hunter.io/v2/account?api_key=' + req.headers['x-hunter-key']);
    res.json(await response.json());
  } catch(e) { res.status(500).json({ error: e.message }); }
});

app.get('/hunter/find', async (req, res) => {
  try {
    const { first_name, last_name, company } = req.query;
    const url = `https://api.hunter.io/v2/email-finder?api_key=${req.headers['x-hunter-key']}&first_name=${first_name}&last_name=${last_name}&company=${company}`;
    res.json(await (await fetch(url)).json());
  } catch(e) { res.status(500).json({ error: e.message }); }
});

// ── SCRAPERS ──────────────────────────────────────────────────────
app.post('/scrape-email', async (req, res) => {
  try {
    const { company, domain } = req.body;
    const emailsFound = [];
    if (domain) {
      const urls = ['https://' + domain + '/contact', 'https://' + domain + '/contact-us', 'https://' + domain + '/about', 'https://' + domain];
      for (const url of urls) {
        try {
          const response = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; business inquiry)' }, signal: AbortSignal.timeout(5000) });
          if (!response.ok) continue;
          const html = await response.text();
          const found = html.match(/[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g) || [];
          const filtered = found.filter(e => !e.includes('example.') && !e.includes('youremail') && !e.includes('email@') && !e.includes('@sentry') && !e.includes('@google') && !e.includes('@adobe') && !e.includes('.png') && !e.includes('.jpg') && e.split('@')[1].includes('.'));
          if (filtered.length > 0) {
            const personal = filtered.find(e => { const l = e.split('@')[0].toLowerCase(); return !['info', 'contact', 'hello', 'admin', 'sales', 'support', 'team', 'office', 'mail'].includes(l); });
            emailsFound.push(...(personal ? [personal] : filtered.slice(0, 1)));
            break;
          }
        } catch(e) { continue; }
      }
    }
    res.json({ emails: emailsFound, found: emailsFound.length > 0 });
  } catch(e) { res.status(500).json({ error: e.message, emails: [] }); }
});

app.get('/suppressed', (req, res) => {
  const db = loadDB();
  const suppressed = Object.values(db.contacts)
    .filter(c => c.bounced || c.unsubscribed)
    .map(c => ({ email: c.email, reason: c.unsubscribed ? 'unsubscribed' : 'bounced', at: c.unsubscribedAt || c.firstSentAt }));
  res.json({ suppressed, count: suppressed.length });
});

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'Legacy Workforce AI CSO', env: { sendgrid: !!SENDGRID_KEY, anthropic: !!ANTHROPIC_KEY, apollo: !!APOLLO_KEY } }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Legacy CSO proxy running on port ' + PORT));
