function selectModel(el) {
  document.querySelectorAll('.model-opt').forEach(o => o.classList.remove('active'));
  el.classList.add('active');
}

function getModel() {
  return document.querySelector('.model-opt.active')?.dataset.val || 'sat';
}

function showError(msg) {
  const b = document.getElementById('errorBanner');
  b.textContent = msg;
  b.style.display = 'block';
}

function hideError() {
  document.getElementById('errorBanner').style.display = 'none';
}

async function analyze() {
  const input = document.getElementById('sentence');
  const btn = document.getElementById('analyzeBtn');
  const model = getModel();
  hideError();

  if (!input.value.trim()) {
    showError('Please enter a sentence to analyze.');
    return;
  }

  btn.disabled = true;
  btn.classList.add('loading');
  btn.querySelector('.btn-text').textContent = 'Analyzing…';

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sentence: input.value, model })
    });
    const data = await response.json();

    if (!response.ok) {
      showError(data.detail || 'Unknown error');
      return;
    }

    const results = document.getElementById('results');
    const badge = document.getElementById('badge');
    const list = document.getElementById('sentence-list');

    badge.textContent = `${data.count} sentence${data.count !== 1 ? 's' : ''} · ${data.model}`;
    list.innerHTML = '';
    data.result.forEach((s, i) => {
      const item = document.createElement('div');
      item.className = 'sentence-item';
      item.innerHTML = `<span class="sentence-num">${i + 1}</span><span class="sentence-text">${s}</span>`;
      list.appendChild(item);
    });

    results.style.display = 'block';
  } catch (err) {
    showError('Request failed: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.querySelector('.btn-text').textContent = 'Analyze';
  }
}
Sa

document.getElementById('sentence').addEventListener('keydown', e => {
  if (e.key === 'Enter') analyze();
});