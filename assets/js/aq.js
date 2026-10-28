/* Al-Qastal: the gate opens (loader + page-to-page), sections arrive, the gates rail, the Jerusalem clock,
   the prototype forms and search. No library. */
(function () {
  var d = document.documentElement, ss;
  try { ss = sessionStorage; } catch (e) { ss = null; }
  var still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  d.classList.add('js');

  // ---------------------------------------------------------------- the loader ends
  if (d.classList.contains('js-load')) {
    var done = function () {
      d.classList.remove('js-load');
      if (ss) ss.setItem('aq-in', '1');
    };
    setTimeout(done, 2650);
  }

  // ---------------------------------------------------------------- the first story's door opens once the page is seen
  var hero = document.querySelector('[data-hero]');
  if (hero) {
    var open = function () { hero.classList.add('go'); };
    if (d.classList.contains('js-load')) setTimeout(open, 1750);       // as the loader's doorway grows
    else if (d.classList.contains('aq-arrive')) setTimeout(open, 380);  // after the page-to-page door
    else requestAnimationFrame(function () { requestAnimationFrame(open); });
  }

  // ---------------------------------------------------------------- page to page
  var nav = document.querySelector('.gate-nav .hole');
  if (d.classList.contains('aq-arrive') && nav) {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        d.classList.add('aq-open');
        setTimeout(function () { d.classList.remove('aq-arrive', 'aq-open'); }, 760);
      });
    });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || !nav || still || !ss) return;
    if (e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (a.target === '_blank' || a.hasAttribute('download')) return;
    var u = new URL(a.href, location.href);
    if (u.origin !== location.origin || (u.pathname === location.pathname && u.hash)) return;
    if (!/\.html$|\/$/.test(u.pathname)) return;
    e.preventDefault();
    ss.setItem('aq-nav', '1');
    nav.classList.add('from');
    d.classList.add('aq-leave');
    void nav.getBoundingClientRect();
    nav.classList.remove('from');
    setTimeout(function () { location.href = a.href; }, 360);
  });
  // back/forward from the cache: never leave the page shut
  addEventListener('pageshow', function (e) {
    if (e.persisted) d.classList.remove('aq-leave', 'aq-arrive', 'aq-open', 'js-load');
  });

  // ---------------------------------------------------------------- arrivals
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
    es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } });
  }, { rootMargin: '0px 0px -8% 0px' }) : null;
  document.querySelectorAll('.rv,.sec-h').forEach(function (el) { io ? io.observe(el) : el.classList.add('in'); });

  // ---------------------------------------------------------------- the gates slider (Swiper, right to left)
  var sw = document.querySelector('[data-gates]');
  if (sw && window.Swiper) {
    var box = sw.closest('[data-rail]'), now = box.querySelector('[data-now]');
    var two = function (n) { return (n < 10 ? '0' : '') + n; };
    new Swiper(sw, {
      slidesPerView: 1.3, spaceBetween: 16, speed: still ? 0 : 700, grabCursor: true,
      watchSlidesProgress: true, keyboard: { enabled: true, onlyInViewport: true },
      navigation: { prevEl: box.querySelector('[data-prev]'), nextEl: box.querySelector('[data-next]') },
      pagination: { el: box.querySelector('.gates-prog'), type: 'progressbar' },
      a11y: { prevSlideMessage: 'الأبواب السابقة', nextSlideMessage: 'أبواب أخرى', slideLabelMessage: 'باب {{index}} من {{slidesLength}}' },
      breakpoints: { 640: { slidesPerView: 2.3, spaceBetween: 20 }, 900: { slidesPerView: 3.3, spaceBetween: 22 }, 1200: { slidesPerView: 4.3, spaceBetween: 24 } },
      on: { slideChange: function (s) { if (now) now.textContent = two(s.realIndex + 1); } }
    });
  }

  // ---------------------------------------------------------------- the gates rail without Swiper: scroll by two doors
  document.querySelectorAll('[data-rail]').forEach(function (box) {
    if (box.querySelector('.swiper-initialized')) return;
    var rail = box.querySelector('.rail'), prev = box.querySelector('[data-prev]'), next = box.querySelector('[data-next]');
    if (!rail || !prev) return;
    var step = function () { var li = rail.querySelector('li'); return li ? li.getBoundingClientRect().width + 20 : 300; };
    // right to left: the rail starts at its right edge, scrollLeft runs from 0 down to negative
    var dir = getComputedStyle(rail).direction === 'rtl' ? -1 : 1;
    var sync = function () {
      var x = Math.abs(rail.scrollLeft);
      prev.disabled = x < 8;
      next.disabled = x + rail.clientWidth > rail.scrollWidth - 8;
    };
    prev.addEventListener('click', function () { rail.scrollBy({ left: -dir * step() * 2, behavior: still ? 'auto' : 'smooth' }); });
    next.addEventListener('click', function () { rail.scrollBy({ left: dir * step() * 2, behavior: still ? 'auto' : 'smooth' }); });
    rail.addEventListener('scroll', sync, { passive: true });
    addEventListener('resize', sync);
    sync();
  });

  // ---------------------------------------------------------------- Jerusalem time
  var clock = document.querySelector('[data-clock]');
  if (clock && window.Intl) {
    var f = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Jerusalem', hour: '2-digit', minute: '2-digit' });
    var tick = function () { clock.textContent = 'القدس ' + f.format(new Date()); };
    tick();
    setInterval(tick, 30000);
  }

  // ---------------------------------------------------------------- prototype forms
  document.querySelectorAll('form[data-proto]').forEach(function (fm) {
    fm.addEventListener('submit', function (e) {
      e.preventDefault();
      var m = fm.querySelector('.msg') || (fm.nextElementSibling && fm.nextElementSibling.classList.contains('msg') ? fm.nextElementSibling : null);
      if (!fm.checkValidity()) { fm.reportValidity(); return; }
      if (m) m.textContent = fm.getAttribute('data-proto') || 'وصلت. هذا نموذج تصميم، فلم يرسل شيء.';
      fm.reset();
    });
  });
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.textContent;
      (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () {
        b.textContent = 'نسخ الرابط';
      }, function () { b.textContent = 'انسخ العنوان من المتصفح'; });
      setTimeout(function () { b.textContent = t; }, 1800);
    });
  });

  // ---------------------------------------------------------------- search (the index is built with the site)
  var sf = document.querySelector('[data-search]');
  if (sf) {
    var input = sf.querySelector('input'), out = document.querySelector('[data-results]'), idx = null;
    var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var run = function () {
      var q = input.value.trim().toLowerCase();
      history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) : location.pathname);
      if (!idx) return;
      if (!q) { out.innerHTML = ''; return; }
      var words = q.split(/\s+/);
      var hits = idx.filter(function (s) { var t = s.t.toLowerCase(); return words.every(function (w) { return t.indexOf(w) > -1; }); });
      out.innerHTML = '<p class="n" role="status">' + (hits.length ? hits.length + ' ' + (hits.length > 2 && hits.length < 11 ? 'أخبار' : 'خبر') : 'لا نتائج') + ' عن «' + esc(q) + '»</p>' +
        '<ul class="list">' + hits.map(function (s) {
          return '<li><p class="kick"><span class="c" style="--cc:' + s.cc + '">' + esc(s.c) + '</span><span>' + esc(s.p) + '</span><time>' + esc(s.d) + '</time></p>' +
            '<h3 class="hl" style="font-size:20px;margin-top:6px"><a href="' + s.u + '">' + esc(s.h) + '</a></h3></li>';
        }).join('') + '</ul>';
    };
    fetch(sf.getAttribute('data-search')).then(function (r) { return r.json(); }).then(function (j) {
      idx = j;
      var q = new URLSearchParams(location.search).get('q');
      if (q) input.value = q;
      run();
    }).catch(function () {
      out.innerHTML = '<p class="n" role="status">تعذر تحميل فهرس البحث. حاول بعد قليل.</p>';
    });
    sf.addEventListener('submit', function (e) { e.preventDefault(); run(); });
    input.addEventListener('input', run);
    document.querySelectorAll('[data-q]').forEach(function (b) {
      b.addEventListener('click', function () { input.value = b.getAttribute('data-q'); run(); input.focus(); });
    });
  }
})();
