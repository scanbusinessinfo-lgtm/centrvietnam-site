# Пересборка centrvietnam.ru: дизайн из сохранённых страниц (site/), данные из Supabase.
# python3 -I gen.py <site_dir> <tours.json> <banners.json> <out_dir>
import json, re, os, sys, shutil, html, urllib.parse, datetime

SRC, TOURS, BANNERS, OUT = sys.argv[1:5]
URL = 'https://centrvietnam.ru'
TODAY = datetime.date.today().isoformat()
WA = 'https://wa.me/79226416247'
TG = 'https://t.me/Ilya_centrr_tourism_NhaTrang'
CHANNEL = 'https://t.me/center_tourism_NhaTrang'
PIXEL = '1110705904663945'
ELFSIGHT = 'c7368daf-dcfd-4d84-9f0b-4b3c8d450268'
CATS = {'sea': ('Море и острова', 'morskie'), 'nature': ('Горы и природа', 'priroda'), 'kids': ('С детьми', 's-detmi'),
        'active': ('Активный отдых', 'aktivnye'), 'city': ('Города и культура', 'goroda'), 'multi': ('Туры на 2–3 дня', 'na-2-3-dnya')}
FAMILY = {'dalat': ['dalat-new', 'dalat-super', 'dalat-the-best', 'dalat-all-in', 'dalat-2-dnya'],
          'danang': ['danang-1-den'], 'saigon': ['saigon-1-den'], 'atv-zipline': ['atv', 'zipline'],
          'doi-dep': ['doi-dep-vecher'], 'ba-ho-zoclet': ['zoclet-aquapark'], 'south-islands': ['snorkeling', 'diving']}
PARENT = {k: p for p, ks in FAMILY.items() for k in ks}

E = lambda s: html.escape(str(s or ''), quote=True)
tours = [t for t in json.load(open(TOURS)) if t.get('published')]
tours.sort(key=lambda t: (t.get('sort') or 99, 0 if t['slug'] in FAMILY else 1, t['slug']))
BY = {t['slug']: t for t in tours}
banners = [b for b in json.load(open(BANNERS)) if b.get('active')]
N = len(tours)

def read(p): return open(os.path.join(SRC, p), encoding='utf-8').read()
def write(p, s):
    fp = os.path.join(OUT, p); os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(s)

shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(SRC, OUT, ignore=shutil.ignore_patterns('.git'))

# ---------- общие куски из шаблона ----------
TPL = read('dalat/index.html')
SVG = {k: re.search(p, TPL, re.S).group(0) for k, p in {
    'cal': r'<svg[^>]*><rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    'clock': r'<svg[^>]*><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    'check': r'<svg[^>]*><path d="M5 12.5l4.5 4.5L19 7"/></svg>',
    'wa': r'<svg[^>]*><path d="M3 21l1\.6-4\.6A9.*?</svg>',
    'tg': r'<svg[^>]*><path d="M21 4L3 11l6 2 2 6 3-4 5 4 2-15z"/>.*?</svg>',
}.items()}
FACTS_SVG = re.findall(r'<div class="fact">(<svg.*?</svg>)', TPL, re.S)  # цена, длительность, время, гид, трансфер
LEAD = re.search(r'<section class="section" id="lead">.*?</form>\s*</div></div></section>', read('ekskursii/morskie/index.html'), re.S).group(0)
ORG = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', TPL, re.S).group(1))['@graph'][0]

