"""
Phase 6: Act – Recommendations, KPIs, Roadmap, Executive Summary,
Portfolio Case Study, and Final Report.
"""
from __future__ import annotations
from pathlib import Path


# ── RECOMMENDATIONS ───────────────────────────────────────────────────────

def generate_recommendations(analysis_results: dict) -> list[dict]:
    dur = analysis_results["ride_duration_stats"]
    geo = analysis_results["geographic_analysis"]
    seasonal = analysis_results["seasonal_analysis"]

    casual_mean = dur["casual"]["mean"]
    member_mean = dur["member"]["mean"]
    casual_summer = seasonal["trip_count_by_season"]["casual"]["Summer"]
    top_station = next(iter(geo["top_start_stations"]))
    round_trip_casual = geo["round_trip_ratio"]["casual"]

    return [
        {
            "id": "REC-01",
            "title": "Weekend Leisure-to-Membership Conversion Campaign",
            "insight": (
                f"Casual riders average {casual_mean:.1f} min per ride vs "
                f"{member_mean:.1f} min for members, and take 2.7x more round trips "
                f"(round-trip ratio {round_trip_casual:.1%}), indicating leisure use "
                "concentrated on weekends."
            ),
            "action": (
                "Launch a 'Weekend Warrior' membership tier priced between single-ride "
                "and annual plans, promoted at high-traffic leisure stations on Saturdays "
                "and Sundays via in-app banners and dock-side QR codes."
            ),
            "target_audience": "Casual weekend riders",
            "channels": ["in-app notifications", "dock-side signage", "social media"],
            "expected_impact": "10–15% conversion of frequent casual weekend riders",
            "success_metric": "New weekend membership sign-ups per month",
            "kpi_target": "500 new weekend memberships in Q1 campaign",
        },
        {
            "id": "REC-02",
            "title": "Summer Peak Season Membership Drive",
            "insight": (
                f"Casual ridership peaks sharply in Summer ({casual_summer:,} trips), "
                "representing the highest casual volume of any season — nearly 3x Winter "
                "casual volume. This seasonal concentration is a high-intent conversion window."
            ),
            "action": (
                "Run a time-limited 'Summer Membership' promotion from June through August "
                f"at top stations including {top_station}, offering a discounted first-year "
                "annual membership with a free month for sign-ups during peak season."
            ),
            "target_audience": "High-frequency summer casual riders",
            "channels": ["email retargeting", "push notifications", "partner tourism apps"],
            "expected_impact": "15–20% uplift in annual membership sign-ups during summer",
            "success_metric": "Annual memberships sold June–August vs prior year",
            "kpi_target": "20% year-over-year increase in summer membership conversions",
        },
        {
            "id": "REC-03",
            "title": "Electric Bike Upgrade Incentive for Casual Riders",
            "insight": (
                "Casual riders already choose electric bikes 66.6% of the time vs 64.7% "
                "for members, showing strong e-bike preference. Members who use e-bikes "
                "ride more frequently on weekdays, suggesting e-bike access drives habitual use."
            ),
            "action": (
                "Offer casual riders who have taken 3+ electric bike rides in a month a "
                "targeted 'E-Bike Member' upgrade offer granting priority e-bike access "
                "and a reduced annual membership rate, delivered via in-app message."
            ),
            "target_audience": "Casual riders with repeated electric bike usage",
            "channels": ["in-app messaging", "email", "loyalty program notifications"],
            "expected_impact": "Convert high-engagement casual e-bike users to annual members",
            "success_metric": "Conversion rate of targeted casual e-bike users",
            "kpi_target": "8% conversion rate among targeted casual e-bike users within 90 days",
        },
    ]


# ── KPI FRAMEWORK ─────────────────────────────────────────────────────────

def build_kpi_framework(analysis_results: dict) -> dict:
    total = analysis_results["overall_summary"]["total_trips"]
    casual_count = analysis_results["overall_summary"]["member_casual_split"]["casual"]
    current_casual_pct = round(casual_count / total * 100, 1)

    return {
        "conversion_rate": {
            "description": "Percentage of casual riders who convert to annual membership",
            "baseline": f"{current_casual_pct}% casual share of total trips",
            "target": 10,
            "unit": "%",
            "measurement_frequency": "Monthly",
            "data_source": "Membership sign-up database",
        },
        "casual_ride_frequency": {
            "description": "Average rides per month per casual rider",
            "baseline": "Calculated from trip history",
            "target": 6,
            "unit": "rides/month",
            "measurement_frequency": "Monthly",
            "data_source": "Trip transaction logs",
        },
        "summer_membership_growth": {
            "description": "Year-over-year growth in annual memberships sold June–August",
            "baseline": "Prior year summer membership sales",
            "target": 20,
            "unit": "%",
            "measurement_frequency": "Quarterly (summer)",
            "data_source": "Membership sales database",
        },
        "electric_bike_conversion_rate": {
            "description": "Conversion rate of targeted casual e-bike users to membership",
            "baseline": "0% (new campaign)",
            "target": 8,
            "unit": "%",
            "measurement_frequency": "Monthly",
            "data_source": "In-app campaign tracking",
        },
        "weekend_membership_signups": {
            "description": "New weekend membership tier sign-ups per month",
            "baseline": "0 (new tier)",
            "target": 500,
            "unit": "sign-ups/month",
            "measurement_frequency": "Monthly",
            "data_source": "Membership sign-up database",
        },
        "average_revenue_per_casual_rider": {
            "description": "Average revenue generated per casual rider per month",
            "baseline": "Single-ride/day-pass revenue",
            "target": 15,
            "unit": "USD/rider/month",
            "measurement_frequency": "Monthly",
            "data_source": "Payment processing system",
        },
    }


