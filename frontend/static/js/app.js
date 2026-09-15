let latestResult = null;
const $ = (id) => document.getElementById(id);

function setStatus(text) { $('status-pill').textContent = text; }
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
}
function money(value) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value || 0);
}
function setPipeline(trace = []) {
  const statusByStage = Object.fromEntries(trace.map(x => [x.stage, x.status]));
  const labels = ['requirements', 'spatial_extraction', 'recommendation', 'optimization', 'layout_validation', 'rendering'];
  document.querySelectorAll('#pipeline-list li').forEach((item, i) => {
    item.classList.remove('done', 'failed');
    const status = statusByStage[labels[i]];
    if (status === 'success' || status === 'provided') item.classList.add('done');
    if (status === 'error') item.classList.add('failed');
  });
}
function renderResult(result) {
  latestResult = result;
  setStatus(result.status === 'success' ? 'Design ready' : result.status);
  setPipeline(result.trace || []);

  const products = (result.bundle?.products || []).map(p => `
    <article class="product-card">
      <strong>${escapeHtml(p.name)}</strong>
      <div class="product-meta">${escapeHtml(p.category)} · ${money(p.price)} · ${p.width} × ${p.depth} mm</div>
    </article>`).join('');
  $('products').innerHTML = products || '<p class="muted">No products returned.</p>';
  $('bundle-cost').textContent = result.bundle?.total_cost != null ? money(result.bundle.total_cost) : '';

  $('bundles').innerHTML = (result.alternatives || []).map((b, i) => `
    <article class="bundle-card ${i === 0 ? 'selected' : ''}">
      <strong>Bundle ${String.fromCharCode(65 + i)}</strong>
      <div class="product-meta">${money(b.total_cost)} · ${b.budget_feasible ? 'Budget satisfied' : 'Budget shortfall ' + money(b.budget_shortfall)}</div>
      <div class="product-meta">${(b.products || []).map(p => escapeHtml(p.name)).join(' · ')}</div>
    </article>`).join('');

  $('canvas').innerHTML = result.svg || '<p class="muted">No renderable layout was produced.</p>';
  $('layout-score').textContent = result.layout ? escapeHtml(result.layout.strategy) : '';

  const validation = result.validation || {};
  const violations = validation.violations || [];
  $('validation').innerHTML = validation.valid
    ? '<div class="validation-item ok">✓ All deterministic hard geometry checks passed</div>'
    : `<div class="validation-item bad">✕ ${escapeHtml(validation.error || validation.reason || 'Validation did not pass')}</div>${violations.slice(0, 8).map(v => `<div class="validation-item bad">✕ ${escapeHtml(v.message || v.type)}</div>`).join('')}`;

  const spatial = result.spatial_plan;
  $('spatial-summary').innerHTML = spatial ? `<strong>Spatial input</strong><br>Room: ${spatial.room_width?.value ?? '?'} ${escapeHtml(spatial.room_width?.unit || '')} × ${spatial.room_depth?.value ?? '?'} ${escapeHtml(spatial.room_depth?.unit || '')}<br>Door: ${spatial.door ? 'identified' : 'not identified'}` : '';
  $('explanation').innerHTML = result.explanation ? `<p>${escapeHtml(result.explanation.summary || '')}</p><p><strong>Theme:</strong> ${escapeHtml(result.explanation.theme || '—')}</p><p><strong>Tradeoffs:</strong></p><ul>${(result.explanation.tradeoffs || []).map(x => `<li>${escapeHtml(x)}</li>`).join('')}</ul><details><summary>Trace</summary><pre class="trace">${escapeHtml(JSON.stringify(result.trace || [], null, 2))}</pre></details>` : '<p class="muted">No explanation was returned.</p>';
}

$('design-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  $('error').textContent = '';
  $('generate-btn').disabled = true;
  setStatus('Generating…');
  try {
    const form = new FormData();
    form.append('requirements', $('requirements').value);
    const image = $('image').files[0];
    if (image) form.append('image', image);
    const spatialText = $('spatial-plan').value.trim();
    if (spatialText) {
      let parsed;
      try { parsed = JSON.parse(spatialText); } catch (err) { throw new Error('Structured spatial plan is not valid JSON.'); }
      form.append('payload', JSON.stringify({ requirements: $('requirements').value, spatial_plan: parsed }));
    }
    const response = await fetch('/api/design', { method: 'POST', body: form });
    const result = await response.json();
    if (!response.ok && result.status === 'error') throw new Error(result.error || 'Design generation failed');
    renderResult(result);
  } catch (err) {
    $('error').textContent = err.message || 'Unexpected error';
    setStatus('Error');
  } finally {
    $('generate-btn').disabled = false;
  }
});

$('replace-btn').addEventListener('click', async () => {
  if (!latestResult) { $('error').textContent = 'Generate a design before replacing a product.'; return; }
  const category = $('replace-category').value;
  $('error').textContent = '';
  $('replace-btn').disabled = true;
  setStatus('Replacing…');
  try {
    const response = await fetch('/api/replace', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, requirements: $('requirements').value, result: latestResult })
    });
    const result = await response.json();
    if (!response.ok && result.status === 'error') throw new Error(result.error || 'Replacement failed');
    renderResult(result);
  } catch (err) {
    $('error').textContent = err.message || 'Replacement failed';
    setStatus('Error');
  } finally {
    $('replace-btn').disabled = false;
  }
});
