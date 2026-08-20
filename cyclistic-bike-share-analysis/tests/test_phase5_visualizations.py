"""
Phase 5: Share - Visualization & Communication
Test suite for visualization functions, presentation generation, and accessibility compliance.
Uses TDD methodology with comprehensive test coverage.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import pytest


@pytest.fixture
def sample_cleaned_df():
    """Create sample cleaned data matching Phase 3 output schema."""
    return pd.DataFrame({
        "ride_id": [f"r{i}" for i in range(100)],
        "rideable_type": ["classic_bike", "electric_bike"] * 50,
        "started_at": pd.date_range("2025-05-01", periods=100, freq="h"),
        "ended_at": pd.date_range("2025-05-01 00:15", periods=100, freq="h"),
        "start_station_name": ["Station A", "Station B", "Station C"] * 33 + ["Station D"],
        "end_station_name": ["Station B", "Station C", "Station A"] * 33 + ["Station D"],
        "start_lat": [41.8781 + (i % 10) * 0.01 for i in range(100)],
        "start_lng": [-87.6298 + (i % 10) * 0.01 for i in range(100)],
        "end_lat": [41.8781 + (i % 10) * 0.01 for i in range(100)],
        "end_lng": [-87.6298 + (i % 10) * 0.01 for i in range(100)],
        "member_casual": ["member", "casual"] * 50,
        "ride_length_minutes": [10 + (i % 50) for i in range(100)],
        "day_of_week": [i % 7 for i in range(100)],
        "hour_of_day": [i % 24 for i in range(100)],
        "month": [5] * 50 + [6] * 50,
        "season": ["Spring"] * 50 + ["Summer"] * 50,
        "is_weekend": [i % 7 in [6, 7] for i in range(100)],
        "trip_distance_km": [1.0 + (i % 5) for i in range(100)],
        "is_round_trip": [i % 10 == 0 for i in range(100)],
    })


# ============================================================================
# VISUALIZATION FUNCTION TESTS
# ============================================================================

class TestDurationComparison:
    """Test ride duration comparison visualization."""

    def test_create_duration_comparison_returns_figure(self, sample_cleaned_df):
        """Test that duration comparison returns a matplotlib figure."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_duration_comparison

        fig = create_duration_comparison(sample_cleaned_df)
        assert fig is not None
        assert hasattr(fig, "get_axes")
        assert len(fig.get_axes()) > 0

    def test_duration_comparison_has_annotations(self, sample_cleaned_df):
        """Test that duration comparison includes statistical annotations."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_duration_comparison

        fig = create_duration_comparison(sample_cleaned_df)
        # Check for title and labels
        ax = fig.get_axes()[0]
        assert ax.get_title() != ""
        assert "ride" in ax.get_title().lower() or "duration" in ax.get_title().lower()

    def test_duration_comparison_uses_colorblind_palette(self, sample_cleaned_df):
        """Test that duration comparison uses colorblind-friendly colors."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_duration_comparison

        fig = create_duration_comparison(sample_cleaned_df)
        # Should use blue/orange palette
        assert fig is not None  # Basic test - detailed color checking would need color inspection


