"""
full_evaluation.py

This is the single simulation script for this project, covering all
six schedulers evaluated in the paper: FIFO, RR, FPS, ResQMesh
(RESQ), ML-ResQMesh (ML_RESQ), and the lightweight Q-learning baseline
(QLEARN). For each scheduler and each of the six traffic scenarios, it
computes mean latency, P75 latency, jitter, delivery ratio, mean
energy consumption per delivered message, and the mean criticality of
delivered messages.

An earlier, narrower version of this simulation (five schedulers,
latency/P75/jitter/delivery ratio only, no energy or criticality
tracking) produced the results originally reported in Table VI. This
script's output for those five schedulers and four metrics was
verified to match that earlier version's output exactly before any
of the additional metrics (energy, criticality) or the QLEARN
scheduler were trusted. This script now supersedes that earlier
version and is the sole reference for reproducing every quantitative
result reported in the paper.
"""

import random
import numpy as np
from collections import deque
import joblib
import pandas as pd
import json

NUM_NODES = 50
SIM_TIME = 4000
Q_MAX = 100
SPIKE_PROB = 0.1
TTL = 300
ML_WEIGHT = 0.2

ml_model = joblib.load("resqmesh_dt_model.pkl")

# ---------------------------------------------------------------------
# Energy model constants (Section III, Energy Consumption Model)
# ---------------------------------------------------------------------
V = 3.3
I_TX = 0.120
I_IDLE = 0.012
P_TX = V * I_TX
P_IDLE = V * I_IDLE

EPS_OP = 1e-9
OPS_RESQ = 5
OPS_ML = 10
# QLEARN per-candidate cost: state discretization (3 divisions/multiplications
# + 2 min() bound checks = ~5 ops) plus one dict lookup (~1 op) plus the
# epsilon-greedy comparison (~1 op) = ~7 ops per candidate evaluated.
OPS_QLEARN = 7
E_PROC_RESQ = OPS_RESQ * EPS_OP
E_PROC_ML = OPS_ML * EPS_OP
E_PROC_QLEARN = OPS_QLEARN * EPS_OP

# ---------------------------------------------------------------------
# Q-learning hyperparameters (Section III, Lightweight Q-Learning Baseline)
# ---------------------------------------------------------------------
ALPHA = 0.3
EPSILON = 0.1
N_WAIT_BUCKETS = 5
N_OCC_BUCKETS = 5
N_HOP_BUCKETS = 3


class Message:
    def __init__(self, arrival, criticality, hop):
        self.arrival = arrival
        self.criticality = criticality
        self.hop = hop


def transmission_delay(hop, retrans_prob):
    base = hop
    noise = random.uniform(0, 2)
    spike = 0
    if random.random() < SPIKE_PROB:
        spike = random.randint(2, 5)
    retrans = 0
    if random.random() < retrans_prob:
        retrans = hop
    return base + noise + spike + retrans


def urgency(Tm, Cm, Sm):
    T_norm = min(Tm / 50, 1)
    C_norm = Cm / 3
    S_norm = Sm
    W1, W2, W3 = 0.6, 0.3, 0.1
    return W1 * T_norm + W2 * C_norm + W3 * S_norm


def generate_message(t, criticality_pool):
    Cm = random.choice(criticality_pool)
    hop = random.randint(1, 7)
    return Message(t, Cm, hop)


def select_fifo(queues):
    oldest_msg, oldest_q, oldest_index, oldest_time = None, None, None, 1e9
    for q in queues:
        for i, m in enumerate(q):
            if m.arrival < oldest_time:
                oldest_time, oldest_msg, oldest_q, oldest_index = m.arrival, m, q, i
    if oldest_msg:
        del oldest_q[oldest_index]
    return oldest_msg


def select_rr(queues, rr_index):
    n = len(queues)
    for i in range(n):
        idx = (rr_index + i) % n
        if len(queues[idx]) > 0:
            msg = queues[idx].popleft()
            return msg, (idx + 1) % n
    return None, rr_index


