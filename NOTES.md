# World Headline — Notes, Ideas & Session Log

One place for everything: ideas, decisions, questions, and a record of every session.
Open in Notepad (or any text editor) to add your own notes any time.

---

## 💡 Ideas

- **"What the Markets Think"** — weekly panel per country showing currency performance vs USD/EUR/GBP and bond market direction, framed against which party (L/C/R) is in government. Tagline: *"Hips and markets don't lie."* Data source TBD (Yahoo Finance or similar free API). Fits naturally into the weekly Monday automation.

- **Weekend edition** — Observer, Mail on Sunday, Sunday Times as an alternative weekend view for the UK page. Currently using daily papers (Guardian/Daily Mail/Times) for the weekly Monday update. Weekend edition is a future concept.

- **What the markets think** - left to right what did currency do vs dollar euro sterling - what is the bond market for that country doing - can be done every week - hips and markets don't lie.

---

## 🗒️ Notes & Decisions

- **Filenames stay as uk_press_today.html etc.** — don't rename them, it would break saved links. Only the visible display text says "Press This Week."

- **Adding a new country — checklist:**
  1. Papers display left-to-right across the page (not stacked)
  2. Each paper card has a link to its website
  3. resources.html updated with the new newspapers

- **UK papers** are now Guardian (Left), Times (Centre-right), Daily Mail (Right) — the Sunday equivalents (Observer, Sunday Times, Mail on Sunday) are parked for a future weekend edition.

- **Automation** runs every Monday at 6am UTC via GitHub Actions. Secret must be named exactly `ANTHROPIC_API_KEY`. Workflow permissions must be set to Read & Write in repo Settings → Actions → General.

- **Comments (#94)**: vision is one shared discussion page where threads from individual newspaper sections all appear together, with commenter's country visible to give an international flavour. Giscus (GitHub Discussions) is likely mechanism — already live on Axis of Equal. Parked until we have more to discuss.

- **Water Cooler automation**: wants it automated but in Michael's own editorial voice. Plan is to train Claude on existing Water Cooler writing samples first, then automate. Keep distinct from press page automation.

---

## ❓ Questions / Things to Decide

- Comments: Giscus on every press page, or a dedicated community hub page?
- Newsletter: what platform? what content structure? who is the audience?
- "What the Markets Think": which countries first? which currencies to show per country?
- Saudi Arabia / Egypt: lean labels (Left/Centre/Right) don't really apply to state-controlled press — how should we frame it instead?

---

## 📋 Session Log

### Session 1 — c. 18 May 2026
**Theme: Project setup and early prototype**

- Established core concept: country-by-country left/centre/right newspaper comparison, with editorial trackers (Hobby Horses, Undue Influence, Blind Spots)
- Tech stack decided: static HTML/CSS/JS, GitHub Pages (free hosting), GitHub Actions for automation
- UK press dashboard built (v4): Observer, Sunday Times, Mail on Sunday
- Europe press dashboard built: France, Germany, Italy, Spain, Poland
- Decisions: static site over CMS for simplicity and zero server cost; running cost ~£3–6/month when automated (Claude API only)

---

### Session 2 — c. 18–19 May 2026
**Theme: Homepage, navigation, site expansion**

- Homepage (index.html) built with world map navigation
- Continent → region → country hierarchy established
- Americas, Asia-Pacific, Africa, Middle East press pages created
- Navigation bar added across all pages
- Site published to GitHub Pages at jmcpublic.github.io/world-headline/

---

### Session 3 — 19 May 2026
**Theme: First live test — 12 bugs and features identified**

Michael tested the site and submitted a list of issues. All resolved:

- AoE scoring scale changed to 0–10 numeric
- Grid guidelines added at every 1-unit interval on AoE chart
- Party hover boxes: leader name, in-power/opposition flag, founding date, score
- Best Place to Be panel repositioned below chart with own nav item
- "Why some countries aren't here" text added
- "Work in Progress" label removed
- Back/Up navigation added to AoE
- "Show Selected Only" country compare bug fixed
- Nav options added to bottom of every page
- Americas and Asia-Pacific horizontal scroll layout bug fixed
- AoE party name tooltip overlap fixed
- Water Cooler given its own nav item
- "When parties agree" feature added to Poles Apart (8 countries)

---

### Session 4 — 20–21 May 2026
**Theme: v1.0 — new countries, AoE features, Poles Apart completion**

New countries added (40 total): Greece, Turkey (Europe), Peru (Americas), Senegal (Africa)
All 40 countries given Blind Spot panels.

AoE: Political Compass (Fiscal vs Social axis), Country Similarity + Rankings, scoring methodology explainer, party pill score badges, "When Parties Agree" badges.

Poles Apart: Consensus Moments, Divergence Tracker, Cross-border Influence, When Parties Agree panel.

**v1.0 declared.**

---

### Session 5 — 21–22 May 2026
**Theme: Automation, Giscus comments, paper swaps, edition headers, resources page**

- GitHub Actions automation built and debugged (3 failed runs → Run #4 success ✅)
- Giscus comments installed on AoE scoring methodology section
- UK papers swapped: Observer/Sunday Times/Mail on Sunday → Guardian/Times/Daily Mail
- Edition headers added to all 6 press pages (auto-patched by script every Monday)
- "Why some countries aren't here" box repositioned on AoE
- resources.html created: all 120 newspapers, searchable, with website links
- All files uploaded to GitHub

---

### Session 6 — 22 May 2026
**Theme: Press This Week, paywall tips, country planning, new ideas**

- "Press Today" → "Press This Week" across all 6 press pages (17 replacements, filenames unchanged)
- Paywall tips collapsible box added to resources.html (library subscriptions, Google trick, Wayback Machine, direct support)
- New country priority order agreed: Botswana → Tanzania → Lebanon → Zimbabwe → Saudi Arabia → Egypt → Iran
- "Adding a country" checklist established
- "What the Markets Think" feature idea noted
- Session log and NOTES.md started (this file)
- All files uploaded to GitHub

---

### Session 7 — 22 May 2026
**Theme: Language headings, new countries, quick wins sweep, AoE compass fix**

- Local-language "Press This Week" equivalents added to all non-English country headings (26 replacements across Europe, Americas, Asia, Africa)
- Botswana added to africa_press_today.html: Mmegi (Left), The Voice (Centre), Botswana Gazette (Centre-right)
- Tanzania added to africa_press_today.html: The Citizen (Centre-left), Daily News (Centre/State), The Guardian Tanzania (Centre-right)
- Lebanon added to middleeast_press_today.html: Al-Akhbar (Left), L'Orient Today (Centre/Reform), An-Nahar (Centre-right)
- resources.html updated with 9 new newspapers; count now 129 / 43 countries
- resources.html added to all 11 nav bars
- All newspaper masthead names on all press pages made clickable links (linked to paper websites)
- Pilots checklist run across all 6 press pages — all pass (blind spots, paper names, headings, links)
- **AoE Political Compass filter bug fixed**: lean filter and country compare filter now both work in compass view — `renderCompass()` reads active filter state and re-fires on filter/compare changes
- All files uploaded to GitHub (session-end upload pending — upload after this)

---

## ⏭️ Next Session

1. **Upload to GitHub** (files from this session)
2. **Next country**: Zimbabwe (africa_press_today.html)
3. **Then**: Saudi Arabia, Egypt, Iran
4. Comments (#94) — design the shared discussion page (parked but not forgotten)
5. "What the Markets Think" feature — start scoping data sources
