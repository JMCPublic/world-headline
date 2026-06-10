#!/usr/bin/env python3
"""
World Headline — Post-Refresh Site Validator
=============================================
Runs after refresh_stories.py to confirm the HTML files are still healthy.

Checks:
  1. DIV balance on all 6 press pages
  2. Every paper with an RSS feed still has a valid anchor in its HTML file
  3. Edition notice is present on every page

Exit code 0 = all clear.
Exit code 1 = one or more failures (GitHub Actions will mark the run red).
"""

import sys
import html as _html

# ── HTML files to validate ─────────────────────────────────────────────────

HTML_FILES = [
    "uk_press_today.html",
    "europe_press_today.html",
    "americas_press_today.html",
    "asia_press_today.html",
    "africa_press_today.html",
    "middleeast_press_today.html",
]

# ── Papers with RSS feeds (must have a valid anchor) ───────────────────────

RSS_PAPERS = [
    # UK
    ("The Guardian",                    "uk_press_today.html"),
    ("The Times",                       "uk_press_today.html"),
    ("Daily Mail",                      "uk_press_today.html"),
    # France
    ("Libération",                      "europe_press_today.html"),
    ("Le Monde",                        "europe_press_today.html"),
    ("Le Figaro",                       "europe_press_today.html"),
    # Germany
    ("Süddeutsche Zeitung",             "europe_press_today.html"),
    ("Frankfurter Allgemeine",          "europe_press_today.html"),
    ("Bild",                            "europe_press_today.html"),
    # Netherlands
    ("de Volkskrant",                   "europe_press_today.html"),
    ("NRC Handelsblad",                 "europe_press_today.html"),
    ("De Telegraaf",                    "europe_press_today.html"),
    # Ireland
    ("Irish Examiner",                  "europe_press_today.html"),
    ("The Irish Times",                 "europe_press_today.html"),
    ("Irish Independent",               "europe_press_today.html"),
    # Sweden
    ("Aftonbladet",                     "europe_press_today.html"),
    ("Dagens Nyheter",                  "europe_press_today.html"),
    ("Svenska Dagbladet",               "europe_press_today.html"),
    # Norway
    ("Aftenposten",                     "europe_press_today.html"),
    ("VG (Verdens Gang)",               "europe_press_today.html"),
    # Denmark
    ("Politiken",                       "europe_press_today.html"),
    ("Berlingske",                      "europe_press_today.html"),
    ("Jyllands-Posten",                 "europe_press_today.html"),
    # Finland
    ("Helsingin Sanomat",               "europe_press_today.html"),
    ("Kauppalehti",                     "europe_press_today.html"),
    ("Iltalehti",                       "europe_press_today.html"),
    # Italy
    ("La Repubblica",                   "europe_press_today.html"),
    ("Corriere della Sera",             "europe_press_today.html"),
    ("Il Giornale",                     "europe_press_today.html"),
    # Spain
    ("El País",                         "europe_press_today.html"),
    ("El Mundo",                        "europe_press_today.html"),
    ("ABC",                             "europe_press_today.html"),
    # Portugal
    ("Público",                         "europe_press_today.html"),
    ("Jornal de Notícias",              "europe_press_today.html"),
    ("Observador",                      "europe_press_today.html"),
    # Greece
    ("Kathimerini",                     "europe_press_today.html"),
    # Hungary
    ("Telex",                           "europe_press_today.html"),
    # Austria
    ("Der Standard",                    "europe_press_today.html"),
    # Belgium
    ("De Morgen",                       "europe_press_today.html"),
    ("Le Soir",                         "europe_press_today.html"),
    ("Het Laatste Nieuws",              "europe_press_today.html"),
    # USA
    ("The New York Times",              "americas_press_today.html"),
    ("USA Today",                       "americas_press_today.html"),
    ("Wall Street Journal",             "americas_press_today.html"),
    # Canada
    ("Toronto Star",                    "americas_press_today.html"),
    ("The Globe and Mail",              "americas_press_today.html"),
    ("National Post",                   "americas_press_today.html"),
    # Mexico
    ("La Jornada",                      "americas_press_today.html"),
    ("Milenio",                         "americas_press_today.html"),
    # Brazil
    ("Folha de S.Paulo",                "americas_press_today.html"),
    ("O Estado de S. Paulo",            "americas_press_today.html"),
    # Argentina
    ("Página 12",                       "americas_press_today.html"),
    ("La Nación",                       "americas_press_today.html"),
    # Colombia
    ("El Espectador",                   "americas_press_today.html"),
    ("Semana",                          "americas_press_today.html"),
    # Chile
    ("El Mostrador",                    "americas_press_today.html"),
    # Peru
    ("La República",                    "americas_press_today.html"),
    ("Correo",                          "americas_press_today.html"),
    # Japan
    ("Asahi Shimbun",                   "asia_press_today.html"),
    ("Sankei Shimbun",                  "asia_press_today.html"),
    # South Korea
    ("Hankyoreh",                       "asia_press_today.html"),
    # Malaysia
    ("Malaysiakini",                    "asia_press_today.html"),
    ("The Star",                        "asia_press_today.html"),
    ("New Straits Times",               "asia_press_today.html"),
    # India
    ("The Hindu",                       "asia_press_today.html"),
    ("Hindustan Times",                 "asia_press_today.html"),
    ("Times of India",                  "asia_press_today.html"),
    # Philippines
    ("Rappler",                         "asia_press_today.html"),
    ("Philippine Daily Inquirer",       "asia_press_today.html"),
    ("Manila Bulletin",                 "asia_press_today.html"),
    # Australia
    ("Sydney Morning Herald",           "asia_press_today.html"),
    # New Zealand
    ("The Spinoff",                     "asia_press_today.html"),
    ("Stuff / Dominion Post",           "asia_press_today.html"),
    # Israel
    ("Haaretz",                         "middleeast_press_today.html"),
    # Nigeria
    ("The Punch",                       "africa_press_today.html"),
    ("Vanguard",                        "africa_press_today.html"),
    ("ThisDay",                         "africa_press_today.html"),
    # South Africa
    ("Mail & Guardian",                 "africa_press_today.html"),
    ("Daily Maverick",                  "africa_press_today.html"),
    ("The Citizen",                     "africa_press_today.html"),
    # Kenya
    ("Daily Nation",                    "africa_press_today.html"),
    ("The Standard",                    "africa_press_today.html"),
    # Botswana
    ("Mmegi",                           "africa_press_today.html"),
    ("The Voice",                       "africa_press_today.html"),
    # Tanzania
    ("The Citizen Tanzania",            "africa_press_today.html"),
    ("Daily News",                      "africa_press_today.html"),
    ("The Guardian Tanzania",           "africa_press_today.html"),
    # Zimbabwe
    ("NewsDay Zimbabwe",                "africa_press_today.html"),
    ("The Herald",                      "africa_press_today.html"),
    ("The Zimbabwe Independent",        "africa_press_today.html"),
    # Lebanon
    ("Al-Akhbar",                       "middleeast_press_today.html"),
    ("L'Orient Today",                  "middleeast_press_today.html"),
    ("An-Nahar",                        "middleeast_press_today.html"),
    # Saudi Arabia
    ("Arab News",                       "middleeast_press_today.html"),
    ("Saudi Gazette",                   "middleeast_press_today.html"),
    ("Asharq Al-Awsat / الشرق الأوسط", "middleeast_press_today.html"),
    # Egypt
    ("Al-Ahram",                        "middleeast_press_today.html"),
    ("Egypt Independent",               "middleeast_press_today.html"),
    ("Mada Masr",                       "middleeast_press_today.html"),
    # Iran
    ("Iran International",              "middleeast_press_today.html"),
]


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


