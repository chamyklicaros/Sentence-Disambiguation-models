async function analyze() {
  const sentenceInput = document.getElementById('sentence');
  const model = document.getElementById('model').value;

  if (!sentenceInput.value) {
    alert('Please enter a sentence to analyze.');
    return;
  }

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sentence: sentenceInput.value, model: model })
    });

    const data = await response.json();

    if (!response.ok) {
      alert('Error: ' + (data.detail || 'Unknown error'));
      return;
    }

    // Display results instead of alert
    const resultDiv = document.getElementById('results');
    const countEl = document.getElementById('sentence-count');
    const list = document.getElementById('sentence-list');

    countEl.textContent = `[${data.model}] found ${data.count} sentence(s):`;
    list.innerHTML = '';
    data.result.forEach(s => {
      const li = document.createElement('li');
      li.textContent = s;
      list.appendChild(li);
    });

    resultDiv.style.display = 'block';

  } catch (err) {
    alert('Request failed: ' + err.message);
  }
}

// Moved OUTSIDE analyze() — only needs to be registered once
document.getElementById('sentence').addEventListener('keydown', e => {
  if (e.key === 'Enter') analyze();
});