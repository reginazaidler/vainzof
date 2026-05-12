(function () {
  function openWA() {
    window.open('https://wa.me/972524520222', '_blank', 'noopener,noreferrer');
  }
  function handleContact(e) {
    e.preventDefault();
    const modal = document.getElementById('contactModal');
    if (modal) {
      modal.classList.remove('hidden', 'opacity-0');
      modal.classList.add('opacity-100');
      modal.style.display = 'flex';
    } else {
      openWA();
    }
  }
  document.getElementById('openContactDesktop')?.addEventListener('click', handleContact);
  document.getElementById('openContactMobile')?.addEventListener('click', handleContact);
})();