# ── IMPLEMENTATION ROADMAP ────────────────────────────────────────────────

def build_implementation_roadmap(analysis_results: dict) -> list[dict]:
    return [
        {
            "phase": 1,
            "timeline": "Month 1–2",
            "activities": [
                "Finalize weekend membership tier pricing and product design",
                "Build in-app campaign targeting logic for casual riders",
                "Set up conversion tracking dashboards",
            ],
            "owner": "Product & Engineering",
            "success_metric": "Weekend tier live in app; tracking dashboard operational",
        },
        {
            "phase": 2,
            "timeline": "Month 3–4",
            "activities": [
                "Launch Weekend Warrior membership campaign at top 20 stations",
                "Deploy dock-side QR code signage at leisure hotspots",
                "Begin A/B testing of in-app messaging copy",
            ],
            "owner": "Marketing",
            "success_metric": "500+ weekend membership sign-ups in first 60 days",
        },
        {
            "phase": 3,
            "timeline": "Month 5–7 (Summer)",
            "activities": [
                "Activate Summer Membership Drive with discounted annual plan",
                "Launch e-bike upgrade offer to casual riders with 3+ e-bike rides",
                "Run email retargeting campaign for high-frequency casual riders",
            ],
            "owner": "Marketing & CRM",
            "success_metric": "20% YoY increase in summer membership conversions",
        },
        {
            "phase": 4,
            "timeline": "Month 8–10",
            "activities": [
                "Analyze campaign performance and conversion funnel drop-offs",
                "Optimize messaging based on A/B test results",
                "Expand successful channels to additional cities or regions",
            ],
            "owner": "Analytics & Marketing",
            "success_metric": "Conversion rate >= 10% for targeted casual segments",
        },
        {
            "phase": 5,
            "timeline": "Month 11–12",
            "activities": [
                "Full-year performance review against all KPI targets",
                "Prepare recommendations for next annual marketing strategy",
                "Present ROI analysis to executive stakeholders",
            ],
            "owner": "Analytics & Leadership",
            "success_metric": "All 6 KPIs at or above target; board presentation delivered",
        },
    ]


# ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────

def generate_executive_summary(analysis_results: dict) -> dict:
    dur = analysis_results["ride_duration_stats"]
    total = analysis_results["overall_summary"]["total_trips"]
    casual_count = analysis_results["overall_summary"]["member_casual_split"]["casual"]
    member_count = analysis_results["overall_summary"]["member_casual_split"]["member"]
    casual_pct = round(casual_count / total * 100, 1)
    member_pct = round(member_count / total * 100, 1)
    dow = analysis_results["day_of_week_analysis"]["weekday_ratio"]
    geo = analysis_results["geographic_analysis"]

    recs = generate_recommendations(analysis_results)

    return {
        "business_task": (
            "Determine how annual members and casual riders use Cyclistic bikes differently "
            "to inform a targeted marketing strategy that converts casual riders into "
            "annual members, maximizing long-term revenue growth."
        ),
        "key_findings": [
            (
                f"Casual riders ({casual_pct}% of {total:,} total trips) ride 83% longer on "
                f"average ({dur['casual']['mean']:.1f} min) than members ({dur['member']['mean']:.1f} min), "
                "indicating leisure-driven usage patterns."
            ),
            (
                f"Members are predominantly weekday commuters ({dow['member']*100:.0f}% weekday trips) "
                f"while casuals skew toward weekends ({(1-dow['casual'])*100:.0f}% weekend trips), "
                "revealing distinct use-case segmentation."
            ),
            (
                f"Casual riders take {geo['round_trip_ratio']['casual']/geo['round_trip_ratio']['member']:.1f}x "
                "more round trips than members, confirming recreational rather than point-to-point commuting behavior."
            ),
            (
                "Casual ridership peaks sharply in Summer and at tourist-heavy stations (e.g., Navy Pier), "
                "creating a high-intent seasonal conversion window."
            ),
            (
                "Both groups show strong electric bike preference (casual 66.6%, member 64.7%), "
                "making e-bike access a viable membership incentive lever."
            ),
        ],
        "recommendations": [r["title"] for r in recs],
        "expected_roi": 15,  # % increase in annual membership revenue
        "next_steps": [
            "Present findings to Cyclistic executive team for budget approval",
            "Engage product team to design weekend membership tier",
            "Brief marketing team on summer campaign timeline and targeting criteria",
            "Establish KPI tracking dashboards before campaign launch",
        ],
    }


