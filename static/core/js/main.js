/**
 * main.js — CANACINTRA Portal de Noticias
 * Autocompletado AJAX del buscador + mejoras UX.
 */

(function () {
  'use strict';

  // ── Buscador con autocompletado AJAX ──────────────────────
  const inputBusqueda = document.getElementById('input-busqueda');
  const dropdown      = document.getElementById('sugerencias-busqueda');
  const AJAX_URL      = '/api/buscar/';

  let debounceTimer = null;

  if (inputBusqueda && dropdown) {
    inputBusqueda.addEventListener('input', function () {
      const query = this.value.trim();
      clearTimeout(debounceTimer);

      if (query.length < 2) {
        dropdown.classList.add('d-none');
        dropdown.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`${AJAX_URL}?q=${encodeURIComponent(query)}`)
          .then(res => res.json())
          .then(data => {
            renderSugerencias(data.resultados, query);
          })
          .catch(() => {
            dropdown.classList.add('d-none');
          });
      }, 280);
    });

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function (e) {
      if (!inputBusqueda.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('d-none');
      }
    });

    // Navegar con teclado
    inputBusqueda.addEventListener('keydown', function (e) {
      const items = dropdown.querySelectorAll('.suggestion-item');
      const active = dropdown.querySelector('.suggestion-item.focused');
      if (!items.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (!active) {
          items[0].classList.add('focused');
        } else {
          active.classList.remove('focused');
          const next = active.nextElementSibling;
          if (next) next.classList.add('focused');
        }
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (active) {
          active.classList.remove('focused');
          const prev = active.previousElementSibling;
          if (prev) prev.classList.add('focused');
        }
      } else if (e.key === 'Enter') {
        if (active) {
          e.preventDefault();
          window.location.href = active.dataset.url;
        }
      } else if (e.key === 'Escape') {
        dropdown.classList.add('d-none');
      }
    });
  }

  function renderSugerencias(resultados, query) {
    if (!resultados.length) {
      dropdown.classList.add('d-none');
      dropdown.innerHTML = '';
      return;
    }

    const fragment = document.createDocumentFragment();
    resultados.forEach(item => {
      const el = document.createElement('a');
      el.href = item.url;
      el.classList.add('suggestion-item');
      el.dataset.url = item.url;

      // Resaltar la query dentro del título
      const tituloResaltado = item.titulo.replace(
        new RegExp(`(${escapeRegex(query)})`, 'gi'),
        '<strong>$1</strong>'
      );

      el.innerHTML = `
        <span>${tituloResaltado}</span>
        <span class="d-flex gap-2 mt-1">
          <span class="sug-cat">${item.categoria}</span>
          <span class="text-muted" style="font-size:.7rem;">${item.fecha}</span>
        </span>
      `;
      fragment.appendChild(el);
    });

    dropdown.innerHTML = '';
    dropdown.appendChild(fragment);
    dropdown.classList.remove('d-none');
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // ── Resaltar nav link activo ──────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // ── Smooth reveal on scroll (Intersection Observer) ──────
  const animatedItems = document.querySelectorAll('.news-card, .resultado-card, .card-hero');
  if ('IntersectionObserver' in window && animatedItems.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    animatedItems.forEach(item => {
      item.style.opacity = '0';
      item.style.transform = 'translateY(20px)';
      item.style.transition = 'opacity .45s ease, transform .45s ease';
      observer.observe(item);
    });
  }

  // ── Navbar: sombra al hacer scroll ────────────────────────
  const navbar = document.getElementById('navbar-principal');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 30) {
        navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,.25)';
      } else {
        navbar.style.boxShadow = '0 2px 12px rgba(0,0,0,.2)';
      }
    }, { passive: true });
  }

})();
