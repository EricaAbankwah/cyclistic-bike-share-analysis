import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from phase2_prepare import (
    CHICAGO_BOUNDS,
    discover_csv_files,
    load_csv_files,
    save_json,
    standardize_dataframe,
)

PHASE3_CHICAGO_BOUNDS = {
    "lat_min": 41.5,
    "lat_max": 42.0,
    "lng_min": -88.3,
    "lng_max": -87.5,
}

PHASE3_SEASON_MAP = {
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Fall",
    10: "Fall",
    11: "Fall",
    12: "Winter",
}


def normalize_station_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["start_station_name", "end_station_name"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": None})
                .where(lambda s: s.notna(), None)
            )
            df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
    return df


def parse_mixed_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["started_at", "ended_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True, format="mixed")
    return df


def compute_trip_distance_km(df: pd.DataFrame) -> pd.Series:
    """Vectorized Haversine distance calculation."""
    lat1 = np.radians(df["start_lat"])
    lng1 = np.radians(df["start_lng"])
    lat2 = np.radians(df["end_lat"])
    lng2 = np.radians(df["end_lng"])
    
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng / 2) ** 2
    distance = 6371.0 * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    # Set NaN where any coordinate is missing
    mask = df[["start_lat", "start_lng", "end_lat", "end_lng"]].isna().any(axis=1)
    distance = distance.where(~mask, np.nan)
    return distance


def compute_is_round_trip(df: pd.DataFrame) -> pd.Series:
    """Vectorized round-trip detection by station name or location proximity."""
    # Check station name match (case-insensitive)
    start_stations = df["start_station_name"].fillna("").str.strip().str.lower()
    end_stations = df["end_station_name"].fillna("").str.strip().str.lower()
    by_station = (start_stations == end_stations) & (start_stations != "")
    
    # Compute distances for all rows
    distances = compute_trip_distance_km(df)
    by_proximity = distances <= 0.05
    
    return by_station | by_proximity


