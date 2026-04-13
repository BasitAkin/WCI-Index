# Water Consumption Impact (WCI) Index

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)

**Reproducible code, data, and companion workbook for the ten-site Water Consumption Impact (WCI) assessment.**

> Akinade, B. A., Amanambu, A. C., & Frame, J. M. (2026). *AI Data Centers and the Water Use Feedback Loop.*

---

## Overview

Aggregate national metrics show data centres consuming less than 1% of total U.S. water, but this masks community-level realities where a single facility's peak-day demand can exceed the entire capacity of its host public water system. The **Water Consumption Impact (WCI)** index resolves this scale mismatch by measuring impact at the utility level, on the worst day.

The WCI quantifies the fraction of a host public water system's peak-day delivery capacity that is permanently consumed by a single data-centre facility's evaporative cooling demand:

```
WCI = C_peak / K = (W / K) x r x PF
```

A three-factor decomposition maps each term to a distinct policy lever:

| Factor | Meaning | Policy Lever | Intervention |
|--------|---------|-------------|--------------|
| **W/K** | Demand scale | **Siting** | Locate facilities in communities with larger utility capacity |
| **r** | Consumptive ratio | **Technology** | Adopt closed-loop or dry-cooling systems to reduce evaporative loss |
| **PF** | Peak amplification | **Management** | Flatten demand peaks through load shifting and storage |

## Variable Definitions

| Symbol | Definition | Units |
|--------|-----------|-------|
| W | Facility water withdrawal | ML/d |
| K | Host utility permitted delivery capacity | ML/d |
| r | Consumptive ratio (C/W; fraction lost to evaporation) | dimensionless |
| PF | Peaking factor (peak-day / average-day consumption) | dimensionless |
| C_avg | Average-day consumption = r x W | ML/d |
| C_peak | Peak-day consumption = C_avg x PF | ML/d |
| HH_eq | Household equivalents = (C_avg x 365.25) / 0.4146 | households |
| g | Compound annual growth rate | dimensionless |

## Risk Classification

| Tier | WCI Range | Interpretation |
|------|----------|----------------|
| **OVERLOAD** | > 100% | Peak-day demand exceeds the entire utility capacity |
| **SEVERE** | 50 -- 100% | More than half of capacity claimed on peak day |
| **HIGH** | 25 -- 50% | Growth headroom eliminated |
| **MODERATE** | 10 -- 25% | Noticeable; demand management warranted |
| **LOW** | 5 -- 10% | Minor contribution; standard planning suffices |
| **MINIMAL** | < 5% | Negligible impact |

## Ten-Site Results

| Rank | Site | State | Operator | WCI (%) | Risk Class | Household Equiv. | Breach Year (13% CAGR) |
|------|------|-------|----------|---------|------------|-------------------|------------------------|
| 1 | Lebanon | IN | Meta | 134.0 | OVERLOAD | 3,261 | Already breached |
| 2 | Council Bluffs | IA | Google | 59.9 | SEVERE | 9,220 | 2029 |
| 3 | Mayes County | OK | Google | 57.0 | SEVERE | 7,610 | 2029 |
| 4 | The Dalles | OR | Google | 48.6 | HIGH | 3,301 | 2030 |
| 5 | Douglas County | GA | Google | 31.4 | HIGH | 3,348 | 2034 |
| 6 | Wisconsin Site | WI | Microsoft | 26.6 | HIGH | 59 | 2035 |
| 7 | Botetourt County | VA | Google | 13.8 | MODERATE | 5,136 | 2041 |
| 8 | Midlothian | TX | Google | 3.5 | MINIMAL | 1,665 | 2052 |
| 9 | Memphis | TN | xAI | 1.3 | MINIMAL | 2,568 | 2060 |
| 10 | Henderson | NV | Google | 0.2 | MINIMAL | 1,893 | Beyond 2074 |

The index spans nearly three orders of magnitude, from 0.2% at a large municipal utility (Henderson, NV; SNWA 900 MGD) to 134% at a small rural system (Lebanon, IN; 4.6 MGD) where peak demand exceeds the entire municipal water supply.

## Repository Structure

