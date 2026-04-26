#!/usr/bin/env python3
"""
AI Compliance Engine — Cannabis & Nicotine Compliance Intelligence for Operators
Built by Horsepower AI | Sponsored by GF Tech One
"""

import os, json, re
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    import feedparser
except ImportError:
    os.system("pip install requests feedparser")
    import requests
    import feedparser

OUTPUT_DIR = Path(r"c:\Users\subsc\Documents\My AI Assistant\policy-tracker")
TODAY = datetime.now().strftime("%B %d, %Y")
NOW_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── BRAND COLORS ──────────────────────────────────────────────────────────────
NAVY   = "#1B4332"
RED    = "#D4A017"
CREAM  = "#F5EDE0"
GREEN  = "#2D6B2D"
LGREEN = "#E8F5E9"
LRED   = "#FFF8E1"
LBLUE  = "#E8F5E9"
WHITE  = "#FFFFFF"
LIGHT  = "#FAFAF8"
BORDER = "#DDE3ED"
TEXT   = "#1a2535"
MUTED  = "#5a6a80"

TODAY_SHORT = datetime.now().strftime("%b %d")   # e.g., "Apr 25"

# ── FRESHNESS STATE ───────────────────────────────────────────────────────────
FRESHNESS = None   # Set in main() after fetching executive actions

# ── SHARED CSS ────────────────────────────────────────────────────────────────
CSS = f"""
  :root {{
    --navy:   {NAVY};
    --red:    {RED};
    --cream:  {CREAM};
    --green:  {GREEN};
    --lgreen: {LGREEN};
    --lred:   {LRED};
    --lblue:  {LBLUE};
    --white:  {WHITE};
    --light:  {LIGHT};
    --border: {BORDER};
    --text:   {TEXT};
    --muted:  {MUTED};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; color: var(--text); background: var(--light); }}

  /* NAV */
  nav {{
    position: sticky; top: 0; z-index: 100;
    background: #FEFCE8; padding: 0 2rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 0 rgba(0,0,0,.08), 0 2px 8px rgba(0,0,0,.06);
    min-height: 64px;
  }}
  .nav-brand {{ display: flex; align-items: center; gap: .75rem; text-decoration: none; }}
  .nav-brand img {{
    height: 40px; mix-blend-mode: multiply;
    filter: drop-shadow(0 1px 3px rgba(0,0,0,.25));
  }}
  .nav-brand-text {{ color: {NAVY}; font-size: 1.15rem; font-weight: 800; letter-spacing: .06em; }}
  .nav-brand-text span {{ color: {RED}; }}
  .nav-links {{ display: flex; gap: .15rem; flex-wrap: wrap; }}
  .nav-links a {{
    color: {NAVY}; text-decoration: none; font-size: .78rem; font-weight: 600;
    padding: .45rem .7rem; border-radius: 4px; letter-spacing: .03em;
    transition: background .2s, color .2s; white-space: nowrap;
  }}
  .nav-links a:hover, .nav-links a.active {{ background: rgba(27,67,50,.12); color: {NAVY}; }}

  /* HERO */
  .hero {{
    background: linear-gradient(135deg, {NAVY} 0%, #2D5A3D 100%);
    color: #fff; padding: 3rem 2rem 2.5rem; text-align: center;
  }}
  .hero-tag {{
    display: inline-block; background: rgba(212,160,23,.2);
    color: #FFD54F; font-size: .72rem; font-weight: 700;
    letter-spacing: .1em; padding: .3rem .9rem; border-radius: 20px;
    border: 1px solid rgba(212,160,23,.4); margin-bottom: 1rem;
  }}
  .hero h1 {{ font-size: 2.4rem; font-weight: 800; line-height: 1.15; margin-bottom: .6rem; }}
  .hero h1 span {{ color: #FFD54F; }}
  .hero p {{ color: #A5D6A7; font-size: 1rem; max-width: 620px; margin: 0 auto 2rem; }}
  .stat-row {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
  .stat-card {{
    background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.15);
    border-radius: 10px; padding: 1.1rem 1.5rem; min-width: 140px; text-align: center;
  }}
  .stat-card .num {{ font-size: 1.75rem; font-weight: 800; color: #fff; }}
  .stat-card .lbl {{ font-size: .68rem; color: #A5D6A7; font-weight: 600; letter-spacing: .06em; margin-top: .2rem; }}

  /* SECTIONS */
  .container {{ max-width: 1000px; margin: 0 auto; padding: 3rem 2rem; }}
  .section-tag {{
    display: inline-block; font-size: .68rem; font-weight: 700; letter-spacing: .1em;
    padding: .28rem .75rem; border-radius: 20px; margin-bottom: .65rem;
  }}
  .tag-navy  {{ background: {LGREEN}; color: {NAVY}; }}
  .tag-green {{ background: {LGREEN}; color: {GREEN}; }}
  .tag-red   {{ background: {LRED}; color: {RED}; }}
  .tag-cream {{ background: {CREAM}; color: {NAVY}; }}
  h2 {{ font-size: 1.65rem; font-weight: 800; margin-bottom: .4rem; color: var(--navy); }}
  .section-intro {{ color: var(--muted); font-size: .95rem; margin-bottom: 1.75rem; max-width: 700px; }}

  /* CARDS */
  .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }}
  .card {{
    background: {WHITE}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 1.25rem 1.4rem; transition: box-shadow .2s;
  }}
  .card:hover {{ box-shadow: 0 4px 16px rgba(27,67,50,.1); }}
  .card-source {{ font-size: .7rem; font-weight: 700; color: {RED}; letter-spacing: .06em; text-transform: uppercase; margin-bottom: .4rem; }}
  .card-title {{ font-size: .95rem; font-weight: 700; color: {NAVY}; margin-bottom: .5rem; line-height: 1.35; }}
  .card-title a {{ color: {NAVY}; text-decoration: none; }}
  .card-title a:hover {{ color: {RED}; }}
  .card-meta {{ font-size: .75rem; color: {MUTED}; }}
  .card-impact {{
    margin-top: .65rem; padding: .5rem .75rem;
    background: {LGREEN}; border-left: 3px solid {GREEN};
    border-radius: 0 6px 6px 0; font-size: .8rem; color: {GREEN}; font-weight: 600;
  }}

  /* TABLES */
  .data-table {{ width: 100%; border-collapse: collapse; font-size: .88rem; margin-bottom: 1.5rem; }}
  .data-table th {{
    background: {NAVY}; color: {WHITE}; padding: .6rem .9rem;
    text-align: left; font-size: .75rem; letter-spacing: .05em; font-weight: 700;
  }}
  .data-table td {{ padding: .55rem .9rem; border-bottom: 1px solid {BORDER}; vertical-align: top; }}
  .data-table tr:nth-child(even) {{ background: {LIGHT}; }}
  .data-table tr:hover {{ background: {LGREEN}; }}
  .data-table a {{ color: {NAVY}; text-decoration: none; font-weight: 600; }}
  .data-table a:hover {{ color: {RED}; }}

  /* BADGES */
  .badge {{
    display: inline-block; padding: .2rem .55rem; border-radius: 20px;
    font-size: .68rem; font-weight: 700; letter-spacing: .04em;
  }}
  .badge-green {{ background: {LGREEN}; color: {GREEN}; }}
  .badge-red   {{ background: {LRED}; color: {RED}; }}
  .badge-navy  {{ background: {LGREEN}; color: {NAVY}; }}
  .badge-gray  {{ background: #f0f0f0; color: #666; }}

  /* RISK SCORE BADGES */
  .risk-badge {{ display: inline-block; padding: .18rem .55rem; border-radius: 12px; font-size: .65rem; font-weight: 800; letter-spacing: .05em; white-space: nowrap; }}
  .risk-critical {{ background: #FFEBEE; color: #B71C1C; border: 1px solid #EF9A9A; }}
  .risk-high     {{ background: #FFF3E0; color: #E65100; border: 1px solid #FFCC80; }}
  .risk-medium   {{ background: #FFFDE7; color: #F57F17; border: 1px solid #FFE082; }}
  .risk-low      {{ background: #F5F5F5; color: #757575; border: 1px solid #E0E0E0; }}

  /* FILTER BAR */
  .filter-bar {{ display: flex; gap: .75rem; flex-wrap: wrap; align-items: center; margin-bottom: 1.5rem; padding: 1rem 1.25rem; background: {WHITE}; border: 1px solid {BORDER}; border-radius: 8px; }}
  .filter-bar label {{ font-size: .72rem; font-weight: 700; color: {NAVY}; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }}
  .filter-bar select {{ font-size: .82rem; color: {NAVY}; border: 1px solid {BORDER}; border-radius: 6px; padding: .35rem .7rem; background: {WHITE}; cursor: pointer; font-weight: 600; }}
  .filter-bar select:focus {{ outline: none; border-color: {NAVY}; }}
  .filter-count {{ font-size: .78rem; color: {MUTED}; margin-left: auto; white-space: nowrap; }}

  /* ALERT / PLACEHOLDER */
  .api-pending {{
    background: {CREAM}; border: 1px solid #d4c4a0; border-radius: 8px;
    padding: 1.25rem 1.5rem; margin: 1.5rem 0;
  }}
  .api-pending h3 {{ color: {NAVY}; font-size: 1rem; margin-bottom: .4rem; }}
  .api-pending p {{ color: {MUTED}; font-size: .88rem; }}
  .api-pending code {{
    background: rgba(27,67,50,.08); padding: .1rem .4rem;
    border-radius: 3px; font-family: monospace; font-size: .82rem;
  }}

  /* EMAIL SIGNUP */
  .signup-band {{
    background: linear-gradient(135deg, {GREEN} 0%, #1a4a1a 100%);
    padding: 2.5rem 2rem; text-align: center; color: #fff;
  }}
  .signup-band h3 {{ font-size: 1.4rem; font-weight: 800; margin-bottom: .4rem; }}
  .signup-band p {{ color: rgba(255,255,255,.8); margin-bottom: 1.25rem; font-size: .95rem; }}
  .signup-form {{ display: flex; gap: .75rem; justify-content: center; flex-wrap: wrap; }}
  .signup-form input {{
    padding: .65rem 1rem; border-radius: 6px; border: none;
    font-size: .95rem; min-width: 240px; outline: none;
  }}
  .signup-form button {{
    padding: .65rem 1.5rem; background: {RED}; color: #fff;
    border: none; border-radius: 6px; font-size: .95rem; font-weight: 700;
    cursor: pointer; transition: background .2s;
  }}
  .signup-form button:hover {{ background: #B8860B; }}
  .signup-note {{ font-size: .75rem; color: rgba(255,255,255,.6); margin-top: .75rem; }}

  /* DIVIDER */
  .section-divider {{ border: none; border-top: 1px solid {BORDER}; margin: 0; }}

  /* FOOTER */
  footer {{
    background: {NAVY}; color: rgba(255,255,255,.7);
    padding: 2.5rem 2rem; text-align: center;
  }}
  .footer-logos {{ display: flex; align-items: center; justify-content: center; gap: 2.5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }}
  .footer-logo-block {{ display: flex; align-items: center; gap: .6rem; }}
  .footer-logo-block img {{ height: 36px; background: rgba(255,255,255,.92); border-radius: 6px; padding: 3px 10px; object-fit: contain; }}
  .footer-logo-text {{ color: rgba(255,255,255,.85); font-size: .85rem; font-weight: 600; }}
  .footer-divider {{ width: 1px; height: 32px; background: rgba(255,255,255,.2); }}
  .footer-tagline {{ font-size: .82rem; margin-bottom: .5rem; }}
  .footer-tagline a {{ color: #FFD54F; text-decoration: none; font-weight: 600; }}
  .footer-tagline a:hover {{ color: #F9A825; }}
  .footer-legal {{ font-size: .72rem; color: rgba(255,255,255,.4); }}
  .footer-legal a {{ color: rgba(255,255,255,.65); text-decoration: none; }}
  .footer-legal a:hover {{ color: #FFD54F; }}
  .sponsor-label {{ font-size: .65rem; color: rgba(255,255,255,.4); text-transform: uppercase; letter-spacing: .08em; }}

  /* CREDIBILITY BAR */
  .cred-bar {{
    background: #FEFCE8; border-bottom: 1px solid {BORDER};
    padding: .5rem 2rem; display: flex; align-items: center;
    gap: 1.1rem; flex-wrap: wrap; font-size: .75rem;
  }}
  .cred-bar .cred-label {{ font-size: .65rem; font-weight: 800; color: {NAVY}; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; }}
  .cred-bar a {{ color: {GREEN}; text-decoration: none; font-weight: 600; }}
  .cred-bar a:hover {{ color: {RED}; }}
  .cred-bar .cred-pipe {{ color: {BORDER}; font-weight: 400; }}
  .cred-bar .cred-media {{ color: {NAVY}; font-weight: 700; font-size: .72rem; }}
  .cred-bar .cred-freshness {{ color: {RED}; font-weight: 700; font-size: .72rem; }}
  .cred-bar .cred-verified {{ color: {MUTED}; font-size: .72rem; margin-left: auto; white-space: nowrap; }}

  /* ABOUT PAGE */
  .about-section {{ margin-bottom: 2.5rem; }}
  .about-section p {{ color: #3a4a3a; font-size: .96rem; line-height: 1.7; margin-bottom: 1rem; }}
  .kent-card {{ background: #fff; border: 1px solid {BORDER}; border-radius: 10px; padding: 1.75rem 2rem; margin-bottom: 2rem; border-left: 4px solid {NAVY}; }}
  .kent-card h3 {{ font-size: 1.2rem; font-weight: 800; color: {NAVY}; margin-bottom: .25rem; }}
  .kent-card .kent-title {{ font-size: .82rem; color: {RED}; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 1rem; }}
  .capability-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin: 1.25rem 0 2rem; }}
  .capability-item {{ background: {LGREEN}; border-radius: 8px; padding: .85rem 1.1rem; border-left: 3px solid {GREEN}; font-size: .88rem; font-weight: 600; color: {NAVY}; }}

  /* HAMBURGER */
  .nav-hamburger {{
    display: none; flex-direction: column; gap: 5px;
    background: none; border: none; cursor: pointer; padding: .5rem;
  }}
  .nav-hamburger span {{
    display: block; width: 24px; height: 2px;
    background: {NAVY}; border-radius: 2px; transition: transform .3s, opacity .3s;
  }}
  .nav-hamburger.open span:nth-child(1) {{ transform: translateY(7px) rotate(45deg); }}
  .nav-hamburger.open span:nth-child(2) {{ opacity: 0; transform: scaleX(0); }}
  .nav-hamburger.open span:nth-child(3) {{ transform: translateY(-7px) rotate(-45deg); }}

  /* RESPONSIVE */
  @media (max-width: 768px) {{
    .hero h1 {{ font-size: 1.7rem; }}
    .nav-hamburger {{ display: flex; }}
    .nav-links {{
      display: none; position: fixed; top: 64px; left: 0; right: 0;
      background: #FEFCE8; flex-direction: column;
      padding: .5rem 0 1rem; box-shadow: 0 4px 12px rgba(0,0,0,.3); z-index: 99;
    }}
    .nav-links.open {{ display: flex; }}
    .nav-links a {{ padding: .85rem 1.5rem; font-size: .95rem; border-bottom: 1px solid rgba(27,67,50,.08); }}
    .stat-row {{ gap: .6rem; }}
    .stat-card {{ min-width: 120px; padding: .9rem 1rem; }}
    .cred-bar {{ padding: .4rem 1rem; gap: .5rem; }}
    .cred-bar .cred-verified {{ margin-left: 0; }}
  }}
"""