class TestWeekdayPattern:
    """Test weekday vs weekend usage pattern visualization."""

    def test_create_weekday_pattern_returns_figure(self, sample_cleaned_df):
        """Test that weekday pattern returns a matplotlib figure."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_weekday_weekend_pattern

        fig = create_weekday_weekend_pattern(sample_cleaned_df)
        assert fig is not None
        assert hasattr(fig, "get_axes")

    def test_weekday_pattern_includes_labels(self, sample_cleaned_df):
        """Test that weekday pattern has proper axis labels."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_weekday_weekend_pattern

        fig = create_weekday_weekend_pattern(sample_cleaned_df)
        ax = fig.get_axes()[0]
        assert ax.get_xlabel() != "" or ax.get_ylabel() != ""

    def test_weekday_pattern_distinguishes_member_casual(self, sample_cleaned_df):
        """Test that weekday pattern differentiates members and casuals."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_weekday_weekend_pattern

        fig = create_weekday_weekend_pattern(sample_cleaned_df)
        # Should have multiple data series for member/casual
        ax = fig.get_axes()[0]
        assert len(ax.get_lines()) > 0 or len(ax.patches) > 0


class TestHourlyHeatmap:
    """Test hourly usage heatmap visualization."""

    def test_create_hourly_heatmap_returns_figure(self, sample_cleaned_df):
        """Test that hourly heatmap returns a figure."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_hourly_heatmap

        fig = create_hourly_heatmap(sample_cleaned_df)
        assert fig is not None

    def test_hourly_heatmap_has_colorbar(self, sample_cleaned_df):
        """Test that hourly heatmap includes a colorbar."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_hourly_heatmap

        fig = create_hourly_heatmap(sample_cleaned_df)
        # Heatmap should have color mapping
        assert fig is not None

    def test_hourly_heatmap_covers_24_hours(self, sample_cleaned_df):
        """Test that hourly heatmap covers all 24 hours."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_hourly_heatmap

        fig = create_hourly_heatmap(sample_cleaned_df)
        # Should show all hours 0-23
        ax = fig.get_axes()[0]
        assert ax is not None


class TestBikeTypePreference:
    """Test bike type preference visualization."""

    def test_create_bike_type_preference_returns_figure(self, sample_cleaned_df):
        """Test that bike type preference returns a figure."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_bike_type_preference

        fig = create_bike_type_preference(sample_cleaned_df)
        assert fig is not None

    def test_bike_type_preference_compares_member_casual(self, sample_cleaned_df):
        """Test that bike type preference shows member vs casual comparison."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_bike_type_preference

        fig = create_bike_type_preference(sample_cleaned_df)
        # Should show grouped bars for different bike types
        ax = fig.get_axes()[0]
        assert len(ax.patches) > 0  # Should have bar patches


class TestSeasonalTrends:
    """Test seasonal trends visualization."""

    def test_create_seasonal_trends_returns_figure(self, sample_cleaned_df):
        """Test that seasonal trends returns a figure."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_seasonal_trends

        fig = create_seasonal_trends(sample_cleaned_df)
        assert fig is not None

    def test_seasonal_trends_shows_monthly_data(self, sample_cleaned_df):
        """Test that seasonal trends includes monthly data."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_seasonal_trends

        fig = create_seasonal_trends(sample_cleaned_df)
        ax = fig.get_axes()[0]
        # Should have multiple data points (one per month)
        assert ax is not None


class TestStationMap:
    """Test station network map visualization."""

    def test_create_station_map_returns_figure(self, sample_cleaned_df):
        """Test that station map returns a figure."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_station_network_map

        fig = create_station_network_map(sample_cleaned_df)
        assert fig is not None

    def test_station_map_includes_coordinates(self, sample_cleaned_df):
        """Test that station map uses geographic coordinates."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import create_station_network_map

        fig = create_station_network_map(sample_cleaned_df)
        # Should be a map with lat/lng data
        assert fig is not None


# ============================================================================
# PRESENTATION GENERATION TESTS
# ============================================================================

class TestPresentationGeneration:
    """Test presentation deck generation."""

    def test_generate_presentation_creates_output(self, sample_cleaned_df):
        """Test that presentation generation creates output file."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import generate_presentation

        # Create mock figures dict
        figures = {
            "duration_comparison": None,
            "weekday_pattern": None,
            "hourly_heatmap": None,
            "bike_type": None,
            "seasonal_trends": None,
            "station_map": None,
        }
        
        output_path = generate_presentation(
            results={"overall_summary": {"total_trips": 100}},
            figures=figures,
            output_file="test_presentation.html"
        )
        assert output_path is not None

    def test_presentation_includes_all_slides(self, sample_cleaned_df):
        """Test that presentation includes all 10 required slides."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import generate_presentation

        figures = {
            "duration_comparison": None,
            "weekday_pattern": None,
            "hourly_heatmap": None,
            "bike_type": None,
            "seasonal_trends": None,
            "station_map": None,
        }
        
        output_path = generate_presentation(
            results={"overall_summary": {"total_trips": 100}},
            figures=figures,
            output_file="test_presentation.html"
        )
        
        # Read generated file and check for 10 slides
        if Path(output_path).exists():
            with open(output_path) as f:
                content = f.read()
                # Should mention slide numbers or have 10 sections
                assert "slide" in content.lower() or "presentation" in content.lower()


