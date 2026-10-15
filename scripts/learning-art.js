
/* Learning page drawings, used by scripts/build-learning.js at build time (nothing here ships to the browser).
   Pool scenes. One cast for every word: Sho Hatakeyama's O-heads are always people (thick navy ring, cream face, two dot
   eyes, bobbing half under with the ring showing lighter through the water). The AI is always the little blue square with
   the same eyes and an antenna. Every scene shares one waterline (y = 72 of 100) and one stroke weight. */
var ART = (function () {
  'use strict';
  var N = '#0B2A45', C = '#FBF1E5', B = '#38B6FF', T = '#A9DCFF', UID = 0;
  var WAVE_TOP = 'M0 72 Q10 67.5 20 72 T40 72 T60 72 T80 72 T100 72 T120 72 T140 72 T160 72';
  var WAVE = WAVE_TOP + ' V100 H0 Z';
  function f(n) { return Math.round(n * 10) / 10; }
  function attrs(o) { var s = ''; for (var k in o) s += ' ' + k + '="' + o[k] + '"'; return s; }
  function el(tag, o, inner) { return '<' + tag + attrs(o) + (inner == null ? '/>' : '>' + inner + '</' + tag + '>'); }
  var SW = 2.2, INK = { stroke: N, 'stroke-width': SW, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
  function ink(o) { var r = {}; for (var k in INK) r[k] = INK[k]; for (k in o) r[k] = o[k]; return r; }

  // ---------- eyes, shared by O-heads and the AI ----------
  function eyes(x, y, gap, r, o) {
    o = o || {}; var dx = o.dx || 0, dy = o.dy || 0, s = '';
    [-1, 1].forEach(function (side) {
      var ex = f(x + side * gap + dx), ey = f(y + dy);
      if (o.mood === 'happy') s += el('path', ink({ d: 'M' + f(ex - r * 1.4) + ' ' + f(ey + r * .6) + ' Q' + ex + ' ' + f(ey - r * 1.6) + ' ' + f(ex + r * 1.4) + ' ' + f(ey + r * .6), fill: 'none', 'stroke-width': f(r * 1.1) }));
      else if (o.mood === 'dizzy') s += el('circle', { cx: ex, cy: ey, r: f(r * 1.3), fill: 'none', stroke: N, 'stroke-width': f(r * .7) });
      else s += el('circle', { cx: ex, cy: ey, r: f(o.mood === 'wow' ? r * 1.4 : r), fill: N });
    });
    return s;
  }
  // ---------- Sho's O-head ----------
  function oHead(x, y, r, o) {
    o = o || {}; var sw = r * .34, s = '';
    if (o.glitch) s += el('circle', { cx: f(x + 2.4), cy: f(y - 1), r: f(r - sw / 2), fill: 'none', stroke: B, 'stroke-width': f(sw) });
    s += el('circle', { cx: x, cy: y, r: f(r - sw / 2), fill: C, stroke: N, 'stroke-width': f(sw), 'stroke-dasharray': o.dashed ? '3 2.4' : 'none' });
    return s + eyes(x, y - r * .12, r * .28, r * .13, o);
  }
  function oUnder(x, y, r) { var sw = r * .34; return el('circle', { cx: x, cy: y, r: f(r - sw / 2), fill: 'none', stroke: T, 'stroke-width': f(sw) }); }
  // ---------- the AI ----------
  function bot(x, y, s, o) {
    o = o || {}; var h = o.h || s, top = y - h / 2, sw = Math.max(1.8, s * .09), out = '';
    if (o.cap) out += el('path', { d: 'M' + x + ' ' + f(top - 7) + ' L' + f(x + s * .62) + ' ' + f(top - 2.5) + ' L' + x + ' ' + f(top + 2) + ' L' + f(x - s * .62) + ' ' + f(top - 2.5) + ' Z', fill: N }) +
      el('path', ink({ d: 'M' + f(x + s * .45) + ' ' + f(top - 3) + ' V' + f(top + 7), fill: 'none', 'stroke-width': 1.4 }));
    else out += el('line', ink({ x1: x, y1: f(top), x2: x, y2: f(top - s * .22), 'stroke-width': f(sw * .8) })) + el('circle', { cx: x, cy: f(top - s * .27), r: f(s * .085), fill: N });
    out += el('rect', { x: f(x - s / 2), y: f(top), width: f(s), height: f(h), rx: f(s * .28), fill: B, stroke: N, 'stroke-width': f(sw) });
    return out + eyes(x, top + s * .42, s * .19, s * .075, o);
  }
  function botUnder(x, y, s, o) { o = o || {}; var h = o.h || s; return el('rect', { x: f(x - s / 2), y: f(y - h / 2), width: f(s), height: f(h), rx: f(s * .28), fill: 'none', stroke: T, 'stroke-width': f(Math.max(1.8, s * .09)) }); }

  // ---------- props ----------
  function lines(x, y, w, n, gap, o) {
    o = o || {}; var s = '';
    for (var i = 0; i < n; i++) s += el('line', { x1: f(x), y1: f(y + i * (gap || 5)), x2: f(x + (i === n - 1 && n > 1 ? w * .6 : w)), y2: f(y + i * (gap || 5)), stroke: o.color || N, 'stroke-width': 1.6, 'stroke-linecap': 'round', opacity: o.op || .55 });
    return s;
  }
  function doc(x, y, w, h, n, o) {
    o = o || {};
    return el('rect', ink({ x: x, y: y, width: w, height: h, rx: 2.5, fill: o.fill || C, 'stroke-dasharray': o.dashed ? '3 2.4' : 'none' })) + (n ? lines(x + 5, y + 7, w - 10, n, o.gap || 5) : '');
  }
  function bubble(x, y, w, h, tail, o) {
    o = o || {}; var s = el('rect', ink({ x: x, y: y, width: w, height: h, rx: 8, fill: C })), b = y + h - 1.2;
    if (tail === 'bl') s += el('path', ink({ d: 'M' + (x + 10) + ' ' + b + ' L' + (x + 4) + ' ' + (y + h + 8) + ' L' + (x + 18) + ' ' + b, fill: C }));
    if (tail === 'br') s += el('path', ink({ d: 'M' + (x + w - 18) + ' ' + b + ' L' + (x + w - 4) + ' ' + (y + h + 8) + ' L' + (x + w - 10) + ' ' + b, fill: C }));
    if (tail === 'think-l') s += el('circle', ink({ cx: x + 6, cy: y + h + 5, r: 3, fill: C })) + el('circle', ink({ cx: x - 1, cy: y + h + 11, r: 1.8, fill: C }));
    if (tail === 'think-r') s += el('circle', ink({ cx: x + w - 6, cy: y + h + 5, r: 3, fill: C })) + el('circle', ink({ cx: x + w + 1, cy: y + h + 11, r: 1.8, fill: C }));
    return s;
  }
  function arrow(x1, y1, x2, y2, o) {
    o = o || {}; var a = Math.atan2(y2 - y1, x2 - x1), h = 5;
    return el('line', ink({ x1: x1, y1: y1, x2: f(x2 - Math.cos(a) * 1.5), y2: f(y2 - Math.sin(a) * 1.5), 'stroke-dasharray': o.dash ? '3 3' : 'none' })) +
      el('path', ink({ d: 'M' + f(x2 - h * Math.cos(a - .55)) + ' ' + f(y2 - h * Math.sin(a - .55)) + ' L' + x2 + ' ' + y2 + ' L' + f(x2 - h * Math.cos(a + .55)) + ' ' + f(y2 - h * Math.sin(a + .55)), fill: 'none' }));
  }
  function star(x, y, r, fill) {
    var p = []; for (var i = 0; i < 10; i++) { var a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .45 : r; p.push(f(x + rr * Math.cos(a)) + ' ' + f(y + rr * Math.sin(a))); }
    return el('path', ink({ d: 'M' + p.join(' L') + ' Z', fill: fill || B, 'stroke-width': 1.6 }));
  }
  function sparkle(x, y, r) { return el('path', { d: 'M' + x + ' ' + (y - r) + ' Q' + x + ' ' + y + ' ' + (x + r) + ' ' + y + ' Q' + x + ' ' + y + ' ' + x + ' ' + (y + r) + ' Q' + x + ' ' + y + ' ' + (x - r) + ' ' + y + ' Q' + x + ' ' + y + ' ' + x + ' ' + (y - r) + ' Z', fill: N }); }
  function check(x, y, s) { return el('path', ink({ d: 'M' + x + ' ' + y + ' l' + f(s * .35) + ' ' + f(s * .35) + ' l' + f(s * .65) + ' ' + f(-s * .7), fill: 'none', 'stroke-width': 2.4 })); }
  function mag(x, y, r) { return el('circle', ink({ cx: x, cy: y, r: r, fill: C, 'stroke-width': 2.6 })) + el('line', ink({ x1: f(x + r * .7), y1: f(y + r * .7), x2: f(x + r * 1.5), y2: f(y + r * 1.5), 'stroke-width': 3.2 })); }
  function flag(x, yBase, h, fill) { return el('line', ink({ x1: x, y1: yBase, x2: x, y2: yBase - h })) + el('path', ink({ d: 'M' + x + ' ' + (yBase - h) + ' L' + (x + 13) + ' ' + (yBase - h + 5) + ' L' + x + ' ' + (yBase - h + 10) + ' Z', fill: fill || B, 'stroke-width': 1.8 })); }
  function tile(x, y, w, h, inner, fill) { return el('rect', ink({ x: x, y: y, width: w, height: h, rx: 4, fill: fill || C })) + (inner || ''); }
  function text(x, y, s, size, o) { o = o || {}; return el('text', { x: x, y: y, 'text-anchor': o.anchor || 'middle', class: 'ink', 'font-size': size, style: o.display ? 'font-family:var(--display);font-weight:800' : '' }, s); }

  // ---------- scene builder: characters, then water, then their ghost under the surface, then labels ----------
  function Scene() { this.a = []; this.u = []; this.t = []; }
  Scene.prototype.add = function (s) { this.a.push(s); return this; };
  Scene.prototype.under = function (s) { this.u.push(s); return this; };
  Scene.prototype.top = function (s) { this.t.push(s); return this; };
  Scene.prototype.o = function (x, y, r, o) { this.a.push(oHead(x, y, r, o)); this.u.push(oUnder(x, y, r)); return this; };
  Scene.prototype.bot = function (x, y, s, o) { this.a.push(bot(x, y, s, o)); this.u.push(botUnder(x, y, s, o)); return this; };
  Scene.prototype.label = function (x, s) { this.t.push(el('text', { x: x, y: 91, 'text-anchor': 'middle', class: 'lbl' }, s)); return this; };
  Scene.prototype.svg = function () {
    var id = 'pool' + (++UID);
    return '<svg viewBox="0 0 160 100" aria-hidden="true" focusable="false"><defs><clipPath id="' + id + '"><path d="' + WAVE + '"/></clipPath></defs>' +
      this.a.join('') + '<path d="' + WAVE + '" fill="' + B + '"/><g clip-path="url(#' + id + ')">' + this.u.join('') + '</g>' +
      '<path d="' + WAVE_TOP + '" fill="none" stroke="' + C + '" stroke-width="2.4"/>' + this.t.join('') + '</svg>';
  };
  function S() { return new Scene(); }

  var scenes = {
    'generative-ai': function () {
      return S().bot(36, 62, 26, { mood: 'happy' }).add(sparkle(16, 34, 5) + sparkle(58, 26, 4))
        .add(arrow(56, 50, 76, 42))
        .add(doc(84, 22, 22, 28, 3))
        .add(tile(112, 24, 28, 22, el('path', { d: 'M115 43 L123 33 L129 39 L132 36 L137 43 Z', fill: B }) + el('circle', { cx: 132, cy: 30, r: 2.5, fill: N })))
        .add(el('path', ink({ d: 'M146 52 V36 L154 34 V48', fill: 'none' })) + el('circle', { cx: 144, cy: 52, r: 3, fill: N }) + el('circle', { cx: 152, cy: 48, r: 3, fill: N }))
        .svg();
    },
    'llm': function () {
      return S().add(tile(14, 54, 40, 10, '', T) + tile(17, 44, 36, 10, '', C) + tile(12, 34, 38, 10, '', B) + tile(18, 24, 32, 10, '', C))
        .bot(78, 62, 24).add(bubble(96, 14, 58, 30, 'bl'))
        .add(el('rect', { x: 103, y: 25, width: 14, height: 8, rx: 2.5, fill: N }) + el('rect', { x: 120, y: 25, width: 11, height: 8, rx: 2.5, fill: N }) +
          el('rect', { x: 134, y: 25, width: 13, height: 8, rx: 2.5, fill: 'none', stroke: N, 'stroke-width': 1.6, 'stroke-dasharray': '2.5 2' }))
        .svg();
    },
    'model-vs-app': function () {
      return S().add(tile(10, 26, 30, 40, lines(16, 34, 18, 1) + el('rect', { x: 15, y: 40, width: 6, height: 6, fill: T }) + el('rect', { x: 29, y: 40, width: 6, height: 6, fill: T }) + el('rect', { x: 15, y: 52, width: 6, height: 6, fill: T }) + el('rect', { x: 29, y: 52, width: 6, height: 6, fill: T })))
        .add(arrow(46, 46, 60, 46)).bot(80, 60, 24).add(arrow(98, 46, 112, 46))
        .add(el('rect', ink({ x: 118, y: 16, width: 30, height: 50, rx: 6, fill: C })) + el('rect', { x: 123, y: 24, width: 20, height: 26, rx: 2, fill: T }) + el('circle', { cx: 133, cy: 58, r: 2.2, fill: N }))
        .label(25, 'COMPANY').label(80, 'MODEL').label(133, 'APP').svg();
    },
    'model-sizes': function () {
      return S().bot(30, 68, 15).bot(78, 64, 23).bot(128, 58, 34, { mood: 'happy' })
        .label(30, 'LUNA').label(78, 'SOL').label(128, 'ASTRA').svg();
    },
    'training': function () {
      var pile = '';
      [[96, 46, 22, 20], [118, 48, 22, 18], [104, 32, 22, 18], [126, 34, 20, 16], [112, 18, 22, 18], [88, 56, 24, 12], [132, 56, 22, 12]].forEach(function (d) { pile += doc(d[0], d[1], d[2], d[3], 2, { gap: 5 }); });
      return S().bot(36, 62, 24, { mood: 'wow', dx: 1.5 }).add(pile).add(arrow(84, 40, 56, 48)).add(arrow(84, 30, 60, 38, { dash: true })).svg();
    },
    'prompt': function () {
      return S().o(28, 63, 13, { dx: 1.5 }).add(bubble(44, 14, 70, 32, 'bl')).add(lines(52, 24, 54, 3, 6))
        .add(arrow(118, 32, 130, 46)).bot(140, 62, 22, { dx: -1.5 }).svg();
    },
    'token': function () {
      var s = '', x = 56, w = [18, 10, 22, 9, 14];
      w.forEach(function (ww, i) { s += el('rect', { x: x, y: 27, width: ww, height: 12, rx: 3, fill: i % 2 ? B : N, stroke: N, 'stroke-width': 1.4 }); x += ww + 4; });
      return S().bot(28, 62, 22, { dx: 1.5 }).add(bubble(46, 16, 108, 34, 'bl')).add(s).svg();
    },
    'context-window': function () {
      return S().add(el('rect', ink({ x: 50, y: 12, width: 74, height: 48, rx: 4, fill: C })))
        .add(el('rect', { x: 58, y: 20, width: 40, height: 7, rx: 2.5, fill: B }) + el('rect', { x: 66, y: 31, width: 50, height: 7, rx: 2.5, fill: T }) + el('rect', { x: 58, y: 42, width: 34, height: 7, rx: 2.5, fill: B }))
        .add(el('rect', { x: 16, y: 20, width: 26, height: 7, rx: 2.5, fill: 'none', stroke: N, 'stroke-width': 1.5, 'stroke-dasharray': '2.5 2', opacity: .6 }))
        .add(arrow(48, 24, 38, 24 + 0.01, { dash: false }))
        .bot(142, 62, 20, { dx: -1.5 }).svg();
    },
    'knowledge-cutoff': function () {
      return S().add(el('line', ink({ x1: 12, y1: 42, x2: 98, y2: 42, 'stroke-width': 2.6 })) + el('line', ink({ x1: 98, y1: 42, x2: 152, y2: 42, 'stroke-dasharray': '3 4', opacity: .6 })))
        .add([24, 44, 64, 84].map(function (x) { return el('line', ink({ x1: x, y1: 38, x2: x, y2: 46 })); }).join(''))
        .add(el('line', ink({ x1: 98, y1: 26, x2: 98, y2: 56, 'stroke-width': 2.6 })) + text(98, 21, 'CUTOFF', 6.5))
        .add(text(130, 36, '?', 18, { display: true }))
        .bot(54, 62, 22, { dx: 2 }).svg();
    },
    'hallucination': function () {
      return S().bot(40, 61, 24, { mood: 'happy' }).add(bubble(62, 10, 90, 40, 'bl'))
        .add(text(76, 38, '"', 26, { display: true })).add(lines(86, 22, 28, 3, 6))
        .add(doc(124, 16, 20, 26, 0, { dashed: true }) + text(134, 34, '?', 12, { display: true })).svg();
    },
    'multimodal': function () {
      var bars = ''; [5, 10, 14, 8, 12, 5].forEach(function (h, i) { bars += el('line', ink({ x1: 18 + i * 5, y1: 42 - h / 2, x2: 18 + i * 5, y2: 42 + h / 2, 'stroke-width': 2.4 })); });
      return S().add(tile(12, 8, 30, 20, el('path', { d: 'M15 25 L24 15 L30 21 L33 18 L39 25 Z', fill: B }) + el('circle', { cx: 34, cy: 13, r: 2.5, fill: N })))
        .add(bars).add(doc(14, 52, 26, 16, 2, { gap: 5 }))
        .add(arrow(48, 18, 106, 52) + arrow(50, 42, 106, 58) + arrow(46, 60, 106, 64))
        .bot(124, 61, 24, { dx: -1.5 }).svg();
    },
    'memory': function () {
      return S().o(34, 63, 13, { dx: 1.5 }).bot(112, 62, 24, { dy: -.5 })
        .add(bubble(58, 8, 70, 30, 'think-r')).add(oHead(76, 23, 8)).add(lines(90, 18, 28, 3, 5)).svg();
    },
    'custom-instructions': function () {
      return S().add(el('rect', ink({ x: 50, y: 12, width: 46, height: 42, rx: 2, fill: T })) + el('circle', { cx: 73, cy: 12, r: 3.2, fill: N }) + lines(57, 24, 32, 4, 6, { op: .7 }))
        .bot(124, 62, 24, { dx: -1.5, dy: -1 }).svg();
    },
    'projects': function () {
      return S().add(el('path', ink({ d: 'M30 24 H56 L62 30 H118 V66 H30 Z', fill: T })))
        .add(doc(42, 18, 22, 26, 2) + el('rect', ink({ x: 92, y: 14, width: 22, height: 14, rx: 6, fill: C })))
        .add(bot(76, 34, 22))
        .add(el('rect', ink({ x: 26, y: 40, width: 96, height: 28, rx: 4, fill: C })) + el('line', ink({ x1: 64, y1: 54, x2: 84, y2: 54 })))
        .svg();
    },
    'reasoning': function () {
      var pts = [[78, 38], [96, 22], [114, 36], [134, 20]], path = 'M' + pts.map(function (p) { return p.join(' '); }).join(' L');
      return S().bot(36, 61, 24, { dx: 1.5, dy: -1 }).add(bubble(60, 8, 92, 42, 'think-l'))
        .add(el('path', ink({ d: path, fill: 'none', 'stroke-dasharray': '3 3' })))
        .add(pts.map(function (p, i) { return el('circle', ink({ cx: p[0], cy: p[1], r: 4.2, fill: i === 3 ? B : C, 'stroke-width': 1.8 })); }).join('')).svg();
    },
    'deep-research': function () {
      var g = ''; [[10, 14], [26, 14], [42, 14], [10, 38], [26, 38], [42, 38]].forEach(function (p) { g += doc(p[0], p[1], 12, 16, 2, { gap: 4 }); });
      return S().add(g).bot(78, 62, 22, { dx: 1.5 }).add(mag(92, 38, 9))
        .add(arrow(104, 34, 116, 34)).add(doc(120, 14, 28, 38, 4)).add(el('circle', { cx: 146, cy: 16, r: 7, fill: B, stroke: N, 'stroke-width': 1.8 }) + check(142.5, 16, 7)).svg();
    },
    'skills': function () {
      return S().add(el('rect', ink({ x: 20, y: 30, width: 42, height: 30, rx: 3, fill: T })) + el('rect', ink({ x: 26, y: 24, width: 42, height: 30, rx: 3, fill: C })) + el('rect', ink({ x: 32, y: 18, width: 42, height: 30, rx: 3, fill: C })) + lines(38, 28, 28, 3, 6))
        .add(el('rect', ink({ x: 88, y: 12, width: 34, height: 26, rx: 3, fill: C })) + star(100, 24, 6) + lines(109, 21, 8, 2, 5))
        .add(arrow(80, 30, 86, 26)).bot(136, 62, 22, { dx: -1.5, dy: -1 }).svg();
    },
    'agent': function () {
      return S().o(16, 64, 10, { dx: 1 }).bot(46, 61, 20, { dx: 1.5 })
        .add(el('path', ink({ d: 'M58 52 C70 28 84 20 92 24 S112 46 122 40 S138 28 144 30', fill: 'none', 'stroke-dasharray': '3 3.5' })))
        .add(el('circle', ink({ cx: 92, cy: 24, r: 7, fill: C })) + el('circle', ink({ cx: 91, cy: 23, r: 3, fill: 'none', 'stroke-width': 1.6 })) + el('line', ink({ x1: 93.2, y1: 25.2, x2: 95.5, y2: 27.5, 'stroke-width': 1.6 })))
        .add(el('rect', ink({ x: 115, y: 33, width: 14, height: 13, rx: 2, fill: C })) + el('line', ink({ x1: 115, y1: 37.5, x2: 129, y2: 37.5, 'stroke-width': 1.6 })))
        .add(flag(146, 46, 30)).svg();
    },
    'computer-use': function () {
      return S().add(el('rect', ink({ x: 36, y: 10, width: 78, height: 44, rx: 4, fill: C })) + el('rect', { x: 43, y: 17, width: 30, height: 8, rx: 2, fill: T }) + el('rect', { x: 43, y: 29, width: 56, height: 6, rx: 2, fill: T }) + el('rect', { x: 43, y: 39, width: 22, height: 8, rx: 2, fill: B }) +
          el('path', ink({ d: 'M28 54 H122 L128 62 H22 Z', fill: C })))
        .add(el('path', { d: 'M86 34 L86 48 L90 44 L93 50 L95.5 49 L92.5 43 L98 43 Z', fill: N, stroke: C, 'stroke-width': 1 }))
        .bot(144, 63, 20, { dx: -1.5, dy: -1 }).svg();
    },
    'mcp': function () {
      return S().bot(28, 62, 24, { dx: 1.5 })
        .add(el('path', ink({ d: 'M40 58 C52 58 50 42 62 42', fill: 'none' })) + el('rect', ink({ x: 62, y: 36, width: 12, height: 12, rx: 2, fill: B })) + el('line', ink({ x1: 74, y1: 39, x2: 79, y2: 39 })) + el('line', ink({ x1: 74, y1: 45, x2: 79, y2: 45 })))
        .add(el('path', ink({ d: 'M82 42 C96 42 96 20 108 20 M82 42 H108 M82 42 C96 42 96 62 108 62', fill: 'none', opacity: .55 })))
        .add(tile(110, 11, 24, 18, el('path', ink({ d: 'M112 13 L122 21 L132 13', fill: 'none', 'stroke-width': 1.6 }))))
        .add(tile(110, 33, 24, 18, el('line', ink({ x1: 110, y1: 38, x2: 134, y2: 38, 'stroke-width': 1.6 })) + el('rect', { x: 115, y: 41, width: 5, height: 5, fill: B })))
        .add(tile(110, 54, 24, 14, el('path', { d: 'M116 65 L122 57 L128 65 Z', fill: B })))
        .svg();
    },
    'vibe-coding': function () {
      return S().o(20, 63, 12, { dx: 1.5 }).add(bubble(32, 10, 52, 28, 'bl')).add(lines(39, 19, 38, 3, 5))
        .add(arrow(86, 36, 94, 44)).bot(104, 62, 20, { dx: 1.5 })
        .add(el('rect', ink({ x: 118, y: 14, width: 36, height: 34, rx: 4, fill: C })) + el('line', ink({ x1: 118, y1: 22, x2: 154, y2: 22 })) + el('rect', { x: 123, y: 26, width: 26, height: 7, rx: 2, fill: B }) + el('rect', { x: 123, y: 36, width: 12, height: 8, rx: 2, fill: T }) + el('rect', { x: 137, y: 36, width: 12, height: 8, rx: 2, fill: T }))
        .under(el('text', { x: 136, y: 92, 'text-anchor': 'middle', 'font-size': 10, fill: T }, '&lt;/&gt;')).svg();
    },
    'sycophancy': function () {
      return S().add(doc(14, 22, 26, 30, 0) + el('path', ink({ d: 'M19 30 q4 -3 8 0 t8 0 M19 37 q4 3 8 0 t8 0 M19 44 q3 -2 6 0', fill: 'none', 'stroke-width': 1.6, opacity: .6 })))
        .o(48, 63, 12, { dx: 2 }).bot(100, 62, 24, { mood: 'happy' }).add(bubble(114, 10, 42, 26, 'bl'))
        .add(star(124, 23, 5) + star(135, 23, 5) + star(146, 23, 5)).svg();
    },
    'ai-slop': function () {
      var d = ''; [56, 78, 100, 122].forEach(function (x, i) { d += el('rect', ink({ x: x, y: 24 + (i % 2) * 4, width: 26, height: 32, rx: 2.5, fill: T })) + el('path', { d: 'M' + (x + 5) + ' ' + (33 + (i % 2) * 4) + ' q4 -3 8 0 t8 0 M' + (x + 5) + ' ' + (41 + (i % 2) * 4) + ' q4 -3 8 0 t8 0 M' + (x + 5) + ' ' + (49 + (i % 2) * 4) + ' q4 -3 8 0', fill: 'none', stroke: N, 'stroke-width': 1.4, opacity: .5 }); });
      return S().bot(28, 62, 22, { dy: 1 }).add(d).add(text(150, 18, 'zzz', 8)).svg();
    },
    'prompt-injection': function () {
      return S().add(doc(12, 12, 46, 48, 0) + lines(18, 20, 34, 2, 5) + el('rect', { x: 17, y: 32, width: 36, height: 9, rx: 2, fill: B, stroke: N, 'stroke-width': 1.4, 'stroke-dasharray': '2.5 2' }) + lines(18, 48, 34, 2, 5))
        .add(arrow(60, 38, 72, 48)).bot(86, 62, 22, { mood: 'dizzy' })
        .add(arrow(100, 50, 120, 36, { dash: true }))
        .add(tile(122, 16, 28, 24, text(136, 33, '$', 15, { display: true }))).add(el('circle', { cx: 150, cy: 16, r: 6, fill: N }) + el('text', { x: 150, y: 19, 'text-anchor': 'middle', 'font-size': 8, fill: C }, '!')).svg();
    },
    'rag': function () {
      return S().add(el('path', ink({ d: 'M14 24 Q28 20 40 26 Q52 20 66 24 V56 Q52 52 40 58 Q28 52 14 56 Z', fill: C })) + el('line', ink({ x1: 40, y1: 26, x2: 40, y2: 58 })) + lines(19, 32, 15, 3, 6) + lines(45, 32, 15, 3, 6))
        .add(arrow(70, 42, 80, 50)).bot(92, 62, 22, { dx: 1.5, dy: -1 })
        .add(bubble(106, 12, 48, 30, 'bl')).add(lines(113, 21, 24, 2, 6)).add(el('rect', { x: 138, y: 28, width: 12, height: 9, rx: 2, fill: B }) + text(144, 35, '1', 7)).svg();
    },
    'fine-tuning': function () {
      return S().add(el('rect', ink({ x: 12, y: 30, width: 22, height: 16, rx: 2, fill: T })) + el('rect', ink({ x: 16, y: 25, width: 22, height: 16, rx: 2, fill: C })) + el('rect', ink({ x: 20, y: 20, width: 22, height: 16, rx: 2, fill: C })) + star(31, 28, 4))
        .add(arrow(46, 32, 56, 40)).bot(76, 59, 28, { cap: true, mood: 'happy' })
        .add(el('circle', ink({ cx: 128, cy: 36, r: 15, fill: C })) + el('line', ink({ x1: 128, y1: 36, x2: 136, y2: 26, 'stroke-width': 3 })) + el('circle', { cx: 128, cy: 36, r: 3, fill: N }) +
          [-150, -110, -70, -30, 10].map(function (deg) { var a = deg * Math.PI / 180; return el('line', ink({ x1: f(128 + 19 * Math.cos(a)), y1: f(36 + 19 * Math.sin(a)), x2: f(128 + 23 * Math.cos(a)), y2: f(36 + 23 * Math.sin(a)), 'stroke-width': 1.8 })); }).join(''))
        .svg();
    },
    'open-closed': function () {
      return S().add(bot(39, 34, 18, { mood: 'happy' }))
        .add(el('path', ink({ d: 'M14 40 L4 30 M64 40 L74 30', fill: 'none' })) + el('rect', ink({ x: 14, y: 40, width: 50, height: 26, rx: 2, fill: T })))
        .add(el('rect', ink({ x: 96, y: 36, width: 50, height: 30, rx: 2, fill: T })) + el('path', ink({ d: 'M114 44 V38 a7 7 0 0 1 14 0 V44', fill: 'none', 'stroke-width': 2.6 })) + el('rect', ink({ x: 110, y: 44, width: 22, height: 16, rx: 3, fill: N })) + el('circle', { cx: 121, cy: 51, r: 2, fill: C }))
        .label(39, 'OPEN').label(121, 'CLOSED').svg();
    },
    'benchmark': function () {
      return S().add(doc(52, 8, 50, 56, 0) + [18, 30, 42, 54].map(function (y, i) { return (i < 3 ? check(58, y, 6) : text(61, y + 3, 'x', 8)) + lines(70, y, 24, 1); }).join(''))
        .add(el('circle', ink({ cx: 102, cy: 12, r: 10, fill: B })) + text(102, 15.5, 'A+', 8))
        .bot(132, 62, 22, { mood: 'happy' }).svg();
    },
    'gpu': function () {
      var pins = ''; for (var i = 0; i < 5; i++) { var p = 60 + i * 9; pins += el('line', ink({ x1: p, y1: 6, x2: p, y2: 12 })) + el('line', ink({ x1: p, y1: 62, x2: p, y2: 68 })); }
      for (i = 0; i < 4; i++) { var q = 20 + i * 11; pins += el('line', ink({ x1: 48, y1: q, x2: 54, y2: q })) + el('line', ink({ x1: 106, y1: q, x2: 112, y2: q })); }
      return S().add(pins + el('rect', ink({ x: 54, y: 12, width: 52, height: 50, rx: 5, fill: N })) + el('rect', { x: 66, y: 24, width: 28, height: 26, rx: 3, fill: B }) + el('path', { d: 'M82 28 L74 38 H80 L77 46 L86 35 H80 Z', fill: N }))
        .bot(138, 63, 20, { dx: -1.5, mood: 'wow' }).svg();
    },
    'data-center': function () {
      var r = ''; [16, 52, 88].forEach(function (x) { r += el('rect', ink({ x: x, y: 12, width: 30, height: 56, rx: 3, fill: N })); for (var j = 0; j < 4; j++) r += el('line', { x1: x + 5, y1: 22 + j * 11, x2: x + 18, y2: 22 + j * 11, stroke: T, 'stroke-width': 2, 'stroke-linecap': 'round' }) + el('circle', { cx: x + 24, cy: 22 + j * 11, r: 1.8, fill: B }); });
      return S().add(r).add(el('path', ink({ d: 'M140 12 L130 30 H138 L134 44 L148 24 H140 Z', fill: B })) + el('path', ink({ d: 'M141 50 Q148 58 148 62 A7 7 0 0 1 134 62 Q134 58 141 50 Z', fill: C }))).svg();
    },
    'scaling-laws': function () {
      return S().add(el('path', ink({ d: 'M16 8 V64 H150', fill: 'none' })) + el('path', ink({ d: 'M20 60 C56 58 86 44 116 24', fill: 'none', 'stroke-width': 2.6 })) + el('path', ink({ d: 'M116 24 C128 16 138 12 148 10', fill: 'none', 'stroke-dasharray': '3 3', opacity: .6 })) + text(148, 28, '?', 14, { display: true }))
        .add(bot(48, 50, 10) + bot(84, 40, 14) + bot(112, 20, 18, { mood: 'happy' })).svg();
    },
    'deepfake': function () {
      return S().o(40, 63, 13, { dx: 2 })
        .add(el('rect', ink({ x: 88, y: 10, width: 44, height: 56, rx: 7, fill: C })) + el('rect', { x: 93, y: 18, width: 34, height: 38, rx: 2, fill: T }))
        .add(oHead(110, 37, 11, { glitch: true })).add(el('path', ink({ d: 'M138 30 q4 7 0 14 M144 26 q7 11 0 22', fill: 'none', 'stroke-width': 1.8 }))).svg();
    },
    'alignment': function () {
      return S().add(el('circle', ink({ cx: 116, cy: 32, r: 22, fill: C })) + el('circle', ink({ cx: 116, cy: 32, r: 14, fill: T })) + el('circle', ink({ cx: 116, cy: 32, r: 6, fill: B })))
        .o(22, 64, 11, { dx: 2, dy: -1 }).bot(60, 61, 20, { dx: 2, dy: -1 })
        .add(arrow(32, 58, 109, 35, { dash: true }) + arrow(70, 48, 110, 34, { dash: true })).svg();
    },
    'agi': function () {
      return S().add(flag(84, 70, 34) + flag(114, 70, 44, C) + flag(144, 70, 28))
        .bot(36, 62, 22, { dx: 2 }).under(el('path', { d: 'M0 86 H160', stroke: C, 'stroke-width': 1.6, 'stroke-dasharray': '4 4', opacity: .8 })).svg();
    },
    'superintelligence': function () {
      return S().o(48, 63, 12, { dy: -2.5, dx: 2 }).bot(112, 46, 30, { h: 60 }).add(sparkle(138, 16, 5) + sparkle(86, 22, 4) + sparkle(142, 40, 3)).svg();
    }
  };
  return function (id) { return scenes[id] ? scenes[id]() : ''; };
})();
if (typeof module !== "undefined") module.exports = ART;
