import json
from pathlib import Path

import pandas as pd
import pytest
from scipy import stats

ROOT = Path(".").resolve()


@pytest.fixture
def sample_cleaned_df():
    """Create sample cleaned data matching Phase 3 output schema."""
    return pd.DataFrame(
        {
            "ride_id": ["r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"],
            "rideable_type": ["classic_bike", "electric_bike", "classic_bike", "electric_bike", "docked_bike", "classic_bike", "electric_bike", "classic_bike"],
            "started_at": pd.to_datetime(["2025-05-01 08:00", "2025-05-01 12:15", "2025-05-02 07:30", "2025-05-02 18:45", "2025-05-05 09:00", "2025-05-06 11:30", "2025-05-06 15:00", "2025-06-01 08:00"]),
            "ended_at": pd.to_datetime(["2025-05-01 08:12", "2025-05-01 13:00", "2025-05-02 07:42", "2025-05-02 19:45", "2025-05-05 09:30", "2025-05-06 11:50", "2025-05-06 16:15", "2025-06-01 08:18"]),
            "start_station_name": ["Station A", "Station B", "Station A", "Station C", "Station D", "Station A", "Station B", "Station A"],
            "end_station_name": ["Station B", "Station A", "Station C", "Station A", "Station D", "Station B", "Station C", "Station B"],
            "member_casual": ["member", "casual", "member", "casual", "casual", "member", "casual", "member"],
            "ride_length_minutes": [12.0, 45.0, 12.0, 60.0, 30.0, 20.0, 75.0, 18.0],
            "day_of_week": [4, 4, 5, 5, 1, 2, 2, 1],
            "hour_of_day": [8, 12, 7, 18, 9, 11, 15, 8],
            "month": [5, 5, 5, 5, 5, 5, 5, 6],
            "season": ["Spring", "Spring", "Spring", "Spring", "Spring", "Spring", "Spring", "Summer"],
            "is_weekend": [False, False, True, True, True, False, False, True],
            "trip_distance_km": [0.5, 1.2, 0.8, 1.5, 0.3, 0.6, 1.0, 0.4],
            "is_round_trip": [False, False, False, False, True, False, False, False],
        }
    )


# ============================================================================
# DESCRIPTIVE STATISTICS TESTS
# ============================================================================

