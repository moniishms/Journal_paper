import random
import numpy as np
from collections import deque

NUM_NODES = 50
SIM_TIME = 4000
Q_MAX = 100
SPIKE_PROB = 0.1
TTL = 300

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
    return W1*T_norm + W2*C_norm + W3*S_norm

def generate_message(t, criticality_pool):
    Cm = random.choice(criticality_pool)
    hop = random.randint(1, 7)
    return Message(t, Cm, hop)

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

def select_rr(queues, rr_index):
    n = len(queues)
    for i in range(n):
        idx = (rr_index + i) % n
        if len(queues[idx]) > 0:
            msg = queues[idx].popleft()
            return msg, (idx + 1) % n
    return None, rr_index
def select_fps(queues):
    best = None
    best_q = None
    best_index = None
    highest_priority = -1

    for q in queues:
        for i, m in enumerate(q):
            # Higher criticality = higher priority
            # Priority mapping:
            # 3 = SOS (Highest)
            # 2 = Emergency
            # 1 = Routine
            priority = m.criticality

            if priority > highest_priority:
                highest_priority = priority
                best = m
                best_q = q
                best_index = i

            # FIFO within the same priority
            elif priority == highest_priority:
                if m.arrival < best.arrival:
                    best = m
                    best_q = q
                    best_index = i

    if best:
        del best_q[best_index]

    return best

def select_resqmesh(queues, t):
    best = None
    best_q = None
    best_index = None
    best_score = -1

    for q in queues:
        for i, m in enumerate(q):
            Tm = t - m.arrival
            Cm = m.criticality
            Sm = len(q) / Q_MAX
            score = urgency(Tm, Cm, Sm)
            if score > best_score:
                best_score = score
                best = m
                best_q = q
                best_index = i

    if best:
        del best_q[best_index]

    return best

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
            Sm = len(q) / Q_MAX
            base = urgency(Tm, Cm, Sm)
            risk = ml_risk_prediction(Cm, Sm, m.hop)
            score = base + 0.2 * risk
            if score > best_score:
                best_score = score
                best = m
                best_q = q
                best_index = i

    if best:
        del best_q[best_index]

    return best

def run_simulation(scheduler_type, scenario="baseline"):

    # Scenario parameters
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
    generated = 0
    delivered = 0
    rr_index = 0

    for t in range(SIM_TIME):

        # Drop old packets
        for q in queues:
            for m in list(q):
                if t - m.arrival > TTL:
                    q.remove(m)
        current_gen_prob = gen_prob
        if scenario == "burst" and 1500 <= t < 2000:
            current_gen_prob = 0.08   # spike above baseline for a limited window

        # Message generation
        for i in range(NUM_NODES):
            if random.random() < current_gen_prob:
                if len(queues[i]) < Q_MAX:
                    queues[i].append(
                        generate_message(t, criticality_pool)
                    )
                    generated += 1

        # Scheduling
        if t >= channel_busy_until:
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
            else:
                msg = None

            if msg:
                delay = transmission_delay(msg.hop, retrans_prob)
                channel_busy_until = t + delay
                latency = channel_busy_until - msg.arrival
                latencies.append(latency)
                delivered += 1

    return latencies, generated, delivered

def compute_metrics(latencies, generated, delivered):
    mean_latency = np.mean(latencies)
    p75 = np.percentile(latencies, 75)
    jitter = np.std(latencies)
    delivery_ratio = delivered / generated if generated > 0 else 0
    return mean_latency, p75, jitter, delivery_ratio

# Run all scenarios and schedulers
scenarios = [
    "baseline",
    "high_routine",
    "burst",
    "sos_intensive",
    "large_load",
    "packet_loss"
]

schedulers = ["FIFO", "RR", "FPS","RESQ", "ML_RESQ"]

results = {}

for scenario in scenarios:
    results[scenario] = {}
    for sch in schedulers:
        metrics_all = []
        for trial in range(10):
            random.seed(1000 + trial)
            np.random.seed(1000 + trial)
            lat, gen, deliv = run_simulation(sch, scenario)
            metrics = compute_metrics(lat, gen, deliv)
            metrics_all.append(metrics)

        avg = np.mean(metrics_all, axis=0)
        results[scenario][sch] = avg

        print(f"Scenario: {scenario} | Scheduler: {sch}")
        print(f"  Mean Latency : {avg[0]:.2f}")
        print(f"  P75 Latency  : {avg[1]:.2f}")
        print(f"  Jitter       : {avg[2]:.2f}")
        print(f"  Delivery Ratio: {avg[3]:.3f}")
        print("-------------")