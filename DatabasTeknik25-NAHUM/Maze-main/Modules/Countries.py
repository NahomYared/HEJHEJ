# Modules/Countries.py
import json, os

def _try_load(path: str):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and all("country" in x and "cities" in x for x in data):
                    return data
    except Exception:
        pass
    return None

# Try a few sensible locations; keep your own JSON where you like
_CANDIDATES = [
    "media/data/countries.json",
    "media/data/50_wellknown_countries_cities.json",
    "data/countries.json",
]

COUNTRIES = None
for p in _CANDIDATES:
    COUNTRIES = _try_load(p)
    if COUNTRIES:
        break

# Safe minimal fallback so the game still runs without an external JSON
if not COUNTRIES:
    COUNTRIES = [
        {"country": "India",      "cities": ["Mumbai", "Delhi", "Bengaluru", "Chennai"]},
        {"country": "Sweden",     "cities": ["Stockholm", "Gothenburg", "Malmö", "Uppsala"]},
        {"country": "USA",        "cities": ["New York", "Los Angeles", "Chicago", "Houston"]},
        {"country": "Japan",      "cities": ["Tokyo", "Osaka", "Yokohama", "Nagoya"]},
        {"country": "Brazil",     "cities": ["São Paulo", "Rio", "Brasília", "Salvador"]},
        {"country": "Australia",  "cities": ["Sydney", "Melbourne", "Brisbane", "Perth"]},
        {"country": "Egypt",      "cities": ["Cairo", "Alexandria", "Giza", "Shubra El Kheima"]},
        {"country": "Germany",    "cities": ["Berlin", "Hamburg", "Munich", "Cologne"]},
        {"country": "UK",         "cities": ["London", "Birmingham", "Manchester", "Leeds"]},
        {"country": "France",     "cities": ["Paris", "Marseille", "Lyon", "Toulouse"]},
    ]
