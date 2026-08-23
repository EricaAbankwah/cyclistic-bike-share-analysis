"""
Phase 4: Exploratory & Comparative Analysis Module
Analyzes cleaned Cyclistic data to compare member vs casual rider patterns.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from scipy import stats

from phase2_prepare import discover_csv_files, save_json


def convert_to_native_types(obj: Any) -> Any:
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        # Convert tuple keys to strings
        new_dict = {}
        for k, v in obj.items():
            if isinstance(k, tuple):
                k = str(k)
            new_dict[k] = convert_to_native_types(v)
        return new_dict
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    return obj


# ============================================================================
# DESCRIPTIVE STATISTICS
# ============================================================================

def compute_overall_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Compute overall dataset summary statistics."""
    summary = {
        "total_trips": int(len(df)),
        "date_range_min": str(df["started_at"].min()),
        "date_range_max": str(df["started_at"].max()),
        "unique_start_stations": int(df["start_station_name"].nunique()),
        "unique_end_stations": int(df["end_station_name"].nunique()),
        "bike_type_distribution": df["rideable_type"].value_counts().to_dict(),
        "member_casual_split": df["member_casual"].value_counts().to_dict(),
    }
    return summary


def compute_ride_duration_stats(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Compute ride duration statistics for members vs casuals."""
    stats_dict = {}
    
    for member_type in ["member", "casual"]:
        subset = df[df["member_casual"] == member_type]["ride_length_minutes"]
        stats_dict[member_type] = {
            "count": int(len(subset)),
            "mean": float(subset.mean()),
            "median": float(subset.median()),
            "std_dev": float(subset.std()),
            "min": float(subset.min()),
            "max": float(subset.max()),
            "percentile_25": float(subset.quantile(0.25)),
            "percentile_75": float(subset.quantile(0.75)),
            "percentile_95": float(subset.quantile(0.95)),
        }
    
    return stats_dict


# ============================================================================
# COMPARATIVE ANALYSIS
# ============================================================================

def analyze_day_of_week(df: pd.DataFrame) -> Dict[str, object]:
    """Analyze riding patterns by day of week for members vs casuals."""
    trip_count = df.groupby(["day_of_week", "member_casual"]).size().unstack(fill_value=0)
    avg_duration = df.groupby(["day_of_week", "member_casual"])["ride_length_minutes"].mean().unstack(fill_value=0)
    
    # Calculate weekday vs weekend ratio
    df["is_weekday"] = df["day_of_week"].isin([2, 3, 4, 5, 6])
    weekday_ratio = {}
    for member_type in ["member", "casual"]:
        subset = df[df["member_casual"] == member_type]
        weekday_trips = subset[subset["is_weekday"]].shape[0]
        total_trips = subset.shape[0]
        weekday_ratio[member_type] = float(weekday_trips / total_trips) if total_trips > 0 else 0.0
    
    return {
        "trip_count_by_day": trip_count.to_dict(),
        "avg_duration_by_day": avg_duration.to_dict(),
        "weekday_ratio": weekday_ratio,
    }


def analyze_hour_of_day(df: pd.DataFrame) -> Dict[str, object]:
    """Analyze riding patterns by hour of day for members vs casuals."""
    trip_count = df.groupby(["hour_of_day", "member_casual"]).size().unstack(fill_value=0)
    
    # Identify peak hours (top 3) for each member type
    peak_hours = {}
    for member_type in ["member", "casual"]:
        subset = df[df["member_casual"] == member_type]
        peak_by_hour = subset.groupby("hour_of_day").size().nlargest(3)
        peak_hours[member_type] = peak_by_hour.index.tolist()
    
    return {
        "trip_count_by_hour": trip_count.to_dict(),
        "peak_hours_member": peak_hours["member"],
        "peak_hours_casual": peak_hours["casual"],
    }


def analyze_seasonal(df: pd.DataFrame) -> Dict[str, object]:
    """Analyze seasonal and monthly patterns for members vs casuals."""
    trip_count = df.groupby(["month", "member_casual"]).size().unstack(fill_value=0)
    avg_duration = df.groupby(["month", "member_casual"])["ride_length_minutes"].mean().unstack(fill_value=0)
    season_count = df.groupby(["season", "member_casual"]).size().unstack(fill_value=0)
    
    return {
        "trip_count_by_month": trip_count.to_dict(),
        "avg_duration_by_month": avg_duration.to_dict(),
        "trip_count_by_season": season_count.to_dict(),
    }


def analyze_bike_type(df: pd.DataFrame) -> Dict[str, object]:
    """Analyze bike type preferences for members vs casuals."""
    distribution = df.groupby(["rideable_type", "member_casual"]).size().unstack(fill_value=0)
    
    # Normalize to percentages
    pct_distribution = distribution.div(distribution.sum(axis=0), axis=1).multiply(100)
    
    avg_duration_by_type = df.groupby(["rideable_type", "member_casual"])["ride_length_minutes"].mean().unstack(fill_value=0)
    
    return {
        "rideable_type_distribution": distribution.to_dict(),
        "rideable_type_pct": pct_distribution.to_dict(),
        "avg_duration_by_type": avg_duration_by_type.to_dict(),
    }


def analyze_geographic(df: pd.DataFrame) -> Dict[str, object]:
    """Analyze geographic patterns: top stations and trip distances."""
    # Top start and end stations
    top_start = df.groupby(["start_station_name", "member_casual"]).size().unstack(fill_value=0)
    top_start = top_start.sum(axis=1).nlargest(20)
    
    top_end = df.groupby(["end_station_name", "member_casual"]).size().unstack(fill_value=0)
    top_end = top_end.sum(axis=1).nlargest(20)
    
    # Round-trip ratio
    round_trip_ratio = {}
    for member_type in ["member", "casual"]:
        subset = df[df["member_casual"] == member_type]
        round_trips = subset["is_round_trip"].sum()
        total = len(subset)
        round_trip_ratio[member_type] = float(round_trips / total) if total > 0 else 0.0
    
    # Average trip distance
    avg_distance = {}
    for member_type in ["member", "casual"]:
        subset = df[df["member_casual"] == member_type]
        avg_distance[member_type] = float(subset["trip_distance_km"].mean())
    
    return {
        "top_start_stations": top_start.to_dict(),
        "top_end_stations": top_end.to_dict(),
        "round_trip_ratio": round_trip_ratio,
        "avg_trip_distance": avg_distance,
    }


# ============================================================================
# STATISTICAL TESTING
# ============================================================================

def statistical_t_test_ride_length(df: pd.DataFrame) -> Dict[str, object]:
    """Perform two-sample t-test on ride length differences."""
    member_duration = df[df["member_casual"] == "member"]["ride_length_minutes"]
    casual_duration = df[df["member_casual"] == "casual"]["ride_length_minutes"]
    
    t_stat, p_value = stats.ttest_ind(member_duration, casual_duration)
    
    # Calculate Cohen's d
    n1, n2 = len(member_duration), len(casual_duration)
    var1, var2 = member_duration.var(), casual_duration.var()
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    cohens_d = (member_duration.mean() - casual_duration.mean()) / pooled_std if pooled_std > 0 else 0
    
    # 95% Confidence interval for difference of means
    se_diff = np.sqrt(var1 / n1 + var2 / n2)
    mean_diff = member_duration.mean() - casual_duration.mean()
    ci_lower = mean_diff - 1.96 * se_diff
    ci_upper = mean_diff + 1.96 * se_diff
    
    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "ci_95": {"lower": float(ci_lower), "upper": float(ci_upper)},
    }


def statistical_chi_square_day_of_week(df: pd.DataFrame) -> Dict[str, object]:
    """Chi-square test: independence of member type and day of week."""
    contingency = pd.crosstab(df["day_of_week"], df["member_casual"])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    
    return {
        "chi2_statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof),
    }


def statistical_chi_square_bike_type(df: pd.DataFrame) -> Dict[str, object]:
    """Chi-square test: independence of member type and bike type."""
    contingency = pd.crosstab(df["rideable_type"], df["member_casual"])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    
    return {
        "chi2_statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof),
    }


# ============================================================================
# PIVOT TABLES
# ============================================================================

def pivot_duration_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: average ride duration by day of week and member type."""
    pivot = df.pivot_table(
        values="ride_length_minutes",
        index="day_of_week",
        columns="member_casual",
        aggfunc="mean",
    )
    return pivot


def pivot_volume_by_day(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: trip count by day of week and member type."""
    pivot = df.pivot_table(
        values="ride_id",
        index="day_of_week",
        columns="member_casual",
        aggfunc="count",
        fill_value=0,
    )
    return pivot


def pivot_duration_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: average ride duration by hour of day and member type."""
    pivot = df.pivot_table(
        values="ride_length_minutes",
        index="hour_of_day",
        columns="member_casual",
        aggfunc="mean",
    )
    return pivot


def pivot_bike_type_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: bike type distribution by member type."""
    pivot = df.pivot_table(
        values="ride_id",
        index="rideable_type",
        columns="member_casual",
        aggfunc="count",
        fill_value=0,
    )
    return pivot


def pivot_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table: monthly trip counts and durations by member type."""
    pivot = df.pivot_table(
        values="ride_length_minutes",
        index="month",
        columns="member_casual",
        aggfunc=["count", "mean"],
    )
    return pivot


def pivot_top_start_stations(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Pivot table: top start stations by member type."""
    top_stations = df["start_station_name"].value_counts().head(top_n).index
    subset = df[df["start_station_name"].isin(top_stations)]
    pivot = subset.pivot_table(
        values="ride_id",
        index="start_station_name",
        columns="member_casual",
        aggfunc="count",
        fill_value=0,
    )
    return pivot.sort_values(by=pivot.columns.tolist(), ascending=False)


# ============================================================================
# FULL ANALYSIS PIPELINE
# ============================================================================

def run_full_analysis(df: pd.DataFrame) -> Dict[str, object]:
    """Execute complete Phase 4 analysis pipeline."""
    results = {
        "overall_summary": compute_overall_summary(df),
        "ride_duration_stats": compute_ride_duration_stats(df),
        "day_of_week_analysis": analyze_day_of_week(df),
        "hour_of_day_analysis": analyze_hour_of_day(df),
        "seasonal_analysis": analyze_seasonal(df),
        "bike_type_analysis": analyze_bike_type(df),
        "geographic_analysis": analyze_geographic(df),
        "statistical_tests": {
            "ride_length_ttest": statistical_t_test_ride_length(df),
            "chi_square_day_of_week": statistical_chi_square_day_of_week(df),
            "chi_square_bike_type": statistical_chi_square_bike_type(df),
        },
        "pivot_tables": {
            "duration_by_day": pivot_duration_by_day(df).to_dict(),
            "volume_by_day": pivot_volume_by_day(df).to_dict(),
            "duration_by_hour": pivot_duration_by_hour(df).to_dict(),
            "bike_type_mix": pivot_bike_type_mix(df).to_dict(),
            "monthly_trends": pivot_monthly_trends(df).to_dict(),
            "top_start_stations": pivot_top_start_stations(df).to_dict(),
        },
    }
    return convert_to_native_types(results)


def main() -> int:
    """Execute Phase 4 analysis on full cleaned dataset."""
    root = Path(".").resolve()
    
    # Load cleaned Phase 3 data
    phase3_file = root / "analysis_output" / "phase3_cleaned_data.csv"
    if not phase3_file.exists():
        print(f"Error: {phase3_file} not found. Run Phase 3 first.", flush=True)
        return 1
    
    print("[1/4] Loading Phase 3 cleaned data...", flush=True)
    df = pd.read_csv(phase3_file)
    print(f"[1/4] Loaded {len(df)} rows", flush=True)
    
    # Parse datetime columns
    df["started_at"] = pd.to_datetime(df["started_at"])
    df["ended_at"] = pd.to_datetime(df["ended_at"])
    
    print("[2/4] Running full analysis pipeline...", flush=True)
    analysis_results = run_full_analysis(df)
    print("[2/4] Analysis complete", flush=True)
    
    print("[3/4] Saving results to JSON...", flush=True)
    save_json(analysis_results, root / "analysis_output" / "phase4_analysis_results.json")
    print("[3/4] Saved phase4_analysis_results.json", flush=True)
    
    print("[4/4] Summary statistics saved", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
