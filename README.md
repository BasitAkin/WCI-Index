# AI Data Centres and the Water Use Feedback Loop

## WCI and PDLR reproducibility package

**Authors:** Basit A. Akinade, Amobichukwu C. Amanambu, Jonathan M. Frame, and Shaolei Ren

**Correspondence:** Amobichukwu C. Amanambu, Water INtelligence and Geospatial Sensing (WINGS) Laboratory, Department of Geography and the Environment, The University of Alabama, Tuscaloosa, Alabama, USA

This repository provides the data, analysis code, validation tests, and
figure-generation workflow supporting *AI Data Centres and the Water Use
Feedback Loop*. It is the authoritative public reproducibility package for the
Water Consumption Impact (WCI) index and its companion Peak Delivery Load
Ratio (PDLR).

## Study overview

The study connects three pathways through which water systems and artificial
intelligence interact:

1. **Burden pathway:** AI data centres create direct and indirect demands on
   water systems.
2. **Constraint pathway:** water availability, infrastructure, regulation, and
   community conditions can influence data-centre siting and development.
3. **Adaptive pathway:** AI-enabled tools can support water monitoring,
   forecasting, treatment, conservation, and system management.

Together, these pathways form the **Water and AI Feedback Loop**. The
quantitative component introduces WCI and PDLR as transparent screening
metrics for comparing estimated peak data-centre water demand with an
explicitly declared host-utility capacity reference.

## Metric definitions

The two dimensionless screening metrics are

```text
WCI  = C_peak / K
PDLR = W_peak / K
```

where `C_peak` is estimated peak consumptive demand, `W_peak` is peak
withdrawal or delivery demand, and `K` is the explicitly declared utility-
capacity reference. Under a shared-peaking-factor or constant-consumptive-
ratio construction, `WCI = r * PDLR`.

| Symbol | Definition |
|---|---|
| `C_peak` | Estimated peak consumptive water demand |
| `W_peak` | Estimated peak withdrawal or delivery demand |
| `K` | Explicitly declared utility-capacity reference |
| `r` | Consumptive ratio, when required by the calculation route |
| `PF` | Applicable peaking factor when demand is not already reported as peak |

The implementation preserves directly reported peak quantities without
applying an additional peaking factor.

WCI and PDLR do not measure firm available headroom, watershed scarcity,
drought probability, distribution-system adequacy, ecological effect, or the
probability of service failure. A ratio of one is arithmetic equality with the
selected capacity reference, not a validated operational threshold.

Results depend on the definition and boundary of `K`. Local, system-wide,
historical, planned, nominal-capacity, allocation, and available-headroom
denominators are not interchangeable.

## Case-study results represented in this repository

The application audit contains ten US cases. All ten primary comparison anchors now have explicitly conditional numerical WCI and PDLR values under declared boundaries. Council Bluffs uses a reconstructed 30 MGD combined nominal potable-treatment capacity; The Dalles uses 8.7 MGD of current reliable peak-season supply; and Douglas County is evaluated on the matched reclaimed-water pathway using the reported 3.0 MGD subsystem capacity and a within-campus consumptive-ratio proxy. The ten numerical WCI anchors span approximately `0.157%` to `134%` after rounding.

The community-context calculation has a separate gate. Six cases have a
defensible FY2024 average-consumption value; four planned or service-maximum
records do not. Figure 3a and Figure 4a include all ten primary WCI/PDLR cases. Figures 3b and 4b retain only the six cases eligible for the independent community-context calculation.
The tabular files preserve the full ten-case audit and the reason for every
unreported result.

This span describes the retained conditional cases. It is not an empirical
confidence interval, a definitive cross-site ranking, or evidence that one
denominator convention applies across all sites. Alternative-boundary and
failure-mode tests demonstrate that magnitudes and ordering can change with
the selected denominator and other governing assumptions.

## Repository contents

```text
analysis/  Reproducible numerical analysis and figure-generation scripts
data/      Audited model inputs, provenance, and community-context inputs
docs/      Data dictionary and evidence/boundary documentation
results/   Generated tables, validation checks, and file manifests
figures/   Generated vector figures used in the manuscript and supplement
```

The repository intentionally excludes internal working notes, superseded
implementations, external source documents, and superseded figure exports.

## Reproduce the numerical analysis

Python 3.10 or newer is recommended. The numerical analysis uses only the
Python standard library.

Clone the repository and enter its root directory:

```bash
git clone https://github.com/BasitAkin/Water-Consumption-Impact_WCI-and-Peak-Delivery-Load-Ratio_PDLR.git
cd Water-Consumption-Impact_WCI-and-Peak-Delivery-Load-Ratio_PDLR
```

Then run:

```bash
python analysis/run_wci_pdlr_analysis.py
```

A successful run writes the result tables to `results/` and reports that:

- 14 audited scenarios were calculated;
- the ten-case comparison retains ten conditional numerical WCI/PDLR anchors;
- 48 one-at-a-time sensitivity checks were completed;
- 23 synthetic boundary and failure-mode cases passed; and
- no unsupported empirical low or high bounds were generated;
- all 15 automated validation checks passed.

## Reproduce the figures

Install the plotting dependencies and run:

```bash
python -m pip install -r requirements.txt
python analysis/build_figures.py
```

This creates:

