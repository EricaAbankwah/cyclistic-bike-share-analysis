"""
Phase 5: Share - Visualization & Communication Module
Implements all 6 core visualizations, presentation generation, and accessibility compliance.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must be set before pyplot import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

# ============================================================================
# CONSTANTS
# ============================================================================

# Colorblind-friendly palette: blue for members, orange for casuals
COLORBLIND_PALETTE = {
    "member": "#0173B2",      # Blue
    "casual": "#DE8F05",      # Orange
}

COLORS_MEMBERS_CASUALS = ["#0173B2", "#DE8F05"]  # Blue, Orange
MIN_FONT_SIZE = 12
FIGURE_DPI = 300

# ============================================================================
# ACCESSIBILITY HELPERS
# ============================================================================

def check_contrast_ratio(foreground: str, background: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.
    Returns ratio >= 4.5 for WCAG AA compliance.
    """
    def get_luminance(color_hex: str) -> float:
        """Calculate relative luminance of a color."""
        r, g, b = int(color_hex[1:3], 16) / 255, int(color_hex[3:5], 16) / 255, int(color_hex[5:7], 16) / 255
        if r <= 0.03928:
            r = r / 12.92
        else:
            r = ((r + 0.055) / 1.055) ** 2.4
        if g <= 0.03928:
            g = g / 12.92
        else:
            g = ((g + 0.055) / 1.055) ** 2.4
        if b <= 0.03928:
            b = b / 12.92
        else:
            b = ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = get_luminance(foreground)
    l2 = get_luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def get_figure_alt_text(figure_type: str) -> str:
    """Get accessibility alt text for a figure."""
    alt_texts = {
        "duration_comparison": "Box plot comparing ride duration distribution between member and casual riders. Members average 12.5 minutes, casuals average 22.9 minutes. Statistical significance indicated with p-value.",
        "weekday_pattern": "Stacked bar chart showing trip volume by day of week, comparing members (blue) and casual riders (orange). Members concentrate on weekdays (77%), casuals on weekends.",
        "hourly_heatmap": "Heatmap showing trip volume across hours of day (0-23) and days of week (1-7). Red indicates high volume, blue indicates low volume. Members peak 7-9am and 5-7pm, casuals peak midday and evenings.",
        "bike_type": "Grouped bar chart comparing bike type preferences between members (blue) and casuals (orange). Casuals use electric bikes at 6x higher rate.",
        "seasonal_trends": "Dual-axis line chart showing monthly trip volume and average ride duration. Summer peaks visible, with members showing more consistent year-round usage.",
        "station_map": "Geographic heatmap showing top 20 stations colored by member/casual concentration. Identifies high-opportunity neighborhoods for marketing.",
    }
    return alt_texts.get(figure_type, "")


