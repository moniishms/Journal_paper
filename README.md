# ResQMesh

**An Urgency-Aware Scheduling Framework for LoRa Mesh Networks in Disaster Communication**

Moniish Mohan Srinivasan, Kirankumar Manivannan, Reena Roy R — VIT Chennai

Standard LoRa mesh schedulers (FIFO, Round Robin) treat an SOS message the same as routine telemetry. ResQMesh scores each queued message by urgency and transmits the highest-scoring one first. ML-ResQMesh adds a Decision Tree delay-risk predictor on top of that score.

## How it works
U = w1 * Tm + w2 * Cm + w3 * Sm

- `Tm` — time in queue
- `Cm` — criticality: SOS (3), Medical (2), Routine (1)
- `Sm` — queue congestion ratio (`queue_length / Q_max`)

Weights: `w1=0.5, w2=0.3, w3=0.2`. Computed locally per node, per tick — no central coordinator.

ML-ResQMesh trains a Decision Tree (max depth 4) on `{Cm, Sm, hop_count}` to predict delay risk and folds that into the urgency score.

## Repo structure
ResQMesh/
├── scheduler_simulation.py   # FIFO / RR / FPS / ResQMesh / ML-ResQMesh comparison
├── gen_dataset.py             # generates ML training dataset
├── train.py                   # trains and evaluates the Decision Tree
├── dataset.csv
├── plots/                     # figure-generation scripts (output: PDF)
└── README.md

## Running it

```bash
python gen_dataset.py              # dataset (2000 ticks, GEN_PROB=0.15)
python train.py                    # Decision Tree train + eval
python scheduler_simulation.py     # 6 scenarios x 5 schedulers x 10 trials, 4000 ticks
python plots/mean_latency.py
python plots/p75_latency.py
python plots/jitter.py
python plots/delivery_ratio.py
```

`scheduler_simulation.py` uses fixed seeds (1000–1009) — fully reproducible. `gen_dataset.py` is **not seeded**; reruns give different datasets, and Decision Tree accuracy varies ~0.80–0.99 between runs. Fixing this is on the to-do list.

Figures are saved as PDF under `results/` (not embedded here — see the PDFs directly).

## Scenarios

| Scenario | Change |
|---|---|
| `baseline` | standard traffic |
| `high_routine` | routine-heavy criticality mix |
| `burst` | temporary generation spike (ticks 1500–2000) |
| `sos_intensive` | SOS-heavy criticality mix |
| `large_load` | generation probability raised throughout |
| `packet_loss` | retransmission probability raised (0.15 → 0.30) |

## Results (10-trial average, 4000 ticks)

### Baseline
| Scheduler | Mean Latency | P75 | Jitter | Delivery Ratio |
|---|--:|--:|--:|--:|
| FIFO | 288.71 | 306.16 | 53.08 | 0.307 |
| Round Robin | 211.14 | 275.99 | 78.47 | 0.307 |
| FPS | 160.13 | 219.43 | 79.02 | 0.307 |
| ResQMesh | 96.03 | 112.22 | 59.19 | 0.305 |
| ML-ResQMesh | 86.74 | 91.87 | 57.59 | 0.293 |

### High Routine
| Scheduler | Mean Latency | P75 | Jitter | Delivery Ratio |
|---|--:|--:|--:|--:|
| FIFO | 287.70 | 306.12 | 55.57 | 0.306 |
| Round Robin | 212.27 | 275.43 | 77.74 | 0.304 |
| FPS | 101.33 | 246.05 | 120.97 | 0.301 |
| ResQMesh | 87.29 | 88.31 | 61.52 | 0.306 |
| ML-ResQMesh | 72.92 | 70.37 | 54.66 | 0.278 |

### Burst
| Scheduler | Mean Latency | P75 | Jitter | Delivery Ratio |
|---|--:|--:|--:|--:|
| FIFO | 288.95 | 306.27 | 53.10 | 0.165 |
| Round Robin | 221.59 | 285.76 | 78.41 | 0.164 |
| FPS | 203.50 | 293.73 | 101.72 | 0.163 |
| ResQMesh | 120.00 | 169.67 | 78.54 | 0.164 |
| ML-ResQMesh | 103.16 | 124.28 | 70.05 | 0.149 |