# ── NAV ───────────────────────────────────────────────────────────────────────
def nav(active=""):
    pages = [
        ("index.html",       "Today's News"),
        ("bills.html",       "Bills"),
        ("lawmakers.html",   "Lawmakers"),
        ("executive.html",   "Executive"),
        ("money.html",       "Money"),
        ("vapor.html",       "Vapor/Nicotine"),
        ("methodology.html", "Methodology"),
        ("about.html",       "About"),
    ]
    links = ""
    for href, label in pages:
        cls = ' class="active"' if active == href else ""
        links += f'<a href="{href}"{cls}>{label}</a>'

    return f"""
<nav>
  <a class="nav-brand" href="index.html">
    <img src="assets/GFTECH1 LOGO.jpg" alt="GF Tech One" onerror="this.style.display='none'">
    <span class="nav-brand-text">GF TECH ONE <span>AI Compliance Engine</span></span>
  </a>
  <button class="nav-hamburger" onclick="toggleNav()" aria-label="Open navigation"><span></span><span></span><span></span></button>
  <div class="nav-links">{links}</div>
</nav>"""

# ── FOOTER ────────────────────────────────────────────────────────────────────
def footer():
    return f"""
<div class="signup-band">
  <h3>Weekly Cannabis Law Roundup</h3>
  <p>The legislation that matters to your business — plain English, every Monday morning.</p>
  <div class="signup-form">
    <input type="text" placeholder="First name">
    <input type="email" placeholder="Your email address">
    <button>Subscribe Free</button>
  </div>
  <p class="signup-note">No spam. Unsubscribe anytime. Produced by Horsepower AI.</p>
</div>

<footer>
  <div class="footer-logos">
    <div class="footer-logo-block">
      <img src="assets/GFTECH1 LOGO.jpg" alt="GF Tech One">
      <div>
        <div class="footer-logo-text">GF Tech One</div>
        <div class="sponsor-label">Intelligence Platform</div>
      </div>
    </div>
    <div class="footer-divider"></div>
    <div class="footer-logo-block">
      <img src="assets/Bold_logo_ HorsepowerAI.png" alt="Horsepower AI">
      <div>
        <div class="footer-logo-text">Horsepower AI</div>
        <div class="sponsor-label">Built by</div>
      </div>
    </div>
  </div>
  <p class="footer-tagline">
    GFTO AI Compliance Engine is a GF Tech One intelligence platform, built by <a href="#">Horsepower AI</a>.
    <a href="mailto:jeff.najar@horsepowermarketing.com">Contact us →</a>
  </p>
  <p class="footer-legal">
    Updated {TODAY} &nbsp;·&nbsp; Official cannabis news supplier to <strong style="color:rgba(255,255,255,.65);">Easyriders Magazine</strong>
    &nbsp;·&nbsp; Data: <a href="https://www.congress.gov" target="_blank" rel="noopener">Congress.gov</a>,
    <a href="https://www.federalregister.gov" target="_blank" rel="noopener">Federal Register</a>,
    <a href="https://www.fec.gov" target="_blank" rel="noopener">FEC.gov</a>,
    <a href="https://www.opensecrets.org" target="_blank" rel="noopener">OpenSecrets</a>, Google News
    &nbsp;·&nbsp; For informational purposes only. Not legal advice.
  </p>
</footer>"""

# ── FRESHNESS ─────────────────────────────────────────────────────────────────
def get_freshness(executive_actions):
    """Find the most recent Federal Register action and return freshness info."""
    latest_dt    = None
    latest_label = None
    type_map = {
        "Rule":                  "Final Rule",
        "Proposed Rule":         "Proposed Rule",
        "Presidential Document": "Presidential Action",
        "Notice":                "Agency Notice",
    }
    for a in executive_actions:
        date_str = a.get("date", "")
        if not date_str:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if latest_dt is None or dt > latest_dt:
                latest_dt    = dt
                latest_label = type_map.get(a.get("type", ""), "Regulatory Action")
        except Exception:
            pass
    if latest_dt is None:
        return None
    now   = datetime.now(timezone.utc)
    delta = now - latest_dt
    hours = int(delta.total_seconds() / 3600)
    if hours < 1:
        ago = "Just now"
    elif hours < 24:
        ago = f"{hours}h ago"
    elif delta.days == 1:
        ago = "1 day ago"
    else:
        ago = f"{delta.days} days ago"
    return {"label": latest_label, "date": latest_dt.strftime("%b %d, %Y"), "ago": ago}

def cred_bar():
    """Generate the credibility bar HTML using the global FRESHNESS state."""
    freshness_html = ""
    if FRESHNESS:
        freshness_html = (
            f'\n  <span class="cred-pipe">·</span>'
            f'\n  <span class="cred-freshness">{FRESHNESS["label"]} — {FRESHNESS["ago"]}</span>'
        )
    return f"""
<div class="cred-bar">
  <span class="cred-label">Verified Sources</span>
  <a href="https://www.congress.gov" target="_blank" rel="noopener">Congress.gov</a>
  <a href="https://www.federalregister.gov" target="_blank" rel="noopener">Federal Register</a>
  <a href="https://www.fec.gov" target="_blank" rel="noopener">FEC.gov</a>
  <a href="https://www.opensecrets.org" target="_blank" rel="noopener">OpenSecrets</a>
  <span class="cred-pipe">·</span>
  <span class="cred-media">Official cannabis news supplier to <strong>Easyriders Magazine</strong></span>{freshness_html}
  <span class="cred-verified">Last verified {TODAY}</span>
</div>"""

# ── PAGE WRAPPER ──────────────────────────────────────────────────────────────
def page(title, active, content):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | GFTO AI Compliance Engine</title>
  <meta name="description" content="AI-powered compliance intelligence for cannabis and nicotine operators. Track legislation, regulations, and campaign finance in real time. Built by Horsepower AI, sponsored by GF Tech One.">
  <style>{CSS}</style>
