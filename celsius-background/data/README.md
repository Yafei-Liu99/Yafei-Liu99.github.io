# SIPP state population estimates

The maps show adults aged 18+, matching the original project scope. They do not show all-age populations or measured temperature-unit use.

## Source data

- 2023: [Official Census SIPP microdata](https://www2.census.gov/programs-surveys/sipp/data/datasets/2023/pu2023_csv.zip), downloaded 2026-09-22. Reference year 2022. SHA-256: `9c5363d56aca2041db20d46d17b81e9be931eb5b18bd5f5238b367d2dd7fb74b`.
- 2025: existing project [state_mapping.csv](https://github.com/Yafei-Liu99/sipp-yale-immigration-climate-map/blob/c0d2fa0249e65b8b7e3d82b7a0592447f44ad47e/results/state_mapping.csv), reference year 2024. The repository may require access. No new 2025 microdata processing was performed for this update.

## Aggregation

1. Keep MONTHCODE = 12, THHLDSTATUS in [1, 2], TAGE >= 18.
2. Group by TST_INTV (state of the interview address), keeping the 50 states and DC. In 2023, three records had code 61, which is not a U.S. state/DC code; their combined weight was zero and they are excluded.
3. An immigrant is EBORNUS = 2 and (ECITIZEN = 2 or ENATCIT in [1, 2, 3]).
4. Celsius-background immigrants are immigrants with TBORNPLACE in [61, 62, 64, 65]. All remaining immigrants are mixed or unclassified, including code 63 (Americas and Caribbean), code 66 (Other), and any unrecognized birthplace.
5. Sum WPFINWGT separately for Celsius-background immigrants, mixed/unclassified immigrants, and all eligible adults. The total adult population includes both immigrant groups and non-immigrants; it is not a third mutually exclusive group.
6. Store full-precision weighted counts in CSV. Round only when displaying people. For 2025, counts are reconstructed from the existing unrounded state shares multiplied by adult_population; the two immigrant counts agree with immigrant_population within 0.001 person in every state.

Each person appears once in the retained December sample. No division by 12 is used. The 2023 state totals sum to 256,388,915.36207038 adults, including 17,271,038.9932307 Celsius-background immigrants and 20,705,773.231689498 mixed/unclassified immigrants. Retained 2023 sample: 32,141 adults, including 4,399 immigrants.

## Interpretation

Classification is a research assumption based on broad birthplace regions, not a survey response about Celsius/Fahrenheit. No Fahrenheit-user count is calculated. States with no sampled immigrants are displayed as “No estimate” for both immigrant counts; their raw weighted sum is zero in the CSV. Other observed zero subgroup counts are sample estimates, not proof of absence. Hatching indicates fewer than 50 immigrant sample records. This threshold is a project display rule, not an official reliability criterion. No standard errors or significance tests were calculated.

Both maps color the estimated Celsius-background immigrant population using the same thresholds: 100,000; 250,000; 500,000; 1,000,000; 2,000,000 people. The original percentage shading was replaced with population shading to match the requested count display.

## Reproduce 2023

Place the official pu2023_csv.zip in this directory, install pandas, and run `python3 aggregate_sipp_2023.py`. The included state_population_2025.csv supplies only state names. Only aggregated data are hosted here; the raw microdata are obtained from Census.
