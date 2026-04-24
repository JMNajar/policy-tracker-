# PolicyTracker

Cannabis and executive policy intelligence for GF Tech One. Built by [Horsepower AI](https://horsepowermarketing.com).

## Pages

| Page | Update Frequency | Data Source |
|---|---|---|
| Today's News | Daily | Google News RSS |
| Bills | Weekly | Congress.gov API |
| Lawmakers | Monthly | OpenSecrets API |
| Executive | Daily | Federal Register API |
| Money | Weekly | FEC.gov API |
| About | Static | — |

## Setup

### 1. Add logo files
Drop these two files into the `assets/` folder:
- `assets/horsepowerai-logo.png`
- `assets/gft1-logo.png`

### 2. Get API keys (both free)
- **Congress.gov:** Register at [api.congress.gov](https://api.congress.gov) — takes 2 minutes
- **OpenSecrets:** Register at [opensecrets.org/open-data/api](https://www.opensecrets.org/open-data/api)

### 3. Add secrets to GitHub
In your GitHub repo → Settings → Secrets and variables → Actions:
- `CONGRESS_API_KEY` — your Congress.gov key
- `OPENSECRETS_API_KEY` — your OpenSecrets key

### 4. Deploy to Vercel
1. Create a new Vercel project and link to this GitHub repo
2. Set output directory to `/` (root — all HTML files are at root level)
3. Vercel auto-deploys on every push (including the daily GitHub Actions commit)

### 5. Run locally
```bash
pip install requests feedparser
python build_policytracker.py
```
Open any `.html` file in your browser.

## Automation

GitHub Actions runs automatically:
- **Daily 6am ET** — refreshes news and executive actions
- **Weekly Monday 5am ET** — full rebuild including bills and PAC data

## Adding States (Phase 2)
State-level data will be added after the federal site is live. Priority states: California, Florida, Texas, New York, Illinois.

---

*Presented by GF Tech One. Intelligence by Horsepower AI.*