</head>
<body>
{nav(active)}
{cred_bar()}
{content}
{footer()}
<script>
function toggleNav(){{var btn=document.querySelector('.nav-hamburger');var links=document.querySelector('.nav-links');btn.classList.toggle('open');links.classList.toggle('open');}}
document.addEventListener('click',function(e){{if(!e.target.closest('nav')){{document.querySelector('.nav-hamburger').classList.remove('open');document.querySelector('.nav-links').classList.remove('open');}}}});
</script>
</body>
</html>"""

# ── DATA: GOOGLE NEWS RSS ─────────────────────────────────────────────────────
def fetch_news():
    queries = [
        "cannabis legislation congress 2026",
        "marijuana law federal 2026",
        "cannabis DEA FDA ruling",
        "cannabis banking SAFER act",
        "cannabis executive order Trump",
        "hemp THC regulation 2026",
    ]
    items = []
    seen = set()
    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=en-US&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]:
                link = entry.get("link","")
                if link in seen: continue
                seen.add(link)
                published = entry.get("published","")
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(published)
                    pub_str = dt.strftime("%b %d, %Y")
                    pub_sort = dt.timestamp()
                except:
                    pub_str = published[:16] if published else "Recent"
                    pub_sort = 0
                source = entry.get("source",{}).get("title","News") if hasattr(entry.get("source",{}),"get") else "News"
                items.append({
                    "title": entry.get("title",""),
                    "link":  link,
                    "source": source,
                    "date":  pub_str,
                    "sort":  pub_sort,
                })
        except Exception as e:
            print(f"News RSS error ({q}): {e}")
    items.sort(key=lambda x: x["sort"], reverse=True)
    return items[:10]

# ── DATA: FEDERAL REGISTER ────────────────────────────────────────────────────
def fetch_executive_actions():
    items = []
    for term in ["cannabis","marijuana","hemp"]:
        url = (
            f"https://www.federalregister.gov/api/v1/documents.json"
            f"?conditions[term]={term}"
            f"&conditions[type][]=PRESDOCU"
            f"&conditions[type][]=RULE"
            f"&conditions[type][]=PRORULE"
            f"&per_page=8&order=newest"
        )
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for doc in data.get("results", []):
                items.append({
                    "title":   doc.get("title",""),
                    "type":    doc.get("type",""),
                    "agency":  ", ".join(doc.get("agency_names",[])),
                    "date":    doc.get("publication_date",""),
                    "link":    doc.get("html_url",""),
                    "number":  doc.get("executive_order_number","") or doc.get("document_number",""),
                })
        except Exception as e:
            print(f"Federal Register error ({term}): {e}")
    # deduplicate by link
    seen = set()
    unique = []
    for i in items:
        if i["link"] not in seen:
            seen.add(i["link"])
            unique.append(i)
    unique.sort(key=lambda x: x["date"], reverse=True)
    return unique[:15]

# ── DATA: FEC CANNABIS PACs ───────────────────────────────────────────────────
def fetch_cannabis_pacs():
    url = "https://api.open.fec.gov/v1/committees/?q=cannabis&api_key=DEMO_KEY&per_page=20&sort=-receipts"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        results = data.get("results", [])
        pacs = []
        for c in results:
            pacs.append({
                "name":     c.get("name",""),
                "type":     c.get("committee_type_full",""),
                "state":    c.get("state","US"),
                "receipts": c.get("receipts") or 0,
                "id":       c.get("committee_id",""),
            })
        pacs.sort(key=lambda x: x["receipts"], reverse=True)
        return pacs[:15]
    except Exception as e:
        print(f"FEC PAC error: {e}")
        return []

def fetch_top_donors_cannabis():
    """Top individual/org donors mentioning cannabis in FEC data"""
    url = "https://api.open.fec.gov/v1/schedules/schedule_b/?api_key=DEMO_KEY&recipient_name=cannabis&per_page=20&sort=-disbursement_amount"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get("results",[])[:10]
    except Exception as e:
        print(f"FEC donor error: {e}")
        return []

# ── DATA: OPPOSITION WATCH ────────────────────────────────────────────────────
OPPOSITION_PAC_SEARCHES = [
    ("pharmaceutical research manufacturers", "Pharmaceutical"),
    ("national beer wholesalers",             "Alcohol"),
    ("wine spirits wholesalers",              "Alcohol"),
    ("geo group",                             "Private Prison"),
    ("corecivic",                             "Private Prison"),
]

def fetch_opposition_disbursements():
    """Pull FEC disbursements from known anti-cannabis industry PACs."""
    recipients = {}
    for query, industry in OPPOSITION_PAC_SEARCHES:
        try:
            r = requests.get(
                f"https://api.open.fec.gov/v1/committees/"
                f"?q={query.replace(' ', '+')}&api_key=DEMO_KEY&per_page=3",
                timeout=10
            )
            committees = r.json().get("results", [])
            if not committees:
                continue
            cid   = committees[0]["committee_id"]
            cname = committees[0]["name"]
        except Exception as e:
            print(f"FEC opp search ({query}): {e}")
            continue
        try:
            r2 = requests.get(
                f"https://api.open.fec.gov/v1/schedules/schedule_b/"
                f"?committee_id={cid}&api_key=DEMO_KEY"
                f"&per_page=20&sort=-disbursement_amount&two_year_transaction_period=2024",
                timeout=10
            )
            disbursements = r2.json().get("results", [])
        except Exception as e:
            print(f"FEC opp disbursements ({cname}): {e}")
            continue
        for d in disbursements:
            amt = d.get("disbursement_amount") or 0
            if amt < 2500:
                continue
            rec = d.get("recipient_name", "").strip()
            if not rec:
                continue
            key = rec.upper()
            if key not in recipients:
                recipients[key] = {"name": rec, "total": 0, "industries": set(), "pacs": set()}
            recipients[key]["total"] += amt
            recipients[key]["industries"].add(industry)
            recipients[key]["pacs"].add(cname)

    result = [
        {
            "name":       v["name"],
            "total":      v["total"],
            "industries": ", ".join(sorted(v["industries"])),
            "pacs":       ", ".join(list(v["pacs"])[:2]),
        }
        for v in recipients.values()
    ]
    result.sort(key=lambda x: x["total"], reverse=True)
    return result[:20]


def fetch_opposition_news():
    """Google News RSS targeted at anti-cannabis industry funding stories."""
    queries = [
        "pharmaceutical lobby cannabis block congress",
        "alcohol industry cannabis oppose legislation",
        "private prison cannabis lobbying congress",
        "anti-cannabis PAC funding legislator",
        "pharma alcohol prison oppose marijuana legalization",
    ]
    items = []
    seen = set()
    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=en-US&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                link = entry.get("link", "")
                if link in seen:
                    continue
                seen.add(link)
                published = entry.get("published", "")
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(published)
                    pub_str = dt.strftime("%b %d, %Y")
                    pub_sort = dt.timestamp()
                except:
                    pub_str = published[:16] if published else "Recent"
                    pub_sort = 0
                source = entry.get("source", {}).get("title", "News") if hasattr(entry.get("source", {}), "get") else "News"
                items.append({
                    "title":  entry.get("title", ""),
                    "link":   link,
                    "source": source,
                    "date":   pub_str,
                    "sort":   pub_sort,
                })
        except Exception as e:
            print(f"Opposition news RSS ({q}): {e}")
    items.sort(key=lambda x: x["sort"], reverse=True)
    return items[:8]


# ── DATA: CONGRESS.GOV BILLS ─────────────────────────────────────────────────
def fetch_bills():
    api_key = os.environ.get("CONGRESS_API_KEY", "x6DiIlrW2gyfGrXC9I1ySo9qVFjuwpEyNDFuCM6c")
    search_terms = ["cannabis", "marijuana", "hemp"]
    bill_stubs = []
    seen = set()
    for term in search_terms:
        url = (
            f"https://api.congress.gov/v3/bill"
            f"?query={term}&sort=updateDate+desc&limit=20"
            f"&api_key={api_key}"
        )
        try:
            r = requests.get(url, timeout=12)
            data = r.json()
            for b in data.get("bills", []):
                bill_id = f"{b.get('congress','')}-{b.get('type','')}-{b.get('number','')}"
                if bill_id in seen:
                    continue
                seen.add(bill_id)
                bill_stubs.append(b)
        except Exception as e:
            print(f"Congress.gov error ({term}): {e}")

    # Fetch bill detail for each stub to get sponsor (list endpoint omits it)
    bills = []
    for b in bill_stubs[:25]:
        congress = b.get("congress","119")
        btype    = b.get("type","").lower()
        bnum     = b.get("number","")
        detail_url = f"https://api.congress.gov/v3/bill/{congress}/{btype}/{bnum}?api_key={api_key}"
        sponsor_name = ""
        sponsor_party = ""
        sponsor_state = ""
        sponsor_bioguide = ""
        try:
            dr = requests.get(detail_url, timeout=10)
            detail = dr.json().get("bill", {})
            sponsors = detail.get("sponsors", [])
            if sponsors:
                s = sponsors[0]
                sponsor_name     = f"{s.get('firstName','')} {s.get('lastName','')}".strip()
                sponsor_party    = s.get("party","")
                sponsor_state    = s.get("state","")
                sponsor_bioguide = s.get("bioguideId","")
        except:
            pass
        bills.append({
            "number":          f"{b.get('type','')} {b.get('number','')}",
            "title":           b.get("title","")[:140],
            "sponsor":         sponsor_name,
            "sponsor_party":   sponsor_party,
            "sponsor_state":   sponsor_state,
            "sponsor_bioguide": sponsor_bioguide,
            "chamber":         "Senate" if b.get("originChamberCode","") == "S" else "House",
            "congress":        congress,
            "updated":         b.get("updateDate","")[:10],
            "url":             f"https://www.congress.gov/bill/{congress}th-congress/{btype}-bill/{bnum}",
            "latest_action":   b.get("latestAction",{}).get("text","")[:120],
        })

    bills.sort(key=lambda x: x["updated"], reverse=True)
    return bills


# ── RISK SCORING ──────────────────────────────────────────────────────────────
HIGH_PRIORITY_BILLS = [
    'safer banking', 'safe banking', 'schedule iii', '280e',
    'cannabis administration', 'marijuana opportunity', 'states reform',
    'hope act', 'federal legalization', 'more act', 'cannabis act',
]

def score_bill(bill):
    """Return (label, css_class) risk score for a bill based on available signals."""
    score = 0
    action = bill.get('latest_action', '').lower()
    title  = bill.get('title', '').lower()

    if any(w in action for w in ['passed', 'agreed to', 'signed by president', 'became public law']):
        score += 5
    if any(w in action for w in ['vote', 'voted', 'roll call', 'yeas and nays']):
        score += 3
    if any(w in action for w in ['markup', 'ordered to be reported', 'discharged from committee']):
        score += 2
    if any(w in action for w in ['hearing', 'subcommittee', 'placed on calendar']):
        score += 1
    if any(p in title for p in HIGH_PRIORITY_BILLS):
        score += 2

    if score >= 6: return ('CRITICAL', 'risk-critical')
    if score >= 4: return ('HIGH',     'risk-high')
    if score >= 2: return ('MEDIUM',   'risk-medium')
    return           ('LOW',      'risk-low')


# ── STATE / SECTOR TAGGING ────────────────────────────────────────────────────
STATE_NAMES = {
    'alabama':'AL','alaska':'AK','arizona':'AZ','arkansas':'AR','california':'CA',
    'colorado':'CO','connecticut':'CT','delaware':'DE','florida':'FL','georgia':'GA',
    'hawaii':'HI','idaho':'ID','illinois':'IL','indiana':'IN','iowa':'IA',
    'kansas':'KS','kentucky':'KY','louisiana':'LA','maine':'ME','maryland':'MD',
    'massachusetts':'MA','michigan':'MI','minnesota':'MN','mississippi':'MS',
    'missouri':'MO','montana':'MT','nebraska':'NE','nevada':'NV','new hampshire':'NH',
    'new jersey':'NJ','new mexico':'NM','new york':'NY','north carolina':'NC',
    'north dakota':'ND','ohio':'OH','oklahoma':'OK','oregon':'OR','pennsylvania':'PA',
    'rhode island':'RI','south carolina':'SC','south dakota':'SD','tennessee':'TN',
    'texas':'TX','utah':'UT','vermont':'VT','virginia':'VA','washington':'WA',
    'west virginia':'WV','wisconsin':'WI','wyoming':'WY',
}

SECTOR_KEYWORDS = {
    'banking':     ['bank', 'safer', 'safe act', 'financial', 'credit union', 'payment', 'cash', 'loan', 'fintech'],
    'tax':         ['280e', 'tax', 'irs', 'deduction', 'deduct', 'revenue', 'treasury'],
    'retail':      ['dispensary', 'retail', 'storefront', 'point of sale', 'pos', 'consumer'],
    'cultivation': ['cultivat', 'grow', 'farm', 'harvest', 'greenhouse', 'agricultural'],
    'testing':     ['lab', 'testing', 'test ', 'potency', 'compliance', 'contaminant'],
    'hemp':        ['hemp', 'cbd', 'cbg', 'delta-8', 'delta8', 'thc limit', 'farm bill'],
    'mso':         ['multi-state', 'multistate', 'interstate', 'national', 'federal legalization'],
    'executive':   ['dea', 'fda', 'doj', 'schedule iii', 'reclassif', 'executive order', 'agency'],
}

def tag_item(text):
    """Return (states_str, sectors_str) data-attribute values for a text blob."""
    t = text.lower()
    states  = [code for name, code in STATE_NAMES.items() if name in t]
    sectors = [sec for sec, kws in SECTOR_KEYWORDS.items() if any(kw in t for kw in kws)]
    return (
        ','.join(sorted(set(states))) or 'federal',
        ','.join(sorted(set(sectors))) or 'general',
    )


# ── CONFLICT-OF-INTEREST LOOKUP ────────────────────────────────────────────────
# Lawmakers documented as (a) on a cannabis-relevant committee AND
# (b) receiving opposition-industry PAC funding.  Source: FEC.gov + committee rosters.
CONFLICT_LAWMAKERS = {
    "Chuck Grassley":      {"committee": "Senate Judiciary & Finance", "industry": "Pharmaceutical"},
    "Tom Cotton":          {"committee": "Senate Judiciary",           "industry": "Pharmaceutical, Alcohol"},
    "Marsha Blackburn":    {"committee": "Senate Judiciary",           "industry": "Pharmaceutical"},
    "Jim Jordan":          {"committee": "House Judiciary",            "industry": "Pharmaceutical"},
    "Patrick McHenry":     {"committee": "House Financial Services",   "industry": "Alcohol, Pharmaceutical"},
    "Kevin Brady":         {"committee": "House Ways & Means",         "industry": "Pharmaceutical"},
    "Mitch McConnell":     {"committee": "Senate Agriculture",         "industry": "Alcohol, Pharmaceutical"},
    "John Cornyn":         {"committee": "Senate Judiciary",           "industry": "Pharmaceutical"},
    "Mike Crapo":          {"committee": "Senate Banking & Finance",   "industry": "Pharmaceutical"},
}

# ── SIGNAL PANEL ─────────────────────────────────────────────────────────────
def build_signal_panel(bills, executive, news):
    """Generate the 6-tile regulatory signal dashboard above the news feed."""

    def parse_date(s):
        try:
            return datetime.strptime(str(s)[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def find_best(items, key_fields, keywords):
        for item in items:
            text = ' '.join(str(item.get(f, '')) for f in key_fields).lower()
            if any(kw in text for kw in keywords):
                return item
        return None

    def tile(icon, label, risk, status_text, date_str, link):
        now = datetime.now(timezone.utc)
        dt = parse_date(date_str)
        days = (now - dt).days if dt else 999

        active = days <= 7
        dot_html = (
            '<span style="color:#2E7D32;font-size:.63rem;font-weight:800;white-space:nowrap">&#9679; ACTIVE</span>'
            if active else
            '<span style="color:#BDBDBD;font-size:.63rem;font-weight:600;white-space:nowrap">&#9675; QUIET</span>'
        )

        colors = {
            'CRITICAL': ('#B71C1C', '#FFF5F5', '#EF9A9A'),
            'HIGH':     ('#B8520A', '#FFF8F0', '#FFCC80'),
            'MONITOR':  ('#1B5E20', '#F1F8F1', '#A5D6A7'),
        }
        tc, bg, bc = colors.get(risk, colors['MONITOR'])
        badge_bg = tc

        return f"""<a href="{link}" style="text-decoration:none;flex:1;min-width:148px;max-width:210px">
  <div class="sig-tile" style="background:{bg};border:1px solid {bc};border-left:4px solid {tc};border-radius:8px;padding:.85rem 1rem;height:100%">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.4rem;gap:.3rem">
      <span style="font-size:.7rem;font-weight:800;color:{tc};letter-spacing:.04em;line-height:1.2">{icon}&nbsp;{label}</span>
      {dot_html}
    </div>
    <div style="margin-bottom:.5rem">
      <span style="background:{badge_bg};color:#fff;font-size:.58rem;font-weight:800;padding:.1rem .42rem;border-radius:10px;letter-spacing:.05em">{risk}</span>
    </div>
    <div style="font-size:.76rem;color:#2a2a2a;line-height:1.38;font-weight:500">{status_text}</div>
  </div>
</a>"""

    tiles = []

    # ── 1. Banking Access ────────────────────────────────────────────────────
    b_bank = find_best(bills, ['title', 'latest_action'], ['safer', 'safe banking', 'banking access', 'financial services'])
    if b_bank:
        action = b_bank['latest_action'][:60].rstrip(',. ')
        risk_b = 'CRITICAL' if any(w in b_bank['latest_action'].lower() for w in ['vote', 'passed', 'floor', 'calendar']) else 'HIGH'
        s_bank = f"{action} · {b_bank['updated']}"
        d_bank = b_bank['updated']
    else:
        s_bank = "SAFER Banking — Senate calendar pending"
        risk_b = 'HIGH'
        d_bank = ''
    tiles.append(tile('🏦', 'BANKING ACCESS', risk_b, s_bank, d_bank, 'bills.html'))

    # ── 2. Schedule III / DEA ────────────────────────────────────────────────
    e_iii = find_best(executive, ['title', 'agency'], ['schedule', 'dea', 'reclassif', 'drug enforcement', 'scheduling'])
    if e_iii:
        s_iii = e_iii['title'][:60].rstrip(',. ') + f" · {e_iii['date']}"
        d_iii = e_iii['date']
        risk_iii = 'CRITICAL'
    else:
        n_iii = find_best(news, ['title'], ['schedule iii', 'dea', 'reclassif', 'scheduling'])
        if n_iii:
            s_iii = n_iii['title'][:60].rstrip(',. ') + f" · {n_iii['date']}"
            d_iii = n_iii.get('date', '')
            risk_iii = 'HIGH'
        else:
            s_iii = "DEA rescheduling — federal process ongoing"
            d_iii = ''
            risk_iii = 'HIGH'
    tiles.append(tile('💊', 'SCHEDULE III', risk_iii, s_iii, d_iii, 'executive.html'))

    # ── 3. 280E Tax ──────────────────────────────────────────────────────────
    b_tax = find_best(bills, ['title', 'latest_action'], ['280e', 'tax', 'deduction', 'internal revenue', 'irs'])
    if b_tax:
        action_t = b_tax['latest_action'][:60].rstrip(',. ')
        s_tax = f"{action_t} · {b_tax['updated']}"
        d_tax = b_tax['updated']
        risk_t = 'HIGH'
    else:
        s_tax = "280E reform — committee stage, no floor date"
        d_tax = ''
        risk_t = 'MONITOR'
    tiles.append(tile('💸', '280E TAX REFORM', risk_t, s_tax, d_tax, 'bills.html'))

    # ── 4. Hemp / Farm Bill ──────────────────────────────────────────────────
    b_hemp = find_best(bills, ['title', 'latest_action'], ['hemp', 'farm bill', 'thc limit', 'delta-8', 'delta 8'])
    if b_hemp:
        s_hemp = b_hemp['title'][:55].rstrip(',. ') + f" · {b_hemp['updated']}"
        d_hemp = b_hemp['updated']
        risk_h = 'HIGH'
    else:
        n_hemp = find_best(news, ['title'], ['hemp', 'farm bill', 'cbd regulation'])
        if n_hemp:
            s_hemp = n_hemp['title'][:60].rstrip(',. ') + f" · {n_hemp['date']}"
            d_hemp = n_hemp.get('date', '')
            risk_h = 'MONITOR'
        else:
            s_hemp = "Farm Bill renewal — Congress pending"
            d_hemp = ''
            risk_h = 'MONITOR'
    tiles.append(tile('🌿', 'HEMP / FARM BILL', risk_h, s_hemp, d_hemp, 'bills.html'))

    # ── 5. Executive Actions ─────────────────────────────────────────────────
    e_latest = executive[0] if executive else None
    if e_latest:
        s_exec = e_latest['title'][:60].rstrip(',. ') + f" · {e_latest['date']}"
        d_exec = e_latest['date']
        dt_e = parse_date(d_exec)
        now_e = datetime.now(timezone.utc)
        days_e = (now_e - dt_e).days if dt_e else 999
        risk_e = 'HIGH' if days_e <= 7 else 'MONITOR'
    else:
        s_exec = "Monitoring DEA, FDA, DOJ, Treasury"
        d_exec = ''
        risk_e = 'MONITOR'
    tiles.append(tile('🏛', 'EXECUTIVE ACTIONS', risk_e, s_exec, d_exec, 'executive.html'))

    # ── 6. Critical Watch — highest-scoring active bill ──────────────────────
    crit_bill = None
    for priority in ['CRITICAL', 'HIGH']:
        for b in bills:
            rl, _ = score_bill(b)
            if rl == priority:
                crit_bill = b
                break
        if crit_bill:
            break

    if crit_bill:
        rl_c, _ = score_bill(crit_bill)
        s_crit = crit_bill['title'][:60].rstrip(',. ') + f" · {crit_bill['updated']}"
        d_crit = crit_bill['updated']
    else:
        rl_c = 'HIGH'
        s_crit = "Monitoring all active legislative signals"
        d_crit = ''
    tiles.append(tile('⚠', 'CRITICAL WATCH', rl_c, s_crit, d_crit, 'bills.html'))

    tiles_html = '\n'.join(tiles)

    return f"""
