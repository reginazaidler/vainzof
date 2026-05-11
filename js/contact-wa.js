(function () {
  function openWA() {
    window.open('https://wa.me/972524520222', '_blank', 'noopener,noreferrer');
  }
  document.getElementById('openContactDesktop')?.addEventListener('click', openWA);
  document.getElementById('openContactMobile')?.addEventListener('click', openWA);
})();