EXTRA_CSS = """
.desc h2,.gal h2,.kids h2{margin:0 0 14px}
.desc-t{background:#fff;border:1px solid #e3edf0;border-radius:var(--r,18px);padding:26px 28px;font-size:16px;line-height:1.7;color:var(--ink,#0d2b33);overflow-wrap:anywhere}
.desc-t p{margin:0 0 14px}.desc-t p:last-child{margin:0}
.memo .desc-t{background:#fff8ec;border-color:#f3dfb8}
.tour-main>section+section{margin-top:34px}
.gal-g{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.gal-g a{display:block;border-radius:14px;overflow:hidden;aspect-ratio:4/3;background:#e9f1f2}
.gal-g a:first-child{grid-column:span 2;grid-row:span 2;aspect-ratio:auto}
.gal-g img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s}
.gal-g a:hover img{transform:scale(1.04)}
.tour-main .kids .cards.c2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.reviews-w{min-height:320px;background:#fff;border-radius:var(--r-lg,24px);box-shadow:var(--shadow-sm,0 4px 18px rgba(6,57,47,.08));padding:18px;overflow:hidden}
.tgc{display:flex;gap:22px;align-items:center;justify-content:space-between;flex-wrap:wrap;background:linear-gradient(135deg,#0b5245,#0f86b0);color:#fff;border-radius:var(--r-lg,24px);padding:30px 34px}
.tgc h2{color:#fff;margin:0 0 6px}.tgc p{margin:0;opacity:.9;max-width:620px}
.tgc .btn{background:#fff;color:#0b5245}
.card-media.noimg{display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0b5245,#0f86b0);aspect-ratio:4/3}
.card-media.noimg b{color:#fff;font-size:20px;padding:0 18px;text-align:center}
@media (max-width:760px){.desc-t{padding:18px;font-size:15px}.gal-g{grid-template-columns:repeat(2,1fr)}.tour-main .kids .cards.c2{grid-template-columns:1fr}.reviews-w{padding:8px;min-height:260px}.tgc{padding:22px}}
"""
PIXEL_HEAD = f"""<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{PIXEL}');fbq('track','PageView');__VC__</script>
<noscript><img height="1" width="1" style="display:none" alt="" src="https://www.facebook.com/tr?id={PIXEL}&ev=PageView&noscript=1"></noscript>"""

def num(t): return float(t['price_from']) if t.get('price_from') is not None else 0
def is_req(t): return not t.get('price_from') and 'запрос' in (t.get('price_label') or '').lower()
def price_b(t): return E(t.get('price_label') or 'по запросу')
def img(t): return t.get('image') or (t.get('gallery') or [{}])[0].get('src')

def card(t, extra=''):
    cats = ' '.join(t.get('categories') or [])
    im = img(t)
    media = (f'<a class="card-media" href="/{t["slug"]}" tabindex="-1" aria-hidden="true"><img src="{E(im)}" alt="{E(t["title"])}" loading="lazy" decoding="async" width="600" height="450">'
             if im else f'<a class="card-media noimg" href="/{t["slug"]}" tabindex="-1" aria-hidden="true"><b>{E(t["title"])}</b>')
    media += (f'<span class="tag">{E(t["badge"])}</span>' if t.get('badge') else '') + '</a>'
    pr = ('<div class="price"><b style="font-size:16px">Цена по запросу</b></div>' if is_req(t)
          else f'<div class="price"><small>от</small><b>{price_b(t).replace("от ", "")}</b></div>')
    return f'''<article class="card rv{extra}" data-cats="{E(cats)}" data-price="{int(num(t))}">
  {media}
  <div class="card-b">
    <h3><a href="/{t["slug"]}">{E(t["title"])}</a></h3>
    <div class="meta"><span>{SVG["cal"]}{E(t.get("duration"))}</span><span>{SVG["clock"]}{E(t.get("time"))}</span></div>
    <p>{E(t.get("short"))}</p>
    <div class="card-f">{pr}<a class="btn btn-primary" href="/{t["slug"]}">Подробнее</a></div>
  </div>
</article>'''

def row(t):
    hl = ', '.join(x if isinstance(x, str) else x.get('title', '') for x in (t.get('highlights') or [])[:4]) or E(t.get('short'))[:110]
    return (f'<tr data-cats="{E(" ".join(t.get("categories") or []))}" data-price="{int(num(t))}"><td><a href="/{t["slug"]}">{E(t["title"])}</a></td>'
            f'<td>{price_b(t)}</td><td>{E(t.get("duration"))}</td><td>{E(t.get("time"))}</td><td>{E(hl)}</td><td>{E(t.get("audience"))}</td></tr>')

def desc_html(s):
    s = str(s or '').replace('\r', '').strip()
    blocks = re.split(r'\n\s*\n', s)
    out = []
    for b in blocks:
        lines = [E(l.rstrip()) for l in b.split('\n')]
        lines = [re.sub(r'(https?://[^\s<]+)', r'<a href="\1" rel="noopener">\1</a>', l) for l in lines]
        out.append('<p>' + '<br>'.join(lines) + '</p>')
    return ''.join(out)

def wa_link(title): return WA + '?text=' + urllib.parse.quote(f'Здравствуйте! Хочу забронировать экскурсию «{title}».')