```
Water-Consumption-Impact_WCI_Index/
|
|-- README.md                       This file
|-- LICENSE                         MIT License
|-- CITATION.cff                    Machine-readable citation metadata
|-- requirements.txt                Python dependencies
|-- .gitignore                      Git ignore rules
|
|-- workbook/
|   |-- WCI_10Site_Workbook.xlsx   Companion Excel workbook with live formulas
|                                        (7 sheets, 1,080+ formulas, zero errors)
|
|-- data/
|   |-- site_inputs.csv                 Raw input data for 10 sites
|   |-- wci_decomposition.csv           Three-factor decomposition results
|   |-- community_equivalence.csv       Household equivalents and community share
|   |-- growth_projections_high.csv     24% CAGR scenario (2024-2035)
|   |-- growth_projections_moderate.csv 13% CAGR scenario (2024-2035)
|   |-- ranked_summary.csv             All sites ranked by WCI
|   |-- policy_sensitivity.csv         Policy lever sensitivity analysis
|
|-- src/
|   |-- __init__.py                 Package initialisation
|   |-- wci_calculator.py           Core WCI computation module (Eqs. 1-9)
|   |-- visualize.py                Publication-quality figure generation
|
|-- results/
|   |-- wci_results.csv             Full computed results (all metrics, all sites)
|   |-- fig_wci_bar.png             WCI by site (colour-coded by risk tier)
|   |-- fig_three_factor.png        Three-factor decomposition
|   |-- fig_growth_trajectories.png Growth projections to 2035
|   |-- fig_policy_levers.png       Policy lever effectiveness comparison
|
|-- docs/
|   |-- DATA_DICTIONARY.md          Variable definitions, units, and provenance
|   |-- METHODOLOGY.md              Complete equation derivations and assumptions
|
|-- references/
|   |-- README.md                   Catalogue of all source documents with URLs
```

## Companion Excel Workbook

The file `workbook/WCI_10Site_Workbook_v6_6.xlsx` is the self-contained companion workbook submitted as supplementary material with the manuscript. It contains seven sheets:

| Sheet | Contents |
|-------|----------|
| 0. Overview & Methods | Purpose, sheet index, equations, variable definitions, data sources, colour legend |
| 1. Inputs | Raw site inputs (W, r, K, PF, population) with source citations. Yellow cells are editable. |
| 2. WCI Decomposition | Three-factor decomposition and six-tier risk classification |
| 3. Community Equivalence | Household equivalents and facility share of community water use |
| 4. Growth Projections | Year-by-year WCI to 2035 under HIGH (24%) and MODERATE (13%) CAGR |
| 5. Ranked Summary | One-row-per-site reference with all metrics |
| 6. Chart Data | Tidy data blocks feeding manuscript figures |
| 7. Policy Sensitivity | Siting, technology, and management lever analysis |

Every formula is live. Change any yellow input cell and all downstream values, risk classifications, and chart data recalculate automatically. The CSV files in `data/` are exports from this workbook.

## Quick Start

### Requirements

```
Python >= 3.8
pandas >= 1.3
numpy >= 1.20
matplotlib >= 3.4
```

### Installation

```bash
git clone https://github.com/BasitAkin/Water-Consumption-Impact_WCI_Index.git
cd Water-Consumption-Impact_WCI_Index
pip install -r requirements.txt
```

### Run the Full Analysis

```bash
python src/wci_calculator.py
```

Reads `data/site_inputs.csv`, computes all WCI metrics for 10 sites, and writes results to `results/wci_results.csv`.

### Generate Figures

```bash
python src/visualize.py
```

Produces four publication-quality PNG figures (300 DPI) in `results/`.

### Use as a Python Module

```python
from src.wci_calculator import compute_wci, classify_risk, run_all

# Single-site calculation
result = compute_wci(W_ML_d=4.81, r=0.77, K_ML_d=17.41, PF=6.3)
print(f"WCI = {result['WCI']:.2%}")   # WCI = 133.93%
print(classify_risk(result['WCI']))    # OVERLOAD

# Full batch analysis
df = run_all('data/site_inputs.csv')
print(df[['site', 'WCI', 'risk_class', 'HH_equiv']].to_string())
```

### Apply to Your Own Sites

Create a CSV with these columns:

