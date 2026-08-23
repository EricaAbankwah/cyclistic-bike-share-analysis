"""
Phase 6: Act – TDD Test Suite
Covers: recommendations, KPI framework, implementation roadmap,
executive summary, portfolio case study, final report, full pipeline.
"""
import json
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def analysis_results():
    return {
        "overall_summary": {
            "total_trips": 5475207,
            "member_casual_split": {"member": 3532594, "casual": 1942613},
            "bike_type_distribution": {"electric_bike": 3580537, "classic_bike": 1894670},
            "unique_start_stations": 1809,
            "date_range_min": "2025-04-30",
            "date_range_max": "2026-04-30",
        },
        "ride_duration_stats": {
            "member": {"mean": 12.54, "median": 9.0, "std_dev": 32.83, "count": 3532594},
            "casual": {"mean": 22.94, "median": 12.0, "std_dev": 81.88, "count": 1942613},
        },
        "statistical_tests": {
            "ride_length_ttest": {"t_statistic": -209.96, "p_value": 0.0, "cohens_d": -0.19},
            "chi_square_day_of_week": {"chi2_statistic": 144895.1, "p_value": 0.0, "degrees_of_freedom": 6},
            "chi_square_bike_type": {"chi2_statistic": 1950.8, "p_value": 0.0, "degrees_of_freedom": 1},
        },
        "day_of_week_analysis": {
            "weekday_ratio": {"member": 0.77, "casual": 0.63},
        },
        "bike_type_analysis": {
            "rideable_type_pct": {
                "casual": {"electric_bike": 66.6, "classic_bike": 33.4},
                "member": {"electric_bike": 64.7, "classic_bike": 35.3},
            }
        },
        "geographic_analysis": {
            "top_start_stations": {"Navy Pier": 42567, "Millennium Park": 27287},
            "round_trip_ratio": {"member": 0.031, "casual": 0.084},
        },
        "seasonal_analysis": {
            "trip_count_by_season": {
                "casual": {"Summer": 911195, "Fall": 558885, "Spring": 383091, "Winter": 89442},
                "member": {"Summer": 1238638, "Fall": 1088555, "Spring": 834144, "Winter": 371257},
            }
        },
    }


# ── 1. RECOMMENDATIONS ────────────────────────────────────────────────────

class TestRecommendationsEngine:

    def test_returns_three_recommendations(self, analysis_results):
        from phase6_act import generate_recommendations
        recs = generate_recommendations(analysis_results)
        assert len(recs) == 3

    def test_each_recommendation_has_required_keys(self, analysis_results):
        from phase6_act import generate_recommendations
        required = {"id", "title", "insight", "action", "target_audience",
                    "channels", "expected_impact", "success_metric", "kpi_target"}
        for rec in generate_recommendations(analysis_results):
            assert required.issubset(rec.keys())

    def test_recommendation_ids_are_unique(self, analysis_results):
        from phase6_act import generate_recommendations
        ids = [r["id"] for r in generate_recommendations(analysis_results)]
        assert len(ids) == len(set(ids))

    def test_recommendations_are_data_backed(self, analysis_results):
        from phase6_act import generate_recommendations
        for rec in generate_recommendations(analysis_results):
            assert len(rec["insight"]) > 20
            assert len(rec["action"]) > 20


# ── 2. KPI FRAMEWORK ─────────────────────────────────────────────────────

class TestKPIFramework:

    def test_returns_dict_with_five_or_more_kpis(self, analysis_results):
        from phase6_act import build_kpi_framework
        kpis = build_kpi_framework(analysis_results)
        assert isinstance(kpis, dict)
        assert len(kpis) >= 5

    def test_each_kpi_has_target_frequency_source(self, analysis_results):
        from phase6_act import build_kpi_framework
        for name, kpi in build_kpi_framework(analysis_results).items():
            assert "target" in kpi, f"KPI '{name}' missing target"
            assert "measurement_frequency" in kpi
            assert "data_source" in kpi

    def test_conversion_rate_target_is_realistic(self, analysis_results):
        from phase6_act import build_kpi_framework
        kpis = build_kpi_framework(analysis_results)
        assert "conversion_rate" in kpis
        assert 5 <= kpis["conversion_rate"]["target"] <= 20


# ── 3. IMPLEMENTATION ROADMAP ─────────────────────────────────────────────

class TestImplementationRoadmap:

    def test_returns_five_phases(self, analysis_results):
        from phase6_act import build_implementation_roadmap
        roadmap = build_implementation_roadmap(analysis_results)
        assert isinstance(roadmap, list)
        assert len(roadmap) == 5

    def test_each_phase_has_required_fields(self, analysis_results):
        from phase6_act import build_implementation_roadmap
        required = {"phase", "timeline", "activities", "owner", "success_metric"}
        for phase in build_implementation_roadmap(analysis_results):
            assert required.issubset(phase.keys())

    def test_phases_are_sequential(self, analysis_results):
        from phase6_act import build_implementation_roadmap
        phases = [p["phase"] for p in build_implementation_roadmap(analysis_results)]
        assert phases == sorted(phases)