def reviews_block(title='Что говорят туристы', eyebrow='Отзывы в Google'):
    return (f'<section class="section" style="padding-top:0"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">{eyebrow}</span><h2>{title}</h2></div>'
            f'<a class="link-arrow" href="/otzyvy">Все отзывы</a></div><div class="reviews-w" id="reviews"><div class="elfsight-app-{ELFSIGHT}" data-elfsight-app-lazy></div></div></div></section>')

def channel_block():
    return (f'<section class="section-tight"><div class="wrap"><div class="tgc rv"><div><span class="eyebrow" style="color:#bfe9dc">Наш Telegram-канал</span><h2>Акции, новые экскурсии и советы по Нячангу</h2>'
            f'<p>Подписывайтесь на канал Центра Туризма — первыми узнавайте о скидках и свободных местах.</p></div>'
            f'<a class="btn" href="{CHANNEL}" rel="noopener" data-ev="channel_click">{SVG["tg"]}Подписаться на канал</a></div></div></section>')

def lead_block(tour=''):
    return LEAD.replace('<input type="hidden" name="tour" value="">', f'<input type="hidden" name="tour" value="{E(tour)}">')

# ---------- head ----------
def build_head(page, title, desc, path, image, graph, md=None, vc=''):
    h = page[:page.find('<body')]
    canon = URL + (path if path != '/' else '')
    h = re.sub(r'<title>.*?</title>', f'<title>{E(title)}</title>', h, 1, re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', h, 1)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canon}">', h, 1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{E(title)}">', h, 1)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{E(desc)}">', h, 1)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canon}">', h, 1)
    if image: h = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{E(image)}">', h, 1)
    if md: h = re.sub(r'<link rel="alternate" type="text/markdown" href="[^"]*"', f'<link rel="alternate" type="text/markdown" href="{md}"', h, 1)
    else: h = re.sub(r'<link rel="alternate" type="text/markdown"[^>]*>\n?', '', h, 1)
    if graph is not None:
        h = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>', h, 1, re.S)
    return h

def finish(html_):
    """Общая доводка любой страницы: CSS, пиксель, абсолютные пути, счётчики."""
    if '/* restored-2026-11 */' not in html_:
        html_ = html_.replace('</style>', '/* restored-2026-11 */' + EXTRA_CSS + '</style>', 1)
    if 'fbevents.js' not in html_:
        html_ = html_.replace('</head>', PIXEL_HEAD + '\n</head>', 1)
    html_ = html_.replace('__VC__', '')
    html_ = re.sub(r"url\('(?:\.\./)+img/", "url('/img/", html_)
    html_ = re.sub(r'content="(?:\.\./)+img/', f'content="{URL}/img/', html_)
    html_ = re.sub(r'"image":"(?:\.\./)+img/', f'"image":"{URL}/img/', html_)
    if 'elfsight-app-' in html_ and 'elfsightcdn.com/platform.js' not in html_:
        html_ = html_.replace('</body>', '<script src="https://elfsightcdn.com/platform.js" async></script>\n</body>', 1)
    # меню: пункт «Отзывы»
    html_ = html_.replace('<li><a href="/faq">Вопросы</a></li>', '<li><a href="/otzyvy">Отзывы</a></li><li><a href="/faq">Вопросы</a></li>') if '/otzyvy">Отзывы' not in html_ else html_
    return html_

def body_tail(page):
    i = page.find('<footer'); return page[i:]

def body_head(page):
    i = page.find('<body'); j = page.find('<main id="main">'); return page[i:j]

