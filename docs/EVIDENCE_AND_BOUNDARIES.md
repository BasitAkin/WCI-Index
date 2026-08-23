# Evidence and boundary decisions

## Calculation gates

Before WCI or PDLR is calculated, the numerator and denominator are checked for
agreement in:

1. analysis unit (facility, campus, development, utility, or region);
2. period and operating stage;
3. water pathway (potable, reclaimed, groundwater, surface water, or combined);
4. geographic/service boundary; and
5. capacity convention (nominal treatment, reliable supply, allocation,
   available headroom, or regional capacity).

An authoritative value is not automatically admissible. If its boundary does
not match the numerator, WCI and PDLR are not calculated or the comparison is
retained only as a clearly labelled alternative scenario. Supported numerator
quantities remain visible in the machine-readable results.

## Ten-case denominator decisions

| Case | Retained capacity decision | Interpretation |
|---|---|---|
| Lebanon, Indiana | 4.6 MGD existing system; 25 MGD planned wholesale allocation kept separately | The 4.6 MGD comparison is a pre-expansion counterfactual; no total post-expansion capacity is inferred. |
| Council Bluffs, Iowa | Current combined capacity unresolved | The accessible plant-component record does not verify the legacy 30 MGD sum as the current combined applicable capacity; WCI and PDLR are not calculated. |
| Mayes County, Oklahoma | 50 MGD park-owned potable-system nominal capacity | Distinct from the reported 32 MGD available headroom. |
| The Dalles, Oregon | Current capacity unresolved; 4.5 MGD retained only as a historical alternative | The 4.5 MGD value is documented for 2006 and is not represented as current after a newer plan. |
| Douglas County, Georgia | Combined denominator unresolved; 3 MGD reclaimed subsystem retained separately | The campus numerator combines potable and reclaimed water, so the reclaimed-only capacity is not used as a combined denominator. |
| Mount Pleasant, Wisconsin | 40 MGD Racine system filtration capacity, conditionally retained | Current confirmation and final parcel/service-boundary matching remain pending. |
| Botetourt County, Virginia | 24 MGD serving-plant nominal capacity | The 2 MGD project quantity is a reported maximum and is not peaked again. |
| Memphis, Tennessee | 30 MGD serving-plant anchor; 258 MGD whole-system alternative | The 2 MGD local headroom is not treated as nominal treatment capacity. |
| Midlothian, Texas | 36 MGD city-system nominal capacity | Retained conditionally on the declared city-system boundary. |
| Henderson, Nevada | 900 MGD regional SNWA capacity | This is not local Henderson capacity, allocation, or available headroom. |

## Interpretation limits

The ten comparison rows do not share one evidence class or one denominator
type. Seven produce conditional numerical anchors; three retain supported
numerators but do not produce WCI or PDLR because the denominator gate fails.
No case has a complete verified set of low and high inputs. Consequently:

- no empirical confidence interval is reported;
- no definitive cross-site ranking is claimed;
- no site-specific threshold-crossing forecast is reported;
- WCI or PDLR unity is not interpreted as utility failure; and
- the one-at-a-time and synthetic tests diagnose construct behaviour rather
  than empirical site uncertainty.

The complete parameter-level source names, years, locators, evidence codes,
and boundary notes are retained in `data/wci_input_provenance.csv`. External
source documents are cited in the manuscript and Supplementary Information and
are not redistributed in this repository.

## Community-context eligibility

The household-equivalent and residential-use-equivalent calculations require
reported or defensibly reconstructed annual-average consumption. Six FY2024
operating Google campuses pass this gate. Lebanon reports a planned 2031
full-buildout peak; Mount Pleasant reports a planned annual envelope and peak;
Botetourt County reports a maximum reservation with actual use described as
seasonal and lower; and Memphis reports an "up to" service maximum. Those four
records are not converted into average consumption by assumption.
