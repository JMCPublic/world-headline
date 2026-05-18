# World Headline — Project Roadmap

> *A global "news empathy" tool. Country-by-country newspaper comparison — Left / Centre / Right — with Hobby Horse (topic) and Undue Influence (people) trackers that build over time.*

---

## What you have right now

| File | What it is |
|------|------------|
| `uk_press_today.html` | UK edition — Observer / Sunday Times / Mail on Sunday, v4 with both trackers |
| `europe_press_today.html` | Europe edition — France, Germany, Italy, Spain, Poland, tabbed |
| `ROADMAP.md` | This file |

Open either HTML file in any browser. That's the working prototype.

---

## Running it manually (right now, before any website exists)

1. Open Claude (here in Cowork)
2. Say "it's Sunday — here are this week's UK headlines" (share what you know / saw)
3. Claude rebuilds the HTML with updated content and tracker dots
4. Open the file in your browser — done

Cost: your time, once a week. No tech required.

---

## The full build plan

### PHASE 1 — Foundations (do one step per day, no coding)

| Day | Task | Where |
|-----|------|--------|
| **Day 1** | Buy a domain name | [namecheap.com](https://www.namecheap.com) — search: `theglobalpaper.com`, `presswatch.world`, `newslens.world`, `worldpresstoday.com` — ~£10/year |
| **Day 2** | Create a free Cloudflare Pages account | [cloudflare.com](https://cloudflare.com) — free forever for static sites |
| **Day 3** | Create a free GitHub account | [github.com](https://github.com) — where your files live |
| **Day 4** | Connect GitHub → Cloudflare | One-click setup. After this, every file you update on GitHub goes live on your site automatically |
| **Day 5** | Upload the UK and Europe HTML files to GitHub | Drag and drop. Your site is live. |

**Done. Your site exists on the internet.** ✅

---

### PHASE 2 — More countries (ongoing, with Claude)

| Task | What |
|------|------|
| Add USA | NYT/WaPo (left), Politico/USA Today (centre), WSJ/NY Post (right) |
| Add Middle East | Haaretz / Jerusalem Post (Israel), Arab News / Al-Arabiya, Al Jazeera |
| Add Latin America | Folha de S.Paulo / O Globo (Brazil), El Universal / Reforma (Mexico), La Nación / Clarín (Argentina) |
| Add Scandinavia | Sweden, Norway, Denmark — surprisingly different from each other |
| Add Asia-Pacific | Japan Times, South China Morning Post, The Hindu (India), Sydney Morning Herald |

Each country takes one Claude session. Same format, same trackers.

---

### PHASE 3 — Data layer (makes updates easy)

Instead of rebuilding HTML every week, content moves into a simple JSON text file.  
Claude writes the JSON, you paste it to GitHub, the website updates automatically.

- One HTML template per region
- All stories, trackers, and blind spots in a data file
- Updating a paper's stories = editing a few lines of text, not touching design

---

### PHASE 4 — World View

An aggregate page showing:
- What is the global left talking about this week?
- What is the global right fixated on?
- Where do left AND right agree? (rare — worth highlighting)
- Top 3 global stories that transcend political lean

---

### PHASE 5 — Automation (daily self-updating)

| Step | What |
|------|------|
| Get a Claude API key | [console.anthropic.com](https://console.anthropic.com) — pay as you go |
| Get a NewsAPI key | [newsapi.org](https://newsapi.org) — free tier to start |
| Claude writes the script | Python script: fetch headlines → Claude synthesises → writes JSON → commits to GitHub → site updates |
| GitHub Actions | Free scheduler. Runs the script every morning at 7am |

**Daily running cost when automated: ~£3–6/month total.**

---

### PHASE 6 — Polish & launch

- Mobile optimisation
- Homepage with world map (click to navigate)
- Continent → Region → Country hierarchy
- Search: find a story, person, or country
- About page: explain the mission
- Optional: weekly email digest

---

## Running costs when done

| Item | Cost |
|------|------|
| Domain name | ~£10/year |
| Hosting (Cloudflare Pages) | Free |
| GitHub | Free |
| Claude API (daily automation) | ~£2–5/month |
| NewsAPI | Free to start |
| **Total** | **~£3–6/month** |

---

## What makes this different from what already exists

| Feature | AllSides | Google News | Worldpress | **World Headline** |
|---------|----------|-------------|------------|-------------------|
| Left/Centre/Right framing | ✅ US only | ❌ | ❌ | ✅ |
| Editorial synthesis | ❌ | ❌ | ❌ | ✅ |
| Multiple countries | ❌ | Partial | Basic | ✅ |
| Hobby Horse tracker | ❌ | ❌ | ❌ | ✅ |
| Undue Influence tracker | ❌ | ❌ | ❌ | ✅ |
| Blind spot panels | ❌ | ❌ | ❌ | ✅ |
| World aggregate view | ❌ | ❌ | ❌ | 🔜 |

---

*Start with Day 1. Go to Namecheap. Pick a name. Come back tomorrow.*