def main():
    failures = []

    # ── Load all HTML files ────────────────────────────────────────────────
    html_cache = {}
    for f in HTML_FILES:
        try:
            with open(f, encoding="utf-8") as fh:
                html_cache[f] = fh.read()
        except FileNotFoundError:
            print(f"  FAIL  {f} — file not found")
            failures.append(f"Missing file: {f}")
            html_cache[f] = ""

    print("\n── 1. DIV Balance ────────────────────────────────────────────────")
    for f, content in html_cache.items():
        if not content:
            continue
        opens  = content.count('<div')
        closes = content.count('</div>')
        if opens == closes:
            print(f"  OK    {f} ({opens} divs)")
        else:
            msg = f"{f} — DIV mismatch: {opens} open vs {closes} close"
            print(f"  FAIL  {msg}")
            failures.append(msg)

    print("\n── 2. Paper Anchor Audit ─────────────────────────────────────────")
    ok_count = 0
    for paper_name, html_file in RSS_PAPERS:
        content = html_cache.get(html_file, "")
        start, end = find_stories_block(content, paper_name)
        if start is not None:
            ok_count += 1
        else:
            msg = f"{paper_name} — anchor not found in {html_file}"
            print(f"  FAIL  {msg}")
            failures.append(msg)
    print(f"  {ok_count}/{len(RSS_PAPERS)} paper anchors OK")

    print("\n── 3. Edition Notice Present ─────────────────────────────────────")
    for f, content in html_cache.items():
        if not content:
            continue
        if 'pageEditionNotice' in content or 'page-edition-notice' in content:
            print(f"  OK    {f}")
        else:
            msg = f"{f} — edition notice element missing"
            print(f"  WARN  {msg}")
            # Not a hard failure, just a warning

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    if not failures:
        print(f"✅  ALL CHECKS PASSED")
        print(f"{'='*50}\n")
        sys.exit(0)
    else:
        print(f"❌  {len(failures)} CHECK(S) FAILED:")
        for f in failures:
            print(f"     • {f}")
        print(f"{'='*50}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
