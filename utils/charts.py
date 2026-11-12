"""Matplotlib visualization helpers for five-day forecast temperatures."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure


def build_temperature_trend_figure(
    daily_df: pd.DataFrame,
    location_label: str,
    interval_label: str = "3-hour",
) -> Figure | None:
    """Create a Matplotlib Figure for daily min/max temperatures derived from forecast intervals."""
    if daily_df is None or daily_df.empty:
        return None

    plot_df = daily_df.dropna(subset=["temp_min_c", "temp_max_c"], how="all")
    if plot_df.empty:
        return None

    x_labels = [
        f"{row['date_str']}\n{row['weekday_short']}"
        for _, row in plot_df.iterrows()
    ]
    x_positions = list(range(len(plot_df)))
    min_temps = plot_df["temp_min_c"].tolist()
    max_temps = plot_df["temp_max_c"].tolist()

    fig = Figure(figsize=(9.2, 4.2), dpi=130)
    fig.patch.set_facecolor("#F8FAFC")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#FFFFFF")

    # Plot max and min series using actual values only
    ax.plot(
        x_positions,
        max_temps,
        marker="o",
        linewidth=2.5,
        markersize=7,
        color="#EA580C",
        label="Daily Max Temp (°C)",
        zorder=4,
    )
    ax.plot(
        x_positions,
        min_temps,
        marker="o",
        linewidth=2.5,
        markersize=7,
        color="#0284C7",
        label="Daily Min Temp (°C)",
        zorder=4,
    )

    valid_pairs = [
        (x, mn, mx)
        for x, mn, mx in zip(x_positions, min_temps, max_temps)
        if pd.notna(mn) and pd.notna(mx)
    ]
    if valid_pairs:
        xs = [p[0] for p in valid_pairs]
        mns = [p[1] for p in valid_pairs]
        mxs = [p[2] for p in valid_pairs]
        ax.fill_between(xs, mns, mxs, color="#BAE6FD", alpha=0.35, zorder=2)

    all_vals = [v for v in (min_temps + max_temps) if pd.notna(v)]
    if all_vals:
        y_min = min(all_vals)
        y_max = max(all_vals)
        pad = max(2.5, (y_max - y_min) * 0.25)
        ax.set_ylim(y_min - pad, y_max + pad)

    for x, val in zip(x_positions, max_temps):
        if pd.notna(val):
            ax.annotate(
                f"{val:.1f}°C",
                (x, val),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                fontsize=9,
                fontweight="bold",
                color="#C2410C",
            )

    for x, val in zip(x_positions, min_temps):
        if pd.notna(val):
            ax.annotate(
                f"{val:.1f}°C",
                (x, val),
                textcoords="offset points",
                xytext=(0, -15),
                ha="center",
                fontsize=9,
                fontweight="bold",
                color="#0369A1",
            )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, fontsize=9.5, color="#1E293B")
    ax.tick_params(axis="y", colors="#334155", labelsize=9.5)
    ax.set_ylabel("Temperature (°C)", fontsize=10, fontweight="bold", color="#1E293B")
    ax.set_title(
        f"5-Day Temperature Forecast — {location_label}",
        fontsize=12,
        fontweight="bold",
        color="#0F172A",
        pad=18,
    )
    ax.text(
        0.5,
        1.02,
        f"Daily values derived from provider {interval_label} forecast intervals",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#64748B",
    )

    ax.grid(axis="y", linestyle="--", linewidth=0.7, color="#CBD5E1", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")
    ax.legend(loc="upper right", frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0", fontsize=9)

    fig.tight_layout()
    return fig

