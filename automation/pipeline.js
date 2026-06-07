'use strict';

// GFTO Policy Tracker — Signal-to-Video Automation Pipeline
// Runs daily. Detects CRITICAL signal changes → generates NotebookLM video
// → uploads to YouTube → embeds on policy-tracker-rosy.vercel.app same day.

const { chromium } = require('playwright');
const fs   = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ── Paths ──────────────────────────────────────────────────────────────────
const ROOT         = path.resolve(__dirname, '..');
const STATE_PATH   = path.join(__dirname, 'signals-state.json');
const CONFIGS_PATH = path.join(__dirname, 'signal-configs.json');
const INDEX_PATH   = path.join(ROOT, 'index.html');
const PROFILE_DIR  = path.join(__dirname, 'browser-profile');
const DOWNLOADS    = path.join(process.env.USERPROFILE || process.env.HOME, 'Downloads');
const LOG_PATH     = path.join(__dirname, 'pipeline.log');

const TRACKER_URL = 'https://policy-tracker-rosy.vercel.app';
const YT_STUDIO   = 'https://studio.youtube.com';

// ── Logging ────────────────────────────────────────────────────────────────
function log(...args) {
  const line = `[${new Date().toISOString()}] ${args.join(' ')}`;
  console.log(line);
  fs.appendFileSync(LOG_PATH, line + '\n');
}

// ── Utilities ──────────────────────────────────────────────────────────────
function loadJSON(p)     { return JSON.parse(fs.readFileSync(p, 'utf8')); }
function saveJSON(p, obj) { fs.writeFileSync(p, JSON.stringify(obj, null, 2)); }

function nameToKey(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function formatDate(iso) {
  return new Date(iso || Date.now()).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  });
}

