const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, X-Anthropic-Key, X-Apollo-Key, X-Hunter-Key, X-SendGrid-Key, X-Cron-Key, x-cron-key');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// ── ENV VARS (all keys stored server-side — never exposed to browser) ──
const SENDGRID_KEY = process.env.SENDGRID_API_KEY;
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const APOLLO_KEY = process.env.APOLLO_API_KEY;
const FROM_EMAIL = process.env.FROM_EMAIL || 'carson@staffwithlegacy.com';
const CALENDLY_URL = 'https://calendly.com/carson-staffwithlegacy/15-minute-meeting';
const CRON_SECRET = process.env.CRON_KEY || 'legacy-cron-2024';
function nextTwoBusinessDays() {
  const days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const result = [];
  const d = new Date();
  d.setDate(d.getDate() + 1);
  while (result.length < 2) {
    const dow = d.getDay();
    if (dow !== 0 && dow !== 6) result.push(days[dow]);
    if (result.length < 2) d.setDate(d.getDate() + 1);
  }
  return result[0] + ' or ' + result[1];
}

const CANSPAM_FOOTER = '\n\n---\nLegacy Workforce · 5730 Anita St, Dallas TX 75206\nUnsubscribe: reply STOP';

// ── PERSISTENT STORAGE (Postgres with /tmp fallback) ────────────
const DB_FILE = '/tmp/legacy_events.json';
let pgClient = null;

async function initDB() {
  if (!process.env.DATABASE_URL) return;
  try {
    const { Client } = require('pg');
    pgClient = new Client({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });
    await pgClient.connect();
    await pgClient.query(`CREATE TABLE IF NOT EXISTS store (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMPTZ DEFAULT NOW())`);
    console.log('Postgres connected');
  } catch(e) {
    console.log('Postgres failed, using /tmp fallback:', e.message);
    pgClient = null;
  }
}

async function loadDB() {
  if (pgClient) {
    try {
      const r = await pgClient.query(`SELECT value FROM store WHERE key = 'db'`);
      if (r.rows.length) return JSON.parse(r.rows[0].value);
    } catch(e) { console.log('Postgres read error:', e.message); }
  }
  try { if (fs.existsSync(DB_FILE)) return JSON.parse(fs.readFileSync(DB_FILE, 'utf8')); } catch(e) {}
  return { events: [], contacts: {}, followupQueue: [], sentFollowups: [] };
}

async function saveDB(db) {
  const json = JSON.stringify(db);
  if (pgClient) {
    try {
      await pgClient.query(`INSERT INTO store (key, value, updated_at) VALUES ('db', $1, NOW()) ON CONFLICT (key) DO UPDATE SET value = $1, updated_at = NOW()`, [json]);
      return;
    } catch(e) { console.log('Postgres write error:', e.message); }
  }
  try { fs.writeFileSync(DB_FILE, json, 'utf8'); } catch(e) {}
}

// ── SENDGRID WEBHOOK ──────────────────────────────────────────────
app.post('/webhook/sendgrid', async (req, res) => {
  try {
    const events = Array.isArray(req.body) ? req.body : [req.body];
    const db = await loadDB();
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
    await saveDB(db);
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
      const db = await loadDB();
      if (!db.contacts[email]) db.contacts[email] = { email };
      db.contacts[email].booked = true;
      db.contacts[email].bookedAt = new Date().toISOString();
      db.contacts[email].meetingTime = startTime;
      db.contacts[email].name = name;
      db.followupQueue = db.followupQueue.filter(f => !(f.email === email && f.type === 'calendly_no_book'));
      db.followupQueue.push({ email, type: 'booking_confirm', sendAfter: new Date().toISOString(), name, meetingTime: startTime });
      await saveDB(db);
      console.log('Booking confirmed:', email, startTime);
    }
    res.status(200).json({ received: true });
  } catch(e) { console.log('Calendly webhook error:', e.message); res.status(200).json({ error: e.message }); }
});

// ── REGISTER SENT EMAIL ───────────────────────────────────────────
app.post('/track/sent', async (req, res) => {
  try {
    const { email, name, org, subject, track } = req.body;
    const db = await loadDB();
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
    await saveDB(db);
    res.json({ success: true });
  } catch(e) { res.status(500).json({ error: e.message }); }
});

