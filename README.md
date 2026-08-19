# WCI and PDLR Reproducibility Package

This repository contains the data and code supporting the Water Consumption
Impact (WCI) index and its companion Peak Delivery Load Ratio (PDLR) in the
revised manuscript *AI Data Centres and the Water Use Feedback Loop*.

## Scope

The two dimensionless screening metrics are

```text
WCI  = C_peak / K
PDLR = W_peak / K
```

where `C_peak` is estimated peak consumptive demand, `W_peak` is peak
withdrawal or delivery demand, and `K` is the explicitly declared utility-
capacity reference. Under a shared-peaking-factor or constant-consumptive-
ratio construction, `WCI = r * PDLR`.

WCI and PDLR do not measure firm available headroom, watershed scarcity,
drought probability, distribution-system adequacy, ecological effect, or the
probability of service failure. A ratio of one is arithmetic equality with the
selected capacity reference, not a validated operational threshold.

## Repository contents

```text
analysis/  Reproducible numerical analysis and figure-generation scripts
data/      Audited model inputs, provenance, and community-context inputs
docs/      Data dictionary and evidence/boundary documentation
results/   Generated tables, validation checks, and file manifests
figures/   Generated vector figures used in the manuscript and supplement
```

The repository intentionally excludes the superseded first-submission
implementation, internal working notes, and duplicate figure formats.

## Reproduce the numerical analysis

Python 3.10 or newer is recommended. The numerical analysis uses only the
Python standard library.

From the repository root, run:

```bash
python analysis/run_wci_pdlr_analysis.py
```

A successful run writes the result tables to `results/` and reports that:

- 14 audited scenarios were calculated;
- the ten-case comparison retains seven conditional numerical WCI anchors and
  three explicit NA values;
- 48 one-at-a-time sensitivity checks were completed;
- 23 synthetic boundary and failure-mode cases passed; and
- no unsupported empirical low or high bounds were generated.

## Reproduce the figures

Install the plotting dependencies and run:

```bash
python -m pip install -r requirements.txt
python analysis/build_figures.py
```

This creates:

- `figures/Figure_3ab_WCI.pdf`;
- `figures/Figure_4ab_Decomposition.pdf`; and
- `figures/Figure_S1_Sensitivity_FailureModes.pdf`.

The plotting script checks the expected case counts, direct-peak calculation
route, community-context coverage, PDF validity, and text-layout intersections.

## Principal data and results

- `data/wci_input_provenance.csv` is the authoritative input ledger. Each row
  records one scenario parameter, its evidence class, source, time basis,
  water pathway, capacity convention, and boundary decision.
- `data/community_context_inputs.csv` contains the independently labelled
  jurisdictional comparison inputs used in the contextual figure panels.
- `results/wci_pdlr_comparative_results.csv` contains the ten comparison
  anchors, including all explicit NA results.
- `results/wci_pdlr_scenario_results.csv` contains the comparison anchors and
  documented alternative-boundary scenarios.
- `results/wci_pdlr_analytic_sensitivity.csv` contains the 48 exact algebraic
  one-at-a-time checks at +/-10%, +/-25%, and +/-50%.
- `results/wci_synthetic_boundary_tests.csv` contains the 23 constructed
  boundary, invalid-input, and failure-mode cases.
- `results/wci_validation_tests.csv` records automated reproducibility checks.

See `docs/DATA_DICTIONARY.md` and `docs/EVIDENCE_AND_BOUNDARIES.md` before
reusing or comparing the scenarios.

## Evidence policy

Evidence codes are `M` (measured or directly reported site-specific actual),
`R` (reconstructed), `T` (transferred), `A` (author assumption), `P` (planned
or permitted), and `U` (unresolved). A numerical result is calculated only when
the declared numerator and denominator pass the analysis-unit, time, water-
pathway, geographic, and capacity-convention checks. Missing or incompatible
comparisons remain NA.

No complete source-backed low/high input set was available for any of the ten
comparison cases. The sensitivity and synthetic outputs are therefore
diagnostic tests, not empirical confidence intervals, site forecasts, or
definitive rank-stability estimates.

## Licence and citation

The software is released under the MIT License. Citation metadata are provided
in `CITATION.cff`. External source documents are not redistributed; they are
identified in the input ledger and cited in the manuscript or Supplementary
Information.
