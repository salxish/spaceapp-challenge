import csv
from pathlib import Path

METRICS = {
    "slope_degree": {"label": "Slope", "unit": "°", "min": 0, "max": 45},
    "min_temp": {"label": "Min temperature", "unit": "K", "min": 150, "max": 350},
    "rain_mm": {"label": "Rainfall", "unit": "mm", "min": 0, "max": 3000},
    "albedo": {"label": "Albedo", "unit": "", "min": 0, "max": 1},
}

DEFAULT_METRICS = ["slope_degree", "min_temp"]


def _parse_value(raw):
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_earth(path="data/earth_data.csv"):
    rows = _read_csv(path)
    if not rows:
        return {}
    row = rows[0]
    return {
        "site": row.get("site", "").strip(),
        "coords": row.get("coords", "").strip(),
        "slope_degree": _parse_value(row.get("slope_degree")),
        "min_temp": _parse_value(row.get("min_temp")),
        "rain_mm": _parse_value(row.get("rain_mm")),
        "albedo": _parse_value(row.get("albedo")),
    }


def load_mars(path="complete_datasets/mars_data.csv", site="Jezero Crater"):
    rows = _read_csv(path)
    selected = [r for r in rows if str(r.get("site", "")).startswith(site)]
    if not selected:
        return {"site": site, "coords": "", "slope_degree": None, "min_temp": None, "rain_mm": None, "albedo": None}

    def avg(key):
        values = [_parse_value(r.get(key)) for r in selected]
        values = [v for v in values if v is not None]
        if not values:
            return None
        return sum(values) / len(values)

    return {
        "site": site,
        "coords": str(selected[0].get("coords", "")).strip(),
        "slope_degree": avg("slope_degree"),
        "min_temp": avg("min_temp"),
        "rain_mm": avg("rain_mm"),
        "albedo": avg("albedo"),
    }


def metric_similarity(key, earth_val, mars_val):
    if earth_val is None or mars_val is None:
        return None
    spec = METRICS[key]
    span = spec["max"] - spec["min"]
    if span == 0:
        return 1.0 if earth_val == mars_val else 0.0
    
    return max(0.0, 1.0 - abs(earth_val - mars_val) / span)


def score(earth, mars, keys):
    breakdown = []
    missing = []
    similarities = []

    for key in keys:
        spec = METRICS[key]
        earth_val = earth.get(key)
        mars_val = mars.get(key)
        sim = metric_similarity(key, earth_val, mars_val)
        available = sim is not None
        if not available:
            missing.append(spec["label"])
        else:
            similarities.append(sim)
        breakdown.append(
            {
                "key": key,
                "label": spec["label"],
                "unit": spec["unit"],
                "earth": earth_val,
                "mars": mars_val,
                "similarity": sim,
                "available": available,
            }
        )

    overall = None if not similarities else round(100 * sum(similarities) / len(similarities), 1)
    return {"score": overall, "breakdown": breakdown, "missing": missing}