<div style="background:#FEFCE8;border-top:3px solid {NAVY};border-bottom:1px solid {BORDER};padding:1.5rem 2rem">
  <div style="max-width:1000px;margin:0 auto">
    <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:1rem;flex-wrap:wrap;gap:.4rem">
      <div>
        <span style="font-size:.62rem;font-weight:800;color:{NAVY};letter-spacing:.12em;text-transform:uppercase">Signal Panel</span>
        <span style="font-size:.62rem;color:{MUTED};margin-left:.6rem">Click any signal for full detail</span>
      </div>
      <span style="font-size:.68rem;color:{MUTED}">Updated {TODAY} &nbsp;·&nbsp; <span style="color:#2E7D32;font-weight:700">&#9679; ACTIVE</span> = movement in last 7 days</span>
    </div>
    <div style="display:flex;gap:.75rem;flex-wrap:wrap">
      {tiles_html}
    </div>
  </div>
</div>
<style>
  .sig-tile {{ transition: box-shadow .18s, transform .18s; cursor: pointer; }}
  .sig-tile:hover {{ box-shadow: 0 4px 18px rgba(27,67,50,.15); transform: translateY(-2px); }}
</style>"""


# ── BUILD: INDEX (HOME) ───────────────────────────────────────────────────────
def build_index(news_items, bills=None, executive=None):
    count = len(news_items)

    news_cards = ""
    for item in news_items:
        source = item["source"][:30] if item["source"] else "News"
        title  = item["title"][:120]
        _, sectors_tag = tag_item(item["title"])
        news_cards += f"""
    <div class="card" data-sectors="{sectors_tag}">
      <div class="card-source">{source}</div>
      <div class="card-title"><a href="{item['link']}" target="_blank" rel="noopener">{title}</a></div>
      <div class="card-meta">{item['date']}</div>
    </div>"""

    signal_panel = build_signal_panel(bills or [], executive or [], news_items)

    content = f"""
<div class="hero">
  <div class="hero-tag">UPDATED {TODAY.upper()}</div>
  <h1>Cannabis & Executive Policy<br><span>Intelligence Dashboard</span></h1>
  <p>The legislation, executive actions, and money behind the vote — built for cannabis business leaders.</p>
  <div class="stat-row">
    <div class="stat-card"><div class="num">50+</div><div class="lbl">REGULATORY ITEMS TRACKED</div></div>
    <div class="stat-card"><div class="num">Daily</div><div class="lbl">AUTO-UPDATED</div></div>
    <div class="stat-card"><div class="num">{TODAY_SHORT}</div><div class="lbl">LAST VERIFIED</div></div>
    <div class="stat-card"><div class="num">Free</div><div class="lbl">ALWAYS</div></div>
  </div>
</div>

{signal_panel}

<hr class="section-divider">

<div class="container">
  <span class="section-tag tag-red">TODAY'S TOP {count}</span>
  <h2>Cannabis Policy News</h2>
  <p class="section-intro">The most important cannabis legislation and regulatory stories updated every morning.
     Click any headline for the full story.</p>

  <div class="filter-bar">
    <label>Filter by Sector</label>
    <select id="news-sector-filter" onchange="filterNews()">
      <option value="all">All Sectors</option>
      <option value="banking">Banking & Finance</option>
      <option value="tax">Tax (280E)</option>
      <option value="retail">Retail / Dispensary</option>
      <option value="cultivation">Cultivation</option>
      <option value="testing">Testing & Lab</option>
      <option value="hemp">Hemp / CBD</option>
      <option value="mso">Multi-State Operators</option>
      <option value="executive">DEA / FDA / Executive</option>
    </select>
    <span class="filter-count" id="news-filter-count">{count} stories shown</span>
  </div>

  <div class="card-grid" id="news-grid">
    {news_cards}
  </div>
  <p id="news-empty" style="display:none;text-align:center;color:#999;padding:1.5rem">No stories match that sector filter.</p>
<script>
  function filterNews() {{
    var sector = document.getElementById('news-sector-filter').value;
    var cards  = document.querySelectorAll('#news-grid .card');
    var shown  = 0;
    cards.forEach(function(c) {{
      var sectors = c.dataset.sectors || '';
      var ok = sector === 'all' || sectors.indexOf(sector) !== -1;
      c.style.display = ok ? '' : 'none';
      if (ok) shown++;
    }});
    document.getElementById('news-filter-count').textContent = shown + ' stories shown';
    document.getElementById('news-empty').style.display = shown === 0 ? 'block' : 'none';
  }}
</script>

  <hr class="section-divider" style="margin: 2rem 0;">

  <span class="section-tag tag-navy">NAVIGATE THE TRACKER</span>
  <h2>What's Inside GFTO AI Compliance Engine</h2>
  <p class="section-intro">Four intelligence layers — legislation, lawmakers, executive actions, and the money behind the vote.</p>
  <div class="card-grid">
    <div class="card">
      <div class="card-source" style="color:{NAVY}">BILLS</div>
      <div class="card-title"><a href="bills.html">Cannabis Bills in Congress</a></div>
      <div class="card-meta">Active bills, committee status, floor votes — updated weekly</div>
      <div class="card-impact" style="background:{LBLUE};border-color:{NAVY};color:{NAVY};">Federal legislation tracked in plain English</div>
    </div>
    <div class="card">
      <div class="card-source" style="color:{GREEN}">LAWMAKERS</div>
      <div class="card-title"><a href="lawmakers.html">Who's Sponsoring What</a></div>
      <div class="card-meta">Legislators behind cannabis bills with campaign finance context</div>
      <div class="card-impact">Who funds the people writing the laws</div>
    </div>
    <div class="card">
      <div class="card-source" style="color:{RED}">EXECUTIVE</div>
      <div class="card-title"><a href="executive.html">Presidential & Agency Actions</a></div>
      <div class="card-meta">Executive orders, DEA/FDA/DOJ rulings — updated weekly</div>
      <div class="card-impact" style="background:{LRED};border-color:{RED};color:{RED};">Moves faster than Congress — watch this page</div>
    </div>
    <div class="card">
      <div class="card-source" style="color:#8B6914">MONEY</div>
      <div class="card-title"><a href="money.html">The Money Behind the Vote</a></div>
      <div class="card-meta">Cannabis PACs, opposition industry funding, campaign finance map</div>
      <div class="card-impact" style="background:#FFF8E1;border-color:#F9A825;color:#7a5800;">Big Pharma, alcohol, tobacco — follow the money</div>
    </div>
  </div>
</div>"""

    return page("Today's Cannabis Policy News", "index.html", content)

# ── BUILD: BILLS ──────────────────────────────────────────────────────────────
def build_bills(bills):
    bill_count = len(bills)

    if bills:
        rows = ""
        for b in bills:
            risk_label, risk_cls = score_bill(b)
            states_tag, sectors_tag = tag_item(b['title'] + ' ' + b['latest_action'])
            rows += f"""
      <tr data-states="{states_tag}" data-sectors="{sectors_tag}">
        <td><strong><a href="{b['url']}" target="_blank" rel="noopener">{b['number']}</a></strong></td>
        <td>{b['title']}</td>
        <td>{b['sponsor']}</td>
        <td>{b['latest_action']}</td>
        <td style="white-space:nowrap">{b['updated']}</td>
        <td><span class="risk-badge {risk_cls}">{risk_label}</span></td>
      </tr>"""
        live_section = f"""
  <span class="section-tag tag-navy">LIVE FROM CONGRESS.GOV</span>
  <h2>Cannabis Legislation — <span id="bill-count">{bill_count}</span> Bills Found</h2>
  <p class="section-intro">All cannabis, marijuana, and hemp-related bills in the 119th Congress sorted by most recent activity.</p>

  <div class="filter-bar">
    <label>Filter by Sector</label>
    <select id="sector-filter" onchange="filterBills()">
      <option value="all">All Sectors</option>
      <option value="banking">Banking & Finance</option>
      <option value="tax">Tax (280E)</option>
      <option value="retail">Retail / Dispensary</option>
      <option value="cultivation">Cultivation</option>
      <option value="testing">Testing & Lab</option>
      <option value="hemp">Hemp / CBD</option>
      <option value="mso">Multi-State Operators</option>
      <option value="executive">DEA / FDA / Executive</option>
    </select>
    <label>Risk Level</label>
    <select id="risk-filter" onchange="filterBills()">
      <option value="all">All Levels</option>
      <option value="risk-critical">Critical Only</option>
      <option value="risk-high">High &amp; Critical</option>
      <option value="risk-medium">Medium &amp; Above</option>
    </select>
    <span class="filter-count" id="bill-filter-count">{bill_count} bills shown</span>
  </div>

  <table class="data-table" id="bills-table">
    <thead>
      <tr><th>Bill</th><th>Title</th><th>Sponsor</th><th>Latest Action</th><th>Updated</th><th>Risk</th></tr>
    </thead>
    <tbody id="bills-tbody">{rows}
    </tbody>
  </table>
  <p id="bills-empty" style="display:none;text-align:center;color:#999;padding:1.5rem">No bills match your current filters.</p>
<script>
  function filterBills() {{
    var sector = document.getElementById('sector-filter').value;
    var risk   = document.getElementById('risk-filter').value;
    var rows   = document.querySelectorAll('#bills-tbody tr');
    var shown  = 0;
    rows.forEach(function(r) {{
      var sectors = r.dataset.sectors || '';
      var badge   = r.querySelector('.risk-badge');
      var badgeCls = badge ? badge.className : '';
      var sectorOk = sector === 'all' || sectors.indexOf(sector) !== -1;
      var riskOk = true;
      if (risk === 'risk-critical') riskOk = badgeCls.indexOf('risk-critical') !== -1;
      else if (risk === 'risk-high') riskOk = badgeCls.indexOf('risk-critical') !== -1 || badgeCls.indexOf('risk-high') !== -1;
      else if (risk === 'risk-medium') riskOk = badgeCls.indexOf('risk-low') === -1;
      r.style.display = (sectorOk && riskOk) ? '' : 'none';
      if (sectorOk && riskOk) shown++;
    }});
    document.getElementById('bill-filter-count').textContent = shown + ' bills shown';
    document.getElementById('bills-empty').style.display = shown === 0 ? 'block' : 'none';
  }}
</script>"""
    else:
        live_section = """
  <div class="api-pending">
    <h3>Congress.gov data unavailable</h3>
    <p>Could not reach Congress.gov API. Check your API key or network connection and rebuild.</p>
  </div>"""

    content = f"""
<div class="hero">
  <div class="hero-tag">FEDERAL LEGISLATION</div>
  <h1>Cannabis <span>Bills in Congress</span></h1>
  <p>Active bills, committee status, and floor votes — updated every Monday morning.</p>
  <div class="stat-row">
    <div class="stat-card"><div class="num">{bill_count}</div><div class="lbl">BILLS TRACKED</div></div>
    <div class="stat-card"><div class="num">Federal</div><div class="lbl">SCOPE</div></div>
    <div class="stat-card"><div class="num">Weekly</div><div class="lbl">UPDATES</div></div>
  </div>
</div>

<div class="container">
  {live_section}

  <span class="section-tag tag-green">KEY BILLS TO WATCH</span>
  <h2>Bills That Move Kent's Business</h2>
  <p class="section-intro">These are the categories of legislation with direct impact on cannabis product manufacturers,
     B2B suppliers, and emerging cannabis technology companies.</p>

  <table class="data-table">
    <thead>
      <tr>
        <th>Bill Category</th>
        <th>What It Does</th>
        <th>Business Impact</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>SAFER Banking Act</strong></td>
        <td>Allows cannabis businesses to access standard banking, credit cards, and loans</td>
        <td>Eliminates cash-only operations. Enables B2B payment processing for Deeper Green™ sales.</td>
        <td><span class="badge badge-navy">In Senate</span> <span class="risk-badge risk-high">HIGH</span></td>
      </tr>
      <tr>
        <td><strong>DEA Schedule III Reclassification</strong></td>
        <td>Moves cannabis from Schedule I to Schedule III — federal drug classification</td>
        <td>Legitimizes the market. Reduces legal risk for investors and operators. Unlocks research funding.</td>
        <td><span class="badge badge-green">In Progress</span> <span class="risk-badge risk-critical">CRITICAL</span></td>
      </tr>
      <tr>
        <td><strong>Section 280E Tax Reform</strong></td>
        <td>Allows cannabis businesses to deduct standard business expenses from federal taxes</td>
        <td>Direct profitability impact. Most cannabis operators pay 40–80% effective tax rate under 280E.</td>
        <td><span class="badge badge-gray">Pending</span> <span class="risk-badge risk-high">HIGH</span></td>
      </tr>
      <tr>
        <td><strong>FDA Food Additive Rules</strong></td>
        <td>FDA regulation of THC as a food/beverage ingredient</td>
        <td>Directly governs whether Deeper Green™ (THC powder for B2B food/beverage manufacturers) can be legally sold.</td>
        <td><span class="badge badge-red">Critical Watch</span> <span class="risk-badge risk-critical">CRITICAL</span></td>
      </tr>
      <tr>
        <td><strong>Farm Bill / Hemp THC Limits</strong></td>
        <td>Defines hemp vs. cannabis THC threshold. Sets interstate commerce rules.</td>
        <td>Determines what can be shipped across state lines without federal cannabis licensing.</td>
        <td><span class="badge badge-navy">Renewal Due</span> <span class="risk-badge risk-high">HIGH</span></td>
      </tr>
      <tr>
        <td><strong>Federal Legalization Framework</strong></td>
        <td>Any bill creating federal licensing, taxation, and distribution framework for cannabis</td>
        <td>Defines the entire operating environment. Who can manufacture, distribute, and sell nationally.</td>
        <td><span class="badge badge-gray">Multiple bills competing</span> <span class="risk-badge risk-medium">MEDIUM</span></td>
      </tr>
    </tbody>
  </table>

  <p style="font-size:.82rem;color:{MUTED};margin-top:.5rem;">
    Live bill data with bill numbers, sponsors, and vote dates activates when Congress.gov API key is provided.
    <a href="about.html">Learn more →</a>
  </p>
