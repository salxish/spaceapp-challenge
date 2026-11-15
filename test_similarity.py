from similarity import load_earth, load_mars, metric_similarity, score


def approx(a, b, eps=1e-9):
    return abs(a - b) < eps


def main():
    sim = metric_similarity("slope_degree", 0.5, 2.9)
    assert sim is not None and approx(sim, 1 - 2.4 / 45)

    assert metric_similarity("slope_degree", 10, 10) == 1.0
    assert metric_similarity("slope_degree", 0, 45) == 0.0
    assert metric_similarity("slope_degree", None, 1) is None

    earth = load_earth()
    mars = load_mars()
    result = score(earth, mars, ["slope_degree", "min_temp", "rain_mm", "albedo"])
    assert result["score"] is not None
    assert 0 <= result["score"] <= 100

    print("ok")


if __name__ == "__main__":
    main()
