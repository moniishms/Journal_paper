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
    "xtick.labelsize": 11,
    "ytick.labelsize": 11
})

# ==========================================
# Scheduler Labels
# ==========================================

schedulers = [
    "FIFO",
    "RR",
    "FPS",
    "ResQMesh",
    "ML-ResQMesh"
]

scheduler_keys = ["FIFO", "RR", "FPS", "RESQ", "ML_RESQ"]

# ==========================================
# Scientific Color Palette (same as Mean Latency plots)
# ==========================================

colors = [
    "#4E79A7",   # Blue
    "#F28E2B",   # Orange
    "#59A14F",   # Green
    "#E15759",   # Red
    "#B07AA1"    # Purple
]

# ==========================================
# Scenario label mapping (json key -> display name)
# ==========================================

scenario_labels = {
    "baseline": "Baseline",
    "high_routine": "High Routine",
    "burst": "Burst",
    "sos_intensive": "SOS Intensive",
    "large_load": "Large Load",
    "packet_loss": "Packet Loss"
}

# ==========================================
# Load Energy Results
# ==========================================

with open("energy_results.json", "r") as f:
    energy_data = json.load(f)

results = {}
for scenario_key, display_name in scenario_labels.items():
    values = [
        energy_data[scenario_key][sch]["mean_energy_mJ"]
        for sch in scheduler_keys
    ]
    results[display_name] = values

# ==========================================
# Plot
# ==========================================

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(6.8, 4.8))

    bars = ax.bar(
        schedulers,
        values,
        width=0.60,
        color=colors,
        edgecolor="black",
        linewidth=0.8
    )

    # Give space above bars
    ax.set_ylim(0, max(values) * 1.18)

    # Value Labels
    offset = max(values) * 0.02

    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    ax.set_title(f"Mean Energy per Message - {scenario}")

    ax.set_xlabel("Scheduler")

    ax.set_ylabel("Mean Energy per Message (mJ)")

    ax.grid(
        axis="y",
        linestyle=":",
        linewidth=0.8,
        alpha=0.45
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)

    plt.savefig(
        f"Energy_{scenario}.pdf",
        bbox_inches="tight"
    )

    plt.show()

print("All Energy Consumption graphs generated successfully.")