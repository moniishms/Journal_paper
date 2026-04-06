import matplotlib.pyplot as plt

# Scheduler names
schedulers = ["FIFO", "RR", "ResQMesh", "ML-ResQMesh"]

# Results from your simulation
mean_latency = [287.68, 210.92, 93.90, 85.87]
p75_latency = [306.05, 275.27, 106.86, 91.03]
jitter = [54.91, 78.39, 58.35, 57.56]
delivery_ratio = [0.308, 0.309, 0.305, 0.297]

# -------------------------
# Mean Latency Bar Graph
# -------------------------
plt.figure()
plt.bar(schedulers, mean_latency)
plt.title("Mean Latency Comparison")
plt.xlabel("Scheduler")
plt.ylabel("Mean Latency")
plt.show()

# -------------------------
# P75 Latency Bar Graph
# -------------------------
plt.figure()
plt.bar(schedulers, p75_latency)
plt.title("P75 Latency Comparison")
plt.xlabel("Scheduler")
plt.ylabel("P75 Latency")
plt.show()

# -------------------------
# Jitter Bar Graph
# -------------------------
plt.figure()
plt.bar(schedulers, jitter)
plt.title("Jitter Comparison")
plt.xlabel("Scheduler")
plt.ylabel("Jitter")
plt.show()

# -------------------------
# Delivery Ratio Bar Graph
# -------------------------
plt.figure()
plt.bar(schedulers, delivery_ratio)
plt.title("Delivery Ratio Comparison")
plt.xlabel("Scheduler")
plt.ylabel("Delivery Ratio")
plt.show()