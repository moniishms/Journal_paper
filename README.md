# ResQMesh: Urgency-Aware Scheduling for LoRa Mesh Networks

##  Overview

ResQMesh is a lightweight urgency-aware scheduling framework designed for LoRa mesh networks in disaster communication scenarios. Traditional schedulers such as FIFO and Round Robin treat all messages equally, leading to delays in critical alerts.

This project introduces a heuristic-based scheduling mechanism that prioritizes messages based on urgency, along with an optional machine learning component for delay prediction.

---

##  Key Features

* Urgency-aware scheduling using heuristic scoring
* Congestion-aware prioritization
* Multi-hop LoRa mesh simulation
* ML-based delay risk prediction (Decision Tree)
* Comparative evaluation with FIFO and Round Robin
* Simulation across multiple disaster scenarios

---

##  System Architecture

The system consists of:

1. Message generation at nodes
2. Queue-based scheduling
3. Urgency score computation
4. Transmission over multi-hop network
5. Optional ML-based delay prediction

---

##  Urgency Function

The urgency score is computed as:

U = w1 * Tm + w2 * Cm + w3 * Sm

Where:

* Tm → Time in queue
* Cm → Message criticality
* Sm → Queue congestion ratio

---

##  Machine Learning Component

* Model: Decision Tree Classifier
* Features: Cm, Sm, hop count
* Task: Predict high-delay risk messages
* Used to enhance scheduling decisions (ML-boost variant)

---

##  Project Structure

```
ResQMesh/
│
├── data.py
├── scheduler.py
├── ml_model.py
├── plot.py
├── dataset.csv
│
├── results/
│   ├── mean_latency.png
│   ├── p75_latency.png
│   ├── jitter.png
│   └── delivery_ratio.png
│
└── README.md
```

---

##  Results Summary

The performance of different scheduling strategies is evaluated using key network metrics.

---

###  Mean Latency

<img src="results/mean_latency.png" width="600"/>

###  P75 Latency

<img src="results/p75_latency.png" width="600"/>

###  Jitter

<img src="results/jitter.png" width="600"/>

###  Delivery Ratio

<img src="results/delivery_ratio.png" width="600"/>

---

###  Numerical Results

## Baseline

| Scheduler        | Mean Latency | P75 Latency | Jitter | Delivery Ratio |
|------------------|-------------|-------------|--------|----------------|
| FIFO             | 288.71      | 306.16      | 53.08  | 0.307          |
| Round Robin      | 211.14      | 275.99      | 78.47  | 0.307          |
| ResQMesh         | 96.03       | 112.22      | 59.19  | 0.305          |
| ResQMesh + ML    | 86.74       | 91.87       | 57.59  | 0.293          |

## High Routine

| Scheduler        | Mean Latency | P75 Latency | Jitter | Delivery Ratio |
|------------------|-------------|-------------|--------|----------------|
| FIFO             | 287.70      | 306.12      | 55.57  | 0.306          |
| Round Robin      | 212.27      | 275.43      | 77.74  | 0.304          |
| ResQMesh         | 87.29       | 88.31       | 61.52  | 0.306          |
| ResQMesh + ML    | 72.92       | 70.37       | 54.66  | 0.278          |

## Burst

| Scheduler        | Mean Latency | P75 Latency | Jitter | Delivery Ratio |
|------------------|-------------|-------------|--------|----------------|
| FIFO             | 293.34      | 307.37      | 49.03  | 0.062          |
| Round Robin      | 275.83      | 300.25      | 49.68  | 0.062          |
| ResQMesh         | 209.08      | 270.62      | 74.14  | 0.061          |
| ResQMesh + ML    | 159.98      | 233.06      | 82.30  | 0.046          |

## SOS Intensive

| Scheduler        | Mean Latency | P75 Latency | Jitter | Delivery Ratio |
|------------------|-------------|-------------|--------|----------------|
| FIFO             | 287.70      | 306.12      | 55.57  | 0.306          |
| Round Robin      | 212.27      | 275.43      | 77.74  | 0.304          |
| ResQMesh         | 156.80      | 225.07      | 79.83  | 0.305          |
| ResQMesh + ML    | 105.32      | 128.70      | 65.70  | 0.229          |

## Large Load

| Scheduler        | Mean Latency | P75 Latency | Jitter | Delivery Ratio |
|------------------|-------------|-------------|--------|----------------|
| FIFO             | 293.34      | 307.37      | 49.03  | 0.062          |
| Round Robin      | 275.83      | 300.25      | 49.68  | 0.062          |
| ResQMesh         | 209.08      | 270.62      | 74.14  | 0.061          |
| ResQMesh + ML    | 159.98      | 233.06      | 82.30  | 0.046          |

## Packet Loss

| Scheduler        | Mean Latency | P75 Latency | Jitter | Delivery Ratio |
|------------------|-------------|-------------|--------|----------------|
| FIFO             | 289.44      | 306.87      | 53.58  | 0.280          |
| Round Robin      | 213.95      | 278.10      | 78.79  | 0.282          |
| ResQMesh         | 106.96      | 137.40      | 65.97  | 0.281          |
| ResQMesh + ML    | 91.81       | 99.98       | 60.17  | 0.261          |

---

##  How to Run

### 1. Generate Dataset

```bash
python data.py
```

### 2. Train ML Model

```bash
python ml_model.py
```

### 3. Run Simulation

```bash
python scheduler.py
```

### 4. Plot Results

```bash
python plot.py
```

---

##  Simulation Details

* Nodes: 50
* Simulation Time: 4000 ticks
* Max Queue Size: 100
* Multi-hop range: 1–7 hops

Includes:

* Channel noise
* Congestion spikes
* Retransmissions

---

##  Applications

* Disaster communication systems
* Emergency response networks
* IoT-based low-power networks
* Delay-sensitive distributed systems

---

##  Future Improvements

* Integration with real LoRa hardware
* Advanced ML models (Random Forest, XGBoost)
* Real-time deployment optimization
* Adaptive weight tuning

---

##  Author

Moniish Mohan Srinivasan
B.Tech CSE, VIT Chennai
