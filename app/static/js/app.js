(() => {
  const $ = s => document.querySelector(s);
  const fine = matchMedia('(pointer:fine)').matches;
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const mouse = { x: innerWidth / 2, y: innerHeight / 2 };

  let n = 0;
  (function tick() {
    n = Math.min(100, n + Math.random() * 12 + 4);
    $('#ldNum').textContent = Math.floor(n); $('#ldBar').style.width = n + '%';
    if (n < 100) setTimeout(tick, 50);
    else setTimeout(() => { document.body.classList.remove('loading'); document.body.classList.add('ready'); }, 250);
  })();

  const cv = $('#fx'), cx = cv.getContext('2d'); let W, H, P = [];
  function size() {
    W = cv.width = innerWidth; H = cv.height = innerHeight;
    P = Array.from({ length: Math.min(80, W * H / 18000 | 0) }, () => ({
      x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .3, vy: (Math.random() - .5) * .3,
      r: Math.random() * 1.4 + .4, c: Math.random() > .5 ? '192,132,252' : '56,189,248' }));
  }
  size(); addEventListener('resize', size);
  (function draw() {
    cx.clearRect(0, 0, W, H);
    for (const p of P) {
      const dx = mouse.x - p.x, dy = mouse.y - p.y, d = Math.hypot(dx, dy);
      if (d < 150) { p.vx -= dx / d * .01; p.vy -= dy / d * .01; }
      p.vx *= .995; p.vy *= .995; p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1; if (p.y < 0 || p.y > H) p.vy *= -1;
      cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, 7); cx.fillStyle = `rgba(${p.c},.8)`; cx.fill();
    }
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) {
      const d = Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y);
      if (d < 110) { cx.strokeStyle = `rgba(124,92,255,${.18 * (1 - d / 110)})`; cx.beginPath();
        cx.moveTo(P[i].x, P[i].y); cx.lineTo(P[j].x, P[j].y); cx.stroke(); }
    }
    if (!reduce) requestAnimationFrame(draw);
  })();

  const dot = $('.cur-dot'), ring = $('.cur-ring'); let rx = 0, ry = 0;
  addEventListener('mousemove', e => {
    mouse.x = e.clientX; mouse.y = e.clientY;
    if (fine) dot.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
    document.querySelectorAll('[data-tilt]').forEach(el => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', e.clientX - r.left + 'px'); el.style.setProperty('--my', e.clientY - r.top + 'px');
    });
  });
  if (fine) {
    (function f() { rx += (mouse.x - rx) * .16; ry += (mouse.y - ry) * .16;
      ring.style.transform = `translate(${rx}px,${ry}px)`; requestAnimationFrame(f); })();
    document.addEventListener('mouseover', e => ring.classList.toggle('on', !!e.target.closest('a,button,input,.stat')));
  }
  $('#burger').addEventListener('click', () => document.body.classList.toggle('menu'));
  const nb = $('#nb'); let last = null;
  function toast(t) {
    const d = document.createElement('div'); d.className = 'toast'; d.textContent = '🔔 ' + t;
    document.body.appendChild(d); setTimeout(() => d.remove(), 6000);
  }
  async function poll() {
    try {
      const r = await fetch('/notifications/count'); if (!r.ok) return;
      const { n, latest } = await r.json();
      nb.textContent = n || ''; nb.style.display = n ? '' : 'none';
      if (last !== null && n > last) toast(latest);
      last = n;
    } catch (e) {}
  }
  poll(); setInterval(poll, 15000);
})();
