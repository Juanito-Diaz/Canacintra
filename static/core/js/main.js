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

  // ── AJAX dashboard navigation ─────────────────────────────
  const sidebar = document.querySelector('.admin-sidebar');
  const cuerpo = document.getElementById('cuerpo');

  if (sidebar && cuerpo) {
    // Intercept clicks on links inside the sidebar
    sidebar.addEventListener('click', function (e) {
      const link = e.target.closest('a[data-ajax-link]');
      if (link) {
        e.preventDefault();
        const url = link.getAttribute('href');
        loadSection(url, true);
      }
    });

    // Intercept click on action buttons inside #cuerpo (like EDITAR, VER, ELIMINAR, etc.)
    cuerpo.addEventListener('click', function (e) {
      const link = e.target.closest('a[data-ajax-action]');
      if (link) {
        e.preventDefault();
        const url = link.getAttribute('href');
        loadSection(url, true);
      }
    });

    // Intercept form submissions inside #cuerpo
    cuerpo.addEventListener('submit', function (e) {
      const form = e.target.closest('form');
      if (form) {
        if (form.getAttribute('data-no-ajax') === 'true') {
          return;
        }
        e.preventDefault();
        submitFormAjax(form);
      }
    });

    // Handle back/forward navigation
    window.addEventListener('popstate', function (e) {
      if (e.state && e.state.url) {
        loadSection(e.state.url, false);
      }
    });

    // Initial state setup
    window.history.replaceState({ url: window.location.pathname }, '', window.location.pathname);
  }

  function loadSection(url, pushState = true) {
    cuerpo.innerHTML = `
      <div class="d-flex justify-content-center align-items-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
      </div>
    `;

    fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => {
      if (!res.ok) throw new Error('Error al cargar la sección');
      return res.text();
    })
    .then(html => {
      cuerpo.innerHTML = html;
      if (pushState) {
        window.history.pushState({ url: url }, '', url);
      }
      updateActiveSidebarLink(url);
    })
    .catch(err => {
      cuerpo.innerHTML = `
        <div class="alert alert-danger" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error al cargar el contenido: ${err.message}
        </div>
      `;
    });
  }

  function submitFormAjax(form) {
    const url = form.getAttribute('action') || window.location.pathname;
    const method = form.getAttribute('method') || 'POST';
    const formData = new FormData(form);

    cuerpo.innerHTML = `
      <div class="d-flex justify-content-center align-items-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Procesando...</span>
        </div>
      </div>
    `;

    fetch(url, {
      method: method,
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => {
      if (res.redirected) {
        loadSection(res.url, true);
        return null;
      }
      return res.text();
    })
    .then(html => {
      if (html) {
        cuerpo.innerHTML = html;
      }
    })
    .catch(err => {
      cuerpo.innerHTML = `
        <div class="alert alert-danger" role="alert">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error al procesar la solicitud: ${err.message}
        </div>
      `;
    });
  }

  function updateActiveSidebarLink(url) {
    if (!sidebar) return;
    const pathname = new URL(url, window.location.origin).pathname;
    sidebar.querySelectorAll('a[data-ajax-link]').forEach(link => {
      const linkPath = new URL(link.getAttribute('href'), window.location.origin).pathname;
      if (pathname.startsWith(linkPath)) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

})();