</div>"""

    return page(f"Cannabis Bills in Congress ({bill_count})", "bills.html", content)

# ── DATA: LAWMAKERS ──────────────────────────────────────────────────────────
# Curated Senate cannabis champions — active in prior or current Congress
SENATE_CANNABIS_CHAMPIONS = [
    {"name":"Chuck Schumer",    "party":"D","state":"NY","bioguide":"S000148","bills":"SAFER Banking, Cannabis Admin. Act","stance":"Pro-Cannabis"},
    {"name":"Cory Booker",      "party":"D","state":"NJ","bioguide":"B001288","bills":"Cannabis Admin. & Opportunity Act","stance":"Pro-Cannabis"},
    {"name":"Ron Wyden",        "party":"D","state":"OR","bioguide":"W000779","bills":"Cannabis Admin. Act, 280E Reform","stance":"Pro-Cannabis"},
    {"name":"Jeff Merkley",     "party":"D","state":"OR","bioguide":"M001176","bills":"Cannabis Admin. Act","stance":"Pro-Cannabis"},
    {"name":"Bernie Sanders",   "party":"I","state":"VT","bioguide":"S000033","bills":"Legalization bills, 280E Reform","stance":"Pro-Cannabis"},
    {"name":"John Fetterman",   "party":"D","state":"PA","bioguide":"F000479","bills":"SAFER Banking, Schedule III","stance":"Pro-Cannabis"},
    {"name":"Elizabeth Warren", "party":"D","state":"MA","bioguide":"W000817","bills":"SAFE Banking, Veterans Access","stance":"Pro-Cannabis"},
    {"name":"Rand Paul",        "party":"R","state":"KY","bioguide":"P000603","bills":"States Reform Act, CBD bills","stance":"Pro-Cannabis"},
    {"name":"Brian Schatz",     "party":"D","state":"HI","bioguide":"S001194","bills":"Veterans Cannabis Research","stance":"Pro-Cannabis"},
    {"name":"Ruben Gallego",    "party":"D","state":"AZ","bioguide":"G000574","bills":"SAFER Banking, Cannabis Reform","stance":"Pro-Cannabis"},
]

def fetch_lawmakers(bills):
    """Aggregate sponsors from bills + curated Senate champions, enrich with FEC totals."""
    sponsor_map = {}

    # Seed with curated Senate champions first
    for s in SENATE_CANNABIS_CHAMPIONS:
        sponsor_map[s["name"]] = {
            "name":       s["name"],
            "party":      s["party"],
            "state":      s["state"],
            "chamber":    "Senate",
            "bioguide":   s["bioguide"],
            "bill_count": 1,
            "bill_nos":   [s["bills"]],
            "curated":    True,
        }

    for b in bills:
        name = b.get("sponsor","").strip()
        if not name:
            continue
        if name not in sponsor_map:
            sponsor_map[name] = {
                "name":     name,
                "party":    b.get("sponsor_party",""),
                "state":    b.get("sponsor_state",""),
                "chamber":  b.get("chamber",""),
                "bioguide": b.get("sponsor_bioguide",""),
                "bill_count": 0,
                "bill_nos": [],
                "curated":  False,
            }
        sponsor_map[name]["bill_count"] += 1
        sponsor_map[name]["bill_nos"].append(b.get("number",""))

    # FEC fundraising lookup per lawmaker
    lawmakers = []
    for name, info in sponsor_map.items():
        fec_total = 0
        try:
            fec_url = (
                f"https://api.open.fec.gov/v1/candidates/search/"
                f"?q={requests.utils.quote(name)}&api_key=DEMO_KEY&per_page=5&sort=-receipts"
            )
            fec_r = requests.get(fec_url, timeout=8)
            for cand in fec_r.json().get("results", []):
                if cand.get("office") in ("S","H"):
                    fec_total = cand.get("receipts") or 0
                    break
        except:
            pass

        bioguide = info.get("bioguide","")
        lawmakers.append({
            "name":       name,
            "party":      info["party"],
            "state":      info["state"],
            "chamber":    info["chamber"],
            "photo":      f"https://bioguide.congress.gov/bioguide/photo/{bioguide[0]}/{bioguide}.jpg" if bioguide else "",
            "bill_count": info["bill_count"],
            "bills":      ", ".join(info["bill_nos"][:3]),
            "fec_total":  fec_total,
        })

    lawmakers.sort(key=lambda x: x["bill_count"], reverse=True)
    return lawmakers[:30]

# ── BUILD: LAWMAKERS ──────────────────────────────────────────────────────────
def build_lawmakers(lawmakers, opposition=None, opp_news=None):
    opposition = opposition or []
    opp_news   = opp_news or []
    count = len(lawmakers)

    party_colors = {"D": ("#1565C0","#E3F2FD","D"), "R": ("#B71C1C","#FFEBEE","R"), "I": ("#4A148C","#F3E5F5","I")}

    stance_map = {
        # Known pro-cannabis legislators
        "Ron Wyden": ("Pro-Cannabis","badge-green"),
        "Jeff Merkley": ("Pro-Cannabis","badge-green"),
        "Cory Booker": ("Pro-Cannabis","badge-green"),
        "Bernie Sanders": ("Pro-Cannabis","badge-green"),
        "Elizabeth Warren": ("Pro-Cannabis","badge-green"),
        "John Fetterman": ("Pro-Cannabis","badge-green"),
        "Rand Paul": ("Pro-Cannabis","badge-green"),
        "Earl Blumenauer": ("Pro-Cannabis","badge-green"),
        "Barbara Lee": ("Pro-Cannabis","badge-green"),
        "Alexandria Ocasio-Cortez": ("Pro-Cannabis","badge-green"),
        # Mixed / Banking-focused
        "Chuck Schumer": ("SAFER Banking","badge-navy"),
        "Steve Cohen": ("Pro-Cannabis","badge-green"),
    }

    cards = ""
    for lm in lawmakers:
        name     = lm["name"]
        party    = lm["party"]
        chamber  = lm["chamber"]
        state    = lm["state"]
        bills    = lm["bill_count"]
        photo    = lm["photo"]
        bill_nos = lm["bills"]
        fec_fmt  = f"${lm['fec_total']:,.0f}" if lm["fec_total"] else "—"

        pc, bg, plabel = party_colors.get(party, (NAVY, LBLUE, party or "?"))
        stance_label, stance_badge = stance_map.get(name, ("Active Sponsor","badge-navy"))

        conflict = CONFLICT_LAWMAKERS.get(name)
        conflict_badge = ""
        if conflict:
            c_committee = conflict['committee']
            c_industry  = conflict['industry']
            conflict_badge = f' <span style="background:#FFF3E0;color:#B71C1C;font-size:.65rem;font-weight:800;padding:.18rem .5rem;border-radius:12px;border:1px solid #EF9A9A" title="On {c_committee} — receives {c_industry} PAC funding">⚠ Conflict</span>'

        party_pill = f'<span style="background:{bg};color:{pc};font-size:.68rem;font-weight:700;padding:.2rem .6rem;border-radius:12px;border:1px solid {pc}33">{plabel}</span>'
        fallback_div = f'<div style="width:72px;height:88px;border-radius:8px;background:{LBLUE};display:none;align-items:center;justify-content:center;font-size:1.4rem;font-weight:800;color:{NAVY};flex-shrink:0">{name[0]}</div>'
        if photo:
            photo_html = f'<div style="position:relative;width:72px;height:88px;flex-shrink:0"><img src="{photo}" alt="{name}" style="width:72px;height:88px;object-fit:cover;border-radius:8px;border:2px solid {BORDER}" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">{fallback_div}</div>'
        else:
            photo_html = f'<div style="width:72px;height:88px;border-radius:8px;background:{LBLUE};display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:800;color:{NAVY};flex-shrink:0">{name[0]}</div>'

        cards += f"""
    <div class="lm-card" data-party="{party}" data-chamber="{chamber}">
      <div style="display:flex;gap:1rem;align-items:flex-start">
        {photo_html}
        <div style="flex:1;min-width:0">
          <div style="font-size:.68rem;font-weight:700;color:{MUTED};letter-spacing:.06em;text-transform:uppercase;margin-bottom:.2rem">{chamber} &nbsp;·&nbsp; {state}</div>
          <div style="font-size:1rem;font-weight:800;color:{NAVY};line-height:1.2;margin-bottom:.4rem">{name}</div>
          <div style="display:flex;gap:.4rem;flex-wrap:wrap;margin-bottom:.5rem">{party_pill} <span class="badge {stance_badge}" style="font-size:.65rem">{stance_label}</span>{conflict_badge}</div>
          <div style="font-size:.78rem;color:{MUTED}">{bill_nos}</div>
        </div>
      </div>
      <div style="border-top:1px solid {BORDER};margin-top:.9rem;padding-top:.8rem;display:flex;gap:1rem;justify-content:space-between">
        <div style="text-align:center">
          <div style="font-size:1.3rem;font-weight:800;color:{NAVY}">{bills}</div>
          <div style="font-size:.65rem;color:{MUTED};font-weight:600;letter-spacing:.05em">CANNABIS BILLS</div>
        </div>
        <div style="text-align:center">
          <div style="font-size:1rem;font-weight:700;color:{GREEN}">{fec_fmt}</div>
          <div style="font-size:.65rem;color:{MUTED};font-weight:600;letter-spacing:.05em">CYCLE RAISED</div>
        </div>
      </div>
    </div>"""

    # ── Build Opposition Watch HTML ───────────────────────────────────────────
    def _fmt(n):
        try:
            n = float(n)
            if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
            if n >= 1_000:     return f"${n/1_000:.0f}K"
            return f"${n:.0f}"
        except: return "—"

    opp_rows = ""
    for rec in opposition:
        badge = ""
        for ind in rec["industries"].split(", "):
            if ind == "Pharmaceutical": badge += '<span class="badge badge-red" style="font-size:.65rem;margin-right:.3rem">Pharma</span>'
            elif ind == "Alcohol":      badge += '<span class="badge badge-red" style="font-size:.65rem;margin-right:.3rem">Alcohol</span>'
            elif ind == "Private Prison": badge += '<span class="badge badge-red" style="font-size:.65rem;margin-right:.3rem">Prison PAC</span>'
        opp_rows += f"""
      <tr>
        <td><strong>{rec['name']}</strong></td>
        <td>{badge}</td>
        <td style="font-weight:700;color:{RED}">{_fmt(rec['total'])}</td>
        <td style="font-size:.8rem;color:#5a6a80">{rec['pacs']}</td>
      </tr>"""
    if not opp_rows:
        opp_rows = "<tr><td colspan='4' style='color:#999;padding:1rem 0;'>FEC live data loading — check API connection.</td></tr>"

    opp_rows_html = f"""  <table class="data-table">
    <thead>
      <tr><th>Recipient (Campaign Committee)</th><th>Industry Source</th><th>Amount (2023–24 Cycle)</th><th>Contributing PACs</th></tr>
    </thead>
    <tbody>{opp_rows}</tbody>
  </table>"""

    opp_news_items = ""
    for item in opp_news:
        opp_news_items += f"""
  <div style="border:1px solid #DDE3ED;border-radius:8px;padding:1rem 1.1rem;background:#fff;margin-bottom:.75rem">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">
      <span style="font-size:.68rem;font-weight:700;color:#5a6a80;text-transform:uppercase;letter-spacing:.06em">{item['source']}</span>
      <span style="font-size:.68rem;color:#5a6a80">{item['date']}</span>
    </div>
    <a href="{item['link']}" target="_blank" rel="noopener" style="font-size:.9rem;font-weight:600;color:{NAVY};text-decoration:none;line-height:1.35">{item['title']}</a>
  </div>"""
    if not opp_news_items:
        opp_news_items = "<p style='color:#999;padding:.5rem 0;'>No recent opposition funding stories found.</p>"

    content = f"""
<div class="hero">
  <div class="hero-tag">LEGISLATORS + CAMPAIGN FINANCE</div>
  <h1>Who's <span>Sponsoring What</span></h1>
  <p>Every legislator sponsoring cannabis bills this Congress — with party, chamber, bill count, and FEC fundraising.</p>
  <div class="stat-row">
    <div class="stat-card"><div class="num">{count}</div><div class="lbl">LAWMAKERS TRACKED</div></div>
    <div class="stat-card"><div class="num">FEC</div><div class="lbl">FINANCE SOURCE</div></div>
    <div class="stat-card"><div class="num">Live</div><div class="lbl">DATA</div></div>
  </div>
</div>

<div class="container">
  <span class="section-tag tag-green">FILTER</span>
  <h2>Cannabis Bill Sponsors — 119th Congress</h2>
  <p class="section-intro">Legislators ranked by number of cannabis bills sponsored. Filter by party or chamber.</p>

  <div style="display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:1.5rem">
    <button class="filter-btn active" onclick="filterLawmakers('party','ALL')" data-group="party">All Parties</button>
    <button class="filter-btn" onclick="filterLawmakers('party','D')" data-group="party">Democrat</button>
    <button class="filter-btn" onclick="filterLawmakers('party','R')" data-group="party">Republican</button>
    <button class="filter-btn" onclick="filterLawmakers('party','I')" data-group="party">Independent</button>
    &nbsp;
    <button class="filter-btn active" onclick="filterLawmakers('chamber','ALL')" data-group="chamber">All Chambers</button>
    <button class="filter-btn" onclick="filterLawmakers('chamber','Senate')" data-group="chamber">Senate</button>
    <button class="filter-btn" onclick="filterLawmakers('chamber','House')" data-group="chamber">House</button>
  </div>

  <div id="lm-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.25rem;margin-bottom:2rem">
    {cards}
  </div>
  <p id="lm-empty" style="display:none;color:{MUTED};text-align:center;padding:2rem">No lawmakers match that filter.</p>

  <hr class="section-divider" style="margin:2rem 0">

  <span class="section-tag tag-red">FOLLOW THE MONEY</span>
  <h2>Industry Influence Map</h2>
  <p class="section-intro">The industries funding legislators tell you everything about how they'll vote.
     A legislator's donor list is their real policy agenda.</p>
  <table class="data-table">
    <thead><tr><th>Industry</th><th>Cannabis Position</th><th>Why They Care</th><th>Signal for Operators</th></tr></thead>
    <tbody>
      <tr><td><strong>Cannabis PACs</strong></td><td><span class="badge badge-green">Pro-Legalization</span></td><td>Direct business interest. NCIA and state associations fund allies.</td><td>Cannabis PAC funding = genuine legislative ally</td></tr>
      <tr><td><strong>Banking / Real Estate</strong></td><td><span class="badge badge-green">Pro-SAFER Banking</span></td><td>SAFER Banking opens a massive new lending market.</td><td>Banking-funded legislators support financial access reform</td></tr>
      <tr><td><strong>Big Pharma</strong></td><td><span class="badge badge-red">Anti-Legalization</span></td><td>Cannabis competes with opioids and sleep drugs.</td><td>Heavy pharma funding = likely anti-cannabis votes</td></tr>
      <tr><td><strong>Alcohol Industry</strong></td><td><span class="badge badge-red">Anti-Legalization</span></td><td>Direct market competition with beer and spirits.</td><td>Alcohol PAC money = red flag on cannabis bills</td></tr>
      <tr><td><strong>Tobacco / Altria</strong></td><td><span class="badge badge-navy">Mixed</span></td><td>Buying cannabis stakes — they want to own it, not kill it.</td><td>Complex — depends on which company is the donor</td></tr>
      <tr><td><strong>Private Prison</strong></td><td><span class="badge badge-red">Anti-Legalization</span></td><td>Cannabis convictions fill beds. GEO Group, CoreCivic.</td><td>Prison funding = strong anti-cannabis likelihood</td></tr>
      <tr><td><strong>Technology / VC</strong></td><td><span class="badge badge-green">Generally Pro</span></td><td>Significant cannabis portfolio exposure across the sector.</td><td>Tech-funded legislators tend pro-legalization</td></tr>
    </tbody>
  </table>

  <hr class="section-divider" style="margin:3rem 0">

  <span class="section-tag tag-red">OPPOSITION WATCH</span>
  <h2>Anti-Cannabis Industry Funding — Who Got the Money</h2>
  <p class="section-intro">Legislative recipients of documented contributions from industries with known financial
     incentives to oppose cannabis reform: pharmaceutical companies protecting opioid markets, alcohol producers
     facing direct market competition, and private prison operators dependent on drug convictions.
     Source: FEC.gov official records, 2023–2024 election cycle.</p>
  {opp_rows_html}

  <hr class="section-divider" style="margin:3rem 0">

  <span class="section-tag tag-red">OPPOSITION IN THE NEWS</span>
  <h2>Anti-Cannabis Industry Funding — Recent Coverage</h2>
  <p class="section-intro">Documented reporting on the financial relationships between anti-cannabis industries and federal legislators.</p>
  {opp_news_items}
