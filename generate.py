# -*- coding: utf-8 -*-
"""
Genera el sitio estatico a partir de data.py.

Uso:
    python generate.py

Vuelve a ejecutarlo cada vez que edites data.py (nuevos enlaces de fotos/
documentos, cambios de texto, gastos, etc.).
"""
import hashlib
import io
import json
import os
import urllib.parse

import data

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- iconos --

ICON_PLANE = '<path d="M4 4v16l16-8Z"/>'
ICON_HOTEL = '<path d="M3 21h18M5 21V9l7-6 7 6v12M9 21v-6h6v6"/>'
ICON_SHIELD = '<rect x="3" y="7" width="18" height="12" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
ICON_TRANSFER = '<path d="M3 13h13l4-4M20 13a4 4 0 0 1-4 4H8l-4 4"/>'
ICON_CAMERA = '<path d="M4 8h3l2-3h6l2 3h3v11H4Z"/><circle cx="12" cy="13.5" r="3.5"/>'
ICON_DOC = '<path d="M14 3v5h5M6 3h8l5 5v13H6z"/>'
ICON_PIN = '<path d="M12 21s-7-6.1-7-11a7 7 0 0 1 14 0c0 4.9-7 11-7 11Z"/><circle cx="12" cy="10" r="2.4"/>'
ICON_LOCK = '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
ICON_LEAF = '<path d="M4 20c4-10 8-14 16-16-2 8-6 12-16 16Z"/><path d="M4 20c2-4 4-6 7-8"/>'
ICON_CALENDAR = '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'
ICON_TICKET = '<path d="M3 9a2 2 0 0 0 0 4v3a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3a2 2 0 0 0 0-4V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2Z"/><path d="M13 6v1.5M13 11v2M13 16.5V18"/>'

# Colores del sistema que se van rotando para etiquetas de documentos.
TAG_COLORS = ["hoja", "mango", "oceano", "guanacaste", "ciudad"]


def tag_color(i):
    return TAG_COLORS[i % len(TAG_COLORS)]

ACTIVITY_ICONS = {
    "building": '<rect x="6" y="8" width="5" height="13"/><rect x="13" y="4" width="5" height="17"/>',
    "boat": '<path d="M3 15h18l-2 5H5Z"/><path d="M6 15V9h9l3 6"/><path d="M9 9V4h1v5"/>',
    "tree": '<path d="M12 3 6 12h4l-5 8h14l-5-8h4Z"/><path d="M12 21v-4"/>',
    "waterfall": '<path d="M7 3v6c0 2 1 3 3 3h4c2 0 3-1 3-3V3"/><path d="M9 12v9M12 12v9M15 12v9"/>',
    "bridge": '<path d="M3 16c4-6 14-6 18 0"/><path d="M7 16v5M12 16v5M17 16v5"/>',
    "thermal": '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M4 12H2M22 12h-2M5 5l1.5 1.5M19 19l-1.5-1.5M5 19l1.5-1.5M19 5l-1.5 1.5"/>',
    "turtle-mini": '<ellipse cx="12" cy="13" rx="7" ry="8"/><path d="M12 3c-2 2-2 4 0 6M5 10c-2-1-3 1-2 3M19 10c2-1 3 1 2 3M6 19c-1 2 1 3 3 2M18 19c1 2-1 3-3 2"/>',
    "whale": '<path d="M12 4c-1 5 1 8 4 9-3 2-7 1-9-2 0 3 1 6-1 8-3-2-4-6-2-10 1-3 4-5 8-5Z"/>',
}

ACTIVITY_ICON_MAP = {
    "visita-san-jose": "building",
    "canales-tortuguero": "boat",
    "parque-nacional-tortuguero": "tree",
    "desove-tortugas": "turtle-mini",
    "catarata-la-fortuna": "waterfall",
    "puentes-colgantes": "bridge",
    "ecotermales": "thermal",
    "rio-tarcoles": "boat",
    "manglares": "boat",
    "parque-nacional-manuel-antonio": "tree",
    "ballenas-uvita": "whale",
}

DOC_ICONS = {"plane": ICON_PLANE, "hotel": ICON_HOTEL, "shield": ICON_SHIELD, "transfer": ICON_TRANSFER, "ticket": ICON_TICKET}

GRADIENTS = {
    "ciudad": "linear-gradient(135deg, var(--ciudad), #443a5e 120%)",
    "oceano": "linear-gradient(135deg, var(--oceano), #145f73 120%)",
    "guanacaste": "linear-gradient(135deg, var(--guanacaste), #b8391f 120%)",
    "mango": "linear-gradient(135deg, var(--mango), #c96a0d 120%)",
}

# --------------------------------------------------------- critters SVG --

