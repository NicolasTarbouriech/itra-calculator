# Rétro-ingénierie de la cote ITRA — notes de recherche

Recherche menée le 30 octobre 2026. Ce document rassemble ce qu'ITRA publie, ce que les données ont permis d'établir, les chiffres obtenus et les limites de chaque résultat. Vocabulaire :

- **Score de course** : les points obtenus sur une course (0 à 1000), par exemple 629 à la Boffi Fifty.
- **Cote** : l'indice de performance ITRA, moyenne pondérée des meilleurs scores des 36 derniers mois, par exemple 655.
- **T_ref** : le temps qui vaut 1000 points sur une édition donnée. ITRA ne l'affiche nulle part ; on le reconstitue.
- **Km-effort** : distance + D+/100.
- **Répétants** : coureurs présents sur deux éditions d'une même course. Leur variation de temps mesure la variation réelle de difficulté d'une année sur l'autre.

## 1. Méthode

### Pourquoi une approche « boîte noire »

L'outil REA (github.com/morluto/rea) a analysé les 51 scripts JavaScript d'itra.run, fichiers du site et scripts intégrés aux pages. Aucun calcul de score ne s'y trouve : itra.run est un site ASP.NET rendu côté serveur, et le navigateur ne reçoit que des scores déjà calculés. Le code de calcul reste sur les serveurs d'ITRA et n'est accessible par aucun moyen légitime. Tout ce qui suit vient donc de l'observation des entrées (temps, parcours) et des sorties (scores, cotes).

### Données utilisées

| Source | Contenu | Volume |
|---|---|---|
| ITRA, pages publiques | Cotes des coureurs, temps, parcours | Échantillon pilote de 28 coureurs |
| ITRA, compte abonné | Scores de course de chaque finisher | 32 éditions UTMB/CCC/OCC/TDS/MCC, 14 éditions locales, Veni Vici, Boffi Fifty, Brocéliande : environ 50 000 résultats |
| LiveTrail (API publique du site) | Points et temps de passage de la Veni Vici 2025, parcours 2026 | 7 456 finishers |
| Open-Meteo | Météo historique du jour de course et prévisions | 43 éditions |
| Sites des organisateurs | Distances et D+ officiels | — |

### La contrainte du pare-feu ITRA

ITRA protège son site par un pare-feu AWS. Au-delà de quelques dizaines de pages chargées en peu de temps, il renvoie une page « Human Verification » (code 405). Il s'est déclenché trois fois : après une trentaine de pages scriptées sans navigateur, après environ 65 pages de résultats dans le navigateur, puis après une quarantaine de pages en deux collectes rapprochées. À chaque fois la collecte a été arrêtée, sans tenter de contourner la protection. Les collectes suivantes ont été limitées à quelques dizaines de pages espacées de 5 à 8 secondes.

## 2. Ce qu'ITRA déclare

### Le score de course (FAQ « ITRA Score »)

Deux étapes, d'après ITRA :

1. **Un « record du monde à plat équivalent »** : la distance, le D+ et le D− et les altitudes sont convertis en distance plate équivalente (km-effort). ITRA compare ensuite le temps du coureur au record théorique pour cette distance, établi à partir des records d'athlétisme.
2. **Un coefficient d'ajustement propre à chaque course**, calculé statistiquement : ITRA compare les temps des finishers à leurs performances passées sur des parcours comparables, pour absorber la technicité, le terrain et les conditions du jour.

ITRA affirme que le classement, le nombre d'abandons, la présence d'élites et la notoriété de la course n'influencent pas le score. Pas de score pour une course de moins de 5 km-effort ou de moins de 5 finishers.

### La cote (FAQ « Performance Index »)

1. On garde les scores des 36 derniers mois, sans les abandons.
2. Chaque score est pondéré selon son âge :

| Âge du résultat | Poids |
|---|---|
| 0 à 11 mois | 1,000 |
| 12 à 17 mois | 0,995 |
| 18 à 23 mois | 0,990 |
| 24 à 29 mois | 0,985 |
| 30 à 35 mois | 0,980 |