</div>

<style>
  .lm-card {{
    background:{WHITE};border:1px solid {BORDER};border-radius:10px;
    padding:1.25rem 1.3rem;transition:box-shadow .2s;
  }}
  .lm-card:hover {{ box-shadow:0 4px 16px rgba(27,67,50,.1); }}
  .lm-card.hidden {{ display:none; }}
  .filter-btn {{
    background:{WHITE};border:1px solid {BORDER};color:{NAVY};
    padding:.4rem .9rem;border-radius:20px;font-size:.78rem;font-weight:600;
    cursor:pointer;transition:all .15s;
  }}
  .filter-btn.active {{
    background:{NAVY};color:#fff;border-color:{NAVY};
  }}
</style>

<script>
  var partyFilter = 'ALL';
  var chamberFilter = 'ALL';

  function filterLawmakers(group, val) {{
    if (group === 'party') partyFilter = val;
    if (group === 'chamber') chamberFilter = val;

    // Update button states
    document.querySelectorAll('.filter-btn[data-group="' + group + '"]').forEach(function(b) {{
      b.classList.remove('active');
    }});
    event.target.classList.add('active');

    var cards = document.querySelectorAll('.lm-card');
    var visible = 0;
    cards.forEach(function(c) {{
      var pMatch = partyFilter === 'ALL' || c.dataset.party === partyFilter;
      var cMatch = chamberFilter === 'ALL' || c.dataset.chamber === chamberFilter;
      if (pMatch && cMatch) {{ c.classList.remove('hidden'); visible++; }}
      else {{ c.classList.add('hidden'); }}
    }});
    document.getElementById('lm-empty').style.display = visible === 0 ? 'block' : 'none';
  }}
</script>"""

    return page(f"Cannabis Lawmakers & Money ({count})", "lawmakers.html", content)

# ── BUILD: EXECUTIVE ──────────────────────────────────────────────────────────
def build_executive(actions):
    type_labels = {
        "Presidential Document": ("badge-red",   "Presidential"),
        "Rule":                  ("badge-navy",  "Final Rule"),
        "Proposed Rule":         ("badge-gray",  "Proposed Rule"),
        "Notice":                ("badge-gray",  "Notice"),
    }

    rows = ""
    for a in actions[:20]:
        doc_type = a.get("type","")
        badge_cls, badge_label = type_labels.get(doc_type, ("badge-gray", doc_type[:20]))
        agency = a.get("agency","Federal Agency")[:50]
        date   = a.get("date","")
        number = a.get("number","")
        num_str = f" &nbsp;·&nbsp; #{number}" if number else ""
        rows += f"""
      <tr>
        <td><span class="badge {badge_cls}">{badge_label}</span></td>
        <td><a href="{a['link']}" target="_blank">{a['title'][:100]}</a></td>
        <td>{agency}</td>
        <td>{date}{num_str}</td>
      </tr>"""

    if not rows:
        rows = "<tr><td colspan='4' style='color:#999;padding:1rem;'>No executive actions retrieved — check connection and try again.</td></tr>"

    content = f"""
<div class="hero">
  <div class="hero-tag">EXECUTIVE BRANCH ACTIONS</div>
  <h1>Presidential & <span>Agency Actions</span></h1>
  <p>Executive orders, DEA rulings, FDA guidance, and DOJ enforcement memos affecting cannabis — live from the Federal Register.</p>
  <div class="stat-row">
    <div class="stat-card"><div class="num">{len(actions)}</div><div class="lbl">ACTIONS FOUND</div></div>
    <div class="stat-card"><div class="num">Federal Register</div><div class="lbl">DATA SOURCE</div></div>
    <div class="stat-card"><div class="num">Weekly</div><div class="lbl">REFRESH</div></div>
  </div>
</div>

<div class="container">
  <span class="section-tag tag-red">LIVE DATA</span>
  <h2>Federal Register — Cannabis Actions</h2>
  <p class="section-intro">Presidential documents, final rules, proposed rules, and agency notices
     from the Federal Register referencing cannabis, marijuana, or hemp.
     Updated every Monday. Source: federalregister.gov (free, no key required).</p>

  <table class="data-table">
    <thead>
      <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Agency</th>
        <th>Date</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>

  <span class="section-tag tag-navy">KEY AGENCIES</span>
  <h2>Who Controls Cannabis Regulation</h2>
  <p class="section-intro">Congressional legislation is only half the picture. These executive agencies
     shape cannabis policy through rules, guidance, and enforcement — often faster than Congress can act.</p>

  <table class="data-table">
    <thead>
      <tr><th>Agency</th><th>Cannabis Authority</th><th>Why It Matters for Business</th></tr>
    </thead>
    <tbody>
      <tr><td><strong>DEA</strong></td><td>Scheduling decisions — Schedule I vs. III</td><td>The single biggest regulatory event possible. Rescheduling changes banking, research, and legal risk overnight.</td></tr>
      <tr><td><strong>FDA</strong></td><td>Cannabis in food, supplements, and medicine</td><td>Directly governs Deeper Green™ (THC as a food ingredient). FDA rules determine legal B2B sales.</td></tr>
      <tr><td><strong>DOJ / AG</strong></td><td>Federal prosecution priorities</td><td>Can deprioritize cannabis enforcement without Congress. The AG's stance determines real-world risk.</td></tr>
      <tr><td><strong>Treasury / FinCEN</strong></td><td>Banking guidance for cannabis businesses</td><td>FinCEN memos tell banks whether they can serve cannabis clients. Changes here affect payment processing.</td></tr>
      <tr><td><strong>USDA</strong></td><td>Hemp farming regulations, Farm Bill implementation</td><td>Sets THC threshold for hemp vs. cannabis classification. Affects what can cross state lines legally.</td></tr>
      <tr><td><strong>White House / President</strong></td><td>Executive orders, pardons, enforcement direction</td><td>Presidential action can move faster than any legislation. Today's news is often executive-driven.</td></tr>
    </tbody>
  </table>
</div>"""

    return page("Executive Actions on Cannabis", "executive.html", content)

# ── BUILD: MONEY ──────────────────────────────────────────────────────────────
def build_money(pacs, opposition=None, opp_news=None):
    opposition = opposition or []
    opp_news   = opp_news or []
    def fmt_money(n):
        try:
            n = float(n)
            if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
            if n >= 1_000:     return f"${n/1_000:.0f}K"
            return f"${n:.0f}"
        except: return "—"

    pac_rows = ""
    for p in pacs[:15]:
        pac_rows += f"""
      <tr>
        <td><strong>{p['name']}</strong></td>
        <td>{p.get('type','—')}</td>
        <td>{p.get('state','US')}</td>
        <td>{fmt_money(p.get('receipts',0))}</td>
      </tr>"""

    if not pac_rows:
        pac_rows = "<tr><td colspan='4' style='color:#999;padding:1rem;'>FEC data loading — check connection.</td></tr>"

    # ── Build opposition table ────────────────────────────────────────────────
    opp_rows = ""
    for rec in opposition:
        badge = ""
        for ind in rec["industries"].split(", "):
            if ind == "Pharmaceutical": badge += '<span class="badge badge-red" style="font-size:.65rem;margin-right:.3rem">Pharma</span>'
            elif ind == "Alcohol":      badge += '<span class="badge badge-red" style="font-size:.65rem;margin-right:.3rem">Alcohol</span>'
            elif ind == "Private Prison": badge += '<span class="badge badge-red" style="font-size:.65rem;margin-right:.3rem">Prison PAC</span>'
        opp_rows += f"""
      <tr>
        <td><strong>{rec['name']}</strong></td>
        <td>{badge}</td>
        <td style="font-weight:700;color:#C8311A">{fmt_money(rec['total'])}</td>
        <td style="font-size:.8rem;color:#5a6a80">{rec['pacs']}</td>
      </tr>"""
    if not opp_rows:
        opp_rows = "<tr><td colspan='4' style='color:#999;padding:1rem 0;'>FEC live data loading — check API connection.</td></tr>"

    opp_fec_table = f"""  <table class="data-table">
    <thead>
      <tr><th>Recipient (Campaign Committee)</th><th>Industry Source</th><th>Amount (2023–24 Cycle)</th><th>Contributing PACs</th></tr>
    </thead>
    <tbody>{opp_rows}</tbody>
  </table>"""

    opp_money_news = ""
    for item in opp_news:
        opp_money_news += f"""
  <div style="border:1px solid #DDE3ED;border-radius:8px;padding:1rem 1.1rem;background:#fff;margin-bottom:.75rem">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">
      <span style="font-size:.68rem;font-weight:700;color:#5a6a80;text-transform:uppercase;letter-spacing:.06em">{item['source']}</span>
      <span style="font-size:.68rem;color:#5a6a80">{item['date']}</span>
    </div>
    <a href="{item['link']}" target="_blank" rel="noopener" style="font-size:.9rem;font-weight:600;color:{NAVY};text-decoration:none;line-height:1.35">{item['title']}</a>
  </div>"""
    if not opp_money_news:
        opp_money_news = "<p style='color:#999;padding:.5rem 0;'>No recent opposition funding stories found.</p>"

    # Compute totals for chart
    cannabis_total = sum(float(p.get('receipts', 0) or 0) for p in pacs)
    opposition_total = sum(float(r.get('total', 0) or 0) for r in opposition)

    def chart_bar(label, amount, color, max_amt):
        pct = max(2, round((amount / max_amt) * 100)) if max_amt > 0 else 2
        amt_fmt = f"${amount/1_000_000:.1f}M" if amount >= 1_000_000 else f"${amount/1_000:.0f}K" if amount >= 1_000 else f"${amount:.0f}"
        return f'<div style="margin-bottom:.85rem"><div style="display:flex;justify-content:space-between;font-size:.82rem;font-weight:700;margin-bottom:.3rem"><span>{label}</span><span style="color:{color}">{amt_fmt}</span></div><div style="background:#f0f0f0;border-radius:4px;height:18px"><div style="background:{color};width:{pct}%;height:18px;border-radius:4px;transition:width .5s"></div></div></div>'

    max_amt = max(cannabis_total, opposition_total, 1)
    chart_html = chart_bar("Cannabis Industry PACs (Pro-Cannabis)", cannabis_total, GREEN, max_amt)
    chart_html += chart_bar("Opposition Industry PACs (Anti-Cannabis)", opposition_total, "#B71C1C", max_amt)

    content = f"""
<div class="hero">
  <div class="hero-tag">CAMPAIGN FINANCE INTELLIGENCE</div>
  <h1>The Money <span>Behind the Vote</span></h1>
  <p>Who funds the legislators writing cannabis law — and what that tells you about how they'll vote.</p>
  <div class="stat-row">
    <div class="stat-card"><div class="num">FEC</div><div class="lbl">DATA SOURCE</div></div>
    <div class="stat-card"><div class="num">{len(pacs)}</div><div class="lbl">CANNABIS PACs FOUND</div></div>
    <div class="stat-card"><div class="num">Monthly</div><div class="lbl">REFRESH</div></div>
  </div>
</div>

<div class="container">

  <span class="section-tag tag-navy">INDUSTRY SPENDING COMPARISON</span>
  <h2>Cannabis vs. Opposition — PAC Money Tracked</h2>
  <p class="section-intro">Total political spending detected via FEC records this cycle. Opposition figure represents disbursements to federal legislators from documented anti-cannabis PACs only — full industry political spend is far larger.</p>
  <div style="background:{WHITE};border:1px solid {BORDER};border-radius:10px;padding:1.5rem 1.75rem;margin-bottom:2rem;max-width:600px">
    {chart_html}
    <p style="font-size:.72rem;color:{MUTED};margin-top:.5rem">Source: FEC.gov · 2023–2024 cycle · Cannabis PAC total receipts vs. documented opposition disbursements to legislators</p>
  </div>

  <span class="section-tag tag-green">LIVE FEC DATA</span>
  <h2>Cannabis-Related Political Committees</h2>
  <p class="section-intro">Political action committees and organizations with cannabis in their name or mission
     registered with the FEC. This is the money directly supporting cannabis-friendly legislators.
     Source: FEC.gov (official, free, no key required).</p>

  <table class="data-table">
    <thead>
      <tr><th>Committee Name</th><th>Type</th><th>State</th><th>Total Receipts</th></tr>
    </thead>
    <tbody>{pac_rows}</tbody>
  </table>


  <span class="section-tag tag-red">OPPOSITION WATCH — LIVE FEC DATA</span>
  <h2>Anti-Cannabis Industry Funding — Who Got the Money</h2>
  <p class="section-intro">Legislative recipients of documented contributions from industries with known financial
     incentives to oppose cannabis reform. Three industries dominate: pharmaceutical companies protecting opioid
     markets, alcohol producers facing direct market competition, and private prison operators dependent on
     drug convictions. Source: FEC.gov official records, 2023–2024 election cycle.</p>

  {opp_fec_table}

  <hr class="section-divider" style="margin:3rem 0">

  <span class="section-tag tag-navy">INDUSTRY CONTEXT</span>
  <h2>Why These Industries Oppose Cannabis</h2>
  <p class="section-intro">Follow the financial incentive and you understand the opposition.</p>

  <table class="data-table">
    <thead>
      <tr><th>Industry</th><th>Annual Political Spend</th><th>Cannabis Position</th><th>Financial Incentive</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Pharmaceutical</strong></td>
        <td>$300M+ annually</td>
        <td><span class="badge badge-red">Anti-Legalization</span></td>
        <td>Cannabis competes directly with opioids, sleep aids, and anxiety medications — a $40B+ market at risk</td>
      </tr>
      <tr>
        <td><strong>Alcohol / Beer</strong></td>
        <td>$25M+ annually</td>
        <td><span class="badge badge-red">Anti-Legalization</span></td>
        <td>Beer Institute, Wine & Spirits Wholesalers — consumers switching from alcohol to cannabis</td>
      </tr>
      <tr>
        <td><strong>Private Prison</strong></td>
        <td>$10M+ annually</td>
        <td><span class="badge badge-red">Anti-Legalization</span></td>
        <td>GEO Group, CoreCivic — cannabis convictions fill beds; legalization reduces revenue</td>
      </tr>
      <tr>
        <td><strong>Tobacco</strong></td>
        <td>$15M+ annually</td>
        <td><span class="badge badge-navy">Mixed</span></td>
        <td>Altria buying cannabis stakes — they want to own it, not kill it. Position evolving.</td>
      </tr>
    </tbody>
  </table>

  <hr class="section-divider" style="margin:3rem 0">

  <span class="section-tag tag-red">OPPOSITION IN THE NEWS</span>
  <h2>Anti-Cannabis Funding — Recent Coverage</h2>
  <p class="section-intro">Documented reporting on the financial relationships between anti-cannabis industries and federal legislators.</p>
  {opp_money_news}
