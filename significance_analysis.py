"""
significance_analysis.py

A verified twin of full_evaluation.py, identical in every scheduling,
channel, energy and Q-learning detail. Instead of averaging away the
10 per-trial values immediately, this script keeps them, so that
standard deviation and significance tests can be computed across the
10 random seeds (1000-1009) used for every scheduler/scenario
combination.

This script first re-derives the mean values for all six metrics and
checks them against full_evaluation_results.json. If those means do
not match exactly, the per-trial data and significance tests below
should not be trusted.

Three significance tables are produced, matched to the specific
claims made in the paper:

  Table 1 -- ResQMesh vs. FIFO, paired t-test, on the three headline
             metrics quantified in the abstract (mean latency, P75
             latency, mean energy). Backs the abstract's percentage
             claims against the seeds used.

  Table 2 -- QLEARN vs. the CORRECT per-scenario no-preference
             baseline (the actual mean of that scenario's
             criticality-generation pool, not a flat 2.0), one-sample
             t-test on mean delivered criticality. Backs the paper's
             central claim that QLEARN neglects message criticality.

  Table 3 -- ResQMesh vs. ML-ResQMesh, a single paired t-test on mean
             latency (the same metric already tested against FIFO,
             for consistency), across all six scenarios. Deliberately
             NOT run separately across all six metrics: doing so
             surfaces a borderline result (jitter, High Routine,
             p=0.044) that does not survive correction for the 6
             simultaneous comparisons (Bonferroni alpha = 0.05/6 =
             0.0083) and would misleadingly look "significant" if
             reported in isolation. The other metrics in the one
             scenario where ResQMesh and ML-ResQMesh differ (High
             Routine) are reported descriptively in the paper instead
             of as separate formal tests.
"""

import random
import numpy as np
from collections import deque
import joblib
import pandas as pd
import json
from scipy import stats

NUM_NODES = 50
SIM_TIME = 4000
Q_MAX = 100
SPIKE_PROB = 0.1
TTL = 300
ML_WEIGHT = 0.2

ml_model = joblib.load("resqmesh_dt_model.pkl")

V = 3.3
I_TX = 0.120
I_IDLE = 0.012
P_TX = V * I_TX
P_IDLE = V * I_IDLE

EPS_OP = 1e-9
OPS_RESQ = 5
OPS_ML = 10
OPS_QLEARN = 7
E_PROC_RESQ = OPS_RESQ * EPS_OP
E_PROC_ML = OPS_ML * EPS_OP
E_PROC_QLEARN = OPS_QLEARN * EPS_OP

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
    W1, W2, W3 = 0.10, 0.40, 0.50  # re-derived via weight sensitivity grid search
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

# The true no-preference baseline per scenario: the actual mean of that
# scenario's criticality-generation pool (Section V-B / Table
# traffic_modes), NOT a flat 2.0 assumed for all six.
POOL_MEANS = {
    "baseline": 2.0,
    "high_routine": 1.6,
    "burst": 2.0,
    "sos_intensive": 2.4,
    "large_load": 2.0,
    "packet_loss": 2.0,
}

metric_idx = {"mean_latency": 0, "p75_latency": 1, "jitter": 2,
              "delivery_ratio": 3, "mean_criticality": 4, "mean_energy": 5}

# ---------------------------------------------------------------------
# Run all simulations, keeping every per-trial value
# ---------------------------------------------------------------------
per_trial = {}
results = {}

for scenario in scenarios:
    per_trial[scenario] = {}
    results[scenario] = {}
    for sch in all_schedulers:
        metrics_all = []
        for trial in range(10):
            random.seed(1000 + trial)
            np.random.seed(1000 + trial)
            lat, gen, deliv, crit, energies = run_simulation(sch, scenario)
            metrics_all.append(compute_metrics(lat, gen, deliv, crit, energies))
        per_trial[scenario][sch] = metrics_all
        results[scenario][sch] = np.mean(metrics_all, axis=0)

# ---------------------------------------------------------------------
# Step 1: verify means match full_evaluation_results.json exactly
# ---------------------------------------------------------------------
with open("full_evaluation_results.json") as f:
    published = json.load(f)

metric_keys = ["mean_latency", "p75_latency", "jitter", "delivery_ratio",
               "mean_delivered_criticality", "mean_energy_mJ"]

mismatches = 0
for scenario in scenarios:
    for sch in all_schedulers:
        avg = results[scenario][sch]
        pub = published[scenario][sch]
        for idx, key in enumerate(metric_keys):
            if abs(avg[idx] - pub[key]) > 1e-3:
                print(f"MISMATCH {scenario} {sch} {key}: computed={avg[idx]:.4f} published={pub[key]:.4f}")
                mismatches += 1

print(f"Verification against full_evaluation_results.json: "
      f"{'ALL MATCH' if mismatches == 0 else f'{mismatches} MISMATCHES -- DO NOT TRUST BELOW'}")


def paired_trials(scenario, sch_a, sch_b, metric):
    idx = metric_idx[metric]
    a = [m[idx] for m in per_trial[scenario][sch_a]]
    b = [m[idx] for m in per_trial[scenario][sch_b]]
    return a, b