# ---------- страница тура ----------
def tour_page(t):
    slug, title = t['slug'], t['title']
    im = img(t) or '/img/59deb966a64a.jpg'
    cat = (t.get('categories') or ['sea'])[0]
    catname, catslug = CATS.get(cat, CATS['sea'])
    crumbs = f'<ol class="crumbs"><li><a href="/">Главная</a></li><li><a href="/ekskursii-nyachang-ceny">Экскурсии</a></li>'
    if slug in PARENT: crumbs += f'<li><a href="/{PARENT[slug]}">{E(BY[PARENT[slug]]["title"])}</a></li>'
    else: crumbs += f'<li><a href="/ekskursii/{catslug}">{catname}</a></li>'
    crumbs += f'<li aria-current="page">{E(title)}</li></ol>'
    facts = [('Цена', t.get('price_label') or 'по запросу'), ('Длительность', t.get('duration')), ('Время', t.get('time')), ('Гид', 'Русскоязычный'), ('Трансфер', 'От отеля')]
    facts_html = ''.join(f'<div class="fact">{FACTS_SVG[i]}<div><small>{k}</small><b>{E(v)}</b></div></div>' for i, (k, v) in enumerate(facts) if v)
    gal = t.get('gallery') or []
    gal_html = ('<section class="gal"><h2>Фото экскурсии</h2><div class="gal-g">' + ''.join(
        f'<a href="{E(g["src"])}" target="_blank" rel="noopener"><img src="{E(g["src"])}" alt="{E(g.get("alt") or title)}" loading="lazy" decoding="async"></a>' for g in gal[:12]) + '</div></section>') if gal else ''
    memo = f'<section class="desc memo"><h2>Памятка туристу</h2><div class="desc-t">{desc_html(t["memo"])}</div></section>' if t.get('memo') else ''
    kids = [BY[k] for k in FAMILY.get(slug, []) if k in BY]
    if slug in PARENT:
        p = PARENT[slug]; kids = [BY[p]] + [BY[k] for k in FAMILY[p] if k in BY and k != slug]
    kids_html = (f'<section class="kids"><h2>{"Выберите программу" if slug in FAMILY and slug == "dalat" else "Другие программы"}</h2><div class="cards c2">' + ''.join(card(k) for k in kids) + '</div></section>') if kids else ''
    if t.get('description'):
        main = f'<section class="desc"><h2>Описание экскурсии</h2><div class="desc-t">{desc_html(t["description"])}</div></section>{memo}{kids_html}{gal_html}'
    else:
        parts = []
        if t.get('short'): parts.append(f'<section class="tldr"><b class="k">Коротко об экскурсии</b><p>{E(t["short"])}</p></section>')
        if t.get('program'):
            parts.append('<section><h2>Программа экскурсии</h2><ol class="timeline">' + ''.join(
                f'<li data-n="{i+1}">' + (f'<span class="t">{E(p.get("time"))}</span>' if p.get('time') else '') + f'<b>{E(p.get("title"))}</b>' + (f'<p>{E(p.get("text"))}</p>' if p.get('text') else '') + '</li>'
                for i, p in enumerate(t['program'])) + '</ol></section>')
        if t.get('included'):
            parts.append('<section><h2>Что включено в стоимость</h2><div class="hl">' + ''.join(f'<span>{SVG["check"]}{E(x)}</span>' for x in t['included']) + '</div></section>')
        if t.get('excluded'):
            parts.append('<section><h2>Оплачивается отдельно</h2><p>' + E('; '.join(t['excluded'])) + '.</p></section>')
        main = ''.join(parts) + memo + kids_html + gal_html
    faq = t.get('faq') or []
    faq_html = ('<section class="section"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Вопрос — ответ</span>'
                f'<h2>Вопросы об экскурсии «{E(title)}»</h2></div></div><div class="faq">' + ''.join(
                    f'<details{" open" if i == 0 else ""}><summary>{E(q.get("q"))}</summary><div>{E(q.get("a"))}</div></details>' for i, q in enumerate(faq)) + '</div></div></section>') if faq else ''
    rel = [x for x in tours if x['slug'] != slug and x['slug'] not in [k['slug'] for k in kids] and cat in (x.get('categories') or []) and x['slug'] not in PARENT][:3]
    rel_html = ('<section class="section" style="padding-top:0"><div class="wrap"><div class="sec-head"><div><span class="eyebrow">Похожие программы</span><h2>Вам также понравится</h2></div></div><div class="cards c3">'
                + ''.join(card(x) for x in rel) + '</div></div></section>') if rel else ''
    book = f'''<aside class="book" aria-label="Бронирование">
      <div class="price"><small>Стоимость с человека</small><b{' style="font-size:24px"' if is_req(t) else ''}>{price_b(t)}</b></div>
      <a class="btn btn-jade" href="{E(wa_link(title))}" data-ev="book_click" data-ch="whatsapp">{SVG["wa"]}Забронировать в WhatsApp</a>
      <a class="btn btn-line" href="{TG}" data-ev="book_click" data-ch="telegram">{SVG["tg"]}Написать в Telegram</a>
      <a class="btn btn-line" href="#lead">Оставить заявку</a>
      <hr>
      <ul><li>{SVG["check"]}Ответ за 15 минут, ежедневно 08:00–21:00</li><li>{SVG["check"]}Трансфер от вашего отеля</li><li>{SVG["check"]}Оплата в офисе или по договорённости</li></ul>
    </aside>'''
    body = f'''<main id="main">

<section class="page-hero">
  <div class="hero-media"><img src="{E(im)}" alt="{E(title)}" fetchpriority="high" decoding="async" width="1600" height="1200"></div>
  <div class="wrap">
    {crumbs}
    {f'<span class="tag alt">{E(t["badge"])}</span>' if t.get("badge") else ''}
    <h1>{E(title)}</h1>
    <p class="phl">{E(t.get("short"))}</p>
  </div>
</section>
<div class="wrap">
  <div class="facts">{facts_html}</div>
  <div class="tour-g">
    <div class="tour-main">
      {main}
      <p class="updated">Цены и программа обновлены {datetime.date.fromisoformat(t["updated_at"][:10]).strftime("%d.%m.%Y")}. Порядок локаций может меняться из-за погоды — гид предупредит заранее.</p>
    </div>
    {book}
  </div>
</div>
{faq_html}{reviews_block()}{channel_block()}{rel_html}{lead_block(title)}
</main>
'''
    offer = {'@type': 'Offer', 'priceCurrency': 'USD', 'availability': 'https://schema.org/InStock', 'url': f'{URL}/{slug}'}
    if t.get('price_from'): offer['price'] = str(t['price_from']).rstrip('0').rstrip('.') if '.' in str(t['price_from']) else str(t['price_from'])
    trip = {'@type': 'TouristTrip', '@id': f'{URL}/{slug}#trip', 'name': title, 'description': t.get('short') or title, 'url': f'{URL}/{slug}',
            'image': [im if im.startswith('http') else URL + im] + [g['src'] for g in gal[:4]], 'inLanguage': 'ru', 'provider': {'@id': URL + '/#org'}}
    if t.get('price_from'): trip['offers'] = offer
    if t.get('audience'): trip['touristType'] = t['audience']
    crumbs_ld = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': URL},
        {'@type': 'ListItem', 'position': 2, 'name': 'Экскурсии', 'item': URL + '/ekskursii-nyachang-ceny'},
        {'@type': 'ListItem', 'position': 3, 'name': title, 'item': f'{URL}/{slug}'}]}
    graph = [ORG, trip, crumbs_ld]
    if faq: graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q.get('q'), 'acceptedAnswer': {'@type': 'Answer', 'text': q.get('a')}} for q in faq]})
    pr = t.get('price_label') or 'цена по запросу'
    seo_t = t.get('seo_title') or (f'{title}: цена {pr}, программа 2026' if not is_req(t) else f'{title} — экскурсия из Нячанга 2026')
    seo_d = t.get('seo_description') or f'{t.get("short") or title} {t.get("duration") or ""}, {t.get("time") or ""}. Русскоязычный гид, трансфер от отеля.'.replace(' ,', ',')
    head = build_head(TPL, seo_t, seo_d[:300], f'/{slug}', im if im.startswith('http') else URL + im, graph, md=f'/{slug}.md')
    head = head.replace('</head>', '', 1)
    page = head + PIXEL_HEAD.replace('__VC__', f"fbq('track','ViewContent',{{content_ids:['{slug}'],content_type:'product'}});") + '\n</head>\n' + body_head(TPL) + body + body_tail(TPL)
    page = re.sub(r'<div class="mbar">.*?</div></div>|<div class="mbar">.*?</a></div>', '', page, 1, re.S)
    mbar = f'<div class="mbar"><div class="price"><small>с человека</small><b{' style="font-size:15px"' if is_req(t) else ''}>{price_b(t)}</b></div><a class="btn btn-jade" href="{E(wa_link(title))}" data-ev="book_click" data-ch="whatsapp">{SVG["wa"]}Забронировать</a></div>'
    page = page.replace('<script>window.CT=', mbar + '\n<script>window.CT=', 1)
    return finish(page)