CRITTERS = {
    "toucan": '''<svg viewBox="0 0 120 120">
      <rect x="10" y="95" width="100" height="6" rx="3" fill="#6b4226"/>
      <path d="M40 70 Q20 85 15 100 Q35 95 48 78 Z" fill="#0d1a15"/>
      <ellipse cx="60" cy="70" rx="26" ry="30" fill="#0d1a15"/>
      <ellipse cx="58" cy="79" rx="14" ry="16" fill="#fdf6e8"/>
      <ellipse cx="58" cy="95" rx="9" ry="6" fill="#e0563f"/>
      <circle cx="70" cy="42" r="18" fill="#0d1a15"/>
      <circle cx="76" cy="38" r="7" fill="#1c8ca8"/>
      <circle cx="77" cy="38" r="3.4" fill="#fdf6e8"/>
      <circle cx="78" cy="38" r="1.6" fill="#0d1a15"/>
      <path d="M85 40 C110 30 115 48 100 55 C90 59 82 52 82 46 Z" fill="#ef8a17"/>
      <path d="M85 41 C99 37 107 44 100 49" fill="none" stroke="#f5a441" stroke-width="2" stroke-linecap="round"/>
      <path d="M98 52 C102 54 104 56 100 58 C96 59 93 56 95 53 Z" fill="#e0563f"/>
      <path d="M50 98 v6 M66 98 v6" stroke="#ef8a17" stroke-width="3" stroke-linecap="round"/>
    </svg>''',
    "sloth": '''<svg viewBox="0 0 120 120">
      <rect x="0" y="10" width="120" height="7" rx="3.5" fill="#6b4226"/>
      <path d="M50 17 C46 30 40 34 34 40" stroke="#9c7a4f" stroke-width="10" stroke-linecap="round" fill="none"/>
      <path d="M70 17 C76 30 82 34 90 42" stroke="#9c7a4f" stroke-width="10" stroke-linecap="round" fill="none"/>
      <ellipse cx="60" cy="66" rx="28" ry="32" fill="#b08d5c"/>
      <ellipse cx="60" cy="60" rx="16" ry="14" fill="#e9dcbf"/>
      <path d="M50 56 q4 -6 10 -2" stroke="#4a3623" stroke-width="4" stroke-linecap="round" fill="none"/>
      <path d="M70 56 q-4 -6 -10 -2" stroke="#4a3623" stroke-width="4" stroke-linecap="round" fill="none"/>
      <circle cx="55" cy="58" r="2.4" fill="#12211c"/>
      <circle cx="65" cy="58" r="2.4" fill="#12211c"/>
      <ellipse cx="60" cy="66" rx="4" ry="3" fill="#4a3623"/>
      <path d="M56 70 q4 4 8 0" stroke="#4a3623" stroke-width="2" fill="none" stroke-linecap="round"/>
      <path d="M46 90 C40 96 38 100 40 104" stroke="#9c7a4f" stroke-width="9" stroke-linecap="round" fill="none"/>
      <path d="M74 90 C80 96 82 100 80 104" stroke="#9c7a4f" stroke-width="9" stroke-linecap="round" fill="none"/>
    </svg>''',
    "turtle": '''<svg viewBox="0 0 120 90">
      <path d="M30 30 C10 20 4 10 14 6 C26 4 34 18 36 32 Z" fill="#1c8ca8"/>
      <path d="M90 30 C110 20 116 10 106 6 C94 4 86 18 84 32 Z" fill="#1c8ca8"/>
      <path d="M30 60 C10 70 4 80 14 84 C26 86 34 72 36 58 Z" fill="#1c8ca8"/>
      <path d="M90 60 C110 70 116 80 106 84 C94 86 86 72 84 58 Z" fill="#1c8ca8"/>
      <ellipse cx="60" cy="14" rx="9" ry="10" fill="#2f9e6e"/>
      <ellipse cx="60" cy="50" rx="30" ry="34" fill="#2f9e6e"/>
      <ellipse cx="60" cy="50" rx="30" ry="34" fill="none" stroke="#1c6b49" stroke-width="2"/>
      <path d="M60 20 L60 80 M38 36 L82 36 M36 60 L84 60 M46 24 L46 78 M74 24 L74 78" stroke="#1c6b49" stroke-width="2" opacity=".6"/>
      <circle cx="55" cy="12" r="1.4" fill="#0d1a15"/>
      <circle cx="65" cy="12" r="1.4" fill="#0d1a15"/>
    </svg>''',
    "morpho": '''<svg viewBox="0 0 100 80">
      <path d="M50 40 C40 10 10 8 6 22 C2 36 24 46 50 40 Z" fill="#2e6fe0"/>
      <path d="M50 40 C60 10 90 8 94 22 C98 36 76 46 50 40 Z" fill="#2e6fe0"/>
      <path d="M50 40 C42 60 20 66 16 56 C12 48 28 42 50 40 Z" fill="#1c4fc0"/>
      <path d="M50 40 C58 60 80 66 84 56 C88 48 72 42 50 40 Z" fill="#1c4fc0"/>
      <path d="M50 10 L50 66" stroke="#0d1a15" stroke-width="3" stroke-linecap="round"/>
      <circle cx="48" cy="8" r="2" fill="#0d1a15"/>
      <circle cx="52" cy="8" r="2" fill="#0d1a15"/>
    </svg>''',
    "monarch": '''<svg viewBox="0 0 100 80">
      <path d="M50 40 C40 10 10 8 6 22 C2 36 24 46 50 40 Z" fill="#ef8a17"/>
      <path d="M50 40 C60 10 90 8 94 22 C98 36 76 46 50 40 Z" fill="#ef8a17"/>
      <path d="M50 40 C42 60 20 66 16 56 C12 48 28 42 50 40 Z" fill="#e0563f"/>
      <path d="M50 40 C58 60 80 66 84 56 C88 48 72 42 50 40 Z" fill="#e0563f"/>
      <path d="M50 10 L50 66" stroke="#12211c" stroke-width="3" stroke-linecap="round"/>
      <circle cx="48" cy="8" r="2" fill="#12211c"/>
      <circle cx="52" cy="8" r="2" fill="#12211c"/>
    </svg>''',
    "volcano": '''<svg viewBox="0 0 140 110">
      <path d="M8 100 L58 26 L82 26 L132 100 Z" fill="#3f4a3a"/>
      <path d="M58 26 L70 8 L82 26 Z" fill="#12211c"/>
      <path d="M64 17 C60 8 66 2 63 -6" stroke="#dfe6dd" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/>
      <path d="M72 17 C77 10 74 3 78 -4" stroke="#dfe6dd" stroke-width="3" fill="none" stroke-linecap="round" opacity=".55"/>
      <path d="M67 20 L57 100 L67 100 L73 30 Z" fill="#ef8a17"/>
      <path d="M75 26 L90 100 L80 100 L71 34 Z" fill="#e0563f" opacity=".9"/>
      <circle cx="70" cy="17" r="7" fill="#f5a441"/>
    </svg>''',
    "monkey": '''<svg viewBox="0 0 120 120">
      <path d="M85 90 C105 95 108 75 95 68" stroke="#3b2a1d" stroke-width="8" stroke-linecap="round" fill="none"/>
      <ellipse cx="60" cy="75" rx="24" ry="28" fill="#3b2a1d"/>
      <ellipse cx="58" cy="82" rx="13" ry="15" fill="#f2e6d0"/>
      <path d="M38 70 C28 66 22 58 24 48" stroke="#3b2a1d" stroke-width="9" stroke-linecap="round" fill="none"/>
      <rect x="8" y="42" width="30" height="6" rx="3" fill="#6b4226"/>
      <circle cx="46" cy="38" r="5" fill="#3b2a1d"/>
      <circle cx="78" cy="38" r="5" fill="#3b2a1d"/>
      <circle cx="62" cy="42" r="20" fill="#3b2a1d"/>
      <ellipse cx="62" cy="46" rx="13" ry="12" fill="#f2e6d0"/>
      <circle cx="57" cy="44" r="2.2" fill="#12211c"/>
      <circle cx="67" cy="44" r="2.2" fill="#12211c"/>
      <path d="M59 50 q3 3 6 0" stroke="#4a3623" stroke-width="2" fill="none" stroke-linecap="round"/>
    </svg>''',
    "frog": '''<svg viewBox="0 0 100 90">
      <ellipse cx="50" cy="80" rx="46" ry="8" fill="#2f9e6e" opacity=".4"/>
      <path d="M20 60 C8 62 4 74 14 80 C22 84 28 74 30 64 Z" fill="#1c3fae"/>
      <path d="M80 60 C92 62 96 74 86 80 C78 84 72 74 70 64 Z" fill="#1c3fae"/>
      <path d="M30 50 C20 48 14 54 16 62" stroke="#1c3fae" stroke-width="7" stroke-linecap="round" fill="none"/>
      <path d="M70 50 C80 48 86 54 84 62" stroke="#1c3fae" stroke-width="7" stroke-linecap="round" fill="none"/>
      <ellipse cx="50" cy="45" rx="26" ry="22" fill="#d81e3a"/>
      <circle cx="42" cy="50" r="2.6" fill="#12211c" opacity=".5"/>
      <circle cx="58" cy="52" r="2.2" fill="#12211c" opacity=".5"/>
      <circle cx="50" cy="42" r="2" fill="#12211c" opacity=".4"/>
      <circle cx="40" cy="30" r="8" fill="#d81e3a"/>
      <circle cx="60" cy="30" r="8" fill="#d81e3a"/>
      <circle cx="40" cy="30" r="4.4" fill="#12211c"/>
      <circle cx="60" cy="30" r="4.4" fill="#12211c"/>
      <circle cx="38.5" cy="28.5" r="1.3" fill="#fff"/>
      <circle cx="58.5" cy="28.5" r="1.3" fill="#fff"/>
    </svg>''',
}


