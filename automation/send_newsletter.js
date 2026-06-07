'use strict';

// Weekly Cannabis Law Roundup — Monday 9AM newsletter
// Reads signal data + YouTube video IDs → sends HTML email via SendGrid to all subscribers.

const https  = require('https');
const http   = require('http');
const fs     = require('fs');
const path   = require('path');

// ── Load .env ──────────────────────────────────────────────────────────────
const envFile = path.join(__dirname, '.env');
if (fs.existsSync(envFile)) {
  fs.readFileSync(envFile, 'utf8').split('\n').forEach(line => {
    const eq = line.indexOf('=');
    if (eq > 0) process.env[line.slice(0, eq).trim()] = line.slice(eq + 1).trim();
  });
}

const SENDGRID_API_KEY  = process.env.SENDGRID_API_KEY;
const FROM_EMAIL        = process.env.SENDGRID_FROM_EMAIL || 'subscriptions@horsepowermarketing.com';
const FROM_NAME         = process.env.SENDGRID_FROM_NAME  || 'Horsepower AI';
const YOUTUBE_CHANNEL   = 'UCJw8gCUT9EjhUnMyYnsAPpA';

const CONFIGS_PATH = path.join(__dirname, 'signal-configs.json');
const STATE_PATH   = path.join(__dirname, 'signals-state.json');

const SIGNAL_KEYWORDS = {
  'banking-access':   ['banking access', 'safer banking'],
  'schedule-iii':     ['schedule iii', 'dea reschedul', 'dea reclassif'],
  '280e-tax-reform':  ['280e'],
  'hemp-farm-bill':   ['hemp', 'farm bill'],
  'executive-actions':['executive action'],
  'critical-watch':   ['critical watch'],
};

const RISK_COLORS = {
  CRITICAL: { bg: '#B71C1C', text: '#fff' },
  HIGH:     { bg: '#B8520A', text: '#fff' },
  MONITOR:  { bg: '#1B5E20', text: '#fff' },
};

function log(...args) { console.log(`[${new Date().toISOString()}]`, ...args); }

// ── HTTP helper ────────────────────────────────────────────────────────────
function request(url, options = {}, body = null) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http;
    const req = lib.request(url, options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

// ── Fetch YouTube channel RSS ──────────────────────────────────────────────
async function fetchSignalVideos() {
  const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${YOUTUBE_CHANNEL}`;
  const res = await request(url);
  const videos = {};
  const entries = res.body.match(/<entry>[\s\S]*?<\/entry>/g) || [];
  for (const entry of entries) {
    const titleMatch = entry.match(/<title>([\s\S]*?)<\/title>/);
    const idMatch    = entry.match(/<yt:videoId>([\s\S]*?)<\/yt:videoId>/);
    if (!titleMatch || !idMatch) continue;
    const title  = titleMatch[1].toLowerCase();
    const vidId  = idMatch[1].trim();
    for (const [key, keywords] of Object.entries(SIGNAL_KEYWORDS)) {
      if (!videos[key] && keywords.some(kw => title.includes(kw))) {
        videos[key] = vidId;
      }
    }
  }
  return videos;
}

// ── Get all SendGrid subscribers ───────────────────────────────────────────
async function getSubscribers() {
  const body = JSON.stringify({ query: "email != ''" });
  const res = await request(
    'https://api.sendgrid.com/v3/marketing/contacts/search',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SENDGRID_API_KEY}`,
        'Content-Type': 'application/json',
      }
    },
    body
  );
  if (res.status !== 200) {
    log('SendGrid contacts error:', res.status, res.body);
    return [];
  }
  const data = JSON.parse(res.body);
  return data.result || [];
}

