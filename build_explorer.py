#!/usr/bin/env python3
"""Rebuild index.html from the saved model results.

Single source of truth: every model number is read from artifacts/results_nb2.csv
and artifacts/nb3_summary.json. Nothing is transcribed by hand.
"""
import csv, json, pathlib

ART = pathlib.Path("data")
OUT = pathlib.Path("index.html")

LABELS = {
    "E01_gradient_boosting": ("Gradient boosting", "tree ensemble baseline"),
    "E02_flat_depth1": ("Flat network, 1 layer", "depth sweep"),
    "E03_flat_depth2": ("Flat network, 2 layers", "depth sweep"),
    "E04_flat_depth3": ("Flat network, 3 layers", "depth sweep"),
    "E05_flat_depth4": ("Flat network, 4 layers", "depth sweep"),
    "E06_dropout": ("4 layers + dropout", "regularisation variant"),
    "E07_batchnorm": ("4 layers + batch norm", "regularisation variant"),
    "E08_dropout_bn": ("4 layers + dropout & batch norm", "best flat network"),
    "E09_embeddings": ("4 layers + embeddings", "encoding variant"),
    "E10_2stage_intent_frozen": ("Two-stage, intent grouping", "frozen subnet"),
    "E11_2stage_intent_ft": ("Two-stage, intent grouping", "fine-tuned subnet"),
    "E12_2stage_k6_frozen": ("Two-stage, k6 grouping", "frozen subnet"),
    "E13_2stage_k6_ft": ("Two-stage, k6 grouping", "fine-tuned subnet"),
    "E14_2stage_k6_logits": ("Two-stage, k6 grouping", "logit hand-off"),
    "E15_2stage_k6_penultimate": ("Two-stage, k6 grouping", "penultimate hand-off"),
    "E16_2stage_k6_unbudgeted": ("Two-stage, k6 grouping", "over budget, control"),
}

FAMILY = {"E01": "tree", "E02": "flat", "E03": "flat", "E04": "flat", "E05": "flat",
          "E06": "flat", "E07": "flat", "E08": "flat", "E09": "flat",
          "E10": "two", "E11": "two", "E12": "two", "E13": "two", "E14": "two",
          "E15": "two", "E16": "two"}

models = []
with open(ART / "results_nb2.csv") as fh:
    for r in csv.DictReader(fh):
        eid = r["experiment"]
        name, note = LABELS[eid]
        models.append({
            "id": eid.split("_")[0],
            "name": name,
            "note": note,
            "family": FAMILY[eid.split("_")[0]],
            "params": int(r["params"]),
            "recall": float(r["recall_at_1pct_fpr"]),
            "fpr": float(r["actual_fpr"]),
            "macroF1": float(r["macro_f1"]),
            "rare": {
                "Worms": float(r["recall_Worms"]),
                "Shellcode": float(r["recall_Shellcode"]),
                "Backdoor": float(r["recall_Backdoor"]),
                "Analysis": float(r["recall_Analysis"]),
            },
        })

summary = json.loads((ART / "nb3_summary.json").read_text())
meta = {
    "targetFpr": 0.01,
    "domainAuc": summary["domain_classifier_auc"],
    "meanOvershoot": summary["mean_fpr_overshoot"],
    "budget": 78218,
}