def critter_div(name, extra_class=""):
    cls = "critter critter--%s" % name
    if extra_class:
        cls += " " + extra_class
    return '<div class="%s" aria-hidden="true">%s</div>' % (cls, CRITTERS[name])


# ------------------------------------------------------------- helpers --

def favicon_link():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">\U0001F99C</text></svg>'
    return '<link rel="icon" href="data:image/svg+xml,%s">' % urllib.parse.quote(svg)


def dest_by_id(dest_id):
    for d in data.DESTINATIONS:
        if d["id"] == dest_id:
            return d
    raise KeyError(dest_id)


def activities_for(dest_id):
    return [a for a in data.ACTIVITIES if a["destination_id"] == dest_id]


def nav_html(depth, active):
    """depth: 0 for root pages, 1 for pages inside destinos/ or actividades/"""
    p = "" if depth == 0 else "../"
    items = [("index", "Inicio", p + "index.html")]
    for d in data.DESTINATIONS:
        items.append((d["id"], d["name"], p + "destinos/%s.html" % d["id"]))
    items.append(("documentos", "Documentos", p + "documentos.html"))
    items.append(("gastos", "Gastos", p + "gastos.html"))

    links = []
    for key, label, href in items:
        cls = "link active" if key == active else "link"
        links.append('<a class="%s" href="%s">%s</a>' % (cls, href, label))

    return '''<nav class="topnav">
  <div class="row">
    <a class="brand" href="%(home)s"><svg class="icon" viewBox="0 0 24 24">%(leaf)s</svg>Costa Rica 2026</a>
    <button class="burger" onclick="toggleNav()" aria-label="Abrir menú">
      <svg class="icon" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    </button>
    <div class="links" id="nav-links">%(links)s</div>
  </div>
</nav>''' % {"home": p + "index.html", "leaf": ICON_LEAF, "links": "".join(links)}


