"""Reproduce the 2023 state estimates using the existing project's adult sample."""
from pathlib import Path
import json
import zipfile
import pandas as pd

HERE = Path(__file__).resolve().parent
COLS = ['SSUID', 'PNUM', 'MONTHCODE', 'THHLDSTATUS', 'TST_INTV',
        'TBORNPLACE', 'EBORNUS', 'ECITIZEN', 'ENATCIT', 'TAGE', 'WPFINWGT']
parts = []
with zipfile.ZipFile(HERE / 'pu2023_csv.zip') as z:
    print(z.namelist(), flush=True)
    with z.open('pu2023.csv') as f:
        for chunk in pd.read_csv(f, sep='|', usecols=COLS,
                                 dtype={'SSUID': str}, chunksize=50000):
            keep = (chunk.MONTHCODE.eq(12) & chunk.THHLDSTATUS.isin([1, 2])
                    & chunk.TAGE.ge(18))
            parts.append(chunk.loc[keep].copy())
            print('Retained adults:', sum(map(len, parts)), flush=True)
adults = pd.concat(parts, ignore_index=True)
assert not adults.duplicated(['SSUID', 'PNUM']).any()
assert adults.WPFINWGT.notna().all() and adults.WPFINWGT.ge(0).all()
assert adults.TST_INTV.notna().all()
adults['immigrant'] = (adults.EBORNUS.eq(2)
    & (adults.ECITIZEN.eq(2) | adults.ENATCIT.isin([1, 2, 3])))
adults['celsius'] = adults.immigrant & adults.TBORNPLACE.isin([61, 62, 64, 65])
adults['mixed_unclassified'] = adults.immigrant & ~adults.celsius
names = pd.read_csv(HERE / 'state_population_2025.csv').set_index('state_fips').state.to_dict()
excluded = adults.loc[~adults.TST_INTV.isin(names)]
print('Excluded non-state records:', len(excluded), 'weight:', excluded.WPFINWGT.sum(), flush=True)
adults = adults.loc[adults.TST_INTV.isin(names)].copy()
assert set(adults.TST_INTV.astype(int)) == set(names)
rows = []
for state, frame in adults.groupby('TST_INTV'):
    w = frame.WPFINWGT
    rows.append(dict(state_fips=int(state), state=names[int(state)],
        adult_sample_n=len(frame), immigrant_sample_n=int(frame.immigrant.sum()),
        celsius_immigrant_population=float(w[frame.celsius].sum()),
        mixed_unclassified_immigrant_population=float(w[frame.mixed_unclassified].sum()),
        total_adult_population=float(w.sum())))
result = pd.DataFrame(rows)
assert (result.celsius_immigrant_population
    + result.mixed_unclassified_immigrant_population
    <= result.total_adult_population + 1e-6).all()
assert abs(result.total_adult_population.sum() - adults.WPFINWGT.sum()) < 1e-5
result.to_csv(HERE / 'state_population_2023.csv', index=False)
print(json.dumps(dict(adult_sample_n=len(adults),
    immigrant_sample_n=int(adults.immigrant.sum()),
    totals=result.select_dtypes('number').sum().to_dict(),
    immigrant_birth_codes=adults.loc[adults.immigrant, 'TBORNPLACE'].value_counts().to_dict()), indent=2))