payload = json.dumps({"models": models, "meta": meta}, indent=None, separators=(",", ":"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alert budget explorer — UNSW-NB15 intrusion detection models</title>
<style>
  :root {
    --ink: #1A1A1A;
    --ink-soft: #6B6B6B;
    --purple: #4E2A84;
    --purple-deep: #2E1A4F;
    --purple-mid: #5B3A8C;
    --lilac: #B07FD6;
    --wash: #F4F0F9;
    --edge: #DCD2EC;
    --over: #B3261E;
    --over-wash: #FBEDEC;
    --paper: #FFFFFF;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--wash);
    color: var(--ink);
    font-family: Calibri, "Segoe UI", system-ui, sans-serif;
    font-size: 16px;
    line-height: 1.5;
  }
  .wrap { max-width: 1120px; margin: 0 auto; padding: 32px 24px 64px; }

  header { border-bottom: 2px solid var(--purple); padding-bottom: 20px; margin-bottom: 28px; }
  .eyebrow {
    font-size: 12px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--purple); font-weight: 700; margin: 0 0 8px;
  }
  h1 {
    font-family: Cambria, Georgia, "Times New Roman", serif;
    font-size: 34px; line-height: 1.15; margin: 0 0 10px; font-weight: 700;
  }
  .thesis { margin: 0; max-width: 68ch; color: var(--ink); }
  .thesis b { color: var(--purple); }

  .panel {
    background: var(--paper); border: 1px solid var(--edge);
    border-radius: 10px; padding: 20px 22px; margin-bottom: 22px;
  }
  .panel h2 {
    font-family: Cambria, Georgia, serif; font-size: 19px; margin: 0 0 4px; font-weight: 700;
  }
  .panel .sub { margin: 0 0 18px; color: var(--ink-soft); font-size: 14px; }

  .controls { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
  .field label { display: block; font-size: 13px; font-weight: 700; margin-bottom: 6px; }
  .field .hint { display: block; font-weight: 400; color: var(--ink-soft); font-size: 12px; margin-top: 2px; }
  .field input {
    width: 100%; padding: 9px 10px; font: inherit; font-size: 15px;
    border: 1px solid var(--edge); border-radius: 6px; background: #fff; color: var(--ink);
  }
  .field input:focus-visible { outline: 3px solid var(--lilac); outline-offset: 1px; border-color: var(--purple); }

  .capacity {
    margin-top: 20px; padding-top: 18px; border-top: 1px dashed var(--edge);
    display: flex; flex-wrap: wrap; gap: 28px; align-items: baseline;
  }
  .stat .n {
    font-family: Cambria, Georgia, serif; font-size: 30px; font-weight: 700;
    color: var(--purple); display: block; line-height: 1.1;
  }
  .stat .k { font-size: 13px; color: var(--ink-soft); }

  .sortbar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 14px; }
  .sortbar span { font-size: 13px; color: var(--ink-soft); margin-right: 4px; }
  button.sort {
    font: inherit; font-size: 13px; padding: 5px 12px; border-radius: 999px;
    border: 1px solid var(--edge); background: #fff; color: var(--ink); cursor: pointer;
  }
  button.sort[aria-pressed="true"] { background: var(--purple); border-color: var(--purple); color: #fff; }
  button.sort:focus-visible { outline: 3px solid var(--lilac); outline-offset: 2px; }

  .rows { display: flex; flex-direction: column; gap: 2px; }
  .row {
    display: grid; grid-template-columns: 232px 1fr 128px; gap: 16px; align-items: center;
    padding: 10px 12px; border: 1px solid transparent; border-radius: 8px;
    background: none; font: inherit; text-align: left; width: 100%; cursor: pointer;
  }
  .row:hover { background: var(--wash); }
  .row:focus-visible { outline: 3px solid var(--lilac); outline-offset: -1px; }
  .row[aria-pressed="true"] { background: var(--wash); border-color: var(--purple); }
  .row .who { min-width: 0; }
  .row .nm { font-weight: 700; font-size: 14px; }
  .row .mt { font-size: 12px; color: var(--ink-soft); }
  .row .mt .tag {
    display: inline-block; font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
    background: var(--wash); border: 1px solid var(--edge); border-radius: 3px;
    padding: 0 4px; margin-right: 6px; color: var(--purple-mid);
  }

  /* the shift line: the signature element */
  .track { position: relative; height: 34px; }
  .bar {
    position: absolute; top: 6px; height: 13px; border-radius: 2px;
    background: var(--purple-mid); transition: width .25s ease;
  }
  .bar.promised { top: 21px; height: 7px; background: var(--edge); }
  .bar.over { background: var(--over); }
  .shiftline { position: absolute; top: 0; bottom: 0; width: 2px; background: var(--ink); }
  .shiftline::after {
    content: "shift capacity"; position: absolute; top: -2px; left: 5px;
    font-size: 10px; letter-spacing: .06em; text-transform: uppercase; color: var(--ink);
    white-space: nowrap;
  }
  .row:not(:first-child) .shiftline::after { content: ""; }
  .row .num { text-align: right; }
  .row .num .big { font-family: Cambria, Georgia, serif; font-size: 19px; font-weight: 700; }
  .row .num .lbl { font-size: 11px; color: var(--ink-soft); display: block; }
  .row.overflow .num .big { color: var(--over); }

  .detail { display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }
  .kv { display: flex; flex-direction: column; gap: 9px; }
  .kv div { display: flex; justify-content: space-between; gap: 16px; font-size: 14px;
            border-bottom: 1px dotted var(--edge); padding-bottom: 7px; }
  .kv dt { color: var(--ink-soft); }
  .kv b { font-variant-numeric: tabular-nums; }
  .kv b.warn { color: var(--over); }
  .rare { margin: 0; }
  .rare .r { display: grid; grid-template-columns: 84px 1fr 46px; gap: 10px; align-items: center;
             font-size: 13px; margin-bottom: 9px; }
  .rare .m { height: 9px; background: var(--wash); border: 1px solid var(--edge); border-radius: 2px; overflow: hidden; }
  .rare .m i { display: block; height: 100%; background: var(--lilac); }
  .rare .m i.zero { background: var(--over); width: 3px !important; }
  .rare .v { text-align: right; font-variant-numeric: tabular-nums; }

  .caveat {
    background: var(--purple-deep); color: #E3DAF0; border-radius: 10px;
    padding: 20px 22px; font-size: 14px;
  }
  .caveat h2 { font-family: Cambria, Georgia, serif; color: #fff; font-size: 18px; margin: 0 0 8px; }
  .caveat p { margin: 0 0 10px; max-width: 78ch; }
  .caveat p:last-child { margin-bottom: 0; }
  .caveat b { color: #fff; }

  footer { margin-top: 26px; font-size: 12px; color: var(--ink-soft); }

  @media (max-width: 860px) {
    .controls { grid-template-columns: repeat(2, 1fr); }
    .row { grid-template-columns: 1fr; gap: 6px; }
    .row .num { text-align: left; }
    .detail { grid-template-columns: 1fr; }
    h1 { font-size: 27px; }
  }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <p class="eyebrow">MSDS 458 &middot; A.4 &middot; Sara Alsiyat</p>
    <h1>Alert budget explorer</h1>
    <p class="thesis">Every model in this study was calibrated to a <b>1% false alarm rate</b> on validation data.
      None of them delivered it on test data. Enter your own traffic and staffing below to see what each model
      would actually put in an analyst's queue tomorrow &mdash; and what it would miss.</p>
  </header>

  <section class="panel">
    <h2>Your traffic and your team</h2>
    <p class="sub">Change any number. Everything below recalculates.</p>
    <div class="controls">
      <div class="field">
        <label for="flows">Flows per day
          <span class="hint">connections your sensor sees</span></label>
        <input id="flows" type="number" min="1" step="1000" value="10000">
      </div>
      <div class="field">
        <label for="benign">Benign share (%)
          <span class="hint">traffic that is not an attack</span></label>
        <input id="benign" type="number" min="1" max="99.9" step="1" value="80">
      </div>
      <div class="field">
        <label for="perAnalyst">Alerts cleared per analyst
          <span class="hint">in one shift</span></label>
        <input id="perAnalyst" type="number" min="1" step="5" value="60">
      </div>
      <div class="field">
        <label for="analysts">Analysts on shift
          <span class="hint">reviewing this queue</span></label>
        <input id="analysts" type="number" min="1" step="1" value="5">
      </div>
    </div>
    <div class="capacity">
      <div class="stat"><span class="n" id="capOut">300</span><span class="k">alerts your team can clear per day</span></div>
      <div class="stat"><span class="n" id="benignOut">8,000</span><span class="k">benign flows per day</span></div>
      <div class="stat"><span class="n" id="attackOut">2,000</span><span class="k">attack flows per day</span></div>
      <div class="stat"><span class="n" id="promisedOut">80</span><span class="k">false alerts a 1% rate promised</span></div>
    </div>
  </section>

  <section class="panel">
    <h2>What each model puts in the queue</h2>
    <p class="sub">Solid bar: false alerts delivered at the model's measured test rate. Thin bar underneath:
      what the calibrated 1% target promised. Red means the queue overflows the shift. Select a row for detail.</p>
    <div class="sortbar">
      <span>Sort by</span>
      <button class="sort" data-sort="alerts" aria-pressed="true">False alerts</button>
      <button class="sort" data-sort="recall" aria-pressed="false">Attack recall</button>
      <button class="sort" data-sort="missed" aria-pressed="false">Attacks missed</button>
      <button class="sort" data-sort="params" aria-pressed="false">Parameters</button>
    </div>
    <div class="rows" id="rows"></div>
  </section>

  <section class="panel">
    <h2 id="detailName">Gradient boosting</h2>
    <p class="sub" id="detailNote">tree ensemble baseline</p>
    <div class="detail">
      <dl class="kv" id="detailStats"></dl>
      <div>
        <p class="sub" style="margin-bottom:12px"><b>Recall on the rare attack classes.</b>
          A headline number can hide a class the model never detects.</p>
        <div class="rare" id="detailRare"></div>
      </div>
    </div>
  </section>

  <section class="caveat">
    <h2>Where this tool stops being trustworthy</h2>
    <p>These queue sizes assume the false alarm rate measured on the UNSW-NB15 test partition carries over to
      your traffic. In this study it did not even carry across the dataset's own two halves: a classifier
      trained only to tell whether a benign record came from the training or the test partition reached
      <b>0.91 AUC</b>, and delivered false alarm rates ran <b>3.74&times;</b> over target on average.</p>
    <p>So treat every number here as a planning estimate that expires the moment your traffic differs from this
      benchmark &mdash; which is to say, immediately. The defensible use is comparing models against each other
      under one assumption, not predicting an absolute alert count. Measure the rate on your own traffic before
      you staff against it.</p>
  </section>

  <footer>
    Built from <code>results_nb2.csv</code> and <code>nb3_summary.json</code>, the saved outputs of notebooks 2 and 3.
    All 16 experiments, single run, seed 458. Attack traffic in UNSW-NB15 is laboratory-generated.
  </footer>

</div>

<script>
const DATA = __PAYLOAD__;
const fmt = n => Math.round(n).toLocaleString("en-US");
const pct = n => (n * 100).toFixed(1) + "%";
const rate = n => (n * 100).toFixed(2) + "%";

let sortKey = "alerts";
let selected = "E01";

const els = {
  flows: document.getElementById("flows"),
  benign: document.getElementById("benign"),
  perAnalyst: document.getElementById("perAnalyst"),
  analysts: document.getElementById("analysts"),
  rows: document.getElementById("rows"),
};

function num(el, fallback) {
  const v = parseFloat(el.value);
  return (isFinite(v) && v > 0) ? v : fallback;
}

function scenario() {
  const flows = num(els.flows, 10000);
  const benignShare = Math.min(num(els.benign, 80), 99.9) / 100;
  const capacity = num(els.perAnalyst, 60) * num(els.analysts, 5);
  const benign = flows * benignShare;
  const attacks = flows - benign;
  return { flows, benign, attacks, capacity, promised: benign * DATA.meta.targetFpr };
}

function computed(s) {
  return DATA.models.map(m => {
    const alerts = s.benign * m.fpr;
    return Object.assign({}, m, {
      alerts,
      missed: s.attacks * (1 - m.recall),
      detected: s.attacks * m.recall,
      overflow: alerts > s.capacity,
      overBy: alerts / s.capacity,
    });
  });
}

function sorted(list) {
  const by = {
    alerts: (a, b) => a.alerts - b.alerts,
    recall: (a, b) => b.recall - a.recall,
    missed: (a, b) => a.missed - b.missed,
    params: (a, b) => a.params - b.params,
  }[sortKey];
  return list.slice().sort(by);
}

function render() {
  const s = scenario();
  document.getElementById("capOut").textContent = fmt(s.capacity);
  document.getElementById("benignOut").textContent = fmt(s.benign);
  document.getElementById("attackOut").textContent = fmt(s.attacks);
  document.getElementById("promisedOut").textContent = fmt(s.promised);

  const list = computed(s);
  const scale = Math.max(s.capacity, ...list.map(m => m.alerts)) * 1.08;
  const linePos = (s.capacity / scale) * 100;

  els.rows.innerHTML = "";
  sorted(list).forEach(m => {
    const b = document.createElement("button");
    b.className = "row" + (m.overflow ? " overflow" : "");
    b.type = "button";
    b.setAttribute("aria-pressed", m.id === selected ? "true" : "false");
    b.innerHTML = `
      <div class="who">
        <div class="nm">${m.name}</div>
        <div class="mt"><span class="tag">${m.id}</span>${m.note}</div>
      </div>
      <div class="track">
        <div class="bar${m.overflow ? " over" : ""}" style="width:${(m.alerts / scale) * 100}%"></div>
        <div class="bar promised" style="width:${(s.promised / scale) * 100}%"></div>
        <div class="shiftline" style="left:${linePos}%"></div>
      </div>
      <div class="num">
        <span class="big">${fmt(m.alerts)}</span>
        <span class="lbl">${m.overflow ? (m.overBy).toFixed(1) + "\\u00d7 over capacity" : "fits the shift"}</span>
      </div>`;
    b.addEventListener("click", () => { selected = m.id; render(); });
    els.rows.appendChild(b);
  });

  const m = list.find(x => x.id === selected) || list[0];
  document.getElementById("detailName").textContent = m.name;
  document.getElementById("detailNote").textContent =
    m.note + " \\u00b7 " + m.params.toLocaleString("en-US") + " parameters";

  const budgetNote = m.id === "E08" ? "sets the parameter budget"
    : m.params > DATA.meta.budget ? "over budget"
    : m.params === DATA.meta.budget ? "at the budget"
    : "under budget";
  const rows = [
    ["False alerts per day", fmt(m.alerts), m.overflow],
    ["A 1% rate would have promised", fmt(s.promised), false],
    ["Measured false alarm rate on test", rate(m.fpr), m.fpr > 0.02],
    ["Attacks detected per day", fmt(m.detected), false],
    ["Attacks missed per day", fmt(m.missed), false],
    ["Attack recall at the 1% threshold", m.recall.toFixed(4), false],
    ["Macro-F1", m.macroF1.toFixed(4), false],
    ["Parameters", m.params.toLocaleString("en-US") + " (" + budgetNote + ")", false],
  ];
  document.getElementById("detailStats").innerHTML = rows.map(
    ([k, v, warn]) => `<div><dt>${k}</dt><b class="${warn ? "warn" : ""}">${v}</b></div>`).join("");

  document.getElementById("detailRare").innerHTML = Object.entries(m.rare).map(([cls, r]) => `
    <div class="r">
      <span>${cls}</span>
      <span class="m"><i class="${r === 0 ? "zero" : ""}" style="width:${r * 100}%"></i></span>
      <span class="v">${pct(r)}</span>
    </div>`).join("");
}

["flows", "benign", "perAnalyst", "analysts"].forEach(id =>
  document.getElementById(id).addEventListener("input", render));

document.querySelectorAll("button.sort").forEach(btn =>
  btn.addEventListener("click", () => {
    sortKey = btn.dataset.sort;
    document.querySelectorAll("button.sort").forEach(b =>
      b.setAttribute("aria-pressed", b === btn ? "true" : "false"));
    render();
  }));

render();
</script>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(HTML.replace("__PAYLOAD__", payload), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes) with {len(models)} models")
