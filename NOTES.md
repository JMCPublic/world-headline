# World Headline — Notes, Ideas & Session Log

One place for everything: ideas, decisions, questions, and a record of every session.
Open in Notepad (or any text editor) to add your own notes any time.

---

## 💡 Ideas

- **"What the Markets Think"** — weekly panel per country showing currency performance vs USD/EUR/GBP and bond market direction, framed against which party (L/C/R) is in government. Tagline: *"Hips and markets don't lie."* See full scoping note below.

- **Weekend edition** — Observer, Mail on Sunday, Sunday Times as an alternative weekend view for the UK page. Currently using daily papers (Guardian/Daily Mail/Times) for the weekly Monday update. Weekend edition is a future concept.

---

---

## 📊 What the Markets Think — API Scoping

### The feature
Each country press page gets a weekly panel showing:
- Currency performance that week vs USD, EUR, and GBP
- Bond market / interest rate direction (up / down / flat)
- Framed against which party (left/centre/right) is in power
- Updated every Monday by the existing GitHub Actions automation

### Currency data — ✅ Fully solved, free, no key needed

**Best option: fawazahmed0/exchange-api**
- GitHub: github.com/fawazahmed0/exchange-api
- Endpoint: `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json`
- 200+ currencies including all 44 World Headline countries (ZWL, NGN, KES, GHS, etc.)
- No API key. No registration. No rate limits. Served via jsDelivr CDN.
- Daily updates. Historical data available: swap `@latest` for `@YYYY-MM-DD`
- To get week-on-week change: fetch today's rate + last Monday's rate, calculate % change
- Special case: Zimbabwe now uses ZiG (Zimbabwe Gold, introduced April 2024). ZiG may not appear as a standard currency code yet — show USD/ZWL or note "USD economy" as a flag

**Runner-up: Frankfurter (api.frankfurter.dev)**
- Free, no key, no rate limits, ECB-sourced
- Limitation: only ~33 major currencies — misses most African, Middle Eastern, and some Asian currencies
- Good fallback for European countries if primary source has issues

### Bond yield data — ⚠️ Harder, no perfect free solution yet

**What we actually need:** Weekly 10-year government bond yield for each country (the standard measure of sovereign borrowing cost / market confidence)

**The honest picture:**
- No truly free, no-key, comprehensive bond yield API exists for all 44 countries
- The good services (Bloomberg, Refinitiv, CBonds) are paid
- Trading Economics has the data (tradingeconomics.com/bonds) but no free API

**Best available free options:**

1. **World Bank API** (api.worldbank.org) — free, no key, covers central bank policy rates and lending rates for all countries. Not live bond yields, but a reasonable proxy for bond market direction. Updated quarterly not weekly — not ideal for the "this week" framing.

2. **FRED API** (api.stlouisfed.org) — free with a free API key (no cost, just register). Excellent for US Treasuries and some international bonds. Limited coverage of emerging markets.

3. **FinanceFlowAPI** — 200 free requests/month, covers 50+ countries, real-time bond yields. Enough for weekly automation (44 countries × 1 call/week = 44 calls/week = ~176/month — slightly over the free limit).

4. **Scraping Trading Economics** — technically feasible but fragile; against their ToS.

### Recommended build approach

**Phase 1 (Build now):** Currency moves only
- Use fawazahmed0 exchange API — completely free, zero setup, covers all countries
- Show: local currency vs USD, EUR, GBP — weekly % change (Monday to Monday)
- Simple visual: up arrow (green) / down arrow (red) / flat, with % figure
- Add to weekly refresh script alongside existing story updates
- Enough to launch the feature and it looks great

**Phase 2 (add when ready):** Bond market — self-hosted data file approach
- **Build our own `bond_data.json`** — a single file in the repo with bond yield for each country, updated manually (then eventually automatically)
- Source the numbers weekly from tradingeconomics.com/bonds or investing.com/rates-bonds/world-government-bonds — both free to view, just not free to call as an API
- The GitHub Actions refresh script reads `bond_data.json` and bakes the direction (up/flat/down) and yield % into each country's press page HTML — same pattern as story updates
- This means zero API dependency, zero rate limits, zero cost — we own the data
- Eventually: could write a scraper for the refresh script to auto-populate bond_data.json. Or just update it manually since bond yields don't move wildly week to week.
- **Format for bond_data.json:**
  ```json
  {
    "updated": "2026-05-26",
    "yields": {
      "united-kingdom": { "yield": 4.62, "change": +0.08, "direction": "up" },
      "france":         { "yield": 3.41, "change": -0.02, "direction": "down" },
      "zimbabwe":       { "yield": null, "note": "No sovereign bond market" }
    }
  }
  ```