3. On trie les scores pondérés et on garde les 5 meilleurs.
4. On calcule cinq scénarios, de 1 à 5 courses, chacun avec ses poids « d'expérience » :

| Courses | Poids |
|---|---|
| 1 | 0,97 |
| 2 | 0,99 ; 0,98 |
| 3 | 1,00 ; 0,99 ; 0,99 |
| 4 | 1,01 ; 1,00 ; 1,00 ; 0,99 |
| 5 | 1,02 ; 1,01 ; 1,00 ; 1,00 ; 0,99 |

5. La cote est le meilleur des cinq scénarios.

Catégories de distance ITRA (en km) : 10K de 5 à 15, semi de 15 à 35, marathon de 35 à 45, 50K de 45 à 65, 50M de 65 à 90, 100K de 90 à 130, 100M de 130 à 190, Endurance au-delà de 190. Une course « verticale » doit avoir un rapport montée/descente de 10 pour 1.

## 3. Ce que les données établissent

### 3.1 La formule exacte du score

**score = ⌊1000 × T_ref / temps⌋**, arrondi à l'entier inférieur, avec un seul T_ref par édition, le même pour les hommes et les femmes.

- **Pilote sur données publiques** (Neirivue-Moléson 2026) : pour les 6 coureurs dont c'était la seule course, cote × temps est constant à 0,05 % près, la précision de l'arrondi. Le score est donc exactement inversement proportionnel au temps.
- **Confirmation avec les scores** : sur les 706 finishers de Neirivue 2026, 704 suivent exactement la formule avec T_ref = 3 288,03 s (54 min 48 s). Les 2 autres sont à 0,001 point de la frontière, sans doute des temps enregistrés au dixième de seconde.
- **À grande échelle** : sur les 30 éditions UTMB/CCC/OCC/TDS/MCC 2021-2026, environ 99,8 % des finishers sont reproduits au point près. Les rares écarts, de 0,01 point, s'expliquent de la même façon. Hommes et femmes suivent le même T_ref.
- Le score du vainqueur varie d'une année à l'autre (UTMB : de 924 en 2021 à 993 en 2026). T_ref n'est donc pas calé sur le vainqueur.

Conséquence pratique : **un seul couple (temps, score) d'une édition suffit pour retrouver son T_ref**, à environ 0,1 % près (T_ref est compris entre score × temps / 1000 et (score + 1) × temps / 1000).

### 3.2 La formule exacte de la cote

**cote = ⌊max des 5 scénarios⌋**, l'âge étant compté en **mois pleins** : un résultat de 12 mois et 12 jours pèse 0,995. Une moyenne de scénario est la somme des scores pondérés divisée par le nombre de courses du scénario.

- Avec une seule course, cote = ⌊0,97 × score⌋, vérifié sur les 6 coureurs « mono-course » de Neirivue.
- Les **4 cotes publiées de Nicolas au 30/10/2026** sont reproduites au point près : générale 655, semi 655, marathon 501, 50K 616. Les cotes par catégorie suivent la même formule, avec les mêmes poids d'âge, en ne gardant que les courses de la catégorie.

Détail de la cote générale de 655 :

| Scénario | Calcul | Résultat |
|---|---|---|
| 1 course | 0,97 × 668 | 647,96 |
| **2 courses** | (0,99 × 668 + 0,98 × 663) / 2 | **655,53** |
| 3 courses | (1,00 × 668 + 0,99 × 663 + 0,99 × 648) / 3 | 655,30 |
| 4 courses | … + 0,99 × 629 | 652,10 |
| 5 courses | … + 0,99 × 625 | 649,35 |

Avec peu de courses, les poids d'expérience sont inférieurs à 1 : c'est une pénalité pour manque de résultats. Ajouter des scores nettement inférieurs aux meilleurs fait baisser la moyenne plus que le bonus ne la fait monter.

