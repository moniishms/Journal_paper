import json
import numpy as np
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
    "ytick.labelsize": 11,
    "legend.fontsize": 9.5,
})

scenario_labels = {
    "baseline": "Baseline",
    "high_routine": "High\nRoutine",
    "burst": "Burst",
    "sos_intensive": "SOS\nIntensive",
    "large_load": "Large\nLoad",
    "packet_loss": "Packet\nLoss"
}

# Only the two schedulers this comparison is about, matching the section
# title ("Comparison with a Learning-Based Baseline"). FIFO/RR/FPS/
# ML-ResQMesh's criticality values are still reported -- in the
# mean_delivered_criticality column added to Table overall_results --
# just not duplicated in this figure.
schedulers = ["ResQMesh", "QLEARN"]
scheduler_keys = ["RESQ", "QLEARN"]

colors = [
    "#E15759",   # ResQMesh
    "#76B7B2"    # QLEARN
]

# The true no-preference baseline per scenario, derived from each
# scenario's actual criticality-sampling pool (Section V-B / Table
# traffic_modes), rather than a single flat value assumed for all six.
pool_means = {
    "baseline": 2.0,
    "high_routine": 1.6,
    "burst": 2.0,
    "sos_intensive": 2.4,
    "large_load": 2.0,
    "packet_loss": 2.0,
}

with open("full_evaluation_results.json", "r") as f:
    data = json.load(f)

x_labels = list(scenario_labels.values())
x = np.arange(len(x_labels))
n_sched = len(schedulers)
width = 0.32

fig, ax = plt.subplots(figsize=(8.0, 5.0))

for idx, (sched_label, sched_key, color) in enumerate(zip(schedulers, scheduler_keys, colors)):
    vals = [data[s][sched_key]["mean_delivered_criticality"] for s in scenario_labels]
    offset = (idx - (n_sched - 1) / 2) * width
    bars = ax.bar(
        x + offset, vals, width,
        label=sched_label,
        color=color,
        edgecolor="black",
        linewidth=0.6
    )
    for xi, v in zip(x + offset, vals):
        ax.text(xi, v + 0.07, f"{v:.2f}", ha="center", va="bottom", fontsize=8.5,
                 bbox=dict(boxstyle="round,pad=0.1", facecolor="white",
                            edgecolor="none", alpha=0.75))

# One short dashed segment per scenario, at that scenario's own pool
# mean, instead of a single line at a flat 2.0 across the whole figure.
# Segment spans the width of that scenario's bar group.
half_span = width + width / 2
for xi, (scenario_key, pm) in zip(x, pool_means.items()):
    ax.hlines(
        y=pm, xmin=xi - half_span, xmax=xi + half_span,
        color="black", linestyle="--", linewidth=1.1, alpha=0.75
    )

ax.text(
    0.01, 0.97,
    "Dashed segments: each scenario's own no-preference baseline\n"
    "(mean $C_m$ of its criticality-generation pool; 1.6 / 2.0 / 2.4)",
    fontsize=8.5, style="italic", ha="left", va="top",
    transform=ax.transAxes
)

ax.set_ylim(0, 3.6)
ax.set_ylabel("Mean Criticality of Delivered Messages ($C_m$)")
ax.set_xlabel("Scenario")
ax.set_title("ResQMesh vs. QLEARN: Delivered-Message Criticality")
ax.set_xticks(x)
ax.set_xticklabels(x_labels)

ax.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.45)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(loc="upper right", frameon=False, ncol=2, columnspacing=1.2)

plt.tight_layout(pad=1.8)
plt.savefig("Criticality_ResQMesh_vs_QLEARN.pdf", bbox_inches="tight")
plt.show()

print("ResQMesh vs QLEARN criticality comparison plot generated successfully.")