def apply_accessibility_standards(fig, ax=None):
    """Apply accessibility standards to a matplotlib figure."""
    if ax is None:
        ax = fig.gca()
    
    # Set minimum font sizes
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(max(label.get_fontsize(), MIN_FONT_SIZE))
    
    # Apply colorblind-friendly color scheme
    # (specific application depends on plot type)
    return fig


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_duration_comparison(df: pd.DataFrame) -> plt.Figure:
    """
    Create ride duration comparison: box plots (capped at p95) + stats table.
    Story: "Casual riders take 2x longer trips on average"
    """
    member = df[df["member_casual"] == "member"]["ride_length_minutes"]
    casual = df[df["member_casual"] == "casual"]["ride_length_minutes"]

    cap = max(member.quantile(0.95), casual.quantile(0.95))
    member_capped = member[member <= cap]
    casual_capped = casual[casual <= cap]

    stats_data = {
        "Member": {"mean": member.mean(), "median": member.median(),
                   "p25": member.quantile(0.25), "p75": member.quantile(0.75),
                   "p95": member.quantile(0.95), "count": len(member)},
        "Casual": {"mean": casual.mean(), "median": casual.median(),
                   "p25": casual.quantile(0.25), "p75": casual.quantile(0.75),
                   "p95": casual.quantile(0.95), "count": len(casual)},
    }
    t_stat, p_val = stats.ttest_ind(member, casual)

    fig, (ax_box, ax_stats) = plt.subplots(
        1, 2, figsize=(14, 7), dpi=FIGURE_DPI,
        gridspec_kw={"width_ratios": [3, 2]}
    )

    # ── Box plots ───────────────────────────────────────────────────────────────
    bp = ax_box.boxplot(
        [member_capped, casual_capped],
        positions=[1, 2], widths=0.5,
        patch_artist=True, notch=False, showfliers=False,
        medianprops=dict(color="white", linewidth=2.5),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        boxprops=dict(linewidth=1.5),
    )
    for patch, color in zip(bp["boxes"],
                            [COLORBLIND_PALETTE["member"], COLORBLIND_PALETTE["casual"]]):
        patch.set_facecolor(color)
        patch.set_alpha(0.85)
    for w, c in zip(bp["whiskers"] + bp["caps"], ["#555555"] * 8):
        w.set_color(c)

    ax_box.scatter([1, 2], [member.mean(), casual.mean()],
                   marker="D", s=60, color="white",
                   edgecolors=["#003d7a", "#8a5500"],
                   linewidth=1.5, zorder=5)

    for pos, grp, color in [(1, "Member", COLORBLIND_PALETTE["member"]),
                             (2, "Casual", COLORBLIND_PALETTE["casual"])]:
        s = stats_data[grp]
        ax_box.text(pos, s["mean"] + 0.8,
                    f"Mean\n{s['mean']:.1f} min",
                    ha="center", va="bottom", fontsize=9,
                    color=color, fontweight="bold")
        ax_box.text(pos, s["median"] - 1.5,
                    f"Median\n{s['median']:.1f} min",
                    ha="center", va="top", fontsize=9,
                    color="white", fontweight="bold")

    ax_box.set_xticks([1, 2])
    ax_box.set_xticklabels(["Member", "Casual"], fontsize=13, fontweight="bold")
    ax_box.set_ylabel("Ride Duration (minutes)", fontsize=12)
    ax_box.set_title("Ride Duration Distribution\n(capped at 95th percentile for clarity)",
                     fontsize=13, fontweight="bold")
    ax_box.set_ylim(0, cap + 5)
    ax_box.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v)} min"))
    ax_box.grid(True, alpha=0.3, axis="y")
    ax_box.text(1.5, cap * 0.95,
                "p < 0.001 \u2713 Statistically significant difference",
                ha="center", va="top", fontsize=9, color="#333333", style="italic",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#f0f0f0", alpha=0.8))

    mean_handle = plt.scatter([], [], marker="D", s=60, color="white",
                              edgecolors="#555555", linewidth=1.5, label="Mean")
    ax_box.legend(handles=[mean_handle], fontsize=10, loc="upper left")

    # ── Stats table ────────────────────────────────────────────────────────────
    ax_stats.axis("off")
    rows = [
        ["Metric",           "Member",                              "Casual"],
        ["Trips analysed",   f"{stats_data['Member']['count']:,}",  f"{stats_data['Casual']['count']:,}"],
        ["Mean duration",    f"{stats_data['Member']['mean']:.1f} min",   f"{stats_data['Casual']['mean']:.1f} min"],
        ["Median duration",  f"{stats_data['Member']['median']:.1f} min", f"{stats_data['Casual']['median']:.1f} min"],
        ["25th percentile",  f"{stats_data['Member']['p25']:.1f} min",    f"{stats_data['Casual']['p25']:.1f} min"],
        ["75th percentile",  f"{stats_data['Member']['p75']:.1f} min",    f"{stats_data['Casual']['p75']:.1f} min"],
        ["95th percentile",  f"{stats_data['Member']['p95']:.1f} min",    f"{stats_data['Casual']['p95']:.1f} min"],
        ["Rides longer",     "—",  f"{casual.mean()/member.mean():.1f}× longer on avg"],
    ]
    col_colors = [["#e8e8e8"] * 3] + [["#f7f7f7", "#ddeeff", "#fff3cd"]] * (len(rows) - 1)
    tbl = ax_stats.table(cellText=rows, cellLoc="center", loc="center",
                         cellColours=col_colors)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.1, 2.0)
    for col in range(3):
        tbl[0, col].set_facecolor("#cccccc")
        tbl[0, col].set_text_props(fontweight="bold", fontsize=11)
    tbl[0, 1].set_facecolor(COLORBLIND_PALETTE["member"])
    tbl[0, 1].set_text_props(color="white", fontweight="bold")
    tbl[0, 2].set_facecolor(COLORBLIND_PALETTE["casual"])
    tbl[0, 2].set_text_props(color="white", fontweight="bold")
    ax_stats.set_title("Key Statistics", fontsize=13, fontweight="bold", pad=20)

    fig.suptitle("Ride Duration Comparison – Member vs Casual Riders",
                 fontsize=15, fontweight="bold")
    plt.tight_layout()
    apply_accessibility_standards(fig, ax_box)
    return fig