Pour atteindre 700 de cote à partir de cette situation :

| Stratégie | Score de course nécessaire |
|---|---|
| 1 course | 722 |
| 2 courses | 711 chacune |
| 3 courses | 705 chacune |
| 4 courses | 700 chacune |
| 5 courses | 698 chacune |

### 3.3 Le T_ref selon la distance

Au sein d'un même événement, T_ref suit le km-effort avec un exposant d'environ 1,23 à 1,27 :

- Chamonix (UTMB, CCC, OCC, TDS, MCC, 30 éditions) : ln T_ref = 4,163 + 1,241 × ln(km-effort), corrélation 0,999, écart résiduel 3,4 %.
- Veni Vici 2025 (16, 27, 48 et 82 km) : exposant de 1,23 à 1,25.

C'est la forme attendue d'une courbe de records : l'allure de référence ralentit avec la distance. Le record « équivalent plat » et le coefficient de course ne sont jamais observables séparément, seulement leur produit.

### 3.4 Le T_ref d'une année sur l'autre : pourquoi la cotation d'une même course change

#### Les T_ref reconstitués

Famille UTMB (distance, D+, T_ref) :

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| UTMB | 175,7 km +10 370 · 19:11 | 172,6 +10 180 · 18:53 | 175,8 +10 040 · 18:49 | 175,8 +10 040 · 18:48 | 174 +10 200 · 18:40 | 171 +9 700 · 18:08 |
| CCC | 101 +6 100 · 9:34 | 99,7 +6 030 · 9:21 | 100,1 +6 030 · 9:38 | 100,1 +6 030 · 9:39 | 100,1 +6 030 · 9:36 | 107,2 +6 155 · 9:57 |
| OCC | 55 +3 500 · 4:46 | 56 +3 476 · 4:53 | 56 +3 480 · **4:24** | 55,6 +3 470 · 4:49 | 60,5 +3 280 · 4:46 | 60,5 +3 410 · 4:57 |
| TDS | 145 +9 100 · 16:49 | 149,7 +8 750 · 16:40 | 158,5 +8 900 · 17:20 | 153,5 +9 580 · 17:13 | 153 +9 100 · 16:57 | 154,4 +9 700 · 17:44 |
| MCC | 40 +2 300 · 3:07 | 40,8 +2 440 · 3:21 | 37,7 +2 400 · **2:52** | 38,8 +2 380 · 3:06 | 39,1 +2 380 · 3:07 | 38,6 +2 310 · 3:05 |

Courses locales :

| Course | 2024 | 2025 | 2026 |
|---|---|---|---|
| Trail des Citadelles 40 km (39 km +2 000) | 2:50:47 | 2:50:35 | 2:50:23 |
| Trail des Hospitaliers | 75,6 km +3 220 · 6:05:43 | 75,4 km +3 294 · 6:05:21 | — |
| Hérault Trail (63,7 km +2 720) | 5:29:35 | 5:29:25 | 5:22:06 |
| SkyRace des Matheysins | 25,35 km +1 922 · 2:13:02 | 26,62 km +1 937 · 2:14:07 | 25,35 km +1 922 · 2:11:47 |
| Trail de Guerlédan (66,15 km +2 369) | — | 4:59:12 | 4:55:50 |
| Veni Vici 27 km | 27 km +700 · 1:25:32 | 27 km +710 · 1:25:28 | — |
| Veni Vici 47/48 km | 47 km +1 250 · 2:56:43 | 48 km +1 300 · 2:56:31 | — |
| Veni Vici 82 km | 82 km +2 200 · 5:41:29 | 82 km +2 240 · 5:41:28 | — |
| Boffi Fifty (Templiers) | — | 47,32 km +2 208 · 3:41:49 | 46,56 km +1 995 · 3:27:51 |

Brocéliande (Trail le Graal 2026, 26 km +700, première édition) : 1:19:18. Neirivue-Moléson 2026 : 54:48.

#### Ce que mesurent les répétants