### Currency codes for all 44 countries (for Phase 1)
```
UK: GBP | France/Germany/etc (Eurozone): EUR | Sweden: SEK | Norway: NOK | Denmark: DKK
Finland: EUR | Poland: PLN | Czechia: CZK | Hungary: HUF | Turkey: TRY
USA: USD | Canada: CAD | Mexico: MXN | Brazil: BRL | Argentina: ARS
Colombia: COP | Chile: CLP | Peru: PEN | Malaysia: MYR | India: INR
Philippines: PHP | Taiwan: TWD | South Korea: KRW | Japan: JPY | Australia: AUD | NZ: NZD
Israel: ILS | Nigeria: NGN | Kenya: KES | Senegal: XOF | Ghana: GHS
South Africa: ZAR | Botswana: BWP | Tanzania: TZS | Zimbabwe: USD/ZiG*
Lebanon: LBP (note: Lebanon uses USD informally post-2019 crisis)
Ireland: EUR | Portugal: EUR | Spain: EUR | Italy: EUR | Greece: EUR
Austria: EUR | Netherlands: EUR
```
*Zimbabwe: Show USD since economy is effectively dollarised. The ZiG is too new for reliable API data.
*Lebanon: Show LBP and note it alongside USD given the dual-currency reality post-2019 collapse.

### Design concept
Small collapsible panel below the paper cards, per country:
```
📈 Markets This Week  [▼ expand]
  🇿🇦 ZAR vs USD  ▼ -1.2%   vs EUR  ▲ +0.3%   vs GBP  ▼ -0.8%
  📊 SA 10yr bond: 9.4%  ▲ +0.1pp  [Govt: ANC/GNU — Centre-left]
```

---

## 🗒️ Notes & Decisions

- **Filenames stay as uk_press_today.html etc.** — don't rename them, it would break saved links. Only the visible display text says "Press This Week."

- **Adding a new country — full checklist (every single time):**
  1. Press page: country tab + papers display left-to-right (not stacked)
  2. Press page: each paper card has a clickable link to its website — title is the hyperlink, with hint text below reading "↗ click the newspaper title to visit their website" (non-clickable, outside the anchor)
  3. Press page: blind spot panel uses the **standard dark collapsible format** (`.blind-spot` class) — not the old expanded `.blind-spots` / `.blind-spot-item` format
  4. resources.html: add 3 rows, update count (newspapers + countries)
  5. axis_of_equal.html: add `aoe-row` with party pills and lean/leader/status data
  6. axis_of_equal.html: add party scores to `PARTY_FISCAL` and `PARTY_SOCIAL` (for compass)
  7. axis_of_equal.html: add `cpick-btn` in the country picker list
  8. Best Place to Be: auto-updates once step 5 is done (reads live `aoe-row` elements — no manual step)
  9. water_cooler.html: add wc-card (3 talking points) + Weekly Pulse table row (4 weeks of categorised topics)
  10. NOTES.md: update session log

- **Poles Apart — not a per-country checklist item.** Poles Apart is structured around analytical themes (coherence gap, playbooks, cross-border influence, consensus moments, divergence tracker, when-parties-agree), not individual country slots. It gets expanded separately as a content piece — typically a dedicated session once enough new countries have been added to make the expansion worthwhile. Currently covers ~15 countries; expand as a batch when adding a new region or after every 5–6 new countries.

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

### Session 8 — 22 May 2026
**Theme: Full pilots audit, Zimbabwe added, AoE completed, Water Cooler to 44 countries**

- Full pilots audit run across all features: AoE ✅ 44/44, cpick ✅ 44/44, R&A ✅ 44/44, Water Cooler ❌ 14/44 → fixed this session
- Zimbabwe added to africa_press_today.html: NewsDay (Centre-Left), The Herald (State/ZANU-PF), Zimbabwe Independent (Centre-Right)
- resources.html updated: 129→132 newspapers, 43→44 countries (Zimbabwe rows added)
- axis_of_equal.html: 6 missing countries added retroactively (Zimbabwe, South Africa, Ghana, Botswana, Tanzania, Lebanon) with aoe-rows, cpick-btns, PARTY_FISCAL & PARTY_SOCIAL data
- AoE Political Compass filter bug fixed: lean filter + country compare filter now both work in compass view
- Corrupt PARTY_FISCAL block fixed (social values had leaked in); Peru & Senegal PARTY_SOCIAL gaps fixed
- **What the Markets Think** feature fully scoped: Phase 1 (currency, fawazahmed0 API, free/no-key), Phase 2 (self-hosted bond_data.json, worldgovernmentbonds.com as manual source). Full scoping note added to NOTES.md
- **Water Cooler expanded from 14 → 44 countries**: 30 new wc-cards + 30 new Weekly Pulse table rows added for all missing countries (UK, France, Germany, Netherlands, Sweden, Norway, Italy, Spain, Greece, Turkey, Austria, Czechia, Hungary, USA, Canada, Mexico, Colombia, Chile, Peru, Philippines, Taiwan, Australia, New Zealand, Nigeria, Kenya, Senegal, Botswana, Tanzania, Zimbabwe, Lebanon)
- All files uploaded to GitHub (pending — upload after this)

---

---

### Session 9 — 22 May 2026
**Theme: Saudi Arabia added, version backup created**

