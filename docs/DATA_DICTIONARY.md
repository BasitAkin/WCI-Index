# Data dictionary

## Units and missing values

- `MGD`: million US gallons per day.
- `ML_d`: megalitres per day.
- `WCI` and `PDLR`: dimensionless ratios.
- `WCI_pct` and `PDLR_pct`: ratios multiplied by 100.
- Blank numerical fields mean unavailable, ineligible, or not calculated; they
  never mean zero. Supported numerator fields remain populated when only the
  denominator gate fails.

The conversion used throughout is `1 MGD = 3.785411784 ML/d`.

## Input files

### `data/wci_input_provenance.csv`

Each row represents one parameter in one declared scenario.

| Field group | Meaning |
|---|---|
| `site_id`, `site_name`, `state`, `operator` | Case identification |
| `scenario_id`, `scenario_name`, `scenario_type` | Unique calculation scenario and its role |
| `comparison_anchor` | Whether the scenario is one of the ten primary comparison rows |
| `calculation_allowed` | Whether the evidence and boundary gates permit calculation |
| `analysis_unit`, `operational_status` | Facility/campus/development scope and operating stage |
| `parameter`, `central_value`, `units` | Harmonised input used by the calculation |
| `source_reported_value`, `source_reported_units` | Value and units as reported by the source |
| `evidence_class` | M, R, T, A, P, or U evidence code |
| `source`, `source_year`, `source_locator` | Source-identification trail |
| `temporal_basis`, `water_source`, `geographic_boundary` | Boundary metadata |
| `capacity_type`, `boundary_match`, `source_status` | Denominator and admissibility decisions |
| `low_value`, `high_value`, `range_basis` | Reserved for verified source-backed ranges; intentionally blank here |
| `rank_admissibility`, `notes` | Limits on cross-site interpretation |

Recognised calculation parameters are `W_avg`, `C_avg`, `W_peak`, `r_avg`,
`r_peak`, `PF_shared`, and `K`.

### `data/community_context_inputs.csv`

This file records average consumption, reporting days, civil-jurisdiction
population, household-use equivalents, residential-use-equivalent shares,
source URLs, and caveats. These are communication comparisons only. A city or
county population is not assumed to be the matching utility-service population.

### `data/source_corpus_classification.csv`

Contains one row for each of the 103 sources in Supplementary Table S3. Fields
record corpus order, unique citation key and label, primary contribution,
primary pathway, evidence tier, detailed source type, cross-pathway role,
inclusion basis, and the source URL when available. Automated validation checks
the 103 unique keys and reproduces every pathway-by-evidence-tier cell in
Supplementary Table S4.

## Main result files

### `results/wci_pdlr_scenario_results.csv`

Contains all admissible and unresolved scenarios. Important fields include the
average and peak withdrawal/consumption quantities, the consumptive ratio,
withdrawal and consumption peaking factors, `K`, WCI, PDLR, evidence status,
boundary status, calculation status, identity residual, interpretation, and
`WCI_per_unit_PF_pct`/`PDLR_per_unit_PF_pct` for average-flow scenarios.

### `results/douglas_reclaimed_allocation_bound.csv`

Reconstructs the deterministic Douglas reclaimed-water allocation bound from
reported FY2024 total withdrawal, reclaimed withdrawal, potable withdrawal by
difference, and total consumption. It reports the implied reclaimed `r` and WCI
endpoints with PF and K held fixed. This is not a confidence interval or a full
empirical uncertainty envelope.

### `results/wci_pdlr_comparative_results.csv`

The ten-row principal audit. All ten primary comparison rows contain conditional numerical WCI/PDLR anchors under explicitly declared boundaries. Unresolved or intentionally mismatched alternative scenarios remain available in the broader scenario table and retain blank derived fields where appropriate.

### `results/wci_evidence_status.csv`

Summarises evidence classes and the limiting evidence for each scenario.

### `results/wci_rank_admissibility.csv`

Provides exploratory numerical positions while explicitly recording that a
definitive cross-site ranking is inadmissible under the heterogeneous evidence
and boundary conditions.

### `results/wci_pdlr_analytic_sensitivity.csv`

Contains exact one-at-a-time algebraic response multipliers and elasticities
for WCI and PDLR. Perturbations are diagnostic and not empirical input ranges.

### `results/wci_synthetic_boundary_tests.csv`

Contains constructed tests of unit and scale invariance, ratio boundaries,
denominator choice, source mismatch, headroom, aggregation, growth decoupling,
rank reversal, and invalid or missing inputs. These are not site observations.

### `results/wci_validation_tests.csv`

Records automated PASS/FAIL checks for case coverage, leap-year conversion,
WCI-PDLR identity, direct-peak handling, denominator scenarios, numerator retention,
the reported WCI span, sensitivity coverage, and synthetic-test execution.
