import json
import matplotlib.pyplot as plt

# ==========================================
# Publication Style
# ==========================================

plt.style.use("default")

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 11
})

# ==========================================
# Scheduler Labels (all six, including the QLEARN baseline)
# ==========================================

schedulers = [
    "FIFO",
    "RR",
    "FPS",
    "ResQMesh",
    "ML-ResQMesh",
    "QLEARN"
]

scheduler_keys = ["FIFO", "RR", "FPS", "RESQ", "ML_RESQ", "QLEARN"]

scenario_labels = {
    "baseline": "Baseline",
    "high_routine": "High Routine",
    "burst": "Burst",
    "sos_intensive": "SOS Intensive",
    "large_load": "Large Load",
    "packet_loss": "Packet Loss"
}

# ==========================================
# Load results from full_evaluation.py output
# ==========================================

with open("full_evaluation_results.json", "r") as f:
    data = json.load(f)


def get_metric(metric_key):
    """Return {display_scenario_name: [values per scheduler]} for a metric."""
    out = {}
    for scenario_key, display_name in scenario_labels.items():
        out[display_name] = [
            data[scenario_key][sch][metric_key] for sch in scheduler_keys
        ]
    return out


# ==========================================
# 1. Mean Latency -- vertical bar chart
# ==========================================

colors_latency = [
    "#4E79A7", "#F28E2B", "#59A14F", "#E15759", "#B07AA1", "#76B7B2"
]

results = get_metric("mean_latency")

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(7.2, 4.8))

    bars = ax.bar(
        schedulers,
        values,
        width=0.60,
        color=colors_latency,
        edgecolor="black",
        linewidth=0.8
    )

    ax.set_ylim(0, max(values) * 1.18)
    offset = max(values) * 0.02

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"{height:.1f}",
            ha="center", va="bottom", fontsize=9
        )

    ax.set_title(f"Mean Latency - {scenario}")
    ax.set_xlabel("Scheduler")
    ax.set_ylabel("Mean Latency (ms)")
    ax.tick_params(axis='x', labelrotation=12)

    ax.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.45)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)
    plt.savefig(f"MeanLatency_{scenario}.pdf", bbox_inches="tight")
    pass

print("All Mean Latency graphs generated successfully.")

# ==========================================
# 2. P75 Latency -- line chart
# ==========================================

results = get_metric("p75_latency")

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(7.2, 4.8))

    ax.plot(
        schedulers,
        values,
        color="#4E79A7",
        linewidth=2.8,
        marker="o",
        markersize=8,
        markerfacecolor="white",
        markeredgecolor="#4E79A7",
        markeredgewidth=2.2
    )

    ax.set_ylim(0, max(values) * 1.18)
    offset = max(values) * 0.02

    for i, value in enumerate(values):
        ax.text(
            i, value + offset, f"{value:.1f}",
            ha="center", va="bottom", fontsize=9
        )

    ax.set_title(f"P75 Latency - {scenario}")
    ax.set_xlabel("Scheduler")
    ax.set_ylabel("P75 Latency (ms)")
    ax.tick_params(axis='x', labelrotation=12)

    ax.grid(linestyle=":", linewidth=0.8, alpha=0.45)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)
    plt.savefig(f"P75Latency_{scenario}.pdf", bbox_inches="tight")
    pass

print("All P75 Latency graphs generated successfully.")

# ==========================================
# 3. Jitter -- horizontal bar chart
# ==========================================

colors_jitter = [
    "#4E79A7", "#F28E2B", "#59A14F", "#E15759", "#B07AA1", "#76B7B2"
]

results = get_metric("jitter")

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(7.2, 4.8))

    bars = ax.barh(
        schedulers,
        values,
        height=0.55,
        color=colors_jitter,
        edgecolor="black",
        linewidth=0.8
    )

    ax.set_xlim(0, max(values) * 1.20)
    offset = max(values) * 0.02

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}",
            va="center", ha="left", fontsize=9
        )

    ax.set_title(f"Jitter - {scenario}")
    ax.set_xlabel("Jitter (ms)")
    ax.set_ylabel("Scheduler")

    ax.grid(axis="x", linestyle=":", linewidth=0.8, alpha=0.45)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)
    plt.savefig(f"Jitter_{scenario}.pdf", bbox_inches="tight")
    pass

print("All Jitter graphs generated successfully.")

# ==========================================
# 4. Delivery Ratio -- pastel vertical bar chart
# ==========================================

colors_delivery = [
    "#8FBCE6", "#F6B47B", "#8FD19E", "#F29A94", "#C7AEDB", "#9FD8D3"
]

results = get_metric("delivery_ratio")

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(7.2, 4.8))

    bars = ax.bar(
        schedulers,
        values,
        width=0.45,
        color=colors_delivery,
        edgecolor="black",
        linewidth=0.8,
        alpha=0.90
    )

    ax.set_ylim(0, max(values) * 1.18)
    offset = max(values) * 0.02

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"{height:.3f}",
            ha="center", va="bottom", fontsize=9
        )

    ax.set_title(f"Delivery Ratio - {scenario}")
    ax.set_xlabel("Scheduler")
    ax.set_ylabel("Delivery Ratio")
    ax.tick_params(axis='x', labelrotation=12)

    ax.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.45)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)
    plt.savefig(f"DeliveryRatio_{scenario}.pdf", bbox_inches="tight")
    pass

print("All Delivery Ratio graphs generated successfully.")