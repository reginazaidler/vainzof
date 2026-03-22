(function () {
  var SUPPORTED_LANGS = {
    he: { label: 'עברית', short: 'HE' },
    ru: { label: 'Русский', short: 'RU' }
  };

  function getCurrentUrl() {
    if (!window.location) return '';
    return window.location.href;
  }

  function buildGoogleTranslateUrl(targetLang) {
    return 'https://translate.google.com/translate?sl=he&tl=' + encodeURIComponent(targetLang) + '&u=' + encodeURIComponent(getCurrentUrl());
  }

  function isLocalPreview() {
    return window.location.protocol === 'file:' || /^(localhost|127\.0\.0\.1)$/i.test(window.location.hostname);
  }

  function navigateTo(lang) {
    if (lang === 'he') {
      try {
        sessionStorage.removeItem('preferredSiteLanguage');
      } catch (error) {}
      window.location.href = getCurrentUrl();
      return;
    }

    try {
      sessionStorage.setItem('preferredSiteLanguage', lang);
    } catch (error) {}

    if (isLocalPreview()) {
      window.alert('התרגום לרוסית עובד על הדומיין החי של האתר דרך Google Translate. בתצוגה מקומית אי אפשר להפעיל את ההפניה הזאת.');
      return;
    }

    window.location.href = buildGoogleTranslateUrl(lang);
  }

  function createButton(lang, currentLang) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'site-language-switcher__option';
    button.textContent = SUPPORTED_LANGS[lang].short;
    button.setAttribute('aria-label', 'הצג את האתר ב' + SUPPORTED_LANGS[lang].label);
    if (lang === currentLang) {
      button.classList.add('is-active');
      button.setAttribute('aria-pressed', 'true');
    } else {
      button.setAttribute('aria-pressed', 'false');
    }

    button.addEventListener('click', function () {
      navigateTo(lang);
    });

    return button;
  }

  function createNote() {
    var note = document.createElement('p');
    note.className = 'site-language-switcher__note';
    note.textContent = 'RU פועל בתרגום אוטומטי מלא דרך Google Translate.';
    return note;
  }

  function mountSwitcher() {
    var host = document.querySelector('.site-header__inner') || document.querySelector('.site-topbar__inner') || document.body;
    if (!host || document.querySelector('.site-language-switcher')) return;

    var currentLang = 'he';
    try {
      currentLang = sessionStorage.getItem('preferredSiteLanguage') || 'he';
    } catch (error) {}

    var wrapper = document.createElement('div');
    wrapper.className = 'site-language-switcher';
    wrapper.setAttribute('aria-label', 'בחירת שפה');

    var label = document.createElement('span');
    label.className = 'site-language-switcher__label';
    label.textContent = 'שפה';
    wrapper.appendChild(label);

    var controls = document.createElement('div');
    controls.className = 'site-language-switcher__controls';
    controls.appendChild(createButton('he', currentLang));
    controls.appendChild(createButton('ru', currentLang));
    wrapper.appendChild(controls);
    wrapper.appendChild(createNote());

    host.appendChild(wrapper);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountSwitcher);
  } else {
    mountSwitcher();
  }
})();
