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

  if (cfg.email) {
    document.querySelectorAll('[data-email]').forEach(function (a) {
      a.href = 'mailto:' + cfg.email;
      if (a.classList.contains('footer__mail')) a.textContent = cfg.email;
    });
  }

  var socials = document.querySelector('[data-socials]');
  if (socials && cfg.socials) {
    cfg.socials.forEach(function (s) {
      var a = document.createElement('a');
      a.className = 'label label--light';
      a.href = s.url;
      a.target = '_blank';
      a.rel = 'noopener';
      a.textContent = s.label;
      socials.appendChild(a);
    });
  }

  // Latest-episode popup
  var popup = document.querySelector('[data-popup]');

  function showEpisode(ep) {
    if (!ep || !ep.url || !ep.title) return;
    popup.querySelector('[data-episode-kicker]').textContent = 'Latest episode';
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
    popup.classList.add('popup--live');
  }

  if (cfg.pinnedEpisode) {
    showEpisode(cfg.pinnedEpisode);
  } else if (window.fetch) {
    fetch('/api/latest')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) { if (data && data.video) showEpisode(data.video); })
      .catch(function () {});
  }

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
