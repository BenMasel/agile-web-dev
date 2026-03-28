const MOCK_VIDEOS = [
  {
    id: "dQw4w9WgXcQ",
    title: "Never Gonna Give You Up",
    thumbnail: "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
    channelTitle: "Rick Astley",
    publishedAt: "2009-10-25",
  },
  {
    id: "9bZkp7q19f0",
    title: "PSY - GANGNAM STYLE",
    thumbnail: "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
    channelTitle: "officialpsy",
    publishedAt: "2012-07-15",
  },
  {
    id: "kJQP7kiw5Fk",
    title: "Luis Fonsi - Despacito ft. Daddy Yankee",
    thumbnail: "https://i.ytimg.com/vi/kJQP7kiw5Fk/mqdefault.jpg",
    channelTitle: "Luis Fonsi",
    publishedAt: "2017-01-12",
  },
  {
    id: "JGwWNGJdvx8",
    title: "Ed Sheeran - Shape of You",
    thumbnail: "https://i.ytimg.com/vi/JGwWNGJdvx8/mqdefault.jpg",
    channelTitle: "Ed Sheeran",
    publishedAt: "2017-01-30",
  },
  {
    id: "RgKAFK5djSk",
    title: "Wiz Khalifa - See You Again ft. Charlie Puth",
    thumbnail: "https://i.ytimg.com/vi/RgKAFK5djSk/mqdefault.jpg",
    channelTitle: "Wiz Khalifa",
    publishedAt: "2015-04-06",
  },
  {
    id: "OPf0YbXqDm0",
    title: "Mark Ronson - Uptown Funk ft. Bruno Mars",
    thumbnail: "https://i.ytimg.com/vi/OPf0YbXqDm0/mqdefault.jpg",
    channelTitle: "Mark Ronson",
    publishedAt: "2014-11-19",
  },
];

// Replace this function body with a real YouTube Data API v3 fetch() call later.
// Expected shape: { id, title, thumbnail, channelTitle, publishedAt }
async function searchVideos(query) {
  return MOCK_VIDEOS.filter((v) =>
    v.title.toLowerCase().includes(query.toLowerCase()) ||
    v.channelTitle.toLowerCase().includes(query.toLowerCase())
  );
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

  const videos = await searchVideos(query);
  renderResults(videos);

  btn.disabled = false;
  btn.textContent = "Search";
});