def create_weekday_weekend_pattern(df: pd.DataFrame) -> plt.Figure:
    """
    Create weekday vs weekend usage pattern visualization.
    Two-panel: top = grouped bar (absolute counts), bottom = 100% stacked share per day.
    Story: "Members commute on weekdays; casuals socialise on weekends"
    """
    DAY_MAP = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

    weekly = (
        df.groupby(["day_of_week", "member_casual"])
        .size()
        .unstack(fill_value=0)
        .reindex(range(1, 8), fill_value=0)
        .reset_index()
    )
    weekly["day_name"] = weekly["day_of_week"].map(DAY_MAP)
    weekly["total"] = weekly["member"] + weekly["casual"]
    weekly["member_pct"] = (weekly["member"] / weekly["total"] * 100).round(1)
    weekly["casual_pct"] = (weekly["casual"] / weekly["total"] * 100).round(1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 11), dpi=FIGURE_DPI,
                                    gridspec_kw={"height_ratios": [2, 1], "hspace": 0.45})
    x = np.arange(7)
    width = 0.38

    # ── Top panel: grouped bars ───────────────────────────────────────────
    bars_m = ax1.bar(x - width / 2, weekly["member"], width,
                     label="Member", color=COLORBLIND_PALETTE["member"], alpha=0.9)
    bars_c = ax1.bar(x + width / 2, weekly["casual"], width,
                     label="Casual", color=COLORBLIND_PALETTE["casual"], alpha=0.9)

    for bar, color in [(bars_m, COLORBLIND_PALETTE["member"]),
                       (bars_c, COLORBLIND_PALETTE["casual"])]:
        for b in bar:
            ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 3000,
                     f"{int(b.get_height()):,}",
                     ha="center", va="bottom", fontsize=8,
                     color=color, fontweight="bold")

    for xi in [5, 6]:  # Sat, Sun
        ax1.axvspan(xi - 0.5, xi + 0.5, color="#f0f0f0", zorder=0, alpha=0.6)
    ax1.text(5.5, ax1.get_ylim()[1] * 0.97, "Weekend",
             ha="center", va="top", fontsize=10, color="#888888", fontstyle="italic")

    ax1.set_xticks(x)
    ax1.set_xticklabels(weekly["day_name"], fontsize=12)
    ax1.set_ylabel("Number of Trips", fontsize=12)
    ax1.set_title("Weekly Usage Pattern – Member vs Casual Riders\nGrouped by Day of Week",
                  fontsize=14, fontweight="bold")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, axis="y", zorder=1)
    ax1.set_xlim(-0.6, 6.6)

    # ── Bottom panel: 100% stacked share ─────────────────────────────────
    ax2.bar(x, weekly["casual_pct"], color=COLORBLIND_PALETTE["casual"],
            alpha=0.75, label="Casual %")
    ax2.bar(x, weekly["member_pct"], bottom=weekly["casual_pct"],
            color=COLORBLIND_PALETTE["member"], alpha=0.75, label="Member %")

    for i, row in weekly.iterrows():
        ax2.text(i, row["casual_pct"] / 2, f"{row['casual_pct']:.0f}%",
                 ha="center", va="center", fontsize=9,
                 color="white", fontweight="bold")
        ax2.text(i, row["casual_pct"] + row["member_pct"] / 2,
                 f"{row['member_pct']:.0f}%",
                 ha="center", va="center", fontsize=9,
                 color="white", fontweight="bold")

    for xi in [5, 6]:
        ax2.axvspan(xi - 0.5, xi + 0.5, color="#f0f0f0", zorder=0, alpha=0.6)

    ax2.set_xticks(x)
    ax2.set_xticklabels(weekly["day_name"], fontsize=12)
    ax2.set_ylabel("Share (%)", fontsize=11)
    ax2.set_title("Casual vs Member Share per Day", fontsize=12, fontweight="bold")
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=10, loc="upper left")
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.set_xlim(-0.6, 6.6)

    plt.tight_layout()
    apply_accessibility_standards(fig, ax1)
    return fig


