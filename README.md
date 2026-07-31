# ResQMesh: An Urgency-Aware Scheduling Framework for LoRa Mesh Networks in Disaster Communication

This repository contains the simulation code, machine learning pipeline, dataset, and result figures for the paper:

> **An Urgency-Aware Scheduling Framework for LoRa Mesh Networks in Disaster Communication**
> Moniish Mohan Srinivasan, Kirankumar Manivannan, Kumaran K, Saranya G
> Vellore Institute of Technology (VIT), Chennai

---

## Overview

**ResQMesh** is a lightweight, urgency-aware heuristic scheduler for LoRa mesh networks operating in disaster communication scenarios. It prioritizes message transmission using a weighted combination of:

- **Waiting time** (how long a message has been queued)
- **Message criticality** (SOS / Medical / Routine)
- **Queue congestion** (local queue occupancy ratio)

**ML-ResQMesh** is an optional variant that augments the heuristic urgency score with a delay-risk prediction from a lightweight Decision Tree classifier, trained offline on simulation-generated data.

Both schedulers are evaluated against **FIFO**, **Round Robin (RR)**, and **Fair Priority Scheduling (FPS)** across six disaster communication traffic scenarios: baseline, high routine, burst, SOS intensive, large load, and packet loss.

---

## Repository Structure

```
├── scheduler_simulation.py     # Main simulation: runs all 5 schedulers across 6 scenarios,
│                                # produces mean latency, P75 latency, jitter, and delivery ratio
├── dataset.py                  # Generates the message-level training dataset used to train
│                                # the Decision Tree classifier
├── ml_model.py                 # Trains the Decision Tree classifier on dataset.csv, evaluates
│                                # classification performance, and saves the trained model
├── plots.py                    # Generates all result figures (bar/line/horizontal bar charts)
│                                # from the simulation output
├── dataset.csv                 # Generated dataset (1,253 message-level records) used to train
│                                # the Decision Tree classifier — also archived on Zenodo (see below)
├── resqmesh_dt_model.pkl       # Trained Decision Tree classifier (serialized with joblib)
├── results/                    # All generated result figures (24 PDFs + ROC curve)
│   ├── MeanLatency_*.pdf       # Mean latency comparison, per scenario
│   ├── P75Latency_*.pdf        # 75th-percentile latency comparison, per scenario
│   ├── Jitter_*.pdf            # Jitter comparison, per scenario
│   ├── DeliveryRatio_*.pdf     # Delivery ratio comparison, per scenario
│   └── roc_curve.png           # ROC curve of the Decision Tree classifier
└── README.md
```

---

## Requirements

```bash
pip install numpy pandas scikit-learn matplotlib joblib
```

Tested with Python 3.9+.

---

## Reproducing the Results

The pipeline runs in three stages. Run them in this order:

### 1. Generate the training dataset

```bash
python dataset.py
```

This runs a discrete-event simulation of the heuristic ResQMesh scheduler and records message-level features (`Tm`, `Cm`, `Sm`, `hop`, `latency`) the first time each message becomes eligible for transmission — not only at the moment it is scheduled — to avoid selection bias toward already-congested conditions. Messages with latency above the 75th percentile are labeled high delay risk (`1`); the rest are labeled low risk (`0`).

Output: `dataset.csv` (1,253 rows, ~75/25 class split)

### 2. Train the Decision Tree classifier

```bash
python ml_model.py
```

Trains a Decision Tree classifier (`max_depth=5`, `min_samples_leaf=8`, Gini splitting criterion, `random_state=42`) on `dataset.csv` using an 80/20 train-test split. Prints accuracy, precision, recall, F1-score, ROC-AUC, and the confusion matrix, and plots the ROC curve.

Output: `resqmesh_dt_model.pkl`, `roc_curve.png`

### 3. Run the scheduling simulation

```bash
python scheduler_simulation.py
```

Runs all five schedulers (FIFO, RR, FPS, ResQMesh, ML-ResQMesh) across all six traffic scenarios, with 10 trials per scenario (seeds 1000–1009), each trial running 4,000 discrete simulation ticks. ML-ResQMesh loads the trained classifier from `resqmesh_dt_model.pkl` and blends its predicted risk score into the urgency formula.

Output: printed Mean Latency / P75 Latency / Jitter / Delivery Ratio for every scheduler × scenario combination.

### 4. Generate figures

```bash
python plots.py
```

Produces all result figures (bar charts, line charts, horizontal bar charts) shown in the paper, saved to `results/`.

---

## Key Results

| Metric | ResQMesh vs. FIFO | ML-ResQMesh vs. ResQMesh |
|---|---|---|
| Average Mean Latency | **−55.4%** | Comparable in 5/6 scenarios; small trade-off under burst congestion |
| Average P75 Latency | **−45.5%** | Comparable in 5/6 scenarios; small trade-off under burst congestion |

The Decision Tree classifier achieves **87.3% accuracy**, **78.7% precision**, **71.6% recall**, and a **0.939 ROC-AUC** on held-out test data for high-delay-risk prediction. However, integrating this classifier into the live scheduler provided limited additional scheduling benefit beyond the heuristic urgency score alone — full analysis and discussion in the paper (Sections VI–VIII).

A sensitivity analysis over the risk-weighting constant λ ∈ {0.1, 0.2, 0.3, 0.5, 0.8, 1.0} confirmed this limitation is not resolved by increasing the strength of the predictive term.

---

## Dataset

The dataset generated for this study (`dataset.csv`) is also permanently archived on Zenodo with a DOI:

📦 **[https://doi.org/10.5281/zenodo.21587358](https://doi.org/10.5281/zenodo.21587358)**

Licensed under CC-BY 4.0.

---

## Citation

If you use this code or dataset, please cite:

```bibtex
@article{resqmesh2026,
  title   = {An Urgency-Aware Scheduling Framework for LoRa Mesh Networks in Disaster Communication},
  author  = {Srinivasan, Moniish Mohan and Manivannan, Kirankumar and K, Kumaran and G, Saranya},
  journal = {Under review},
  year    = {2026}
}
```


## Acknowledgment

The authors would like to thank Vellore Institute of Technology (VIT), Chennai, for providing the academic environment, computing resources, and infrastructure that supported this research.
