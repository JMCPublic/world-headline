#!/usr/bin/env python3
"""
World Headline — Weekly Story Refresh
======================================
Fetches RSS feeds for each newspaper, calls Claude API to summarise the top 3
stories, and patches the relevant .html file in-place.

Usage:
  python scripts/refresh_stories.py              # refresh all papers
  COUNTRY_FILTER=uk python scripts/refresh_stories.py  # one country only

Required env var:
  ANTHROPIC_API_KEY   — set as GitHub Secret "ANTHROPIC_API_KEY"
Optional:
  COUNTRY_FILTER      — limit to one country slug (e.g. "uk", "france")
  DRY_RUN=1           — fetch + generate but don't write files (for testing)
"""

import os, re, sys, datetime, textwrap, time
import html as _html
import feedparser, anthropic

# ── Date / Edition ────────────────────────────────────────────────────────────

WEEK_OF      = datetime.date.today().strftime("%-d %B %Y")   # "2 June 2026"
EDITION_STR  = f"Edition · Week of {WEEK_OF}"

# ── Paper registry ────────────────────────────────────────────────────────────
# Each entry: name (must match exactly what's in the HTML's paper-name div),
# html_file (relative to repo root), rss (empty string = skip / manual-only).
# Claude gets the paper name + lean to frame its editorial voice.

