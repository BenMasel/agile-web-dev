// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------
const input       = document.getElementById('search-input');
const clearBtn    = document.getElementById('clear-btn');
const spinner     = document.getElementById('loading-spinner');
const hintState   = document.getElementById('hint-state');
const errorState  = document.getElementById('error-state');
const emptyState  = document.getElementById('empty-state');
const resultsGrid = document.getElementById('results-grid');

// ---------------------------------------------------------------------------
// Channel pills — rendered from CHANNELS constant (data/channels.js)
// ---------------------------------------------------------------------------
const pillsContainer = document.getElementById('channel-pills');

CHANNELS.forEach(ch => {
  const pill = document.createElement('span');
  pill.className = 'text-[11px] px-2 py-[3px] rounded-md bg-rc-fill border border-rc-border text-rc-text-secondary';
  pill.textContent = ch.name;
  pillsContainer.appendChild(pill);
});

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function searchChannel(channelId, query) {
  const url = new URL('/api/youtube/search', window.location.origin);
  url.searchParams.set('channelId', channelId);
  url.searchParams.set('q', query);

  const res = await fetch(url);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `YouTube search error ${res.status}`);
  return data.videos || [];
}

async function searchVideos(query) {
  const results = await Promise.all(CHANNELS.map(ch => searchChannel(ch.id, query)));
  return results
    .flat()
    .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

function renderResults(videos) {
  resultsGrid.innerHTML = '';

  if (videos.length === 0) {
    showState('empty');
    return;
  }

  showState('results');

  for (const video of videos) {
    const card = document.createElement('a');
    card.href   = `https://www.youtube.com/watch?v=${video.id}`;
    card.target = '_blank';
    card.rel    = 'noopener noreferrer';

    // Use inline CSS variables so dynamic classes resolve correctly under
    // the Tailwind browser build (which scans static markup, not JS strings).
    card.style.cssText = `
      display: flex;
      flex-direction: column;
      background: var(--color-rc-surface);
      border: 1px solid var(--color-rc-border);
      border-radius: 10px;
      overflow: hidden;
      transition: border-color 0.15s, background 0.15s;
      text-decoration: none;
      cursor: pointer;
    `;

    card.addEventListener('mouseenter', () => {
      card.style.borderColor = 'rgba(255,255,255,0.12)';
      card.style.background  = 'rgba(255,255,255,0.04)';
    });
    card.addEventListener('mouseleave', () => {
      card.style.borderColor = 'var(--color-rc-border)';
      card.style.background  = 'var(--color-rc-surface)';
    });

    card.innerHTML = `
      <div style="position:relative; aspect-ratio:16/9; overflow:hidden; background:#0d0d0d;">
        <img
          src="${escapeHtml(video.thumbnail)}"
          alt="${escapeHtml(video.title)}"
          style="width:100%; height:100%; object-fit:cover;"
          loading="lazy"
        />
      </div>
      <div style="padding: 10px 12px 12px; display:flex; flex-direction:column; gap:4px; flex:1;">
        <p style="font-size:12px; font-weight:500; color:rgba(255,255,255,0.85); line-height:1.4;
                  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
          ${escapeHtml(video.title)}
        </p>
        <p style="font-size:11px; color:rgba(255,255,255,0.4); margin-top:auto; padding-top:4px;">
          ${escapeHtml(video.channelTitle)}
        </p>
        <p style="font-size:10px; color:rgba(255,255,255,0.25);">
          ${formatDate(video.publishedAt)}
        </p>
      </div>
    `;

    resultsGrid.appendChild(card);
  }
}

// ---------------------------------------------------------------------------
// State management — only one panel visible at a time
// ---------------------------------------------------------------------------

function showState(state) {
  hintState.classList.add('hidden');
  errorState.classList.add('hidden');
  emptyState.classList.add('hidden');
  resultsGrid.classList.add('hidden');
  spinner.classList.add('hidden');

  if (state === 'hint')    hintState.classList.remove('hidden');
  if (state === 'error')   errorState.classList.remove('hidden');
  if (state === 'empty')   emptyState.classList.remove('hidden');
  if (state === 'loading') spinner.classList.remove('hidden');
  if (state === 'results') resultsGrid.classList.remove('hidden');
}

// ---------------------------------------------------------------------------
// Search trigger — Enter key only (no submit button)
// ---------------------------------------------------------------------------

async function runSearch() {
  const query = input.value.trim();
  if (!query) return;

  showState('loading');

  try {
    const videos = await searchVideos(query);
    renderResults(videos);
  } catch (err) {
    console.error(err);
    document.getElementById('error-title').textContent   = 'Search failed';
    document.getElementById('error-message').textContent = err.message || 'Check your API key and try again.';
    showState('error');
  }
}

input.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    e.preventDefault();
    runSearch();
  }
  if (e.key === 'Escape') {
    clearSearch();
  }
});

// ---------------------------------------------------------------------------
// Clear
// ---------------------------------------------------------------------------

clearBtn.addEventListener('click', clearSearch);

function clearSearch() {
  input.value = '';
  clearBtn.classList.add('hidden');
  showState('hint');
  input.focus();
}

input.addEventListener('input', () => {
  clearBtn.classList.toggle('hidden', input.value.length === 0);
});

// ---------------------------------------------------------------------------
// Auto-focus
// ---------------------------------------------------------------------------
input.focus();