def link_tile(label, url, icon, primary=False):
    cls = "link-tile primary" if primary else "link-tile"
    if url:
        return '<a class="%s" href="%s" target="_blank" rel="noopener"><svg class="icon" viewBox="0 0 24 24">%s</svg><span>%s</span></a>' % (cls, url, icon, label)
    return '<span class="link-tile empty"><svg class="icon" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg><span>%s — añádelo en data.py</span></span>' % label


def doc_tiles(docs, icon, empty_label):
    """Una lista de documentos -> una tile por documento (cada una con un color distinto
    del sistema), o un hueco discontinuo si está vacía."""
    if not docs:
        return '<span class="link-tile empty"><svg class="icon" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg><span>%s — añádelos en data.py</span></span>' % empty_label
    tiles = []
    for i, d in enumerate(docs):
        tiles.append('<a class="link-tile c-%s" href="%s" target="_blank" rel="noopener"><svg class="icon" viewBox="0 0 24 24">%s</svg><span>%s</span></a>' % (tag_color(i), d["url"], icon, d["label"]))
    return "".join(tiles)


def doc_item(item):
    icon = ICON_DOC
    docs = item.get("docs", [])
    info = item.get("info", [])

    if info:
        info_rows = "".join(
            '<div class="info-row"><span class="k">%s</span>%s</div>' % (
                r["label"],
                '<a class="v tel" href="tel:%s">%s</a>' % (r["value"].replace(" ", ""), r["value"]) if r.get("tel")
                else '<span class="v">%s</span>' % r["value"],
            )
            for r in info
        )
        links = "".join(
            '<a class="doc-link c-%s" href="%s" target="_blank" rel="noopener">%s</a>' % (tag_color(i), d["url"], d["label"])
            for i, d in enumerate(docs)
        ) if docs else '<span class="doc-link empty">Añadir documentos</span>'
        return '''<div class="doc-item doc-item--rich">
      <div class="doc-item-head"><svg class="icon" viewBox="0 0 24 24">%s</svg><div class="n"><b>%s</b><span>%s</span></div></div>
      <div class="doc-info">%s</div>
      <div class="doc-links">%s</div>
    </div>''' % (icon, item["title"], item["subtitle"], info_rows, links)

    if docs:
        links = "".join(
            '<a class="doc-link c-%s" href="%s" target="_blank" rel="noopener">%s</a>' % (tag_color(i), d["url"], d["label"])
            for i, d in enumerate(docs)
        )
        return '''<div class="doc-item">
      <svg class="icon" viewBox="0 0 24 24">%s</svg>
      <div class="n"><b>%s</b><span>%s</span></div>
      <div class="doc-links">%s</div>
    </div>''' % (icon, item["title"], item["subtitle"], links)
    return '''<span class="doc-item empty">
      <svg class="icon" viewBox="0 0 24 24">%s</svg>
      <div class="n"><b>%s</b><span>%s</span></div>
      <span class="go">Añadir</span>
    </span>''' % (icon, item["title"], item["subtitle"])


