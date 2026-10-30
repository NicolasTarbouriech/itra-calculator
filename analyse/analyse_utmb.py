import json, math, statistics as st, sys
eds = json.load(open(sys.argv[1])); pairs = json.load(open(sys.argv[2]))['pairs']
hms = lambda s: f"{int(s//3600)}:{int(s%3600//60):02d}"
def ols(x, y):
    mx, my = st.mean(x), st.mean(y); sxx = sum((a-mx)**2 for a in x); b = sum((a-mx)*(c-my) for a, c in zip(x, y))/sxx
    a = my - b*mx; r = [c-(a+b*v) for v, c in zip(x, y)]; return a, b, st.pstdev(r), st.correlation(x, y)
for e in eds: e['keff'] = e['dist'] + e['gain']/100; e['pace'] = e['T']/e['keff']
print("== Par course et par année : T_ref, allure de référence, score du vainqueur, météo")
for lab in ['UTMB', 'CCC', 'OCC', 'TDS', 'MCC']:
    print(f"-- {lab}")
    for e in sorted([e for e in eds if e['label'] == lab], key=lambda e: e['year']):
        print(f"{e['year']} {e['dist']:6.1f}km +{e['gain']:5.0f} keff={e['keff']:6.1f} T={hms(e['T'])} ({e['T']:7.0f}s) pace={e['pace']:5.1f}s/kmE "
              f"win={1000*e['T']/e['t_win']:4.0f}pts med={e['s_med']} | Tmax={e['tmax']:4.1f} Tmin={e['tmin']:4.1f} pluie={e['precip']:4.1f}mm (veille {e['precip_before']:4.1f}) vent={e['wind']:4.1f}")
a, b, sd, r = ols([math.log(e['keff']) for e in eds], [math.log(e['T']) for e in eds])
print(f"\n== Courbe commune log T = {a:.3f} + {b:.3f} log keff ; écart-type résiduel {100*sd:.1f}% ; r={r:.3f}")
for e in eds: e['resid'] = math.log(e['T']) - (a + b*math.log(e['keff']))
print("\n== Répétants (mêmes coureurs, deux éditions) : variation de T d'ITRA vs variation de leurs temps")
x = [p['med_log_time_ratio'] for p in pairs]; y = [p['log_T_ratio'] for p in pairs]
a2, b2, sd2, r2 = ols(x, y)
print(f"toutes paires (n={len(pairs)}): log(T2/T1) = {a2:.4f} + {b2:.3f} × log(t2/t1 répétants) ; r={r2:.3f} ; résidu {100*sd2:.1f}%")
cons = [p for p in pairs if p['y2'] - p['y1'] == 1 or (p['y1'], p['y2']) in []]
print("écarts de score médian des répétants (points) :", sorted(p['med_score_delta'] for p in pairs))
print("médiane", st.median(p['med_score_delta'] for p in pairs), "| |écart| médian", st.median(abs(p['med_score_delta']) for p in pairs))
print("\n== La météo explique-t-elle le ralentissement des répétants ? (paires, différences de météo)")
idx = {(e['label'], e['year']): e for e in eds}
rows = []
for p in pairs:
    e1, e2 = idx.get((p['label'], p['y1'])), idx.get((p['label'], p['y2']))
    if not e1 or not e2: continue
    rows.append(dict(p, dtmax=e2['tmax']-e1['tmax'], dprecip=e2['precip']-e1['precip'], dwind=e2['wind']-e1['wind'], dkeff=math.log(e2['keff']/e1['keff'])))
for k in ['dtmax', 'dprecip', 'dwind', 'dkeff']:
    xs = [r[k] for r in rows]
    print(f"{k:8}: corr avec temps répétants {st.correlation(xs, [r['med_log_time_ratio'] for r in rows]):+.2f} | avec T ITRA {st.correlation(xs, [r['log_T_ratio'] for r in rows]):+.2f} | avec Δscore répétants {st.correlation(xs, [r['med_score_delta'] for r in rows]):+.2f}")
print("\n== T suit-il le vainqueur ou le peloton ? corr(log T, ...) à course fixée (écarts à la moyenne de la course)")
def demean(key):
    out = []
    for lab in set(e['label'] for e in eds):
        g = [e for e in eds if e['label'] == lab]; m = st.mean(math.log(e[key]) for e in g)
        out += [(e, math.log(e[key]) - m) for e in g]
    return {(e['label'], e['year']): v for e, v in out}
dT = demean('T'); dK = demean('keff')
for key in ['t_win', 't_p10', 't_med']:
    d = demean(key); ks = list(dT)
    adj = [dT[k] - b*dK[k] for k in ks]; tv = [d[k] - b*dK[k] for k in ks]
    print(f"{key:6}: corr = {st.correlation(adj, tv):+.2f}, pente = {ols(tv, adj)[1]:.2f}")
