import random
import numpy as np
from collections import deque
import pandas as pd

NUM_NODES = 50
SIM_TIME = 2000
Q_MAX = 100
GEN_PROB = 0.15

RETRANS_PROB = 0.15
SPIKE_PROB = 0.1

# Message class
class Message:
    def __init__(self, arrival, criticality, hop):
        self.arrival = arrival
        self.criticality = criticality
        self.hop = hop

# Channel model
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

# Urgency function
def urgency(Tm, Cm, Sm):
    W1, W2, W3 = 0.5, 0.3, 0.2
    return W1*Tm + W2*Cm + W3*Sm

# Generate message
def generate_message(t):
    Cm = random.choice([1,2,3])
    hop = random.randint(1,7)
    return Message(t, Cm, hop)

def generate_dataset():
    queues = [deque() for _ in range(NUM_NODES)]
    channel_busy_until = 0

    data = []

    for t in range(SIM_TIME):

        # Message generation
        for i in range(NUM_NODES):
            if random.random() < GEN_PROB:
                if len(queues[i]) < Q_MAX:
                    queues[i].append(generate_message(t))

        # Scheduling
        if t >= channel_busy_until:

            all_msgs = []
            for q in queues:
                if len(q) > 0:
                    all_msgs.append(q[0])

            if len(all_msgs) == 0:
                continue

            # Compute urgency
            best_msg = None
            best_queue = None
            best_u = -1

            for q in queues:
                if len(q) == 0:
                    continue

                m = q[0]
                Tm = t - m.arrival
                Cm = m.criticality
                Sm = len(q)/Q_MAX

                u = urgency(Tm, Cm, Sm)

                if u > best_u:
                    best_u = u
                    best_msg = m
                    best_queue = q

            best_queue.popleft()

            # Transmission
            tx_time = transmission_delay(best_msg.hop)
            channel_busy_until = t + tx_time
            latency = channel_busy_until - best_msg.arrival

            data.append([
                Tm,
                Cm,
                Sm,
                best_msg.hop,
                latency
            ])

    df = pd.DataFrame(data, columns=[
        "Tm", "Cm", "Sm", "hop", "latency"
    ])

    # Label generation (P75 rule)
    threshold = np.percentile(df["latency"], 75)
    df["label"] = (df["latency"] > threshold).astype(int)

    return df

# Run dataset generation
df = generate_dataset()
print(df.head())
print("Dataset size:", len(df))
df.to_csv("dataset.csv", index=False)