def layout(title, description, depth, active, body, hero="", extra_script=""):
    p = "" if depth == 0 else "../"
    return '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(description)s">
%(favicon)s
<link rel="stylesheet" href="%(css)s">
</head>
<body>
%(nav)s
%(hero)s
<main class="wrap">
%(body)s
</main>
<footer>
  <div class="wrap"><p>Cuaderno de viaje — Costa Rica 2026 · %(dates)s</p></div>
</footer>
<script src="%(js)s"></script>
%(extra_script)s
</body>
</html>''' % {
        "title": title,
        "description": description,
        "favicon": favicon_link(),
        "css": p + "assets/css/styles.css",
        "nav": nav_html(depth, active),
        "hero": hero,
        "body": body,
        "js": p + "assets/js/main.js",
        "extra_script": extra_script,
        "dates": data.TRIP_DATES,
    }


def write(rel_path, html):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with io.open(full, "w", encoding="utf-8") as f:
        f.write(html)
    print("  ->", rel_path)


# =========================================================== index.html ==

def build_index():
    hero = '''<header class="hero">
  %(toucan)s
  <div class="wrap">
    <p class="hero-eyebrow">Cuaderno de viaje</p>
    <h1>%(title)s</h1>
    <p class="lead">Un sitio para revivir el viaje día a día: calendario, destinos, actividades con fotos y documentos.</p>
    <div class="sticker-badge-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">%(leaf)s</svg>
      <span class="sticker-badge">&iexcl;Pura Vida!</span>
    </div>
    <div class="meta-row">
      <span class="pill"><svg class="icon" viewBox="0 0 24 24" style="width:13px;height:13px">%(cal)s</svg>%(dates)s</span>
      <span class="pill"><svg class="icon" viewBox="0 0 24 24" style="width:13px;height:13px">%(pin)s</svg>%(ndest)s destinos · %(ndays)s días</span>
    </div>
  </div>
  <svg class="ridge" viewBox="0 0 1200 90" preserveAspectRatio="none"><path d="M0 90 L0 55 C120 20 220 75 340 45 C460 15 540 70 660 40 C780 15 860 65 980 35 C1080 12 1140 55 1200 40 L1200 90 Z" fill="#0d1a15"/></svg>
</header>''' % {
        "toucan": critter_div("toucan"),
        "title": data.TRIP_TITLE,
        "leaf": ICON_LEAF,
        "cal": ICON_CALENDAR,
        "pin": ICON_PIN,
        "dates": data.TRIP_DATES,
        "ndest": len(data.DESTINATIONS),
        "ndays": len(data.DAYS),
    }

    # tarjetas de destino
    cards = []
    for d in data.DESTINATIONS:
        cards.append('''<a class="dest-card" href="destinos/%(id)s.html">
      <div class="top" style="background:%(grad)s">
        <p class="k">%(stay)s</p>
        <h3>%(name)s</h3>
      </div>
      <div class="bottom">%(subtitle)s · %(n)s %(word)s</div>
    </a>''' % {
            "id": d["id"], "grad": GRADIENTS[d["color"]], "stay": d["stays"][0]["dates"],
            "name": d["name"], "subtitle": d["subtitle"], "n": len(activities_for(d["id"])),
            "word": "actividad" if len(activities_for(d["id"])) == 1 else "actividades",
        })

    # calendario agrupado por bloques consecutivos de destino
    groups = []
    cur_dest = None
    cur_days = []
    for day in data.DAYS:
        if day["destination_id"] != cur_dest:
            if cur_days:
                groups.append((cur_dest, cur_days))
            cur_dest = day["destination_id"]
            cur_days = []
        cur_days.append(day)
    if cur_days:
        groups.append((cur_dest, cur_days))

    critter_by_dest_id = {"tortuguero": "turtle", "la-fortuna": "volcano", "manuel-antonio": "monkey"}

    tl_html = []
    for dest_id, days in groups:
        d = dest_by_id(dest_id)
        crit = critter_by_dest_id.get(dest_id)
        crit_html = critter_div(crit) if crit else ""
        cards_html = []
        for day in days:
            cards_html.append('''<div class="day-card" style="--tag:var(--%(color)s)">
        <div class="dnum">Día %(n)s · %(weekday)s %(date)s</div>
        <div class="ddate">%(headline)s</div>
        <div class="dact">%(detail)s</div>
      </div>''' % {"color": d["color"], "n": day["n"], "weekday": day["weekday"][:3],
                     "date": day["date"], "headline": day["headline"], "detail": day["detail"]})
        tl_html.append('''<div class="tl-group">
      %(crit)s
      <a class="tl-group-head" href="destinos/%(id)s.html" style="color:var(--%(color)s)">
        <span class="tag" style="background:var(--%(color)s)"></span>%(name)s<span class="dash"></span>
      </a>
      <div class="tl-days">%(cards)s</div>
    </div>''' % {"crit": crit_html, "id": dest_id, "color": d["color"], "name": d["name"], "cards": "".join(cards_html)})

    body = '''<section class="tight">
  <div class="sec-head">
    <p class="sec-eyebrow">Destinos</p>
    <h2>A dónde vamos</h2>
  </div>
  <div class="dest-grid">%(cards)s</div>