def tour_md(t):
    s = f"# {t['title']}\n\n- Цена: {t.get('price_label') or 'по запросу'} (USD с человека)\n- Длительность: {t.get('duration')}\n- Время: {t.get('time')}\n- Гид: русскоязычный\n- Страница: {URL}/{t['slug']}\n\n"
    s += (str(t.get('description') or t.get('short') or '').strip()) + '\n'
    if t.get('memo'): s += '\n## Памятка туристу\n\n' + str(t['memo']).strip() + '\n'
    if t.get('gallery'): s += '\n## Фото\n' + '\n'.join(f"![{g.get('alt') or t['title']}]({g['src']})" for g in t['gallery']) + '\n'
    s += f"\nБронирование: WhatsApp +7 922 641-62-47 ({WA}), Telegram @Ilya_centrr_tourism_NhaTrang, ежедневно 08:00–21:00. Обновлено: {TODAY}.\n"
    return s

# ---------- списки ----------
def replace_cards(page, items):
    return re.sub(r'(<div class="cards">).*?(</div>\s*</div></section>)', lambda m: m.group(1) + ''.join(card(t) for t in items) + m.group(2), page, 1, re.S)
def replace_rows(page, items):
    return re.sub(r'(<tbody>).*?(</tbody>)', lambda m: m.group(1) + '\n  ' + ''.join(row(t) for t in items) + '\n  ' + m.group(2), page, 1, re.S)
