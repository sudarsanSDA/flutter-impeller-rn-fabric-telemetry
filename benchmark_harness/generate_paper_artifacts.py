"""Statistical synthesis and publication-quality figure generation for multi-tier cross-platform benchmark paper."""

import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure publication-grade styling adhering to Springer Nature guidelines
plt.style.use('seaborn-v0_8-paper' if 'seaborn-v0_8-paper' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Computer Modern Roman'],
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9.5,
    'figure.titlesize': 13,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BENCH_DIR = SCRIPT_DIR
RESULTS_TIER1 = os.path.join(BENCH_DIR, "benchmark_results.csv")
LATENCIES_TIER1 = os.path.join(BENCH_DIR, "frame_latencies.csv")
RESULTS_TIER2 = os.path.join(BENCH_DIR, "benchmark_results_poco.csv")
LATENCIES_TIER2 = os.path.join(BENCH_DIR, "frame_latencies_poco.csv")

OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "paper_artifacts", "figures")
TABLES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "paper_artifacts", "tables")
MANUSCRIPT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "manuscript")
MANUSCRIPT_FIG_DIR = os.path.join(MANUSCRIPT_DIR, "figures")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(MANUSCRIPT_FIG_DIR, exist_ok=True)


def load_multi_tier_data():
    """Loads benchmark results and frametimes for Tier-1 and Tier-2."""
    df_res1 = pd.read_csv(RESULTS_TIER1)
    df_res1["tier"] = "Tier-1 (SD 720G @ 60Hz)"
    df_res1["device"] = "Redmi Note 9 Pro"

    df_lat1 = pd.read_csv(LATENCIES_TIER1)
    df_lat1["tier"] = "Tier-1 (SD 720G @ 60Hz)"
    df_lat1["device"] = "Redmi Note 9 Pro"

    df_res2 = pd.read_csv(RESULTS_TIER2)
    df_res2["tier"] = "Tier-2 (Dimensity 8300U @ 120Hz)"
    df_res2["device"] = "POCO X6 Pro 5G"

    df_lat2 = pd.read_csv(LATENCIES_TIER2)
    df_lat2["tier"] = "Tier-2 (Dimensity 8300U @ 120Hz)"
    df_lat2["device"] = "POCO X6 Pro 5G"

    combined_res = pd.concat([df_res1, df_res2], ignore_index=True)
    combined_lat = pd.concat([df_lat1, df_lat2], ignore_index=True)
    return combined_res, combined_lat, df_res1, df_lat1, df_res2, df_lat2


