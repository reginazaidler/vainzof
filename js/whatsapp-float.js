(function () {
  var PHONE_URL = 'tel:0524520222';
  var WHATSAPP_URL = 'https://wa.me/972524520222';

  function hasMobileStickyCta() {
    return !!document.querySelector('.mobile-sticky-cta');
  }


  function hasDesktopStickyCta() {
    return !!document.querySelector('.desktop-sticky-cta');
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

  function createDesktopStickyCta() {
    var link = document.createElement('a');
    link.href = WHATSAPP_URL;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'desktop-sticky-cta';
    link.setAttribute('aria-label', 'שליחת הודעה בוואטסאפ לתיאום בדיקה אישית');
    link.textContent = 'לתיאום בדיקה אישית';

    document.body.appendChild(link);
  }

  function init() {
    if (!hasMobileStickyCta()) {
      createMobileStickyCta();
    }

    if (!hasDesktopStickyCta()) {
      createDesktopStickyCta();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