def by_price(items): return sorted(items, key=lambda t: (is_req(t), num(t) or 9999, t['slug']))

listed = by_price(tours)
p = read('ekskursii-nyachang-ceny/index.html')
p = replace_cards(p, listed); p = replace_rows(p, listed)
p = re.sub(r'<span id="cat-count">\d+</span>', f'<span id="cat-count">{N}</span>', p)
p = re.sub(r'проводит \d+ экскурсий', f'проводит {N} экскурсий', p)
p = re.sub(r'(<script type="application/ld\+json">).*?(</script>)', lambda m: m.group(1) + json.dumps({'@context': 'https://schema.org', '@graph': [ORG, {'@type': 'ItemList', 'name': 'Экскурсии из Нячанга', 'numberOfItems': N, 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{URL}/{t["slug"]}', 'name': t['title']} for i, t in enumerate(listed)]}]}, ensure_ascii=False) + m.group(2), p, 1, re.S)
write('ekskursii-nyachang-ceny/index.html', finish(p))

for cat, (name, cslug) in CATS.items():
    items = [t for t in listed if cat in (t.get('categories') or [])]
    p = read(f'ekskursii/{cslug}/index.html')
    p = replace_cards(p, items); p = replace_rows(p, items)
    p = re.sub(r'<span id="cat-count">\d+</span>', f'<span id="cat-count">{len(items)}</span>', p)
    mn = min([num(t) for t in items if num(t)] or [0])
    p = re.sub(r'\d+ программ(ы)? от \$\d+', f'{len(items)} программ от ${int(mn)}', p)
    write(f'ekskursii/{cslug}/index.html', finish(p))

# главная
p = read('index.html')
feat = [t for t in tours if t.get('featured')]
feat += [t for t in tours if t not in feat and t['slug'] not in PARENT and img(t)][:8 - len(feat)]
p = replace_cards(p, feat[:8])
p = re.sub(r'\b20 программ на 2026 год', f'{N} программ на 2026 год', p)
p = re.sub(r'<b id="pk-n">\d+</b>', f'<b id="pk-n">{N}</b>', p)
p = re.sub(r'(<div class="stat">.*?<b>)20(</b><span>экскурсий)', rf'\g<1>{N}\2', p, 1, re.S)
p = p.replace('Все 20 программ', f'Все {N} программ')
for cat, (name, cslug) in CATS.items():
    items = [t for t in tours if cat in (t.get('categories') or [])]
    mn = min([num(t) for t in items if num(t)] or [0])
    p = re.sub(rf'(href="/ekskursii/{cslug}">.*?<small>)\d+ программ · от \$\d+', rf'\g<1>{len(items)} программ · от ${int(mn)}', p, 1, re.S)
# индекс для подбора
idx = [{'s': t['slug'], 'c': t.get('categories') or [], 'p': int(num(t)) or 999} for t in tours]
p = re.sub(r'(<script type="application/json" id="tours-index">).*?(</script>)', lambda m: m.group(1) + json.dumps(idx, ensure_ascii=False) + m.group(2), p, 1, re.S)
# баннеры
if banners:
    def promo(b):
        return (f'<article class="promo" data-theme="{E(b.get("theme"))}">' + (f'<img src="{E(b["image"])}" alt="" loading="lazy" decoding="async" width="1200" height="900">' if b.get('image') else '')
                + '<div class="promo-body">' + (f'<span class="promo-badge">{E(b["badge"])}</span>' if b.get('badge') else '') + f'<h3>{E(b["title"])}</h3>'
                + (f'<p>{E(b["subtitle"])}</p>' if b.get('subtitle') else '') + (f'<a class="btn btn-jade" href="{E(b["link"])}">{E(b.get("cta") or "Подробнее")}</a>' if b.get('link') else '') + '</div></article>')
    hb = sorted([b for b in banners if b.get('placement') == 'hero'], key=lambda b: b.get('sort') or 0)
    p = re.sub(r'(<div class="promo-track">).*?(</div>\s*<div class="promo-nav">)', lambda m: m.group(1) + ''.join(promo(b) for b in hb) + m.group(2), p, 1, re.S)
    p = re.sub(r'data-sig="[^"]*"', 'data-sig="' + '|'.join(b['id'] + b['updated_at'] for b in hb) + '"', p, 1)
# отзывы и канал на главной перед формой
p = p.replace('<section class="section" id="lead">', reviews_block() + channel_block() + '<section class="section" id="lead">', 1)
write('index.html', finish(p))

# прочие статичные страницы — общая доводка
for f in ['akcii/index.html', 'faq/index.html', 'gidy-vietnam-nhatrang/index.html', 'kontakty/index.html', '404.html']:
    write(f, finish(read(f)))

# страница «Отзывы»
k = read('kontakty/index.html')
ob = (f'<main id="main">\n<section class="page-hero"><div class="hero-media"></div><div class="wrap"><ol class="crumbs"><li><a href="/">Главная</a></li><li aria-current="page">Отзывы</li></ol>'
      f'<h1>Отзывы туристов</h1><p class="phl">Что говорят гости Центра Туризма об экскурсиях из Нячанга. Отзывы подгружаются из Google Карт.</p></div></section>'
      + reviews_block('Отзывы с Google Карт', 'Реальные отзывы') + channel_block() + lead_block() + '\n</main>\n')
kh = build_head(k, 'Отзывы об экскурсиях Центра Туризма в Нячанге', 'Отзывы туристов об экскурсиях Центра Туризма в Нячанге: Далат, острова, Фанранг, Дананг и другие туры с русскими гидами.', '/otzyvy', None, [ORG])
write('otzyvy/index.html', finish(kh + body_head(k) + ob + body_tail(k)))

# страницы туров
for t in tours:
    write(f'{t["slug"]}/index.html', tour_page(t))
    write(f'{t["slug"]}.md', tour_md(t))

# tours.json, sitemap, llms
json.dump([{'slug': t['slug'], 'url': f'{URL}/{t["slug"]}', 'title': t['title'], 'price': t.get('price_label'), 'price_from_usd': num(t) or None,
            'duration': t.get('duration'), 'time': t.get('time'), 'categories': t.get('categories'), 'summary': t.get('short'), 'image': img(t), 'updated': t['updated_at'][:10]} for t in tours],
          open(os.path.join(OUT, 'tours.json'), 'w'), ensure_ascii=False, indent=1)
urls = [('', '1.0'), ('/ekskursii-nyachang-ceny', '0.9')] + [(f'/{t["slug"]}', '0.8') for t in tours] + [(f'/ekskursii/{c[1]}', '0.7') for c in CATS.values()] + \
       [('/akcii', '0.6'), ('/otzyvy', '0.6'), ('/gidy-vietnam-nhatrang', '0.5'), ('/faq', '0.6'), ('/kontakty', '0.6')]
open(os.path.join(OUT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'<url><loc>{URL}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n' for u, pr in urls) + '</urlset>\n')
llms = read('llms.txt')
llms = re.sub(r'## Экскурсии\n.*?\n\n## ', '## Экскурсии\n' + ''.join(f"- [{t['title']}]({URL}/{t['slug']}.md): {t.get('price_label') or 'цена по запросу'}, {t.get('duration')}, {t.get('time')}. {t.get('short') or ''}\n" for t in tours) + '\n## ', llms, 1, re.S)
llms = re.sub(r'Данные обновлены: [\d-]+', f'Данные обновлены: {TODAY}', llms)
open(os.path.join(OUT, 'llms.txt'), 'w').write(llms)
open(os.path.join(OUT, 'llms-full.txt'), 'w').write(llms + '\n\n' + '\n\n---\n\n'.join(tour_md(t) for t in tours))
# старые md без тура убираем
for f in os.listdir(OUT):
    if f.endswith('.md') and f != 'index.md' and f[:-3] not in BY and f[:-3] != 'ekskursii-nyachang-ceny': os.remove(os.path.join(OUT, f))
print('tours', N, 'ok')
