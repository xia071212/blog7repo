"""Independent checks of saved inputs and arithmetic; not survey inference."""
from pathlib import Path
import hashlib,json,gzip,zipfile
import pandas as pd
import numpy as np
R=Path(__file__).resolve().parents[1]
for s in json.loads((R/'data/sources.json').read_text()):
 if 'sha256' in s: assert hashlib.sha256((R/'data/raw'/s['file']).read_bytes()).hexdigest()==s['sha256'],s['file']
for p in (R/'data/raw').glob('*pub.dat.gz'):
 if zipfile.is_zipfile(p): assert zipfile.ZipFile(p).testzip() is None
 else:
  with gzip.open(p,'rb') as f:
   while f.read(1024*1024):pass
# Independently parse a full month using pandas' fixed-width reader.
d=pd.read_fwf(R/'data/raw/jan22pub.dat.gz',compression='gzip',colspecs=[(121,123),(179,181),(431,433),(845,855),(859,863)],names=['age','status','cow','weight','occ'])
a=d[(d.age>=16)&d.status.isin([1,2])&(d.weight>0)]
t=pd.read_csv(R/'results/cps_monthly_totals.csv');t=t[(t.year==2022)&(t.month==1)&(t['sample']=='all_employed')].iloc[0]
assert np.isclose(a.weight.sum()/10000,t.employment,rtol=0,atol=.01)
assert len(a)==t['n']
for name in ['oews_matched','cps_wage_salary_matched','cps_all_employed_matched']:
 d=pd.read_csv(R/f'data/processed/{name}.csv');assert d.code.is_unique
 assert np.allclose(d.growth,100*(d.emp2025/d.emp2022-1))
 assert d.observed_exposure.between(0,1).all()
c=pd.read_csv(R/'data/processed/soc_census_crosswalk_expanded.csv');assert c.code.is_unique
m=pd.read_csv(R/'data/processed/cps_monthly_occupation.csv');assert not m.duplicated(['year','month','sample','census']).any()
a=pd.read_csv(R/'data/processed/cps_annual_occupation.csv');assert a[a.basis=='common11'].months.eq(11).all()
print('PASS: source checksums; 47 archive integrity checks; independent January 2022 population/record count; unique merge keys; growth arithmetic; common-month denominators.')