- `figures/Figure_3ab_WCI.pdf` and its 600-dpi JPG export;
- `figures/Figure_4ab_Decomposition.pdf` and its 600-dpi JPG export; and
- `figures/Figure_S1_Sensitivity_FailureModes.pdf` and its 600-dpi JPG export.

The plotting script checks the ten numerical primary WCI/PDLR anchors, six community-context-eligible cases, direct-peak calculation routes, PDF/JPG validity, and text-layout intersections.

## Principal data and results

- `data/wci_input_provenance.csv` is the authoritative input ledger. Each row
  records one scenario parameter, its evidence class, source, time basis,
  water pathway, capacity convention, and boundary decision.
- `data/community_context_inputs.csv` contains the independently labelled
  jurisdictional comparison inputs used in the contextual figure panels.
- `results/wci_pdlr_comparative_results.csv` contains all ten primary comparison records, including conditional numerical WCI/PDLR values and their calculation status.
- `results/wci_pdlr_scenario_results.csv` contains the comparison anchors and
  documented alternative-boundary scenarios.
- `results/wci_pdlr_analytic_sensitivity.csv` contains the 48 exact algebraic
  one-at-a-time checks at +/-10%, +/-25%, and +/-50%.
- `results/wci_synthetic_boundary_tests.csv` contains the 23 constructed
  boundary, invalid-input, and failure-mode cases.
- `results/wci_validation_tests.csv` records automated reproducibility checks.
- `results/run_metadata.csv` records the runtime environment, conversion
  constant, and input and script hashes.
- `results/figure_manifest.csv` and `results/figure_layout_audit.csv` record
  figure inputs, output hashes, and layout-validation status.

See `docs/DATA_DICTIONARY.md` and `docs/EVIDENCE_AND_BOUNDARIES.md` before
reusing or comparing the scenarios.

## Evidence policy

Evidence codes are `M` (measured or directly reported boundary-specific value),
`R` (reconstructed), `T` (transferred), `A` (author assumption), `P` (planned
or permitted), and `U` (unresolved). A numerical result is calculated only when
the declared numerator and denominator pass the analysis-unit, time, water-
pathway, geographic, and capacity-convention checks. Missing or incompatible
ratio fields remain blank. Supported numerator quantities are retained rather
than suppressed when only the denominator gate fails.

No complete source-backed low/high input set was available for any of the ten
comparison cases. The sensitivity and synthetic outputs are therefore
diagnostic tests, not empirical confidence intervals, site forecasts, or
definitive rank-stability estimates.

## Sensitivity and failure-mode assessment

The repository separates empirical uncertainty from diagnostic sensitivity
testing:

- **One-at-a-time sensitivity checks** report exact algebraic WCI and PDLR
  responses to `+/-10%`, `+/-25%`, and `+/-50%` perturbations in governing
  inputs.
- **Alternative-boundary scenarios** examine different explicitly labelled
  capacity references for the same numerator.
- **Synthetic failure-mode tests** cover unit and scale invariance, missing or
  invalid inputs, zero direct consumption, extreme peaking, available
  headroom, campus aggregation, growth decoupling, and rank reversal.

These tests diagnose construct behaviour and potential misuse. They are not
site observations, empirical uncertainty intervals, operational thresholds,
or forecasts.

## Automated validation

The committed analysis passes checks covering:

- absence of fabricated empirical bounds;
- ten-site anchor coverage, retention of supported numerators, and suppression
  of ratios when denominator eligibility fails;
- leap-year conversion;
- the stated WCI-PDLR identity;
- direct-peak handling without double peaking;
- denominator-specific alternative scenarios;
- the reported rounded WCI span;
- complete sensitivity-design execution; and
- successful execution of all synthetic tests.

The GitHub Actions workflow in `.github/workflows/validate.yml` reruns the
numerical analysis and figure workflow whenever the repository is updated.

## Reuse guidance

Users extending the analysis to another site should:

1. declare the facility, campus, development, utility, or regional analysis
   unit;
2. document each parameter and its evidence class in the input ledger;
3. match numerator and denominator boundaries before calculation;
4. distinguish nominal capacity, reliable supply, allocation, and available
   headroom;
5. retain supported inputs while leaving missing or inadmissible derived fields
   blank;
6. avoid applying an additional peaking factor to a directly reported peak;
   and
7. rerun all validation and sensitivity checks after modifying the inputs.

Cross-site comparisons should remain conditional unless evidence classes and
denominator conventions are harmonised.

## Reproducibility and provenance

The numerical workflow uses the fixed conversion
`1 MGD = 3.785411784 ML/day`. Generated metadata include the Python version,
operating platform, conversion constant, and SHA-256 hashes of the
authoritative input ledger and analysis script.

## Citation

Citation metadata are provided in `CITATION.cff`. GitHub users can select
**Cite this repository** on the repository page to export the software
citation.

Suggested software citation:

> Akinade, B. A., Amanambu, A. C., Frame, J. M., & Ren, S. (2026). *WCI and
> PDLR Reproducibility Package* (Version 1.1.0) [Software]. GitHub.
> https://github.com/BasitAkin/Water-Consumption-Impact_WCI-and-Peak-Delivery-Load-Ratio_PDLR

Please also cite the associated article when its final bibliographic
information is available.

## Licence

The analysis and figure-generation code is released under the MIT License.
External datasets, reports, and source documents remain subject to their
original terms and licences. External source documents are not redistributed;
they are identified in the input ledger and cited in the associated article or
Supplementary Information.