def select_fps(queues):
    best, best_q, best_index, highest_priority = None, None, None, -1
    for q in queues:
        for i, m in enumerate(q):
            priority = m.criticality
            if priority > highest_priority:
                highest_priority, best, best_q, best_index = priority, m, q, i
            elif priority == highest_priority:
                if m.arrival < best.arrival:
                    best, best_q, best_index = m, q, i
    if best:
        del best_q[best_index]
    return best


def select_resqmesh(queues, t):
    best, best_q, best_index, best_score = None, None, None, -1
    for q in queues:
        for i, m in enumerate(q):
            Tm = t - m.arrival
            Cm = m.criticality
            Sm = len(q) / Q_MAX
            score = urgency(Tm, Cm, Sm)
            if score > best_score:
                best_score, best, best_q, best_index = score, m, q, i
    if best:
        del best_q[best_index]
    return best


def select_resqmesh_ml(queues, t):
    candidates = []
    for q in queues:
        for i, m in enumerate(q):
            Tm = t - m.arrival
            Cm = m.criticality
            Sm = len(q) / Q_MAX
            candidates.append((m, q, i, Tm, Cm, Sm))
    if not candidates:
        return None
    feat_df = pd.DataFrame(
        [[c[4], c[5], c[0].hop] for c in candidates], columns=["Cm", "Sm", "hop"]
    )
    risks = ml_model.predict_proba(feat_df)[:, 1]
    best, best_q, best_index, best_score = None, None, None, -1
    for (m, q, i, Tm, Cm, Sm), risk in zip(candidates, risks):
        base = urgency(Tm, Cm, Sm)
        score = base + ML_WEIGHT * risk
        if score > best_score:
            best_score, best, best_q, best_index = score, m, q, i
    if best:
        del best_q[best_index]
    return best