### SOS Intensive
| Scheduler | Mean Latency | P75 | Jitter | Delivery Ratio |
|---|--:|--:|--:|--:|
| FIFO | 287.70 | 306.12 | 55.57 | 0.306 |
| Round Robin | 212.27 | 275.43 | 77.74 | 0.304 |
| FPS | 278.72 | 304.75 | 63.61 | 0.306 |
| ResQMesh | 156.80 | 225.07 | 79.83 | 0.305 |
| ML-ResQMesh | 105.32 | 128.70 | 65.70 | 0.229 |

### Large Load
| Scheduler | Mean Latency | P75 | Jitter | Delivery Ratio |
|---|--:|--:|--:|--:|
| FIFO | 293.34 | 307.37 | 49.03 | 0.062 |
| Round Robin | 275.83 | 300.25 | 49.68 | 0.062 |
| FPS | 291.14 | 306.84 | 51.35 | 0.062 |
| ResQMesh | 209.08 | 270.62 | 74.14 | 0.061 |
| ML-ResQMesh | 159.98 | 233.06 | 82.30 | 0.046 |

### Packet Loss
| Scheduler | Mean Latency | P75 | Jitter | Delivery Ratio |
|---|--:|--:|--:|--:|
| FIFO | 289.44 | 306.87 | 53.58 | 0.280 |
| Round Robin | 213.95 | 278.10 | 78.79 | 0.282 |
| FPS | 223.11 | 289.88 | 87.88 | 0.279 |
| ResQMesh | 106.96 | 137.40 | 65.97 | 0.281 |
| ML-ResQMesh | 91.81 | 99.98 | 60.17 | 0.261 |

**Averaged across all 6 scenarios (vs. FIFO):** ResQMesh cuts mean latency ~55%, P75 latency ~45%. ML-ResQMesh improves another ~18% over ResQMesh on mean latency. Jitter rises ~31% (cost of urgency-based reordering). Delivery ratio moves <1% on average — driven by channel saturation, not scheduling policy.

## Decision Tree classifier

Features: `{Cm, Sm, hop_count}` — `Tm` excluded (directly correlated with latency, causes trivial threshold learning).

| Metric | Value |
|---|--:|
| Accuracy | 0.857 |
| Precision | 0.55 |
| Recall | 1.00 |
| F1-score | 0.71 |
| ROC-AUC | 0.923 |

**Confusion matrix** (63 test samples):

| | Pred. Low Risk | Pred. High Risk |
|---|--:|--:|
| **Actual Low Risk** | 43 | 9 |
| **Actual High Risk** | 0 | 11 |

Recall = 1.0 → zero false negatives. Precision = 0.55 → some false alarms, an intentional trade-off since missing a genuine high-risk message costs more than a false positive.

> `gen_dataset.py` is unseeded — metrics above are from one representative run; repeats range ~0.80–0.99 accuracy.

## Simulation parameters

| Parameter | Scheduler comparison | Dataset generation |
|---|---|---|
| Nodes | 50 | 50 |
| Duration | 4000 ticks | 2000 ticks |
| Queue size | 100 | 100 |
| Hop range | 1–7 | 1–7 |
| Gen. probability | 0.01 (up to 0.08 in burst) | 0.15 |
| Retransmission prob. | 0.15 (0.30 in packet_loss) | 0.15 |
| Channel noise | U(0,2) ticks | U(0,2) ticks |
| Spike probability | 0.1 | 0.1 |
| TTL | 300 ticks | — |
| Trials | 10/scenario, seeds 1000–1009 | 1 (unseeded) |

## Known limitations

- Simulation only — no real LoRa hardware yet.
- `gen_dataset.py` unseeded — ML metrics not fully reproducible.
- Urgency weights fixed by hand, no sensitivity sweep.
- SOS class (`Cm=3`) can be underrepresented in a given dataset run.

## Next steps

- Seed the dataset generator.
- Weight sensitivity analysis.
- Try Random Forest / gradient boosting.
- Real LoRa testbed validation.

## Author

Moniish Mohan Srinivasan — B.Tech CSE, VIT Chennai
