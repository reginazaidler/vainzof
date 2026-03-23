(function () {
  function isDrawerMenu(menu) {
    return !!menu && menu.classList.contains('mobile-drawer');
  }

  function setMenuState(menuBtn, mobileMenu, shouldOpen) {
    if (!menuBtn || !mobileMenu) return;

    if (isDrawerMenu(mobileMenu)) {
      mobileMenu.classList.toggle('is-open', shouldOpen);
    } else {
      mobileMenu.classList.toggle('hidden', !shouldOpen);
    }

    menuBtn.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
    document.body.classList.toggle('overflow-hidden', shouldOpen && isDrawerMenu(mobileMenu));
  }

  function isMenuOpen(menuBtn, mobileMenu) {
    if (!menuBtn || !mobileMenu) return false;
    if (isDrawerMenu(mobileMenu)) {
      return mobileMenu.classList.contains('is-open');
    }
    return !mobileMenu.classList.contains('hidden');
  }

  function initMobileMenu() {
    var menuBtn = document.getElementById('menuBtn');
    var mobileMenu = document.getElementById('mobileMenu');
    if (!menuBtn || !mobileMenu) return;

    if (!menuBtn.hasAttribute('aria-controls')) {
      menuBtn.setAttribute('aria-controls', 'mobileMenu');
    }
    if (!menuBtn.hasAttribute('aria-expanded')) {
      menuBtn.setAttribute('aria-expanded', 'false');
    }

    menuBtn.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
      var nextState = !isMenuOpen(menuBtn, mobileMenu);
      setMenuState(menuBtn, mobileMenu, nextState);
    }, true);

    mobileMenu.addEventListener('click', function (event) {
      var actionTarget = event.target.closest('a, button.mobile-contact-cta');
      if (!actionTarget) return;
      setMenuState(menuBtn, mobileMenu, false);
    });

    document.addEventListener('click', function (event) {
      if (!isMenuOpen(menuBtn, mobileMenu)) return;
      if (mobileMenu.contains(event.target) || menuBtn.contains(event.target)) return;
      setMenuState(menuBtn, mobileMenu, false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && isMenuOpen(menuBtn, mobileMenu)) {
        setMenuState(menuBtn, mobileMenu, false);
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 1024) {
        setMenuState(menuBtn, mobileMenu, false);
      }
    });
  }

  function initDesktopKnowledgeMenu() {
    var dropdown = document.querySelector('.nav-dropdown');
    if (!dropdown) return;

    var trigger = dropdown.querySelector('.nav-dropdown__trigger');
    var menu = dropdown.querySelector('.nav-dropdown__menu');
    if (!trigger || !menu) return;

    if (!menu.id) {
      menu.id = 'desktopKnowledgeMenu';
    }

    trigger.setAttribute('aria-expanded', 'false');
    trigger.setAttribute('aria-controls', menu.id);
    trigger.setAttribute('aria-haspopup', 'true');

    function setOpenState(shouldOpen) {
      dropdown.classList.toggle('is-open', shouldOpen);
      trigger.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
    }

    trigger.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      var isOpen = dropdown.classList.contains('is-open');
      setOpenState(!isOpen);
    });

    document.addEventListener('click', function (event) {
      if (!dropdown.contains(event.target)) {
        setOpenState(false);
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        setOpenState(false);
      }
    });
  }

  function init() {
    initMobileMenu();
    initDesktopKnowledgeMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