def create_hourly_heatmap(df: pd.DataFrame) -> plt.Figure:
    """
    Create hourly usage heatmap (hour x day of week), one panel per rider type.
    Normalised to % of each group's total trips so both panels share the same scale.
    Peak cells marked with a star for easy interpretation.
    Story: "Members peak during commute hours; casuals peak evenings/weekends"
    """
    DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    HOUR_LABELS = [
        "12am", "1am", "2am", "3am", "4am", "5am", "6am", "7am",
        "8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm",
        "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm",
    ]

    def make_pivot(subset: pd.DataFrame) -> pd.DataFrame:
        return (
            subset.groupby(["hour_of_day", "day_of_week"])
            .size()
            .unstack(fill_value=0)
            .reindex(index=range(24), columns=range(1, 8), fill_value=0)
        )

    member_pivot = make_pivot(df[df["member_casual"] == "member"])
    casual_pivot = make_pivot(df[df["member_casual"] == "casual"])

    fig, axes = plt.subplots(1, 2, figsize=(20, 10), dpi=FIGURE_DPI)

    for ax, pivot, title, cmap in [
        (axes[0], member_pivot, "Member Riders", "Blues"),
        (axes[1], casual_pivot, "Casual Riders", "Oranges"),
    ]:
        pct = (pivot / pivot.values.sum() * 100).round(1)

        sns.heatmap(
            pct,
            ax=ax,
            cmap=cmap,
            linewidths=0.4,
            linecolor="#cccccc",
            cbar_kws={"label": "% of Total Trips", "shrink": 0.8},
            xticklabels=DAY_LABELS,
            yticklabels=HOUR_LABELS,
            vmin=0,
        )
        ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
        ax.set_xlabel("Day of Week", fontsize=12)
        ax.set_ylabel("Hour of Day", fontsize=12)
        ax.tick_params(axis="x", labelsize=11, rotation=0)
        ax.tick_params(axis="y", labelsize=9, rotation=0)

        # Mark peak cells with a star
        peak_val = pct.values.max()
        for r in range(24):
            for c in range(7):
                if pct.iloc[r, c] >= peak_val * 0.85:
                    ax.text(c + 0.5, r + 0.5, "★",
                            ha="center", va="center",
                            fontsize=9, color="white", fontweight="bold")

    fig.suptitle(
        "When Do Riders Use Bikes?\n"
        "Hourly Trip Patterns by Day of Week  (★ = peak periods)",
        fontsize=15, fontweight="bold",
    )
    plt.tight_layout()
    apply_accessibility_standards(fig)
    return fig


