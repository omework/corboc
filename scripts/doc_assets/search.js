/* SPDX-License-Identifier: MIT OR Apache-2.0 */
(() => {
  const input = document.getElementById('search');
  const results = document.getElementById('search-results');
  const index = window.CORBO_SEARCH || [];
  let selected = -1;
  let links = [];
  const clear = () => { results.hidden = true; results.replaceChildren(); links = []; selected = -1; };
  function search() {
    const query = input.value.trim().toLowerCase();
    if (!query) { clear(); return; }
    const words = query.split(/\s+/);
    const matches = index.filter(item => {
      const text = `${item.name} ${item.signature} ${item.summary}`.toLowerCase();
      return words.every(word => text.includes(word));
    }).sort((a, b) => {
      const score = item => (item.label.toLowerCase() === query ? 0 : item.label.toLowerCase().startsWith(query) ? 1 : 2) + (item.name.startsWith('implementation::') ? 3 : 0);
      return score(a) - score(b) || a.name.localeCompare(b.name);
    });
    results.hidden = false;
    results.replaceChildren();
    const heading = document.createElement('h2');
    heading.textContent = matches.length ? `${matches.length} results` : 'No matching declarations';
    results.append(heading);
    for (const item of matches.slice(0, 40)) {
      const link = document.createElement('a');
      link.href = item.url;
      const name = document.createElement('strong'); name.textContent = item.name;
      const description = document.createElement('span'); description.textContent = `${item.kind}: ${item.summary}`;
      link.append(name, description); results.append(link);
    }
    if (matches.length > 40) {
      const hint = document.createElement('p'); hint.textContent = 'Showing the first 40. Add a package or method name to narrow your search.'; results.append(hint);
    }
    links = Array.from(results.querySelectorAll('a')); selected = -1;
  }
  input.addEventListener('input', search);
  document.addEventListener('keydown', event => {
    const editing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if ((event.key === '/' && !editing) || ((event.metaKey || event.ctrlKey) && event.key === 'k')) {
      event.preventDefault(); input.focus(); input.select();
    }
    if (event.key === 'Escape') { input.value = ''; clear(); input.blur(); }
    if (document.activeElement === input && links.length && ['ArrowDown', 'ArrowUp', 'Enter'].includes(event.key)) {
      event.preventDefault();
      if (event.key === 'Enter') { (links[Math.max(selected, 0)]).click(); return; }
      selected = (selected + (event.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
      links.forEach((link, i) => link.classList.toggle('selected', i === selected));
      links[selected].scrollIntoView({ block: 'nearest' });
    }
  });
})();