def compute_statistics(combined_res, combined_lat):
    """Computes academic descriptive statistics across tiers."""
    print("\n=======================================================")
    print("ACADEMIC DESCRIPTIVE STATISTICS (MULTI-TIER SYNTHESIS)")
    print("=======================================================")

    # 1. Cold Startup Latency
    startup_df = combined_res[combined_res["test_name"] == "cold_startup"]
    startup_stats = startup_df.groupby(["tier", "framework"])["metric_value"].agg(
        Mean="mean", Std="std", Min="min", Median="median", Max="max"
    ).reset_index()
    print("\n[1. COLD STARTUP LATENCY (ms)]")
    print(startup_stats.to_string(index=False))

    # 2. Memory Footprint
    print("\n[2. MEMORY PROFILES (PSS in kB)]")
    mem_df = combined_res[combined_res["test_name"].str.startswith("memory_")].copy()
    mem_pivoted = mem_df.pivot_table(
        index=["tier", "framework", "test_name"],
        columns="metric_name",
        values="metric_value"
    ).reset_index()
    mem_pivoted["native_mb"] = (mem_pivoted["native_heap_pss"] / 1024.0).round(2)
    mem_pivoted["dalvik_mb"] = (mem_pivoted["dalvik_heap_pss"] / 1024.0).round(2)
    mem_pivoted["total_mb"] = (mem_pivoted["total_pss"] / 1024.0).round(2)
    print(mem_pivoted[["tier", "framework", "test_name", "native_mb", "dalvik_mb", "total_mb"]].to_string(index=False))

    # 3. Frametime Summary
    print("\n[3. FRAME LATENCY SUMMARY (ms)]")
    def calc_jank(grp):
        tier_name = grp.name[0] if hasattr(grp, "name") else ""
        threshold = 8.333 if "Tier-2" in str(tier_name) else 16.666
        return (grp["duration_ms"] > threshold).sum()

    def calc_jank_pct(grp):
        tier_name = grp.name[0] if hasattr(grp, "name") else ""
        threshold = 8.333 if "Tier-2" in str(tier_name) else 16.666
        return ((grp["duration_ms"] > threshold).sum() / len(grp)) * 100.0 if len(grp) > 0 else 0.0

    lat_stats = combined_lat.groupby(["tier", "framework", "workload"]).apply(
        lambda grp: pd.Series({
            "Count": len(grp),
            "Mean": round(grp["duration_ms"].mean(), 2),
            "Std": round(grp["duration_ms"].std(), 2),
            "p50": round(grp["duration_ms"].median(), 2),
            "p95": round(np.percentile(grp["duration_ms"], 95), 2),
            "Max": round(grp["duration_ms"].max(), 2),
            "Janky_Count": calc_jank(grp),
            "Jank_Pct": round(calc_jank_pct(grp), 1)
        }),
        include_groups=False
    ).reset_index()
    print(lat_stats.to_string(index=False))

    # Save to Markdown
    with open(os.path.join(TABLES_DIR, "descriptive_statistics.md"), "w", encoding="utf-8") as f:
        f.write("# Descriptive Empirical Statistics (Multi-Tier Evaluation)\n\n")
        f.write("## 1. Cold Startup Latency (ms)\n\n")
        f.write(startup_stats.to_markdown(index=False) + "\n\n")
        f.write("## 2. Memory Footprint (PSS in MB)\n\n")
        f.write(mem_pivoted[["tier", "framework", "test_name", "native_mb", "dalvik_mb", "total_mb"]].to_markdown(index=False) + "\n\n")
        f.write("## 3. Frame Latency & Jank Distribution (ms)\n\n")
        f.write(lat_stats.to_markdown(index=False) + "\n")

    return startup_stats, mem_pivoted, lat_stats


def save_figure_multi_format(fig, base_name):
    """Saves figure to artifacts and manuscript directories as vector PDF and 300+ DPI PNG."""
    png_name = f"{base_name}.png"
    pdf_name = f"{base_name}.pdf"

    for d in (OUTPUT_DIR, MANUSCRIPT_FIG_DIR, MANUSCRIPT_DIR):
        fig.savefig(os.path.join(d, png_name))
        fig.savefig(os.path.join(d, pdf_name))
    print(f"Exported: {base_name} (.png and .pdf) to artifacts and manuscript directories.")


