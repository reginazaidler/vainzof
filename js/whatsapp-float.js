(function () {
  var PHONE_URL = 'tel:0524520222';
  var WHATSAPP_URL = 'https://wa.me/972524520222';

  function hasMobileStickyCta() {
    return !!document.querySelector('.mobile-sticky-cta');
  }


  function hasDesktopWhatsappWidget() {
    return !!document.querySelector('.whatsapp-float');
  }

  function createWidget() {
    var link = document.createElement('a');
    link.href = WHATSAPP_URL;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'whatsapp-float fixed-whatsapp';
    link.setAttribute('aria-label', 'שליחת הודעה בוואטסאפ');
    link.innerHTML =
      '<svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true" focusable="false">' +
      '<path fill="currentColor" d="M16.02 3.2C8.94 3.2 3.2 8.9 3.2 15.95c0 2.48.72 4.9 2.08 6.96L3 29l6.29-2.2a12.85 12.85 0 0 0 6.73 1.85h.01c7.07 0 12.8-5.7 12.8-12.75 0-3.41-1.34-6.62-3.8-9.03a12.87 12.87 0 0 0-9-3.67Zm0 23.29h-.01a10.7 10.7 0 0 1-5.44-1.49l-.39-.23-3.74 1.31 1.33-3.63-.25-.37a10.58 10.58 0 0 1-1.65-5.62c0-5.85 4.78-10.6 10.66-10.6 2.85 0 5.53 1.1 7.55 3.11a10.51 10.51 0 0 1 3.14 7.5c0 5.85-4.79 10.6-10.66 10.6Zm5.85-7.95c-.32-.16-1.89-.93-2.18-1.03-.3-.11-.51-.16-.72.16-.22.32-.83 1.03-1.02 1.24-.19.22-.37.24-.69.08-.32-.16-1.35-.49-2.57-1.55-.95-.84-1.59-1.86-1.78-2.18-.19-.32-.02-.49.14-.65.14-.14.32-.37.49-.56.16-.19.22-.32.32-.53.11-.22.05-.4-.03-.56-.08-.16-.72-1.72-.99-2.35-.26-.62-.52-.53-.72-.54h-.61c-.22 0-.56.08-.85.4-.3.32-1.12 1.1-1.12 2.69s1.15 3.11 1.31 3.32c.16.21 2.24 3.57 5.52 4.86.78.31 1.39.5 1.87.64.79.25 1.5.21 2.07.13.63-.09 1.89-.77 2.16-1.52.26-.75.26-1.4.19-1.52-.08-.12-.29-.19-.61-.35Z"/>' +
      '</svg>';

    document.body.appendChild(link);
  }


  function createMobileStickyCta() {
    var wrapper = document.createElement('div');
    wrapper.className = 'mobile-sticky-cta';
    wrapper.setAttribute('aria-label', 'פעולות מהירות במובייל');

    var phoneLink = document.createElement('a');
    phoneLink.href = PHONE_URL;
    phoneLink.className = 'mobile-sticky-cta__btn mobile-sticky-cta__btn--phone';
    phoneLink.setAttribute('aria-label', 'התקשרות מהירה');
    phoneLink.textContent = 'התקשרו עכשיו';

    var whatsappLink = document.createElement('a');
    whatsappLink.href = WHATSAPP_URL;
    whatsappLink.target = '_blank';
    whatsappLink.rel = 'noopener noreferrer';
    whatsappLink.className = 'mobile-sticky-cta__btn mobile-sticky-cta__btn--whatsapp';
    whatsappLink.setAttribute('aria-label', 'שליחת הודעה בוואטסאפ');
    whatsappLink.textContent = 'WhatsApp';

    wrapper.appendChild(phoneLink);
    wrapper.appendChild(whatsappLink);
    document.body.appendChild(wrapper);
  }

  function isKnowledgeHref(href) {
    if (!href) return false;
    return (
      href.indexOf('articles.html') !== -1 ||
      href.indexOf('faq.html') !== -1 ||
      href.indexOf('calculator.html') !== -1 ||
      href.indexOf('media.html') !== -1
    );
  }

  function enhanceLegacyMobileMenu() {
    var mobileMenu = document.getElementById('mobileMenu');
    var menuBtn = document.getElementById('menuBtn');

    if (!mobileMenu || !menuBtn) return;
    if (mobileMenu.classList.contains('mobile-drawer')) return;
    if (mobileMenu.querySelector('#mobileKnowledgeToggle')) return;

    mobileMenu.classList.add('mobile-menu-enhanced');
    menuBtn.classList.add('mobile-menu-toggle');

    var links = Array.prototype.slice.call(mobileMenu.querySelectorAll('a'));
    links.forEach(function (link) {
      link.classList.add('mobile-nav-link');
    });

    var knowledgeLinks = links.filter(function (link) {
      return isKnowledgeHref(link.getAttribute('href'));
    });

    if (!knowledgeLinks.length) return;

    var firstKnowledgeLink = knowledgeLinks[0];

    var knowledgeToggle = document.createElement('button');
    knowledgeToggle.id = 'mobileKnowledgeToggle';
    knowledgeToggle.type = 'button';
    knowledgeToggle.className = 'mobile-nav-link mobile-nav-accordion-toggle';
    knowledgeToggle.setAttribute('aria-expanded', 'false');
    knowledgeToggle.setAttribute('aria-controls', 'mobileKnowledgeMenu');
    knowledgeToggle.innerHTML =
      '<span class="mobile-nav-accordion-toggle__label">מרכז ידע</span><span class="mobile-nav-accordion-toggle__icon" aria-hidden="true">▾</span>';

    var knowledgeMenu = document.createElement('div');
    knowledgeMenu.id = 'mobileKnowledgeMenu';
    knowledgeMenu.className = 'mobile-subnav';
    knowledgeMenu.hidden = true;

    mobileMenu.insertBefore(knowledgeToggle, firstKnowledgeLink);
    mobileMenu.insertBefore(knowledgeMenu, firstKnowledgeLink);

    knowledgeLinks.forEach(function (link) {
      link.classList.remove('mobile-nav-link');
      link.classList.add('mobile-subnav-link');
      knowledgeMenu.appendChild(link);
    });

    knowledgeToggle.addEventListener('click', function () {
      var expanded = knowledgeToggle.getAttribute('aria-expanded') === 'true';
      knowledgeToggle.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      knowledgeMenu.hidden = expanded;
    });
  }

  function createKnowledgeDropdown() {
    var dropdown = document.createElement('div');
    dropdown.className = 'nav-dropdown';

    var trigger = document.createElement('button');
    trigger.className = 'nav-dropdown__trigger';
    trigger.type = 'button';
    trigger.innerHTML = 'מרכז ידע <span aria-hidden="true">▾</span>';

    var menu = document.createElement('div');
    menu.className = 'nav-dropdown__menu';
    menu.setAttribute('role', 'menu');
    menu.setAttribute('aria-label', 'מרכז ידע');

    [
      { href: 'articles.html', label: 'מאמרים מקצועיים' },
      { href: 'faq.html', label: 'שאלות ותשובות' },
      { href: 'calculator.html', label: 'מחשבון חיסכון' },
      { href: 'media.html', label: 'וידאו ומדיה' }
    ].forEach(function (item) {
      var link = document.createElement('a');
      link.href = item.href;
      link.className = 'nav-dropdown__item';
      link.setAttribute('role', 'menuitem');
      link.textContent = item.label;
      menu.appendChild(link);
    });

    dropdown.appendChild(trigger);
    dropdown.appendChild(menu);

    return dropdown;
  }

  function enhanceDesktopKnowledgeMenu() {
    var desktopNav = document.querySelector('.site-nav, .site-header nav.hidden[class~="lg:flex"]');

    if (!desktopNav) return;
    if (desktopNav.querySelector('.nav-dropdown')) return;

    var desktopLinks = Array.prototype.slice.call(desktopNav.querySelectorAll('a[href]'));

    desktopLinks.forEach(function (link) {
      if (isKnowledgeHref(link.getAttribute('href'))) {
        link.parentNode.removeChild(link);
      }
    });

    var insertBeforeNode = desktopNav.querySelector('a[href^="tel:"]') || desktopNav.querySelector('button');
    var dropdown = createKnowledgeDropdown();

    if (insertBeforeNode) {
      desktopNav.insertBefore(dropdown, insertBeforeNode);
      return;
    }

    desktopNav.appendChild(dropdown);
  }

  function init() {
    enhanceLegacyMobileMenu();
    enhanceDesktopKnowledgeMenu();

    if (!hasMobileStickyCta()) {
      createMobileStickyCta();
    }

    if (window.matchMedia('(min-width: 1024px)').matches && !hasDesktopWhatsappWidget()) {
      createWidget();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
