import random
import numpy as np
from collections import deque

# -----------------------
# Simulation Parameters
# -----------------------
NUM_NODES = 50
SIM_TIME = 4000
Q_MAX = 100
GEN_PROB = 0.01

RETRANS_PROB = 0.15
SPIKE_PROB = 0.1
TTL = 300

# -----------------------
# Message Class
# -----------------------
class Message:
    def __init__(self, arrival, criticality, hop):
        self.arrival = arrival
        self.criticality = criticality
        self.hop = hop

# -----------------------
# Channel Model
# -----------------------
def transmission_delay(hop):
    base = hop
    noise = random.uniform(0,2)

    spike = 0
    if random.random() < SPIKE_PROB:
        spike = random.randint(2,5)

    retrans = 0
    if random.random() < RETRANS_PROB:
        retrans = hop

    return base + noise + spike + retrans

# -----------------------
# Urgency Function (Normalized)
# -----------------------
def urgency(Tm, Cm, Sm):
    T_norm = min(Tm / 50, 1)
    C_norm = Cm / 3
    S_norm = Sm

    W1, W2, W3 = 0.6, 0.3, 0.1
    return W1*T_norm + W2*C_norm + W3*S_norm

# -----------------------
# Generate Message
# -----------------------
def generate_message(t):
    Cm = random.choice([1,2,3])
    hop = random.randint(1,7)
    return Message(t, Cm, hop)

# -----------------------
# FIFO Scheduler (Global FIFO)
# -----------------------
def select_fifo(queues):
    oldest_msg = None
    oldest_q = None
    oldest_index = None
    oldest_time = 1e9

    for q in queues:
        for i, m in enumerate(q):
            if m.arrival < oldest_time:
                oldest_time = m.arrival
                oldest_msg = m
                oldest_q = q
                oldest_index = i

    if oldest_msg:
        del oldest_q[oldest_index]

    return oldest_msg

# -----------------------
# Round Robin Scheduler
# -----------------------
def select_rr(queues, rr_index):
    n = len(queues)
    for i in range(n):
        idx = (rr_index + i) % n
        if len(queues[idx]) > 0:
            msg = queues[idx].popleft()
            return msg, (idx + 1) % n
    return None, rr_index

# -----------------------
# ResQMesh Scheduler
# -----------------------
def select_resqmesh(queues, t):
    best = None
    best_q = None
    best_index = None
    best_score = -1

    for q in queues:
        for i, m in enumerate(q):
            Tm = t - m.arrival
            Cm = m.criticality
            Sm = len(q)/Q_MAX

            score = urgency(Tm, Cm, Sm)

            if score > best_score:
                best_score = score
                best = m
                best_q = q
                best_index = i

    if best:
        del best_q[best_index]

    return best

# -----------------------
# ML Boost Scheduler
# -----------------------
def ml_risk_prediction(Cm, Sm, hop):
    risk = 0
    if Sm > 0.6:
        risk += 0.5
    if Cm == 3:
        risk += 0.3
    if hop > 4:
        risk += 0.2
    return risk

def select_resqmesh_ml(queues, t):
    best = None
    best_q = None
    best_index = None
    best_score = -1

    for q in queues:
        for i, m in enumerate(q):
            Tm = t - m.arrival
            Cm = m.criticality
            Sm = len(q)/Q_MAX

            base = urgency(Tm, Cm, Sm)
            risk = ml_risk_prediction(Cm, Sm, m.hop)

            score = base + 0.5 * risk

            if score > best_score:
                best_score = score
                best = m
                best_q = q
                best_index = i

    if best:
        del best_q[best_index]

    return best

# -----------------------
# Simulation
# -----------------------
def run_simulation(scheduler_type):
    queues = [deque() for _ in range(NUM_NODES)]
    channel_busy_until = 0

    latencies = []
    generated = 0
    delivered = 0

    rr_index = 0

    for t in range(SIM_TIME):

        # Drop old packets
        for q in queues:
            for m in list(q):
                if t - m.arrival > TTL:
                    q.remove(m)

        # Message generation
        for i in range(NUM_NODES):
            if random.random() < GEN_PROB:
                if len(queues[i]) < Q_MAX:
                    queues[i].append(generate_message(t))
                    generated += 1

        # Scheduling
        if t >= channel_busy_until:

            if scheduler_type == "FIFO":
                msg = select_fifo(queues)

            elif scheduler_type == "RR":
                msg, rr_index = select_rr(queues, rr_index)

            elif scheduler_type == "RESQ":
                msg = select_resqmesh(queues, t)

            elif scheduler_type == "ML_RESQ":
                msg = select_resqmesh_ml(queues, t)

            else:
                msg = None

            if msg:
                delay = transmission_delay(msg.hop)
                channel_busy_until = t + delay
                latency = channel_busy_until - msg.arrival

                latencies.append(latency)
                delivered += 1

    return latencies, generated, delivered

# -----------------------
# Metrics
# -----------------------
def compute_metrics(latencies, generated, delivered):
    mean_latency = np.mean(latencies)
    p75 = np.percentile(latencies, 75)
    jitter = np.std(latencies)
    delivery_ratio = delivered / generated if generated > 0 else 0

    return mean_latency, p75, jitter, delivery_ratio

# -----------------------
# Run Experiments
# -----------------------
schedulers = ["FIFO", "RR", "RESQ", "ML_RESQ"]

for sch in schedulers:
    metrics_all = []

    for trial in range(10):
        lat, gen, deliv = run_simulation(sch)
        metrics = compute_metrics(lat, gen, deliv)
        metrics_all.append(metrics)

    avg = np.mean(metrics_all, axis=0)

    print(sch)
    print("Mean Latency:", avg[0])
    print("P75 Latency:", avg[1])
    print("Jitter:", avg[2])
    print("Delivery Ratio:", avg[3])
    print("-------------")