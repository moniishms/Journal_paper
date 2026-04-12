import matplotlib.pyplot as plt
import numpy as np

schedulers = ["FIFO", "RR", "ResQMesh", "ML-ResQMesh"]

# All scenario results
results = {
    "Baseline": {
        "mean_latency":   [288.71, 211.14, 96.03,  86.74],
        "p75_latency":    [306.16, 275.99, 112.22, 91.87],
        "jitter":         [53.08,  78.47,  59.19,  57.59],
        "delivery_ratio": [0.307,  0.307,  0.305,  0.293],
    },
    "High Routine": {
        "mean_latency":   [287.70, 212.27, 87.29,  72.92],
        "p75_latency":    [306.12, 275.43, 88.31,  70.37],
        "jitter":         [55.57,  77.74,  61.52,  54.66],
        "delivery_ratio": [0.306,  0.304,  0.306,  0.278],
    },
    "Burst": {
        "mean_latency":   [293.34, 275.83, 209.08, 159.98],
        "p75_latency":    [307.37, 300.25, 270.62, 233.06],
        "jitter":         [49.03,  49.68,  74.14,  82.30],
        "delivery_ratio": [0.062,  0.062,  0.061,  0.046],
    },
    "SOS Intensive": {
        "mean_latency":   [287.70, 212.27, 156.80, 105.32],
        "p75_latency":    [306.12, 275.43, 225.07, 128.70],
        "jitter":         [55.57,  77.74,  79.83,  65.70],
        "delivery_ratio": [0.306,  0.304,  0.305,  0.229],
    },
    "Large Load": {
        "mean_latency":   [293.34, 275.83, 209.08, 159.98],
        "p75_latency":    [307.37, 300.25, 270.62, 233.06],
        "jitter":         [49.03,  49.68,  74.14,  82.30],
        "delivery_ratio": [0.062,  0.062,  0.061,  0.046],
    },
    "Packet Loss": {
        "mean_latency":   [289.44, 213.95, 106.96, 91.81],
        "p75_latency":    [306.87, 278.10, 137.40, 99.98],
        "jitter":         [53.58,  78.79,  65.97,  60.17],
        "delivery_ratio": [0.280,  0.282,  0.281,  0.261],
    },
}

metrics = {
    "mean_latency":   "Mean Latency",
    "p75_latency":    "P75 Latency",
    "jitter":         "Jitter",
    "delivery_ratio": "Delivery Ratio",
}

x = np.arange(len(schedulers))
width = 0.13
scenario_list = list(results.keys())
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", 
          "#d62728", "#9467bd", "#8c564b"]

for metric_key, metric_label in metrics.items():
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, scenario in enumerate(scenario_list):
        values = results[scenario][metric_key]
        ax.bar(x + i * width, values, width, 
               label=scenario, color=colors[i])

    ax.set_title(f"{metric_label} Comparison Across Scenarios")
    ax.set_xlabel("Scheduler")
    ax.set_ylabel(metric_label)
    ax.set_xticks(x + width * (len(scenario_list) - 1) / 2)
    ax.set_xticklabels(schedulers)
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{metric_key}.png", dpi=300)
    plt.show()

print("All graphs saved.")