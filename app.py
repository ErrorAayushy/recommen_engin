import os
import json
import time
import gzip
import csv
import threading
import webbrowser
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Allow long CSV rows (needed for AKAs file)
csv.field_size_limit(10_000_000)

# Paths
BASE_DIR = os.path.dirname(__file__)
IMDB_DIR = os.path.join(BASE_DIR, "imdb")
BASICS_FILE = os.path.join(IMDB_DIR, "title.basics.tsv.gz")
RATINGS_FILE = os.path.join(IMDB_DIR, "title.ratings.tsv.gz")
AKAS_FILE = os.path.join(IMDB_DIR, "title.akas.tsv.gz")
PREVIEW_FILE = os.path.join(BASE_DIR, "movies_preview.json")

# Flask app
app = Flask(__name__, static_folder="public", static_url_path="/")
CORS(app)

# Global movie data
movies = []
movies_map = {}
movies_loaded = False
lock = threading.Lock()

# Progress info for frontend
progress = {
    "stage": "Starting",
    "percent": 0,
    "processed": 0,
    "total": 1,
    "eta": "Calculating..."
}

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def update_progress(stage, processed, total, start_time):
    progress["stage"] = stage
    progress["processed"] = processed
    progress["total"] = total
    progress["percent"] = round((processed / total) * 100, 2)

    elapsed = time.time() - start_time
    if processed > 0:
        remaining = (elapsed / processed) * (total - processed)
        progress["eta"] = f"{int(remaining // 60)}m {int(remaining % 60)}s"
    else:
        progress["eta"] = "Calculating..."


def count_lines_gz(path):
    """Count total lines inside a gzipped TSV file."""
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f) - 1


def stream_gz_tsv(path):
    """Yield rows from gzipped TSV safely."""
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)  # skip header
        for i, row in enumerate(reader, start=1):
            try:
                yield row
            except csv.Error:
                if i % 10000 == 0:
                    app.logger.warning(f"Skipping bad row {i} in {path}")
                continue


# --------------------------------------------------
# IMDb Loading Logic (Preview + Full Mode)
# --------------------------------------------------
def load_imdb_data():
    print("THREAD STARTED")

    try:
        global movies, movies_map, movies_loaded

        with lock:
            movies = []
            movies_map = {}
            movies_loaded = False

        # PREVIEW
        print("CHECKING PREVIEW:", PREVIEW_FILE)
        if os.path.exists(PREVIEW_FILE):
            print("PREVIEW FOUND")
            with open(PREVIEW_FILE, "r", encoding="utf-8") as f:
                preview = json.load(f)

            with lock:
                movies = preview
                movies_loaded = True

            print("PREVIEW LOADED SUCCESS")
            return

        print("NO PREVIEW → FULL LOAD STARTS (SHOULD NOT HAPPEN)")
    
    except Exception as e:
        print("THREAD CRASHED:", e)

    # ------------------------------------------
    # FULL MODE → extremely slow (not recommended)
    # ------------------------------------------
    app.logger.info("Preview not found — loading full IMDb dataset.")

    # STEP 1 — BASICS
    total_basics = count_lines_gz(BASICS_FILE)
    processed = 0
    start = time.time()

    progress["stage"] = "Loading basics"
    progress["total"] = total_basics

    for row in stream_gz_tsv(BASICS_FILE):
        processed += 1
        update_progress("Loading basics", processed, total_basics, start)

        if len(row) < 9:
            continue

        tconst, type_, title, _, _, year, _, _, genres = row[:9]

        if type_ != "movie":
            continue
        if title == "" or year == "\\N":
            continue

        movies_map[tconst] = {
            "id": tconst,
            "title": title,
            "year": year,
            "genres": [] if genres == "\\N" else genres.split(","),
            "rating": 0.0,
            "numVotes": 0,
            "regions": set(),
            "languages": set()
        }
    # STEP 2 — RATINGS
    total_ratings = count_lines_gz(RATINGS_FILE)
    processed = 0
    start = time.time()

    progress["stage"] = "Merging ratings"
    progress["total"] = total_ratings

    for row in stream_gz_tsv(RATINGS_FILE):
        processed += 1
        update_progress("Merging ratings", processed, total_ratings, start)

        if len(row) < 3:
            continue

        tconst, avg, votes = row[:3]

        if tconst in movies_map:
            try:
                movies_map[tconst]["rating"] = float(avg)
                movies_map[tconst]["numVotes"] = int(votes)
            except:
                pass

    # STEP 3 — AKAS
    total_akas = count_lines_gz(AKAS_FILE)
    processed = 0
    start = time.time()

    progress["stage"] = "Processing AKAs"
    progress["total"] = total_akas

    for row in stream_gz_tsv(AKAS_FILE):
        processed += 1
        update_progress("Processing AKAs", processed, total_akas, start)

        if len(row) < 5:
            continue

        tconst, _, _, region, language = row[:5]

        if tconst in movies_map:
            if region not in ("", "\\N"):
                movies_map[tconst]["regions"].add(region)
            if language not in ("", "\\N"):
                movies_map[tconst]["languages"].add(language)

    # FINALIZE
    final_movies = []
    for m in movies_map.values():
        m["regions"] = list(m["regions"])
        m["languages"] = list(m["languages"])
        final_movies.append(m)

    with lock:
        movies = final_movies
        movies_loaded = True

    progress["stage"] = "Completed"
    progress["percent"] = 100
    progress["eta"] = "0s"

    app.logger.info(f"Full IMDb load complete: {len(movies)} movies")


