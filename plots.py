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

# ==========================================
# Scientific Color Palette
# ==========================================

colors = [
    "#4E79A7",   # Blue
    "#F28E2B",   # Orange
    "#59A14F",   # Green
    "#E15759",   # Red
    "#B07AA1"    # Purple
]

# ==========================================
# Mean Latency Results
# ==========================================

results = {

    "Baseline":[288.71,211.14,160.13,96.03,88.91],

    "High Routine":[287.70,212.27,101.33,87.29,77.60],

    "Burst":[293.34,275.83,291.14,209.08,160.86],

    "SOS Intensive":[287.70,212.27,278.72,156.80,104.75],

    "Large Load":[293.34,275.83,291.14,209.08,160.86],

    "Packet Loss":[289.44,213.95,223.11,106.96,95.53]
}

# ==========================================
# Plot
# ==========================================

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(6.8,4.8))

    bars = ax.bar(
        schedulers,
        values,
        width=0.60,
        color=colors,
        edgecolor="black",
        linewidth=0.8
    )

    # Give space above bars
    ax.set_ylim(0, max(values)*1.18)

    # Value Labels
    offset = max(values)*0.02

    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x()+bar.get_width()/2,
            height+offset,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    ax.set_title(f"Mean Latency - {scenario}")

    ax.set_xlabel("Scheduler")

    ax.set_ylabel("Mean Latency (ms)")

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
        f"MeanLatency_{scenario}.pdf",
        bbox_inches="tight"
    )

    plt.show()

print("All Mean Latency graphs generated successfully.")
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

# ==========================================
# P75 Results
# ==========================================

results = {

    "Baseline":[306.16,275.99,219.43,112.22,92.90],

    "High Routine":[306.12,275.43,246.05,88.31,74.87],

    "Burst":[307.37,300.25,306.84,270.62,231.89],

    "SOS Intensive":[306.12,275.43,304.75,225.07,129.16],

    "Large Load":[307.37,300.25,306.84,270.62,231.89],

    "Packet Loss":[306.87,278.10,289.88,137.40,105.20]
}

# ==========================================
# Plot
# ==========================================

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(6.8,4.8))

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

    # Give space for labels
    ax.set_ylim(0, max(values) * 1.18)

    offset = max(values) * 0.02

    # Value Labels
    for i, value in enumerate(values):

        ax.text(
            i,
            value + offset,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    ax.set_title(f"P75 Latency - {scenario}")

    ax.set_xlabel("Scheduler")

    ax.set_ylabel("P75 Latency (ms)")

    ax.grid(
        linestyle=":",
        linewidth=0.8,
        alpha=0.45
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)

    plt.savefig(
        f"P75Latency_{scenario}.pdf",
        bbox_inches="tight"
    )

    plt.show()

print("All P75 Latency graphs generated successfully.")
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

# ==========================================
# Scientific Color Palette
# ==========================================

colors = [
    "#4E79A7",
    "#F28E2B",
    "#59A14F",
    "#E15759",
    "#B07AA1"
]

# ==========================================
# Jitter Results
# ==========================================

results = {

    "Baseline":[53.08,78.47,79.02,59.19,56.23],

    "High Routine":[55.57,77.74,120.97,61.52,53.38],

    "Burst":[49.03,49.68,51.35,74.14,81.79],

    "SOS Intensive":[55.57,77.74,63.61,79.83,63.31],

    "Large Load":[49.03,49.68,51.35,74.14,81.79],

    "Packet Loss":[53.58,78.79,87.88,65.97,59.49]
}

# ==========================================
# Plot
# ==========================================

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(6.8,4.8))

    bars = ax.barh(
        schedulers,
        values,
        height=0.55,
        color=colors,
        edgecolor="black",
        linewidth=0.8
    )

    ax.set_xlim(0, max(values) * 1.20)

    offset = max(values) * 0.02

    # Value Labels
    for bar in bars:

        width = bar.get_width()

        ax.text(
            width + offset,
            bar.get_y() + bar.get_height()/2,
            f"{width:.1f}",
            va="center",
            ha="left",
            fontsize=9
        )

    ax.set_title(f"Jitter - {scenario}")

    ax.set_xlabel("Jitter (ms)")

    ax.set_ylabel("Scheduler")

    ax.grid(
        axis="x",
        linestyle=":",
        linewidth=0.8,
        alpha=0.45
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout(pad=1.8)

    plt.savefig(
        f"Jitter_{scenario}.pdf", 
        bbox_inches="tight"
    )

    plt.show()

print("All Jitter graphs generated successfully.")
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

# ==========================================
# Pastel Scientific Palette
# ==========================================

colors = [
    "#8FBCE6",   # FIFO
    "#F6B47B",   # RR
    "#8FD19E",   # FPS
    "#F29A94",   # ResQMesh
    "#C7AEDB"    # ML-ResQMesh
]

# ==========================================
# Delivery Ratio Results
# ==========================================

results = {

    "Baseline":[0.307,0.307,0.307,0.305,0.294],

    "High Routine":[0.306,0.304,0.301,0.306,0.285],

    "Burst":[0.062,0.062,0.062,0.061,0.046],

    "SOS Intensive":[0.306,0.304,0.306,0.305,0.232],

    "Large Load":[0.062,0.062,0.062,0.061,0.046],

    "Packet Loss":[0.280,0.282,0.279,0.281,0.263]
}

# ==========================================
# Plot
# ==========================================

for scenario, values in results.items():

    fig, ax = plt.subplots(figsize=(6.8,4.8))

    bars = ax.bar(
        schedulers,
        values,
        width=0.45,
        color=colors,
        edgecolor="black",
        linewidth=0.8,
        alpha=0.90
    )

    # Honest axis
    ax.set_ylim(0, max(values)*1.18)

    offset = max(values)*0.02

    # Value Labels
    for bar in bars:

        height = bar.get_height()

        ax.text(
            bar.get_x()+bar.get_width()/2,
            height+offset,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    ax.set_title(f"Delivery Ratio - {scenario}")

    ax.set_xlabel("Scheduler")

    ax.set_ylabel("Delivery Ratio")

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
        f"DeliveryRatio_{scenario}.pdf",
        bbox_inches="tight"
    )

    plt.show()

print("All Delivery Ratio graphs generated successfully.")