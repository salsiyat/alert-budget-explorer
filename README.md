# Alert Budget Explorer

An interactive tool for comparing intrusion detection models based on **attack detection, false alerts, and analyst workload**.

**Live Tool:** https://salsiyat.github.io/alert-budget-explorer/

Built for my MSDS 458 Deep Learning project at Northwestern University using the public UNSW-NB15 dataset.

## What it does

Enter your daily traffic and SOC staffing to compare 16 intrusion detection models.

The tool shows:
- Expected false alerts
- Attacks detected and missed
- Analyst workload
- Model size
- Recall for rare attack classes

## Key Finding

Models that perform well on attack recall do not always create a manageable alert workload.

The best neural model reached strong attack recall but also had the highest test false-positive rate (4.40%). The gradient boosting baseline achieved higher recall with a lower false-positive rate.

The study also found evidence of distribution shift between the training and test data (AUC = 0.91), so the tool should be used for **model comparison and planning**, not as a prediction of real-world alert volume.

## Data

Model results are stored in:

- `data/results_nb2.csv`
- `data/nb3_summary.json`

`build_explorer.py` regenerates `index.html` from these results.

## Dataset

Moustafa, N., & Slay, J. (2015). *UNSW-NB15: A comprehensive data set for network intrusion detection systems.* MilCIS.

## Note

This is a personal academic project using a public benchmark dataset. No operational or organizational data was used.

## License

MIT
