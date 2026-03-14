(function () {
  var PHONE_URL = 'tel:0524520222';

  function hasMobileStickyCta() {
    return !!document.querySelector('.mobile-sticky-cta');
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

    wrapper.appendChild(phoneLink);
    document.body.appendChild(wrapper);
  }

  function init() {
    if (!hasMobileStickyCta()) {
      createMobileStickyCta();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
