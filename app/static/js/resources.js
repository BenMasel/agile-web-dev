// resources.js — drives the /resources page
// Reads the current semester's units from the planner state in localStorage
// and aggregates channels, platforms, and textbooks across those units.
// Falls back to all units if the planner has no current-semester units.

// ---------------------------------------------------------------------------
// Current semester units from planner state
// ---------------------------------------------------------------------------

function getCurrentSemKey() {
  const now = new Date();
  const sem = now.getMonth() < 6 ? 1 : 2;
  return `${now.getFullYear()}-${sem}`;
}

// Returns the unit codes the user has in their planner for the current semester.
// Empty array means no planner data — callers should fall back to "all".
function getCurrentSemCodes() {
  try {
    const state = JSON.parse(localStorage.getItem('stUwa_planner_v3') || '{}');
    const key   = getCurrentSemKey();
    return (state.plan && state.plan[key] || []).filter(c => c);
  } catch {}
  return [];
}

// ---------------------------------------------------------------------------
// Active resource helpers
// ---------------------------------------------------------------------------

// Returns entries from UNIT_RESOURCES that match the user's current units.
// Falls back to all UNIT_RESOURCES if the planner has no current-semester data.
function getActiveUnits() {
  const codes = getCurrentSemCodes();
  if (codes.length === 0) return UNIT_RESOURCES;
  return UNIT_RESOURCES.filter(u => codes.includes(u.code));
}

function getActiveChannels() {
  const seen = new Set();
  const channels = [];
  for (const u of getActiveUnits()) {
    for (const ch of (u.resources.youtube_channels || [])) {
      if (!seen.has(ch.id)) {
        seen.add(ch.id);
        channels.push(ch);
      }
    }
  }
  return channels;
}

function getActivePlatforms() {
  const seen = new Set();
  const platforms = [];
  for (const u of getActiveUnits()) {
    for (const p of (u.resources.platforms || [])) {
      const key = p.url || p.name;
      if (!seen.has(key)) {
        seen.add(key);
        platforms.push({ ...p, unitCode: u.code });
      }
    }
  }
  return platforms;
}