Sur 61 paires d'éditions de la famille UTMB, en comparant la variation de T_ref à la variation de temps des mêmes coureurs :

- log(T₂/T₁) ≈ 0,66 × log(temps₂/temps₁ des répétants), corrélation 0,84, écart résiduel 2,7 %.
- En séparant parcours et conditions : **log(T₂/T₁) ≈ 1,27 × Δlog(km-effort déclaré) + 0,52 × (variation de difficulté non expliquée par le parcours)**, R² = 0,82.

ITRA suit donc **intégralement le parcours déclaré**, mais ne compense qu'**environ la moitié des conditions réelles**. L'autre moitié retombe sur les scores. Le score médian des répétants varie de −50 à +55 points selon la paire d'éditions (médiane +3, écart absolu médian 12).

#### La règle découverte : report ou recalcul selon le parcours déclaré

Sur 72 paires d'éditions (famille UTMB et courses locales) :

| Parcours déclaré | Paires | Variation médiane de T_ref | Pente par rapport aux conditions réelles |
|---|---|---|---|
| **Identique** (même distance, même D+) | 12 | 0,31 % | 0,09 : quasiment aucune compensation |
| **Modifié** | 60 | 1,62 % | 0,51 : la moitié est compensée |

- **Parcours identique** : ITRA reprend le T_ref de l'édition précédente avec une légère dérive à la baisse (0,1 à 0,5 %). Les conditions du jour retombent entièrement sur les scores. Exemple : Citadelles 40 km, 2024 → 2026, répétants 10,6 % plus lents, T_ref −0,2 %, score médian −41.
- **Parcours modifié** : ITRA recalcule. Un changement de 4 m de D+ déclaré suffit (OCC 2022 → 2023 : 3 476 → 3 480 m), et le T_ref a alors baissé de 10,3 %.
- Sur les courses locales, la pente globale est de 0,05 : T_ref y est presque figé (Chamonix : 0,66).

Exceptions : la Veni Vici 47 → 48 km (+50 m de D+) a gardé son T_ref ; l'Hérault Trail 2025 → 2026 a baissé de 2,2 % sans changement déclaré. Le déclencheur exact du recalcul reste inconnu ; il pourrait aussi y avoir une mise à jour progressive.

#### Exemples

| Comparaison | Contexte | Mêmes coureurs | T_ref | Score médian des répétants |
|---|---|---|---|---|
| OCC 2025 → 2026 | 28 °C au lieu de 21 °C | 12 % plus lents | +4 % | −50 |
| UTMB 2025 → 2026 | parcours un peu plus court | 7 % plus rapides | −3 % | +37 |
| MCC 2022 → 2023 | parcours raccourci, 12 °C | 21 % plus rapides | −16 % | +23 |
| OCC 2022 → 2023 | 18 °C au lieu de 25 °C | 9 % plus rapides | −10 % | −6 (bien compensé) |
| Citadelles 2024 → 2026 | parcours identique | 11 % plus lents | −0,2 % | −41 |
| Hospitaliers 2024 → 2025 | 9 °C au lieu de 16 °C | 5,5 % plus rapides | −0,1 % | +34 |
| Guerlédan 2025 → 2026 | 28 °C au lieu de 18 °C | 1,8 % plus lents | −1,1 % | −17 |
| Matheysins 2024 → 2025 | plus frais, déclaré 1,3 km plus long | 4,4 % plus rapides | +0,8 % | +35 |

#### Effet de la météo

ITRA n'utilise aucune donnée météo ; la météo n'agit qu'à travers le recalcul statistique, quand il a lieu. Sur les paires de la famille UTMB :

- chaque degré de température maximale en plus ralentit les répétants d'environ 0,54 % (R² = 0,32) ;
- et leur coûte environ 1,3 point de score (R² = 0,19) ;
- l'effet de la pluie est ambigu : en fin d'été dans les Alpes, la pluie va souvent avec la fraîcheur.

#### Qui le coefficient suit-il ?

