import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

EXPECTED_COLUMNS = [
    "ride_id",
    "rideable_type",
    "started_at",
    "ended_at",
    "start_station_name",
    "start_station_id",
    "end_station_name",
    "end_station_id",
    "start_lat",
    "start_lng",
    "end_lat",
    "end_lng",
    "member_casual",
]

CHICAGO_BOUNDS = {
    "lat_min": 41.5,
    "lat_max": 42.1,
    "lng_min": -88.4,
    "lng_max": -87.4,
}

SEASON_MAP = {
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


def discover_csv_files(root: Path) -> List[Path]:
    csv_files = sorted(root.glob("*.csv"))
    return [path for path in csv_files if path.name.lower().endswith(".csv")]


def load_csv_files(csv_files: List[Path]) -> pd.DataFrame:
    if not csv_files:
        raise ValueError("No CSV files found to load.")

    dfs = []
    for i, path in enumerate(csv_files, 1):
        print(f"  Loading {i}/{len(csv_files)}: {path.name}", flush=True)
        df = pd.read_csv(
            path,
            keep_default_na=False,
            na_values=["", "NA", "NaN"],
        )
        # Parse dates with flexible handling for both am/pm and 24-hour formats
        for col in ["started_at", "ended_at"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format="mixed", dayfirst=True, errors="coerce")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined.columns = [col.strip() for col in combined.columns]
    return combined


def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["ride_id", "rideable_type", "start_station_name", "end_station_name", "member_casual"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    if "member_casual" in df.columns:
        df["member_casual"] = df["member_casual"].str.lower()
    return df


def compute_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "started_at" not in df.columns or "ended_at" not in df.columns:
        raise ValueError("Required date columns are missing.")

    df["ride_length_minutes"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
    df["day_of_week"] = df["started_at"].dt.dayofweek + 1
    df["hour_of_day"] = df["started_at"].dt.hour
    df["month"] = df["started_at"].dt.month
    df["season"] = df["month"].map(SEASON_MAP)
    df["is_weekend"] = df["day_of_week"].isin([1, 7])
    return df


def validate_dataframe(df: pd.DataFrame) -> Dict[str, object]:
    metrics: Dict[str, object] = {}

    missing_core = df[["ride_id", "started_at", "ended_at", "member_casual"]].isna().sum().to_dict()
    metrics["missing_core_columns"] = missing_core

    if df["ride_id"].duplicated().any():
        metrics["duplicate_ride_id_count"] = int(df["ride_id"].duplicated().sum())
    else:
        metrics["duplicate_ride_id_count"] = 0

    metrics["member_casual_values"] = sorted(df["member_casual"].dropna().unique().tolist())

    if "ride_length_minutes" not in df.columns:
        raise ValueError("ride_length_minutes has not been computed.")

    metrics["negative_ride_length_count"] = int((df["ride_length_minutes"] < 0).sum())
    metrics["zero_ride_length_count"] = int((df["ride_length_minutes"] == 0).sum())

    metrics["min_started_at"] = str(df["started_at"].min())
    metrics["max_started_at"] = str(df["started_at"].max())
    metrics["period_coverage"] = {
        "min_month": int(df["started_at"].dt.month.min()),
        "max_month": int(df["started_at"].dt.month.max()),
        "min_year": int(df["started_at"].dt.year.min()),
        "max_year": int(df["started_at"].dt.year.max()),
    }

    coords = {
        "start_lat_valid": int(df["start_lat"].dropna().apply(float).between(CHICAGO_BOUNDS["lat_min"], CHICAGO_BOUNDS["lat_max"]).all()),
        "start_lng_valid": int(df["start_lng"].dropna().apply(float).between(CHICAGO_BOUNDS["lng_min"], CHICAGO_BOUNDS["lng_max"]).all()),
        "end_lat_valid": int(df["end_lat"].dropna().apply(float).between(CHICAGO_BOUNDS["lat_min"], CHICAGO_BOUNDS["lat_max"]).all()),
        "end_lng_valid": int(df["end_lng"].dropna().apply(float).between(CHICAGO_BOUNDS["lng_min"], CHICAGO_BOUNDS["lng_max"]).all()),
    }
    metrics["coordinate_bounds_valid"] = coords

    return metrics


def generate_data_summary(df: pd.DataFrame, csv_files: List[Path]) -> Dict[str, object]:
    summary = {
        "file_count": len(csv_files),
        "files": [str(path.name) for path in csv_files],
        "row_count": int(len(df)),
        "columns": df.columns.tolist(),
        "member_casual_distribution": df["member_casual"].value_counts(dropna=False).to_dict(),
        "rideable_type_distribution": df["rideable_type"].value_counts(dropna=False).to_dict(),
        "date_range": {
            "min": str(df["started_at"].min()),
            "max": str(df["started_at"].max()),
        },
        "missing_values": df.isna().sum().to_dict(),
    }
    return summary


def save_json(data: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def main() -> int:
    root = Path(".").resolve()
    csv_files = discover_csv_files(root)
    df = load_csv_files(csv_files)
    df = standardize_dataframe(df)
    df = compute_derived_columns(df)
    metrics = validate_dataframe(df)
    summary = generate_data_summary(df, csv_files)

    save_json(summary, root / "analysis_output" / "phase2_data_summary.json")
    save_json(metrics, root / "analysis_output" / "phase2_validation_metrics.json")
    df.head(1000).to_csv(root / "analysis_output" / "combined_data_sample.csv", index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
