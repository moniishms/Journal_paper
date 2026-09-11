import random
import numpy as np
from collections import deque
import pandas as pd

NUM_NODES = 50
SIM_TIME = 8000
Q_MAX = 100
GEN_PROB = 0.01

RETRANS_PROB = 0.15
SPIKE_PROB = 0.1

random.seed(42)
np.random.seed(42)

class Message:
    _counter = 0

    def __init__(self, arrival, criticality, hop):
        self.arrival = arrival
        self.criticality = criticality
        self.hop = hop
        Message._counter += 1
        self.uid = Message._counter

def transmission_delay(hop):
    base = hop
    noise = random.uniform(0, 2)

    spike = 0
    if random.random() < SPIKE_PROB:
        spike = random.randint(2, 5)

    retrans = 0
    if random.random() < RETRANS_PROB:
        retrans = hop

    return base + noise + spike + retrans

T_CAP = 50  # ticks

def urgency(Tm, Cm, Sm):
    W1, W2, W3 = 0.6, 0.3, 0.1
    Tm_hat = min(Tm / T_CAP, 1)
    Cm_hat = Cm / 3
    return W1 * Tm_hat + W2 * Cm_hat + W3 * Sm

def generate_message(t):
    Cm = random.choice([1, 2, 3])
    hop = random.randint(1, 7)
    return Message(t, Cm, hop)

def generate_dataset():
    queues = [deque() for _ in range(NUM_NODES)]
    channel_busy_until = 0

    pending_snapshots = {}  # uid -> (Tm, Cm, Sm, hop)
    seen_ids = set()
    data = []

    for t in range(SIM_TIME):

        for i in range(NUM_NODES):
            if random.random() < GEN_PROB:
                if len(queues[i]) < Q_MAX:
                    queues[i].append(generate_message(t))

        # Record a snapshot the first time each message becomes head-of-queue
        for q in queues:
            if len(q) > 0:
                m = q[0]
                if m.uid not in seen_ids:
                    seen_ids.add(m.uid)
                    Tm = t - m.arrival
                    Cm = m.criticality
                    Sm = len(q) / Q_MAX
                    pending_snapshots[m.uid] = (Tm, Cm, Sm, m.hop)

        if t >= channel_busy_until:

            all_msgs = [q[0] for q in queues if len(q) > 0]
            if len(all_msgs) == 0:
                continue

            best_msg = None
            best_queue = None
            best_u = -1

            for q in queues:
                if len(q) == 0:
                    continue
                m = q[0]
                Tm = t - m.arrival
                Cm = m.criticality
                Sm = len(q) / Q_MAX
                u = urgency(Tm, Cm, Sm)
                if u > best_u:
                    best_u = u
                    best_msg = m
                    best_queue = q

            best_queue.popleft()

            tx_time = transmission_delay(best_msg.hop)
            channel_busy_until = t + tx_time
            latency = channel_busy_until - best_msg.arrival

            # Use the ORIGINAL snapshot taken when this message first became a candidate
            snap_Tm, snap_Cm, snap_Sm, snap_hop = pending_snapshots.pop(best_msg.uid)

            data.append([snap_Tm, snap_Cm, snap_Sm, snap_hop, latency])

    df = pd.DataFrame(data, columns=["Tm", "Cm", "Sm", "hop", "latency"])
    threshold = np.percentile(df["latency"], 75)
    df["label"] = (df["latency"] > threshold).astype(int)

    return df


df = generate_dataset()
print(df.head())
print("Dataset size:", len(df))
df.to_csv("dataset.csv", index=False)
print(df["Sm"].describe())
print(df.groupby("label")["Sm"].describe())