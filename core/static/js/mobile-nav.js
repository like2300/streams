document.addEventListener('DOMContentLoaded', () => {
  try {
    const menuToggle = document.getElementById('menu-toggle');
    const searchToggle = document.getElementById('search-toggle');
    const closeSearch = document.getElementById('close-search');
    const mobileMenu = document.getElementById('mobile-menu');
    const searchPopup = document.getElementById('search-popup');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const closeButtons = document.querySelectorAll('#mobile-menu a, #mobile-menu button');

    if (!menuToggle || !searchToggle || !closeSearch || !mobileMenu || !searchPopup || !mobileMenuOverlay) {
      console.warn('Mobile navigation elements not found. Skipping mobile nav script.');
      return;
    }

    // Fonction pour fermer le menu mobile
    function closeMobileMenu() {
      if (mobileMenu) {
        mobileMenu.classList.remove('mobile-menu-open');
      }
      if (mobileMenuOverlay) {
        mobileMenuOverlay.classList.remove('open');
      }
      document.body.style.overflow = '';
    }

    // Fonction pour fermer le popup de recherche
    function closeSearchPopup() {
      if (searchPopup) {
        searchPopup.classList.remove('search-popup-open');
      }
      document.body.style.overflow = '';
    }

    // Ouvrir le menu ☰
    menuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (mobileMenu) {
        mobileMenu.classList.add('mobile-menu-open');
      }
      if (mobileMenuOverlay) {
        mobileMenuOverlay.classList.add('open');
      }
      document.body.style.overflow = 'hidden';
      
      // Fermer recherche si ouverte
      closeSearchPopup();
    });

    // Ouvrir la recherche 🔍
    searchToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (searchPopup) {
        searchPopup.classList.add('search-popup-open');
      }
      document.body.style.overflow = 'hidden';
      
      // Fermer menu si ouvert
      closeMobileMenu();
    });

    // Fermer la recherche avec ✕
    closeSearch.addEventListener('click', (e) => {
      e.stopPropagation();
      closeSearchPopup();
    });

    // Fermer le menu quand on clique sur l'overlay
    mobileMenuOverlay.addEventListener('click', (e) => {
      e.stopPropagation();
      closeMobileMenu();
    });

    // Fermer les menus quand on clique sur un lien
    closeButtons.forEach(button => {
      button.addEventListener('click', () => {
        closeMobileMenu();
      });
    });

    // Fermer avec ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (searchPopup && searchPopup.classList.contains('search-popup-open')) {
          closeSearchPopup();
        }
        if (mobileMenu && mobileMenu.classList.contains('mobile-menu-open')) {
          closeMobileMenu();
        }
      }
    });

    // Fermer le menu quand on clique à l'extérieur
    document.addEventListener('click', (e) => {
      if (mobileMenu && !mobileMenu.contains(e.target) && !menuToggle.contains(e.target) && mobileMenu.classList.contains('mobile-menu-open')) {
        closeMobileMenu();
      }
      
      if (searchPopup && !searchPopup.contains(e.target) && !searchToggle.contains(e.target) && searchPopup.classList.contains('search-popup-open')) {
        closeSearchPopup();
      }
    });

    // Empêcher la propagation des clics à l'intérieur des menus
    if (mobileMenu) {
      mobileMenu.addEventListener('click', (e) => {
        e.stopPropagation();
      });
    }
    
    if (searchPopup) {
      searchPopup.addEventListener('click', (e) => {
        e.stopPropagation();
      });
    }
  } catch (error) {
    console.error('An error occurred in the mobile navigation script:', error);
  }
});