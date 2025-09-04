(function(){
  const path = window.DATA_PATH || '';
  const tableEl = document.getElementById('table');
  const q = document.getElementById('q');

  function render(items){
    const rows = items.map(j => `
      <tr>
        <td class="job-details">
          <div class="job-number">#${escapeHtml(j.job_id)}</div>
          <div class="job-title"><strong>${escapeHtml(j.title)}</strong></div>
          <div class="job-org muted">${escapeHtml(j.organization)}</div>
          <div class="job-description">${escapeHtml((j.description || '').substring(0, 150))}${(j.description || '').length > 150 ? '...' : ''}</div>
        </td>
        <td>
          <div class="job-locations">${(j.locations||[]).map(escapeHtml).join('<br/>')}</div>
          <div class="job-date muted">Posted: ${formatDate(j.posted_at)}</div>
        </td>
        <td><a href="${j.url}" target="_blank" rel="noopener" class="apply-btn">Apply</a></td>
      </tr>`).join('');
    tableEl.innerHTML = `
      <table aria-label="Jobs table">
        <thead><tr><th>Job Details</th><th>Location & Date</th><th>Apply</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  }

  function escapeHtml(s){
    return String(s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  }

  function formatDate(dateStr) {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch (e) {
      return dateStr || '';
    }
  }

  function filter(items, term){
    if(!term) return items;
    const t = term.toLowerCase();
    return items.filter(j =>
      (j.title||'').toLowerCase().includes(t) ||
      (j.organization||'').toLowerCase().includes(t) ||
      (j.description||'').toLowerCase().includes(t) ||
      (j.job_id||'').toLowerCase().includes(t) ||
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

