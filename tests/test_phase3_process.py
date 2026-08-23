import json
from pathlib import Path

import pandas as pd
import pytest

from phase3_process import (
    PHASE3_CHICAGO_BOUNDS,
    compute_phase3_features,
    compute_trip_distance_km,
    compute_is_round_trip,
    normalize_station_names,
    parse_mixed_datetimes,
    process_dataframe,
    remove_invalid_trips,
    validate_phase3_dataframe,
)

ROOT = Path(".").resolve()


def test_parse_mixed_datetimes_parses_varied_formats():
    df = pd.DataFrame(
        {
            "started_at": ["30/04/2025 2:18 am", "29/06/2025 23:20"],
            "ended_at": ["01/05/2025 3:18 am", "01/07/2025 0:20"],
        }
    )
    parsed = parse_mixed_datetimes(df)
    assert pd.api.types.is_datetime64_any_dtype(parsed["started_at"])
    assert pd.api.types.is_datetime64_any_dtype(parsed["ended_at"])
    assert parsed.loc[0, "started_at"].hour == 2
    assert parsed.loc[1, "ended_at"].hour == 0


def test_normalize_station_names_title_cases():
    df = pd.DataFrame(
        {
            "start_station_name": [" station a ", None, "MAIN st"],
            "end_station_name": ["END ST", "North ave", None],
        }
    )
    normalized = normalize_station_names(df)
    assert normalized.loc[0, "start_station_name"] == "Station A"
    assert normalized.loc[1, "end_station_name"] == "North Ave"
    assert pd.isna(normalized.loc[2, "end_station_name"])


def test_compute_trip_distance_km_returns_realistic_distance():
    df = pd.DataFrame(
        {
            "start_lat": [41.8781],
            "start_lng": [-87.6298],
            "end_lat": [41.8810],
            "end_lng": [-87.6270],
        }
    )
    distances = compute_trip_distance_km(df)
    assert distances.iloc[0] == pytest.approx(0.4, rel=0.1)


def test_compute_is_round_trip_by_station_name():
    df = pd.DataFrame(
        {
            "start_station_name": ["Loop Station", "North Ave"],
            "end_station_name": ["loop station", "Michigan Ave"],
            "start_lat": [41.88, 41.89],
            "start_lng": [-87.63, -87.62],
            "end_lat": [41.88, 41.89],
            "end_lng": [-87.63, -87.62],
        }
    )
    result = compute_is_round_trip(df)
    assert bool(result.iloc[0]) is True
    assert bool(result.iloc[1]) is True


def test_remove_invalid_trips_filters_bad_data():
    df = pd.DataFrame(
        {
            "ride_id": ["a", "b", "c", "d", "e", "f"],
            "rideable_type": ["classic_bike"] * 6,
            "started_at": ["01/05/2025 08:00", "01/05/2025 08:00", "01/05/2025 08:00", "01/05/2025 08:00", "01/05/2025 08:00", "01/05/2025 08:00"],
            "ended_at": ["01/05/2025 07:59", "01/05/2025 08:00", "01/05/2025 08:00", "01/05/2025 09:00", "01/05/2025 08:00", "01/05/2025 08:30"],
            "member_casual": ["member", "member", None, "casual", "", "casual"],
            "start_lat": [41.88, 41.88, 41.88, 41.88, None, 41.88],
            "start_lng": [-87.63, -87.63, -87.63, -87.63, -87.63, -87.63],
            "end_lat": [41.88, 41.88, 41.88, 41.88, 41.88, 41.88],
            "end_lng": [-87.63, -87.63, -87.63, -87.63, -87.63, -87.63],
        }
    )
    cleaned, removals = remove_invalid_trips(df)
    assert removals["removed_null_member_casual"] == 2
    assert removals["removed_invalid_dates"] == 0
    assert removals["removed_negative_duration"] == 1
    assert removals["removed_zero_duration"] == 3
    assert removals["removed_out_of_bounds_start"] == 0
    assert removals["removed_out_of_bounds_end"] == 0
    assert removals["removed_duplicate_ride_ids"] == 0
    assert len(cleaned) == 2


def test_validate_phase3_dataframe_reports_expected_metrics():
    df = pd.DataFrame(
        {
            "ride_id": ["a", "a", "b"],
            "started_at": pd.to_datetime(["2025-05-01 08:00", "2025-05-01 08:00", "2025-05-01 08:00"]),
            "ended_at": pd.to_datetime(["2025-05-01 08:10", "2025-05-01 08:10", "2025-05-01 07:50"]),
            "member_casual": ["member", "member", "casual"],
            "start_lat": [41.88, 41.88, 41.88],
            "start_lng": [-87.63, -87.63, -87.63],
            "end_lat": [41.88, 41.88, 41.88],
            "end_lng": [-87.63, -87.63, -87.63],
        }
    )
    metrics = validate_phase3_dataframe(df)
    assert metrics["duplicate_ride_id_count"] == 1
    assert metrics["invalid_date_ranges"] == 1
    assert metrics["out_of_bounds_start"] == 0
    assert metrics["out_of_bounds_end"] == 0
    assert metrics["data_completeness_score"] == 100.0


def test_process_dataframe_produces_cleaned_output():
    df = pd.DataFrame(
        {
            "ride_id": ["x", "y", "z"],
            "rideable_type": ["classic_bike", "electric_bike", "classic_bike"],
            "started_at": ["01/05/2025 08:00", "01/05/2025 08:00", "01/05/2025 08:00"],
            "ended_at": ["01/05/2025 08:10", "01/05/2025 08:10", "01/05/2025 08:20"],
            "member_casual": ["Member", "casual", "member"],
            "start_lat": [41.88, 41.88, 41.88],
            "start_lng": [-87.63, -87.63, -87.63],
            "end_lat": [41.88, 41.88, 41.88],
            "end_lng": [-87.63, -87.63, -87.63],
            "start_station_name": ["Start A", "Start B", "Start C"],
            "end_station_name": ["Start A", "End B", "End C"],
        }
    )
    cleaned, metrics = process_dataframe(df)
    assert "ride_length_minutes" in cleaned.columns
    assert "trip_distance_km" in cleaned.columns
    assert cleaned["member_casual"].tolist() == ["member", "casual", "member"]
    assert metrics["removed_negative_duration"] == 0

