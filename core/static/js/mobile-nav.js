// Améliorations de la navigation mobile pour Pornflixe

document.addEventListener('DOMContentLoaded', function() {
  // Éléments du DOM
  const menuToggle = document.getElementById('menu-toggle');
  const searchToggle = document.getElementById('search-toggle');
  const closeSearch = document.getElementById('close-search');
  const mobileMenu = document.getElementById('mobile-menu');
  const searchPopup = document.getElementById('search-popup');
  const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
  
  // Vérifier que tous les éléments existent
  if (!menuToggle || !searchToggle || !mobileMenu || !searchPopup) {
    console.warn('Certains éléments de navigation mobile sont manquants');
    return;
  }

  // Fonction pour fermer le menu mobile
  function closeMobileMenu() {
    mobileMenu.classList.remove('mobile-menu-open');
    if (mobileMenuOverlay) {
      mobileMenuOverlay.classList.remove('open');
    }
    document.body.style.overflow = '';
  }

  // Fonction pour fermer le popup de recherche
  function closeSearchPopup() {
    searchPopup.classList.remove('search-popup-open');
    document.body.style.overflow = '';
  }

  // Fonction pour ouvrir le menu mobile
  function openMobileMenu() {
    mobileMenu.classList.add('mobile-menu-open');
    if (mobileMenuOverlay) {
      mobileMenuOverlay.classList.add('open');
    }
    document.body.style.overflow = 'hidden';
    
    // Fermer recherche si ouverte
    closeSearchPopup();
  }

  // Fonction pour ouvrir le popup de recherche
  function openSearchPopup() {
    searchPopup.classList.add('search-popup-open');
    document.body.style.overflow = 'hidden';
    
    // Fermer menu si ouvert
    closeMobileMenu();
  }

  // Événements pour le menu hamburger
  menuToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    if (mobileMenu.classList.contains('mobile-menu-open')) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  });

  // Événements pour le bouton de recherche
  searchToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    if (searchPopup.classList.contains('search-popup-open')) {
      closeSearchPopup();
    } else {
      openSearchPopup();
    }
  });

  // Événement pour fermer la recherche
  if (closeSearch) {
    closeSearch.addEventListener('click', function(e) {
      e.stopPropagation();
      closeSearchPopup();
    });
  }

  // Événement pour l'overlay (fermer le menu)
  if (mobileMenuOverlay) {
    mobileMenuOverlay.addEventListener('click', function(e) {
      e.stopPropagation();
      closeMobileMenu();
    });
  }

  // Fermer avec la touche ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeSearchPopup();
      closeMobileMenu();
    }
  });

  // Fermer les menus quand on clique à l'extérieur
  document.addEventListener('click', function(e) {
    const isClickInsideMenu = mobileMenu && mobileMenu.contains(e.target);
    const isClickOnMenuToggle = menuToggle && menuToggle.contains(e.target);
    const isClickInsideSearch = searchPopup && searchPopup.contains(e.target);
    const isClickOnSearchToggle = searchToggle && searchToggle.contains(e.target);
    
    if (!isClickInsideMenu && !isClickOnMenuToggle && mobileMenu && mobileMenu.classList.contains('mobile-menu-open')) {
      closeMobileMenu();
    }
    
    if (!isClickInsideSearch && !isClickOnSearchToggle && searchPopup && searchPopup.classList.contains('search-popup-open')) {
      closeSearchPopup();
    }
  });

  // Améliorations pour le touch sur mobile
  if ('ontouchstart' in window) {
    // Ajouter des classes pour le touch
    document.body.classList.add('touch-device');
    
    // Améliorer les zones de touch
    const touchTargets = document.querySelectorAll('a, button, .touch-target');
    touchTargets.forEach(target => {
      // S'assurer que les éléments touchables ont une taille minimale
      const computedStyle = window.getComputedStyle(target);
      const minHeight = parseInt(computedStyle.minHeight) || 0;
      const minWidth = parseInt(computedStyle.minWidth) || 0;
      
      if (minHeight < 44) {
        target.style.minHeight = '44px';
      }
      
      if (minWidth < 44) {
        target.style.minWidth = '44px';
      }
      
      // Centrer le contenu
      target.style.display = 'flex';
      target.style.alignItems = 'center';
      target.style.justifyContent = 'center';
    });
  }

  // Améliorations pour l'accessibilité
  function setupAccessibility() {
    // Ajouter les attributs ARIA
    if (menuToggle) {
      menuToggle.setAttribute('aria-label', 'Ouvrir le menu de navigation');
      menuToggle.setAttribute('aria-expanded', 'false');
    }
    
    if (searchToggle) {
      searchToggle.setAttribute('aria-label', 'Ouvrir la recherche');
    }
    
    if (mobileMenu) {
      mobileMenu.setAttribute('role', 'dialog');
      mobileMenu.setAttribute('aria-label', 'Menu de navigation');
      mobileMenu.setAttribute('aria-hidden', 'true');
    }
    
    if (searchPopup) {
      searchPopup.setAttribute('role', 'dialog');
      searchPopup.setAttribute('aria-label', 'Recherche');
      searchPopup.setAttribute('aria-hidden', 'true');
    }
    
    // Mettre à jour les attributs ARIA quand les menus s'ouvrent/ferment
    if (menuToggle && mobileMenu) {
      menuToggle.addEventListener('click', function() {
        const isOpen = mobileMenu.classList.contains('mobile-menu-open');
        menuToggle.setAttribute('aria-expanded', isOpen.toString());
        mobileMenu.setAttribute('aria-hidden', (!isOpen).toString());
      });
    }
  }
  
  setupAccessibility();

  // Améliorations pour le chargement rapide
  function optimizeMobileNav() {
    // Précharger les icônes
    const icons = document.querySelectorAll('.bx');
    icons.forEach(icon => {
      const iconName = icon.className.match(/bx-[a-zA-Z0-9-]+/);
      if (iconName) {
        // Précharger l'icône en arrière-plan
        const img = new Image();
        img.src = `https://unpkg.com/boxicons@2.1.4/svg/regular/${iconName[0]}.svg`;
      }
    });
  }
  
  optimizeMobileNav();

  console.log('Navigation mobile initialisée avec succès');
});