La variation de T_ref suit mieux la tête de course que le peloton :

| Répétants | Pente | Corrélation | Écart résiduel |
|---|---|---|---|
| Rapides (score ≥ 650) | 0,73 | 0,91 | 1,9 % |
| Milieu (520 à 650) | 0,57 | 0,83 | 2,9 % |
| Peloton (< 520) | 0,54 | 0,76 | 3,1 % |

Une partie de l'écart vient du bruit plus fort dans le peloton. La variation de T_ref est aussi fortement corrélée au temps du vainqueur (0,83), beaucoup moins au temps médian (0,46). Hypothèse : ITRA s'appuie surtout sur les coureurs dont l'historique est le plus fourni, souvent la tête de course. Les années difficiles pénalisent alors surtout le peloton.

### 3.5 Cas de la Boffi Fifty (Festival des Templiers)

| | 2025 | 2026 |
|---|---|---|
| Parcours déclaré | 47,32 km +2 208 m | 46,56 km +1 995 m |
| Km-effort | 69,4 | 66,5 (−4,2 %) |
| T_ref | 3:41:49 | 3:27:51 (−6,3 %) |
| Temps de Nicolas | 5:53:47 → 626 | 5:30:24 → 629 |

- La baisse de 6,3 % se décompose en environ 5,3 % dus au parcours plus court (1,27 × 4,2 %) et 1 % de recalcul, tout le peloton ayant été plus rapide que ce que le raccourcissement explique (temps médian −7 %). La météo était quasi identique (sec, environ 20 °C).
- Nicolas a gagné 6,6 % en temps, comme le peloton (−7 %, score médian 466 → 470). Son +3 correspond à la progression médiane du peloton.
- La partie technique retirée du parcours explique que le peloton ait été plus rapide que prévu.
- Anecdote : en 2025, 627 était atteint en 5:53:46, une seconde plus vite.

### 3.6 Cas de Brocéliande : course sévère ou profil du coureur ?

Trail le Graal 2026 : Nicolas, 10e en 2:06:42, score 625, alors qu'il score 648 à 668 sur des trails de montagne de km-effort comparable. Les allures de référence diffèrent : 2:24 par km-effort à Brocéliande, 2:33 à la Chaussée des Géants, 2:45 à la Pastourelle, 2:47 au Val d'Aran. À km-effort égal, un parcours roulant a une référence plus rapide.

Le test décisif compare les autres coureurs de tête à leurs propres scores ailleurs :

| Rang | Score Brocéliande | Autres scores récents |
|---|---|---|
| 1 | 694 | aucun (cote 673 = ⌊0,97 × 694⌋) |
| 3 | 676 | 607, 557 |
| 5 | 665 | 624, 624, 662 |
| 7 | 644 | 637, 631, 598, 585 |
| 9 | 631 | 469 (2023) |
| 12 | 623 | aucun |
| 14 | 615 | 606, 591, 590, 576 |
| **Nicolas (10e)** | **625** | **668, 663, 648, 629, 626** |

Pour les autres, Brocéliande est leur meilleur score, souvent de 10 à 40 points au-dessus de leurs autres courses, surtout des trails bretons roulants. La course n'est donc pas sévère : c'est un **effet de profil**. Nicolas est plus fort en montagne que sur le roulant, où les coureurs « route » vont relativement plus vite. L'échantillon est limité à 7 coureurs, le pare-feu ITRA ayant bloqué la suite.

### 3.7 Prévoir le T_ref de la prochaine édition

Modèle :

- **Parcours déclaré identique** : T_ref = T_ref précédent × 0,997.
- **Parcours modifié** : T_ref = T_ref précédent × (km-effort nouveau / ancien)^1,27.
- **Chrono maximum pour un score S** : 1000 × T_ref / S.

Test sur les éditions consécutives connues :