function getActiveTextbooks() {
  const seen = new Set();
  const books = [];
  for (const u of getActiveUnits()) {
    for (const t of (u.resources.textbooks || [])) {
      const key = t.isbn || t.title;
      if (!seen.has(key)) {
        seen.add(key);
        books.push({ ...t, unitCode: u.code });
      }
    }
  }
  return books;
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

function escapeHtml(str) {
  return String(str ?? '')
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

// ---------------------------------------------------------------------------
// Current units bar
// ---------------------------------------------------------------------------

const currentBar = document.getElementById('current-units-bar');

function renderCurrentBar() {
  currentBar.innerHTML = '';

  const codes = getCurrentSemCodes();

  const label = document.createElement('span');
  label.className = 'text-[11px] text-rc-text-tertiary shrink-0';
  currentBar.appendChild(label);

  if (codes.length === 0) {
    label.textContent = 'Showing all resources —';
    const hint = document.createElement('span');
    hint.className = 'text-[11px] text-rc-text-faint';
    hint.textContent = 'set up your planner to filter by semester';
    currentBar.appendChild(hint);
    return;
  }

  label.textContent = 'Your units this semester:';
  for (const code of codes) {
    const chip = document.createElement('span');
    chip.className = 'text-[11px] px-2 py-[3px] rounded-md bg-rc-blue-muted border border-rc-blue/20 text-rc-blue';
    chip.textContent = code;
    currentBar.appendChild(chip);
  }
}

// ---------------------------------------------------------------------------
// Channel pills (Videos tab)
// ---------------------------------------------------------------------------

const pillsContainer = document.getElementById('channel-pills');

function renderChannelPills() {
  // Keep the label node; remove old pills
  Array.from(pillsContainer.children).forEach(el => {
    if (!el.classList.contains('shrink-0')) el.remove();
  });

  const channels = getActiveChannels();
  if (channels.length === 0) {
    const msg = document.createElement('span');
    msg.className = 'text-[11px] text-rc-text-faint';
    msg.textContent = 'no channels available for your current units';
    pillsContainer.appendChild(msg);
    return;
  }

  for (const ch of channels) {
    const pill = document.createElement('span');
    pill.className = 'text-[11px] px-2 py-[3px] rounded-md bg-rc-fill border border-rc-border text-rc-text-secondary';
    pill.textContent = ch.name;
    pillsContainer.appendChild(pill);
  }
}

// ---------------------------------------------------------------------------
// Tab management
// ---------------------------------------------------------------------------

let currentTab = 'videos';

function switchTab(tab) {
  currentTab = tab;

  document.querySelectorAll('.tab-btn').forEach(btn => {
    const active = btn.id === `tab-${tab}`;
    btn.style.color         = active ? 'rgba(255,255,255,0.85)' : 'rgba(255,255,255,0.3)';
    btn.style.borderBottom  = active ? '2px solid #FF6363'      : '2px solid transparent';
  });

  ['videos', 'platforms', 'textbooks'].forEach(t => {
    document.getElementById(`tab-content-${t}`).classList.toggle('hidden', t !== tab);
  });

  if (tab === 'platforms')  renderPlatforms();
  if (tab === 'textbooks')  renderTextbooks();
  if (tab === 'videos')     input.focus();
}

// ---------------------------------------------------------------------------
// Platform cards
// ---------------------------------------------------------------------------

const platformsGrid  = document.getElementById('platforms-grid');
const platformsEmpty = document.getElementById('platforms-empty');

function renderPlatforms() {
  platformsGrid.innerHTML = '';
  const platforms = getActivePlatforms();

  if (platforms.length === 0) {
    platformsGrid.classList.add('hidden');
    platformsEmpty.classList.remove('hidden');
    return;
  }

  platformsGrid.classList.remove('hidden');
  platformsEmpty.classList.add('hidden');

  for (const p of platforms) {
    const card = document.createElement('a');
    card.href   = p.url;
    card.target = '_blank';
    card.rel    = 'noopener noreferrer';
    card.style.cssText = `
      display: flex; flex-direction: column; gap: 8px;
      background: var(--color-rc-surface);
      border: 1px solid var(--color-rc-border);
      border-radius: 10px; padding: 14px 16px;
      text-decoration: none;
      transition: border-color 0.15s, background 0.15s;
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
      <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:8px;">
        <p style="font-size:13px; font-weight:500; color:rgba(255,255,255,0.85);">${escapeHtml(p.name)}</p>
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none" style="flex-shrink:0; opacity:0.25; margin-top:2px;">
          <path d="M1.5 9.5L9.5 1.5M9.5 1.5H4.5M9.5 1.5V6.5" stroke="white" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      ${p.description
        ? `<p style="font-size:11px; color:rgba(255,255,255,0.4); line-height:1.5;">${escapeHtml(p.description)}</p>`
        : ''}
      <span style="font-size:10px; color:rgba(255,255,255,0.22); margin-top:auto;">${escapeHtml(p.unitCode)}</span>
    `;
    platformsGrid.appendChild(card);
  }
}

// ---------------------------------------------------------------------------
// Textbook cards
// ---------------------------------------------------------------------------

const textbooksList  = document.getElementById('textbooks-list');
const textbooksEmpty = document.getElementById('textbooks-empty');

function renderTextbooks() {
  textbooksList.innerHTML = '';
  const books = getActiveTextbooks();

  if (books.length === 0) {
    textbooksList.classList.add('hidden');
    textbooksEmpty.classList.remove('hidden');
    return;
  }

  textbooksList.classList.remove('hidden');
  textbooksEmpty.classList.add('hidden');

  for (const t of books) {
    const card = document.createElement('div');
    card.style.cssText = `
      display: flex; align-items: center; gap: 14px;
      background: var(--color-rc-surface);
      border: 1px solid var(--color-rc-border);
      border-radius: 10px; padding: 12px 16px;
    `;
    card.innerHTML = `
      <div style="width:34px; height:42px; flex-shrink:0; border-radius:3px;
                  background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.07);
                  display:flex; align-items:center; justify-content:center;">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M2.5 2.5h9M2.5 5.5h9M2.5 8.5h6" stroke="rgba(255,255,255,0.2)" stroke-width="1.1" stroke-linecap="round"/>
        </svg>
      </div>
      <div style="flex:1; min-width:0;">
        <p style="font-size:13px; font-weight:500; color:rgba(255,255,255,0.85);
                  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHtml(t.title)}</p>
        <p style="font-size:11px; color:rgba(255,255,255,0.4); margin-top:3px;">${escapeHtml(t.author)}</p>
        ${t.isbn
          ? `<p style="font-size:10px; color:rgba(255,255,255,0.2); margin-top:2px; font-family:monospace, monospace;">ISBN ${escapeHtml(t.isbn)}</p>`
          : ''}
      </div>
      <span style="font-size:10px; color:rgba(255,255,255,0.22); flex-shrink:0;">${escapeHtml(t.unitCode)}</span>
    `;
    textbooksList.appendChild(card);
  }
}

// ---------------------------------------------------------------------------
// YouTube search
// ---------------------------------------------------------------------------

const input       = document.getElementById('search-input');
const clearBtn    = document.getElementById('clear-btn');
const spinner     = document.getElementById('loading-spinner');
const hintState   = document.getElementById('hint-state');
const errorState  = document.getElementById('error-state');
const emptyState  = document.getElementById('empty-state');
const resultsGrid = document.getElementById('results-grid');

function showVideoState(state) {
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

async function searchChannel(channelId, query) {
  const url = new URL('/api/youtube/search', window.location.origin);
  url.searchParams.set('channelId',  channelId);
  url.searchParams.set('q',          query);

  const res = await fetch(url);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `YouTube search error ${res.status}`);
  return data.videos || [];
}

async function searchVideos(query) {
  const channels = getActiveChannels();
  if (channels.length === 0) return [];
  const batches = await Promise.all(channels.map(ch => searchChannel(ch.id, query)));
  return batches.flat().sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
}

function renderVideoResults(videos) {
  resultsGrid.innerHTML = '';

  if (videos.length === 0) {
    showVideoState('empty');
    return;
  }

  showVideoState('results');

  for (const video of videos) {
    const card = document.createElement('a');
    card.href   = `https://www.youtube.com/watch?v=${video.id}`;
    card.target = '_blank';
    card.rel    = 'noopener noreferrer';
    card.style.cssText = `
      display: flex; flex-direction: column;
      background: var(--color-rc-surface);
      border: 1px solid var(--color-rc-border);
      border-radius: 10px; overflow: hidden;
      transition: border-color 0.15s, background 0.15s;
      text-decoration: none; cursor: pointer;
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
        <img src="${escapeHtml(video.thumbnail)}" alt="${escapeHtml(video.title)}"
             style="width:100%; height:100%; object-fit:cover;" loading="lazy"/>
      </div>
      <div style="padding:10px 12px 12px; display:flex; flex-direction:column; gap:4px; flex:1;">
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

async function runSearch() {
  const query = input.value.trim();
  if (!query) return;

  const channels = getActiveChannels();
  if (channels.length === 0) {
    document.getElementById('error-title').textContent   = 'No YouTube channels available';
    document.getElementById('error-message').textContent = 'None of your current units have YouTube resources configured.';
    showVideoState('error');
    return;
  }

  showVideoState('loading');

  try {
    const videos = await searchVideos(query);
    renderVideoResults(videos);
  } catch (err) {
    console.error(err);
    document.getElementById('error-title').textContent   = 'Search failed';
    document.getElementById('error-message').textContent = err.message || 'Check your API key and try again.';
    showVideoState('error');
  }
}

input.addEventListener('keydown', e => {
  if (e.key === 'Enter')  { e.preventDefault(); runSearch(); }
  if (e.key === 'Escape') { clearSearch(); }
});

clearBtn.addEventListener('click', clearSearch);

function clearSearch() {
  input.value = '';
  clearBtn.classList.add('hidden');
  showVideoState('hint');
  input.focus();
}

input.addEventListener('input', () => {
  clearBtn.classList.toggle('hidden', input.value.length === 0);
});

// ---------------------------------------------------------------------------
// Global refresh
// ---------------------------------------------------------------------------

function refresh() {
  renderCurrentBar();
  renderChannelPills();
  if (currentTab === 'platforms') renderPlatforms();
  if (currentTab === 'textbooks') renderTextbooks();
  if (input.value.trim() && currentTab === 'videos') runSearch();
}

// ---------------------------------------------------------------------------
// Initialise tab button styles
// ---------------------------------------------------------------------------

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.style.cssText = `
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.3);
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    background: none;
    border-top: none;
    border-left: none;
    border-right: none;
    cursor: pointer;
    transition: color 0.15s;
  `;
});

switchTab('videos');
renderCurrentBar();
renderChannelPills();
input.focus();