def test_compute_overall_summary_returns_dict(sample_cleaned_df):
    """Test that overall summary computation returns a dictionary with required keys."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import compute_overall_summary

    result = compute_overall_summary(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "total_trips" in result
    assert "date_range_min" in result
    assert "date_range_max" in result
    assert "unique_start_stations" in result


def test_compute_ride_duration_stats_members_vs_casuals(sample_cleaned_df):
    """Test ride duration statistics are computed for members and casuals separately."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import compute_ride_duration_stats

    result = compute_ride_duration_stats(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "member" in result
    assert "casual" in result
    assert result["member"]["mean"] > 0
    assert result["casual"]["mean"] > 0
    # Casuals should have higher average duration
    assert result["casual"]["mean"] > result["member"]["mean"]


def test_ride_duration_stats_include_percentiles(sample_cleaned_df):
    """Test that 95th percentile is included in duration stats."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import compute_ride_duration_stats

    result = compute_ride_duration_stats(sample_cleaned_df)
    
    assert "percentile_95" in result["member"]
    assert "percentile_95" in result["casual"]


# ============================================================================
# COMPARATIVE ANALYSIS TESTS
# ============================================================================

def test_day_of_week_analysis_by_member_type(sample_cleaned_df):
    """Test day-of-week analysis produces aggregations by member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import analyze_day_of_week

    result = analyze_day_of_week(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "trip_count_by_day" in result
    assert "avg_duration_by_day" in result
    # Should have rows for each day represented in sample
    assert len(result["trip_count_by_day"]) > 0


def test_hour_of_day_analysis_identifies_peaks(sample_cleaned_df):
    """Test hour-of-day analysis identifies peak hours for members vs casuals."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import analyze_hour_of_day

    result = analyze_hour_of_day(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "trip_count_by_hour" in result
    assert "peak_hours_member" in result
    assert "peak_hours_casual" in result


def test_seasonal_analysis_computes_monthly_trends(sample_cleaned_df):
    """Test seasonal/monthly analysis computes trends by member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import analyze_seasonal

    result = analyze_seasonal(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "trip_count_by_month" in result
    assert "avg_duration_by_month" in result


def test_bike_type_analysis_by_member_casual(sample_cleaned_df):
    """Test bike type preference analysis by member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import analyze_bike_type

    result = analyze_bike_type(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "rideable_type_distribution" in result
    assert "member" in result["rideable_type_distribution"]
    assert "casual" in result["rideable_type_distribution"]


def test_geographic_analysis_identifies_top_stations(sample_cleaned_df):
    """Test geographic analysis identifies top start/end stations."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import analyze_geographic

    result = analyze_geographic(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "top_start_stations" in result
    assert "top_end_stations" in result
    assert "round_trip_ratio" in result
    assert "avg_trip_distance" in result


# ============================================================================
# STATISTICAL TESTING TESTS
# ============================================================================

def test_two_sample_t_test_ride_length(sample_cleaned_df):
    """Test two-sample t-test for ride length differences."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import statistical_t_test_ride_length

    result = statistical_t_test_ride_length(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "t_statistic" in result
    assert "p_value" in result
    assert "cohens_d" in result
    assert "ci_95" in result


def test_chi_square_member_casual_day_of_week(sample_cleaned_df):
    """Test chi-square test for independence of member type and day of week."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import statistical_chi_square_day_of_week

    result = statistical_chi_square_day_of_week(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "chi2_statistic" in result
    assert "p_value" in result


def test_chi_square_member_casual_bike_type(sample_cleaned_df):
    """Test chi-square test for independence of member type and bike type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import statistical_chi_square_bike_type

    result = statistical_chi_square_bike_type(sample_cleaned_df)
    
    assert isinstance(result, dict)
    assert "chi2_statistic" in result
    assert "p_value" in result


# ============================================================================
# PIVOT TABLE TESTS
# ============================================================================

def test_pivot_duration_by_day(sample_cleaned_df):
    """Test pivot table: avg ride duration by day of week and member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import pivot_duration_by_day

    result = pivot_duration_by_day(sample_cleaned_df)
    
    assert isinstance(result, pd.DataFrame)
    assert "member" in result.columns or isinstance(result.index, pd.MultiIndex)


def test_pivot_volume_by_day(sample_cleaned_df):
    """Test pivot table: trip count by day of week and member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import pivot_volume_by_day

    result = pivot_volume_by_day(sample_cleaned_df)
    
    assert isinstance(result, pd.DataFrame)
    assert result.sum().sum() == len(sample_cleaned_df)


def test_pivot_duration_by_hour(sample_cleaned_df):
    """Test pivot table: avg ride duration by hour of day and member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import pivot_duration_by_hour

    result = pivot_duration_by_hour(sample_cleaned_df)
    
    assert isinstance(result, pd.DataFrame)


def test_pivot_bike_type_mix(sample_cleaned_df):
    """Test pivot table: bike type distribution by member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import pivot_bike_type_mix

    result = pivot_bike_type_mix(sample_cleaned_df)
    
    assert isinstance(result, pd.DataFrame)
    assert result.sum().sum() == len(sample_cleaned_df)


def test_pivot_monthly_trends(sample_cleaned_df):
    """Test pivot table: monthly trip counts and durations by member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import pivot_monthly_trends

    result = pivot_monthly_trends(sample_cleaned_df)
    
    assert isinstance(result, pd.DataFrame)


def test_pivot_top_stations(sample_cleaned_df):
    """Test pivot table: top start stations by member type."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import pivot_top_start_stations

    result = pivot_top_start_stations(sample_cleaned_df)
    
    assert isinstance(result, pd.DataFrame)
    # Should have station names in index and member_casual columns
    assert len(result) > 0


# ============================================================================
# FULL ANALYSIS PIPELINE TESTS
# ============================================================================

def test_full_analysis_pipeline_returns_complete_results(sample_cleaned_df):
    """Test that the full analysis pipeline returns all expected analysis components."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import run_full_analysis

    results = run_full_analysis(sample_cleaned_df)
    
    assert isinstance(results, dict)
    assert "overall_summary" in results
    assert "ride_duration_stats" in results
    assert "day_of_week_analysis" in results
    assert "hour_of_day_analysis" in results
    assert "seasonal_analysis" in results
    assert "bike_type_analysis" in results
    assert "geographic_analysis" in results
    assert "statistical_tests" in results
    assert "pivot_tables" in results


def test_analysis_results_serializable_to_json(sample_cleaned_df):
    """Test that analysis results can be serialized to JSON for reporting."""
    pytest.importorskip("phase4_analyze")
    from phase4_analyze import run_full_analysis

    results = run_full_analysis(sample_cleaned_df)
    
    # Should be serializable to JSON (may need conversion for DataFrames)
    try:
        json_str = json.dumps(results, default=str)
        assert isinstance(json_str, str)
    except TypeError:
        pytest.fail("Results should be JSON-serializable")
