(function(){
  const path = window.DATA_PATH || '';
  const tableEl = document.getElementById('table');
  const q = document.getElementById('q');

  function render(items){
    const rows = items.map((j, index) => {
      const shortDesc = (j.description || '').substring(0, 150);
      const hasMore = (j.description || '').length > 150;
      return `
      <tr class="job-row" data-index="${index}">
        <td class="job-details">
          <div class="job-number">#${escapeHtml(j.job_id)}</div>
          <div class="job-title"><strong>${escapeHtml(j.title)}</strong></div>
          <div class="job-org muted">${escapeHtml(j.organization)}</div>
          <div class="job-description">
            <div class="desc-short">${escapeHtml(shortDesc)}${hasMore ? '...' : ''}</div>
            ${hasMore ? `<div class="desc-full" style="display: none;">${escapeHtml(j.description || '')}</div>` : ''}
            ${hasMore ? '<div class="expand-hint muted">Click to expand description</div>' : ''}
          </div>
        </td>
        <td>
          <div class="job-locations">${(j.locations||[]).map(escapeHtml).join('<br/>')}</div>
          <div class="job-date muted">Posted: ${formatDate(j.posted_at)}</div>
        </td>
        <td><a href="${j.url}" target="_blank" rel="noopener" class="apply-btn">Apply</a></td>
      </tr>`;
    }).join('');
    tableEl.innerHTML = `
      <table aria-label="Jobs table">
        <thead><tr><th>Job Details</th><th>Location & Date</th><th>Apply</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
    
    // Add click handlers for expandable descriptions
    tableEl.querySelectorAll('.job-row').forEach(row => {
      const jobDetails = row.querySelector('.job-details');
      const shortDesc = row.querySelector('.desc-short');
      const fullDesc = row.querySelector('.desc-full');
      const expandHint = row.querySelector('.expand-hint');
      
      if (fullDesc) {
        let isExpanded = false;
        jobDetails.style.cursor = 'pointer';
        
        jobDetails.addEventListener('click', (e) => {
          // Don't expand if clicking on a link
          if (e.target.tagName === 'A') return;
          
          isExpanded = !isExpanded;
          if (isExpanded) {
            shortDesc.style.display = 'none';
            fullDesc.style.display = 'block';
            expandHint.textContent = 'Click to collapse description';
            row.classList.add('expanded');
          } else {
            shortDesc.style.display = 'block';
            fullDesc.style.display = 'none';
            expandHint.textContent = 'Click to expand description';
            row.classList.remove('expanded');
          }
        });
      }
    });
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

