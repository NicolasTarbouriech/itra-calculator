import math
from dataclasses import dataclass

KM_EFFORT_EXPONENT = 1.27
DRIFT_WHEN_UNCHANGED = -0.003
BAND_WHEN_UNCHANGED = 0.012
BAND_WHEN_CHANGED = 0.035
HEAT_SLOWDOWN_PER_DEGREE = 0.0054


@dataclass(frozen=True)
class Edition:
    year: int
    distance_km: float
    elevation_gain_m: float
    reference_time_s: float

    @property
    def km_effort(self) -> float:
        return self.distance_km + self.elevation_gain_m / 100


@dataclass(frozen=True)
class ReferenceForecast:
    expected_s: float
    strict_s: float
    lenient_s: float
    method: str


def forecast_reference(last: Edition, distance_km: float, elevation_gain_m: float) -> ReferenceForecast:
    unchanged = last.distance_km == distance_km and last.elevation_gain_m == elevation_gain_m
    if unchanged:
        expected = last.reference_time_s * (1 + DRIFT_WHEN_UNCHANGED)
        band, method = BAND_WHEN_UNCHANGED, "parcours déclaré identique : T_ref reporté"
    else:
        ratio = (distance_km + elevation_gain_m / 100) / last.km_effort
        expected = last.reference_time_s * ratio ** KM_EFFORT_EXPONENT
        band, method = BAND_WHEN_CHANGED, "parcours modifié : T_ref recalculé, mis à l'échelle du km-effort"
    return ReferenceForecast(expected, expected * (1 - band), expected * (1 + band), method)


def max_time_for_score(reference_time_s: float, target_score: int) -> int:
    return math.floor(1000 * reference_time_s / target_score)


def same_effort_time(time_s: float, hotter_by_degrees: float) -> float:
    return time_s * (1 + HEAT_SLOWDOWN_PER_DEGREE * hotter_by_degrees)


def hms(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds // 3600}h{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def plan(last: Edition, distance_km: float, elevation_gain_m: float, target_score: int) -> str:
    forecast = forecast_reference(last, distance_km, elevation_gain_m)
    safe = max_time_for_score(forecast.strict_s, target_score)
    expected = max_time_for_score(forecast.expected_s, target_score)
    optimistic = max_time_for_score(forecast.lenient_s, target_score)
    return (f"{forecast.method}\n"
            f"T_ref attendu {hms(forecast.expected_s)} (fourchette {hms(forecast.strict_s)} – {hms(forecast.lenient_s)})\n"
            f"Pour {target_score} : viser {hms(safe)} (sûr), {hms(expected)} (central), {hms(optimistic)} (si ITRA est clément)")


if __name__ == "__main__":
    boffi_2025 = Edition(2025, 47.32, 2208, 13309.0)
    print(plan(boffi_2025, 46.56, 1995, 629))
    print("réel 2026 : T_ref 3h27:51, 629 obtenu en 5h30:24")
