const state = {
  data: [],
  authorized: true,
  query: '',
  tag: 'all'
};

const els = {
  searchInput: document.querySelector('#search-input'),
  tagFilter: document.querySelector('#tag-filter'),
  videoGrid: document.querySelector('#video-grid'),
  totalCount: document.querySelector('#total-count'),
  batchOutput: document.querySelector('#batch-output'),
  authStatus: document.querySelector('#auth-status'),
  modeIndicator: document.querySelector('#mode-indicator'),
  loadDefaultBatch: document.querySelector('#load-default-batch'),
  toggleRaw: document.querySelector('#toggle-raw')
};

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${String(secs).padStart(2, '0')}`;
}

function defaultBatch(items) {
  return items.slice(0, 3).map((item) => ({
    id: item.id,
    title: item.title,
    start: formatTime(item.start_sec),
    end: formatTime(item.end_sec)
  }));
}

function renderBatch(items) {
  const batch = defaultBatch(items);
  els.batchOutput.innerHTML = batch.map((item) => `<li>${item.title} · ${item.start}–${item.end}</li>`).join('');
}

function renderCards(items) {
  els.totalCount.textContent = String(items.length);
  if (!items.length) {
    els.videoGrid.innerHTML = '<article class="video-card"><div class="video-body"><h3 class="video-title">没有符合条件的候选</h3></div></article>';
    return;
  }

  els.videoGrid.innerHTML = items.map((item) => `
    <article class="video-card">
      <div class="video-thumb" aria-label="${item.title}"></div>
      <div class="video-body">
        <div class="video-header">
          <h3 class="video-title">${item.title}</h3>
          <span class="score-tag">${item.score}</span>
        </div>
        <div class="video-meta">${item.source_channel} · ${formatTime(item.start_sec)}–${formatTime(item.end_sec)} · ${item.status}</div>
        <p>${item.note}</p>
        <div class="tag-list">
          ${item.tags.map((tag) => `<span class="tag">#${tag}</span>`).join('')}
        </div>
      </div>
    </article>
  `).join('');
}

function filterItems() {
  const items = state.data.filter((item) => {
    const query = state.query.trim().toLowerCase();
    const matchQuery = !query || [item.title, item.source_title, item.source_channel, item.note, ...item.tags].join(' ').toLowerCase().includes(query);
    const matchTag = state.tag === 'all' || item.tags.includes(state.tag);
    return matchQuery && matchTag;
  });

  renderCards(items);
  renderBatch(items);
  els.modeIndicator.textContent = state.authorized ? 'ready' : 'preview';
  els.authStatus.textContent = state.authorized ? '已生成默认批次，可直接提交到 Pages' : '预览模式：仅展示候选，不生成内容';
  document.querySelector('.auth-dot').style.background = state.authorized ? '#34d399' : '#fbbf24';
}

async function loadHighlights() {
  const response = await fetch('./data/generated/default_batch.json');
  const payload = await response.json();
  const data = payload.batch || payload;
  state.data = Array.isArray(data) ? data : [];
  filterItems();
}

els.searchInput.addEventListener('input', (event) => {
  state.query = event.target.value;
  filterItems();
});

els.tagFilter.addEventListener('change', (event) => {
  state.tag = event.target.value;
  filterItems();
});

els.loadDefaultBatch.addEventListener('click', () => {
  state.authorized = true;
  filterItems();
});

els.toggleRaw.addEventListener('click', () => {
  const grid = document.querySelector('#video-grid');
  grid.classList.toggle('hidden');
  els.toggleRaw.textContent = grid.classList.contains('hidden') ? '显示候选列表' : '隐藏候选列表';
});

loadHighlights();
