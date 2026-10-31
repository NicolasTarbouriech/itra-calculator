const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

const elements = {};
const fakeElement = id => ({
  id, value: "", textContent: "", innerHTML: "", hidden: false, dataset: {}, className: "", style: {},
  addEventListener() {}, setAttribute() {}, append() {}, querySelectorAll() { return []; }, closest() { return null; }, focus() {},
});
global.document = {
  getElementById: id => (elements[id] ||= fakeElement(id)),
  querySelectorAll: () => [],
  createElement: () => fakeElement("element"),
};
global.location = { hash: "" };

vm.runInThisContext(`${script}
global.page = { els, pe, pf, sc, renderCote, renderProfil, loadRace };
`);

const { els, pe, pf, sc, renderCote, renderProfil, loadRace } = global.page;
const text = html => html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ");

assert.equal(els.tSafe.textContent, "5h12", "Veni Vici 52 km, 600 points : chrono à viser");
assert.match(els.tPace.textContent, /6:00 min\/km/, "Veni Vici 52 km, 600 points : allure");
assert.match(els.tExplain.textContent, /5h20, soit 6:09 min\/km/, "Veni Vici 52 km, 600 points : temps le plus probable et son allure");

els.race.value = "custom";
loadRace("custom");
assert.equal(els.tReliability.textContent, "Faible", "sans résultat de l'an dernier : mode sans historique");
assert.equal(els.tSafe.textContent, "4h19", "42 km +1500, 600 points, estimé à partir du parcours");
els.race.value = "vv52";
loadRace("vv52");

pe.asOf.value = "2026-10-30";
renderCote();
assert.equal(String(pe.now.textContent), "655", "cote générale publiée par ITRA le 30/10/2026");
assert.equal(pe.min.textContent, "645", "score minimum pour faire monter la cote le 07/11/2026");

renderProfil();
assert.equal(pf.headline.textContent, "Plus fort dès que ça grimpe");
assert.match(text(sc.table.innerHTML), /Trail le Graal \(Brocéliande\) Déjà couru : 625 en 2026 .* 643 647 − 7 roulant \+ 3 court/);

console.log("Tous les calculs vérifiés.");