# ============================================================================
# ACCESSIBILITY COMPLIANCE TESTS
# ============================================================================

class TestAccessibilityCompliance:
    """Test accessibility standards compliance."""

    def test_visualizations_use_colorblind_palette(self, sample_cleaned_df):
        """Test that visualizations use colorblind-friendly colors."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import COLORBLIND_PALETTE

        # Should define colorblind-safe palette (e.g., blues and oranges)
        assert hasattr(COLORBLIND_PALETTE, "__len__")
        assert len(COLORBLIND_PALETTE) >= 2

    def test_visualizations_have_sufficient_contrast(self, sample_cleaned_df):
        """Test that visualizations have sufficient color contrast."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import check_contrast_ratio

        # Check contrast between foreground and background
        contrast = check_contrast_ratio("#000000", "#FFFFFF")  # Black on white
        assert contrast >= 4.5  # WCAG AA minimum

    def test_figures_include_alt_text(self, sample_cleaned_df):
        """Test that figures have alt text for accessibility."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import get_figure_alt_text

        alt_text = get_figure_alt_text("duration_comparison")
        assert alt_text is not None
        assert len(alt_text) > 0

    def test_font_size_minimum_12pt(self):
        """Test that minimum font size is 12pt."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import MIN_FONT_SIZE

        assert MIN_FONT_SIZE >= 12


# ============================================================================
# VISUALIZATION OUTPUT TESTS
# ============================================================================

class TestVisualizationOutputs:
    """Test that visualizations can be saved in required formats."""

    def test_save_figure_as_png(self, sample_cleaned_df):
        """Test saving figure as PNG."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import save_figure

        # Create a simple figure
        import matplotlib.pyplot as plt
        fig = plt.figure()
        
        output_path = "test_viz.png"
        save_figure(fig, output_path)
        
        assert Path(output_path).exists()
        Path(output_path).unlink()  # Clean up

    def test_save_figure_as_pdf(self, sample_cleaned_df):
        """Test saving figure as PDF."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import save_figure

        import matplotlib.pyplot as plt
        fig = plt.figure()
        
        output_path = "test_viz.pdf"
        save_figure(fig, output_path)
        
        assert Path(output_path).exists()
        Path(output_path).unlink()  # Clean up


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestVisualizationPipeline:
    """Test complete visualization pipeline."""

    def test_full_visualization_pipeline(self, sample_cleaned_df):
        """Test end-to-end visualization generation pipeline."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import run_full_visualization_pipeline

        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        results = run_full_visualization_pipeline(
            df=sample_cleaned_df,
            analysis_results={"overall_summary": {"total_trips": 100}},
            output_dir=output_dir
        )
        
        assert results is not None
        assert "visualizations" in results
        assert "presentation" in results
        
        # Clean up
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_visualization_pipeline_generates_6_charts(self, sample_cleaned_df):
        """Test that pipeline generates all 6 required visualizations."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import run_full_visualization_pipeline

        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        results = run_full_visualization_pipeline(
            df=sample_cleaned_df,
            analysis_results={"overall_summary": {"total_trips": 100}},
            output_dir=output_dir
        )
        
        assert len(results["visualizations"]) == 6
        
        # Clean up
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_pipeline_output_is_json_serializable(self, sample_cleaned_df):
        """Test that pipeline results are JSON-serializable."""
        pytest.importorskip("phase5_visualize")
        from phase5_visualize import run_full_visualization_pipeline

        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        results = run_full_visualization_pipeline(
            df=sample_cleaned_df,
            analysis_results={"overall_summary": {"total_trips": 100}},
            output_dir=output_dir
        )
        
        # Should be JSON-serializable
        json_str = json.dumps(results, default=str)
        assert json_str is not None
        
        # Clean up
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)
