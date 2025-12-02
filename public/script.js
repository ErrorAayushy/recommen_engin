// =========================================================
// Correct final JS compatible with your backend + preview
// =========================================================

const API_URL = "http://localhost:5000/api";
let moviesLoaded = false;

// Loading screen
const loadingScreen = document.getElementById("loading-screen");
const loadingText = document.getElementById("loading-text");

// DOM elements
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const genreSelect = document.getElementById("genreSelect");
const regionSelect = document.getElementById("regionSelect");
const languageSelect = document.getElementById("languageSelect");
const recommendBtn = document.getElementById("recommendBtn");
const movieList = document.getElementById("movieList");
const personalList = document.getElementById("personalList");
const resultsTitle = document.getElementById("resultsTitle");
const personalTitle = document.getElementById("personalTitle");

// Dropdown data
const GENRES = [
  "Action","Adventure","Animation","Biography","Comedy","Crime",
  "Documentary","Drama","Family","Fantasy","Film-Noir","History",
  "Horror","Music","Musical","Mystery","Romance","Sci-Fi",
  "Short","Sport","Thriller","War","Western"
];

const REGIONS = {
  "US":"United States","GB":"United Kingdom","FR":"France",
  "DE":"Germany","ES":"Spain","IT":"Italy","JP":"Japan",
  "KR":"South Korea","CN":"China","IN":"India"
};

const LANGS = {
  "en":"English","fr":"French","de":"German","es":"Spanish",
  "it":"Italian","ja":"Japanese","ko":"Korean","zh":"Chinese",
  "hi":"Hindi","pt":"Portuguese"
};

// Populate dropdowns
function populateSelects() {
  GENRES.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g.toLowerCase();
    opt.textContent = g;
    genreSelect.appendChild(opt);
  });

  Object.entries(REGIONS).forEach(([code, name]) => {
    const opt = document.createElement("option");
    opt.value = code.toLowerCase();
    opt.textContent = `${name} (${code})`;
    regionSelect.appendChild(opt);
  });

  Object.entries(LANGS).forEach(([code, name]) => {
    const opt = document.createElement("option");
    opt.value = code.toLowerCase();
    opt.textContent = `${name} (${code})`;
    languageSelect.appendChild(opt);
  });
}

// ---------------------------
// STATUS CHECK
// ---------------------------
async function checkServerStatus() {
  try {
    const res = await fetch(`${API_URL}/status`);
    const data = await res.json();

    if (data.loaded) {
      moviesLoaded = true;
      loadingScreen.style.display = "none";
      fetchPersonalRecommendations();
    } else {
      loadingText.textContent = "Loading movie data…";
      setTimeout(checkServerStatus, 800);
    }
  } catch {
    loadingText.textContent = "Retrying…";
    setTimeout(checkServerStatus, 1000);
  }
}

// ---------------------------
// SEARCH
// ---------------------------
async function fetchSearch(query) {
  if (!moviesLoaded) return alert("Data still loading.");

  movieList.innerHTML = `<p class="status-message">Searching "${query}"...</p>`;
  resultsTitle.textContent = "Results";

  const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
  const data = await res.json();

  displayMovies(movieList, data);
}

// ---------------------------
// FILTERED RECOMMENDATIONS
// ---------------------------
async function fetchFilteredRecommendations() {
  if (!moviesLoaded) return alert("Loading… wait.");

  const params = new URLSearchParams();
  if (genreSelect.value) params.append("genre", genreSelect.value);
  if (regionSelect.value) params.append("region", regionSelect.value);
  if (languageSelect.value) params.append("language", languageSelect.value);

  movieList.innerHTML = "<p>Loading filtered results…</p>";

  const res = await fetch(`${API_URL}/recommend/genre?${params.toString()}`);
  const data = await res.json();

  resultsTitle.textContent = "Filtered Results";
  displayMovies(movieList, data);
}

// ---------------------------
// PERSONAL RECOMMENDATIONS
// ---------------------------
async function fetchPersonalRecommendations() {
  const res = await fetch(`${API_URL}/recommend/personal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      genreHistory: JSON.parse(localStorage.getItem("userGenreHistory") || "[]"),
      regionHistory: JSON.parse(localStorage.getItem("userRegionHistory") || "[]"),
      languageHistory: JSON.parse(localStorage.getItem("userLanguageHistory") || "[]")
    })
  });

  const data = await res.json();
  personalTitle.textContent = "🌟 " + data.title;
  displayMovies(personalList, data.movies);
}

// ---------------------------
// MOVIE CARD RENDER
// ---------------------------
function displayMovies(target, movies) {
  target.innerHTML = "";

  if (!movies || movies.length === 0) {
    target.innerHTML = "<p>No results found.</p>";
    return;
  }

  movies.forEach(m => {
    const card = document.createElement("div");
    card.className = "movie-card";

    card.innerHTML = `
      <h3>${m.title}</h3>
      <p><strong>Year:</strong> ${m.year}</p>
      <p><strong>Genres:</strong> ${m.genres.join(", ")}</p>
      <p><strong>Rating:</strong> ⭐ ${m.rating.toFixed(1)} (${m.numVotes} votes)</p>
    `;

    target.appendChild(card);
  });
}

// ---------------------------
// EVENT LISTENERS
// ---------------------------
searchBtn.onclick = () => fetchSearch(searchInput.value.trim());
recommendBtn.onclick = fetchFilteredRecommendations;

// Start
populateSelects();
checkServerStatus();