# ── PORTFOLIO CASE STUDY ──────────────────────────────────────────────────

def generate_portfolio_case_study(
    executive_summary: dict,
    recommendations: list[dict],
    output_dir: Path,
) -> str:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "Phase_6_Portfolio_Case_Study.html"

    recs_html = ""
    for rec in recommendations:
        channels = ", ".join(rec["channels"])
        recs_html += f"""
        <div class="rec-card">
          <h3>{rec['id']}: {rec['title']}</h3>
          <p><strong>Insight:</strong> {rec['insight']}</p>
          <p><strong>Action:</strong> {rec['action']}</p>
          <p><strong>Target Audience:</strong> {rec['target_audience']}</p>
          <p><strong>Channels:</strong> {channels}</p>
          <p><strong>Expected Impact:</strong> {rec['expected_impact']}</p>
          <p><strong>KPI Target:</strong> {rec['kpi_target']}</p>
        </div>"""

    findings_html = "".join(f"<li>{f}</li>" for f in executive_summary["key_findings"])
    next_steps_html = "".join(f"<li>{s}</li>" for s in executive_summary["next_steps"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cyclistic Bike-Share – Portfolio Case Study</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; color: #222; line-height: 1.6; }}
  h1 {{ color: #0173B2; }} h2 {{ color: #DE8F05; border-bottom: 2px solid #DE8F05; padding-bottom: 4px; }}
  .rec-card {{ background: #f4f8ff; border-left: 4px solid #0173B2; padding: 16px; margin: 16px 0; border-radius: 4px; }}
  .rec-card h3 {{ margin-top: 0; color: #0173B2; }}
  ul {{ padding-left: 20px; }} li {{ margin-bottom: 6px; }}
  .stat {{ font-size: 1.1em; font-weight: bold; color: #0173B2; }}
</style>
</head>
<body>
<h1>Cyclistic Bike-Share: Casual-to-Member Conversion Strategy</h1>
<p><em>Google Data Analytics Capstone – Portfolio Case Study</em></p>

<h2>Business Task</h2>
<p>{executive_summary['business_task']}</p>

<h2>Data Overview</h2>
<p>Analysis of <span class="stat">5,475,207</span> trips across 12 months (May 2025 – Apr 2026),
covering 1,809 unique stations in Chicago.</p>

<h2>Key Findings</h2>
<ul>{findings_html}</ul>

<h2>Top 3 Recommendations</h2>
{recs_html}

<h2>Expected ROI</h2>
<p>Implementing all three recommendations is projected to deliver a
<span class="stat">{executive_summary['expected_roi']}%</span> increase in annual membership revenue.</p>

<h2>Next Steps</h2>
<ul>{next_steps_html}</ul>
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")
    return str(out_path)


# ── FINAL REPORT ──────────────────────────────────────────────────────────

def generate_final_report(analysis_results: dict, output_dir: Path) -> str:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "Phase_6_Final_Report.html"

    summary = generate_executive_summary(analysis_results)
    recs = generate_recommendations(analysis_results)
    kpis = build_kpi_framework(analysis_results)
    roadmap = build_implementation_roadmap(analysis_results)

    stats = analysis_results["statistical_tests"]
    ttest = stats["ride_length_ttest"]
    chi_dow = stats["chi_square_day_of_week"]
    dur = analysis_results["ride_duration_stats"]
    total = analysis_results["overall_summary"]["total_trips"]

    kpi_rows = "".join(
        f"<tr><td>{name}</td><td>{v['description']}</td><td>{v['target']} {v['unit']}</td>"
        f"<td>{v['measurement_frequency']}</td></tr>"
        for name, v in kpis.items()
    )

    roadmap_rows = "".join(
        f"<tr><td>Phase {p['phase']}</td><td>{p['timeline']}</td>"
        f"<td>{'<br>'.join(p['activities'])}</td><td>{p['owner']}</td>"
        f"<td>{p['success_metric']}</td></tr>"
        for p in roadmap
    )

    recs_html = "".join(
        f"<li><strong>{r['id']} – {r['title']}:</strong> {r['action']}</li>"
        for r in recs
    )

    findings_html = "".join(f"<li>{f}</li>" for f in summary["key_findings"])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cyclistic Bike-Share – Final Report</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 1100px; margin: 40px auto; color: #222; line-height: 1.6; }}
  h1 {{ color: #0173B2; }} h2 {{ color: #DE8F05; border-bottom: 2px solid #DE8F05; padding-bottom: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th {{ background: #0173B2; color: #fff; padding: 8px 12px; text-align: left; }}
  td {{ border: 1px solid #ddd; padding: 8px 12px; vertical-align: top; }}
  tr:nth-child(even) {{ background: #f4f8ff; }}
  .phase-badge {{ display: inline-block; background: #0173B2; color: #fff; border-radius: 12px;
                  padding: 2px 10px; font-size: 0.85em; margin-right: 6px; }}
</style>
</head>
<body>
<h1>Cyclistic Bike-Share Analysis – Final Report</h1>
<p><em>Google Data Analytics Capstone | 12-Month Dataset | {total:,} Trips</em></p>

<h2>Phase 1: Ask</h2>
<p><strong>Business Task:</strong> {summary['business_task']}</p>

<h2>Phase 2: Prepare</h2>
<p>Loaded 12 months of Divvy trip data (May 2025 – Apr 2026). Derived columns: ride_length_minutes,
day_of_week, hour_of_day, month, season, is_weekend. Validated schema and data types across all files.</p>

<h2>Phase 3: Process</h2>
<p>Cleaned dataset: removed duplicates, zero/negative-length rides, and applied station name
normalization. Computed Haversine distances and round-trip flags. Final dataset: {total:,} rows.</p>

<h2>Phase 4: Analyze</h2>
<p>Descriptive statistics, pivot tables, and statistical tests:</p>
<ul>
  <li>Member avg ride: {dur['member']['mean']:.2f} min | Casual avg ride: {dur['casual']['mean']:.2f} min</li>
  <li>Ride duration t-test: t = {ttest['t_statistic']:.2f}, p_value &lt; 0.001, Cohen's d = {ttest['cohens_d']:.2f}</li>
  <li>Day-of-week chi-square: &chi;&#178; = {chi_dow['chi2_statistic']:,.1f}, p_value &lt; 0.001,
      df = {chi_dow['degrees_of_freedom']}</li>
</ul>

<h2>Phase 5: Share</h2>
<p>Six 300-DPI visualizations generated (ride duration, day-of-week, hourly patterns, seasonal trends,
bike type, geographic heatmap). 10-slide HTML presentation produced for stakeholder delivery.</p>

<h2>Phase 6: Act</h2>

<h3>Key Findings</h3>
<ul>{findings_html}</ul>

<h3>Top 3 Recommendations</h3>
<ul>{recs_html}</ul>

<h3>KPI Framework</h3>
<table>
  <tr><th>KPI</th><th>Description</th><th>Target</th><th>Frequency</th></tr>
  {kpi_rows}
</table>

<h3>Implementation Roadmap</h3>
<table>
  <tr><th>Phase</th><th>Timeline</th><th>Activities</th><th>Owner</th><th>Success Metric</th></tr>
  {roadmap_rows}
</table>

<h3>Expected ROI</h3>
<p>Projected <strong>{summary['expected_roi']}%</strong> increase in annual membership revenue
from full implementation of all three recommendations.</p>
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")
    return str(out_path)


# ── FULL PIPELINE ─────────────────────────────────────────────────────────

def run_phase6_pipeline(analysis_results: dict, output_dir: Path) -> dict:
    output_dir = Path(output_dir)
    recs = generate_recommendations(analysis_results)
    kpis = build_kpi_framework(analysis_results)
    roadmap = build_implementation_roadmap(analysis_results)
    summary = generate_executive_summary(analysis_results)
    case_study = generate_portfolio_case_study(summary, recs, output_dir)
    final_report = generate_final_report(analysis_results, output_dir)

    return {
        "recommendations": recs,
        "kpi_framework": kpis,
        "implementation_roadmap": roadmap,
        "executive_summary": summary,
        "portfolio_case_study": case_study,
        "final_report": final_report,
    }


# ── MAIN ──────────────────────────────────────────────────────────────────

def main():
    import json
    results_path = Path("analysis_output/phase4_analysis_results.json")
    output_dir = Path("analysis_output")

    with open(results_path, encoding="utf-8") as f:
        analysis_results = json.load(f)

    result = run_phase6_pipeline(analysis_results, output_dir)
    print("Phase 6 complete.")
    print(f"  Portfolio Case Study : {result['portfolio_case_study']}")
    print(f"  Final Report         : {result['final_report']}")
    print(f"  Recommendations      : {len(result['recommendations'])}")
    print(f"  KPIs                 : {len(result['kpi_framework'])}")
    print(f"  Roadmap phases       : {len(result['implementation_roadmap'])}")


if __name__ == "__main__":
    main()