def generate_figure1_dual_tier(combined_lat):
    """Figure 1: Subdivided boxplot showing frametime distributions across Tier-1 and Tier-2."""
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=False)

    tier1_df = combined_lat[combined_lat["tier"].str.contains("Tier-1")].copy()
    tier2_df = combined_lat[combined_lat["tier"].str.contains("Tier-2")].copy()

    for df in (tier1_df, tier2_df):
        df["Framework"] = df["framework"].map({
            "flutter": "Flutter (Impeller)",
            "react_native": "React Native (Fabric)"
        })
        df["Workload"] = df["workload"].map({
            "workload_a": "Workload A (List)",
            "workload_c": "Workload C (Canvas)"
        })

    palette = {"Flutter (Impeller)": "#02569B", "React Native (Fabric)": "#61DAFB"}

    # Subplot 1: Tier-1 (60 Hz)
    ax1 = axes[0]
    sns.boxplot(
        data=tier1_df,
        x="Workload",
        y="duration_ms",
        hue="Framework",
        palette=palette,
        ax=ax1,
        width=0.52,
        fliersize=3,
        linewidth=1.1,
        boxprops=dict(alpha=0.85)
    )
    ax1.axhline(16.666, color="#DC2626", linestyle="--", linewidth=1.5, label="60 Hz Target (16.67 ms)")
    ax1.set_title("(a) Tier-1: Snapdragon 720G (60 Hz Budget)")
    ax1.set_ylabel("Frame Rendering Latency (ms)")
    ax1.set_xlabel("")
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)
    ax1.set_ylim(5, 55)

    # Subplot 2: Tier-2 (120 Hz)
    ax2 = axes[1]
    sns.boxplot(
        data=tier2_df,
        x="Workload",
        y="duration_ms",
        hue="Framework",
        palette=palette,
        ax=ax2,
        width=0.52,
        fliersize=3,
        linewidth=1.1,
        boxprops=dict(alpha=0.85)
    )
    ax2.axhline(8.333, color="#2563EB", linestyle="--", linewidth=1.5, label="120 Hz Target (8.33 ms)")
    ax2.set_title("(b) Tier-2: Dimensity 8300-Ultra (120 Hz Budget)")
    ax2.set_ylabel("Frame Rendering Latency (ms)")
    ax2.set_xlabel("")
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    ax2.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)
    ax2.set_ylim(5, 32)

    fig.tight_layout()
    save_figure_multi_format(fig, "figure1_frametime_distribution")
    plt.close(fig)


def generate_figure2_dual_tier(combined_res):
    """Figure 2: Grouped bar chart comparing Cold Startup Latency across Tier-1 and Tier-2."""
    startup_df = combined_res[combined_res["test_name"] == "cold_startup"].copy()

    summary = startup_df.groupby(["tier", "framework"])["metric_value"].agg(["mean", "std"]).reset_index()

    tier_labels = ["Tier-1 (SD 720G)", "Tier-2 (Dimensity 8300U)"]
    frameworks = ["flutter", "react_native"]

    fig, ax = plt.subplots(figsize=(7.5, 4.6))

    x = np.arange(len(tier_labels))
    width = 0.32

    fl_means = [
        summary[(summary["tier"].str.contains("Tier-1")) & (summary["framework"] == "flutter")]["mean"].values[0],
        summary[(summary["tier"].str.contains("Tier-2")) & (summary["framework"] == "flutter")]["mean"].values[0],
    ]
    fl_stds = [
        summary[(summary["tier"].str.contains("Tier-1")) & (summary["framework"] == "flutter")]["std"].values[0],
        summary[(summary["tier"].str.contains("Tier-2")) & (summary["framework"] == "flutter")]["std"].values[0],
    ]

    rn_means = [
        summary[(summary["tier"].str.contains("Tier-1")) & (summary["framework"] == "react_native")]["mean"].values[0],
        summary[(summary["tier"].str.contains("Tier-2")) & (summary["framework"] == "react_native")]["mean"].values[0],
    ]
    rn_stds = [
        summary[(summary["tier"].str.contains("Tier-1")) & (summary["framework"] == "react_native")]["std"].values[0],
        summary[(summary["tier"].str.contains("Tier-2")) & (summary["framework"] == "react_native")]["std"].values[0],
    ]

    bars_fl = ax.bar(
        x - width / 2, fl_means, width, yerr=fl_stds, capsize=5,
        label="Flutter 3.24 (Impeller)", color="#02569B", edgecolor="#1F2937", linewidth=1.1, alpha=0.9
    )
    bars_rn = ax.bar(
        x + width / 2, rn_means, width, yerr=rn_stds, capsize=5,
        label="React Native 0.76 (Fabric + Hermes)", color="#087EA4", edgecolor="#1F2937", linewidth=1.1, alpha=0.9
    )

    for bar, m, s in zip(bars_fl, fl_means, fl_stds):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0, m + s + 10,
            f"{m:.0f}±{s:.0f} ms", ha="center", va="bottom", fontsize=9, fontweight="bold"
        )

    for bar, m, s in zip(bars_rn, rn_means, rn_stds):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0, m + s + 10,
            f"{m:.0f}±{s:.0f} ms", ha="center", va="bottom", fontsize=9, fontweight="bold"
        )

    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels, fontsize=10.5, fontweight="bold")
    ax.set_ylabel("Cold Startup Latency (ms)")
    ax.set_title("Cold Startup Execution Latency Across Hardware Tiers")
    ax.set_ylim(0, 680)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.9)

    fig.tight_layout()
    save_figure_multi_format(fig, "figure2_cold_startup")
    plt.close(fig)


