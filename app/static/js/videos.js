const YOUTUBE_API_KEY = CONFIG.YOUTUBE_API_KEY;

async function searchChannel(channelId, query) {
  const url = new URL("https://www.googleapis.com/youtube/v3/search");
  url.searchParams.set("part", "snippet");
  url.searchParams.set("type", "video");
  url.searchParams.set("maxResults", "12");
  url.searchParams.set("channelId", channelId);
  url.searchParams.set("q", query);
  url.searchParams.set("key", YOUTUBE_API_KEY);

  const res = await fetch(url);
  if (!res.ok) throw new Error(`YouTube API error: ${res.status} for channel ${channelId}`);
  const data = await res.json();

  return data.items.map((item) => ({
    id: item.id.videoId,
    title: item.snippet.title,
    thumbnail: item.snippet.thumbnails.medium.url,
    channelTitle: item.snippet.channelTitle,
    publishedAt: item.snippet.publishedAt,
  }));
}

async function searchVideos(query) {
  const results = await Promise.all(CHANNELS.map((ch) => searchChannel(ch.id, query)));
  return results
    .flat()
    .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
}

function renderResults(videos) {
  const grid = document.getElementById("results-grid");
  const empty = document.getElementById("empty-state");

  grid.innerHTML = "";

  if (videos.length === 0) {
    empty.classList.remove("hidden");
    return;
  }

  empty.classList.add("hidden");

  for (const video of videos) {
    const card = document.createElement("a");
    card.href = `https://www.youtube.com/watch?v=${video.id}`;
    card.target = "_blank";
    card.rel = "noopener noreferrer";
    card.className =
      "group flex flex-col bg-gray-800 rounded-lg overflow-hidden hover:bg-gray-700 transition-colors";

    card.innerHTML = `
      <div class="relative aspect-video overflow-hidden">
        <img
          src="${video.thumbnail}"
          alt="${escapeHtml(video.title)}"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
        />
      </div>
      <div class="p-3 flex flex-col gap-1">
        <p class="text-white text-sm font-medium leading-snug line-clamp-2">${escapeHtml(video.title)}</p>
        <p class="text-gray-400 text-xs">${escapeHtml(video.channelTitle)}</p>
        <p class="text-gray-500 text-xs">${formatDate(video.publishedAt)}</p>
      </div>
    `;

    grid.appendChild(card);
  }
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

document.getElementById("search-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = document.getElementById("search-input").value.trim();
  if (!query) return;

  const btn = document.getElementById("search-btn");
  btn.disabled = true;
  btn.textContent = "Searching…";

  try {
    const videos = await searchVideos(query);
    renderResults(videos);
  } catch (err) {
    console.error(err);
    document.getElementById("empty-state").textContent =
      "Search failed. Check your API key and try again.";
    document.getElementById("empty-state").classList.remove("hidden");
  }

  btn.disabled = false;
  btn.textContent = "Search";
});
