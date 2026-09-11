import json
import matplotlib.pyplot as plt

# ==========================================
# Publication Style (matches existing plots.py)
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
# Scheduler Labels (all six schedulers, including the QLEARN baseline)
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

colors = [
    "#4E79A7",   # Blue
    "#F28E2B",   # Orange
    "#59A14F",   # Green
    "#E15759",   # Red
    "#B07AA1",   # Purple
    "#76B7B2"    # Teal (QLEARN)
]

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

results = {}
for scenario_key, display_name in scenario_labels.items():
    values = [
        data[scenario_key][sch]["mean_energy_mJ"]
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

    ax.set_ylim(0, max(values) * 1.18)

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
    ax.tick_params(axis='x', labelrotation=15)

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

    pass

print("All Energy graphs generated successfully from full_evaluation_results.json.")