</section>
<hr class="div">
<section id="calendario">
  <div class="sec-head">
    <p class="sec-eyebrow">Itinerario</p>
    <h2>Calendario del viaje</h2>
  </div>
  <div class="timeline">%(timeline)s</div>
</section>''' % {"cards": "".join(cards), "timeline": "".join(tl_html)}

    html = layout(
        "%s — Cuaderno de viaje" % data.TRIP_TITLE,
        "Calendario e itinerario del viaje familiar a Costa Rica, %s." % data.TRIP_DATES,
        depth=0, active="index", body=body, hero=hero,
    )
    write("index.html", html)


# ========================================================= destino.html ==

def build_destinations():
    for d in data.DESTINATIONS:
        acts = activities_for(d["id"])
        crit_map = {"san-jose": "toucan", "tortuguero": "turtle", "la-fortuna": "volcano", "manuel-antonio": "monkey"}
        extra_crit_map = {"la-fortuna": "sloth", "manuel-antonio": "morpho"}

        stays_html = "".join(
            '<span class="pill" style="border-color:rgba(255,255,255,.4)">%s · %s</span>' % (s["dates"], s["hotel"])
            for s in d["stays"]
        )

        dest_hero = '''<div class="dest-hero" style="background:%(grad)s">
      %(crit1)s%(crit2)s
      <p class="k">%(subtitle)s</p>
      <h1>%(name)s</h1>
      <p class="sub">%(intro)s</p>
      <div class="stays">%(stays)s</div>
      <svg class="wave" viewBox="0 0 1200 60" preserveAspectRatio="none"><path d="M0 60V30c150-25 300 25 450 10s300-35 450-10 300 30 300 10V60Z" fill="rgba(255,255,255,0.15)"/></svg>
    </div>''' % {
            "grad": GRADIENTS[d["color"]],
            "crit1": critter_div(crit_map[d["id"]], "critter--sloth" if False else ""),
            "crit2": critter_div(extra_crit_map[d["id"]]) if d["id"] in extra_crit_map else "",
            "subtitle": d["subtitle"], "name": d["name"], "intro": d["intro"], "stays": stays_html,
        }

        act_cards = []
        for a in acts:
            icon_key = ACTIVITY_ICON_MAP.get(a["id"], "tree")
            act_cards.append('''<a class="activity-card" href="../actividades/%(id)s.html">
        <div class="activity-thumb" style="background:%(grad)s">
          <svg class="icon" viewBox="0 0 24 24" style="stroke:#fff;width:26px;height:26px">%(icon)s</svg>
        </div>
        <div class="activity-body">
          <div class="tm">%(day)s · %(time)s</div>
          <div class="t">%(title)s</div>
          <div class="d">%(desc)s</div>
        </div>
      </a>''' % {
                "id": a["id"], "grad": GRADIENTS[d["color"]], "icon": ACTIVITY_ICONS[icon_key],
                "day": a["day_label"], "time": a["time"], "title": a["title"],
                "desc": (a["description"][:90] + "…") if len(a["description"]) > 90 else a["description"],
            })

        body = '''<div class="crumb"><a href="../index.html">Inicio</a> / %(name)s</div>
%(dest_hero)s
<div class="subhead-row"><h4>Actividades</h4></div>
<div class="activity-grid">%(acts)s</div>
<div class="grid-2">
  <div>
    <div class="subhead-row"><h4>Fotos generales del destino</h4></div>
    <div class="link-row">%(photos)s</div>
  </div>
  <div>
    <div class="subhead-row"><h4>Documentación del destino</h4></div>
    <div class="link-row">%(docs)s</div>
  </div>
</div>''' % {
            "name": d["name"], "dest_hero": dest_hero, "acts": "".join(act_cards),
            "photos": link_tile("Ver fotos del destino", d["photos_url"], ICON_CAMERA, primary=True),
            "docs": doc_tiles(d["docs"], ICON_DOC, "Documentos del destino"),
        }

        html = layout(
            "%s — %s" % (d["name"], data.TRIP_TITLE),
            "%s. %s" % (d["subtitle"], d["intro"]),
            depth=1, active=d["id"], body=body,
        )
        write("destinos/%s.html" % d["id"], html)


# ======================================================== actividad.html ==

def build_activities():
    for a in data.ACTIVITIES:
        d = dest_by_id(a["destination_id"])
        body = '''<div class="crumb"><a href="../index.html">Inicio</a> / <a href="../destinos/%(did)s.html">%(dname)s</a> / %(title)s</div>
