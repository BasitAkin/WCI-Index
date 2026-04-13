# Data Dictionary

This document defines every variable in the WCI datasets and traces each value to its source document.

## site_inputs.csv

The primary input dataset. Each row represents one data-centre facility and its host public water system.

| Column | Type | Units | Definition | Source |
|--------|------|-------|-----------|--------|
| site | str | -- | Name of the host community or county | -- |
| state | str | -- | US state abbreviation | -- |
| operator | str | -- | Data-centre operator (Google, Meta, Microsoft, xAI) | -- |
| W_ML_yr | float | ML/yr | Annual water withdrawal reported by operator | Google ER 2025 p.110; Han 2026 |
| W_MGD | float | MGD | Daily withdrawal in million gallons per day | Converted: W_ML_yr / 365.25 / 3.78541 |
| W_ML_d | float | ML/d | Daily withdrawal in megalitres per day | W_ML_yr / 365.25, or W_MGD x 3.78541 |
| r | float | -- | Consumptive ratio (C/W). Fraction of withdrawn water lost to evaporation | Google ER 2025 (site-specific); 0.77 industry average (Han 2026) |
| C_avg_ML_d | float | ML/d | Average-day consumption = r x W | Computed (Eq. 2) |
| K_MGD | float | MGD | Host utility permitted delivery capacity | State permits, utility reports |
| K_ML_d | float | ML/d | K converted to ML/d = K_MGD x 3.78541 | Computed |
| PF | float | -- | Peaking factor: peak-day / average-day consumption | Site-specific permits; 2.5 default |
| C_peak_ML_d | float | ML/d | Peak-day consumption = C_avg x PF | Computed (Eq. 3) |
| population | int | persons | Population served by the host water system | US Census / utility records |
| PUE | float | -- | Power Usage Effectiveness (2024) | Google ER 2025; "--" if not disclosed |
| source | str | -- | Source document(s) for this row's data | -- |
| notes | str | -- | Additional context (multiple facilities, data quality) | -- |

## Key Constants

| Constant | Value | Source |
|----------|-------|--------|
| H_avg | 0.4146 ML/household/year | USGS 2015 Circular 1441 |
| h_pc | 0.000303 ML/person/day | USGS 2015 Circular 1441 (80 gal/day) |
| 1 MGD | 3.78541 ML/d | Standard conversion |
| r_industry | 0.77 | Han et al. 2026, Table 2 (hyperscale weighted average) |

## Consumptive Ratio (r) by Site

For Google facilities, r is computed directly from site-level withdrawal (W) and consumption (C) reported in the Google 2025 Environmental Report (pp. 110-111), externally assured by Ernst & Young.

| Site | r | Basis |
|------|---|-------|
| Lebanon | 0.770 | Industry average (not Google) |
| Council Bluffs | 0.716 | C=1,010.2 / W=1,410.3 Mgal |
| Mayes County | 0.752 | C=833.2 / W=1,108.3 Mgal |
| The Dalles | 0.784 | C=361.4 / W=461.1 Mgal |
| Douglas County | 0.826 | C=366.9 / W=444.1 Mgal |
| Wisconsin Site | 0.770 | Industry average (Microsoft) |
| Botetourt County | 0.770 | Industry average (permit only) |
| Midlothian | 0.825 | C=182.3 / W=221.0 Mgal |
| Memphis | 0.770 | Industry average (xAI) |
| Henderson | 0.576 | C=207.4 / W=359.9 Mgal (low due to discharge reuse) |

## Peaking Factor (PF) by Site

| Site | PF | Basis |
|------|-----|-------|
| Lebanon | 6.3 | Permit application (Project Domino) |
| Council Bluffs | 6.5 | Permit records |
| Mayes County | 2.5 | Warm-climate default |
| The Dalles | 2.21 | Measured ratio (Google/City records) |
| Douglas County | 2.5 | Warm-climate default |
| Wisconsin Site | 30 | Documented peak-to-average ratio (Han 2026 Section 3.1.2; WPR 2025) |
| Botetourt County | 2.5 | Default |
| Midlothian | 2.5 | Default |
| Memphis | 4.5 | Extreme-demand assumption |
| Henderson | 2.5 | Default |

## Host Utility Capacity (K) Sources

| Site | K (MGD) | Source |
|------|---------|--------|
| Lebanon, IN | 4.6 | Project Domino Agreement 2025, Section 2(c); IDEM permit IN5206003 |
| Council Bluffs, IA | 30 | Iowa DNR / utility annual report |
| Mayes County, OK | 10 | Oklahoma DEQ / Mayes County RWD |
| The Dalles, OR | 4.5 | City of The Dalles Water Master Plan |
| Douglas County, GA | 8 | Douglas County Water & Sewer Authority |
| Wisconsin Site, WI | 2 | WI DNR / Racine Water Utility |
| Botetourt County, VA | 28 | Western Virginia Water Authority |
| Midlothian, TX | 36 | TCEQ (Tayman Plant 12 MGD + Auger Plant 24 MGD) |
| Memphis, TN | 258 | Memphis Light, Gas & Water (MLGW) |
| Henderson, NV | 900 | Southern Nevada Water Authority (SNWA) |
