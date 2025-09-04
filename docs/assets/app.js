(function(){
  const path = window.DATA_PATH || '';
  const tableEl = document.getElementById('table');
  const q = document.getElementById('q');

  function render(items){
    const rows = items.map(j => `
      <tr>
        <td><div><strong>${escapeHtml(j.title)}</strong></div><div class="muted">${escapeHtml(j.organization)}</div></td>
        <td>${(j.locations||[]).map(escapeHtml).join('<br/>')}</td>
        <td><a href="${j.url}" target="_blank" rel="noopener">Apply</a></td>
      </tr>`).join('');
    tableEl.innerHTML = `
      <table aria-label="Jobs table">
        <thead><tr><th>Role</th><th>Location</th><th>Link</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  }

  function escapeHtml(s){
    return String(s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  function filter(items, term){
    if(!term) return items;
    const t = term.toLowerCase();
    return items.filter(j =>
      (j.title||'').toLowerCase().includes(t) ||
      (j.organization||'').toLowerCase().includes(t) ||
      (j.locations||[]).join(' ').toLowerCase().includes(t)
    );
  }

  fetch(path, {cache: 'no-cache'})
    .then(r => r.json())
    .then(data => {
      let items = Array.isArray(data) ? data : (data.jobs || []);
      render(items);
      q && q.addEventListener('input', () => render(filter(items, q.value)));
    })
    .catch(() => {
      tableEl.innerHTML = '<p>Failed to load jobs data.</p>';
    });
})();

