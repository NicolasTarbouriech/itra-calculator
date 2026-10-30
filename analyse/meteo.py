import json
import sys
import time
import urllib.request
from datetime import date, timedelta

LOCATIONS = {
    "UTMB": (45.92, 6.87), "CCC": (45.92, 6.87), "OCC": (45.92, 6.87), "TDS": (45.92, 6.87), "MCC": (45.92, 6.87),
    "MdMB 42": (45.92, 6.87), "Sierre-Zinal": (46.20, 7.60), "Zegama": (42.97, -2.29),
    "Western States": (39.02, -120.82), "SaintéLyon": (45.60, 4.57), "Neirivue": (46.53, 7.06),
    "Templiers": (44.10, 3.08), "Guerlédan": (48.20, -3.00), "Ultra Marin 175": (47.60, -2.80),
    "Ronde des Douaniers": (47.60, -2.80), "Citadelles 70": (42.93, 1.85), "Citadelles 40": (42.93, 1.85),
    "Citadelles 24": (42.93, 1.85), "Hospitaliers": (44.02, 3.30), "Larzac-Dourbie": (44.02, 3.30),
    "Hérault Trail": (43.78, 3.81), "Hortus": (43.78, 3.81), "SkyRace Matheysins": (44.90, 5.79),
    "SkyTour Matheysins": (44.90, 5.79),
}
DAILY = "temperature_2m_max,temperature_2m_min,precipitation_sum,rain_sum,snowfall_sum,wind_speed_10m_max,relative_humidity_2m_mean"


def fetch(lat: float, lon: float, start: date, end: date) -> dict:
    url = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           f"&start_date={start}&end_date={end}&daily={DAILY}&timezone=auto")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.load(response)["daily"]
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2)


def main(summary_path: str, out_path: str) -> None:
    editions = json.load(open(summary_path))
    out = []
    for e in editions:
        if e["label"] not in LOCATIONS or not e.get("date"):
            continue
        y, m, d = map(int, e["date"].split("/"))
        start = date(y, m, d)
        end = start + timedelta(days=1 if e["T"] > 30000 else 0)
        daily = fetch(*LOCATIONS[e["label"]], start - timedelta(days=2), end)
        race_days = slice(2, None)
        out.append({**e,
                    "tmax": max(daily["temperature_2m_max"][race_days]),
                    "tmin": min(daily["temperature_2m_min"][race_days]),
                    "precip": sum(daily["precipitation_sum"][race_days]),
                    "precip_before": sum(daily["precipitation_sum"][:2]),
                    "snow": sum(daily["snowfall_sum"][race_days]),
                    "wind": max(daily["wind_speed_10m_max"][race_days]),
                    "humidity": sum(daily["relative_humidity_2m_mean"][race_days]) / len(daily["relative_humidity_2m_mean"][race_days])})
        time.sleep(0.3)
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
    print(len(out), "editions with weather")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
