import json, math, sys, statistics as st
eds = json.load(open(sys.argv[1])); pairs = json.load(open(sys.argv[2]))['pairs']
idx = {(e['label'], e['year']): e for e in eds}
hms = lambda s: f"{int(s//3600)}:{int(s%3600//60):02d}"
for lab in dict.fromkeys(e['label'] for e in eds):
    print(f"-- {lab}")
    for e in sorted([e for e in eds if e['label'] == lab], key=lambda e: e['year']):
        k = e['dist'] + e['gain']/100
        print(f"{e['year']} {e['date']} {e['dist']:6.2f}km +{e['gain']:5.0f} keff={k:6.1f} T={hms(e['T'])} n={e['n']:4} exact={e['matched']}/{e['n']} "
              f"vainqueur={1000*e['T']/e['t_win']:4.0f}pts médiane={e['s_med']} | Tmax={e['tmax']:4.1f} pluie={e['precip']:4.1f}mm veille={e['precip_before']:4.1f} vent={e['wind']:4.1f}")
print("\n== Paires d'éditions (répétants)")
pred = []
for p in pairs:
    a, b = idx[(p['label'], p['y1'])], idx[(p['label'], p['y2'])]
    dk = math.log((b['dist'] + b['gain']/100)/(a['dist'] + a['gain']/100))
    model = 1.27*dk + 0.52*(p['med_log_time_ratio'] - dk)
    pred.append((p['log_T_ratio'], model))
    print(f"{p['label']:20} {p['y1']}→{p['y2']} n={p['n']:3}  temps répétants {100*p['med_log_time_ratio']:+5.1f}%  T ITRA {100*p['log_T_ratio']:+5.1f}%  "
          f"modèle Chamonix {100*model:+5.1f}%  Δscore médian {p['med_score_delta']:+4}  ΔTmax {b['tmax']-a['tmax']:+5.1f}°C  Δkeff {100*dk:+5.1f}%")
if len(pred) > 2:
    print(f"\nerreur du modèle Chamonix sur ces courses : {100*st.pstdev([y-m for y, m in pred]):.1f}% (écart-type), biais {100*st.mean([y-m for y, m in pred]):+.1f}%")
    x = [p['med_log_time_ratio'] for p in pairs]; y = [p['log_T_ratio'] for p in pairs]
    mx, my = st.mean(x), st.mean(y); b = sum((u-mx)*(v-my) for u, v in zip(x, y))/sum((u-mx)**2 for u in x)
    print(f"pente brute T ITRA / temps répétants : {b:.2f} (Chamonix : 0,66) ; r={st.correlation(x, y):.2f}")