// ── CRON PROCESSOR (hit by cron-job.org every morning 8am CT) ────
app.post('/cron/process', async (req, res) => {
  const key = req.headers['x-cron-key'] || req.headers['X-Cron-Key'] || req.body?.cronKey;
  if (key !== CRON_SECRET) return res.status(401).json({ error: 'Unauthorized', received: key ? 'key present but wrong' : 'no key' });
  const db = await loadDB();
  const now = new Date();
  const due = db.followupQueue.filter(f => new Date(f.sendAfter) <= now);
  console.log('Cron: processing', due.length, 'due follow-ups');
  if (!SENDGRID_KEY || !ANTHROPIC_KEY) return res.json({ error: 'Missing env vars SENDGRID_API_KEY or ANTHROPIC_API_KEY', due: due.length });
  const results = [];
  for (const item of due) {
    try {
      // DEDUP: skip if already in sentFollowups
      const alreadySent = db.sentFollowups.find(f => f.email === item.email && f.type === item.type);
      if (alreadySent) {
        console.log('DEDUP: already sent', item.type, 'to', item.email, '-- removing from queue');
        db.followupQueue = db.followupQueue.filter(f => !(f.email===item.email && f.type===item.type));
        continue;
      }
      const contact = db.contacts[item.email] || {};
      if (contact.booked) { db.followupQueue = db.followupQueue.filter(f => !(f.email===item.email && f.type===item.type)); continue; }
      if (item.email === 'dduvall@rffager.com' || item.email === 'csyenrick@smithphillips.net') {
        console.log('Skipping wrong ICP:', item.email);
        db.followupQueue = db.followupQueue.filter(f => f.email !== item.email);
        continue;
      }
      if (contact.bounced || contact.unsubscribed) {
        db.followupQueue = db.followupQueue.filter(f => f.email !== item.email);
        console.log('Skipping', item.email, '-- bounced or unsubscribed');
        continue;
      }
      const firstName = (item.name || item.email.split('@')[0]).split(' ')[0];
      let subject = '', body = '';
      if (item.type === 'calendly_no_book') {
        subject = 'Re: ' + (item.subject || 'connecting');
        body = firstName + ', still worth 15 minutes -- want to understand what your hiring looks like going into Q2. ' + nextTwoBusinessDays() + ' work?\n\n' + CALENDLY_URL + '\n\nCarson · Legacy Workforce · staffwithlegacy.com' + CANSPAM_FOOTER;
      } else if (item.type === 'booking_confirm') {
        subject = 'Looking forward to our call';
        body = firstName + ', confirmed — looking forward to our conversation.\n\nTo make it worthwhile, a couple quick questions beforehand:\n1. What role are you trying to fill right now?\n2. How long has it been open?\n\nFeel free to reply here or just bring it to the call.\n\nCarson · Legacy Workforce · staffwithlegacy.com';
      } else if (item.type === 'day3') {
        const prompt = 'Write a 3-sentence follow-up cold email for Legacy Workforce (trades staffing). Prospect: ' + (item.name||'') + ' at ' + (item.org||'a trades company') + '. Write a 2-sentence Day 3 follow-up cold email for Legacy Workforce staffing. Prospect: '+item.name+' at '+item.org+'. Sentence 1: Lead with new information not in the first email — we source through veteran transition programs, meaning candidates with trade certifications, structured work habits, and military background checks most contractors never access. Sentence 2: our 3-month guarantee means if anyone leaves or underperforms in the first 90 days, we re-recruit at no charge — then end with a soft binary ask like: worth 15 minutes this week? Start with their first name only. No corporate language. Sign off: Carstart with their first name only. End with: Worth 15 minutes? Sign off: Carson';
        const aiRes = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01' }, body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 200, messages: [{ role: 'user', content: prompt }] }) });
        const aiData = await aiRes.json();
        body = (aiData.content?.[0]?.text || '') + '\n\n' + CALENDLY_URL + '\n\nCarson · Legacy Workforce · staffwithlegacy.com' + CANSPAM_FOOTER;
        subject = 'Re: ' + (item.subject || 'skilled trades hiring');
      } else if (item.type === 'day7') {
        const prompt = 'Write a 2-sentence final follow-up cold email for Legacy Workforce staffing. Prospect: ' + (item.name||'') + ' at ' + (item.org||'a trades company') + '. This is the last email — signal finality without aggression. Sentence 1: reference that we have a direct pipeline from Liberty University and trade school partners, meaning candidates who have completed skills assessments and background checks and are not on any job board. Sentence 2: make a graceful low-pressure final ask — if the roles are still open it is worth 15 minutes, if not you will leave them alone. Start with their first name. Do not say Last note verbatim — write it naturally. Sign off: Carson';
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
  await await saveDB(db);
  // Return slim summary only - cron-job.org has response size limit
  res.json({
    processed: results.length,
    remaining: db.followupQueue.length,
    summary: results.map(r => ({ email: r.email, type: r.type, success: r.success, error: r.error||null }))
  });
});

// ── GET EVENTS (app reads this) ───────────────────────────────────
app.get('/events', async (req, res) => {
  const db = await loadDB();
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

app.get('/suppressed', async (req, res) => {
  const db = await loadDB();
  const apiKey = SENDGRID_KEY;
  let sgSuppressions = [];
  if (apiKey) {
    try {
      const [unsubRes, bounceRes, spamRes] = await Promise.all([
        fetch('https://api.sendgrid.com/v3/suppression/unsubscribes?limit=500', { headers: { 'Authorization': 'Bearer ' + apiKey } }),
        fetch('https://api.sendgrid.com/v3/suppression/bounces?limit=500', { headers: { 'Authorization': 'Bearer ' + apiKey } }),
        fetch('https://api.sendgrid.com/v3/suppression/spam_reports?limit=500', { headers: { 'Authorization': 'Bearer ' + apiKey } })
      ]);
      const [unsubData, bounceData, spamData] = await Promise.all([unsubRes.json(), bounceRes.json(), spamRes.json()]);
      const process = (arr, reason) => Array.isArray(arr) ? arr.forEach(x => {
        sgSuppressions.push({ email: x.email, reason, at: new Date(x.created * 1000).toISOString() });
        if (!db.contacts[x.email]) db.contacts[x.email] = { email: x.email, opens: 0, clicks: 0 };
        if (reason === 'unsubscribed' || reason === 'spam') { db.contacts[x.email].unsubscribed = true; db.contacts[x.email].unsubscribedAt = new Date(x.created * 1000).toISOString(); }
        if (reason === 'bounced') db.contacts[x.email].bounced = true;
        db.followupQueue = db.followupQueue.filter(f => f.email !== x.email);
      }) : null;
      process(unsubData, 'unsubscribed');
      process(bounceData, 'bounced');
      process(spamData, 'spam');
      if (sgSuppressions.length) await saveDB(db);
      console.log('SendGrid suppressions:', sgSuppressions.length);
    } catch(e) { console.log('SG suppression error:', e.message); }
  }
  const local = Object.values(db.contacts).filter(c => c.bounced || c.unsubscribed).map(c => ({ email: c.email, reason: c.unsubscribed ? 'unsubscribed' : 'bounced', at: c.unsubscribedAt || c.firstSentAt }));
  const seen = new Set(local.map(x => x.email));
  sgSuppressions.forEach(x => { if (!seen.has(x.email)) local.push(x); });
  res.json({ suppressed: local, count: local.length, fromSendGrid: sgSuppressions.length });
});

// Sync endpoint - returns webhook store stats (Email Activity API requires paid add-on)
app.get('/sendgrid/sync', async (req, res) => {
  const db = await loadDB();
  const total = Object.keys(db.contacts).length;
  res.json({ synced: total, newContacts: 0, updated: total, total });
});

// Get A/B stats from SendGrid activity
app.get('/sendgrid/stats', async (req, res) => {
  try {
    const apiKey = SENDGRID_KEY;
    if (!apiKey) return res.status(500).json({ error: 'No SENDGRID_API_KEY' });

    const db = await loadDB();
    const contacts = Object.values(db.contacts);
    const total = contacts.length;
    const delivered = contacts.filter(c => !c.bounced).length;
    const opens = contacts.filter(c => c.opens > 0).length;
    const clicks = contacts.filter(c => c.clicks > 0).length;
    const calendlyClicks = contacts.filter(c => c.calendlyClick).length;
    const booked = contacts.filter(c => c.booked).length;
    const bounced = contacts.filter(c => c.bounced).length;
    const unsubscribed = contacts.filter(c => c.unsubscribed).length;
    const followupsPending = db.followupQueue.length;
    const followupsSent = db.sentFollowups.length;

    res.json({
      total, delivered, bounced, unsubscribed,
      opens, openRate: delivered > 0 ? Math.round(opens/delivered*100) : 0,
      clicks, clickRate: delivered > 0 ? Math.round(clicks/delivered*100) : 0,
      calendlyClicks, calendlyRate: delivered > 0 ? Math.round(calendlyClicks/delivered*100) : 0,
      booked, followupsPending, followupsSent,
      contacts: db.contacts
    });
  } catch(e) {
    res.status(500).json({ error: e.message });
  }
});


// GET /contacts - return all tracked contacts
app.get('/contacts', async (req, res) => {
  const db = await loadDB();
  res.json({ contacts: Object.values(db.contacts), total: Object.keys(db.contacts).length });
});

// POST /contacts/register - register a sent contact (alias for /track/sent)
app.post('/contacts/register', async (req, res) => {
  try {
    const { email, name, org, subject, track, sentAt } = req.body;
    const db = await loadDB();
    if (!db.contacts[email]) db.contacts[email] = { email };
    const c = db.contacts[email];
    c.name = name||c.name; c.org = org||c.org; c.track = track||c.track;
    c.subject = subject||c.subject; c.firstSentAt = c.firstSentAt || sentAt || new Date().toISOString();
    c.opens = c.opens||0; c.clicks = c.clicks||0;
    const now = Date.now();
    const sentTime = new Date(c.firstSentAt).getTime();
    if (!db.followupQueue.find(f=>f.email===email&&f.type==='day3') && !db.sentFollowups.find(f=>f.email===email&&f.type==='day3'))
      db.followupQueue.push({email,name,org,track,type:'day3',subject,sendAfter:new Date(sentTime+3*24*60*60*1000).toISOString()});
    if (!db.followupQueue.find(f=>f.email===email&&f.type==='day7') && !db.sentFollowups.find(f=>f.email===email&&f.type==='day7'))
      db.followupQueue.push({email,name,org,track,type:'day7',subject,sendAfter:new Date(sentTime+7*24*60*60*1000).toISOString()});
    await saveDB(db);
    res.json({ success: true });
  } catch(e) { res.status(500).json({ error: e.message }); }
});

// POST /config - store config server-side for cron use
app.post('/config', async (req, res) => {
  try {
    const db = await loadDB();
    if (!db.config) db.config = {};
    Object.assign(db.config, req.body);
    await saveDB(db);
    res.json({ success: true });
  } catch(e) { res.status(500).json({ error: e.message }); }
});


// GET /sendgrid/clicks - analyze what the 22 clicks were
// SendGrid free tier doesn't have full activity feed but we can check
// suppressions and our webhook event store
app.get('/sendgrid/clicks', async (req, res) => {
  const db = await loadDB();
  const apiKey = SENDGRID_KEY;

  // Events from our webhook store
  const clickEvents = db.events.filter(e => e.type === 'click');
  const openEvents = db.events.filter(e => e.type === 'open');
  const unsubEvents = db.events.filter(e => e.type === 'unsubscribe' || e.type === 'group_unsubscribe');
  const bounceEvents = db.events.filter(e => e.type === 'bounce');

  // Contacts with engagement
  const engaged = Object.values(db.contacts).filter(c => c.clicks > 0 || c.opens > 0);

  res.json({
    summary: {
      clicks: clickEvents.length,
      opens: openEvents.length,
      unsubscribes: unsubEvents.length,
      bounces: bounceEvents.length,
      engaged: engaged.length
    },
    clickEvents: clickEvents.slice(-50),
    unsubscribeEvents: unsubEvents,
    engagedContacts: engaged.map(c => ({
      email: c.email,
      opens: c.opens,
      clicks: c.clicks,
      calendlyClick: c.calendlyClick,
      unsubscribed: c.unsubscribed || false,
      bounced: c.bounced || false
    }))
  });
});


// ONE-TIME FIX: Re-register all contacts with correct original send dates
app.post('/fix/requeue', async (req, res) => {
  const key = req.headers['x-cron-key'] || req.body?.cronKey;
  if (key !== CRON_SECRET) return res.status(401).json({ error: 'Unauthorized' });

  const contacts = [
    {email:'liz@fixmyair.com',name:'Liz',org:'Fixmyair',subject:'OHA multi-trade hiring challenges',sentAt:'2026-03-18T21:25:00Z'},
    {email:'cvittone@denronhall.com',name:'Chris',org:'Denron Hall',subject:'Denron Hall dual-trade hiring gaps',sentAt:'2026-03-18T21:29:00Z'},
    {email:'smcleod@fields-fowler.com',name:'Scott',org:'Fields & Fowler',subject:'Fields & Fowler multi-trade hiring',sentAt:'2026-03-18T21:32:00Z'},
    {email:'jcordrey@teamrri.com',name:'J. Cordrey',org:'Roofing Resources Inc.',subject:'Qualified roofers — Roofing Resources',sentAt:'2026-03-18T21:35:00Z'},
    {email:'brianm@wcmechanical.com',name:'Brian',org:'WC Mechanical',subject:'72-hour HVAC techs for West Chester',sentAt:'2026-03-18T21:38:00Z'},
    {email:'ssimon@hightechvac.com',name:'S. Simon',org:'HighTec HVAC',subject:'72-hour HVAC techs for HighTec',sentAt:'2026-03-18T21:41:00Z'},
    {email:'nate@dullesplumbinggroup.com',name:'Nate',org:'Dulles Plumbing Group',subject:'Dulles Plumbing Group Northern VA sourcing',sentAt:'2026-03-18T21:44:00Z'},
    {email:'jlc@jamescraftson.com',name:'J.L. Craftson',org:'James CRAFT & Son',subject:'James CRAFT & Son skilled craftspeople',sentAt:'2026-03-18T23:49:00Z'},
    {email:'aggie.king@allamerican-nc.com',name:'Aggie',org:'All American Heating Air & Plumbing',subject:'All American multi-trade hiring gaps',sentAt:'2026-03-19T15:54:00Z'},
    {email:'mhopkins@acmemechanical.com',name:'Matt',org:'Acme Mechanical Contractors',subject:'72-hour HVAC techs for Acme Mechanical',sentAt:'2026-03-19T15:51:00Z'},
    {email:'j.harris@cenvarroofing.com',name:'Jeff',org:'Cenvar Roofing & Solar',subject:'Cenvar dual-skill roofer gaps',sentAt:'2026-03-19T15:57:00Z'},
    {email:'allen@cenvarroofing.com',name:'Allen',org:'Cenvar Roofing & Solar',subject:'Cenvar dual-trade roofer gaps',sentAt:'2026-03-19T16:03:00Z'},
    {email:'jhuttenlock@bestchoiceplumbing.net',name:'Jessica',org:'Best Choice Plumbing & Heating',subject:'Best Choice dual-trade hiring gaps',sentAt:'2026-03-19T16:00:00Z'},
    {email:'jared.haas@ais-york.com',name:'Jared',org:'Advanced Industrial Services Inc.',subject:'AIS industrial maintenance staffing',sentAt:'2026-03-19T16:06:00Z'},
    {email:'csantos@nvroofing.com',name:'Carolina',org:'NV Roofing',subject:'72-hour roofers for NV Roofing',sentAt:'2026-03-19T16:10:00Z'},
    {email:'cal@handysideinc.com',name:'Carley',org:'Handyside Plumbing HVAC & Electrical',subject:'Handyside multi-trade hiring gaps',sentAt:'2026-03-19T16:14:00Z'},
    {email:'michelle@karmacgroup.com',name:'Michelle',org:'Karma Construction Group',subject:'Karma Construction skilled trades gaps',sentAt:'2026-03-19T16:18:00Z'},
    {email:'mark.trickey@comfortsystemsusa.com',name:'Mark',org:'Comfort Systems USA MidAtlantic',subject:'72-hour HVAC techs for Comfort Systems',sentAt:'2026-03-19T16:22:00Z'},
    {email:'mark.sobon@centralmechanical.com',name:'Mark',org:'Central Mechanical Construction',subject:'72-hour pipefitters for Central Mechanical',sentAt:'2026-03-19T16:25:00Z'},
    {email:'gmartin@serviceroofing.com',name:'Guy',org:'Tri-State Service Roofing',subject:'Tri-State multi-territory roofing staffing',sentAt:'2026-03-19T16:28:00Z'},
    {email:'info@rapidfirerentals.com',name:'James',org:'RapidFire Rentals',subject:'RapidFire equipment operator gaps',sentAt:'2026-03-19T16:31:00Z'},
    {email:'jrogers@fourquartersinc.com',name:'Jeremiah',org:'Four Quarters Mechanical',subject:'72-hour HVAC techs for Four Quarters',sentAt:'2026-03-19T16:34:00Z'},
    {email:'daniel@airsolution.us',name:'Daniel',org:'Air Solution Mechanical Services',subject:'72-hour HVAC techs for Air Solution',sentAt:'2026-03-19T16:41:00Z'},
    {email:'sean@superiorphm.com',name:'Sean',org:'Superior Plumbing Heating & Mechanical',subject:'Superior multi-trade technician gaps',sentAt:'2026-03-19T16:44:00Z'},
    {email:'shanedonohue@everyonelovesbacon.com',name:'Shane',org:'Bacon Plumbing Heating Air & Electric',subject:'Bacon Plumbing multi-trade hiring',sentAt:'2026-03-19T16:48:00Z'},
    {email:'rkillian@triangle-contractors.com',name:'Robbie',org:'Triangle Contractors LLC',subject:'Triangle Contractors multi-trade hiring',sentAt:'2026-03-19T18:26:00Z'},
    {email:'rob.struhar@fourtwelvedev.com',name:'Rob',org:'Four Twelve Roofing',subject:'Qualified roofers — Four Twelve market',sentAt:'2026-03-19T18:30:00Z'},
    {email:'dkatchmark@katchmark.com',name:'Denise',org:'Katchmark Construction Inc.',subject:'72-hour carpenters for Katchmark Construction',sentAt:'2026-03-20T21:03:00Z'},
    {email:'ttacconelli@valiantenergyservice.com',name:'Thomas',org:'Valiant Energy Service LLC',subject:'Valiant Energy field tech gaps',sentAt:'2026-03-20T21:00:00Z'},
  ];

  const skip = ['dduvall@rffager.com','csyenrick@smithphillips.net'];
  const db = await loadDB();

  // Clear existing queue for these contacts
  contacts.forEach(c => {
    db.followupQueue = db.followupQueue.filter(f => f.email !== c.email);
  });

  const now = new Date();
  let queued = 0;
  let d3due = 0;

  for (const c of contacts) {
    if (skip.includes(c.email)) continue;
    const sentTime = new Date(c.sentAt).getTime();
    const d3Time = sentTime + 3*24*60*60*1000;
    const d7Time = sentTime + 7*24*60*60*1000;
    const alreadySentD3 = db.sentFollowups.find(f => f.email === c.email && f.type === 'day3');
    const alreadySentD7 = db.sentFollowups.find(f => f.email === c.email && f.type === 'day7');

    if (!db.contacts[c.email]) {
      db.contacts[c.email] = { email: c.email, name: c.name, org: c.org, opens: 0, clicks: 0, firstSentAt: c.sentAt, subject: c.subject };
    }

    if (!alreadySentD3) {
      // If overdue, queue for tomorrow 8am instead of past date
      const sendD3 = d3Time < now.getTime() ? new Date(now.getFullYear(), now.getMonth(), now.getDate()+1, 8, 0, 0).toISOString() : new Date(d3Time).toISOString();
      db.followupQueue.push({ email: c.email, name: c.name, org: c.org, type: 'day3', subject: c.subject, track: 'regional', sendAfter: sendD3 });
      if (d3Time < now.getTime()) d3due++;
      queued++;
    }
    if (!alreadySentD7) {
      const sendD7 = new Date(d7Time).toISOString();
      db.followupQueue.push({ email: c.email, name: c.name, org: c.org, type: 'day7', subject: c.subject, track: 'regional', sendAfter: sendD7 });
      queued++;
    }
  }

  await saveDB(db);
  console.log('Requeue fix:', queued, 'follow-ups queued,', d3due, 'Day 3 rescheduled to tomorrow');
  res.json({ success: true, queued, d3due, message: d3due + ' overdue Day 3 follow-ups scheduled for tomorrow 8am' });
});

app.get('/health', (req, res) => res.json({ status: 'ok', service: 'Legacy Workforce AI CSO', env: { sendgrid: !!SENDGRID_KEY, anthropic: !!ANTHROPIC_KEY, apollo: !!APOLLO_KEY } }));

const PORT = process.env.PORT || 3000;
initDB().then(() => {
  app.listen(PORT, () => console.log('Legacy CSO proxy running on port ' + PORT));
});
