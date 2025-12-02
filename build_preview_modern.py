# build_preview_modern.py

import gzip
import csv
import json
import os

csv.field_size_limit(10_000_000)

BASE = os.path.dirname(__file__)
IMDB_DIR = os.path.join(BASE, "imdb")

BASICS = os.path.join(IMDB_DIR, "title.basics.tsv.gz")
RATINGS = os.path.join(IMDB_DIR, "title.ratings.tsv.gz")
AKAS = os.path.join(IMDB_DIR, "title.akas.tsv.gz")

OUTPUT = os.path.join(BASE, "movies_preview.json")

movies = {}
print("STEP 1: Reading basics...")

with gzip.open(BASICS, "rt", encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)

    for row in reader:
        if len(row) < 9:
            continue

        tconst, ttype, title, _, _, year, _, _, genres = row[:9]

        if ttype != "movie":
            continue

        if year == "\\N":
            continue

        try:
            year_i = int(year)
        except:
            continue

        if year_i < 1990:   # keep modern movies only
            continue

        g = [] if genres == "\\N" else genres.split(",")

        movies[tconst] = {
            "id": tconst,
            "title": title,
            "year": year_i,
            "genres": g,
            "rating": 0.0,
            "numVotes": 0,
            "regions": set(),
            "languages": set()
        }

print("Basics loaded:", len(movies))


print("STEP 2: Reading ratings...")

with gzip.open(RATINGS, "rt", encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)

    for row in reader:
        if len(row) < 3:
            continue

        tconst, rating, votes = row[:3]

        if tconst in movies:
            try:
                rating_f = float(rating)
                votes_i = int(votes)
            except:
                continue

            if votes_i < 10000:  # keep only popular movies
                del movies[tconst]
                continue

            movies[tconst]["rating"] = rating_f
            movies[tconst]["numVotes"] = votes_i

print("After ratings:", len(movies))


print("STEP 3: Reading AKAs...")

with gzip.open(AKAS, "rt", encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)

    for row in reader:
        if len(row) < 5:
            continue

        tconst = row[0]
        region = row[3]
        lang = row[4]

        if tconst in movies:
            if region not in ("", "\\N"):
                movies[tconst]["regions"].add(region)
            if lang not in ("", "\\N"):
                movies[tconst]["languages"].add(lang)

print("AKAs processed.")


print("FINALIZING...")

final = []
for m in movies.values():
    m["regions"] = list(m["regions"])
    m["languages"] = list(m["languages"])
    final.append(m)

final = sorted(final, key=lambda x: x["numVotes"], reverse=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(final[:5000], f, indent=2)

print("DONE! Output:", OUTPUT)
print("Total movies written:", len(final[:5000]))