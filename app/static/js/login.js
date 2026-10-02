(() => {
  const $ = s => document.querySelector(s);
  const fine = matchMedia('(pointer:fine)').matches;
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const mouse = { x: innerWidth / 2, y: innerHeight / 2 };

  /* ---------- loader ---------- */
  let n = 0;
  const num = $('#ldNum'), bar = $('#ldBar');
  (function tick() {
    n = Math.min(100, n + Math.random() * 7 + 2);
    num.textContent = Math.floor(n); bar.style.width = n + '%';
    if (n < 100) setTimeout(tick, 60);
    else setTimeout(() => { document.body.classList.remove('loading'); document.body.classList.add('ready'); }, 350);
  })();

  /* ---------- particles ---------- */
  const cv = $('#fx'), cx = cv.getContext('2d');
  let W, H, P = [];
  function size() {
    W = cv.width = innerWidth; H = cv.height = innerHeight;
    const count = Math.min(110, Math.floor(W * H / 14000));
    P = Array.from({ length: count }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35,
      r: Math.random() * 1.6 + .5, c: Math.random() > .5 ? '192,132,252' : '56,189,248'
    }));
  }
  size(); addEventListener('resize', size);
  function draw() {
    cx.clearRect(0, 0, W, H);
    for (const p of P) {
      const dx = mouse.x - p.x, dy = mouse.y - p.y, d = Math.hypot(dx, dy);
      if (d < 160) { p.vx -= dx / d * .012; p.vy -= dy / d * .012; }
      p.vx *= .995; p.vy *= .995;
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
      cx.beginPath(); cx.arc(p.x, p.y, p.r, 0, 7);
      cx.fillStyle = `rgba(${p.c},.9)`; cx.shadowBlur = 10; cx.shadowColor = `rgb(${p.c})`; cx.fill();
    }
    cx.shadowBlur = 0;
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) {
      const d = Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y);
      if (d < 120) { cx.strokeStyle = `rgba(124,92,255,${.22 * (1 - d / 120)})`; cx.lineWidth = 1;
        cx.beginPath(); cx.moveTo(P[i].x, P[i].y); cx.lineTo(P[j].x, P[j].y); cx.stroke(); }
    }
    if (!reduce) requestAnimationFrame(draw);
  }
  draw();

  /* ---------- mouse: cursor, 3D cube, card tilt ---------- */
  const dot = $('.cur-dot'), ring = $('.cur-ring'), scene = $('#scene'), card = $('#card');
  let rx = mouse.x, ry = mouse.y;
  addEventListener('mousemove', e => {
    mouse.x = e.clientX; mouse.y = e.clientY;
    const nx = e.clientX / innerWidth - .5, ny = e.clientY / innerHeight - .5;
    scene.style.setProperty('--ry', nx * 70 + 'deg');
    scene.style.setProperty('--rx', -ny * 70 + 'deg');
    if (fine) dot.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
    const r = card.getBoundingClientRect();
    card.style.setProperty('--mx', e.clientX - r.left + 'px');
    card.style.setProperty('--my', e.clientY - r.top + 'px');
    const inside = e.clientX > r.left && e.clientX < r.right && e.clientY > r.top && e.clientY < r.bottom;
    card.style.setProperty('--ty', inside ? ((e.clientX - r.left) / r.width - .5) * 8 + 'deg' : '0deg');
    card.style.setProperty('--tx', inside ? -((e.clientY - r.top) / r.height - .5) * 8 + 'deg' : '0deg');
  });
  if (fine) {
    (function follow() {
      rx += (mouse.x - rx) * .16; ry += (mouse.y - ry) * .16;
      ring.style.transform = `translate(${rx}px,${ry}px)`;
      requestAnimationFrame(follow);
    })();
    document.querySelectorAll('input,button').forEach(el => {
      el.addEventListener('mouseenter', () => ring.classList.add('on'));
      el.addEventListener('mouseleave', () => ring.classList.remove('on'));
    });
  }

  /* ---------- form ---------- */
  const p = $('#p');
  $('#eye').addEventListener('click', () => { p.type = p.type === 'password' ? 'text' : 'password'; });
  $('#form').addEventListener('submit', () => $('#go').classList.add('busy'));
})();
