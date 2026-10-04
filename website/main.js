(function () {
  var cfg = window.OOOD || {};

  // Links from config.js
  document.querySelectorAll('[data-link="youtube"]').forEach(function (a) {
    if (cfg.youtube) a.href = cfg.youtube;
  });
  document.querySelectorAll('[data-link="youtube-videos"]').forEach(function (a) {
    if (cfg.youtube) a.href = cfg.youtube.replace(/\/$/, '') + '/videos';
  });

  var spotify = document.querySelector('[data-link="spotify"]');
  if (spotify) {
    if (cfg.spotify) {
      spotify.href = cfg.spotify;
    } else {
      spotify.removeAttribute('href');
      spotify.removeAttribute('target');
      spotify.setAttribute('aria-disabled', 'true');
      spotify.classList.add('btn--soon');
      spotify.querySelector('[data-spotify-label]').textContent = 'Spotify soon';
    }
  }

  // Social icons, top right
  var ICONS = {
    instagram: '<rect x="3" y="3" width="18" height="18" rx="5.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.4" cy="6.6" r="1.3" fill="currentColor"/>',
    x: '<path d="M4 4h4.6l11.4 16h-4.6z" fill="currentColor"/><path d="M19.2 4 13.4 10.6M4.8 20l5.8-6.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    linkedin: '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 10.6V16.2M8 7.7v.1M11.6 16.2v-3.4c0-1.5.9-2.3 2.1-2.3s2 .8 2 2.3v3.4M11.6 10.6v5.6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    facebook: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M13.3 21.9V14h2.4l.4-2.9h-2.8V9.4c0-.8.3-1.4 1.4-1.4h1.5V5.5c-.3 0-1.2-.1-2.2-.1-2.2 0-3.6 1.3-3.6 3.7v2H8v2.9h2.4v7.9" fill="#FBF1E5"/>',
    tiktok: '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M14 3c.4 2.8 2.3 4.6 5 4.8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
    youtube: '<rect x="2" y="5" width="20" height="14" rx="4.5" fill="currentColor"/><path d="M10 9.2v5.6l4.8-2.8z" fill="#FBF1E5"/>',
    spotify: '<circle cx="12" cy="12" r="10" fill="currentColor"/><path d="M7 9.6c3.3-1 7-.7 9.9 1M7.6 12.5c2.7-.8 5.7-.5 8.1.9M8.2 15.2c2.1-.6 4.3-.4 6.2.7" fill="none" stroke="#FBF1E5" stroke-width="1.6" stroke-linecap="round"/>',
    email: '<rect x="2.5" y="5" width="19" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="m3.5 7 8.5 6 8.5-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
  };

  var socials = document.querySelector('[data-socials]');
  if (socials) {
    var items = (cfg.socials || []).slice();
    if (cfg.email) items.push({ label: 'Email ' + cfg.email, icon: 'email', url: 'mailto:' + cfg.email });
    items.forEach(function (s) {
      if (!ICONS[s.icon]) return;
      var a = document.createElement('a');
      a.className = 'social';
      a.href = s.url;
      a.setAttribute('aria-label', s.label);
      a.title = s.label;
      if (s.icon !== 'email') {
        a.target = '_blank';
        a.rel = 'noopener';
      }
      a.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS[s.icon] + '</svg>';
      socials.appendChild(a);
    });
  }

  // Episodes: every public upload, newest first (Josh 2026-10-04). The HTML ships the same cards as a no-JS fallback.
  var grid = document.querySelector('[data-episodes]');
  var WAVE = '<span class="wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span>';

  function thumbFor(ep) {
    if (ep.thumbnail) return ep.thumbnail.replace('/hqdefault.jpg', '/maxresdefault.jpg');
    return ep.id ? 'https://i.ytimg.com/vi/' + ep.id + '/maxresdefault.jpg' : '';
  }

  function renderEpisodes(list) {
    if (!grid || !list.length) return;
    grid.replaceChildren();
    list.forEach(function (ep, i) {
      var card = document.createElement('a');
      card.className = 'ep' + (i === 0 ? ' ep--latest' : '');
      card.href = ep.url;
      card.target = '_blank';
      card.rel = 'noopener';

      var thumb = document.createElement('span');
      thumb.className = 'ep__thumb';
      var img = document.createElement('img');
      img.alt = '';
      img.width = 1280;
      img.height = 720;
      if (i > 0) img.loading = 'lazy';
      // A fresh upload may not have a maxres image yet; YouTube serves a 120px placeholder instead.
      img.onload = function () {
        if (img.naturalWidth <= 120 && img.src.indexOf('maxresdefault') > -1) {
          img.src = img.src.replace('maxresdefault', 'hqdefault');
        }
      };
      img.onerror = function () {
        if (img.src.indexOf('maxresdefault') > -1) img.src = img.src.replace('maxresdefault', 'hqdefault');
      };
      img.src = thumbFor(ep);
      thumb.appendChild(img);

      var meta = document.createElement('span');
      meta.className = 'ep__meta label';
      if (i === 0) {
        meta.innerHTML = WAVE;
        meta.appendChild(document.createTextNode('New' + (ep.number ? ' \u00b7 ' + ep.number : '')));
      } else {
        meta.textContent = ep.number ? 'Episode ' + ep.number : 'Episode';
      }

      var title = document.createElement('h3');
      title.className = 'ep__title';
      title.textContent = ep.title;

      card.append(thumb, meta, title);
      grid.appendChild(card);
    });
    if (window.fitHero) window.fitHero();
  }

  function withLatest(ep) {
    var list = (cfg.episodes || []).slice();
    if (!ep || !ep.url || !ep.title) return list;
    var known = list.find(function (item) { return item.url === ep.url; });
    var merged = known ? Object.assign({}, ep, known) : ep;
    return [merged].concat(list.filter(function (item) { return item.url !== ep.url; }));
  }

  // Render the verified uploads immediately, then pick up anything newer from YouTube.
  renderEpisodes(withLatest(cfg.pinnedEpisode));

  if (!cfg.pinnedEpisode && window.fetch) {
    fetch('/api/latest')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.video) return;
        var newest = (cfg.episodes || [])[0];
        if (newest && data.video.url === newest.url) return;
        // An older cached response must not replace the verified latest upload.
        if (newest && data.video.published &&
            Date.parse(data.video.published) < Date.parse(newest.published)) return;
        renderEpisodes(withLatest(data.video));
      })
      .catch(function () {});
  }

  // Size the hero so everything through the first row of episodes fits on one screen.
  // Older episodes wrap onto later rows and scroll; the hero gets what is left.
  var hero = document.querySelector('.hero');
  var root = document.documentElement;
  var MIN_HERO = 180;
  var ROW_GAP = 44; // breathing room under the first row

  function fitHero() {
    if (window.innerWidth <= 640) {
      root.style.removeProperty('--hero-h');
      return;
    }
    var heroBottom = hero.offsetTop + hero.offsetHeight;
    // Everything after the hero, down to the bottom of the first row of episode cards
    var cards = grid ? grid.children : [];
    var below = document.body.scrollHeight - heroBottom;
    if (cards.length) {
      var firstTop = cards[0].offsetTop, rowBottom = 0;
      for (var i = 0; i < cards.length && cards[i].offsetTop === firstTop; i++) {
        var r = cards[i].getBoundingClientRect();
        rowBottom = Math.max(rowBottom, r.bottom + window.scrollY);
      }
      below = Math.min(below, rowBottom - heroBottom + ROW_GAP);
    }
    var above = hero.offsetTop; // the logo bar, when it sits above the hero
    var available = window.innerHeight - below - above;
    root.style.setProperty('--hero-h', Math.max(MIN_HERO, Math.floor(available)) + 'px');
  }

  fitHero();
  window.addEventListener('resize', fitHero);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitHero);
  window.fitHero = fitHero;
})();
