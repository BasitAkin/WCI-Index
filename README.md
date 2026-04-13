# Water Consumption Impact (WCI) Index

**Reproducible code and data for the ten-site WCI assessment presented in:**

> Akinade, B. A., Amanambu, A. C., & Frame, J. M. (2026). *AI Data Centers and the Water Use Feedback Loop.* Earth-Science Reviews (submitted).

---

## What is the WCI?

The **Water Consumption Impact** index quantifies the fraction of a host public water system's peak-day delivery capacity that is permanently consumed by a single data-centre facility's evaporative cooling demand:

```
WCI = C_peak / K = (W / K) x r x PF
```

where:

| Symbol | Definition | Units |
|--------|-----------|-------|
| W | Facility water withdrawal | ML/d |
| K | Host utility permitted delivery capacity | ML/d |
| r | Consumptive ratio (C/W; fraction lost to evaporation) | dimensionless |
| PF | Peaking factor (peak-day / average-day consumption) | dimensionless |
| C_avg | Average-day consumption = r x W | ML/d |
| C_peak | Peak-day consumption = C_avg x PF | ML/d |

The three-factor decomposition maps each term to a distinct **policy lever**:

| Factor | Policy Lever | Intervention |
|--------|-------------|-------------|
| W/K | **Siting** | Locate facilities in communities with larger utility capacity |
| r | **Technology** | Adopt closed-loop or dry-cooling systems to reduce evaporative loss |
| PF | **Management** | Flatten demand peaks through load shifting and storage |

## Risk Classification

| Tier | WCI Range | Interpretation |
|------|----------|----------------|
| OVERLOAD | > 100% | Peak-day demand exceeds the entire utility capacity |
| SEVERE | 50 -- 100% | More than half of capacity claimed on peak day |
| HIGH | 25 -- 50% | Growth headroom eliminated |
| MODERATE | 10 -- 25% | Noticeable; demand management warranted |
| LOW | 5 -- 10% | Minor contribution; standard planning suffices |
| MINIMAL | < 5% | Negligible impact |

## Ten-Site Results

| Rank | Site | State | Operator | WCI (%) | Risk Class |
|------|------|-------|----------|---------|------------|
| 1 | Lebanon | IN | Meta | 134.0 | OVERLOAD |
| 2 | Council Bluffs | IA | Google | 59.9 | SEVERE |
| 3 | Mayes County | OK | Google | 57.0 | SEVERE |
| 4 | The Dalles | OR | Google | 48.6 | HIGH |
| 5 | Douglas County | GA | Google | 31.4 | HIGH |
| 6 | Wisconsin Site | WI | Microsoft | 26.6 | HIGH |
| 7 | Botetourt County | VA | Google | 13.8 | MODERATE |
| 8 | Midlothian | TX | Google | 3.5 | MINIMAL |
| 9 | Memphis | TN | xAI | 1.3 | MINIMAL |
| 10 | Henderson | NV | Google | 0.2 | MINIMAL |

## Repository Structure

```
WCI-Index/
|-- README.md                  This file
|-- LICENSE                    MIT License
|-- CITATION.cff               Machine-readable citation metadata
|-- requirements.txt           Python dependencies
|
|-- data/
|   |-- site_inputs.csv        Raw input data for 10 sites (W, r, K, PF, pop)
|   |-- wci_decomposition.csv  Three-factor decomposition results
|   |-- community_equivalence.csv   Household equivalents and community share
|   |-- growth_projections_high.csv      24% CAGR scenario (2024-2035)
|   |-- growth_projections_moderate.csv  13% CAGR scenario (2024-2035)
|   |-- ranked_summary.csv     All sites ranked by WCI
|   |-- policy_sensitivity.csv Policy lever sensitivity analysis
|
|-- src/
|   |-- wci_calculator.py      Core WCI computation module (Eqs. 1-9)
|   |-- visualize.py           Publication-quality figure generation
|
|-- results/
|   |-- wci_results.csv        Full computed results (all metrics)
|   |-- fig_wci_bar.png        WCI by site
|   |-- fig_three_factor.png   Three-factor decomposition
|   |-- fig_growth_trajectories.png   Growth projections
|   |-- fig_policy_levers.png  Policy lever effectiveness
|
|-- docs/
|   |-- DATA_DICTIONARY.md     Variable definitions and data sources
|   |-- METHODOLOGY.md         Complete equation derivations and assumptions
|
|-- references/
|   |-- README.md              Catalogue of source documents
```

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
git clone https://github.com/<your-org>/WCI-Index.git
cd WCI-Index
pip install -r requirements.txt
```

### Run the Full Analysis

```bash
python src/wci_calculator.py
```

This reads `data/site_inputs.csv`, computes all WCI metrics, and writes results to `results/wci_results.csv`.

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

# Batch analysis from CSV
df = run_all('data/site_inputs.csv')
print(df[['site', 'WCI', 'risk_class']].to_string())
```

### Apply to Your Own Sites

Create a CSV with these columns:

| Column | Required | Description |
|--------|----------|-------------|
| site | Yes | Site name |
| state | No | State/jurisdiction |
| operator | No | Data-centre operator |
| W_ML_d | Yes | Withdrawal in ML/d |
| r | Yes | Consumptive ratio (0-1) |
| K_MGD | Yes* | Host utility capacity in MGD |
| K_ML_d | Yes* | Host utility capacity in ML/d |
| PF | Yes | Peaking factor |
| population | No | Population served by host utility |

*Provide either K_MGD or K_ML_d; the calculator converts automatically.

Then run:

```python
from src.wci_calculator import run_all
results = run_all('your_data.csv')
```

## Equations Reference

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

All input data are sourced from publicly available documents:

| Source | Sites Covered | Data Provided |
|--------|--------------|---------------|
| Google Environmental Report 2025 (pp. 110-111) | Council Bluffs, Mayes Co., The Dalles, Douglas Co., Midlothian, Henderson | W, r (EY-assured) |
| Han et al. 2026 | Lebanon, Wisconsin Site | W, PF |
| Project Domino Agreement 2025 | Lebanon | K |
| Google Botetourt County FAQ | Botetourt County | W |
| GEAA 2025 | Memphis | W |
| Wisconsin Public Radio 2025 | Wisconsin Site | W, PF |
| Microsoft Environmental Sustainability Report 2025 | (growth scenario) | Fleet-level W trends |
| Shehabi et al. 2024 (LBNL-2001637) | (growth scenario) | National DC water growth |
| USGS Circular 1441 (2015) | (constants) | H_avg, h_pc |
| State environmental permits and utility reports | All 10 sites | K (utility capacity) |

See `references/README.md` for the complete catalogue with URLs.

## Verification

All 10 WCI values computed by `wci_calculator.py` match the companion Excel workbook (`DualBurden_10Site_Workbook_v6_6`) to within floating-point rounding tolerance (< 0.000001 absolute difference per site). See the verification output in the paper's QA/QC audit.

## License

MIT License. See [LICENSE](LICENSE).

## Citation

If you use this code or data, please cite:

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

Amobichukwu C. Amanambu (corresponding author)
Water INtelligence and Geospatial Sensing (WINGS) Laboratory
Department of Geography and the Environment
The University of Alabama, Tuscaloosa, AL, USA