// ── Build HTML email ───────────────────────────────────────────────────────
function buildEmail(configs, state, videos) {
  const today  = new Date().toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric', year:'numeric' });
  const ORDER  = ['banking-access','schedule-iii','280e-tax-reform','hemp-farm-bill','executive-actions','critical-watch'];

  const signalRows = ORDER.map(key => {
    const cfg    = configs[key] || {};
    const st     = state.signals?.[key] || {};
    const risk   = st.lastStatus || 'MONITOR';
    const colors = RISK_COLORS[risk] || RISK_COLORS.MONITOR;
    const vidId  = videos[key] || '';
    const ytUrl  = vidId ? `https://www.youtube.com/watch?v=${vidId}` : null;

    return `
    <tr>
      <td style="padding:0 0 20px 0">
        <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #DDE3ED;border-left:4px solid ${colors.bg};border-radius:8px;background:#fff">
          <tr>
            <td style="padding:16px 20px">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="font-size:11px;font-weight:800;color:#1B4332;letter-spacing:.08em;text-transform:uppercase">${cfg.emoji || '●'} ${cfg.displayName || key.toUpperCase()}</span>
                    &nbsp;&nbsp;
                    <span style="background:${colors.bg};color:${colors.text};font-size:10px;font-weight:800;padding:2px 8px;border-radius:10px;letter-spacing:.06em">${risk}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0 12px">
                    <p style="margin:0;font-size:14px;color:#2a2a2a;line-height:1.6">${cfg.embedDescription || ''}</p>
                  </td>
                </tr>
                ${ytUrl ? `
                <tr>
                  <td>
                    <a href="${ytUrl}" style="display:inline-block;background:${colors.bg};color:#fff;font-size:12px;font-weight:800;padding:8px 18px;border-radius:6px;text-decoration:none">&#9654; Watch Briefing</a>
                  </td>
                </tr>` : `
                <tr>
                  <td>
                    <span style="display:inline-block;background:#9E9E9E;color:#fff;font-size:12px;font-weight:800;padding:8px 18px;border-radius:6px">&#8987; Briefing Coming Soon</span>
                  </td>
                </tr>`}
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>`;
  }).join('');

  return `<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f0;font-family:Arial,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f0;padding:30px 0">
    <tr>
      <td align="center">
        <table width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%">

          <!-- Header -->
          <tr>
            <td style="background:#1B4332;border-radius:10px 10px 0 0;padding:32px 36px;text-align:center">
              <p style="margin:0 0 4px;font-size:11px;font-weight:800;color:#D4A017;letter-spacing:.12em;text-transform:uppercase">GF Tech One AI Compliance Engine</p>
              <h1 style="margin:0 0 8px;font-size:26px;font-weight:800;color:#fff">Weekly Cannabis Law Roundup</h1>
              <p style="margin:0;font-size:13px;color:rgba(255,255,255,.75)">${today}</p>
            </td>
          </tr>

          <!-- Intro -->
          <tr>
            <td style="background:#FEFCE8;padding:20px 36px;border-left:1px solid #DDE3ED;border-right:1px solid #DDE3ED">
              <p style="margin:0;font-size:14px;color:#5a6a80;line-height:1.6">Here are this week's 6 federal cannabis regulatory signals — plain English, with video briefings for each.</p>
            </td>
          </tr>

          <!-- Signal Rows -->
          <tr>
            <td style="background:#f9f9f7;padding:24px 36px;border:1px solid #DDE3ED;border-top:none">
              <table width="100%" cellpadding="0" cellspacing="0">
                ${signalRows}
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#1B4332;border-radius:0 0 10px 10px;padding:20px 36px;text-align:center">
              <p style="margin:0 0 6px;font-size:12px;color:rgba(255,255,255,.7)">Produced by <strong style="color:#fff">Horsepower AI</strong> for GF Tech One</p>
              <p style="margin:0;font-size:11px;color:rgba(255,255,255,.5)">
                <a href="https://policy-tracker-rosy.vercel.app" style="color:#D4A017;text-decoration:none">View Full Dashboard</a>
                &nbsp;·&nbsp;
                <span style="color:rgba(255,255,255,.5)">Reply to unsubscribe</span>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;
}

// ── Send via SendGrid ──────────────────────────────────────────────────────
async function sendNewsletter(subscribers, html) {
  if (subscribers.length === 0) {
    log('No subscribers found — nothing to send.');
    return;
  }

  const today = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const subject = `Weekly Cannabis Law Roundup — ${today}`;

  const personalizations = subscribers.map(s => ({
    to: [{ email: s.email, name: s.first_name || '' }]
  }));

  const payload = JSON.stringify({
    personalizations,
    from: { email: FROM_EMAIL, name: FROM_NAME },
    subject,
    content: [{ type: 'text/html', value: html }],
    tracking_settings: {
      click_tracking:  { enable: true },
      open_tracking:   { enable: true },
    }
  });

  const res = await request(
    'https://api.sendgrid.com/v3/mail/send',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${SENDGRID_API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      }
    },
    payload
  );

  if (res.status === 202) {
    log(`Newsletter sent to ${subscribers.length} subscriber(s).`);
  } else {
    log('SendGrid send error:', res.status, res.body);
  }
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  log('=== Weekly Cannabis Law Roundup — Newsletter Send START ===');

  if (!SENDGRID_API_KEY) { log('ERROR: SENDGRID_API_KEY not set.'); process.exit(1); }

  const configs = JSON.parse(fs.readFileSync(CONFIGS_PATH, 'utf8'));
  const state   = JSON.parse(fs.readFileSync(STATE_PATH, 'utf8'));

  log('Fetching YouTube video IDs...');
  const videos = await fetchSignalVideos();
  log('Videos resolved:', Object.entries(videos).filter(([,v])=>v).map(([k,v])=>`${k}:${v}`).join(', ') || 'none');

  log('Fetching subscribers...');
  const subscribers = await getSubscribers();
  log(`${subscribers.length} subscriber(s) found.`);

  const html = buildEmail(configs, state, videos);

  await sendNewsletter(subscribers, html);

  log('=== Newsletter Send COMPLETE ===');
}

main().catch(err => { console.error(err); process.exit(1); });
