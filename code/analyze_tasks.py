"""Exploratory task structure, with explicit coverage and no missing-to-zero imputation.
Task weights are equal, NOT Anthropic's unavailable task-time weights.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
R=Path(__file__).resolve().parents[1];O=R/'results/tasks';O.mkdir(exist_ok=True)
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
e=pd.read_csv(R/'data/processed/oews_matched.csv',dtype={'code':str}).merge(f,on='code',validate='one_to_one')
e.to_csv(O/'oews_task_sample.csv',index=False)
# Weighted covariance of occupation-level observations (not survey standard errors).
def corr(x,y,w):
 x=np.array(x,float);y=np.array(y,float);w=np.array(w,float);x-=np.average(x,weights=w);y-=np.average(y,weights=w)
 den=np.sqrt(np.sum(w*x*x)*np.sum(w*y*y));return np.sum(w*x*y)/den if den else np.nan
def residual(y,X,w):
 X=np.asarray(X,float);y=np.asarray(y,float);w=np.sqrt(w)
 return y-X@np.linalg.lstsq(X*w[:,None],y*w,rcond=None)[0]
results=[];flows=[]
def inspect(d,survey,cut):
 flows.append(dict(survey=survey,task_coverage_cutoff=cut,n=len(d),employment_2022=d.emp2022.sum()))
 for variant,a in [('full',d),('trim1_99',d[d.growth.between(d.growth.quantile(.01),d.growth.quantile(.99))])]:
  for metric in ['breadth','high50','high80','mean_penetration','concentration']:
   if metric not in a:continue
   b=a.dropna(subset=[metric]).copy()
   if len(b)<30:continue
   for weighting,w in [('equal',np.ones(len(b))),('employment2022',b.emp2022.to_numpy())]:
    X=np.column_stack([np.ones(len(b)),b.observed_exposure]);
    # Concentration's incremental association also conditions on breadth.
    if metric=='concentration':X=np.column_stack([X,b.breadth])
    Z=np.column_stack([X,pd.get_dummies(b.major.astype(str),drop_first=True).to_numpy(float)])
    results.append(dict(survey=survey,coverage_cutoff=cut,variant=variant,metric=metric,weighting=weighting,n=len(b),correlation=corr(b[metric],b.growth,w),corr_with_exposure=corr(b[metric],b.observed_exposure,w),partial_exposure=corr(residual(b[metric],X,w),residual(b.growth,X,w),w),partial_exposure_and_major=corr(residual(b[metric],Z,w),residual(b.growth,Z,w),w)))
for cut in [.8,.95,1.0]:
 inspect(e[e.coverage>=cut],'OEWS',cut)
 # Aggregate task breadth to Census occupations using fixed 2022 OEWS weights.
 cw=pd.read_csv(R/'data/processed/soc_census_crosswalk_expanded.csv',dtype={'census':str,'code':str})
 base=pd.read_csv(R/'data/processed/oews_2022.csv',dtype={'code':str})
 z=cw.merge(base[['code','emp2022']],on='code').merge(f,on='code',how='left');z['valid']=(z.coverage>=cut)
 z['covered_emp']=z.emp2022.where(z.valid,0)
 metrics=['breadth','high50','high80','mean_penetration']
 for col in metrics:z[col+'_num']=z[col].fillna(0)*z.covered_emp
 agg=z.groupby('census')[['emp2022','covered_emp']+[x+'_num' for x in metrics]].sum();agg['task_job_coverage']=agg.covered_emp/agg.emp2022
 for col in metrics:agg[col]=agg[col+'_num']/agg.covered_emp
 for sample in ['all_employed','wage_salary']:
  c=pd.read_csv(R/f'data/processed/cps_{sample}_matched.csv',dtype={'census':str,'code':str});c=c[c.reliable_cell]
  c=c.merge(agg[['task_job_coverage']+metrics],on='census');c=c[c.task_job_coverage>=.9]
  if cut==.95:c.to_csv(O/f'cps_{sample}_task_sample.csv',index=False)
  inspect(c,'CPS_'+sample,cut)
pd.DataFrame(results).to_csv(O/'associations.csv',index=False);pd.DataFrame(flows).to_csv(O/'sample_flow.csv',index=False)
q=e[e.coverage>=.95].copy()
fig=px.scatter(q,x='breadth',y='growth',color='observed_exposure',hover_name='title',hover_data=['n_tasks','n_matched','coverage','emp2022','mean_penetration'],template='plotly_white',labels={'breadth':'Share of matched tasks with penetration > 0','growth':'OEWS employment estimate change, 2022–2025 (%)'},title='Task coverage breadth and employment change | ≥95% task matching')
fig.add_hline(y=0);fig.write_html(O/'task_breadth.html',include_plotlyjs=True)
q[q.code.isin(['15-1251','43-9021','13-2051','13-1161'])].to_csv(O/'examples.csv',index=False)
print('Raw task rows',raw_n,'unique normalized',len(t),'SOC-task mapping rows',len(m),'matched',m.penetration.notna().sum(),'mapping SOCs',len(f))
print(pd.DataFrame(flows).to_string(index=False))
a=pd.DataFrame(results);print(a[(a.coverage_cutoff==.95)&(a.variant=='full')].to_string(index=False))
