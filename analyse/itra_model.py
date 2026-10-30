import math
from dataclasses import dataclass
from datetime import date

TIME_WEIGHTS = [(12, 1.000), (18, 0.995), (24, 0.990), (30, 0.985), (36, 0.980)]

EXPERIENCE_WEIGHTS = {
    1: [0.97],
    2: [0.99, 0.98],
    3: [1.00, 0.99, 0.99],
    4: [1.01, 1.00, 1.00, 0.99],
    5: [1.02, 1.01, 1.00, 1.00, 0.99],
}


@dataclass(frozen=True)
class RaceResult:
    race_date: date
    score: float


def race_score(finish_time_s: float, reference_time_s: float) -> int:
    return math.floor(1000 * reference_time_s / finish_time_s)


def km_effort(distance_km: float, elevation_gain_m: float) -> float:
    return distance_km + elevation_gain_m / 100


def months_between(earlier: date, later: date) -> int:
    months = (later.year - earlier.year) * 12 + later.month - earlier.month
    return months - 1 if later.day < earlier.day else months


def time_weight(race_date: date, today: date) -> float:
    age = months_between(race_date, today)
    return next((w for limit, w in TIME_WEIGHTS if age < limit), 0.0)


def performance_index(results: list[RaceResult], today: date) -> float:
    weighted = sorted(
        (r.score * time_weight(r.race_date, today) for r in results if r.score > 0),
        reverse=True,
    )
    weighted = [s for s in weighted if s > 0][:5]
    scenarios = [
        sum(w * s for w, s in zip(EXPERIENCE_WEIGHTS[n], weighted[:n])) / n
        for n in range(1, len(weighted) + 1)
    ]
    return math.floor(max(scenarios, default=0.0))


if __name__ == "__main__":
    today = date(2026, 10, 30)
    neirivue_reference_s = 3288.035
    for finish, published_pi in [("1:12:51", 729), ("1:16:39", 692), ("1:19:42", 666), ("1:24:00", 632)]:
        h, m, s = map(int, finish.split(":"))
        score = race_score(h * 3600 + m * 60 + s, neirivue_reference_s)
        pi = performance_index([RaceResult(date(2026, 6, 21), score)], today)
        print(f"{finish}  score={score:6.1f}  PI model={pi:6.1f}  PI ITRA={published_pi}")