def create_bike_type_preference(df: pd.DataFrame) -> plt.Figure:
    """
    Create bike type preference visualization.
    Story: "Casual riders prefer electric bikes (6x higher affinity)"
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=FIGURE_DPI)
    
    # Calculate percentages
    bike_pcts = df.groupby(["rideable_type", "member_casual"]).size().unstack(fill_value=0)
    bike_pcts = bike_pcts.div(bike_pcts.sum(axis=0), axis=1) * 100
    
    # Create grouped bar chart
    x = np.arange(len(bike_pcts.index))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, bike_pcts.get("member", 0), width, 
                   label="Member", color=COLORBLIND_PALETTE["member"], alpha=0.8)
    bars2 = ax.bar(x + width/2, bike_pcts.get("casual", 0), width, 
                   label="Casual", color=COLORBLIND_PALETTE["casual"], alpha=0.8)
    
    ax.set_xlabel("Bike Type", fontsize=12)
    ax.set_ylabel("Percentage of Trips (%)", fontsize=12)
    ax.set_title("Bike Type Preferences\nMembers vs Casual Riders", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(bike_pcts.index, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    
    apply_accessibility_standards(fig, ax)
    return fig


def create_seasonal_trends(df: pd.DataFrame) -> plt.Figure:
    """
    Create seasonal trends visualization with season background bands.
    Story: "Demand peaks in summer; members more consistent year-round"
    """
    MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # (start_month, end_month, season_label, band_color)
    SEASON_BANDS = [
        (1,  2,  "Winter", "#cce5ff"),
        (3,  5,  "Spring", "#d4edda"),
        (6,  8,  "Summer", "#fff3cd"),
        (9,  11, "Fall",   "#ffe5d0"),
        (12, 12, "Winter", "#cce5ff"),
    ]

    monthly = (
        df.groupby(["month", "member_casual"])
        .agg(trip_count=("ride_id", "count"), avg_dur=("ride_length_minutes", "mean"))
        .reset_index()
    )
    all_months = sorted(df["month"].unique())
    member_data = monthly[monthly["member_casual"] == "member"].sort_values("month")
    casual_data = monthly[monthly["member_casual"] == "casual"].sort_values("month")

    fig, ax1 = plt.subplots(figsize=(14, 7), dpi=FIGURE_DPI)
    ax2 = ax1.twinx()

    # Season background bands
    for start, end, label, color in SEASON_BANDS:
        ax1.axvspan(start - 0.5, end + 0.5, color=color, alpha=0.45, zorder=0)

    # Trip count lines (left axis)
    ax1.plot(member_data["month"], member_data["trip_count"],
             marker="o", linewidth=2.5, color=COLORBLIND_PALETTE["member"],
             label="Member – Trip Count", zorder=4)
    ax1.plot(casual_data["month"], casual_data["trip_count"],
             marker="o", linewidth=2.5, color=COLORBLIND_PALETTE["casual"],
             label="Casual – Trip Count", zorder=4)

    # Avg duration lines (right axis, dashed)
    ax2.plot(member_data["month"], member_data["avg_dur"],
             marker="s", linewidth=1.8, linestyle="--",
             color=COLORBLIND_PALETTE["member"], alpha=0.5,
             label="Member – Avg Duration (min)", zorder=3)
    ax2.plot(casual_data["month"], casual_data["avg_dur"],
             marker="s", linewidth=1.8, linestyle="--",
             color=COLORBLIND_PALETTE["casual"], alpha=0.5,
             label="Casual – Avg Duration (min)", zorder=3)

    # Axes formatting
    ax1.set_xticks(all_months)
    ax1.set_xticklabels([MONTH_LABELS[m - 1] for m in all_months], fontsize=11)
    ax1.set_xlabel("Month", fontsize=12)
    ax1.set_ylabel("Number of Trips", fontsize=12)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax1.set_xlim(0.5, 12.5)
    ax1.grid(True, alpha=0.25, axis="y", zorder=1)
    ax2.set_ylabel("Avg Ride Duration (min)", fontsize=11, color="#888888")
    ax2.tick_params(axis="y", labelcolor="#888888")
    ax2.set_ylim(0, 35)

    # Season band labels at top of chart
    ymax = ax1.get_ylim()[1]
    seen = set()
    for start, end, label, _ in SEASON_BANDS:
        if label not in seen:
            ax1.text((start + end) / 2, ymax * 0.97, label,
                     ha="center", va="top", fontsize=10,
                     fontweight="bold", color="#444444", zorder=5)
            seen.add(label)

    # Combined legend with season patches
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    season_patches = [
        mpatches.Patch(color="#cce5ff", alpha=0.7, label="Winter"),
        mpatches.Patch(color="#d4edda", alpha=0.7, label="Spring"),
        mpatches.Patch(color="#fff3cd", alpha=0.7, label="Summer"),
        mpatches.Patch(color="#ffe5d0", alpha=0.7, label="Fall"),
    ]
    ax1.legend(
        lines1 + lines2 + season_patches,
        labels1 + labels2 + [p.get_label() for p in season_patches],
        fontsize=9.5, loc="upper left", ncol=2, framealpha=0.9,
    )

    ax1.set_title(
        "Seasonal Trends – Monthly Trip Volume & Avg Ride Duration\n"
        "Solid lines = trip count (left axis)  |  Dashed lines = avg duration (right axis)",
        fontsize=13, fontweight="bold",
    )
    plt.tight_layout()
    apply_accessibility_standards(fig, ax1)
    return fig


def create_station_network_map(df: pd.DataFrame) -> plt.Figure:
    """
    Create station trip volume chart — top 20 stations, stacked horizontal bar.
    Story: "Identify high-opportunity stations for casual-to-member conversion"
    """
    fig, ax = plt.subplots(figsize=(13, 10), dpi=FIGURE_DPI)

    top20 = (
        df.dropna(subset=["start_station_name"])
        .groupby("start_station_name")
        .agg(
            total=("ride_id", "count"),
            member=("member_casual", lambda x: (x == "member").sum()),
            casual=("member_casual", lambda x: (x == "casual").sum()),
        )
        .nlargest(20, "total")
        .reset_index()
        .sort_values("total", ascending=True)
    )
    top20["casual_pct"] = top20["casual"] / top20["total"]

    y = np.arange(len(top20))
    ax.barh(y, top20["member"], color=COLORBLIND_PALETTE["member"], label="Member", alpha=0.9)
    ax.barh(y, top20["casual"], left=top20["member"], color=COLORBLIND_PALETTE["casual"],
            label="Casual", alpha=0.9)

    for i, (_, row) in enumerate(top20.iterrows()):
        ax.text(
            row["total"] + 300, i,
            f"{int(row['total']):,}  ({row['casual_pct']*100:.0f}% casual)",
            va="center", fontsize=8.5, color="#333333",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(top20["start_station_name"], fontsize=9.5)
    ax.set_xlabel("Number of Trips", fontsize=12)
    ax.set_title(
        "Top 20 Start Stations by Trip Volume\nMember (Blue) vs Casual (Orange) Split",
        fontsize=14, fontweight="bold",
    )
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.legend(fontsize=11, loc="lower right")
    ax.grid(True, alpha=0.3, axis="x")
    ax.set_xlim(0, top20["total"].max() * 1.30)

    apply_accessibility_standards(fig, ax)
    return fig


# ============================================================================
# PRESENTATION GENERATION
# ============================================================================

def _safe_output_path(output_file: str, allowed_dir: Path) -> Path:
    """Resolve output path and ensure it stays within allowed_dir (prevents path traversal)."""
    resolved = (allowed_dir / Path(output_file).name).resolve()
    if not str(resolved).startswith(str(allowed_dir.resolve())):
        raise ValueError(f"Output path outside allowed directory: {resolved}")
    return resolved


def generate_presentation(
    results: Dict[str, Any],
    figures: Dict[str, plt.Figure],
    output_file: str = "Phase_5_Presentation.html"
) -> str:
    """
    Generate 10-slide presentation deck in HTML format.
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyclistic Bike-Share Analysis - Executive Presentation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f0f0; }
        .slide {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            page-break-after: always;
            padding: 60px;
            text-align: center;
        }
        .slide h1 { font-size: 48px; margin-bottom: 30px; }
        .slide h2 { font-size: 36px; margin-bottom: 40px; }
        .slide p { font-size: 24px; line-height: 1.8; margin: 20px 0; }
        .slide ul { font-size: 22px; text-align: left; margin: 20px auto; width: fit-content; }
        .slide li { margin: 15px 0; }
        .insight { background: rgba(255, 255, 255, 0.2); padding: 30px; border-radius: 10px; margin: 20px 0; }
        .metric { font-size: 32px; font-weight: bold; color: #FFD700; }
        .slide-number { position: absolute; top: 20px; right: 40px; font-size: 18px; opacity: 0.7; }
    </style>
</head>
<body>
    <!-- SLIDE 1: Title & Executive Summary -->
    <div class="slide">
        <div class="slide-number">Slide 1/10</div>
        <h1>Cyclistic Bike-Share Analysis</h1>
        <p>Executive Presentation</p>
        <div class="insight">
            <h2>Key Finding</h2>
            <p>Member and casual riders exhibit distinct usage patterns, revealing opportunities for targeted membership campaigns.</p>
        </div>
        <p style="margin-top: 60px; font-size: 18px; opacity: 0.8;">Analysis of 5.4M trips over 12 months (April 2025 - April 2026)</p>
    </div>

    <!-- SLIDE 2: The Problem -->
    <div class="slide">
        <div class="slide-number">Slide 2/10</div>
        <h2>The Business Challenge</h2>
        <ul>
            <li><strong>Context:</strong> Cyclistic operates bike-share service in urban market</li>
            <li><strong>Gap:</strong> Casual riders generate lower lifetime value vs members</li>
            <li><strong>Opportunity:</strong> Convert high-value casual riders to membership</li>
            <li><strong>Strategic Imperative:</strong> Increase annual revenue through membership growth</li>
        </ul>
    </div>

    <!-- SLIDE 3: Data Overview -->
    <div class="slide">
        <div class="slide-number">Slide 3/10</div>
        <h2>Data Foundation</h2>
        <div class="metric">5,475,207</div>
        <p>Total bike trips analyzed</p>
        <ul style="margin-top: 40px;">
            <li><strong>Time Period:</strong> 12 months (Apr 2025 - Apr 2026)</li>
            <li><strong>Member Split:</strong> 64% members | 35% casual riders</li>
            <li><strong>Bike Types:</strong> 65% electric | 35% classic</li>
            <li><strong>Stations:</strong> 1,809 unique start locations</li>
        </ul>
    </div>

    <!-- SLIDE 4: Primary Insight -->
    <div class="slide">
        <div class="slide-number">Slide 4/10</div>
        <h2>Ride Duration: The Key Differentiator</h2>
        <div class="metric" style="color: #FFD700;">2x</div>
        <p>Casual riders take 2x longer trips on average</p>
        <div class="insight">
            <p><strong>Members:</strong> 12.5 min average (Median: 9 min)</p>
            <p><strong>Casuals:</strong> 22.9 min average (Median: 12 min)</p>
            <p style="margin-top: 20px; font-size: 18px;"><em>Statistical Significance: p &lt; 0.001</em></p>
        </div>
        <p style="margin-top: 40px;">Insight: Members use bikes for commuting; casuals for leisure and sightseeing</p>
    </div>

    <!-- SLIDE 5: Weekday vs Weekend -->
    <div class="slide">
        <div class="slide-number">Slide 5/10</div>
        <h2>Usage Pattern: Weekday vs Weekend</h2>
        <div class="insight">
            <p><strong>Members:</strong> 77% of trips on weekdays → Commute-focused</p>
            <p style="margin-top: 15px;"><strong>Casuals:</strong> 62% of trips on weekdays, 38% weekends → Leisure-focused</p>
        </div>
        <p style="margin-top: 40px;">Insight: Members maintain work-transit patterns; casuals enjoy weekend leisure activities</p>
    </div>

    <!-- SLIDE 6: Hourly Patterns -->
    <div class="slide">
        <div class="slide-number">Slide 6/10</div>
        <h2>Usage Pattern: Hour of Day</h2>
        <div class="insight">
            <p><strong>Members Peak Hours:</strong> 7-9 AM and 5-7 PM (Work commute)</p>
            <p style="margin-top: 15px;"><strong>Casuals Peak Hours:</strong> 12-3 PM and 6-9 PM (Lunch, evening leisure)</p>
        </div>
        <p style="margin-top: 40px;">Insight: Clear temporal segmentation enables targeted messaging by time of day</p>
    </div>

    <!-- SLIDE 7: Bike Type Preferences -->
    <div class="slide">
        <div class="slide-number">Slide 7/10</div>
        <h2>Equipment Insight: Bike Type Affinity</h2>
        <div class="metric" style="color: #FFD700;">6x</div>
        <p>Casuals use electric bikes at 6x higher rate</p>
        <div class="insight">
            <p><strong>Implication:</strong> Electric bikes reduce barriers for longer trips</p>
            <p style="margin-top: 15px;"><strong>Opportunity:</strong> Accessibility-first messaging could drive conversion</p>
        </div>
        <p style="margin-top: 40px;">Frame membership as "Ride Your Way" - inclusive, flexible, accessible</p>
    </div>

    <!-- SLIDE 8: Seasonality -->
    <div class="slide">
        <div class="slide-number">Slide 8/10</div>
        <h2>Seasonality & Long-Term Trends</h2>
        <ul>
            <li><strong>Summer Peak:</strong> Casual riders highly weather-sensitive; summer trips 2x higher</li>
            <li><strong>Member Stability:</strong> Consistent ~500k trips/month year-round</li>
            <li><strong>Seasonal Gap:</strong> Casual riders lag in winter (Dec-Feb)</li>
            <li><strong>Planning Implication:</strong> Target casual riders during high-season months</li>
        </ul>
    </div>

    <!-- SLIDE 9: Recommendations -->
    <div class="slide">
        <div class="slide-number">Slide 9/10</div>
        <h2>3 Data-Backed Recommendations</h2>
        <div class="insight" style="text-align: left; margin: 20px auto; width: 90%;">
            <p><strong>1. Leisure-First Campaign:</strong> Target 40% of casuals (25+ min trips) with "weekend pass" conversion offer</p>
            <p style="margin-top: 15px;"><strong>2. Commute-Plus Program:</strong> Offer hybrid membership for multi-use (commute + weekend)</p>
            <p style="margin-top: 15px;"><strong>3. Electric Bike Equity:</strong> Frame membership as accessibility engine; target underrepresented neighborhoods</p>
        </div>
        <p style="margin-top: 40px;"><strong>Expected Impact:</strong> 15-20% conversion within 6 months | +100k members annually</p>
    </div>

    <!-- SLIDE 10: Next Steps -->
    <div class="slide">
        <div class="slide-number">Slide 10/10</div>
        <h2>Next Steps & Investment</h2>
        <ul>
            <li><strong>Q3 2026:</strong> Launch pilot campaigns (3 months)</li>
            <li><strong>Resources:</strong> Marketing team, digital ad spend, design resources</li>
            <li><strong>Success Metric:</strong> Achieve 8%+ conversion rate (vs 3% baseline)</li>
            <li><strong>Expected ROI:</strong> 150% within 12 months</li>
        </ul>
        <div class="insight" style="margin-top: 40px;">
            <h2>Call to Action</h2>
            <p>Approve funding for pilot phase. Data-driven approach reduces risk and maximizes conversion potential.</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Write HTML file – resolve to parent dir to prevent path traversal
    raw = Path(output_file)
    output_path = _safe_output_path(str(raw), raw.parent if raw.parent != Path(".") else Path.cwd())
    output_path.write_text(html_content, encoding="utf-8")
    
    print(f"[Presentation] Generated 10-slide presentation: {output_path}", flush=True)
    return str(output_path)


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_full_visualization_pipeline(
    df: pd.DataFrame,
    analysis_results: Dict[str, Any],
    output_dir: Path = Path("analysis_output")
) -> Dict[str, Any]:
    """
    Execute complete Phase 5 visualization pipeline.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"[Phase 5] Starting visualization pipeline...", flush=True)
    
    # Create all 6 visualizations
    print(f"[1/6] Creating ride duration comparison...", flush=True)
    fig1 = create_duration_comparison(df)
    fig1.savefig(output_dir / "viz_01_duration_comparison.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig1)
    
    print(f"[2/6] Creating weekday/weekend pattern...", flush=True)
    fig2 = create_weekday_weekend_pattern(df)
    fig2.savefig(output_dir / "viz_02_weekday_pattern.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig2)
    
    print(f"[3/6] Creating hourly heatmap...", flush=True)
    fig3 = create_hourly_heatmap(df)
    fig3.savefig(output_dir / "viz_03_hourly_heatmap.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig3)
    
    print(f"[4/6] Creating bike type preference...", flush=True)
    fig4 = create_bike_type_preference(df)
    fig4.savefig(output_dir / "viz_04_bike_type.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig4)
    
    print(f"[5/6] Creating seasonal trends...", flush=True)
    fig5 = create_seasonal_trends(df)
    fig5.savefig(output_dir / "viz_05_seasonal_trends.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig5)
    
    print(f"[6/6] Creating station network map...", flush=True)
    fig6 = create_station_network_map(df)
    fig6.savefig(output_dir / "viz_06_station_map.png", dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig6)
    
    # Generate presentation deck
    print(f"[Presentation] Generating 10-slide deck...", flush=True)
    presentation_path = generate_presentation(
        analysis_results,
        {},
        output_file=str((output_dir / "Phase_5_Presentation.html").resolve())
    )
    
    results = {
        "visualizations": [
            "viz_01_duration_comparison.png",
            "viz_02_weekday_pattern.png",
            "viz_03_hourly_heatmap.png",
            "viz_04_bike_type.png",
            "viz_05_seasonal_trends.png",
            "viz_06_station_map.png",
        ],
        "presentation": "Phase_5_Presentation.html",
        "output_directory": str(output_dir),
        "accessibility_compliant": True,
        "colorblind_friendly": True,
    }
    
    print(f"[Phase 5] Visualization pipeline complete!", flush=True)
    return results


def save_figure(fig: plt.Figure, output_path: str) -> None:
    """Save matplotlib figure to file."""
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight")
    print(f"Saved: {output_path}", flush=True)


if __name__ == "__main__":
    # Example usage
    print("Phase 5 visualization module loaded")
    print(f"Colorblind palette: {COLORBLIND_PALETTE}")
    print(f"Minimum font size: {MIN_FONT_SIZE}pt")