PAPERS = [

    # ── United Kingdom ────────────────────────────────────────────────────────
    {"country":"uk",    "name":"The Observer",                   "lean":"Left",                   "html":"uk_press_today.html",        "rss":"https://www.theguardian.com/uk/rss"},
    {"country":"uk",    "name":"The Sunday Times",               "lean":"Centre-right",           "html":"uk_press_today.html",        "rss":"https://www.thetimes.co.uk/rss"},
    {"country":"uk",    "name":"Mail on Sunday",                 "lean":"Right",                  "html":"uk_press_today.html",        "rss":"https://www.dailymail.co.uk/articles.rss"},

    # ── France ────────────────────────────────────────────────────────────────
    {"country":"france","name":"Libération",                     "lean":"Left",                   "html":"europe_press_today.html",    "rss":"https://www.liberation.fr/arc/outboundfeeds/rss/"},
    {"country":"france","name":"Le Monde",                       "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.lemonde.fr/rss/une.xml"},
    {"country":"france","name":"Le Figaro",                      "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://www.lefigaro.fr/rss/figaro_actualites.xml"},

    # ── Germany ───────────────────────────────────────────────────────────────
    {"country":"germany","name":"Süddeutsche Zeitung",           "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://rss.sueddeutsche.de/rss/Politik"},
    {"country":"germany","name":"Frankfurter Allgemeine",        "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://www.faz.net/rss/aktuell/"},
    {"country":"germany","name":"Bild",                          "lean":"Right/tabloid",          "html":"europe_press_today.html",    "rss":"https://www.bild.de/rssfeeds/rss3-20745882,feed=alles.bild.html"},

    # ── Netherlands ───────────────────────────────────────────────────────────
    {"country":"netherlands","name":"de Volkskrant",             "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.volkskrant.nl/nieuws-achtergrond/rss.xml"},
    {"country":"netherlands","name":"NRC Handelsblad",           "lean":"Centre-liberal",         "html":"europe_press_today.html",    "rss":"https://www.nrc.nl/rss/"},
    {"country":"netherlands","name":"De Telegraaf",              "lean":"Right",                  "html":"europe_press_today.html",    "rss":"https://www.telegraaf.nl/rss"},

    # ── Ireland ───────────────────────────────────────────────────────────────
    {"country":"ireland","name":"Irish Examiner",                "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.irishexaminer.com/feed/"},
    {"country":"ireland","name":"The Irish Times",               "lean":"Centre",                 "html":"europe_press_today.html",    "rss":"https://www.irishtimes.com/cmlink/news-1.1319192"},
    {"country":"ireland","name":"Irish Independent",             "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://www.independent.ie/feed/"},

    # ── Sweden ────────────────────────────────────────────────────────────────
    {"country":"sweden","name":"Aftonbladet",                    "lean":"Left/tabloid",           "html":"europe_press_today.html",    "rss":"https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/"},
    {"country":"sweden","name":"Dagens Nyheter",                 "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.dn.se/rss/"},
    {"country":"sweden","name":"Svenska Dagbladet",              "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://www.svd.se/?service=rss"},

    # ── Norway ────────────────────────────────────────────────────────────────
    {"country":"norway","name":"Dagbladet",                      "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.dagbladet.no/"},
    {"country":"norway","name":"Aftenposten",                    "lean":"Centre",                 "html":"europe_press_today.html",    "rss":"https://www.aftenposten.no/rss/"},
    {"country":"norway","name":"VG (Verdens Gang)",              "lean":"Tabloid/centre",         "html":"europe_press_today.html",    "rss":"https://www.vg.no/rss/feed/"},

    # ── Denmark ───────────────────────────────────────────────────────────────
    {"country":"denmark","name":"Politiken",                     "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://politiken.dk/rss/"},
    {"country":"denmark","name":"Berlingske",                    "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://www.berlingske.dk/rss/"},
    {"country":"denmark","name":"Jyllands-Posten",               "lean":"Right",                  "html":"europe_press_today.html",    "rss":"https://jyllands-posten.dk/rss/"},

    # ── Finland ───────────────────────────────────────────────────────────────
    {"country":"finland","name":"Helsingin Sanomat",             "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.hs.fi/rss/tuoreimmat.xml"},
    {"country":"finland","name":"Kauppalehti",                   "lean":"Business/centre",        "html":"europe_press_today.html",    "rss":"https://www.kauppalehti.fi/rss/uutiset/"},
    {"country":"finland","name":"Iltalehti",                     "lean":"Tabloid/right",          "html":"europe_press_today.html",    "rss":"https://www.iltalehti.fi/rss.xml"},

    # ── Italy ─────────────────────────────────────────────────────────────────
    {"country":"italy","name":"La Repubblica",                   "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.repubblica.it/rss/homepage/rss2.0.xml"},
    {"country":"italy","name":"Corriere della Sera",             "lean":"Centre",                 "html":"europe_press_today.html",    "rss":"https://xml2.corriere.it/rss/homepage.xml"},
    {"country":"italy","name":"Il Giornale",                     "lean":"Right",                  "html":"europe_press_today.html",    "rss":"https://www.ilgiornale.it/rss.xml"},

    # ── Spain ─────────────────────────────────────────────────────────────────
    {"country":"spain","name":"El País",                         "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
    {"country":"spain","name":"El Mundo",                        "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml"},
    {"country":"spain","name":"ABC",                             "lean":"Right",                  "html":"europe_press_today.html",    "rss":"https://www.abc.es/rss/feeds/abcPortada.xml"},

    # ── Portugal ──────────────────────────────────────────────────────────────
    {"country":"portugal","name":"Público",                      "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.publico.pt/rss"},
    {"country":"portugal","name":"Jornal de Notícias",           "lean":"Centre",                 "html":"europe_press_today.html",    "rss":"https://www.jn.pt/rss/"},
    {"country":"portugal","name":"Observador",                   "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://observador.pt/feed/"},

    # ── Greece ────────────────────────────────────────────────────────────────
    {"country":"greece","name":"Efimerida ton Syntakton (EfSyn)","lean":"Left",                   "html":"europe_press_today.html",    "rss":""},  # Greek, no public English RSS
    {"country":"greece","name":"Kathimerini",                    "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":"https://www.ekathimerini.com/rss/"},
    {"country":"greece","name":"Dimokratia",                     "lean":"Right/nationalist",      "html":"europe_press_today.html",    "rss":""},  # Greek, no public RSS

    # ── Turkey ────────────────────────────────────────────────────────────────
    {"country":"turkey","name":"Cumhuriyet",                     "lean":"Secular left",           "html":"europe_press_today.html",    "rss":""},  # Turkish, no reliable RSS
    {"country":"turkey","name":"Hürriyet",                       "lean":"Centre",                 "html":"europe_press_today.html",    "rss":""},  # Turkish
    {"country":"turkey","name":"Sabah",                          "lean":"Pro-government",         "html":"europe_press_today.html",    "rss":""},  # Turkish, government-aligned

    # ── Poland ────────────────────────────────────────────────────────────────
    {"country":"poland","name":"Gazeta Wyborcza",                "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":""},  # paywalled
    {"country":"poland","name":"Rzeczpospolita",                 "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":""},  # paywalled
    {"country":"poland","name":"Gazeta Polska Codziennie",        "lean":"Right/nationalist",      "html":"europe_press_today.html",    "rss":""},  # no public RSS

    # ── Czech Republic ────────────────────────────────────────────────────────
    {"country":"czech","name":"Deník N",                         "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":""},  # paywalled
    {"country":"czech","name":"MF Dnes",                         "lean":"Centre",                 "html":"europe_press_today.html",    "rss":""},  # no public RSS
    {"country":"czech","name":"Právo",                           "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":""},  # no public RSS

    # ── Austria ───────────────────────────────────────────────────────────────
    {"country":"austria","name":"Der Standard",                  "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":"https://www.derstandard.at/rss"},
    {"country":"austria","name":"Die Presse",                    "lean":"Centre-right",           "html":"europe_press_today.html",    "rss":""},  # paywalled
    {"country":"austria","name":"Kronen Zeitung",                "lean":"Right/populist",         "html":"europe_press_today.html",    "rss":""},  # no public RSS

    # ── Hungary ───────────────────────────────────────────────────────────────
    {"country":"hungary","name":"Telex",                         "lean":"Independent/centre-left","html":"europe_press_today.html",    "rss":"https://telex.hu/rss"},
    {"country":"hungary","name":"Magyar Hang",                   "lean":"Centre-left",            "html":"europe_press_today.html",    "rss":""},  # limited RSS
    {"country":"hungary","name":"Magyar Nemzet",                 "lean":"Pro-Orbán/right",        "html":"europe_press_today.html",    "rss":""},  # no reliable RSS

    # ── USA ───────────────────────────────────────────────────────────────────
    {"country":"usa",   "name":"The New York Times",             "lean":"Centre-left",            "html":"americas_press_today.html",  "rss":"https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},
    {"country":"usa",   "name":"USA Today",                      "lean":"Centre",                 "html":"americas_press_today.html",  "rss":"https://rssfeeds.usatoday.com/usatoday-NewsTopStories"},
    {"country":"usa",   "name":"Wall Street Journal",            "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":"https://feeds.a.dj.com/rss/RSSWorldNews.xml"},

    # ── Canada ────────────────────────────────────────────────────────────────
    {"country":"canada","name":"Toronto Star",                   "lean":"Centre-left",            "html":"americas_press_today.html",  "rss":"https://www.thestar.com/search/?f=rss&t=article&c=news&s=start_time&sd=desc"},
    {"country":"canada","name":"The Globe and Mail",             "lean":"Centre",                 "html":"americas_press_today.html",  "rss":"https://www.theglobeandmail.com/rss/articles/news/"},
    {"country":"canada","name":"National Post",                  "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":"https://nationalpost.com/feed/"},

    # ── Mexico ────────────────────────────────────────────────────────────────
    {"country":"mexico","name":"La Jornada",                     "lean":"Left",                   "html":"americas_press_today.html",  "rss":"https://www.jornada.com.mx/rss/edicion.xml"},
    {"country":"mexico","name":"Reforma",                        "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":""},  # no public RSS
    {"country":"mexico","name":"Milenio",                        "lean":"Pro-government",         "html":"americas_press_today.html",  "rss":"https://www.milenio.com/rss"},

    # ── Brazil ────────────────────────────────────────────────────────────────
    {"country":"brazil","name":"Folha de S.Paulo",               "lean":"Centre-left",            "html":"americas_press_today.html",  "rss":"https://feeds.folha.uol.com.br/emcimadahora/rss091.xml"},
    {"country":"brazil","name":"O Globo",                        "lean":"Centre",                 "html":"americas_press_today.html",  "rss":""},  # paywalled
    {"country":"brazil","name":"O Estado de S. Paulo",           "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":"https://www.estadao.com.br/feed/"},

    # ── Argentina ─────────────────────────────────────────────────────────────
    {"country":"argentina","name":"Página 12",                   "lean":"Left",                   "html":"americas_press_today.html",  "rss":"https://www.pagina12.com.ar/rss/portada"},
    {"country":"argentina","name":"Clarín",                      "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":""},  # paywalled
    {"country":"argentina","name":"La Nación",                   "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":"https://www.lanacion.com.ar/arc/outboundfeeds/rss/"},

    # ── Colombia ──────────────────────────────────────────────────────────────
    {"country":"colombia","name":"El Espectador",                "lean":"Left",                   "html":"americas_press_today.html",  "rss":"https://www.elespectador.com/feed/"},
    {"country":"colombia","name":"El Tiempo",                    "lean":"Centre",                 "html":"americas_press_today.html",  "rss":""},  # paywalled
    {"country":"colombia","name":"Semana",                       "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":"https://www.semana.com/rss/"},

    # ── Chile ─────────────────────────────────────────────────────────────────
    {"country":"chile","name":"El Mostrador",                    "lean":"Left",                   "html":"americas_press_today.html",  "rss":"https://www.elmostrador.cl/feed/"},
    {"country":"chile","name":"La Tercera",                      "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":""},  # paywalled
    {"country":"chile","name":"El Mercurio",                     "lean":"Right",                  "html":"americas_press_today.html",  "rss":""},  # paywalled

    # ── Peru ──────────────────────────────────────────────────────────────────
    {"country":"peru","name":"La República",                     "lean":"Left",                   "html":"americas_press_today.html",  "rss":"https://larepublica.pe/feed"},
    {"country":"peru","name":"El Comercio",                      "lean":"Centre-right",           "html":"americas_press_today.html",  "rss":""},  # paywalled
    {"country":"peru","name":"Correo",                           "lean":"Right/populist",         "html":"americas_press_today.html",  "rss":"https://diariocorreo.pe/feed/"},

    # ── Japan ─────────────────────────────────────────────────────────────────
    {"country":"japan", "name":"Asahi Shimbun",                  "lean":"Centre-left",            "html":"asia_press_today.html",      "rss":"https://www.asahi.com/rss/asahi/newsheadlines.rdf"},
    {"country":"japan", "name":"Yomiuri Shimbun",                "lean":"Centre-right",           "html":"asia_press_today.html",      "rss":""},  # paywalled
    {"country":"japan", "name":"Sankei Shimbun",                 "lean":"Right/nationalist",      "html":"asia_press_today.html",      "rss":"https://feeds.sankei.com/sankei/top-stories.rss"},

    # ── Taiwan ────────────────────────────────────────────────────────────────
    {"country":"taiwan","name":"Liberty Times (自由時報)",        "lean":"Centre-left",            "html":"asia_press_today.html",      "rss":""},  # Chinese language
    {"country":"taiwan","name":"The Reporter (報導者)",           "lean":"Independent",            "html":"asia_press_today.html",      "rss":""},  # Chinese language
    {"country":"taiwan","name":"United Daily News (聯合報)",      "lean":"Right/pro-KMT",          "html":"asia_press_today.html",      "rss":""},  # Chinese language

    # ── South Korea ───────────────────────────────────────────────────────────
    {"country":"south-korea","name":"Hankyoreh",                 "lean":"Left",                   "html":"asia_press_today.html",      "rss":"https://www.hani.co.kr/rss/"},
    {"country":"south-korea","name":"JoongAng Ilbo",             "lean":"Centre-right",           "html":"asia_press_today.html",      "rss":""},
    {"country":"south-korea","name":"Chosun Ilbo",               "lean":"Right",                  "html":"asia_press_today.html",      "rss":""},

    # Malaysia
    {"country":"malaysia","name":"Malaysiakini",                  "lean":"Left/opposition",        "html":"asia_press_today.html",      "rss":"https://www.malaysiakini.com/rss/news"},
    {"country":"malaysia","name":"The Star",                      "lean":"Centre",                 "html":"asia_press_today.html",      "rss":"https://www.thestar.com.my/rss/news/nation"},
    {"country":"malaysia","name":"New Straits Times",             "lean":"Pro-government",         "html":"asia_press_today.html",      "rss":"https://www.nst.com.my/news/feed"},

    # India
    {"country":"india", "name":"The Hindu",                       "lean":"Centre-left",            "html":"asia_press_today.html",      "rss":"https://www.thehindu.com/feeder/default.rss"},
    {"country":"india", "name":"Hindustan Times",                 "lean":"Centre",                 "html":"asia_press_today.html",      "rss":"https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml"},
    {"country":"india", "name":"Times of India",                  "lean":"Centre-right",           "html":"asia_press_today.html",      "rss":"https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"},

    # Philippines
    {"country":"philippines","name":"Rappler",                    "lean":"Left/anti-Marcos",       "html":"asia_press_today.html",      "rss":"https://www.rappler.com/feed/"},
    {"country":"philippines","name":"Philippine Daily Inquirer",  "lean":"Centre",                 "html":"asia_press_today.html",      "rss":"https://newsinfo.inquirer.net/feed"},
    {"country":"philippines","name":"Manila Bulletin",            "lean":"Centre-right",           "html":"asia_press_today.html",      "rss":"https://mb.com.ph/feed"},

    # Australia
    {"country":"australia","name":"Sydney Morning Herald",        "lean":"Centre-left",            "html":"asia_press_today.html",      "rss":"https://www.smh.com.au/rss/feed.xml"},
    {"country":"australia","name":"Australian Financial Review",  "lean":"Centre-right",           "html":"asia_press_today.html",      "rss":""},
    {"country":"australia","name":"The Australian",               "lean":"Right",                  "html":"asia_press_today.html",      "rss":""},

    # New Zealand
    {"country":"new-zealand","name":"The Spinoff",                "lean":"Centre-left",            "html":"asia_press_today.html",      "rss":"https://thespinoff.co.nz/feed/"},
    {"country":"new-zealand","name":"Stuff / Dominion Post",      "lean":"Centre",                 "html":"asia_press_today.html",      "rss":"https://www.stuff.co.nz/rss"},
    {"country":"new-zealand","name":"NZ Herald",                  "lean":"Centre-right",           "html":"asia_press_today.html",      "rss":""},

    # Israel
    {"country":"israel","name":"Haaretz",                         "lean":"Left",                   "html":"middleeast_press_today.html","rss":"https://www.haaretz.com/cmlink/1.628765"},
    {"country":"israel","name":"Yedioth Ahronoth",                "lean":"Centre",                 "html":"middleeast_press_today.html","rss":""},
    {"country":"israel","name":"Israel Hayom",                    "lean":"Right / pro-Netanyahu",  "html":"middleeast_press_today.html","rss":""},

    # Nigeria
    {"country":"nigeria","name":"The Punch",                      "lean":"Independent",            "html":"africa_press_today.html",    "rss":"https://punchng.com/feed/"},
    {"country":"nigeria","name":"Vanguard",                       "lean":"Independent",            "html":"africa_press_today.html",    "rss":"https://www.vanguardngr.com/feed/"},
    {"country":"nigeria","name":"ThisDay",                        "lean":"Centre",                 "html":"africa_press_today.html",    "rss":"https://www.thisdaylive.com/feed/"},

    # Ghana
    {"country":"ghana","name":"The Chronicle",                    "lean":"Independent",            "html":"africa_press_today.html",    "rss":""},
    {"country":"ghana","name":"Daily Graphic",                    "lean":"State-aligned",          "html":"africa_press_today.html",    "rss":""},
    {"country":"ghana","name":"Daily Guide",                      "lean":"Centre-right",           "html":"africa_press_today.html",    "rss":""},

    # Senegal
    {"country":"senegal","name":"Le Soleil",                      "lean":"Pro-gov",                "html":"africa_press_today.html",    "rss":""},
    {"country":"senegal","name":"L'Observateur",                 "lean":"Independent",            "html":"africa_press_today.html",    "rss":""},
    {"country":"senegal","name":"Sud Quotidien",                  "lean":"Progressive",            "html":"africa_press_today.html",    "rss":""},

    # South Africa
    {"country":"south-africa","name":"Mail & Guardian",           "lean":"Left",                   "html":"africa_press_today.html",    "rss":"https://mg.co.za/feed/"},
    {"country":"south-africa","name":"Daily Maverick",            "lean":"Centre-left",            "html":"africa_press_today.html",    "rss":"https://www.dailymaverick.co.za/feed/"},
    {"country":"south-africa","name":"The Citizen",               "lean":"Centre-right",           "html":"africa_press_today.html",    "rss":"https://citizen.co.za/feed/"},

    # Kenya
    {"country":"kenya","name":"Daily Nation",                     "lean":"Centre-left",            "html":"africa_press_today.html",    "rss":"https://nation.africa/kenya/feed/"},
    {"country":"kenya","name":"The Standard",                     "lean":"Centre",                 "html":"africa_press_today.html",    "rss":"https://www.standardmedia.co.ke/feed"},
    {"country":"kenya","name":"Business Daily",                   "lean":"Business/centre",        "html":"africa_press_today.html",    "rss":""},
]

MODEL     = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1400
RATE_LIMIT_SLEEP = 1.5

SYSTEM_PROMPT = """You write story summaries for World Headline, a site showing how different
newspapers cover news from their own political perspective.

Given recent headlines/summaries from one newspaper, write exactly 3 story
entries. Each must:
- Headline: punchy analytical rephrase (not verbatim copy) -- 8-12 words
- Tease: one sentence hook from this paper's editorial perspective
- Detail: 2-4 sentences with context, written from this paper's angle -- accurate, not invented

Output ONLY the 3 story HTML blocks, nothing else. Exact format:

<div class="story" onclick="toggleStory(this)"><div class="story-rank">RANK</div><div class="story-headline">HEADLINE</div><div class="story-tease">TEASE</div><div class="story-detail">DETAIL<a class="story-url" href="URL" target="_blank" onclick="event.stopPropagation()">DOMAIN</a></div></div>

RANK = "Lead" / "Second" / "Third". URL = original article link. DOMAIN = bare domain only."""

import re, sys, datetime, textwrap, time, html as _html
import feedparser, anthropic

WEEK_OF     = datetime.date.today().strftime("%-d %B %Y")
EDITION_STR = f"Edition - Week of {WEEK_OF}"

def fetch_rss(url, max_items=8):
    if not url:
        return []
    try:
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:max_items]:
            summary = re.sub(r"<[^>]+>", "", e.get("summary", e.get("description", "")) or "")
            items.append({"title": e.get("title","").strip(), "summary": summary.strip()[:400], "link": e.get("link","")})
        return [i for i in items if i["title"]]
    except Exception as ex:
        print(f"  RSS error: {ex}")
        return []

def call_claude(paper_name, lean, country, items, client):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['title']}")
        if item["summary"]:
            lines.append(f"   {item['summary']}")
        lines.append(f"   {item['link']}")
    prompt = f"Newspaper: {paper_name}\nCountry: {country}\nPolitical lean: {lean}\n\nRecent headlines:\n" + "\n".join(lines) + "\n\nWrite the 3 story HTML blocks now."
    msg = client.messages.create(model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT, messages=[{"role":"user","content":prompt}])
    return msg.content[0].text.strip()