# --------------------------------------------------
# Start background loader thread
# --------------------------------------------------
threading.Thread(target=load_imdb_data, daemon=True).start()


# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/status")
def api_status():
    with lock:
        return jsonify({"loaded": movies_loaded, "count": len(movies)})


@app.route("/api/progress")
def api_progress():
    return jsonify(progress)


@app.route("/api/search")
def api_search():
    with lock:
        if not movies_loaded:
            return jsonify({"error": "Movies loading"}), 503

        query = (request.args.get("q") or "").lower()
        if not query:
            return jsonify([])

        results = []
        for m in movies:
            if query in m["title"].lower():
                results.append(m)
                continue

            if any(query in g.lower() for g in m["genres"]):
                results.append(m)
                continue

        results = sorted(results, key=lambda x: x["numVotes"], reverse=True)
        return jsonify(results[:20])


@app.route("/api/recommend/genre")
def api_recommend_genre():
    with lock:
        if not movies_loaded:
            return jsonify({"error": "Movies loading"}), 503

        genre = (request.args.get("genre") or "").lower()

        filtered = [
            m for m in movies
            if genre in [g.lower() for g in m["genres"]]
            and m["numVotes"] > 1000
        ]

        filtered = sorted(filtered, key=lambda x: x["rating"], reverse=True)
        return jsonify(filtered[:20])


@app.route("/api/recommend/personal", methods=["POST"])
def api_recommend_personal():
    with lock:
        if not movies_loaded:
            return jsonify({"error": "Movies loading"}), 503

        data = request.get_json() or {}
        genre_history = data.get("genreHistory", [])

        if not genre_history:
            popular = [m for m in movies if m["numVotes"] > 10000]
            popular = sorted(popular, key=lambda x: x["rating"], reverse=True)
            return jsonify({
                "title": "Popular Movies",
                "movies": popular[:20]
            })

        favorite = max(set(genre_history), key=genre_history.count)

        rec = [
            m for m in movies
            if favorite in [g.lower() for g in m["genres"]]
            and m["numVotes"] > 1000
        ]

        rec = sorted(rec, key=lambda x: x["rating"], reverse=True)
        return jsonify({
            "title": f"Top {favorite.title()} Movies",
            "movies": rec[:20]
        })


# --------------------------------------------------
# Start server and auto-open browser
# --------------------------------------------------
if __name__ == "__main__":
    def open_browser():
        time.sleep(1)
        webbrowser.open("http://localhost:5000")

    threading.Thread(target=open_browser).start()

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)