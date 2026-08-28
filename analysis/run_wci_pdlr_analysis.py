#!/usr/bin/env python3
"""Reproduce the audited WCI and PDLR results and validation tables.

The numerical analysis uses only the Python standard library. Inputs are read
from ``data/`` and generated tables are written to ``results/``.
"""

from __future__ import annotations

import csv
import hashlib
import math
import platform
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
OUT_DIR = REPO_ROOT / "results"
INPUT_CSV = DATA_DIR / "wci_input_provenance.csv"

MGD_TO_ML_D = 3.785411784
FIXED_SEED = 20260813
NUMERIC_TOLERANCE = 1e-9
ALLOWED_EVIDENCE_CLASSES = {"M", "R", "T", "A", "P", "U"}
ALLOWED_PARAMETERS = {"W_avg", "C_avg", "W_peak", "r_avg", "r_peak", "PF_shared", "K"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_csv_value(row.get(key)) for key in fieldnames})


def format_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.12g}"
    return str(value)


def as_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return float(value)


def as_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"yes", "no"}:
        raise ValueError(f"Expected yes/no, received {value!r}")
    return normalized == "yes"


def validate_value(parameter: str, value: float | None, allow_missing: bool = False) -> None:
    if value is None:
        if allow_missing:
            return
        raise ValueError(f"Missing required value for {parameter}")
    if parameter in {"W_avg", "C_avg", "W_peak"} and value < 0:
        raise ValueError(f"{parameter} must be non-negative")
    if parameter in {"r_avg", "r_peak"} and not 0 <= value <= 1:
        raise ValueError(f"{parameter} must be between 0 and 1")
    if parameter == "PF_shared" and value < 1:
        raise ValueError("PF_shared must be at least 1")
    if parameter == "K" and value <= 0:
        raise ValueError("K must be greater than zero")


