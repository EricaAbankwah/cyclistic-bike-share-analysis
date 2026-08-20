import json
import os
from pathlib import Path

import pandas as pd
import pytest

from phase2_prepare import (
    CHICAGO_BOUNDS,
    EXPECTED_COLUMNS,
    SEASON_MAP,
    compute_derived_columns,
    discover_csv_files,
    generate_data_summary,
    load_csv_files,
    standardize_dataframe,
    validate_dataframe,
)

ROOT = Path(".").resolve()


def test_discover_csv_files_returns_csv_files():
    csv_files = discover_csv_files(ROOT)
    assert csv_files
    assert all(path.suffix == ".csv" for path in csv_files)


def test_load_csv_files_reads_all_expected_columns():
    csv_files = discover_csv_files(ROOT)
    df = load_csv_files(csv_files[:1])
    assert set(EXPECTED_COLUMNS).issubset(set(df.columns))


def test_standardize_dataframe_lowercases_member_casual():
    df = pd.DataFrame({"member_casual": ["MEMBER", "Casual", "member"]})
    standardized = standardize_dataframe(df)
    assert standardized["member_casual"].tolist() == ["member", "casual", "member"]


def test_compute_derived_columns_creates_columns():
    df = pd.DataFrame(
        {
            "started_at": pd.to_datetime(["2025-05-01 08:00:00", "2025-05-01 09:00:00"]),
            "ended_at": pd.to_datetime(["2025-05-01 08:12:00", "2025-05-01 09:25:00"]),
        }
    )
    derived = compute_derived_columns(df)
    assert "ride_length_minutes" in derived.columns
    assert "day_of_week" in derived.columns
    assert "hour_of_day" in derived.columns
    assert "season" in derived.columns
    assert derived.loc[0, "ride_length_minutes"] == 12
    assert derived.loc[1, "hour_of_day"] == 9
    assert derived.loc[0, "season"] == SEASON_MAP[5]


def test_validate_dataframe_reports_expected_keys():
    df = pd.DataFrame(
        {
            "ride_id": ["id1", "id2"],
            "started_at": pd.to_datetime(["2025-05-01 08:00:00", "2025-05-01 08:05:00"]),
            "ended_at": pd.to_datetime(["2025-05-01 08:10:00", "2025-05-01 08:15:00"]),
            "member_casual": ["member", "casual"],
            "start_lat": [41.9, 41.8],
            "start_lng": [-87.6, -87.7],
            "end_lat": [41.91, 41.81],
            "end_lng": [-87.61, -87.71],
        }
    )
    df = compute_derived_columns(df)
    metrics = validate_dataframe(df)
    assert metrics["duplicate_ride_id_count"] == 0
    assert metrics["negative_ride_length_count"] == 0
    assert metrics["zero_ride_length_count"] == 0
    assert metrics["member_casual_values"] == ["casual", "member"]
    assert metrics["coordinate_bounds_valid"]["start_lat_valid"] == 1


def test_generate_data_summary_includes_expected_fields():
    csv_files = [ROOT / "May2025.csv"]
    df = pd.DataFrame(
        {
            "ride_id": ["id1"],
            "rideable_type": ["classic_bike"],
            "started_at": pd.to_datetime(["2025-05-01 08:00:00"]),
            "ended_at": pd.to_datetime(["2025-05-01 08:10:00"]),
            "start_station_name": ["Station A"],
            "start_station_id": ["CHI00001"],
            "end_station_name": ["Station B"],
            "end_station_id": ["CHI00002"],
            "start_lat": [41.9],
            "start_lng": [-87.6],
            "end_lat": [41.91],
            "end_lng": [-87.61],
            "member_casual": ["member"],
        }
    )
    summary = generate_data_summary(df, csv_files)
    assert summary["file_count"] == 1
    assert summary["row_count"] == 1
    assert summary["member_casual_distribution"]["member"] == 1


def test_phase2_prepare_main_runs_without_errors(tmp_path):
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(
        "ride_id,rideable_type,started_at,ended_at,start_station_name,start_station_id,end_station_name,end_station_id,start_lat,start_lng,end_lat,end_lng,member_casual\n"
        "id1,classic_bike,01/05/2025 08:00,01/05/2025 08:10,Station A,CHI00001,Station B,CHI00002,41.9,-87.6,41.9,-87.6,member\n"
    )
    original_root = Path.cwd()
    try:
        tmp_output = tmp_path / "analysis_output"
        tmp_output.mkdir(exist_ok=True)
        os.chdir(tmp_path)
        from phase2_prepare import main

        assert main() == 0
    finally:
        os.chdir(original_root)