def generate_figure3_dual_tier(combined_res):
    """Figure 3: Stacked bar chart showing RAM distribution across Idle, Scroll, and Post-Compute for both tiers."""
    mem_df = combined_res[combined_res["test_name"].str.startswith("memory_")].copy()

    state_map = {
        "memory_idle": "1. Idle",
        "memory_workload_a_scroll": "2. Scroll",
        "memory_workload_b_post_compute": "3. Compute"
    }
    mem_df["state"] = mem_df["test_name"].map(state_map)

    pivoted = mem_df.pivot_table(
        index=["tier", "framework", "state"],
        columns="metric_name",
        values="metric_value"
    ).reset_index()

    pivoted["native_mb"] = pivoted["native_heap_pss"] / 1024.0
    pivoted["dalvik_mb"] = pivoted["dalvik_heap_pss"] / 1024.0
    pivoted["other_mb"] = (pivoted["total_pss"] - pivoted["native_heap_pss"] - pivoted["dalvik_heap_pss"]) / 1024.0

    states = ["1. Idle", "2. Scroll", "3. Compute"]

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.8), sharey=True)

    c_native = "#2563EB"
    c_dalvik = "#F59E0B"
    c_other = "#9CA3AF"

    for idx, (tier_key, title) in enumerate([
        ("Tier-1", "(a) Tier-1: Snapdragon 720G (4 GB RAM)"),
        ("Tier-2", "(b) Tier-2: Dimensity 8300-Ultra (8 GB RAM)")
    ]):
        ax = axes[idx]
        sub = pivoted[pivoted["tier"].str.contains(tier_key)]
        fl_data = sub[sub["framework"] == "flutter"].set_index("state").reindex(states).fillna(0)
        rn_data = sub[sub["framework"] == "react_native"].set_index("state").reindex(states).fillna(0)

        x = np.arange(len(states))
        width = 0.35

        # Flutter stacked bars
        ax.bar(x - width / 2, fl_data["native_mb"], width, label="Native Heap" if idx == 0 else "", color=c_native, edgecolor="#1E293B", alpha=0.9)
        ax.bar(x - width / 2, fl_data["dalvik_mb"], width, bottom=fl_data["native_mb"], label="Dalvik/Hermes Heap" if idx == 0 else "", color=c_dalvik, edgecolor="#1E293B", alpha=0.9)
        ax.bar(x - width / 2, fl_data["other_mb"], width, bottom=fl_data["native_mb"] + fl_data["dalvik_mb"], label="Other PSS (EGL/Graphics/So Mmap)" if idx == 0 else "", color=c_other, edgecolor="#1E293B", alpha=0.8)

        # React Native stacked bars
        ax.bar(x + width / 2, rn_data["native_mb"], width, color=c_native, edgecolor="#1E293B", alpha=0.9)
        ax.bar(x + width / 2, rn_data["dalvik_mb"], width, bottom=rn_data["native_mb"], color=c_dalvik, edgecolor="#1E293B", alpha=0.9)
        ax.bar(x + width / 2, rn_data["other_mb"], width, bottom=rn_data["native_mb"] + rn_data["dalvik_mb"], color=c_other, edgecolor="#1E293B", alpha=0.8)

        for i in x:
            fl_tot = fl_data.loc[states[i], "native_mb"] + fl_data.loc[states[i], "dalvik_mb"] + fl_data.loc[states[i], "other_mb"]
            rn_tot = rn_data.loc[states[i], "native_mb"] + rn_data.loc[states[i], "dalvik_mb"] + rn_data.loc[states[i], "other_mb"]
            ax.text(i - width / 2, fl_tot + 4, f"{fl_tot:.0f}M\n(Fl)", ha="center", va="bottom", fontsize=8.0)
            ax.text(i + width / 2, rn_tot + 4, f"{rn_tot:.0f}M\n(RN)", ha="center", va="bottom", fontsize=8.0)

        ax.set_xticks(x)
        ax.set_xticklabels(states, fontweight="bold")
        ax.set_title(title)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        if idx == 0:
            ax.set_ylabel("Memory Consumption PSS (MB)")
            ax.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

    axes[0].set_ylim(0, 290)
    fig.tight_layout()
    save_figure_multi_format(fig, "figure3_ram_distribution")
    plt.close(fig)