- **Version_Before_WTMT.zip** saved to project folder — full snapshot of all 12 site files before What the Markets Think feature is built
- **Saudi Arabia added** — full 10-step checklist (steps 5–8 N/A: correctly in AoE "out of spec" panel as no-parties monarchy):
  - middleeast_press_today.html: Gulf tab activated, Gulf region panel created, Saudi Arabia with 3 papers — Arab News (English/Pro-reform), Saudi Gazette (Official/State-aligned), Asharq Al-Awsat (Pan-Arab/Royal-owned); 4 blind spots (Kafala, MBS succession, Vision 2030 contradictions, Yemen reckoning)
  - resources.html: 3 rows added, count updated 132→135 newspapers / 44→45 countries
  - water_cooler.html: wc-card + Weekly Pulse row added, hero updated 44→45 countries
  - NOTES.md: checklist updated (step 9 = Water Cooler; step 10 = NOTES.md); Poles Apart note added
- AoE "out of spec" note clarified: for non-party / authoritarian states, AoE steps 5–8 are replaced by confirming the country appears in the oos panel
- All files to upload: middleeast_press_today.html, resources.html, water_cooler.html, NOTES.md, Version_Before_WTMT.zip

---

### Session 10 — 26 May 2026
**Theme: McDonald's consistency — blind spots standardised, edition dates fixed**

- **Edition dates fixed** on all 6 press pages: updated from "Week of 18 May 2026" → "Week of 25 May 2026 · Last refreshed: Mon 25 May 2026 · Next update: Mon 1 Jun 2026". Per-country edition tags updated to match.
- **Blind spot format standardised across ALL pages** — 24 countries converted from old cream/light format (`.blind-spots` / `.blind-spot-item`) to the standard dark collapsible panel (`.blind-spot` / `.blind-items` / `.blind-item`). Pages fixed: americas (Brazil, Argentina, Colombia, Chile, Peru), asia (all 8: Japan, Taiwan, South Korea, Malaysia, India, Philippines + 2 more), africa (all 8: Nigeria, Ghana, Senegal, South Africa, Botswana, Zimbabwe, Tanzania, Kenya), middleeast (Israel, Lebanon, Saudi Arabia). UK and Europe were already correct.
- Old blind-spot CSS (`.blind-spots`, `.blind-spot-item`) removed from Americas, Asia, Africa, Middle East stylesheets. New CSS added to Asia, Africa, Middle East.
- Conversion handled programmatically — emoji parsing, `<strong>Title:</strong>` extraction, and " — " separator splitting all correctly handled.

---

### Session 11 — 2 Jun 2026
**Theme: Automation fixed, 3 new countries (Egypt, Iran, Belgium), 5 added to refresh script**

- **Automation diagnosed and fixed**: Two bugs stopped Weekly Story Refresh on May 25 + Jun 1. (1) UK HTML still said "The Sunday Times" — script looked for "The Times". Fixed paper-name div + updated meta/lean/stories. (2) Austria's stories container used `class="stories-list"` — script looks for `class="stories"`. Fixed with global replace in europe_press_today.html. Anchor audit: 80→94→101/101 papers findable.
- **5 missing countries added to refresh script**: Botswana, Tanzania, Lebanon, Zimbabwe, Saudi Arabia now in PAPERS list (15 new entries). Tanzania naming collision fixed: "The Citizen" → "The Citizen Tanzania" in both HTML and script.
- **Egypt added** — full 10-step checklist. North Africa tab activated in middleeast_press_today.html. Papers: Al-Ahram (State/Pro-government), Egypt Independent (Independent/Centre), Mada Masr (Independent/Critical). Egypt → AoE OOS panel. Resources + Water Cooler updated.
- **Iran added** — full 10-step checklist. Added to Gulf tab in middleeast_press_today.html. Papers: Kayhan (Hardline/State), Shargh (Reformist), Iran International (Independent/London). Iran already in AoE OOS panel. Resources + Water Cooler updated.
- **Belgium added** — full 10-step checklist. "Coming Soon" placeholder replaced in europe_press_today.html. Papers: De Morgen (Left/Flemish), Le Soir (Centre-left/French), Het Laatste Nieuws (Right/Flemish). AoE row added with 7 parties (PTB, Vooruit, PS, Les Engagés, N-VA, MR, Vlaams Belang). Resources + Water Cooler updated.
- **Counts**: Resources now 144 sources / 48 countries. Refresh script covers 101 papers.
- **Auto-edition JS**: Added to all 6 press pages — displays correct week automatically from browser clock, never stale.

---

## ⏭️ Next Session

1. **Upload to GitHub** — all changed files (list below)
2. **What the Markets Think Phase 1** — implement currency panel using fawazahmed0 API (fully scoped, ready to build)
3. **Poles Apart** — expand country coverage beyond current ~15 countries
4. **Comments (#94)** — design the shared discussion page (parked but not forgotten)
5. **Belgium** — note: AoE PARTY_FISCAL/SOCIAL compass data uses placeholder party names ("Les Enages" typo) — fix when building compass data properly