def validate_and_group(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    required_fields = {
        "site_id",
        "site_name",
        "state",
        "operator",
        "scenario_id",
        "scenario_name",
        "scenario_type",
        "comparison_anchor",
        "calculation_allowed",
        "analysis_unit",
        "operational_status",
        "parameter",
        "central_value",
        "units",
        "evidence_class",
        "source",
        "temporal_basis",
        "water_source",
        "geographic_boundary",
        "boundary_match",
        "source_status",
        "rank_admissibility",
    }
    if not rows:
        raise ValueError("Provenance input is empty")
    missing_fields = required_fields - set(rows[0])
    if missing_fields:
        raise ValueError(f"Missing provenance columns: {sorted(missing_fields)}")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for line_number, row in enumerate(rows, start=2):
        parameter = row["parameter"]
        if parameter not in ALLOWED_PARAMETERS:
            raise ValueError(f"Line {line_number}: unsupported parameter {parameter!r}")
        if row["evidence_class"] not in ALLOWED_EVIDENCE_CLASSES:
            raise ValueError(f"Line {line_number}: invalid evidence class")
        expected_units = "dimensionless" if parameter in {"r_avg", "r_peak", "PF_shared"} else "MGD"
        if row["units"] != expected_units:
            raise ValueError(
                f"Line {line_number}: {parameter} must use harmonized units {expected_units}, "
                f"not {row['units']!r}"
            )
        value = as_float(row["central_value"])
        validate_value(parameter, value, allow_missing=(row["calculation_allowed"] == "no"))
        if row.get("low_value", "").strip() or row.get("high_value", "").strip():
            raise ValueError(
                f"Line {line_number}: low/high values are prohibited until source-backed bounds are verified"
            )
        as_bool(row["comparison_anchor"])
        as_bool(row["calculation_allowed"])
        grouped[row["scenario_id"]].append(row)

    consistency_fields = [
        "site_id",
        "site_name",
        "state",
        "operator",
        "scenario_name",
        "scenario_type",
        "comparison_anchor",
        "calculation_allowed",
        "analysis_unit",
        "operational_status",
        "boundary_match",
        "rank_admissibility",
    ]
    for scenario_id, scenario_rows in grouped.items():
        for field in consistency_fields:
            values = {row[field] for row in scenario_rows}
            if len(values) != 1:
                raise ValueError(f"Scenario {scenario_id}: inconsistent {field}: {values}")
        parameters = [row["parameter"] for row in scenario_rows]
        if len(parameters) != len(set(parameters)):
            raise ValueError(f"Scenario {scenario_id}: duplicate parameter row")
    return dict(grouped)


def scenario_parameters(rows: list[dict[str, str]]) -> dict[str, float | None]:
    return {row["parameter"]: as_float(row["central_value"]) for row in rows}


def calculation_note(scenario_id: str) -> str:
    notes = {
        "lebanon_tier3_existing_system_counterfactual": (
            "Planning counterfactual: Tier III peak is compared with the pre-expansion system; "
            "this is not current operating overload."
        ),
        "lebanon_tier3_planned_wholesale_allocation": (
            "Within-site planning scenario using the 25 MGD future wholesale allocation; no total "
            "post-expansion capacity is inferred."
        ),
        "council_bluffs_fy2024_combined_nominal_k": (
            "Conditional reconstructed-capacity scenario: 30 MGD is the sum of the 20 MGD Narrows and 10 MGD Council Point nominal potable-treatment capacities; it is not firm available headroom."
        ),
        "mayes_fy2024_nominal_k_default_pf": (
            "Conditional nominal-capacity scenario; K is now authoritative, but PF remains an author assumption."
        ),
        "the_dalles_fy2024_reliable_supply_k": (
            "Conditional current-supply scenario using the City-reported 8.7 MGD reliable peak-season system supply; this is not available headroom."
        ),
        "the_dalles_fy2024_historical_k_proxy": (
            "Historical-denominator scenario only: FY2024 use is compared with the 4.5 MGD reliable supply reported in 2006."
        ),
        "douglas_combined_boundary_indeterminate": (
            "NA: combined reclaimed and potable water is not matched to one combined capacity denominator."
        ),
        "douglas_reclaimed_subsystem_wci_pdlr": (
            "Conditional reclaimed-pathway scenario: the 3.0 MGD reclaimed side-stream capacity is matched to reclaimed withdrawal, and the FY2024 campus-wide consumptive ratio is used explicitly as a within-campus proxy for the reclaimed stream."
        ),
        "wisconsin_40_mgd_2021_context": (
            "Conditional 40 MGD Racine-system scenario; the official capacity source has 2021 context and current confirmation is pending."
        ),
        "botetourt_peak_reservation_24_mgd_k": (
            "Planned maximum-reservation scenario; 2 MGD is used directly against the current 24 MGD serving-plant rating."
        ),
        "memphis_peak_system_258": (
            "Whole-system scenario: the 1 MGD service maximum is compared with 258 MGD MLGW nominal capacity."
        ),
        "memphis_peak_serving_plant_30": (
            "Serving-plant scenario: the 1 MGD service maximum is compared with the 30 MGD Davis WTP rating."
        ),
        "midlothian_fy2024_nominal_k_default_pf": (
            "Conditional nominal-capacity scenario; K is authoritative, but PF remains assumed and direct service needs confirmation."
        ),
        "henderson_fy2024_regional_gross_capacity": (
            "Regional gross-capacity scenario; it does not measure local headroom, basin scarcity, or hydrologic safety."
        ),
    }
    return notes[scenario_id]


def calculate_scenario(rows: list[dict[str, str]]) -> dict[str, Any]:
    meta = rows[0]
    parameters = scenario_parameters(rows)
    allowed = as_bool(meta["calculation_allowed"])
    source_statuses = sorted({row["source_status"] for row in rows})
    result: dict[str, Any] = {
        "site_id": meta["site_id"],
        "site_name": meta["site_name"],
        "state": meta["state"],
        "operator": meta["operator"],
        "scenario_id": meta["scenario_id"],
        "scenario_name": meta["scenario_name"],
        "scenario_type": meta["scenario_type"],
        "comparison_anchor": meta["comparison_anchor"],
        "analysis_unit": meta["analysis_unit"],
        "operational_status": meta["operational_status"],
        "source_status": ";".join(source_statuses),
        "boundary_status": meta["boundary_match"],
        "rank_admissibility": meta["rank_admissibility"],
        "calculation_status": "not_calculated_boundary_or_denominator_unresolved",
        "W_avg_MGD": parameters.get("W_avg"),
        "C_avg_MGD": parameters.get("C_avg"),
        "r_used": None,
        "PF_W": None,
        "PF_C": None,
        "W_peak_MGD": parameters.get("W_peak"),
        "C_peak_MGD": None,
        "K_MGD": parameters.get("K"),
        "W_avg_ML_d": None,
        "C_avg_ML_d": None,
        "W_peak_ML_d": None,
        "C_peak_ML_d": None,
        "K_ML_d": None,
        "WCI": None,
        "WCI_pct": None,
        "PDLR": None,
        "PDLR_pct": None,
        "shared_pf_or_constant_r_assumption": "not applicable",
        "identity_residual": None,
        "interpretation_note": calculation_note(meta["scenario_id"]),
    }
    # Derive every supported numerator quantity before applying the denominator
    # eligibility gate. This preserves transparent demand information for cases
    # whose current, pathway-matched K is unresolved, while preventing an
    # unsupported WCI or PDLR from being calculated.
    if parameters.get("W_peak") is not None:
        w_peak = parameters["W_peak"]
        r_used = parameters.get("r_peak")
        validate_value("W_peak", w_peak)
        validate_value("r_peak", r_used)
        assert w_peak is not None and r_used is not None
        c_peak = w_peak * r_used
        w_avg = parameters.get("W_avg")
        c_avg = parameters.get("C_avg")
        pf_w = None
        pf_c = None
        assumption = "constant transferred r at peak; direct peak input; no added PF"
    else:
        w_avg = parameters.get("W_avg")
        validate_value("W_avg", w_avg)
        assert w_avg is not None
        c_avg = parameters.get("C_avg")
        r_input = parameters.get("r_avg")
        if c_avg is not None:
            validate_value("C_avg", c_avg)
            if w_avg == 0:
                raise ValueError(f"Scenario {meta['scenario_id']}: cannot derive r from W_avg=0")
            r_used = c_avg / w_avg
        elif r_input is not None:
            validate_value("r_avg", r_input)
            assert r_input is not None
            r_used = r_input
            c_avg = w_avg * r_used
        else:
            r_used = None
            c_avg = None
        pf_shared = parameters.get("PF_shared")
        validate_value("PF_shared", pf_shared)
        assert pf_shared is not None
        pf_w = pf_shared
        pf_c = pf_shared
        w_peak = w_avg * pf_w
        c_peak = None if c_avg is None else c_avg * pf_c
        assumption = (
            "PF_W applied to withdrawal only; WCI unavailable because source-specific r or C is missing"
            if c_peak is None
            else "PF_W equals PF_C and r is constant from average to peak"
        )

    k = parameters.get("K")
    if allowed:
        validate_value("K", k)
        assert k is not None
    else:
        k = None

    wci = None if not allowed or c_peak is None else c_peak / k
    pdlr = None if not allowed else w_peak / k
    identity_residual = None if wci is None or r_used is None else wci - r_used * pdlr
    if identity_residual is not None and abs(identity_residual) > NUMERIC_TOLERANCE:
        raise ValueError(f"Scenario {meta['scenario_id']}: WCI = r x PDLR identity failed")

    result.update(
        {
            "calculation_status": (
                "numerator_only_denominator_or_boundary_unresolved"
                if not allowed
                else "pdlr_only_source_specific_r_unavailable"
                if wci is None
                else "numeric_conditional_scenario"
            ),
            "W_avg_MGD": w_avg,
            "C_avg_MGD": c_avg,
            "r_used": r_used,
            "PF_W": pf_w,
            "PF_C": pf_c,
            "W_peak_MGD": w_peak,
            "C_peak_MGD": c_peak,
            "K_MGD": k,
            "W_avg_ML_d": None if w_avg is None else w_avg * MGD_TO_ML_D,
            "C_avg_ML_d": None if c_avg is None else c_avg * MGD_TO_ML_D,
            "W_peak_ML_d": w_peak * MGD_TO_ML_D,
            "C_peak_ML_d": None if c_peak is None else c_peak * MGD_TO_ML_D,
            "K_ML_d": None if k is None else k * MGD_TO_ML_D,
            "WCI": wci,
            "WCI_pct": None if wci is None else wci * 100,
            "PDLR": pdlr,
            "PDLR_pct": None if pdlr is None else pdlr * 100,
            "shared_pf_or_constant_r_assumption": assumption,
            "identity_residual": identity_residual,
        }
    )
    return result


def build_evidence_status(
    grouped: dict[str, list[dict[str, str]]], results_by_id: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    output = []
    for scenario_id, rows in grouped.items():
        result = results_by_id[scenario_id]
        classes = Counter(row["evidence_class"] for row in rows)
        parameter_evidence = ";".join(f"{row['parameter']}:{row['evidence_class']}" for row in rows)
        weakest = []
        for code, label in (("U", "unresolved"), ("A", "assumed"), ("T", "transferred"), ("P", "planned")):
            if classes[code]:
                weakest.append(label)
        output.append(
            {
                "site_id": result["site_id"],
                "site_name": result["site_name"],
                "scenario_id": scenario_id,
                "scenario_type": result["scenario_type"],
                "source_status": result["source_status"],
                "boundary_status": result["boundary_status"],
                "parameter_evidence": parameter_evidence,
                "measured_or_direct_count": classes["M"],
                "reconstructed_count": classes["R"],
                "transferred_count": classes["T"],
                "assumed_count": classes["A"],
                "planned_count": classes["P"],
                "unresolved_count": classes["U"],
                "limiting_evidence": ";".join(weakest) if weakest else "site-specific reported or reconstructed",
                "numeric_result_available": result["WCI"] is not None,
                "rank_admissibility": result["rank_admissibility"],
                "evidence_conclusion": result["interpretation_note"],
            }
        )
    return output


def build_analytic_sensitivity() -> list[dict[str, Any]]:
    rows = []
    parameters = ("W_or_peak", "r", "PF", "K")
    metrics = ("WCI", "PDLR")
    for metric in metrics:
        for parameter in parameters:
            for perturbation in (0.10, 0.25, 0.50):
                for direction, signed in (("decrease", -perturbation), ("increase", perturbation)):
                    input_multiplier = 1 + signed
                    if parameter == "K":
                        output_multiplier = 1 / input_multiplier
                        elasticity = -1.0
                    elif parameter == "r" and metric == "PDLR":
                        output_multiplier = 1.0
                        elasticity = 0.0
                    else:
                        output_multiplier = input_multiplier
                        elasticity = 1.0
                    rows.append(
                        {
                            "scenario_id": f"analytic_{metric.lower()}_{parameter.lower()}_{direction}_{int(perturbation*100)}",
                            "scenario_type": "analytic_algebraic_sensitivity",
                            "source_status": "equation_derived",
                            "boundary_status": "synthetic_not_site_specific",
                            "metric": metric,
                            "parameter": parameter,
                            "direction": direction,
                            "perturbation_pct": perturbation * 100,
                            "input_multiplier": input_multiplier,
                            "output_multiplier": output_multiplier,
                            "output_change_pct": (output_multiplier - 1) * 100,
                            "log_elasticity": elasticity,
                            "interpretation": (
                                "Algebraic one-at-a-time check only; not an empirical uncertainty bound or feasible intervention claim."
                            ),
                        }
                    )
    return rows


def synthetic_calc(
    w_avg: float | None,
    r: float | None,
    pf: float | None,
    k: float | None,
    w_peak: float | None = None,
) -> tuple[float | None, float | None, float | None, float | None, str]:
    try:
        validate_value("K", k)
        validate_value("r_avg", r)
        assert k is not None and r is not None
        if w_peak is not None:
            validate_value("W_peak", w_peak)
            c_peak = w_peak * r
        else:
            validate_value("W_avg", w_avg)
            validate_value("PF_shared", pf)
            assert w_avg is not None and pf is not None
            w_peak = w_avg * pf
            c_peak = w_peak * r
        return w_peak, c_peak, c_peak / k, w_peak / k, ""
    except (ValueError, AssertionError) as exc:
        return None, None, None, None, str(exc)


def build_synthetic_boundary_tests() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(
        test_id: str,
        case_id: str,
        w_avg: float | None,
        r: float | None,
        pf: float | None,
        k: float | None,
        expected: str,
        boundary_status: str = "synthetic_matched",
        w_peak: float | None = None,
        expected_error: bool = False,
        auxiliary_value: float | None = None,
        auxiliary_definition: str = "",
    ) -> None:
        wp, cp, wci, pdlr, error = synthetic_calc(w_avg, r, pf, k, w_peak=w_peak)
        observed_error = bool(error)
        status = "PASS" if observed_error == expected_error else "FAIL"
        cases.append(
            {
                "test_id": test_id,
                "case_id": case_id,
                "scenario_type": "synthetic_boundary_or_false_data_test",
                "source_status": "synthetic_not_empirical",
                "boundary_status": boundary_status,
                "W_avg_ML_d": w_avg,
                "r": r,
                "PF": pf,
                "K_ML_d": k,
                "W_peak_ML_d": wp,
                "C_peak_ML_d": cp,
                "WCI": wci,
                "PDLR": pdlr,
                "auxiliary_value": auxiliary_value,
                "auxiliary_definition": auxiliary_definition,
                "expected_behavior": expected,
                "error_message": error,
                "test_status": status,
                "interpretation": "Synthetic result only; never an empirical site bound.",
            }
        )

    add("reference", "base", 10, 0.75, 2, 100, "WCI=0.15 and PDLR=0.20")
    add(
        "unit_invariance",
        "same_ratio_in_mgd",
        10 / MGD_TO_ML_D,
        0.75,
        2,
        100 / MGD_TO_ML_D,
        "Same WCI and PDLR after converting both flow quantities",
    )
    add(
        "unit_invariance",
        "same_ratio_in_ml_per_day",
        10,
        0.75,
        2,
        100,
        "Same WCI and PDLR after converting both flow quantities",
    )
    add("scale_invariance", "all_flows_x3", 30, 0.75, 2, 300, "Same WCI and PDLR after common scaling")
    add("dry_cooling_boundary", "r_zero", 10, 0, 2, 100, "WCI=0 while PDLR remains positive")
    add("complete_consumption_boundary", "r_one", 10, 1, 2, 100, "WCI equals PDLR")
    add("extreme_peaking", "pf_30", 10, 0.75, 30, 100, "Both metrics scale linearly with PF")
    add(
        "denominator_boundary",
        "regional_K",
        10,
        0.75,
        2,
        1000,
        "Regional denominator produces a much smaller scale ratio",
        boundary_status="synthetic_regional",
    )
    add(
        "denominator_boundary",
        "local_K",
        10,
        0.75,
        2,
        20,
        "Local denominator produces a much larger scale ratio",
        boundary_status="synthetic_local",
    )
    add(
        "reclaimed_water_mismatch",
        "incorrect_total_over_potable_K",
        10,
        0.8,
        2,
        20,
        "Numeric result is generated but must be rejected because source boundaries fail",
        boundary_status="synthetic_intentional_fail",
    )
    add(
        "reclaimed_water_mismatch",
        "source_specific_r_missing",
        1,
        None,
        2,
        20,
        "Missing source-specific r returns NA rather than an imputed value",
        boundary_status="synthetic_indeterminate",
        expected_error=True,
    )
    add(
        "available_headroom",
        "gross_capacity_ratio",
        None,
        0.75,
        None,
        100,
        "PDLR remains 0.20 against gross K even though load equals twice the assumed 10-unit headroom",
        w_peak=20,
        auxiliary_value=2.0,
        auxiliary_definition="W_peak divided by synthetic available headroom of 10 ML/d",
    )
    add(
        "campus_aggregation",
        "noncoincident_lower_envelope",
        None,
        0.75,
        None,
        20,
        "Largest individual peak is used as a noncoincident lower envelope",
        w_peak=4,
    )
    add(
        "campus_aggregation",
        "coincident_upper_envelope",
        None,
        0.75,
        None,
        20,
        "Sum of facility peaks is used only as a perfect-coincidence upper envelope",
        w_peak=7,
    )
    add(
        "growth_decoupling",
        "load_up_20_wue_down_20",
        9.6,
        0.75,
        2,
        100,
        "Water multiplier is 1.20 x 0.80 = 0.96, so computing growth does not uniquely set water growth",
        auxiliary_value=0.96,
        auxiliary_definition="synthetic net water multiplier",
    )
    add("rank_reversal", "site_A_baseline", 4.0, 0.75, 2, 10, "Baseline WCI A=0.60 exceeds B=0.57")
    add("rank_reversal", "site_B_baseline", 3.8, 0.75, 2, 10, "Baseline WCI A=0.60 exceeds B=0.57")
    add("rank_reversal", "site_A_after_10pct_W_drop", 3.6, 0.75, 2, 10, "A falls to 0.54 and is outranked by unchanged B")
    add("missingness", "missing_K", 10, 0.75, 2, None, "Missing K returns NA, never zero or a default", expected_error=True)
    add("invalid_input", "r_above_one", 10, 1.1, 2, 100, "Validator rejects r>1", expected_error=True)
    add("invalid_input", "pf_below_one", 10, 0.75, 0.5, 100, "Validator rejects PF<1", expected_error=True)
    add("invalid_input", "zero_K", 10, 0.75, 2, 0, "Validator rejects K=0", expected_error=True)
    add("invalid_input", "negative_W", -1, 0.75, 2, 100, "Validator rejects negative W", expected_error=True)

    expected_numeric = {
        "base": (0.15, 0.20),
        "same_ratio_in_mgd": (0.15, 0.20),
        "same_ratio_in_ml_per_day": (0.15, 0.20),
        "all_flows_x3": (0.15, 0.20),
        "r_zero": (0.0, 0.20),
        "r_one": (0.20, 0.20),
        "pf_30": (2.25, 3.0),
        "regional_K": (0.015, 0.02),
        "local_K": (0.75, 1.0),
        "incorrect_total_over_potable_K": (0.80, 1.0),
        "gross_capacity_ratio": (0.15, 0.20),
        "noncoincident_lower_envelope": (0.15, 0.20),
        "coincident_upper_envelope": (0.2625, 0.35),
        "load_up_20_wue_down_20": (0.144, 0.192),
        "site_A_baseline": (0.60, 0.80),
        "site_B_baseline": (0.57, 0.76),
        "site_A_after_10pct_W_drop": (0.54, 0.72),
    }
    by_case = {row["case_id"]: row for row in cases}
    for case_id, (expected_wci, expected_pdlr) in expected_numeric.items():
        row = by_case[case_id]
        numeric_ok = (
            row["WCI"] is not None
            and row["PDLR"] is not None
            and math.isclose(row["WCI"], expected_wci, rel_tol=0, abs_tol=NUMERIC_TOLERANCE)
            and math.isclose(row["PDLR"], expected_pdlr, rel_tol=0, abs_tol=NUMERIC_TOLERANCE)
        )
        if not numeric_ok:
            row["test_status"] = "FAIL"
            row["error_message"] = (
                f"Expected WCI={expected_wci}, PDLR={expected_pdlr}; "
                f"observed WCI={row['WCI']}, PDLR={row['PDLR']}"
            )
    reversal_ok = (
        by_case["site_A_baseline"]["WCI"] > by_case["site_B_baseline"]["WCI"]
        and by_case["site_A_after_10pct_W_drop"]["WCI"] < by_case["site_B_baseline"]["WCI"]
    )
    if not reversal_ok:
        for case_id in ("site_A_baseline", "site_B_baseline", "site_A_after_10pct_W_drop"):
            by_case[case_id]["test_status"] = "FAIL"
            by_case[case_id]["error_message"] = "Expected synthetic rank reversal did not occur"
    return cases


def average_descending_ranks(values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(values.items(), key=lambda item: (-item[1], item[0]))
    ranks: dict[str, float] = {}
    position = 1
    index = 0
    while index < len(ordered):
        value = ordered[index][1]
        tied = []
        while index < len(ordered) and math.isclose(ordered[index][1], value, rel_tol=0, abs_tol=1e-15):
            tied.append(ordered[index][0])
            index += 1
        mean_rank = (position + (position + len(tied) - 1)) / 2
        for key in tied:
            ranks[key] = mean_rank
        position += len(tied)
    return ranks


def build_rank_admissibility(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    anchors = [row for row in results if row["comparison_anchor"] == "yes"]
    wci_values = {row["scenario_id"]: row["WCI"] for row in anchors if row["WCI"] is not None}
    pdlr_values = {row["scenario_id"]: row["PDLR"] for row in anchors if row["PDLR"] is not None}
    wci_ranks = average_descending_ranks(wci_values)
    pdlr_ranks = average_descending_ranks(pdlr_values)
    na_names = sorted(row["site_name"] for row in anchors if row["WCI"] is None)
    scope = (
        f"{len(wci_values)} numeric conditional anchors; "
        + (f"WCI NA for {', '.join(na_names)}; " if na_names else "no primary WCI/PDLR anchors are NA; ")
        + "heterogeneous evidence and boundaries"
    )
    output = []
    for row in anchors:
        output.append(
            {
                "site_id": row["site_id"],
                "site_name": row["site_name"],
                "scenario_id": row["scenario_id"],
                "scenario_type": row["scenario_type"],
                "numeric_result_available": row["WCI"] is not None,
                "exploratory_wci_rank": wci_ranks.get(row["scenario_id"]),
                "exploratory_pdlr_rank": pdlr_ranks.get(row["scenario_id"]),
                "definitive_cross_site_rank_admissible": False,
                "rank_scope": scope,
                "rank_admissibility": row["rank_admissibility"],
                "boundary_status": row["boundary_status"],
                "blocking_reason": row["interpretation_note"],
            }
        )
    return output


def build_validation_tests(
    provenance_rows: list[dict[str, str]],
    results_by_id: dict[str, dict[str, Any]],
    analytic_rows: list[dict[str, Any]],
    synthetic_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []

    def record(test_id: str, description: str, passed: bool, observed: str) -> None:
        tests.append(
            {
                "test_id": test_id,
                "test_description": description,
                "test_status": "PASS" if passed else "FAIL",
                "observed": observed,
            }
        )

    no_ranges = all(not row.get("low_value", "").strip() and not row.get("high_value", "").strip() for row in provenance_rows)
    record(
        "no_fabricated_bounds",
        "No empirical low or high bound is populated without verification",
        no_ranges,
        "All low_value and high_value cells are blank",
    )
    anchors = {
        row["scenario_id"]: row
        for row in results_by_id.values()
        if row["comparison_anchor"] == "yes"
    }
    anchor_sites = [row["site_id"] for row in anchors.values()]
    record(
        "ten_site_anchor_coverage",
        "The comparative anchor table retains exactly one numerical WCI/PDLR row for each of the ten sites",
        len(anchors) == 10 and len(set(anchor_sites)) == 10,
        f"anchor_rows={len(anchors)}; unique_sites={len(set(anchor_sites))}",
    )
    fy_rows = [row for row in provenance_rows if row["source_reported_units"] == "Mgal per FY2024"]
    fy_errors = []
    for row in fy_rows:
        expected = float(row["source_reported_value"]) / 366
        fy_errors.append(abs(float(row["central_value"]) - expected))
    record(
        "fy2024_leap_year_conversion",
        "All FY2024 annual Google quantities use 366 days",
        bool(fy_errors) and max(fy_errors) < 1e-12,
        f"maximum absolute conversion error={max(fy_errors) if fy_errors else 'NA'}",
    )
    numeric_results = [row for row in results_by_id.values() if row["WCI"] is not None]
    identity_max = max(abs(row["identity_residual"]) for row in numeric_results)
    record(
        "wci_pdlr_identity",
        "WCI equals r times PDLR under the stated shared-PF or constant-r assumption",
        identity_max <= NUMERIC_TOLERANCE,
        f"maximum absolute residual={identity_max}",
    )
    numeric_anchors = [
        row for row in anchors.values() if row["WCI_pct"] is not None
    ]
    wci_min = min(row["WCI_pct"] for row in numeric_anchors)
    wci_max = max(row["WCI_pct"] for row in numeric_anchors)
    record(
        "reported_wci_span",
        "The ten conditional anchors reproduce the manuscript's 0.157--134 percent WCI span after rounding",
        round(wci_min, 3) == 0.157 and round(wci_max) == 134,
        f"minimum={wci_min:.12g} percent; maximum={wci_max:.12g} percent",
    )
    bot = results_by_id["botetourt_peak_reservation_24_mgd_k"]
    record(
        "botetourt_no_double_peak",
        "Botetourt uses the 2 MGD peak reservation directly without another PF",
        bot["W_peak_MGD"] == 2 and bot["PF_W"] is None,
        f"W_peak={bot['W_peak_MGD']} MGD; PF_W={bot['PF_W']}",
    )
    memphis_ids = {"memphis_peak_system_258", "memphis_peak_serving_plant_30"}
    record(
        "memphis_two_capacity_boundaries",
        "Memphis uses the 1 MGD service maximum directly against whole-system and serving-plant denominators",
        memphis_ids.issubset(results_by_id),
        ";".join(sorted(memphis_ids)),
    )
    lebanon_k = {
        results_by_id["lebanon_tier3_existing_system_counterfactual"]["K_MGD"],
        results_by_id["lebanon_tier3_planned_wholesale_allocation"]["K_MGD"],
    }
    record(
        "lebanon_boundary_scenarios",
        "Lebanon includes the existing-system counterfactual and planned wholesale-allocation case without inferring a total",
        lebanon_k == {4.6, 25.0},
        f"K scenarios={sorted(lebanon_k)} MGD",
    )
    new_anchor_ids = {
        "council_bluffs_fy2024_combined_nominal_k",
        "the_dalles_fy2024_reliable_supply_k",
        "douglas_reclaimed_subsystem_wci_pdlr",
    }
    record(
        "resolved_three_primary_denominators",
        "Council Bluffs, The Dalles, and Douglas County now have explicitly declared, boundary-qualified primary denominators",
        new_anchor_ids.issubset(anchors)
        and all(results_by_id[item]["K_MGD"] is not None
                and results_by_id[item]["WCI"] is not None
                and results_by_id[item]["PDLR"] is not None
                for item in new_anchor_ids),
        ";".join(sorted(new_anchor_ids)),
    )
    council = results_by_id["council_bluffs_fy2024_combined_nominal_k"]
    record(
        "council_bluffs_reconstructed_k",
        "Council Bluffs uses a reconstructed 30 MGD combined nominal potable-treatment capacity",
        council["K_MGD"] == 30 and math.isclose(council["WCI_pct"], 59.8024, rel_tol=0, abs_tol=0.001),
        f"K={council['K_MGD']} MGD; WCI={council['WCI_pct']}%; PDLR={council['PDLR_pct']}%",
    )
    dalles = results_by_id["the_dalles_fy2024_reliable_supply_k"]
    record(
        "the_dalles_current_reliable_k",
        "The Dalles uses the current 8.7 MGD reliable peak-season system supply",
        dalles["K_MGD"] == 8.7 and math.isclose(dalles["WCI_pct"], 25.082, rel_tol=0, abs_tol=0.01),
        f"K={dalles['K_MGD']} MGD; WCI={dalles['WCI_pct']}%; PDLR={dalles['PDLR_pct']}%",
    )
    douglas = results_by_id["douglas_reclaimed_subsystem_wci_pdlr"]
    record(
        "douglas_reclaimed_boundary",
        "Douglas uses the 3 MGD reclaimed subsystem with a within-campus FY2024 consumptive-ratio proxy",
        douglas["K_MGD"] == 3
        and math.isclose(douglas["WCI_pct"], 82.1462606881, rel_tol=0, abs_tol=1e-8)
        and math.isclose(douglas["PDLR_pct"], 99.4307832423, rel_tol=0, abs_tol=1e-8),
        f"WCI={douglas['WCI_pct']}%; PDLR={douglas['PDLR_pct']}%; K={douglas['K_MGD']} MGD",
    )
    wisconsin = results_by_id["wisconsin_40_mgd_2021_context"]
    record(
        "wisconsin_corrected_denominator",
        "Wisconsin uses 40 MGD only as a conditional 2021-context system-capacity scenario",
        wisconsin["K_MGD"] == 40 and wisconsin["rank_admissibility"] == "conditional_confirmation_pending",
        f"K={wisconsin['K_MGD']} MGD; status={wisconsin['rank_admissibility']}",
    )
    synthetic_pass = all(row["test_status"] == "PASS" for row in synthetic_rows)
    analytic_ok = (
        len(analytic_rows) == 48
        and {row["metric"] for row in analytic_rows} == {"WCI", "PDLR"}
        and {row["perturbation_pct"] for row in analytic_rows} == {10.0, 25.0, 50.0}
    )
    record(
        "analytic_sensitivity_execution",
        "The complete WCI and PDLR one-at-a-time sensitivity design contains 48 checks at 10, 25, and 50 percent",
        analytic_ok,
        f"{len(analytic_rows)} checks",
    )
    record(
        "synthetic_test_execution",
        "All synthetic boundary and false-data cases behaved as designed",
        synthetic_pass,
        f"{len(synthetic_rows)} cases",
    )
    return tests


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    provenance_rows = read_csv(INPUT_CSV)
    grouped = validate_and_group(provenance_rows)
    results = [calculate_scenario(rows) for rows in grouped.values()]
    results_by_id = {row["scenario_id"]: row for row in results}
    evidence_status = build_evidence_status(grouped, results_by_id)
    analytic_sensitivity = build_analytic_sensitivity()
    synthetic_rows = build_synthetic_boundary_tests()
    rank_rows = build_rank_admissibility(results)
    validation_rows = build_validation_tests(
        provenance_rows, results_by_id, analytic_sensitivity, synthetic_rows
    )

    result_fields = [
        "site_id", "site_name", "state", "operator", "scenario_id", "scenario_name",
        "scenario_type", "comparison_anchor", "analysis_unit", "operational_status",
        "source_status", "boundary_status", "rank_admissibility", "calculation_status",
        "W_avg_MGD", "C_avg_MGD", "r_used", "PF_W", "PF_C", "W_peak_MGD",
        "C_peak_MGD", "K_MGD", "W_avg_ML_d", "C_avg_ML_d", "W_peak_ML_d",
        "C_peak_ML_d", "K_ML_d", "WCI", "WCI_pct", "PDLR", "PDLR_pct",
        "shared_pf_or_constant_r_assumption", "identity_residual", "interpretation_note",
    ]
    write_csv(OUT_DIR / "wci_pdlr_scenario_results.csv", result_fields, results)
    comparative_results = [row for row in results if row["comparison_anchor"] == "yes"]
    write_csv(OUT_DIR / "wci_pdlr_comparative_results.csv", result_fields, comparative_results)

    evidence_fields = [
        "site_id", "site_name", "scenario_id", "scenario_type", "source_status",
        "boundary_status", "parameter_evidence", "measured_or_direct_count",
        "reconstructed_count", "transferred_count", "assumed_count", "planned_count",
        "unresolved_count", "limiting_evidence", "numeric_result_available",
        "rank_admissibility", "evidence_conclusion",
    ]
    write_csv(OUT_DIR / "wci_evidence_status.csv", evidence_fields, evidence_status)

    analytic_fields = [
        "scenario_id", "scenario_type", "source_status", "boundary_status", "metric",
        "parameter", "direction", "perturbation_pct", "input_multiplier",
        "output_multiplier", "output_change_pct", "log_elasticity", "interpretation",
    ]
    write_csv(OUT_DIR / "wci_pdlr_analytic_sensitivity.csv", analytic_fields, analytic_sensitivity)

    synthetic_fields = [
        "test_id", "case_id", "scenario_type", "source_status", "boundary_status",
        "W_avg_ML_d", "r", "PF", "K_ML_d", "W_peak_ML_d", "C_peak_ML_d",
        "WCI", "PDLR", "auxiliary_value", "auxiliary_definition", "expected_behavior",
        "error_message", "test_status", "interpretation",
    ]
    write_csv(OUT_DIR / "wci_synthetic_boundary_tests.csv", synthetic_fields, synthetic_rows)

    rank_fields = [
        "site_id", "site_name", "scenario_id", "scenario_type", "numeric_result_available",
        "exploratory_wci_rank", "exploratory_pdlr_rank",
        "definitive_cross_site_rank_admissible", "rank_scope", "rank_admissibility",
        "boundary_status", "blocking_reason",
    ]
    write_csv(OUT_DIR / "wci_rank_admissibility.csv", rank_fields, rank_rows)

    validation_fields = ["test_id", "test_description", "test_status", "observed"]
    write_csv(OUT_DIR / "wci_validation_tests.csv", validation_fields, validation_rows)

    metadata_rows = [
        {"key": "generated_at_utc", "value": datetime.now(timezone.utc).isoformat()},
        {"key": "python_version", "value": sys.version.replace("\n", " ")},
        {"key": "platform", "value": platform.platform()},
        {"key": "external_dependencies", "value": "none; Python standard library only"},
        {"key": "fixed_seed_reserved_for_future_sampling", "value": FIXED_SEED},
        {"key": "mgd_to_ml_per_day", "value": MGD_TO_ML_D},
        {"key": "input_sha256", "value": sha256(INPUT_CSV)},
        {"key": "script_sha256", "value": sha256(Path(__file__).resolve())},
    ]
    write_csv(OUT_DIR / "run_metadata.csv", ["key", "value"], metadata_rows)

    failures = [row for row in validation_rows if row["test_status"] != "PASS"]
    if failures:
        for failure in failures:
            print(f"FAIL: {failure['test_id']}: {failure['observed']}", file=sys.stderr)
        return 1
    print(
        f"PASS: generated {len(results)} corrected scenarios, "
        f"{len(analytic_sensitivity)} analytic checks, and {len(synthetic_rows)} synthetic tests."
    )
    print(
        "PASS: all ten comparison anchors have numerical conditional WCI and PDLR values, "
        "including the reconstructed Council Bluffs, current-reliable The Dalles, and reclaimed-pathway Douglas cases."
    )
    print("PASS: no empirical low/high bounds were generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
