"""Erreur de prévision du T_ref quand le parcours change, hors Chamonix puis à Chamonix.

Usage : python3 analyse/marge_hors_chamonix.py
Compare l'ancien modèle (T_ref × ratio de km-effort ^ 1,27) au modèle proportionnel (exposant 1)
sur les paires d'éditions consécutives dont le parcours déclaré a changé.
"""
import json
import math
import statistics
from pathlib import Path

DONNEES = Path(__file__).resolve().parent.parent / "donnees"
MARGES = [0.01, 0.02, 0.025, 0.03, 0.033]


def editions_hors_chamonix() -> list[dict]:
    lues = json.loads((DONNEES / "hors_chamonix_2026-10-31.json").read_text(encoding="utf-8"))
    locales = json.loads((DONNEES / "local_summary.json").read_text(encoding="utf-8"))["eds"]
    rows = lues["editions"] + lues["editions_deja_connues"]
    return [dict(label=r[0], year=r[1], dist=r[3], gain=r[4], T=r[9]) for r in rows] + locales


def editions_chamonix() -> list[dict]:
    return json.loads((DONNEES / "utmb_summary.json").read_text(encoding="utf-8"))["eds"]


def paires_modifiees(editions: list[dict]) -> list[tuple[str, int, float, float]]:
    par_course: dict[str, list[dict]] = {}
    for e in editions:
        par_course.setdefault(e["label"], []).append(e)
    km_effort = lambda e: e["dist"] + e["gain"] / 100
    paires = []
    for course, liste in par_course.items():
        liste.sort(key=lambda e: e["year"])
        for avant, apres in zip(liste, liste[1:]):
            if avant["dist"] == apres["dist"] and avant["gain"] == apres["gain"]:
                continue
            paires.append((course, apres["year"], km_effort(apres) / km_effort(avant), apres["T"] / avant["T"]))
    return paires


def bilan(nom: str, paires: list, exposant: float) -> None:
    erreurs = [t / r ** exposant - 1 for _, _, r, t in paires]
    rates = " ; ".join(f"{m * 100:.1f} % → {sum(e < -m for e in erreurs)}" for m in MARGES)
    print(f"{nom}, exposant {exposant} : écart-type {statistics.pstdev(erreurs) * 100:.2f} %, "
          f"médiane {statistics.median(erreurs) * 100:+.2f} %, pire {min(erreurs) * 100:+.2f} %")
    print(f"   ITRA plus sévère que la marge, sur {len(erreurs)} paires : {rates}")


if __name__ == "__main__":
    hors = paires_modifiees(editions_hors_chamonix())
    chamonix = paires_modifiees(editions_chamonix())
    for exposant in (1.27, 1.0):
        bilan("Hors Chamonix", hors, exposant)
    for exposant in (1.27, 1.0):
        bilan("Chamonix", chamonix, exposant)
