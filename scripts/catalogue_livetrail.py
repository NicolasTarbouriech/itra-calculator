"""Génère catalogue.js, le catalogue des courses LiveTrail utilisé par index.html.

Usage : python3 scripts/catalogue_livetrail.py [jours_passés]

- Événements à venir : courses, distance, D+ annoncé, départ et points de passage.
- Événements des `jours_passés` derniers jours (400 par défaut) : courses, distance et D+,
  dont la prochaine édition reprend souvent le parcours.
Seules les courses qui peuvent recevoir un score ITRA sont gardées : trail individuel d'au moins
5 km-effort, sans relais, marche, randonnée ni course enfants.
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.v3.livetrail.net/api"
PAUSE_S = 0.4
OUTPUT = Path(__file__).resolve().parent.parent / "catalogue.js"
NOT_SCORED = re.compile(r"relais|relay|\bduo\b|team|[ée]quipe|marche|nordi[cq]|walk|rando|hike|hiking|enfant|kids|famil|poussin|benjamin|minime", re.IGNORECASE)


def get(path: str, tenant: str | None = None):
    headers = {"User-Agent": "itra-calculator/1.0"}
    if tenant:
        headers["X-Tenant"] = tenant
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{API}/{path}", headers=headers), timeout=30) as response:
                return json.load(response)
        except OSError:
            if attempt == 2:
                return None
            time.sleep(2)
        finally:
            time.sleep(PAUSE_S)


def search(states: list[str], order: str) -> list[dict]:
    query = "&".join(f"states={s}" for s in states)
    result = get(f"livetrail/events/search?query=&{query}&limit=1000&order={order}")
    return (result or {}).get("events", [])


def checkpoints(tenant: str, race_id: str) -> list[list]:
    points = get(f"events/points?raceId={race_id}", tenant) or []
    kept = [[p.get("shortName") or p.get("name"), round(p["distance"] / 1000, 2), p.get("elevationGain") or 0]
            for p in points if p.get("distance") is not None]
    kept = [p for i, p in enumerate(kept) if i == 0 or p[2] > 0]
    return [p for i, p in enumerate(kept) if i == 0 or p[1] > kept[i - 1][1]]


def races(event: dict, upcoming: bool) -> list[dict]:
    tenant = f"{event['id']}_{event['year']}"
    summaries = get("events/races/summaries", tenant) or []
    out = []
    for s in summaries:
        km = (s.get("distance") or 0) / 1000
        sport = s.get("sportActivityType")
        name = s.get("fullname") or s.get("shortname") or s["raceId"]
        if km + (s.get("elevationGain") or 0) / 100 < 5 or (sport and sport != "TRAIL_RUNNING") or NOT_SCORED.search(name):
            continue
        race = {
            "id": s["raceId"],
            "name": name,
            "km": round(km, 2),
            "dplus": s.get("elevationGain"),
            "start": s.get("startDate"),
            "place": s.get("startPlace"),
        }
        if upcoming:
            race["checkpoints"] = checkpoints(tenant, s["raceId"])
        out.append(race)
    return out


def main(days_back: int) -> None:
    since = datetime.now(timezone.utc) - timedelta(days=days_back)
    upcoming = search(["ONGOING", "UPCOMING"], "asc")
    past = [e for e in search(["PAST"], "desc") if datetime.fromisoformat(e["startDate"].replace("Z", "+00:00")) >= since]
    catalogue = []
    for event, is_upcoming in [(e, True) for e in upcoming] + [(e, False) for e in past]:
        event_races = races(event, is_upcoming)
        if event_races:
            catalogue.append({
                "id": event["id"], "year": event["year"], "name": event["name"].strip(),
                "country": event.get("countryCode"), "date": event["startDate"][:10],
                "upcoming": is_upcoming, "races": event_races,
            })
        print(f"{'à venir' if is_upcoming else 'passé  '} {event['startDate'][:10]} {event['name'][:50]} : {len(event_races)} course(s)", flush=True)
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "events": catalogue}
    OUTPUT.write_text("window.LIVETRAIL_CATALOGUE = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"{len(catalogue)} événements, {sum(len(e['races']) for e in catalogue)} courses → {OUTPUT}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
