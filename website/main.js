(function () {
  var cfg = window.OOOD || {};

  // Links from config.js
  document.querySelectorAll('[data-link="youtube"]').forEach(function (a) {
    if (cfg.youtube) a.href = cfg.youtube;
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
      spotify.querySelector('[data-spotify-label]').textContent = 'Spotify coming soon';
    }
  }

  // Social icons, top right
  var ICONS = {
    instagram: '<rect x="3" y="3" width="18" height="18" rx="5.5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.4" cy="6.6" r="1.3" fill="currentColor"/>',
    x: '<path d="M4 4h4.6l11.4 16h-4.6z" fill="currentColor"/><path d="M19.2 4 13.4 10.6M4.8 20l5.8-6.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    linkedin: '<rect x="2.5" y="2.5" width="19" height="19" rx="4" fill="currentColor"/><path d="M7.4 10v7M7.4 7.1v.1M11 17v-4.2c0-1.7 1-2.8 2.5-2.8s2.3 1 2.3 2.8V17M11 10.2V17" fill="none" stroke="#FBF1E5" stroke-width="2" stroke-linecap="round"/>',
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

  // Latest-episode popup
  var popup = document.querySelector('[data-popup]');

  function showEpisode(ep) {
    if (!ep || !ep.url || !ep.title) return;
    var known = (cfg.episodes || []).find(function (item) { return item.url === ep.url; });
    if (known) ep = Object.assign({}, known, ep);
    popup.querySelector('[data-episode-kicker]').textContent =
      'Latest episode' + (ep.number ? ' / ' + ep.number : '');
    popup.querySelector('[data-episode-title]').textContent = ep.title;
    popup.querySelector('[data-episode-blurb]').textContent =
      ep.blurb || 'Our newest episode is up. Grab a coffee and come learn with us.';
    var cta = popup.querySelector('[data-episode-cta]');
    cta.href = ep.url;
    cta.textContent = 'Watch the episode';
    popup.querySelector('[data-episode-link]').href = ep.url;
    if (ep.thumbnail) {
      var img = popup.querySelector('[data-episode-thumb]');
      img.onload = function () {
        img.hidden = false;
        popup.querySelector('[data-episode-tile]').hidden = true;
      };
      img.src = ep.thumbnail;
    }
    showEarlierEpisodes(ep.url);
    popup.classList.add('popup--live');
    if (window.fitHero) window.fitHero();
  }

  function showEarlierEpisodes(latestUrl) {
    var grid = document.querySelector('[data-episodes]');
    if (!grid) return;
    grid.replaceChildren();
    (cfg.episodes || []).filter(function (ep) { return ep.url !== latestUrl; }).forEach(function (ep) {
      var card = document.createElement('a');
      card.className = 'episode-card';
      card.href = ep.url;
      card.target = '_blank';
      card.rel = 'noopener';
      var image = document.createElement('img');
      image.src = ep.thumbnail;
      image.alt = '';
      image.loading = 'lazy';
      image.width = 480;
      image.height = 360;
      var body = document.createElement('div');
      body.className = 'episode-card__body';
      var label = document.createElement('span');
      label.className = 'label';
      label.textContent = 'Episode ' + ep.number;
      var title = document.createElement('h3');
      title.textContent = ep.title;
      var blurb = document.createElement('p');
      blurb.textContent = ep.blurb;
      var cta = document.createElement('span');
      cta.className = 'episode-card__cta';
      cta.textContent = 'Watch on YouTube →';
      body.append(label, title, blurb, cta);
      card.append(image, body);
      grid.appendChild(card);
    });
  }

  // Render the verified latest upload immediately, then refresh automatically.
  if (cfg.episodes && cfg.episodes.length) showEpisode(cfg.episodes[0]);

  if (cfg.pinnedEpisode) {
    showEpisode(cfg.pinnedEpisode);
  } else if (window.fetch) {
    fetch('/api/latest')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.video) return;
        var fallback = (cfg.episodes || [])[0];
        // An older cached response must not replace the verified latest upload.
        if (fallback && data.video.published &&
            Date.parse(data.video.published) < Date.parse(fallback.published)) return;
        showEpisode(data.video);
      })
      .catch(function () {});
  }

  // Size the hero so the whole homepage fits on one screen with no scrolling.
  // Everything below the hero has a natural height; the hero gets what is left.
  var hero = document.querySelector('.hero');
  var root = document.documentElement;
  var MIN_HERO = 140;

  function fitHero() {
    if (window.innerWidth <= 640) {
      root.style.removeProperty('--hero-h');
      return;
    }
    var heroBottom = hero.offsetTop + hero.offsetHeight;
    // Everything after the hero, to the very bottom of the page
    var below = document.body.scrollHeight - heroBottom;
    var above = hero.offsetTop; // the logo bar, when it sits above the hero
    var available = window.innerHeight - below - above;
    root.style.setProperty('--hero-h', Math.max(MIN_HERO, Math.floor(available)) + 'px');
  }

  fitHero();
  window.addEventListener('resize', fitHero);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitHero);
  window.fitHero = fitHero;

  // Pop the card in when it scrolls into view
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    popup.classList.add('popup--in');
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          popup.classList.add('popup--in');
          io.disconnect();
        }
      });
    }, { threshold: 0.35 });
    io.observe(popup);
  }
})();