| Column | Required | Description |
|--------|----------|-------------|
| site | Yes | Site name |
| state | No | State or jurisdiction |
| operator | No | Data-centre operator |
| W_ML_d | Yes | Withdrawal in ML/d |
| r | Yes | Consumptive ratio (0-1) |
| K_MGD or K_ML_d | Yes | Host utility capacity |
| PF | Yes | Peaking factor |
| population | No | Population served by host utility |

Then:

```python
from src.wci_calculator import run_all
results = run_all('path/to/your_data.csv')
```

## Equations

| # | Equation | Description |
|---|----------|-------------|
| 1 | WCI = (W/K) x r x PF | Water Consumption Impact index |
| 2 | C_avg = r x W | Average-day consumption |
| 3 | C_peak = C_avg x PF | Peak-day consumption |
| 4 | HH_eq = (C_avg x 365.25) / 0.4146 | Household equivalents |
| 5 | Share = C_avg / (pop x 0.000303) | Community water share |
| 6 | WCI(t) = WCI_0 x (1+g)^t | Growth projection |
| 7 | WCI_sit = (alpha x W/K) x r x PF | Siting lever (alpha = 0.75) |
| 8 | WCI_tec = (W/K) x min(r, 0.25) x PF | Technology lever |
| 9 | WCI_mgt = (W/K) x r x min(PF, 2.0) | Management lever |

## Data Sources

All input data are sourced from publicly available documents. Full details in [`references/README.md`](references/README.md).

| Source | Sites Covered | Data Provided |
|--------|--------------|---------------|
| [Google Environmental Report 2025](https://sustainability.google/reports/google-2025-environmental-report/) (pp. 110-111) | Council Bluffs, Mayes Co., The Dalles, Douglas Co., Midlothian, Henderson | W, r (EY-assured) |
| Han et al. 2026 | Lebanon, Wisconsin Site | W, PF |
| [Project Domino Agreement 2025](https://lebanon.in.gov/) | Lebanon | K = 4.6 MGD |
| [Google Botetourt County FAQ](https://www.botetourtva.gov/1023/Google-Data-Center-Water) | Botetourt County | W |
| [GEAA 2025](https://www.protectouraquifer.org/issues/xai-supercomputer) | Memphis | W |
| [Wisconsin Public Radio 2025](https://www.wpr.org/news/mount-pleasant-approves-site-plans-microsoft-data-center-expansion) | Wisconsin Site | W, PF |
| [Shehabi et al. 2024 (LBNL-2001637)](https://eta.lbl.gov/publications/2024-lbnl-data-center-energy-usage-report) | Growth scenario | National DC water growth |
| [USGS Circular 1441 (2015)](https://pubs.usgs.gov/circ/1441/) | Constants | H_avg, h_pc |
| State environmental permits and utility annual reports | All 10 sites | K (utility capacity) |

## Verification

All 10 WCI values computed by `src/wci_calculator.py` match the companion Excel workbook to within floating-point rounding tolerance (< 0.000001 absolute difference per site):

```
Lebanon              computed=1.339298  expected=1.339298  PASS
Council Bluffs       computed=0.599003  expected=0.599003  PASS
Mayes County         computed=0.570464  expected=0.570464  PASS
The Dalles           computed=0.486085  expected=0.486085  PASS
Douglas County       computed=0.313774  expected=0.313774  PASS
Wisconsin Site       computed=0.265650  expected=0.265650  PASS
Botetourt County     computed=0.137500  expected=0.137500  PASS
Midlothian           computed=0.034666  expected=0.034666  PASS
Memphis              computed=0.013430  expected=0.013430  PASS
Henderson            computed=0.001577  expected=0.001577  PASS
```

## License

[MIT License](LICENSE)

## Citation

If you use this code, data, or workbook, please cite:

```bibtex
@article{Akinade2026_WCI,
  author  = {Akinade, Basit A. and Amanambu, Amobichukwu C. and Frame, Jonathan M.},
  title   = {{AI} Data Centers and the Water Use Feedback Loop},
  journal = {Earth-Science Reviews},
  year    = {2026},
  note    = {Submitted}
}
```

## Contact

**Amobichukwu C. Amanambu** (corresponding author)
Water INtelligence and Geospatial Sensing (WINGS) Laboratory
Department of Geography and the Environment
The University of Alabama, Tuscaloosa, AL, USA