# ── 4. EXECUTIVE SUMMARY ─────────────────────────────────────────────────

class TestExecutiveSummary:

    def test_returns_dict_with_required_sections(self, analysis_results):
        from phase6_act import generate_executive_summary
        summary = generate_executive_summary(analysis_results)
        required = {"business_task", "key_findings", "recommendations",
                    "expected_roi", "next_steps"}
        assert required.issubset(summary.keys())

    def test_has_three_or_more_key_findings(self, analysis_results):
        from phase6_act import generate_executive_summary
        summary = generate_executive_summary(analysis_results)
        assert len(summary["key_findings"]) >= 3

    def test_expected_roi_is_positive(self, analysis_results):
        from phase6_act import generate_executive_summary
        assert generate_executive_summary(analysis_results)["expected_roi"] > 0


# ── 5. PORTFOLIO CASE STUDY ───────────────────────────────────────────────

class TestPortfolioCaseStudy:

    def test_creates_html_file(self, tmp_path, analysis_results):
        from phase6_act import generate_recommendations, generate_executive_summary, generate_portfolio_case_study
        out = generate_portfolio_case_study(
            generate_executive_summary(analysis_results),
            generate_recommendations(analysis_results),
            tmp_path
        )
        assert Path(out).exists() and out.endswith(".html")

    def test_contains_all_recommendation_titles(self, tmp_path, analysis_results):
        from phase6_act import generate_recommendations, generate_executive_summary, generate_portfolio_case_study
        recs = generate_recommendations(analysis_results)
        out = generate_portfolio_case_study(
            generate_executive_summary(analysis_results), recs, tmp_path)
        content = Path(out).read_text(encoding="utf-8")
        for rec in recs:
            assert rec["title"] in content

    def test_contains_total_trip_count(self, tmp_path, analysis_results):
        from phase6_act import generate_recommendations, generate_executive_summary, generate_portfolio_case_study
        out = generate_portfolio_case_study(
            generate_executive_summary(analysis_results),
            generate_recommendations(analysis_results),
            tmp_path
        )
        content = Path(out).read_text(encoding="utf-8")
        assert "5,475,207" in content or "5475207" in content


# ── 6. FINAL REPORT ───────────────────────────────────────────────────────

class TestFinalReport:

    def test_creates_html_file(self, tmp_path, analysis_results):
        from phase6_act import generate_final_report
        out = generate_final_report(analysis_results, tmp_path)
        assert Path(out).exists() and out.endswith(".html")

    def test_contains_all_six_phases(self, tmp_path, analysis_results):
        from phase6_act import generate_final_report
        content = Path(generate_final_report(analysis_results, tmp_path)).read_text(encoding="utf-8")
        for phase in ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6"]:
            assert phase in content

    def test_contains_statistical_results(self, tmp_path, analysis_results):
        from phase6_act import generate_final_report
        content = Path(generate_final_report(analysis_results, tmp_path)).read_text(encoding="utf-8")
        assert "p-value" in content.lower() or "p_value" in content.lower()

    def test_file_is_valid_utf8(self, tmp_path, analysis_results):
        from phase6_act import generate_final_report
        Path(generate_final_report(analysis_results, tmp_path)).read_text(encoding="utf-8")


# ── 7. FULL PIPELINE ─────────────────────────────────────────────────────

class TestPhase6Pipeline:

    def test_pipeline_returns_dict_with_all_keys(self, tmp_path, analysis_results):
        from phase6_act import run_phase6_pipeline
        result = run_phase6_pipeline(analysis_results, tmp_path)
        required = {"recommendations", "kpi_framework", "implementation_roadmap",
                    "executive_summary", "portfolio_case_study", "final_report"}
        assert required.issubset(result.keys())

    def test_pipeline_output_files_exist(self, tmp_path, analysis_results):
        from phase6_act import run_phase6_pipeline
        result = run_phase6_pipeline(analysis_results, tmp_path)
        assert Path(result["portfolio_case_study"]).exists()
        assert Path(result["final_report"]).exists()

    def test_pipeline_result_is_json_serializable(self, tmp_path, analysis_results):
        from phase6_act import run_phase6_pipeline
        result = run_phase6_pipeline(analysis_results, tmp_path)
        serializable = {k: str(v) if isinstance(v, Path) else v for k, v in result.items()}
        json.dumps(serializable)
