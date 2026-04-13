# Methodology

Complete derivation and rationale for the Water Consumption Impact (WCI) framework. This document supplements Section 6 of the manuscript.

## 1. Problem Statement

National-scale volumetric assessments of data-centre water use mask community-level impacts. A single facility's peak-day consumptive demand can claim over 100% of a small utility's delivery capacity, yet aggregate national figures show data centres consuming less than 1% of total US water. The WCI resolves this scale mismatch by measuring impact at the utility level, on the worst day.

## 2. WCI Definition (Eq. 1)

```
WCI = C_peak / K
```

WCI is the ratio of a facility's peak-day consumptive water use to the host public water system's total permitted delivery capacity. It answers: "On the worst day, what fraction of the utility's full capacity is consumed by this one facility?"

### Three-Factor Decomposition

Substituting C_peak = r x W x PF:

```
WCI = (W / K) x r x PF
```

Each factor is independent and controllable:

**W/K (demand scale):** The ratio of facility withdrawal to utility capacity. Determined by siting decisions: where the facility is built and how large the host utility is.

**r (consumptive ratio):** The fraction of withdrawn water permanently removed by evaporation. Determined by cooling technology: wet cooling towers yield r = 0.70-0.90; closed-loop or dry-cooling hybrids can achieve r < 0.25.

**PF (peak amplification):** The ratio of the worst day's consumption to the average day. Determined by demand management: load shifting, thermal storage, and contractual peak caps.

## 3. Supporting Equations

### Eq. 2: Average-Day Consumption

```
C_avg = r x W
```

The steady-state daily consumptive load. This is the volume of water that does not return to the source.

### Eq. 3: Peak-Day Consumption

```
C_peak = C_avg x PF = r x W x PF
```

The maximum single-day consumptive demand. This is the design-critical value for utility infrastructure sizing.

### Eq. 4: Household Equivalence

```
HH_equiv = (C_avg x 365.25) / H_avg
```

where H_avg = 0.4146 ML/household/year (USGS 2015 Circular 1441). Translates facility water use into a number recognisable to non-specialist audiences.

### Eq. 5: Community Water Share

```
Share = C_avg / (pop x h_pc)
```

where h_pc = 0.000303 ML/person/day (80 gal/day, USGS 2015). The facility's average-day consumption expressed as a fraction of the host community's total residential water use.

### Eq. 6: Growth Projection

```
WCI(t) = WCI_0 x (1 + g)^t
```

Compound growth model. Two scenarios are used:

| Scenario | CAGR (g) | Basis |
|----------|----------|-------|
| HIGH | 24% | Microsoft observed water CAGR 2022-2024 |
| MODERATE | 13% | US national DC water growth 2014-2023 (Shehabi 2024) |

The breach year is the first calendar year t in which WCI(t) >= 1.00 (OVERLOAD threshold).

### Eqs. 7-9: Policy Levers

Each lever is applied in isolation, holding the other two factors at current values.

**Eq. 7 (Siting):**
```
WCI_siting = (alpha x W/K) x r x PF,    alpha = 0.75
```
Models relocating the facility to a utility 33% larger (or equivalently, expanding the host utility by 33%).

**Eq. 8 (Technology):**
```
WCI_tech = (W/K) x min(r, r_target) x PF,    r_target = 0.25
```
Models adopting closed-loop or dry-cooling hybrid technology. The min() guard ensures sites already below the target are not penalised.

**Eq. 9 (Management):**
```
WCI_mgmt = (W/K) x r x min(PF, PF_target),    PF_target = 2.0
```
Models effective demand-side management that flattens peak demand to no more than 2x the daily average.

## 4. Risk Classification

The six-tier system maps WCI values to operational implications:

| Tier | Threshold | Meaning |
|------|-----------|---------|
| OVERLOAD | WCI > 1.00 | The facility's peak-day demand alone exceeds the utility's entire permitted capacity. The community physically cannot serve both the data centre and its residents without infrastructure expansion or curtailment. |
| SEVERE | 0.50 < WCI <= 1.00 | More than half of utility capacity claimed. Routine stress events (drought, equipment outage) will produce shortages. |
| HIGH | 0.25 < WCI <= 0.50 | A quarter to a half of capacity consumed. Growth headroom eliminated; any additional facilities compound stress. |
| MODERATE | 0.10 < WCI <= 0.25 | Noticeable but manageable. Monitoring and demand-side management warranted. |
| LOW | 0.05 < WCI <= 0.10 | Minor contribution. Standard utility planning suffices. |
| MINIMAL | WCI <= 0.05 | Negligible. Within routine variation in utility demand. |

## 5. Assumptions and Limitations

**Steady-state model:** WCI uses a single-period snapshot. It does not model intra-annual seasonality or multi-year infrastructure expansion timelines.

**Peaking factor uncertainty:** PF is the most uncertain input. For sites without measured peak-day records, default values (2.5 for warm climates, 4.5 for extreme demand) are adopted from the literature. Sensitivity to PF is quantified through the management lever (Eq. 9).

**Single-facility scope:** WCI measures one facility against one utility. Cumulative effects of multiple facilities sharing a single utility are captured by summing WCI values, which is conservative (it ignores demand coincidence).

**US demonstration:** The ten-site assessment uses US data because utility capacity (K) is standardised through state environmental permits. The framework is transferable to any jurisdiction where K is publicly reported.

## 6. Reproducibility

All calculations are implemented in `src/wci_calculator.py` using only standard scientific Python libraries (pandas, numpy). Every intermediate value can be traced from `data/site_inputs.csv` through the equations above to `results/wci_results.csv`. The companion Excel workbook provides an independent verification path with live formulas.