async function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Signal scraping ────────────────────────────────────────────────────────
async function scrapeSignalStatuses(page) {
  log('Scraping signal panel from live site...');
  await page.goto(TRACKER_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await wait(2000);

  return page.evaluate(() => {
    const results = [];
    document.querySelectorAll('.sig-tile').forEach(tile => {
      const nameSpan  = tile.querySelector('span[style*="font-weight:800"]');
      const badgeSpan = tile.querySelector('span[style*="font-size:.58rem"]');
      if (!nameSpan || !badgeSpan) return;
      const rawName = nameSpan.textContent;
      const name = rawName.replace(/[\u{1F000}-\u{1FFFF}]|[\u{2600}-\u{26FF}]|\u{00a0}|&nbsp;/gu, '').trim();
      const status = badgeSpan.textContent.trim();
      results.push({ name, status });
    });
    return results;
  });
}

// ── Change detection ───────────────────────────────────────────────────────
const LEVEL = { MONITOR: 0, HIGH: 1, CRITICAL: 2 };

function detectChanges(state, currentStatuses) {
  const toRegenerate = [];

  for (const { name, status } of currentStatuses) {
    const key      = nameToKey(name);
    const prev     = state.signals[key]?.lastStatus;
    const noVideo  = !state.signals[key]?.youtubeId;
    const prevLvl  = LEVEL[prev] ?? -1;
    const currLvl  = LEVEL[status] ?? 0;

    if (currLvl > prevLvl) {
      toRegenerate.push(key);
      log(`ESCALATED: ${key} (${prev || 'none'} → ${status}) — new video needed`);
    } else if (noVideo) {
      toRegenerate.push(key);
      log(`NO VIDEO: ${key} (${status}) — generating first video`);
    } else if (prevLvl > currLvl) {
      log(`DE-ESCALATED: ${key} (${prev} → ${status}) — keeping existing video`);
    }
  }

  // Critical Watch always regenerates on Monday — it tracks the highest-priority
  // active bill which changes week to week.
  if (!toRegenerate.includes('critical-watch')) {
    toRegenerate.push('critical-watch');
    log('CRITICAL WATCH: weekly Monday regeneration scheduled');
  }

  return { toRegenerate };
}

// ── NotebookLM — generate video ────────────────────────────────────────────
async function generateNotebookVideo(page, config) {
  log(`Opening notebook: ${config.notebookUrl}`);
  await page.goto(config.notebookUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await wait(2000);

  // Click Studio tab
  await page.getByRole('tab', { name: 'Studio' }).click();
  await wait(1500);

  // Open Video Overview settings (click the expand chevron on the card)
  const videoOverviewBtn = page.locator('button').filter({ hasText: 'Video Overview' }).first();
  // Click the chevron/arrow button adjacent to Video Overview
  const chevronBtn = page.locator('button[class*="chevron"], img[src*="chevron_forward"]').first();
  if (await chevronBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await chevronBtn.click();
  } else {
    await videoOverviewBtn.click();
  }
  await wait(1500);

  // Select "Brief" format if the dialog is open
  const briefOpt = page.getByText('Brief', { exact: true });
  if (await briefOpt.isVisible({ timeout: 3000 }).catch(() => false)) {
    await briefOpt.click();
    await wait(500);
  }

  // Fill focus prompt if a textarea is visible
  const promptArea = page.locator('textarea').last();
  if (await promptArea.isVisible({ timeout: 3000 }).catch(() => false)) {
    await promptArea.click();
    await promptArea.fill(config.focusPrompt);
    await wait(300);
  }

  // Add Business Impact tag if present
  const bizTag = page.getByText('+ Business Impact');
  if (await bizTag.isVisible({ timeout: 2000 }).catch(() => false)) {
    await bizTag.click();
    await wait(300);
  }

  // Click Generate (use last() to avoid ambiguity with other Generate buttons)
  await page.getByRole('button', { name: 'Generate' }).last().click();
  log('Video generation started. Polling every 45 seconds (up to 12 min)...');

  // Poll until "Generating Video Overview..." disappears
  const deadline = Date.now() + 12 * 60 * 1000;
  while (Date.now() < deadline) {
    await wait(45000);
    const stillGenerating = await page
      .getByText('Generating Video Overview')
      .isVisible()
      .catch(() => false);
    if (!stillGenerating) {
      log('Video generation complete.');
      return;
    }
    log('Still generating...');
  }

  throw new Error('Video generation timed out after 12 minutes.');
}

// ── NotebookLM — download video ────────────────────────────────────────────
async function downloadNotebookVideo(page, signalKey) {
  log('Downloading video from NotebookLM...');

  // Click More menu on the generated video card
  const moreBtn = page.getByRole('button', { name: 'More' }).last();
  await moreBtn.click();
  await wait(600);

  // Listen for download event and click Download
  const downloadPromise = page.waitForEvent('download', { timeout: 60000 });
  await page.getByRole('menuitem', { name: 'Download' }).click();

  let filePath;
  try {
    const download = await downloadPromise;
    const suggestedName = download.suggestedFilename();
    filePath = path.join(DOWNLOADS, suggestedName);
    await download.saveAs(filePath);
    log(`Downloaded to: ${filePath}`);
  } catch {
    // Fallback: poll Downloads folder for new MP4
    const before = Date.now();
    const deadline = before + 60000;
    while (Date.now() < deadline) {
      await wait(3000);
      const files = fs.readdirSync(DOWNLOADS)
        .filter(f => f.endsWith('.mp4'))
        .map(f => ({ name: f, mtime: fs.statSync(path.join(DOWNLOADS, f)).mtimeMs }))
        .sort((a, b) => b.mtime - a.mtime);
      if (files.length && files[0].mtime > before - 5000) {
        filePath = path.join(DOWNLOADS, files[0].name);
        log(`Found downloaded file: ${filePath}`);
        break;
      }
    }
  }

  if (!filePath || !fs.existsSync(filePath)) {
    throw new Error('Download failed — MP4 not found in Downloads folder.');
  }

  return filePath;
}

// ── YouTube — upload video ─────────────────────────────────────────────────
async function uploadToYouTube(page, config, filePath) {
  log(`Uploading to YouTube Studio: ${config.videoTitle}`);
  await page.goto(YT_STUDIO, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await wait(2000);

  // Dismiss any welcome/promo dialogs
  const closeBtn = page.getByRole('button', { name: 'Close' }).first();
  if (await closeBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await closeBtn.click();
    await wait(500);
  }

  // Open upload dialog
  await page.getByRole('button', { name: 'Upload videos' }).click();
  await wait(1000);

  // Select file via file chooser
  const [fileChooser] = await Promise.all([
    page.waitForEvent('filechooser'),
    page.getByRole('button', { name: 'Select files' }).click()
  ]);
  await fileChooser.setFiles(filePath);
  log('File selected. Waiting for upload...');
  await wait(4000);

  // Wait for title field to appear
  const titleBox = page.getByRole('textbox', { name: /title/i }).first();
  await titleBox.waitFor({ timeout: 30000 });

  // Set title
  await titleBox.fill(config.videoTitle);

  // Set description
  const descBox = page.getByRole('textbox', { name: /description/i }).first();
  await descBox.fill(config.videoDescription);

  // Answer COPPA
  await page.getByRole('radio', { name: "No, it's not made for kids" }).click();

  // Capture YouTube video ID from the link shown during upload
  const videoLinkEl = page.locator('a[href*="youtu.be"]').first();
  await videoLinkEl.waitFor({ timeout: 60000 });
  const href = await videoLinkEl.getAttribute('href');
  const youtubeId = href?.split('/').pop()?.split('?')[0] || '';
  log(`YouTube ID captured: ${youtubeId}`);

  // Next → Next → Next
  for (let i = 0; i < 3; i++) {
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await wait(1000);
  }

  // Set Public
  await page.getByRole('radio', { name: 'Public' }).click();
  await wait(500);

  // Publish
  await page.locator('role=button[name="Publish"]').click();
  await wait(2000);

  log(`Published: ${config.videoTitle} — https://youtu.be/${youtubeId}`);
  return youtubeId;
}

// ── index.html — build a single video card ─────────────────────────────────
function buildVideoCard(config, youtubeId, status, publishedAt) {
  const dateStr = formatDate(publishedAt);
  const duration = config.embedDuration ? ` · ${config.embedDuration}` : '';
  const badgeBg  = config.statusColor || '#888';

  return `
      <!-- CARD: ${config.displayName} -->
      <div style="border:1px solid ${config.borderColor};border-top:3px solid ${badgeBg};border-radius:10px;overflow:hidden;background:#fff;box-shadow:0 2px 12px rgba(27,67,50,.08)">
        <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden">
          <iframe
            src="https://www.youtube.com/embed/${youtubeId}"
            title="${config.embedTitle}"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
            style="position:absolute;top:0;left:0;width:100%;height:100%">
          </iframe>
        </div>
        <div style="padding:1rem">
          <div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.45rem">
            <span style="background:${badgeBg};color:#fff;font-size:.55rem;font-weight:800;padding:.1rem .4rem;border-radius:8px;letter-spacing:.05em">${status}</span>
            <span style="font-size:.65rem;color:#5a6a80">${config.emoji} ${config.displayName} · ${dateStr}${duration}</span>
          </div>
          <p style="font-size:.82rem;font-weight:700;color:#1B4332;margin:0 0 .4rem">${config.embedTitle}</p>
          <p style="font-size:.76rem;color:#4a5568;line-height:1.5;margin:0 0 .75rem">${config.embedDescription}</p>
          <a href="${config.sourceLink}" target="_blank" rel="noopener" style="font-size:.72rem;font-weight:700;color:#1B4332;text-decoration:none;border:1px solid #A5D6A7;background:#E8F5E9;padding:.3rem .7rem;border-radius:5px;display:inline-block">🏛 ${config.sourceLinkLabel}</a>
        </div>
      </div>`;
}

// ── index.html — rebuild the full VIDEO BRIEFING block ─────────────────────
function rebuildVideoSection(state, configs) {
  const activeVideos = state.activeVideos || [];

  if (activeVideos.length === 0) {
    return ''; // No active videos — remove section entirely
  }

  const cards = activeVideos.map(({ signalKey, youtubeId, publishedAt }) => {
    const config = configs[signalKey];
    const signalState = state.signals[signalKey] || {};
    const status = signalState.lastStatus || 'ACTIVE';
    if (!config || !youtubeId) return '';
    return buildVideoCard(config, youtubeId, status, publishedAt);
  }).join('\n');

  return `<!-- VIDEO BRIEFING -->
<div style="background:#fff;border-top:1px solid #DDE3ED;border-bottom:1px solid #DDE3ED;padding:2rem">
  <div style="max-width:1100px;margin:0 auto">
    <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.25rem;flex-wrap:wrap">
      <span style="font-size:.62rem;font-weight:800;color:#B71C1C;letter-spacing:.12em;text-transform:uppercase;background:#FFEBEE;padding:.28rem .75rem;border-radius:20px;border:1px solid #EF9A9A">📺 VIDEO BRIEFINGS</span>
      <span style="font-size:.78rem;color:#5a6a80">Active signal explainers — AI-generated, same-day</span>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem">
${cards}
    </div>
  </div>
</div>
<!-- END VIDEO BRIEFING -->`;
}

function updateIndexHtml(state, configs) {
  let html = fs.readFileSync(INDEX_PATH, 'utf8');
  const newBlock = rebuildVideoSection(state, configs);

  if (html.includes('<!-- VIDEO BRIEFING -->')) {
    html = html.replace(
      /<!-- VIDEO BRIEFING -->[\s\S]*?<!-- END VIDEO BRIEFING -->/,
      newBlock
    );
  } else if (newBlock) {
    // Insert before WEEK IN REVIEW section
    html = html.replace(
      /(<div class="container"[^>]*>[\s\S]*?WEEK IN REVIEW)/,
      newBlock + '\n\n$1'
    );
  }

  fs.writeFileSync(INDEX_PATH, html);
  log(`index.html updated — ${state.activeVideos?.length || 0} video(s) active.`);
}

// ── Git push ───────────────────────────────────────────────────────────────
function gitPush(message) {
  execSync(`git -C "${ROOT}" add -A`, { stdio: 'pipe' });
  execSync(`git -C "${ROOT}" commit -m "${message.replace(/"/g, '\\"')}"`, { stdio: 'pipe' });
  execSync(`git -C "${ROOT}" push origin main`, { stdio: 'pipe' });
  log('Deployed to Vercel via git push.');
}

// ── Full pipeline: NotebookLM → YouTube → embed ────────────────────────────
async function runVideoPipeline(page, config, signalKey) {
  if (!config.notebookUrl) {
    log(`⚠ No notebook configured for "${signalKey}". Skipping — add notebookUrl to signal-configs.json.`);
    return null;
  }

  // 1. Generate video in NotebookLM
  await generateNotebookVideo(page, config);

  // 2. Download MP4
  const filePath = await downloadNotebookVideo(page, signalKey);

  // 3. Upload to YouTube
  const youtubeId = await uploadToYouTube(page, config, filePath);

  return youtubeId;
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  log('=== Policy Tracker Signal Pipeline START ===');

  const state   = loadJSON(STATE_PATH);
  const configs = loadJSON(CONFIGS_PATH);

  // Launch persistent browser context (preserves Google auth between runs)
  const browser = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false,
    channel: 'chrome',
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--start-maximized'
    ],
    downloadsPath: DOWNLOADS
  });

  const page = (await browser.pages())[0] || await browser.newPage();

  try {
    // 1. Scrape current signal statuses from live site
    const currentStatuses = await scrapeSignalStatuses(page);
    log('Scraped statuses:', JSON.stringify(currentStatuses));

    // 2. Detect changes
    const { toRegenerate } = detectChanges(state, currentStatuses);

    if (toRegenerate.length === 0) {
      log('No signals need new videos. Pipeline done.');
      await browser.close();
      return;
    }

    let embedChanged = false;

    // 3. Generate new videos for all signals that need them
    for (const key of toRegenerate) {
      const config = configs[key];
      if (!config) {
        log(`⚠ Unknown signal key "${key}" — add to signal-configs.json.`);
        continue;
      }

      log(`Running full pipeline for: ${key}`);
      const youtubeId = await runVideoPipeline(page, config, key);
      if (!youtubeId) continue;

      if (!state.signals[key]) state.signals[key] = {};
      state.signals[key].youtubeId = youtubeId;
      state.signals[key].videoPublishedAt = new Date().toISOString().slice(0, 10);
      state.signals[key].embedDuration = config.embedDuration || null;

      // Upsert into active videos list
      if (!state.activeVideos) state.activeVideos = [];
      state.activeVideos = state.activeVideos.filter(v => v.signalKey !== key);
      state.activeVideos.push({
        signalKey: key,
        youtubeId,
        publishedAt: state.signals[key].videoPublishedAt
      });
      embedChanged = true;
    }

    // 4. Update signal status in state
    for (const { name, status } of currentStatuses) {
      const key = nameToKey(name);
      if (!state.signals[key]) state.signals[key] = {};
      state.signals[key].lastStatus = status;
    }
    state.lastRun = new Date().toISOString();
    saveJSON(STATE_PATH, state);

    // 5. Rebuild index.html and deploy if any video changed
    if (embedChanged) {
      updateIndexHtml(state, configs);
      gitPush(`Auto: Monday signal video update [${toRegenerate.join(', ')}]\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`);
    }

    log('=== Pipeline COMPLETE ===');
  } catch (err) {
    log('ERROR:', err.message);
    console.error(err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main();
