# Calculateur de cote ITRA

Outil indépendant (sans lien avec ITRA) qui aide un traileur à viser un score de course ITRA :

- **Chrono à viser** : le temps et l'allure à tenir pour atteindre un score donné sur une course, avec un plan de passage par ravitaillement ;
- **Simulateur de cote** : ta cote ITRA actuelle, l'effet de ta prochaine course, le score nécessaire pour une cote visée et les baisses à venir ;
- **Mon profil** : tes forces par terrain et par format, et les courses qui te conviennent.

Version en ligne (privée, même lien) : https://claude.ai/artifact/YMXuMg4Fu7UYLxkBuAM6sR

## Ouvrir la page

`index.html` est autonome : ouvre-le dans un navigateur. Seules les polices viennent de Google Fonts.

## Base de résultats partagés

La page publiée déclare une base partagée (collection `contributions`, un document par coureur, que lui seul peut écrire ; le propriétaire de la page peut modérer). Quand un coureur saisit le temps et le score d'une édition passée d'une course sans historique, il peut les partager : la page en déduit le temps de référence, rejette les valeurs hors de 0,7 à 1,4 fois l'estimation par le parcours et retient, pour chaque course, l'édition la plus récente (médiane si plusieurs coureurs ont partagé la même). Ouverte en local, la page fonctionne sans cette base.

## Mettre à jour le catalogue des courses

La recherche « Cherche ta course » s'appuie sur `catalogue.js`, généré à partir de l'API publique de LiveTrail : les événements à venir (avec leurs points de passage) et ceux de l'année écoulée (avec distance et D+).

```bash
python3 scripts/catalogue_livetrail.py        # 400 jours d'historique par défaut
```

Le D+ retenu est celui qu'annonce LiveTrail en tête de course, en général le chiffre de l'organisateur. ITRA utilise le chiffre déclaré par l'organisateur : en cas d'écart, c'est celui du site de la course qui compte, jamais le cumul GPS de la trace.

## Vérifier les calculs

```bash
node tests/verifier-calculs.js
```

Le script rejoue des cas connus : ta cote ITRA de 655 au 30/10/2026, le chrono de 5h18 pour 600 points sur la Veni Vici 52 km, ton profil et l'estimation de Brocéliande.

## Ce qu'on a établi sur ITRA

Le détail complet de la recherche (méthode, chiffres, cas étudiés, limites) est dans [RECHERCHE.md](RECHERCHE.md).

- **Score de course** = ⌊1000 × T_ref / temps⌋, avec un T_ref par édition, identique pour les hommes et les femmes. Vérifié sur environ 45 000 résultats.
- **Cote** = ⌊meilleur des 5 scénarios de la FAQ ITRA⌋, avec des poids selon l'âge des résultats (en mois pleins) et selon le nombre de courses. Reproduit au point près les 4 cotes publiées de Nicolas.
- **T_ref d'une année sur l'autre** : reporté quand le parcours déclaré est identique (écart médian 0,3 %) ; recalculé quand le parcours change (pente 0,51 par rapport aux conditions réelles). La météo n'est presque jamais compensée.
- **Prévision du T_ref** : reporté si le parcours est inchangé (erreur médiane 0,23 %), proportionnel au km-effort s'il change (écart-type 1,6 % sur 16 paires hors Chamonix). Marge de sécurité de 1 % ou 3 %, tenue environ 9 fois sur 10.
- **Allure par point de passage** : part du temps = (part de « km + D+/55 »)^1,134, ajustée sur 7 456 finishers LiveTrail de la Veni Vici 2025. Erreur moyenne de 1,3 point de %.

## Contenu

| Dossier | Contenu |
|---|---|
| `index.html` | La page (HTML, CSS et JavaScript en un fichier) |
| `catalogue.js` | Catalogue des courses LiveTrail, chargé par la page |
| `scripts/catalogue_livetrail.py` | Génère `catalogue.js` |
| `analyse/itra_model.py` | Réimplémentation du score et de la cote |
| `analyse/itra_target.py` | Prévision du T_ref et du chrono à viser |
| `analyse/analyse_utmb.py` | Analyse UTMB/CCC/OCC/TDS/MCC 2021-2026 : répétants, météo, courbe km-effort |
| `analyse/analyse_courses_locales.py` | Même analyse sur 5 courses locales 2024-2026 |
| `analyse/meteo.py` | Météo des jours de course (archives Open-Meteo) |
| `predictions/` | Prédictions datées avant course, à vérifier après (Mallorca by UTMB 2026) |
| `donnees/` | Résumés par édition (T_ref, parcours, météo), paires de répétants, passages LiveTrail 2025 |

Exemples :

```bash
python3 analyse/analyse_utmb.py donnees/utmb_eds_weather.json donnees/utmb_summary.json
python3 analyse/analyse_courses_locales.py donnees/local_eds_weather.json donnees/local_summary.json
python3 analyse/itra_target.py
```

## Sources des données

- **ITRA** (compte abonné) : temps de référence reconstitués à partir des scores publiés. Le pare-feu d'ITRA bloque les collectes automatiques au-delà de quelques dizaines de pages : ce dossier ne contient aucun script de collecte, et les scores individuels n'ont pas été conservés.
- **LiveTrail** : points et temps de passage de la Veni Vici (API publique du site).
- **Open-Meteo** : météo historique et prévisions.
- **Sites des organisateurs** : distances et D+ officiels.

Le T_ref de chaque course étant tiré de résultats réservés aux abonnés ITRA, vérifie les conditions d'utilisation d'ITRA avant toute diffusion publique.