<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px; flex-wrap:wrap; margin-bottom:14px;">
  <div>
    <p style="font-family:var(--font-ui); font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--%(color)s); margin:0 0 4px;">%(dname)s · %(day)s</p>
    <h1 style="font-family:var(--font-display); font-weight:400; font-size:28px; margin:0;">%(title)s</h1>
  </div>
  <span class="pill" style="background:var(--niebla-2); color:var(--tinta); border-color:var(--line);">%(time)s</span>
</div>
<p style="font-size:15px; opacity:.85; max-width:60ch; margin:0 0 8px;">%(desc)s</p>

<div class="subhead-row"><h4>Fotos de la actividad</h4></div>
<div class="link-row">%(photos)s</div>

<div class="subhead-row"><h4>Documentación</h4></div>
<div class="link-row">%(docs)s</div>

<div class="subhead-row"><h4></h4></div>
<a class="link-tile" href="../destinos/%(did)s.html">&larr; Volver a %(dname)s</a>''' % {
            "did": d["id"], "dname": d["name"], "title": a["title"], "color": d["color"],
            "day": a["day_label"], "time": a["time"], "desc": a["description"],
            "photos": link_tile("Ver fotos de la actividad", a["photos_url"], ICON_CAMERA, primary=True),
            "docs": doc_tiles(a["docs"], ICON_DOC, "Entradas, vouchers"),
        }

        html = layout(
            "%s — %s" % (a["title"], data.TRIP_TITLE),
            "%s. %s" % (a["day_label"], a["description"]),
            depth=1, active=d["id"], body=body,
        )
        write("actividades/%s.html" % a["id"], html)


# ======================================================= documentos.html ==

def doc_category_html(title, icon_key, color, items):
    items_html = "".join(doc_item(i) for i in items)
    return '''<div class="doc-cat">
      <div class="doc-cat-head"><svg class="icon" viewBox="0 0 24 24" style="color:var(--%(color)s)">%(icon)s</svg><b>%(title)s</b></div>
      <div class="doc-list">%(items)s</div>
    </div>''' % {"color": color, "icon": DOC_ICONS[icon_key], "title": title, "items": items_html}


def build_documentos():
    # Hoteles: se toma directamente de DESTINATIONS, sin duplicar datos.
    hotel_items = []
    for d in data.DESTINATIONS:
        hotel_names = ", ".join(dict.fromkeys(s["hotel"] for s in d["stays"]))
        dates = " y ".join(s["dates"] for s in d["stays"])
        hotel_items.append({"title": hotel_names, "subtitle": "%s · %s" % (d["name"], dates), "docs": d["docs"]})

    # Excursiones: se toma directamente de ACTIVITIES, sin duplicar datos.
    excursion_items = []
    for a in data.ACTIVITIES:
        d = dest_by_id(a["destination_id"])
        excursion_items.append({"title": a["title"], "subtitle": "%s · %s" % (d["name"], a["day_label"]), "docs": a["docs"]})

    cats_html = [
        doc_category_html("Hoteles", "hotel", "hoja", hotel_items),
        doc_category_html("Transportes", "transfer", "oceano", data.TRANSPORT_DOCS),
        doc_category_html("Excursiones", "ticket", "guanacaste", excursion_items),
        doc_category_html("Varios", "shield", "ciudad", data.MISC_DOCS),
    ]

    body = '''<div class="crumb"><a href="index.html">Inicio</a> / Documentos</div>
<div class="sec-head">
  <p class="sec-eyebrow">Todo en un sitio</p>
  <h2>Documentación del viaje</h2>
  <p>Hoteles y excursiones se rellenan desde las páginas de cada destino/actividad en <code>data.py</code>; transportes y varios se editan aquí abajo. Lo que aún no tiene enlace se muestra discontinuo.</p>
</div>
%(cats)s''' % {"cats": "".join(cats_html)}

    html = layout(
        "Documentos — %s" % data.TRIP_TITLE,
        "Hoteles, transportes, excursiones y otros documentos del viaje a Costa Rica.",
        depth=0, active="documentos", body=body,
    )
    write("documentos.html", html)


# =========================================================== gastos.html ==

def build_gastos():
    pass_hash = hashlib.sha256(data.GASTOS_PASSWORD.encode("utf-8")).hexdigest()
    api_url = data.EXPENSES_API_URL

    if api_url:
        content_html = '''<div id="expense-cards" class="exp-cards"></div>
  <div class="grid-2" style="margin-top:28px;">
    <div>
      <div class="subhead-row"><h4>Gasto por categoría</h4></div>
      <div id="expense-chart" class="exp-chart-wrap"></div>
    </div>
    <div>
      <div class="subhead-row"><h4>Todos los gastos</h4></div>
      <div id="expense-list" class="exp-list"></div>
    </div>
  </div>'''
    else:
        content_html = '''<div class="callout">
      <h4>Conecta tu hoja de gastos</h4>
      <ul>
        <li>Crea una Google Sheet y, en ella, ve a <b>Extensiones → Apps Script</b>.</li>
        <li>Pega el contenido de <code>apps-script/Code.gs</code> (en este proyecto) y despliega como <b>Aplicación web</b> (Ejecutar como: Yo · Acceso: Cualquier usuario).</li>
        <li>Pega la URL que te da (termina en <code>/exec</code>) en <code>EXPENSES_API_URL</code> (data.py) y ejecuta <code>python generate.py</code> otra vez.</li>
        <li>Pasos completos en <code>GUIA.md</code>.</li>
      </ul>
    </div>'''

    body = '''<div class="crumb"><a href="index.html">Inicio</a> / Gastos</div>
