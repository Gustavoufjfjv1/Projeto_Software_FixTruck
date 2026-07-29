const Masks = {
  onlyDigits(value) {
    return String(value || '').replace(/\D/g, '');
  },

  cnh(value) {
    return this.onlyDigits(value).slice(0, 11);
  },

  telefone(value) {
    const d = this.onlyDigits(value).slice(0, 11);
    if (d.length <= 2) return d.length ? `(${d}` : '';
    if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    if (d.length <= 10) {
      return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    }
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
  },

  placa(value) {
    const v = String(value || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 7);
    // Mercosul: AAA0A00 — exibe com hífen opcional visual AAA-0A00
    if (v.length <= 3) return v;
    return `${v.slice(0, 3)}${v.slice(3)}`;
  },

  bind(input, type) {
    if (!input || typeof this[type] !== 'function') return;
    const apply = () => {
      const start = input.selectionStart;
      const before = input.value;
      input.value = this[type](input.value);
      // mantém cursor no fim em máscaras curtas
      if (document.activeElement === input && before !== input.value) {
        const pos = input.value.length;
        input.setSelectionRange(pos, pos);
      } else if (document.activeElement === input) {
        input.setSelectionRange(start, start);
      }
    };
    input.addEventListener('input', apply);
    input.addEventListener('blur', apply);
    apply();
  },
};
