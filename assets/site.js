'use strict';
(() => {
  const search = document.querySelector('#problem-search');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const rows = [...document.querySelectorAll('[data-problem]')];
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty-search');
  const reset = document.querySelector('#reset-filters');
  let category = 'all';
  function applyFilters() {
    if (!search) return;
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    rows.forEach(row => {
      const match = (category === 'all' || row.dataset.category === category) && row.dataset.search.toLocaleLowerCase().includes(query);
      row.hidden = !match;
      if (match) visible++;
    });
    count.textContent = `${visible} ${visible === 1 ? 'problem' : 'problems'} in view`;
    empty.hidden = visible !== 0;
    reset.hidden = !query && category === 'all';
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
  }
  if (search) {
    search.addEventListener('input', applyFilters);
    buttons.forEach(button => button.addEventListener('click', () => {category = button.dataset.filter; applyFilters();}));
    reset.addEventListener('click', () => {category = 'all'; search.value = ''; applyFilters(); search.focus();});
    applyFilters();
  }
  function fallbackCopy(text) {
    const dialog = document.createElement('dialog');
    dialog.className = 'copy-dialog';
    dialog.setAttribute('aria-label', 'Copy text');
    const heading = document.createElement('h2'); heading.textContent = 'Copy this text';
    const info = document.createElement('p'); info.textContent = 'Select the text below and copy it using your keyboard or device menu.';
    const area = document.createElement('textarea'); area.readOnly = true; area.value = text; area.setAttribute('aria-label','Text to copy');
    const close = document.createElement('button'); close.className = 'button'; close.textContent = 'Done';
    close.addEventListener('click',()=>dialog.close());
    dialog.addEventListener('close',()=>dialog.remove());
    dialog.append(heading,info,area,close); document.body.append(dialog); dialog.showModal(); area.focus(); area.select();
  }
  document.querySelectorAll('[data-copy-target]').forEach(button => {
    button.addEventListener('click', async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;
      const text = target.textContent.trim();
      const status = document.getElementById(button.dataset.statusTarget || 'copy-status');
      try {
        if (!navigator.clipboard) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(text);
        if (status) status.textContent = 'Copied to clipboard.';
      } catch {
        if (status) status.textContent = 'Copy the text in the dialog.';
        fallbackCopy(text);
      }
    });
  });
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click',()=>window.print()));
})();
