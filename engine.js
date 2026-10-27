/* ============================================================
 * frontend-art — pixel animation engine
 * One continuous, resolution-independent scene sampled onto a
 * pixel-box grid. URL params:
 *   ?px=6|10|16|24   pixel-box size  (default 10)
 *   &view=mobile     full-bleed portrait layout (default desktop)
 *   &site=1          website hero-text overlay (title + byline)
 * An artwork file just calls Art.mount({ name, slug, perspective, build }).
 * ============================================================ */
(function () {
  const P = new URLSearchParams(location.search);
  const PX = Math.max(2, Math.min(48, parseInt(P.get('px') || '10', 10)));
  const VIEW = P.get('view') === 'mobile' ? 'mobile' : 'desktop';
  const SITE = P.get('site') === '1';
  const W = VIEW === 'mobile' ? 540 : 960;
  const H = VIEW === 'mobile' ? 1170 : 640;
  const AR = W / H;

  // ---------- math helpers ----------
  const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
  const mix = (a, b, t) => a + (b - a) * t;
  const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
  const mixC = (a, b, t) => [mix(a[0], b[0], t), mix(a[1], b[1], t), mix(a[2], b[2], t)];
  const fract = (x) => x - Math.floor(x);
  const hash = (x, y) => { const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return s - Math.floor(s); };
  function vnoise(x, y) {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    const a = hash(xi, yi), b = hash(xi + 1, yi), c = hash(xi, yi + 1), d = hash(xi + 1, yi + 1);
    return mix(mix(a, b, u), mix(c, d, u), v);
  }
  function fbm(x, y) { return vnoise(x, y) * 0.6 + vnoise(x * 2.1 + 5.2, y * 2.1 - 1.3) * 0.3 + vnoise(x * 4.3, y * 4.3) * 0.1; }

  // ---------- injected presentation ----------
  const CSS = `
  :root{color-scheme:dark;}
  html,body{margin:0;height:100%;background:#0a0d12;}
  body{display:flex;align-items:center;justify-content:center;min-height:100vh;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:16px;box-sizing:border-box;}
  .stage{position:relative;width:min(960px,100%);}
  canvas{display:block;width:100%;height:auto;border-radius:14px;image-rendering:pixelated;
    box-shadow:0 24px 60px rgba(0,0,0,.55),inset 0 0 0 1px rgba(255,255,255,.05);background:#0d1417;}
  .hud{position:absolute;left:14px;bottom:12px;display:flex;gap:8px;align-items:center;
    font-size:12px;letter-spacing:.06em;color:#e6edef;text-shadow:0 1px 3px rgba(0,0,0,.85);pointer-events:none;flex-wrap:wrap;}
  .hud b{color:#8fe3d6;font-weight:600;}
  .chip{background:rgba(8,16,18,.6);border:1px solid rgba(143,227,214,.28);padding:3px 8px;border-radius:999px;backdrop-filter:blur(2px);}
  .tag{position:absolute;right:14px;top:12px;font-size:11px;letter-spacing:.14em;color:#9ec7bf;
    text-transform:uppercase;text-shadow:0 1px 3px rgba(0,0,0,.85);pointer-events:none;}
  body[data-view="mobile"]{padding:0;align-items:stretch;}
  body[data-view="mobile"] .stage{width:100vw;height:100vh;}
  body[data-view="mobile"] canvas{width:100vw;height:100vh;border-radius:0;object-fit:cover;box-shadow:none;}
  body[data-view="mobile"] .hud{left:12px;bottom:calc(12px + env(safe-area-inset-bottom));}
  body[data-view="mobile"] .tag{right:12px;top:calc(12px + env(safe-area-inset-top));}
  /* website hero overlay */
  .site{position:absolute;inset:0;pointer-events:none;border-radius:14px;overflow:hidden;
    display:flex;flex-direction:column;}
  body[data-view="mobile"] .site{border-radius:0;}
  .site .scrim{position:absolute;inset:0;background:
    linear-gradient(180deg,rgba(6,10,12,.55) 0%,rgba(6,10,12,0) 26%,rgba(6,10,12,0) 55%,rgba(6,10,12,.72) 100%);}
  .site nav{position:relative;display:flex;align-items:center;justify-content:space-between;
    padding:20px 26px;font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#f2f6f7;}
  .site nav .brand{font-weight:700;}
  .site nav .links{display:flex;gap:20px;opacity:.82;font-size:12px;}
  .site .hero{position:relative;margin-top:auto;padding:26px 30px 34px;}
  .site .kicker{font-size:12px;letter-spacing:.32em;text-transform:uppercase;color:#8fe3d6;margin-bottom:14px;}
  .site h1{margin:0;font-family:"Georgia",ui-serif,serif;font-weight:600;color:#fff;
    font-size:clamp(34px,7vw,76px);line-height:1.02;letter-spacing:-.01em;text-shadow:0 2px 24px rgba(0,0,0,.5);}
  .site .by{margin-top:16px;font-size:15px;letter-spacing:.04em;color:#dfe9ea;}
  .site .by b{color:#fff;font-weight:600;}
  .site .cta{margin-top:22px;display:inline-flex;gap:10px;align-items:center;font-size:13px;
    letter-spacing:.1em;text-transform:uppercase;color:#07110f;background:#8fe3d6;padding:11px 18px;border-radius:999px;font-weight:700;}
  body[data-view="mobile"] .site nav .links{display:none;}
  body[data-view="mobile"] .site h1{font-size:clamp(40px,12vw,64px);}
  body[data-view="mobile"] .site .hero{padding:24px 22px calc(40px + env(safe-area-inset-bottom));}
  `;

  function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

  const Art = {
    clamp, mix, smooth, mixC, fract, hash, vnoise, fbm,
    PX, VIEW, SITE, W, H, AR,
    mount(opts) {
      const style = document.createElement('style'); style.textContent = CSS; document.head.appendChild(style);
      document.body.dataset.view = VIEW;
      const root = document.getElementById('root') || document.body.appendChild(el('div'));
      const stage = el('div', 'stage'); root.appendChild(stage);
      const disp = el('canvas'); disp.width = W; disp.height = H; stage.appendChild(disp);

      const cols = Math.floor(W / PX), rows = Math.floor(H / PX);
      const sample = opts.build(VIEW, AR);

      if (SITE) {
        const site = el('div', 'site');
        site.appendChild(el('div', 'scrim'));
        const nav = el('nav');
        nav.appendChild(el('div', 'brand', 'NK&thinsp;/&thinsp;studio'));
        nav.appendChild(el('div', 'links', '<span>work</span><span>process</span><span>contact</span>'));
        site.appendChild(nav);
        const hero = el('div', 'hero');
        hero.appendChild(el('div', 'kicker', (opts.perspective || '') + ' &middot; ' + VIEW));
        hero.appendChild(el('h1', null, (opts.site && opts.site.title) || opts.name));
        hero.appendChild(el('div', 'by', 'by <b>' + ((opts.site && opts.site.body) || 'Nikhil Kulkarni') + '</b>'));
        hero.appendChild(el('div', 'cta', 'view piece →'));
        site.appendChild(hero);
        stage.appendChild(site);
      } else {
        const tag = el('div', 'tag', opts.perspective || ''); stage.appendChild(tag);
        const hud = el('div', 'hud');
        hud.appendChild(el('span', 'chip', opts.name.toUpperCase()));
        hud.appendChild(el('span', 'chip', '<b>pixel box </b>' + PX + 'px'));
        hud.appendChild(el('span', 'chip', cols + '×' + rows + ' grid'));
        stage.appendChild(hud);
      }

      const dctx = disp.getContext('2d'); dctx.imageSmoothingEnabled = false;
      const off = el('canvas'); off.width = cols; off.height = rows;
      const octx = off.getContext('2d');
      const img = octx.createImageData(cols, rows), data = img.data;
      const t0 = performance.now();
      function frame(now) {
        const t = (now - t0) / 1000;
        let p = 0;
        for (let cy = 0; cy < rows; cy++) {
          const v = (cy + 0.5) / rows;
          for (let cx = 0; cx < cols; cx++) {
            const u = (cx + 0.5) / cols * AR;
            const c = sample(u, v, t);
            data[p++] = c[0]; data[p++] = c[1]; data[p++] = c[2]; data[p++] = 255;
          }
        }
        octx.putImageData(img, 0, 0);
        dctx.drawImage(off, 0, 0, cols, rows, 0, 0, W, H);
        requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    }
  };
  window.Art = Art;
})();