def generate_figure4_binary_size():
    """Figure 4: Exact single-ABI binary size comparison (arm64-v8a) with accurate percentage annotations."""
    fig, ax = plt.subplots(figsize=(5.6, 4.2))

    frameworks = ["Flutter 3.24\n(Impeller)", "React Native 0.76\n(Fabric + Hermes)"]
    sizes_mb = [7.42, 13.83]
    colors = ["#02569B", "#087EA4"]

    bars = ax.bar(frameworks, sizes_mb, color=colors, width=0.45, edgecolor="#1F2937", linewidth=1.1, alpha=0.9)

    # Annotate values and accurate relative percentages
    ax.text(
        bars[0].get_x() + bars[0].get_width() / 2.0,
        7.42 + 0.4,
        "7.42 MB\n(-46.3% smaller)",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight="bold"
    )

    ax.text(
        bars[1].get_x() + bars[1].get_width() / 2.0,
        13.83 + 0.4,
        "13.83 MB\n(+86.4% overhead)",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight="bold"
    )

    ax.set_ylabel("Release APK Binary Size (MB)")
    ax.set_title("Release Binary Footprint (Single-ABI: arm64-v8a)")
    ax.set_ylim(0, 18.5)
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    fig.tight_layout()
    save_figure_multi_format(fig, "figure4_binary_size")
    plt.close(fig)


def main():
    combined_res, combined_lat, df_res1, df_lat1, df_res2, df_lat2 = load_multi_tier_data()
    compute_statistics(combined_res, combined_lat)
    generate_figure1_dual_tier(combined_lat)
    generate_figure2_dual_tier(combined_res)
    generate_figure3_dual_tier(combined_res)
    generate_figure4_binary_size()

    # Save companion aliases matching paper layout strictly
    mapping = [
        ('figure2_cold_startup', 'fig1_startup'),
        ('figure3_ram_distribution', 'fig2_memory'),
        ('figure1_frametime_distribution', 'fig3_frametime'),
        ('figure4_binary_size', 'fig4_binary_size'),
        ('figure2_cold_startup', 'figure1_cold_startup'),
        ('figure3_ram_distribution', 'figure2_ram_distribution'),
        ('figure1_frametime_distribution', 'figure3_frametime_distribution'),
    ]
    for d in (OUTPUT_DIR, MANUSCRIPT_FIG_DIR, MANUSCRIPT_DIR):
        for src_base, dst_base in mapping:
            for ext in ['.pdf', '.png']:
                src = os.path.join(d, f'{src_base}{ext}')
                dst = os.path.join(d, f'{dst_base}{ext}')
                if os.path.exists(src):
                    shutil.copy2(src, dst)

    print("\nAll multi-tier statistical tables and publication figures successfully generated!")


if __name__ == "__main__":
    main()