def discretize_state(Tm, Cm, Sm, hop):
    wait_bucket = min(int(Tm / 10), N_WAIT_BUCKETS - 1)
    occ_bucket = min(int(Sm * N_OCC_BUCKETS), N_OCC_BUCKETS - 1)
    hop_bucket = min((hop - 1) * N_HOP_BUCKETS // 7, N_HOP_BUCKETS - 1)
    return (wait_bucket, Cm, occ_bucket, hop_bucket)


def select_qlearn(queues, t, q_table):
    candidates = []
    for q in queues:
        for i, m in enumerate(q):
            Tm = t - m.arrival
            Cm = m.criticality
            Sm = len(q) / Q_MAX
            state = discretize_state(Tm, Cm, Sm, m.hop)
            candidates.append((m, q, i, state))
    if not candidates:
        return None, None
    if random.random() < EPSILON:
        chosen = random.choice(candidates)
    else:
        best_val, chosen = -1e18, candidates[0]
        for cand in candidates:
            val = q_table.get(cand[3], 0.0)
            if val > best_val:
                best_val, chosen = val, cand
    m, q, i, state = chosen
    del q[i]
    return m, state


def qlearn_update(q_table, state, observed_latency):
    reward = -observed_latency
    old_val = q_table.get(state, 0.0)
    q_table[state] = old_val + ALPHA * (reward - old_val)


def run_simulation(scheduler_type, scenario="baseline"):
    gen_prob = 0.01
    retrans_prob = 0.15
    criticality_pool = [1, 2, 3]

    if scenario == "high_routine":
        criticality_pool = [1, 1, 1, 2, 3]
    elif scenario == "burst":
        pass
    elif scenario == "sos_intensive":
        criticality_pool = [1, 2, 3, 3, 3]
    elif scenario == "large_load":
        gen_prob = 0.05
    elif scenario == "packet_loss":
        retrans_prob = 0.3

    queues = [deque() for _ in range(NUM_NODES)]
    channel_busy_until = 0
    latencies = []
    delivered_criticalities = []
    energies = []
    generated = 0
    delivered = 0
    rr_index = 0
    q_table = {}
    if scheduler_type == "ML_RESQ":
        e_proc = E_PROC_ML
    elif scheduler_type == "QLEARN":
        e_proc = E_PROC_QLEARN
    else:
        e_proc = E_PROC_RESQ

    for t in range(SIM_TIME):
        for q in queues:
            for m in list(q):
                if t - m.arrival > TTL:
                    q.remove(m)

        current_gen_prob = gen_prob
        if scenario == "burst" and 1500 <= t < 2000:
            current_gen_prob = 0.08

        for i in range(NUM_NODES):
            if random.random() < current_gen_prob:
                if len(queues[i]) < Q_MAX:
                    queues[i].append(generate_message(t, criticality_pool))
                    generated += 1

        if t >= channel_busy_until:
            state = None
            if scheduler_type == "FIFO":
                msg = select_fifo(queues)
            elif scheduler_type == "RR":
                msg, rr_index = select_rr(queues, rr_index)
            elif scheduler_type == "FPS":
                msg = select_fps(queues)
            elif scheduler_type == "RESQ":
                msg = select_resqmesh(queues, t)
            elif scheduler_type == "ML_RESQ":
                msg = select_resqmesh_ml(queues, t)
            elif scheduler_type == "QLEARN":
                msg, state = select_qlearn(queues, t, q_table)
            else:
                msg = None

            if msg:
                t_wait = t - msg.arrival
                delay = transmission_delay(msg.hop, retrans_prob)
                t_tx = delay
                channel_busy_until = t + delay
                latency = channel_busy_until - msg.arrival
                latencies.append(latency)
                delivered_criticalities.append(msg.criticality)
                delivered += 1

                e_m = (P_TX * t_tx) + (P_IDLE * t_wait) + e_proc
                energies.append(e_m)

                if scheduler_type == "QLEARN" and state is not None:
                    qlearn_update(q_table, state, latency)

    return latencies, generated, delivered, delivered_criticalities, energies


def compute_metrics(latencies, generated, delivered, delivered_criticalities, energies):
    mean_latency = np.mean(latencies)
    p75 = np.percentile(latencies, 75)
    jitter = np.std(latencies)
    delivery_ratio = delivered / generated if generated > 0 else 0
    mean_criticality = np.mean(delivered_criticalities) if delivered_criticalities else 0
    mean_energy_mJ = np.mean(energies) * 1000 if energies else 0
    return mean_latency, p75, jitter, delivery_ratio, mean_criticality, mean_energy_mJ


scenarios = ["baseline", "high_routine", "burst", "sos_intensive", "large_load", "packet_loss"]
all_schedulers = ["FIFO", "RR", "FPS", "RESQ", "ML_RESQ", "QLEARN"]

results = {}

for scenario in scenarios:
    results[scenario] = {}
    for sch in all_schedulers:
        metrics_all = []
        for trial in range(10):
            random.seed(1000 + trial)
            np.random.seed(1000 + trial)
            lat, gen, deliv, crit, energies = run_simulation(sch, scenario)
            metrics = compute_metrics(lat, gen, deliv, crit, energies)
            metrics_all.append(metrics)

        avg = np.mean(metrics_all, axis=0)
        results[scenario][sch] = avg

        print(f"Scenario: {scenario} | Scheduler: {sch}")
        print(f"  Mean Latency : {avg[0]:.2f}")
        print(f"  P75 Latency  : {avg[1]:.2f}")
        print(f"  Jitter       : {avg[2]:.2f}")
        print(f"  Delivery Ratio: {avg[3]:.3f}")
        print(f"  Mean Delivered Criticality: {avg[4]:.3f}")
        print(f"  Mean Energy/msg (mJ): {avg[5]:.4f}")
        print("-------------")

out = {}
for scenario in scenarios:
    out[scenario] = {}
    for sch in all_schedulers:
        m = results[scenario][sch]
        out[scenario][sch] = {
            "mean_latency": float(m[0]),
            "p75_latency": float(m[1]),
            "jitter": float(m[2]),
            "delivery_ratio": float(m[3]),
            "mean_delivered_criticality": float(m[4]),
            "mean_energy_mJ": float(m[5]),
        }

with open("full_evaluation_results.json", "w") as f:
    json.dump(out, f, indent=2)

print("\nSaved to full_evaluation_results.json")