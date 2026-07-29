const Icons = {
  _svg(inner, size = 20) {
    return `<svg class="icon" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner}</svg>`;
  },

  dashboard(size) {
    return this._svg('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>', size);
  },
  alert(size) {
    return this._svg('<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>', size);
  },
  wallet(size) {
    return this._svg('<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M16 14h.01"/>', size);
  },
  truck(size) {
    return this._svg('<path d="M14 18V6a2 2 0 00-2-2H4a2 2 0 00-2 2v11a1 1 0 001 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 001-1v-3.65a1 1 0 00-.22-.624l-3.48-4.35A1 1 0 0017.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>', size);
  },
  wrench(size) {
    return this._svg('<path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>', size);
  },
  chart(size) {
    return this._svg('<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>', size);
  },
  user(size) {
    return this._svg('<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>', size);
  },
  logout(size) {
    return this._svg('<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>', size);
  },
  check(size) {
    return this._svg('<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>', size);
  },
  checkSimple(size) {
    return this._svg('<polyline points="20 6 9 17 4 12"/>', size);
  },
  clipboard(size) {
    return this._svg('<path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/>', size);
  },
  calendar(size) {
    return this._svg('<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>', size);
  },
  clock(size) {
    return this._svg('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>', size);
  },
  search(size) {
    return this._svg('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>', size);
  },
  phone(size) {
    return this._svg('<path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>', size);
  },
  star(size, filled = false) {
    if (filled) {
      return `<svg class="icon" width="${size || 20}" height="${size || 20}" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
    }
    return this._svg('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>', size);
  },
  arrowLeft(size) {
    return this._svg('<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>', size);
  },
  arrowRight(size) {
    return this._svg('<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>', size);
  },
  x(size) {
    return this._svg('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>', size);
  },
};

function hydrateIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    if (el.querySelector('svg')) return;
    const name = el.dataset.icon;
    if (typeof Icons[name] !== 'function') return;
    const size = el.dataset.size ? Number(el.dataset.size) : 20;
    const filled = el.dataset.filled === 'true';
    el.innerHTML = name === 'star' ? Icons.star(size, filled) : Icons[name](size);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => hydrateIcons());
} else {
  hydrateIcons();
}