def find_stories_block(html, paper_name):
    needle = f'>{paper_name}<'
    pos = html.find(needle)
    if pos == -1:
        encoded = _html.escape(paper_name)
        if encoded != paper_name:
            pos = html.find(f'>{encoded}<')
    if pos == -1:
        return None, None
    stories_open = html.find('<div class="stories">', pos)
    if stories_open == -1:
        return None, None
    p = stories_open + len('<div class="stories">')
    depth = 1
    end = None
    while depth > 0 and p < len(html):
        next_o = html.find('<div', p)
        next_c = html.find('</div>', p)
        if next_c == -1:
            break
        if next_o != -1 and next_o < next_c:
            depth += 1; p = next_o + 4
        else:
            depth -= 1
            if depth == 0:
                end = next_c + len('</div>')
            p = next_c + 6
    if end is None:
        return None, None
    return stories_open, end

def patch_stories(html, paper_name, new_stories_html):
    start, end = find_stories_block(html, paper_name)
    if start is None:
        return html, False
    new_block = '<div class="stories">\n            ' + new_stories_html + '\n          </div>'
    return html[:start] + new_block + html[end:], True

def update_edition_tag(html, html_file):
    return re.sub(r'<div class="edition-tag">[^<]+</div>', f'<div class="edition-tag">{EDITION_STR}</div>', html)

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set."); sys.exit(1)
    dry_run = os.environ.get("DRY_RUN","0") == "1"
    country_filter = os.environ.get("COUNTRY_FILTER","").strip().lower()
    if dry_run:
        print("DRY RUN -- no files will be written.")
    client = anthropic.Anthropic(api_key=api_key)
    papers = PAPERS
    if country_filter:
        papers = [p for p in PAPERS if p["country"] == country_filter]
        if not papers:
            print(f"ERROR: No papers for country '{country_filter}'."); sys.exit(1)
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
    loaded = {}
    for p in papers:
        path = os.path.join(repo_root, p["html"])
        if path not in loaded and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                loaded[path] = f.read()
    results = {"ok":0,"skipped":0,"failed":0}
    for paper in papers:
        print(f"\n{chr(45)*56}")
        print(f"  {paper['country'].upper()} | {paper['name']} ({paper['lean']})")
        if not paper["rss"]:
            print("  SKIP  No RSS."); results["skipped"] += 1; continue
        items = fetch_rss(paper["rss"])
        if not items:
            print("  WARN  No RSS items."); results["skipped"] += 1; continue
        print(f"  {len(items)} items fetched")
        try:
            new_stories = call_claude(paper["name"], paper["lean"], paper["country"], items, client)
            time.sleep(RATE_LIMIT_SLEEP)
        except Exception as ex:
            print(f"  ERROR Claude: {ex}"); results["failed"] += 1; continue
        path = os.path.join(repo_root, paper["html"])
        if path not in loaded:
            print(f"  ERROR file not found"); results["failed"] += 1; continue
        html, ok = patch_stories(loaded[path], paper["name"], new_stories)
        if ok:
            loaded[path] = html; print("  OK Patched."); results["ok"] += 1
        else:
            print(f"  ERROR anchor not found for {paper['name']}"); results["failed"] += 1
    for path in loaded:
        loaded[path] = update_edition_tag(loaded[path], os.path.basename(path))
    print(f"\n{chr(61)*56}\nWriting files...")
    for path, content in loaded.items():
        opens = content.count("<div"); closes = content.count("</div>")
        if opens != closes:
            print(f"  WARN DIV MISMATCH {os.path.basename(path)} ({opens} vs {closes}) -- SKIP"); continue
        if not dry_run:
            with open(path,"w",encoding="utf-8") as f:
                f.write(content)
        print(f"  {'OK' if not dry_run else 'DRY'} {os.path.basename(path)}")
    print(f"\nDone -- {results['ok']} patched / {results['skipped']} skipped / {results['failed']} failed")
    if results["failed"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