| Cas | Paires | Erreur médiane | Cas où ITRA a été plus sévère que la marge |
|---|---|---|---|
| Parcours identique | 8 | 0,25 % | 1 sur 8 avec une marge de 1 % |
| Parcours modifié | 29 | 1,46 % | 3 sur 29 avec une marge de 3,3 % |

Seule une erreur dans le sens « ITRA plus sévère » compte pour un chrono à viser : la marge de sécurité est donc unilatérale. Les plus grosses erreurs viennent des recalculs forts (OCC 2023 : −10,4 %, MCC 2023 : −8,8 %). Test sur la Boffi Fifty 2026 : prévu 3:30:09, réel 3:27:51.

**Sans historique** (nouvelle course ou course jamais saisie), on estime à partir du seul parcours, ajusté sur les 21 courses connues : **T_ref ≈ 68,05 s × km-effort^1,235**. Chaque événement a été testé sans avoir servi au calage. L'erreur médiane est de 4,4 % ; 80 % des cas sont sous 7,5 % et le pire atteint 9,5 %. Ajouter la pente ou séparer km et D+ n'améliore rien. Les plus gros écarts viennent de la technicité, que le parcours ne capture pas : la référence de la CCC est 7 % plus rapide que prévu, celles de l'Hérault Trail et de Majorque 6 à 7 % plus lentes. Pour Els Tres Mils (Majorque, 56 km), l'estimation sans historique donne 6h36 pour 600 points, contre 7h33 avec l'édition 2025 : 14 % d'écart. La marge de sécurité passe à 7 % (dépassée dans 3 cas sur 21). Le D− n'est pas modélisé : presque toutes les courses connues ont un D+ proche du D−, ce qui empêche de mesurer l'effet d'un parcours descendant.

### 3.8 L'allure par point de passage

Ajusté sur les temps de passage LiveTrail de la Veni Vici 2025 (82, 48, 27 et 16 km ; 7 456 finishers), pour les coureurs de niveau 550 à 650 :

**part du temps écoulé = (part de « km + D+/55 » parcourue)^1,134**

- Erreur moyenne : 1,33 point de pourcentage, soit environ 4 minutes sur 5 heures ; maximum 3,7 points, au premier pointage du 27 km (bouchons de départ avec 2 700 coureurs).
- La règle naïve (part du km-effort, sans fatigue) se trompe en moyenne de 3,8 points.
- Pour ces coureurs, 55 m de D+ « coûtent » 1 km, contre 100 m dans le km-effort ITRA. L'exposant 1,134 traduit la fatigue.
- La répartition du temps varie à peine entre les niveaux 500 et 750 : un même plan sert à tous les objectifs.

### 3.9 Veni Vici 2026 (7 novembre) : chronos à viser