<div class="sec-head">
  <p class="sec-eyebrow">Privado</p>
  <h2>Gastos del viaje</h2>
</div>

<div id="gastos-lock" class="lock-wrap">
  <div class="lock-badge"><svg class="icon" viewBox="0 0 24 24" style="stroke:var(--niebla)">%(lock_icon)s</svg></div>
  <h2 style="margin:0;">Contenido privado</h2>
  <p class="hint">Introduce la contraseña para ver los gastos.</p>
  <form id="pass-form" class="pass-form">
    <input id="gastos-pass" type="password" placeholder="Contraseña" autocomplete="off">
    <button type="submit">Entrar</button>
  </form>
  <p id="pass-error" class="pass-error">Contraseña incorrecta, inténtalo de nuevo.</p>
</div>

<div id="gastos-content">
  %(content)s
</div>

<button type="button" id="exp-add-btn" class="exp-fab" aria-label="Añadir gasto" title="Añadir gasto">
  <svg class="icon" viewBox="0 0 24 24" style="width:24px;height:24px;stroke-width:2"><path d="M12 5v14M5 12h14"/></svg>
</button>

<div id="exp-popup" class="exp-popup-overlay" onclick="if(event.target===this) closeExpensePopup()">
  <div class="exp-popup-box">
    <div class="exp-popup-head">
      <h3 id="exp-popup-title"></h3>
      <button type="button" class="exp-popup-close" onclick="closeExpensePopup()" aria-label="Cerrar">&times;</button>
    </div>
    <div id="exp-popup-list" class="exp-list"></div>
  </div>
</div>

<div id="exp-form-modal" class="exp-popup-overlay" onclick="if(event.target===this) closeExpenseForm()">
  <div class="exp-popup-box exp-form-box">
    <div class="exp-popup-head">
      <h3 id="exp-form-title">Añadir gasto</h3>
      <button type="button" class="exp-popup-close" onclick="closeExpenseForm()" aria-label="Cerrar">&times;</button>
    </div>
    <form id="exp-form" class="exp-form">
      <input type="hidden" id="exp-form-id">
      <label>Fecha <span class="req">*</span>
        <input type="date" id="exp-form-fecha" required>
      </label>
      <label>Tipo de gasto <span class="req">*</span>
        <select id="exp-form-tipo" required></select>
      </label>
      <label>Descripción
        <input type="text" id="exp-form-desc" placeholder="Ej. Cena en el mercado" maxlength="200">
      </label>
      <label>Lugar
        <select id="exp-form-lugar"></select>
      </label>
      <label>Importe (€) <span class="req">*</span>
        <input type="number" id="exp-form-importe" step="0.01" min="0.01" required>
      </label>
      <p id="exp-form-error" class="pass-error">Revisa los campos obligatorios: fecha, tipo de gasto e importe.</p>
      <div class="exp-form-actions">
        <button type="button" id="exp-form-delete" class="exp-form-delete">Eliminar</button>
        <button type="submit" class="exp-form-save">Guardar</button>
      </div>
    </form>
  </div>
</div>''' % {"lock_icon": ICON_LOCK, "content": content_html}

    expense_config = {
        "apiUrl": api_url,
        "categories": [{"label": c["label"], "color": c["color"]} for c in data.EXPENSE_CATEGORIES],
        "places": [{"label": p["label"], "color": p["color"]} for p in data.EXPENSE_PLACES],
    }

    html = layout(
        "Gastos — %s" % data.TRIP_TITLE,
        "Gastos del viaje (privado).",
        depth=0, active="gastos", body=body,
        extra_script="<script>initGastos(%s, %s);</script>" % (repr(pass_hash), json.dumps(expense_config, ensure_ascii=False)),
    )
    write("gastos.html", html)


# ================================================================ main ==

if __name__ == "__main__":
    print("Generando sitio Costa Rica 2026...")
    build_index()
    build_destinations()
    build_activities()
    build_documentos()
    build_gastos()
    print("Listo.")