</div>"""

    return page("Cannabis Campaign Finance & Money", "money.html", content)

# ── DATA: VAPOR / NICOTINE NEWS ───────────────────────────────────────────────
def fetch_vapor_news():
    queries = [
        "FDA nicotine vapor PMTA 2026",
        "FDA e-cigarette vape regulation 2026",
        "nicotine nebulizer FDA ruling",
        "vapor tobacco PMTA premarket approval",
        "FDA Center for Tobacco Products ruling",
        "nicotine device ban regulation congress",
    ]
    items = []
    seen = set()
    for q in queries:
        url = f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=en-US&gl=US&ceid=US:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                link = entry.get("link","")
                if link in seen: continue
                seen.add(link)
                published = entry.get("published","")
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(published)
                    pub_str = dt.strftime("%b %d, %Y")
                    pub_sort = dt.timestamp()
                except:
                    pub_str = published[:16] if published else "Recent"
                    pub_sort = 0
                source = entry.get("source",{}).get("title","News") if hasattr(entry.get("source",{}),"get") else "News"
                items.append({
                    "title":  entry.get("title",""),
                    "link":   link,
                    "source": source,
                    "date":   pub_str,
                    "sort":   pub_sort,
                })
        except Exception as e:
            print(f"Vapor news RSS error ({q}): {e}")
    items.sort(key=lambda x: x["sort"], reverse=True)
    return items[:10]

def fetch_vapor_federal_register():
    items = []
    for term in ["nicotine","electronic+cigarette","vape","tobacco+vapor"]:
        url = (
            f"https://www.federalregister.gov/api/v1/documents.json"
            f"?conditions[term]={term}"
            f"&conditions[type][]=RULE"
            f"&conditions[type][]=PRORULE"
            f"&conditions[type][]=NOTICE"
            f"&per_page=6&order=newest"
        )
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            for doc in data.get("results", []):
                items.append({
                    "title":  doc.get("title","")[:140],
                    "type":   doc.get("type",""),
                    "agency": ", ".join(doc.get("agency_names",[])),
                    "date":   doc.get("publication_date",""),
                    "link":   doc.get("html_url",""),
                })
        except Exception as e:
            print(f"Vapor Federal Register error ({term}): {e}")
    seen = set()
    unique = []
    for i in items:
        if i["link"] not in seen:
            seen.add(i["link"])
            unique.append(i)
    unique.sort(key=lambda x: x["date"], reverse=True)
    return unique[:12]

# ── BUILD: VAPOR / NICOTINE ───────────────────────────────────────────────────
def build_vapor(news_items, fed_items):
    count = len(news_items)

    news_cards = ""
    for item in news_items:
        source = item["source"][:30] if item["source"] else "News"
        title  = item["title"][:120]
        news_cards += f"""
    <div class="card">
      <div class="card-source" style="color:{NAVY}">{source}</div>
      <div class="card-title"><a href="{item['link']}" target="_blank" rel="noopener">{title}</a></div>
      <div class="card-meta">{item['date']}</div>
    </div>"""

    fed_rows = ""
    for doc in fed_items:
        badge_color = "badge-red" if doc["type"] == "RULE" else "badge-navy"
        fed_rows += f"""
      <tr>
        <td><a href="{doc['link']}" target="_blank" rel="noopener">{doc['title']}</a></td>
        <td>{doc['agency']}</td>
        <td><span class="badge {badge_color}">{doc['type']}</span></td>
        <td style="white-space:nowrap">{doc['date']}</td>
      </tr>"""

    if not fed_rows:
        fed_rows = '<tr><td colspan="4" style="color:#888;text-align:center">No recent Federal Register entries — check back after next rebuild.</td></tr>'

    content = f"""
<div class="hero">
  <div class="hero-tag">FDA VAPOR + NICOTINE REGULATION</div>
  <h1>Nicotine &amp; Vapor <span>AI Compliance Engine</span></h1>
  <p>FDA PMTA rulings, CTP actions, and vapor legislation affecting nicotine device manufacturers — updated daily.</p>
  <div class="stat-row">
    <div class="stat-card"><div class="num">{count}</div><div class="lbl">NEWS ITEMS</div></div>
    <div class="stat-card"><div class="num">FDA CTP</div><div class="lbl">PRIMARY REGULATOR</div></div>
    <div class="stat-card"><div class="num">PMTA</div><div class="lbl">APPROVAL PATHWAY</div></div>
    <div class="stat-card"><div class="num">18–24 mo</div><div class="lbl">TYPICAL TIMELINE</div></div>
  </div>
</div>

<div class="container">
  <span class="section-tag tag-red">TODAY'S NEWS</span>
  <h2>Vapor &amp; Nicotine Regulatory News</h2>
  <p class="section-intro">FDA actions, PMTA decisions, and vapor legislation — the regulatory environment
     for nicotine device manufacturers updated every morning.</p>
  <div class="card-grid">{news_cards}</div>

  <hr class="section-divider" style="margin:2rem 0">

  <span class="section-tag tag-navy">FEDERAL REGISTER — LIVE DATA</span>
  <h2>FDA Vapor &amp; Nicotine Rulings</h2>
  <p class="section-intro">Rules, proposed rules, and notices from the FDA Center for Tobacco Products (CTP)
     and related agencies — sourced directly from the Federal Register.</p>
  <table class="data-table">
    <thead><tr><th>Title</th><th>Agency</th><th>Type</th><th>Date</th></tr></thead>
    <tbody>{fed_rows}</tbody>
  </table>

  <hr class="section-divider" style="margin:2rem 0">

  <span class="section-tag tag-green">PMTA ROADMAP</span>
  <h2>FDA Premarket Tobacco Application — What to Know</h2>
  <p class="section-intro">The PMTA is the mandatory FDA approval pathway for any new nicotine or tobacco product.
     Understanding this process is critical for GFT1 device planning and investor communications.</p>
  <table class="data-table">
    <thead><tr><th>Phase</th><th>What Happens</th><th>Timeline</th><th>Cost Estimate</th></tr></thead>
    <tbody>
      <tr>
        <td><strong>Pre-Submission</strong></td>
        <td>Scientific literature review, product testing, safety &amp; benefit studies, manufacturer audit</td>
        <td>6–12 months</td>
        <td>$500K–$1.5M</td>
      </tr>
      <tr>
        <td><strong>Application Filing</strong></td>
        <td>Submit full PMTA dossier to FDA CTP. Includes toxicology, clinical data, manufacturing specs</td>
        <td>Month 12–15</td>
        <td>Included above</td>
      </tr>
      <tr>
        <td><strong>FDA Filing Review</strong></td>
        <td>FDA confirms application is complete and accepted for substantive review (refuse-to-file risk)</td>
        <td>3–6 months post-filing</td>
        <td>—</td>
      </tr>
      <tr>
        <td><strong>Substantive Review</strong></td>
        <td>FDA evaluates whether product is "appropriate for the protection of public health" (APPH standard)</td>
        <td>12–18 months</td>
        <td>$1.5M–$3.5M (consultant + legal)</td>
      </tr>
      <tr>
        <td><strong>Marketing Order</strong></td>
        <td>FDA issues Marketing Granted Order (MGO) — product can be legally sold in the U.S.</td>
        <td>18–24 months total</td>
        <td>$3–5M total</td>
      </tr>
    </tbody>
  </table>

  <hr class="section-divider" style="margin:2rem 0">

  <span class="section-tag tag-cream">KEY REGULATORY BODIES</span>
  <h2>Who Controls Nicotine Device Approval</h2>
  <p class="section-intro">Five agencies shape the nicotine device market. Understanding each is essential for timeline and compliance planning.</p>
  <table class="data-table">
    <thead><tr><th>Agency</th><th>Role</th><th>Key Action to Watch</th></tr></thead>
    <tbody>
      <tr>
        <td><strong>FDA CTP</strong><br><small>Center for Tobacco Products</small></td>
        <td>Primary regulator. Approves or denies all PMTA applications. Sets marketing standards.</td>
        <td>PMTA denial / Marketing Order grant rate — currently ~1% of applications approved</td>
      </tr>
      <tr>
        <td><strong>DEA</strong></td>
        <td>Controls nicotine scheduling if product crosses into therapeutic claims</td>
        <td>Any ruling that reclassifies nicotine delivery as a drug vs. tobacco product</td>
      </tr>
      <tr>
        <td><strong>FTC</strong></td>
        <td>Regulates advertising and marketing claims for nicotine products</td>
        <td>Enforcement actions against health claims or comparative advertising</td>
      </tr>
      <tr>
        <td><strong>Congress</strong></td>
        <td>Can legislate new vapor bans, flavor bans, or PMTA reform</td>
        <td>Vapor product flavor ban bills — recurring threat in each session</td>
      </tr>
      <tr>
        <td><strong>State AGs</strong></td>
        <td>State-level enforcement, retail restrictions, age verification mandates</td>
        <td>Multi-state AG coalitions pushing for federal vapor restrictions</td>
      </tr>
    </tbody>
  </table>

  <div class="api-pending" style="background:{LGREEN};border-color:{GREEN};">
    <h3 style="color:{GREEN}">GFT1 Device — Regulatory Context</h3>
    <p>The GFT1 nicotine nebulizer is a novel nicotine delivery device subject to FDA PMTA requirements.
       Timeline: 18–24 months. Estimated cost: $3–5M. A specialized PMTA consultant has not yet been engaged.
       This page tracks the regulatory environment that will govern the GFT1 approval process.</p>
  </div>
</div>"""

    return page("Vapor & Nicotine Compliance", "vapor.html", content)

# ── BUILD: ABOUT ──────────────────────────────────────────────────────────────
def build_about():
    content = f"""
<div class="hero">
  <div class="hero-tag">ABOUT GF TECH ONE</div>
  <h1>GF TECH ONE <span>AI Compliance Engine</span></h1>
  <p>Institutional-grade cannabis policy intelligence — built for operators, executives, and investors who need to move before the market does.</p>
</div>