Parcours officiels (site de l'organisateur) : 87 km +2 250, 52 km +1 470, 33 km +715, 18 km +525. Ce sont de vrais changements de parcours par rapport à 2025 (82, 48, 27 et 16 km) : T_ref sera très probablement recalculé.

| Distance | Pour 600 | Pour 700 | Marge incluse (600) |
|---|---|---|---|
| 18 km | 1h26 (4:50/km) | 1h14 (4:09/km) | 3 min |
| 33 km | 2h49 (5:08/km) | 2h25 (4:24/km) | 6 min |
| 52 km | 5h18 (6:08/km) | 4h33 (5:15/km) | 11 min |
| 87 km | 9h44 (6:43/km) | 8h21 (5:46/km) | 20 min |

Plan de passage pour 600 sur le 52 km (départ 8 h) : Lédenon (18,6 km) 1h53 à 9h53, Cabrières (26,3 km) 2h38 à 10h38, Escattes (38,4 km) 3h54 à 11h54, Nîmes (52,5 km) 5h18 à 13h18.

Écarts de données relevés : LiveTrail annonce +420 m pour le 18 km (site officiel : +525), et le cumul GPS de ses points de passage donne +1 273 m pour le 52 km (officiel : +1 470). Le calcul du score utilise les chiffres officiels ; le plan de passage n'utilise que les proportions entre points, insensibles à cet écart.

En 2025, ITRA avait gardé le T_ref d'une année sur l'autre malgré le passage de 47 à 48 km. S'il fait de même en 2026 sur le 87 km, 600 demanderait 9h27.

## 4. Profil coureur

Seuils identiques pour tous les coureurs :

- **Terrain** (m de D+ par km) : montagne à partir de 50, soit une pente moyenne de 5 %, seuil de la course en montagne dans les règles de l'IAAF (2016-2017) ; roulant sous 30, simple convention ; vallonné entre les deux.
- **Format** (km, catégories ITRA) : court sous 35 km (10K, semi), moyen de 35 à 65 km (marathon, 50K), long au-delà.
- **Période** : 12 derniers mois. Sur 24 mois, la progression fausse tout : le niveau de Nicolas tombait à environ 590 et Brocéliande était estimée à 578.
- **Score probable d'une course** = niveau (moyenne 12 mois) + écart terrain + écart format. Un écart mesuré sur n courses compte pour n/(n+2) : un tiers pour une course, la moitié pour deux. Une catégorie jamais courue reprend, réduit, l'écart de la catégorie voisine.

Profil de Nicolas au 30/10/2026 : niveau 647, progression +127 points en un an, régularité ±17 points. Roulant −22 (1 course), vallonné +7 (3), montagne +1 (1) ; court +4 (4), moyen −18 (1). Résumé : « Plus fort dès que ça grimpe, meilleur sur format court ».

## 5. Limites et questions ouvertes

- **Échantillons** : 30 éditions alpines, 14 éditions locales, une poignée de cas individuels. Les conclusions sur les courses locales reposent sur 11 paires, dont certaines n'ont que 11 à 22 répétants.
- **Clémence propre à chaque course** : mesurée seulement à Brocéliande. La mesurer partout demande de comparer les mêmes coureurs sur plusieurs courses, ce que le pare-feu ITRA empêche à grande échelle. Une piste propre : des utilisateurs qui saisissent eux-mêmes leurs résultats.
- **Déclencheur du recalcul** : le parcours déclaré explique la plupart des cas, avec des exceptions (Veni Vici 47 → 48 km, Hérault 2026).
- **Méthode du coefficient** : ITRA dit comparer les finishers à leurs performances passées ; la corrélation avec la tête de course suggère une pondération par l'historique, sans preuve.
- **Cotes par catégorie** : la FAQ annonce une décroissance plus rapide pour les distances courtes, non observée sur les cas vérifiés.
- **Météo** : un seul point de grille par course (vallée pour Chamonix), sans mesure de la boue ni de la neige.
- **Répétants** : ils progressent un peu d'une année sur l'autre (+5 points en médiane), léger biais dans les comparaisons.
- **Données de parcours** : écarts fréquents entre chiffres déclarés, GPS et sites tiers. ITRA utilise les chiffres déclarés.
- **Conditions d'utilisation** : les T_ref proviennent de scores réservés aux abonnés. Vérifier les conditions d'ITRA avant toute diffusion publique de l'outil ou des données.

## 6. Sources

- ITRA, FAQ Performance Index : https://itra.run/FAQ/PerformanceIndex
- ITRA, FAQ Race Score : https://itra.run/FAQ/ItraScore
- ITRA, « All about the ITRA performance index » : https://itra.run/Runners/Performance
- REA, outil de rétro-ingénierie : https://github.com/morluto/rea
- Règles IAAF 2016-2017 de la course en montagne (règles 251 et 252) : https://www.MountainRunning.ru/doc/3996/IAAF%202016-2017%20-%20rules%20251%20252.pdf
- World Athletics, Mountain and Trail Running : https://worldathletics.org/disciplines/mountain-running/mountain-running
- LiveTrail, La Veni Vici : https://lavenivici.v3.livetrail.net/
- La Veni Vici, parcours officiels : https://www.lavenivici.com/parcours/
- Open-Meteo, API d'archives météo : https://open-meteo.com/