def compute_phase3_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = parse_mixed_datetimes(df)
    df["ride_length_minutes"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
    df["day_of_week"] = ((df["started_at"].dt.dayofweek + 1) % 7) + 1
    df["hour_of_day"] = df["started_at"].dt.hour
    df["month"] = df["started_at"].dt.month
    df["season"] = df["month"].map(PHASE3_SEASON_MAP)
    df["is_weekend"] = df["day_of_week"].isin([1, 7])
    df["trip_distance_km"] = compute_trip_distance_km(df)
    df["is_round_trip"] = compute_is_round_trip(df)
    df["is_extreme_duration"] = df["ride_length_minutes"] > 24 * 60
    return df


def is_within_bounds_vectorized(lat_series: pd.Series, lng_series: pd.Series) -> pd.Series:
    """Vectorized bounds checking for coordinates. Returns True for NaN values."""
    has_nan = lat_series.isna() | lng_series.isna()
    in_bounds = (
        (lat_series.ge(PHASE3_CHICAGO_BOUNDS["lat_min"])) &
        (lat_series.le(PHASE3_CHICAGO_BOUNDS["lat_max"])) &
        (lng_series.ge(PHASE3_CHICAGO_BOUNDS["lng_min"])) &
        (lng_series.le(PHASE3_CHICAGO_BOUNDS["lng_max"]))
    )
    return in_bounds | has_nan


def remove_invalid_trips(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    df = df.copy()

    initial_count = len(df)
    df = parse_mixed_datetimes(df)
    df = standardize_dataframe(df)
    df = normalize_station_names(df)
    df["ride_length_minutes"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60

    filters = {
        "null_member_casual": df["member_casual"].isna() | (df["member_casual"].astype(str).str.strip() == ""),
        "invalid_dates": df["started_at"].isna() | df["ended_at"].isna(),
        "negative_duration": df["ride_length_minutes"] < 0,
        "zero_duration": df["ride_length_minutes"] == 0,
        "out_of_bounds_start": ~is_within_bounds_vectorized(df["start_lat"], df["start_lng"]),
        "out_of_bounds_end": ~is_within_bounds_vectorized(df["end_lat"], df["end_lng"]),
    }

    removal_counts = {
        "removed_null_member_casual": int(filters["null_member_casual"].sum()),
        "removed_invalid_dates": int(filters["invalid_dates"].sum()),
        "removed_negative_duration": int(filters["negative_duration"].sum()),
        "removed_zero_duration": int(filters["zero_duration"].sum()),
        "removed_out_of_bounds_start": int(filters["out_of_bounds_start"].sum()),
        "removed_out_of_bounds_end": int(filters["out_of_bounds_end"].sum()),
    }

    removal_mask = (
        filters["null_member_casual"]
        | filters["invalid_dates"]
        | filters["negative_duration"]
        | filters["zero_duration"]
        | filters["out_of_bounds_start"]
        | filters["out_of_bounds_end"]
    )

    df = df.loc[~removal_mask].copy()
    df_before_dedupe = len(df)
    df = df.drop_duplicates(subset=["ride_id"], keep="first")
    removal_counts["removed_duplicate_ride_ids"] = df_before_dedupe - len(df)
    removal_counts["total_removed"] = initial_count - len(df)

    return df, removal_counts


def validate_phase3_dataframe(df: pd.DataFrame) -> Dict[str, object]:
    metrics: Dict[str, object] = {}
    metrics["duplicate_ride_id_count"] = int(df["ride_id"].duplicated().sum())
    metrics["invalid_date_ranges"] = int((df["ended_at"] < df["started_at"]).sum())
    metrics["out_of_bounds_start"] = int((~is_within_bounds_vectorized(df["start_lat"], df["start_lng"])).sum())
    metrics["out_of_bounds_end"] = int((~is_within_bounds_vectorized(df["end_lat"], df["end_lng"])).sum())

    core_fields = ["ride_id", "started_at", "ended_at", "member_casual"]
    total_cells = len(df) * len(core_fields)
    missing_cells = df[core_fields].isna().sum().sum()
    metrics["data_completeness_score"] = round(100.0 * (1 - missing_cells / total_cells), 2) if total_cells else 0.0
    return metrics


def process_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, object]]:
    df = df.copy()
    df = normalize_station_names(df)
    df = compute_phase3_features(df)
    df, removals = remove_invalid_trips(df)
    validation_metrics = validate_phase3_dataframe(df)
    return df, {**removals, **validation_metrics}


def save_cleaned_data(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> int:
    root = Path(".").resolve()
    csv_files = discover_csv_files(root)
    print(f"[1/5] Discovering CSV files: found {len(csv_files)} files", flush=True)
    
    # Process files incrementally and collect metrics
    all_cleaned = []
    all_metrics = {"removed_null_member_casual": 0, "removed_invalid_dates": 0, "removed_negative_duration": 0,
                   "removed_zero_duration": 0, "removed_out_of_bounds_start": 0, "removed_out_of_bounds_end": 0,
                   "removed_duplicate_ride_ids": 0, "total_removed": 0, "duplicate_ride_id_count": 0,
                   "invalid_date_ranges": 0, "out_of_bounds_start": 0, "out_of_bounds_end": 0,
                   "data_completeness_score": 100.0}
    
    print(f"[2/5] Processing {len(csv_files)} CSV files...", flush=True)
    for i, path in enumerate(csv_files, 1):
        print(f"      [{i}/{len(csv_files)}] {path.name}...", flush=True)
        df = pd.read_csv(path, keep_default_na=False, na_values=["", "NA", "NaN"])
        df = standardize_dataframe(df)
        df, metrics = process_dataframe(df)
        all_cleaned.append(df)
        for key in all_metrics:
            if isinstance(all_metrics[key], (int, float)):
                all_metrics[key] += metrics.get(key, 0)
    
    # Combine all cleaned data
    df_cleaned = pd.concat(all_cleaned, ignore_index=True)
    print(f"[3/5] Combined data: {len(df_cleaned)} rows total", flush=True)
    
    # Save outputs
    save_cleaned_data(df_cleaned, root / "analysis_output" / "phase3_cleaned_data.csv")
    print(f"[4/5] Saved cleaned data", flush=True)
    
    save_cleaned_data(df_cleaned.head(1000), root / "analysis_output" / "phase3_cleaned_data_sample.csv")
    print(f"[4/5] Saved cleaned data sample", flush=True)
    
    # Recompute aggregated metrics on the combined dataset
    final_metrics = validate_phase3_dataframe(df_cleaned)
    all_metrics.update(final_metrics)
    save_json(all_metrics, root / "analysis_output" / "phase3_cleaning_report.json")
    print(f"[5/5] Saved cleaning report", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