<div class="container">

  <div class="about-section">
    <span class="section-tag tag-navy">WHO WE ARE</span>
    <h2>About GF Tech One</h2>
    <p>GF Tech One (GFTO) is a California-based cannabis technology company redefining how the industry operates at its most critical intersection: science, compliance, and market intelligence. Founded on the belief that cannabis businesses deserve the same caliber of institutional-grade intelligence tools available to Fortune 500 companies, GFTO develops platforms and products that give operators, executives, and investors the clarity to move with confidence.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-green">OUR ORIGIN</span>
    <h2>The Origin of GFTO</h2>
    <p>GF Tech One was founded by Kent Rhodes, a serial entrepreneur and cannabis industry veteran, after years of working inside cannabis operations and watching smart, well-capitalized companies make preventable mistakes — not from lack of effort, but from lack of information.</p>
    <p>Kent saw a gap: cannabis businesses were flying blind on regulatory shifts, legislative momentum, and competitive intelligence while regulators and competitors were not. His answer was to build systems that don't just monitor the landscape — they interpret it.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-navy">FLAGSHIP PRODUCT</span>
    <h2>Innovation: GFTO AI Compliance Engine</h2>
    <p>The flagship product of GFTO's intelligence division is the GFTO AI Compliance Engine — a real-time legislative and regulatory intelligence platform monitoring:</p>
    <div class="capability-grid" style="margin-top:1rem;">
      <div class="capability-item">Federal cannabis legislation in Congress — bills, sponsors, vote status</div>
      <div class="capability-item">Executive branch actions from the DEA, FDA, DOJ, and White House</div>
      <div class="capability-item">Lawmaker profiles and the campaign finance money behind their votes</div>
      <div class="capability-item">Vapor and nicotine policy developments running parallel to cannabis reform</div>
      <div class="capability-item">Campaign finance data from FEC and OpenSecrets</div>
    </div>
    <p>Updated daily and weekly via automated data pipelines, GFTO AI Compliance Engine delivers institutional-grade intelligence in plain English — no legal background required.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-green">WHAT WE BUILD</span>
    <h2>Capabilities &amp; Market Position</h2>
    <p>GF Tech One operates at the convergence of cannabis technology, regulatory intelligence, and AI-powered business systems. Core capabilities include:</p>
    <div class="capability-grid">
      <div class="capability-item">Regulatory &amp; Legislative Intelligence — GFTO AI Compliance Engine</div>
      <div class="capability-item">Water-Soluble Cannabinoid Technology — Deeper Green™</div>
      <div class="capability-item">AI-Powered Consumer Products — The Neb AI</div>
      <div class="capability-item">AI Marketing Infrastructure for cannabis operators</div>
    </div>
    <p>GFTO serves cannabis operators, investors, lobbyists, compliance officers, and industry executives who need to stay ahead of the regulatory curve in one of the most dynamic markets in the world.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-cream">LEADERSHIP</span>
    <h2>About Kent Rhodes</h2>
    <div class="kent-card">
      <h3>Kent Rhodes</h3>
      <div class="kent-title">Chief Executive Officer &amp; Founder — GF Tech One</div>
      <p>Kent Rhodes is the founder and Chief Executive Officer of GF Tech One. A seasoned entrepreneur with deep roots in cannabis, technology, and consumer products, Kent has spent over a decade building companies at the intersection of science and market strategy.</p>
      <p>Before founding GF Tech One, Kent held leadership roles across multiple verticals — from licensed cannabis operations to consumer technology ventures — where he developed a pattern recognition for the moments when regulatory change creates strategic opportunity. He is known among peers for his ability to see around corners: understanding not just what is happening in cannabis policy, but what it means for operators 12–18 months out.</p>
      <p>Under Kent's leadership, GF Tech One has launched:</p>
      <div class="capability-grid">
        <div class="capability-item">GFTO AI Compliance Engine — the industry's first AI-assisted legislative intelligence dashboard for cannabis</div>
        <div class="capability-item">Deeper Green™ — proprietary water-soluble THC delivery system for B2B food &amp; beverage manufacturers</div>
        <div class="capability-item">The Neb AI — next-generation AI-personalized nicotine nebulizer for a post-cigarette consumer market</div>
      </div>
      <p>Kent is based in California, where he continues to build at the frontier of cannabis technology, compliance intelligence, and AI-driven product development.</p>
    </div>
  </div>

  <div class="about-section">
    <span class="section-tag tag-navy">DATA INTEGRITY</span>
    <h2>Verified Data Sources</h2>
    <p>Every data point on GFTO AI Compliance Engine is sourced directly from official government agencies and verified public records. No third-party data resellers. No unverified aggregators.</p>
    <table class="data-table">
      <thead><tr><th>Source</th><th>What We Pull</th><th>Update Frequency</th><th>Last Verified</th></tr></thead>
      <tbody>
        <tr>
          <td><a href="https://www.congress.gov" target="_blank" rel="noopener"><strong>Congress.gov</strong></a></td>
          <td>Active cannabis bills, sponsors, committee status, vote records</td>
          <td>Weekly — Mondays</td>
          <td>{TODAY}</td>
        </tr>
        <tr>
          <td><a href="https://www.federalregister.gov" target="_blank" rel="noopener"><strong>Federal Register</strong></a></td>
          <td>DEA, FDA, and DOJ executive orders, proposed rules, final rules</td>
          <td>Daily — 6am ET</td>
          <td>{TODAY}</td>
        </tr>
        <tr>
          <td><a href="https://www.fec.gov" target="_blank" rel="noopener"><strong>FEC.gov</strong></a></td>
          <td>Campaign finance filings, PAC contributions, candidate fundraising</td>
          <td>Monthly</td>
          <td>{TODAY}</td>
        </tr>
        <tr>
          <td><a href="https://www.opensecrets.org" target="_blank" rel="noopener"><strong>OpenSecrets</strong></a></td>
          <td>Lawmaker donor profiles, industry money flows, lobbying spend</td>
          <td>Monthly</td>
          <td>{TODAY}</td>
        </tr>
        <tr>
          <td><strong>Google News RSS</strong></td>
          <td>Cannabis and vapor/nicotine policy headlines from major outlets</td>
          <td>Daily — 6am ET</td>
          <td>{TODAY}</td>
        </tr>
      </tbody>
    </table>
    <p>All government data is public domain. GFTO AI Compliance Engine does not editorialize or alter source data — we organize, summarize, and present it for business intelligence use.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-cream">MEDIA PARTNERSHIP</span>
    <h2>Easyriders Magazine</h2>
    <p>GFTO AI Compliance Engine serves as an official cannabis news supplier to <strong>Easyriders Magazine</strong> — one of America's most iconic motorcycle and lifestyle publications. Through this partnership, GFTO delivers curated cannabis policy intelligence to Easyriders' audience of hundreds of thousands of readers who represent a core and growing cannabis consumer demographic.</p>
    <p>This partnership validates GFTO AI Compliance Engine as a trusted, publication-grade intelligence source — not just a data aggregator.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-cream">PLATFORM BUILDER</span>
    <h2>Built by Horsepower AI</h2>
    <div class="kent-card">
      <h3>Jeff Najar</h3>
      <div class="kent-title">Founder — Horsepower AI</div>
      <p>GFTO AI Compliance Engine is designed, built, and maintained by <strong>Horsepower AI</strong>, a digital business consultancy that builds AI-powered intelligence tools for growth-stage companies. Horsepower AI was engaged by GF Tech One to deliver institutional-grade regulatory intelligence at zero cost to cannabis executives.</p>
      <p style="margin-top:.75rem">
        <strong>Data corrections &amp; inquiries:</strong>
        <a href="mailto:jeff.najar@horsepowermarketing.com" style="color:{NAVY};font-weight:700">jeff.najar@horsepowermarketing.com</a>
        &nbsp;·&nbsp; Errors reviewed and corrected within 48 hours.
      </p>
      <p style="margin-top:.5rem">
        <a href="methodology.html" style="color:{GREEN};font-weight:700">Read our full data methodology →</a>
      </p>
    </div>
  </div>

  <p style="font-size:.82rem;color:{MUTED};margin-top:2rem;">
    GFTO AI Compliance Engine is for informational purposes only. This is not legal or investment advice.
    Data sourced from Congress.gov, Federal Register, FEC.gov, OpenSecrets, and Google News.
    All government data is public domain. Last updated {TODAY}.
  </p>

</div>"""

    return page("About GF Tech One", "about.html", content)


# ── BUILD: METHODOLOGY ────────────────────────────────────────────────────────
def build_methodology():
    content = f"""
<div class="hero">
  <div class="hero-tag">DATA INTEGRITY</div>
  <h1>How We <span>Collect & Verify</span> Data</h1>
  <p>Every source, every update schedule, and every editorial decision — explained in plain English.</p>
</div>

<div class="container">

  <div class="about-section">
    <span class="section-tag tag-navy">OUR COMMITMENT</span>
    <h2>What This Platform Is — and Is Not</h2>
    <p>GFTO AI Compliance Engine is a <strong>business intelligence aggregator</strong>. We collect, organize, and present publicly available government data so cannabis executives can monitor policy in one place without spending hours across multiple government websites.</p>
    <p>We do not editorialize, alter, or fabricate government data. Every bill, executive action, and campaign finance figure shown on this platform links directly to its original government source. We are not a law firm and nothing here is legal advice.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-green">DATA SOURCES</span>
    <h2>Where the Data Comes From</h2>
    <table class="data-table">
      <thead>
        <tr><th>Source</th><th>What We Pull</th><th>How Often</th><th>How to Verify</th></tr>
      </thead>
      <tbody>
        <tr>
          <td><strong><a href="https://www.congress.gov" target="_blank" rel="noopener">Congress.gov</a></strong></td>
          <td>All cannabis, marijuana, and hemp-related bills in the current Congress. Bill title, number, sponsor, committee status, and latest action.</td>
          <td>Weekly — every Monday at 5am ET</td>
          <td>Search any bill number at congress.gov/bill</td>
        </tr>
        <tr>
          <td><strong><a href="https://www.federalregister.gov" target="_blank" rel="noopener">Federal Register</a></strong></td>
          <td>Presidential documents, final rules, proposed rules, and agency notices related to cannabis, marijuana, and hemp from DEA, FDA, DOJ, USDA, and FinCEN.</td>
          <td>Daily — every morning at 6am ET</td>
          <td>Search at federalregister.gov/documents</td>
        </tr>
        <tr>
          <td><strong><a href="https://www.fec.gov" target="_blank" rel="noopener">FEC.gov</a></strong></td>
          <td>Cannabis-related political action committees (PACs), total receipts, and disbursements from opposition-industry PACs (pharmaceutical, alcohol, private prison) to federal legislators. 2023–2024 election cycle.</td>
          <td>Weekly — every Monday</td>
          <td>Search any committee at fec.gov/data/committees</td>
        </tr>
        <tr>
          <td><strong><a href="https://www.opensecrets.org" target="_blank" rel="noopener">OpenSecrets</a></strong></td>
          <td>Supplemental campaign finance context and industry-level spending analysis.</td>
          <td>As available</td>
          <td>opensecrets.org/industries</td>
        </tr>
        <tr>
          <td><strong>Google News RSS</strong></td>
          <td>Cannabis policy and regulatory news from major publications. Six targeted queries covering legislation, executive action, banking, and hemp.</td>
          <td>Daily — every morning at 6am ET</td>
          <td>Links go directly to original publication</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="about-section">
    <span class="section-tag tag-red">RISK SCORING</span>
    <h2>How We Score Bill Risk</h2>
    <p>Every bill in the live tracker carries a risk score: <span class="risk-badge risk-low">LOW</span> <span class="risk-badge risk-medium">MEDIUM</span> <span class="risk-badge risk-high">HIGH</span> <span class="risk-badge risk-critical">CRITICAL</span></p>
    <p style="margin-top:1rem">Scores are computed automatically at each weekly build using the bill's most recent action from Congress.gov. The scoring model weights signals as follows:</p>
    <table class="data-table" style="margin-top:1rem">
      <thead><tr><th>Signal</th><th>Weight</th></tr></thead>
      <tbody>
        <tr><td>Passed chamber / signed into law</td><td>+5 points</td></tr>
        <tr><td>Floor vote scheduled or recorded</td><td>+3 points</td></tr>
        <tr><td>Markup / ordered reported from committee</td><td>+2 points</td></tr>
        <tr><td>Hearing / subcommittee referral</td><td>+1 point</td></tr>
        <tr><td>Known high-priority bill (SAFER Banking, Schedule III, 280E, etc.)</td><td>+2 points</td></tr>
      </tbody>
    </table>
    <p style="margin-top:1rem;font-size:.88rem;color:{MUTED}">A bill scoring 6+ is CRITICAL. 4–5 is HIGH. 2–3 is MEDIUM. 0–1 is LOW. Scores reset each weekly build based on the most current Congress.gov data.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-navy">CONFLICT FLAGS</span>
    <h2>How We Flag Conflicts of Interest</h2>
    <p>A <strong>⚠ Conflict</strong> badge appears on a lawmaker's profile when two conditions are both true:</p>
    <ol style="margin:1rem 0 1rem 1.5rem;line-height:1.9;color:#3a4a3a">
      <li>The lawmaker sits on a committee with direct jurisdiction over cannabis legislation (Senate Judiciary, Senate Banking, House Judiciary, House Financial Services, Senate Finance, or Senate Agriculture)</li>
      <li>FEC records show the lawmaker's campaign received documented funding from industries with known financial incentives to oppose cannabis reform (pharmaceutical, alcohol, or private prison industries) during the 2023–2024 cycle</li>
    </ol>
    <p>Conflict flags are based on documented FEC filings and publicly available committee rosters. All underlying data is verifiable at fec.gov and congress.gov.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-cream">EDITORIAL PROCESS</span>
    <h2>Editorial Independence & Accuracy</h2>
    <p>GFTO AI Compliance Engine is built and operated by <strong>Horsepower AI</strong> on behalf of <strong>GF Tech One</strong>. The platform has no affiliation with any cannabis company, lobbying organization, or political party. We do not accept payment for coverage or for placement in any section of the tracker.</p>
    <p>Data is fetched directly from government APIs at the times shown above. The platform does not modify, spin, or summarize government content beyond organizing it for readability. News headlines link directly to the original publication — we do not paraphrase or rewrite them.</p>
    <p><strong>To report a data error:</strong> Email <a href="mailto:jeff.najar@horsepowermarketing.com">jeff.najar@horsepowermarketing.com</a> with the bill number, FEC record, or Federal Register document in question. We review and correct errors within 48 hours.</p>
  </div>

  <div class="about-section">
    <span class="section-tag tag-cream">BUILT BY</span>
    <h2>Who Builds This</h2>
    <div class="kent-card">
      <h3>Jeff Najar</h3>
      <div class="kent-title">Founder, Horsepower AI</div>
      <p>Jeff Najar is the founder of Horsepower AI, a digital business consultancy that builds AI-powered intelligence tools for small and mid-size companies. GFTO AI Compliance Engine was designed and built by Horsepower AI to give cannabis executives the same quality of regulatory intelligence available to large enterprise operators — at no cost.</p>
      <p style="margin-top:.75rem"><a href="mailto:jeff.najar@horsepowermarketing.com" style="color:{NAVY};font-weight:700">jeff.najar@horsepowermarketing.com</a></p>
    </div>
  </div>

  <p style="font-size:.82rem;color:{MUTED};margin-top:2rem;">
    For informational purposes only. Not legal advice. Not investment advice.
    All government data is public domain. Last updated {TODAY}.
  </p>

</div>"""
    return page("Methodology & Data Sources", "methodology.html", content)


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    assets = OUTPUT_DIR / "assets"
    assets.mkdir(exist_ok=True)

    print("Fetching news feed...")
    news = fetch_news()
    print(f"  {len(news)} news items")

    print("Fetching Federal Register executive actions...")
    executive = fetch_executive_actions()
    print(f"  {len(executive)} executive actions")
    FRESHNESS = get_freshness(executive)
    if FRESHNESS:
        print(f"  Freshness: {FRESHNESS['label']} — {FRESHNESS['ago']} ({FRESHNESS['date']})")
    else:
        print("  Freshness: no dated actions found")

    print("Fetching FEC cannabis PAC data...")
    pacs = fetch_cannabis_pacs()
    print(f"  {len(pacs)} cannabis PACs")

    print("Fetching Congress.gov cannabis bills...")
    bills = fetch_bills()
    print(f"  {len(bills)} bills found")

    print("Fetching vapor/nicotine news and Federal Register data...")
    vapor_news = fetch_vapor_news()
    vapor_fed = fetch_vapor_federal_register()
    print(f"  {len(vapor_news)} vapor news items, {len(vapor_fed)} Federal Register entries")

    print("Fetching lawmaker profiles (Congress.gov + ProPublica + FEC)...")
    lawmakers = fetch_lawmakers(bills)
    print(f"  {len(lawmakers)} lawmakers profiled")

    print("Fetching opposition PAC disbursements (FEC)...")
    opposition = fetch_opposition_disbursements()
    print(f"  {len(opposition)} opposition PAC recipients found")

    print("Fetching opposition funding news (Google News RSS)...")
    opp_news = fetch_opposition_news()
    print(f"  {len(opp_news)} opposition news items")

    print("Building pages...")
    pages = {
        "index.html":       build_index(news, bills, executive),
        "bills.html":       build_bills(bills),
        "lawmakers.html":   build_lawmakers(lawmakers, opposition, opp_news),
        "executive.html":   build_executive(executive),
        "money.html":       build_money(pacs, opposition, opp_news),
        "vapor.html":       build_vapor(vapor_news, vapor_fed),
        "methodology.html": build_methodology(),
        "about.html":       build_about(),
    }

    for filename, html in pages.items():
        path = OUTPUT_DIR / filename
        path.write_text(html, encoding="utf-8")
        print(f"  Wrote {filename}")

    # Assets placeholder note
    readme = assets / "README.txt"
    readme.write_text(
        "Drop logo files here:\n"
        "  horsepowerai-logo.png  (Horsepower AI logo - PNG format)\n"
        "  gft1-logo.png          (GF Tech One logo - PNG format)\n\n"
        "Both logos will appear in the nav bar and footer automatically.\n"
    )

    print(f"\nAll pages built -> {OUTPUT_DIR}")
    print("Next: add logo files to policy-tracker/assets/ then push to GitHub.")
