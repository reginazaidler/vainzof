(function () {
  const currentScript = document.currentScript;
  if (!currentScript) return;

  const footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.innerHTML = `
    <div class="container-clean site-footer__inner">
      <div class="site-footer__meta">
        <p>יובל ויינזוף © 2026</p>
        <p class="site-footer__note">סוכן ביטוח פנסיוני מורשה · <a href="tel:0524520222">052-4520222</a></p>
        <p class="site-footer__experience">מעל 18 שנות נסיון מעשי בחברות ביטוח מובילות</p>
      </div>

      <nav class="site-footer__nav" aria-label="ניווט תחתון">
        <a href="index.html">דף הבית</a>
        <a href="about.html">קצת עלי</a>
        <a href="insurance-types.html">סוגי ביטוחים</a>
        <a href="pension-guide.html">איך עושים סדר בפנסיה ובביטוחים</a>
        <a href="faq.html">FAQ</a>
        <a href="articles.html">מאמרים מקצועיים על פנסיה וביטוחים</a>
        <a href="calculator.html">מחשבון חיסכון</a>
        <a href="media.html">וידאו</a>
        <a href="reviews.html">לקוחות ממליצים</a>
        <div class="site-footer__city-links" data-city-links>
          <a href="sochen-bituach-herzliya.html">סוכן ביטוח בהרצליה</a>
          <a href="sochen-bituach-petah-tikva.html">סוכן ביטוח בפתח תקווה</a>
          <a href="sochen-bituach-ashdod.html">סוכן ביטוח באשדוד</a>
        </div>
      </nav>

      <div class="site-footer__social">
        <a href="https://www.facebook.com/yuval.vainzof" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
        </a>
        <a href="https://www.instagram.com/vainzof/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 1.366.062 2.633.332 3.608 1.308.975.975 1.245 2.242 1.308 3.608.058 1.266.07 1.646.07 4.85s-.012 3.584-.07 4.85c-.063 1.366-.33 2.633-1.308 3.608-.975.975-2.242 1.245-3.608 1.308-1.266.058-1.646.07-4.85.07s-3.584-.012-4.85-.07c-1.366-.063-2.633-.33-3.608-1.308-.975-.975-1.245-2.242-1.308-3.608-.058-1.266-.07-1.646-.07-4.85s.012-3.584.07-4.85c.062-1.366.33-2.633 1.308-3.608.975-.975 2.242-1.245 3.608-1.308 1.266-.058 1.646-.07 4.85-.07zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
        </a>
        <a href="https://www.tiktok.com/@vainzof" target="_blank" rel="noopener noreferrer" aria-label="TikTok">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.9-.32-1.98-.23-2.81.33-.85.51-1.44 1.42-1.58 2.41-.18 1.15.15 2.37.91 3.25.75.92 1.98 1.45 3.16 1.45 1.11.03 2.21-.39 3.01-1.14.71-.62 1.15-1.5 1.25-2.43.05-1.56.02-3.13.02-4.69.01-4.71-.01-9.42-.01-14.13z"/></svg>
        </a>
        <a href="mailto:yuval@vainzof.co.il" aria-label="Email">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M1.5 6.75A2.25 2.25 0 0 1 3.75 4.5h16.5a2.25 2.25 0 0 1 2.25 2.25v10.5a2.25 2.25 0 0 1-2.25 2.25H3.75A2.25 2.25 0 0 1 1.5 17.25V6.75Zm2.682-.75 7.818 5.863L19.818 6H4.182Zm15.318 1.875-7.049 5.287a.75.75 0 0 1-.9 0L4.5 7.875V17.25a.75.75 0 0 0 .75.75h14.25a.75.75 0 0 0 .75-.75V7.875Z"/></svg>
        </a>
      </div>
    </div>
  `;

  const currentPage = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const cityPages = [
    'sochen-bituach-herzliya.html',
    'sochen-bituach-petah-tikva.html',
    'sochen-bituach-ashdod.html'
  ];
  const cityLinksGroup = footer.querySelector('[data-city-links]');
  if (cityLinksGroup) {
    cityLinksGroup.querySelectorAll('a').forEach((link) => {
      const href = (link.getAttribute('href') || '').toLowerCase();
      if (cityPages.includes(currentPage) && href !== currentPage) {
        link.remove();
      }
    });

    if (!cityLinksGroup.querySelector('a')) {
      cityLinksGroup.remove();
    }
  }
  footer.querySelectorAll('.site-footer__nav a').forEach((link) => {
    const href = (link.getAttribute('href') || '').toLowerCase();
    if (href === currentPage) {
      link.classList.add('is-active');
    }
  });


  currentScript.replaceWith(footer);
})();
