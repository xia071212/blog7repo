"""Separate descriptive OLS/WLS regressions for exposure and task breadth.
HC3 intervals summarize model-based cross-occupation uncertainty, not BLS forecast uncertainty.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t
R=Path(__file__).resolve().parents[1]
d=pd.read_csv(R/'data/processed/projections_2024_2034_task_sample.csv')
results=[]
for metric in ['observed_exposure','breadth']:
 for weighted in [False,True]:
  for fe in [False,True]:
   X=np.column_stack([np.ones(len(d)),d[metric].to_numpy()*10])
   if fe:X=np.column_stack([X,pd.get_dummies(d.major,drop_first=True).to_numpy(float)])
   w=d.emp2024.to_numpy() if weighted else np.ones(len(d));w=w/w.mean()
   A=X*np.sqrt(w)[:,None];y=d.growth.to_numpy()*np.sqrt(w)
   b=np.linalg.lstsq(A,y,rcond=None)[0];inv=np.linalg.inv(A.T@A)
   e=y-A@b;h=np.einsum('ij,jk,ik->i',A,inv,A)
   meat=A.T@(((e/(1-h))**2)[:,None]*A);cov=inv@meat@inv
   se=np.sqrt(cov[1,1]);df=len(d)-X.shape[1];crit=t.ppf(.975,df)
   results.append(dict(metric=metric,employment_weighted=weighted,group_controls=fe,n=len(d),coefficient_per_10pp=b[1],hc3_se=se,ci_low=b[1]-crit*se,ci_high=b[1]+crit*se,p_value=2*t.sf(abs(b[1]/se),df)))
a=pd.DataFrame(results);out=R/'results/projection_patterns';out.mkdir(exist_ok=True)
a.to_csv(out/'regressions.csv',index=False)
lines=['| Indicator | Employment-weighted | + Group controls | Equal occupation weights |','|---|---:|---:|---:|']
for metric,label in [('observed_exposure','AI exposure'),('breadth','Task breadth')]:
 vals=[]
 for weighted,fe in [(True,False),(True,True),(False,False)]:
  r=a[(a.metric==metric)&(a.employment_weighted==weighted)&(a.group_controls==fe)].iloc[0]
  vals.append(f'{r.coefficient_per_10pp:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}]')
 lines.append('| '+label+' | '+' | '.join(vals)+' |')
(out/'regression_table.md').write_text('\n'.join(lines)+'\n')
print(a.round(4).to_string(index=False))
