/* Центр Туризма — client script (no dependencies, ~4 KB) */
(() => {
  const C = window.CT || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];


  // статистика: события в centr_site_events (анонимно) + события Meta Pixel
  const uid = k => { try { let v = (k === 'vid' ? localStorage : sessionStorage).getItem('ct_' + k); if (!v) { v = Math.random().toString(36).slice(2, 12) + Date.now().toString(36); (k === 'vid' ? localStorage : sessionStorage).setItem('ct_' + k, v); } return v; } catch (e) { return ''; } };
  const qs = new URLSearchParams(location.search);
  const ref = (() => { try { return document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) { return ''; } })();
  const source = (qs.get('utm_source') || (ref && ref !== location.hostname ? ref : 'direct')).slice(0, 80);
  const device = /iPad|Tablet/i.test(navigator.userAgent) ? 'tablet' : (/Mobi|Android|iPhone/i.test(navigator.userAgent) ? 'mobile' : 'desktop');
  const tourSlug = (document.querySelector('link[rel=canonical]')?.href || '').split('/').pop() || '';
  const isTour = !!document.querySelector('.tour-g');
  const track = (type, extra = {}) => {
    if (!C.sbUrl || !C.sbKey) return;
    const body = { type, ts: new Date().toISOString(), page: location.pathname.slice(0, 200), tour: isTour ? tourSlug.slice(0, 80) : (extra.tour || null), source, campaign: (qs.get('utm_campaign') || '').slice(0, 120) || null, device, vid: uid('vid'), sid: uid('sid'), ...extra };
    try { fetch(C.sbUrl + '/rest/v1/centr_site_events', { method: 'POST', keepalive: true, headers: { apikey: C.sbKey, Authorization: 'Bearer ' + C.sbKey, 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify(body) }); } catch (e) {}
  };
  track('pageview');
  document.addEventListener('click', e => {
    const a = e.target.closest('a'); if (!a) return;
    const h = a.href || '';
    if (/wa\.me|t\.me\/Ilya|tel:/.test(h)) {
      const ch = /wa\.me/.test(h) ? 'whatsapp' : (/tel:/.test(h) ? 'phone' : 'telegram');
      track('book_click', { channel: ch, label: (a.textContent || '').trim().slice(0, 120) });
      window.fbq && fbq('track', 'Contact', { content_name: tourSlug || location.pathname });
    } else if (/t\.me\/center_tourism/.test(h)) track('channel_click', { channel: 'telegram' });
    else if (a.closest('.promo')) track('promo_click', { label: (a.closest('.promo').querySelector('h3')?.textContent || '').slice(0, 120) });
  }, true);

  // mobile menu
  const mnav = $('#mnav');
  $$('[data-menu]').forEach(b => b.addEventListener('click', () => {
    mnav.classList.toggle('open');
    document.body.style.overflow = mnav.classList.contains('open') ? 'hidden' : '';
  }));
  mnav && mnav.addEventListener('click', e => { if (e.target === mnav) $('[data-menu]', mnav).click(); });

  // reveal on scroll
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach(el => io.observe(el));
  } else $$('.rv').forEach(el => el.classList.add('in'));

  // promo slider
  const initSlider = root => {
    const track = $('.promo-track', root); if (!track) return;
    const slides = $$('.promo', track), dots = $('.dots', root);
    if (slides.length < 2) { $('.promo-nav', root)?.remove(); return; }
    dots.innerHTML = slides.map(() => '<i></i>').join('');
    const idx = () => Math.round(track.scrollLeft / track.clientWidth);
    const go = i => track.scrollTo({ left: ((i + slides.length) % slides.length) * track.clientWidth, behavior: 'smooth' });
    const mark = () => $$('i', dots).forEach((d, i) => d.classList.toggle('on', i === idx()));
    track.addEventListener('scroll', () => requestAnimationFrame(mark), { passive: true });
    $('[data-prev]', root)?.addEventListener('click', () => go(idx() - 1));
    $('[data-next]', root)?.addEventListener('click', () => go(idx() + 1));
    let t = setInterval(() => go(idx() + 1), 6500);
    root.addEventListener('pointerenter', () => clearInterval(t));
    root.addEventListener('pointerleave', () => { clearInterval(t); t = setInterval(() => go(idx() + 1), 6500); });
    mark();
  };
  $$('[data-slider]').forEach(initSlider);

  // tours index for picker
  let TOURS = [];
  try { TOURS = JSON.parse($('#tours-index')?.textContent || '[]'); } catch (e) {}

  // quick picker (home)
  const picker = $('#picker');
  if (picker) {
    const state = { cat: '', budget: 0 };
    const out = () => {
      const list = TOURS.filter(t => (!state.cat || t.c.includes(state.cat)) && (!state.budget || t.p <= state.budget));
      $('#pk-n').textContent = list.length;
      $('#pk-min').textContent = list.length ? '$' + Math.min(...list.map(t => t.p)) : '—';
      const q = new URLSearchParams(); if (state.cat) q.set('cat', state.cat); if (state.budget) q.set('max', state.budget);
      $('#pk-go').href = (C.catUrl || '/ekskursii-nyachang-ceny') + (q.toString() ? '?' + q : '') + '#catalog';
    };
    $$('[data-pk]', picker).forEach(b => b.addEventListener('click', () => {
      const k = b.dataset.pk, v = b.dataset.v;
      const on = b.getAttribute('aria-pressed') === 'true';
      $$(`[data-pk="${k}"]`, picker).forEach(x => x.setAttribute('aria-pressed', 'false'));
      if (!on) b.setAttribute('aria-pressed', 'true');
      state[k] = on ? (k === 'budget' ? 0 : '') : (k === 'budget' ? +v : v);
      out();
    }));
    out();
  }

  // catalog filters
  const cat = $('#catalog');
  if (cat) {
    const p = new URLSearchParams(location.search);
    let cur = p.get('cat') || '', max = +p.get('max') || 0;
    const apply = () => {
      $$('[data-f]', cat).forEach(b => b.setAttribute('aria-pressed', String(b.dataset.f === cur)));
      let n = 0;
      $$('[data-cats]', cat).forEach(el => {
        const ok = (!cur || el.dataset.cats.split(' ').includes(cur)) && (!max || +el.dataset.price <= max);
        el.hidden = !ok; if (ok && el.classList.contains('card')) n++;
      });
      const c = $('#cat-count'); if (c) c.textContent = n;
    };
    $$('[data-f]', cat).forEach(b => b.addEventListener('click', () => {
      cur = b.dataset.f; max = 0;
      const q = new URLSearchParams(); if (cur) q.set('cat', cur);
      history.replaceState(null, '', location.pathname + (cur ? '?' + q : '') + '#catalog');
      apply();
    }));
    apply();
  }

  // lead forms
  $$('form[data-lead]').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(f));
    if (d.website) return; // honeypot
    const lead = {
      name: (d.name || '').trim(), contact: (d.contact || '').trim(), channel: d.channel || 'WhatsApp',
      tour: d.tour || '', date: d.date || null, people: d.people || '', message: d.message || '',
      page: location.pathname, utm: location.search.slice(0, 200)
    };
    if (!lead.contact) { f.contact?.focus(); return; }
    const btn = $('button[type=submit]', f); btn.disabled = true;
    let saved = false;
    try {
      if (C.sbUrl && C.sbKey) {
        const r = await fetch(C.sbUrl + '/rest/v1/centr_site_leads', {
          method: 'POST',
          headers: { apikey: C.sbKey, Authorization: 'Bearer ' + C.sbKey, 'Content-Type': 'application/json', Prefer: 'return=minimal' },
          body: JSON.stringify(lead)
        });
        saved = r.ok;
      }
      if (C.leadWebhook) { fetch(C.leadWebhook, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(lead), keepalive: true }); saved = true; }
    } catch (err) {}
    window.ym && ym(C.ym, 'reachGoal', 'lead');
    track('lead', { channel: (lead.channel || '').toLowerCase().slice(0, 20), tour: lead.tour ? lead.tour.slice(0, 80) : null });
    window.fbq && fbq('track', 'Lead', { content_name: lead.tour || 'подбор' });
    const ok = $('.form-ok', f);
    if (saved) { ok.classList.add('show'); f.reset(); }
    else {
      const txt = `Здравствуйте! Хочу забронировать${lead.tour ? ': ' + lead.tour : ' экскурсию'}.${lead.date ? ' Дата: ' + lead.date + '.' : ''}${lead.people ? ' Нас: ' + lead.people + '.' : ''} ${lead.message}`.trim();
      const url = lead.channel === 'Telegram' ? C.tg : C.wa + '?text=' + encodeURIComponent(txt);
      window.open(url, '_blank', 'noopener');
      ok.classList.add('show');
    }
    btn.disabled = false;
  }));

  // live promo banners — new promos appear without waiting for a rebuild
  const live = $('[data-live-banners]');
  if (live && C.sbUrl && C.sbKey) {
    const now = new Date().toISOString();
    fetch(`${C.sbUrl}/rest/v1/centr_site_banners?select=*&active=eq.true&placement=eq.hero&order=sort.asc&or=(ends_at.is.null,ends_at.gt.${now})`, {
      headers: { apikey: C.sbKey, Authorization: 'Bearer ' + C.sbKey }
    }).then(r => r.ok ? r.json() : null).then(rows => {
      if (!rows || !rows.length) return;
      rows = rows.filter(b => !b.starts_at || b.starts_at <= now);
      const sig = rows.map(b => b.id + b.updated_at).join('|');
      if (sig === live.dataset.sig) return;
      const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      $('.promo-track', live).innerHTML = rows.map(b => `<article class="promo" data-theme="${esc(b.theme)}">${b.image ? `<img src="${esc(b.image)}" alt="" loading="lazy">` : ''}<div class="promo-body">${b.badge ? `<span class="promo-badge">${esc(b.badge)}</span>` : ''}<h3>${esc(b.title)}</h3>${b.subtitle ? `<p>${esc(b.subtitle)}</p>` : ''}${b.link ? `<a class="btn btn-jade" href="${esc(b.link)}">${esc(b.cta || 'Подробнее')}</a>` : ''}</div></article>`).join('');
      initSlider(live);
    }).catch(() => {});
  }
})();
