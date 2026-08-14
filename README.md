# Alert budget explorer

An interactive tool that translates sixteen intrusion detection models into the question a
security operations manager actually asks: **how many alerts land in an analyst's queue tomorrow,
and what does the model miss?**

**Live:** https://USERNAME.github.io/REPO-NAME/

Built as part of a graduate deep learning project (MSDS 458, Northwestern University) on the
public UNSW-NB15 intrusion detection benchmark.

## Why it exists

Every model in the study was calibrated to a **1% false alarm rate** on validation data, then
evaluated on a held-out test partition. None of them delivered that rate — the average overshoot
was **3.74×**. A target of roughly 370 false alerts became roughly 1,384.

A leaderboard hides that. This tool does not: you enter your own traffic volume and staffing,
and each model shows the false alerts it delivers at its *measured* rate against the alerts your
shift can actually clear.

The result is a ranking inversion worth seeing. The best neural model by attack recall (a
four-layer network with dropout and batch normalisation) has the **worst** delivered false alarm
rate in the study at 4.40%, and overflows the shift first. A gradient boosting baseline has both
the highest recall and the lowest alarm rate, with fewer stored parameters.

## What you can change

| Input | Meaning |
|---|---|
| Flows per day | Connections your sensor sees |
| Benign share | Portion of traffic that is not an attack |
| Alerts cleared per analyst | Triage throughput in one shift |
| Analysts on shift | People reviewing the queue |

Selecting any model shows its delivered alarm rate, attacks detected and missed per day,
parameter count against the study's fixed budget, and per-class recall on the four rarest attack
types — where a strong headline number can hide a class the model never detects at all.

## Where this tool stops being trustworthy

It extrapolates a false alarm rate measured on the UNSW-NB15 test partition to your traffic. In
this study that assumption failed across the dataset's own two halves: a classifier trained only
to tell whether a benign record came from the training or test partition reached **0.91 AUC**, so
the benign traffic itself differs across the split.

Treat every number as a planning estimate for comparing models under one shared assumption — not
as a prediction of absolute alert volume. Measure the rate on your own traffic before staffing
against it. That warning is stated inside the interface, not only here.

## Data provenance

All model numbers come from `data/results_nb2.csv` and `data/nb3_summary.json`, the saved outputs
of the project's notebooks. Nothing is transcribed by hand: `build_explorer.py` reads those files
and writes `index.html`.

Sixteen experiments, single run at a fixed seed (458). Attack traffic in UNSW-NB15 is
laboratory-generated rather than captured from a live network.

## Rebuilding

```bash
python3 build_explorer.py    # reads data/, rewrites index.html
```

No dependencies, no build tooling, no network calls. `index.html` is a single self-contained file.

## Dataset citation

Moustafa, N., & Slay, J. (2015). UNSW-NB15: A comprehensive data set for network intrusion
detection systems (UNSW-NB15 network data set). *2015 Military Communications and Information
Systems Conference (MilCIS)*, 1–6. https://doi.org/10.1109/MilCIS.2015.7348942

## Note

A personal academic project built on a public benchmark dataset. It does not represent any
employer, and no operational or organizational data was used.

## License

MIT — see [LICENSE](LICENSE).
