"""Reproduce the Blog 7 chart from saved public inputs."""
# 1. Setup: project-relative paths and deterministic inputs.
from pathlib import Path
import runpy
import pandas as pd
import numpy as np
R=Path(__file__).resolve().parents[1]
O=R/'results/tasks'
O.mkdir(parents=True,exist_ok=True)
(R/'data/processed').mkdir(parents=True,exist_ok=True)

# 2. Read, normalize, and match task descriptions; retain missing matches.
def norm(s):return s.str.lower().str.replace(r'\s+',' ',regex=True).str.strip()
t=pd.read_csv(R/'data/raw/task_penetration.csv');t['key']=norm(t.task)
conf=t.groupby('key').penetration.nunique();assert conf.max()==1
raw_n=len(t);t=t.drop_duplicates('key')
m=pd.read_excel(R/'data/raw/onet30_task_statements.xlsx');m['code']=m['O*NET-SOC Code'].str[:7];m['key']=norm(m.Task)
# Collapse specializations to SOC, count each distinct task text only once per SOC.
m=m.drop_duplicates(['code','key']);m=m.merge(t[['key','penetration']],on='key',how='left',validate='many_to_one')
m.to_csv(O/'task_matches.csv',index=False)
rows=[]
for code,a in m.groupby('code'):
 x=a.penetration.dropna().to_numpy();n=len(x);s=x.sum();h=((x*x).sum()/s**2-1/n)/(1-1/n) if s>0 and n>1 else np.nan
 rows.append(dict(code=code,n_tasks=len(a),n_matched=n,coverage=n/len(a),breadth=(x>0).mean() if n else np.nan,high50=(x>=.5).mean() if n else np.nan,high80=(x>=.8).mean() if n else np.nan,mean_penetration=x.mean() if n else np.nan,concentration=h))
f=pd.DataFrame(rows);f.to_csv(O/'soc_task_metrics.csv',index=False)

# 3. Match BLS projections and exposure, save chart data.
runpy.run_path(str(R/'code/build_interactive_sample.py'),run_name='__main__')

# 4. Produce the English, offline interactive visualization.
runpy.run_path(str(R/'code/build_blog_assets.py'),run_name='__main__')