# ---------------------------------------------------------------------
# Table 1: ResQMesh vs. FIFO -- mean latency, P75 latency, mean energy
# (the three metrics quantified in the abstract)
# ---------------------------------------------------------------------
print("\n" + "=" * 90)
print("TABLE 1: ResQMesh vs. FIFO -- mean latency, P75 latency, mean energy (paired t-test)")
print("=" * 90)

table1 = {}
for scenario in scenarios:
    table1[scenario] = {}
    for metric in ["mean_latency", "p75_latency", "mean_energy"]:
        fifo_trials, resq_trials = paired_trials(scenario, "FIFO", "RESQ", metric)
        fifo_mean, fifo_std = np.mean(fifo_trials), np.std(fifo_trials, ddof=1)
        resq_mean, resq_std = np.mean(resq_trials), np.std(resq_trials, ddof=1)
        t_stat, p_value = stats.ttest_rel(fifo_trials, resq_trials)

        table1[scenario][metric] = {
            "fifo_mean": float(fifo_mean), "fifo_std": float(fifo_std),
            "resq_mean": float(resq_mean), "resq_std": float(resq_std),
            "t_stat": float(t_stat), "p_value": float(p_value),
        }
        print(f"{scenario:15s} {metric:14s} FIFO={fifo_mean:10.2f}(sd={fifo_std:7.2f})  "
              f"RESQ={resq_mean:10.2f}(sd={resq_std:7.2f})  t={t_stat:8.3f}  p={p_value:.3e}")

# ---------------------------------------------------------------------
# Table 2: QLEARN vs. the CORRECT per-scenario no-preference baseline
# (one-sample t-test on mean delivered criticality)
# ---------------------------------------------------------------------
print("\n" + "=" * 90)
print("TABLE 2: QLEARN vs. correct per-scenario no-preference baseline (mean delivered criticality)")
print("=" * 90)

table2 = {}
for scenario in scenarios:
    idx = metric_idx["mean_criticality"]
    q_trials = [m[idx] for m in per_trial[scenario]["QLEARN"]]
    q_mean, q_std = np.mean(q_trials), np.std(q_trials, ddof=1)
    pool_mean = POOL_MEANS[scenario]
    t_stat, p_value = stats.ttest_1samp(q_trials, pool_mean)

    table2[scenario] = {
        "pool_mean": pool_mean, "qlearn_mean": float(q_mean), "qlearn_std": float(q_std),
        "t_stat": float(t_stat), "p_value": float(p_value),
    }
    verdict = ("indistinguishable from random" if p_value >= 0.05
               else ("significantly ABOVE baseline" if q_mean > pool_mean
                     else "significantly BELOW baseline"))
    print(f"{scenario:15s} pool_mean={pool_mean:.2f}  QLEARN={q_mean:.4f}(sd={q_std:.4f})  "
          f"t={t_stat:8.3f}  p={p_value:.4f}  -- {verdict}")

# ---------------------------------------------------------------------
# Table 3: ResQMesh vs. ML-ResQMesh -- ONE confirmatory test (mean
# latency only, consistent with the FIFO comparison metric), across
# all six scenarios. See module docstring for why the other five
# metrics are not each run as separate formal tests.
# ---------------------------------------------------------------------
print("\n" + "=" * 90)
print("TABLE 3: ResQMesh vs. ML-ResQMesh -- mean latency (paired t-test)")
print("=" * 90)

table3 = {}
for scenario in scenarios:
    resq_trials, ml_trials = paired_trials(scenario, "RESQ", "ML_RESQ", "mean_latency")
    resq_mean, resq_std = np.mean(resq_trials), np.std(resq_trials, ddof=1)
    ml_mean, ml_std = np.mean(ml_trials), np.std(ml_trials, ddof=1)

    if np.allclose(resq_trials, ml_trials):
        t_stat, p_value = 0.0, 1.0
    else:
        t_stat, p_value = stats.ttest_rel(resq_trials, ml_trials)

    table3[scenario] = {
        "resq_mean": float(resq_mean), "resq_std": float(resq_std),
        "ml_resq_mean": float(ml_mean), "ml_resq_std": float(ml_std),
        "t_stat": float(t_stat), "p_value": float(p_value),
    }
    note = "identical across all 10 trials" if np.isclose(p_value, 1.0) else "not identical"
    print(f"{scenario:15s} RESQ={resq_mean:7.2f}(sd={resq_std:5.2f})  "
          f"ML_RESQ={ml_mean:7.2f}(sd={ml_std:5.2f})  t={t_stat:7.3f}  p={p_value:.3f}  ({note})")

# ---------------------------------------------------------------------
# Save all three tables
# ---------------------------------------------------------------------
with open("significance_results.json", "w") as f:
    json.dump({
        "table1_resq_vs_fifo": table1,
        "table2_qlearn_vs_baseline": table2,
        "table3_resq_vs_ml_resq_latency": table3,
    }, f, indent=2)

print("\nSaved to significance_results.json")