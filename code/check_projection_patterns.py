"""Descriptive checks of group differences at similar AI exposure; no causal inference."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
O=R/'results/projection_patterns';O.mkdir(exist_ok=True)
d=pd.read_csv(R/'data/processed/projections_2024_2034_task_sample.csv',dtype={'major':str,'code':str})
a=pd.read_csv(R/'data/processed/projections_major_groups.csv',dtype={'code':str})
focus=['13','15','41','43']
a[a.code.isin(focus)].to_csv(O/'group_summary.csv',index=False)
# Keep published detailed growth rates. Aggregate group growth separately uses levels.
records=[]
for width in [.05,.10]:
 f=d[d.major.isin(focus)].copy(); f['bin']=np.floor((f.observed_exposure+1e-10)/width).astype(int)
 for (group,b),g in f.groupby(['major','bin']):
  records.append(dict(width=width,major=group,bin=b,low=b*width,high=(b+1)*width,n=len(g),emp2024=g.emp2024.sum(),exposure=np.average(g.observed_exposure,weights=g.emp2024),growth=np.average(g.growth,weights=g.emp2024)))
bins=pd.DataFrame(records);bins.to_csv(O/'exposure_bins.csv',index=False)
# Compare target and sales using identical exposure-bin weights (pooled employment).
comparisons=[]
for width in [.05,.10]:
 b=bins[bins.width==width]
 for group in ['13','15','43']:
  pair=b[b.major==group].merge(b[b.major=='41'],on='bin',suffixes=('_target','_sales'))
  w=pair.emp2024_target+pair.emp2024_sales
  comparisons.append(dict(width=width,target=group,shared_bins=len(pair),target_n=int(pair.n_target.sum()),sales_n=int(pair.n_sales.sum()),target_employment_coverage=pair.emp2024_target.sum()/d.loc[d.major==group,'emp2024'].sum(),sales_employment_coverage=pair.emp2024_sales.sum()/d.loc[d.major=='41','emp2024'].sum(),target_growth=np.average(pair.growth_target,weights=w),sales_growth=np.average(pair.growth_sales,weights=w),gap_pp=np.average(pair.growth_target-pair.growth_sales,weights=w)))
pd.DataFrame(comparisons).to_csv(O/'common_bin_comparisons.csv',index=False)
# Fit descriptive least-squares projections; no significance claims or causal interpretation.
regs=[]
for subset in ['all','focus']:
 f=d if subset=='all' else d[d.major.isin(focus)]
 for weighted in [False,True]:
  for fe in [False,True]:
   x=np.column_stack([np.ones(len(f)),f.observed_exposure*10]) # coefficient per 10 pp exposure
   if fe:x=np.column_stack([x,pd.get_dummies(f.major,drop_first=True).to_numpy(dtype=float)])
   w=f.emp2024.to_numpy() if weighted else np.ones(len(f)); y=f.growth.to_numpy(); sw=np.sqrt(w/w.mean())
   coef=np.linalg.lstsq(x*sw[:,None],y*sw,rcond=None)[0]
   regs.append(dict(sample=subset,n=len(f),employment_weighted=weighted,major_group_controls=fe,exposure_coefficient_per_10pp=coef[1]))
pd.DataFrame(regs).to_csv(O/'descriptive_slopes.csv',index=False)
# Show variation within each group, including counterexamples.
f=d[d.major.isin(focus)].copy();f.sort_values(['major','growth']).to_csv(O/'detailed_occupations.csv',index=False)
summary=[]
for k,g in f.groupby('major'):
 summary.append(dict(major=k,n=len(g),growing_n=int((g.growth>0).sum()),declining_n=int((g.growth<0).sum()),declining_employment_share=g.loc[g.growth<0,'emp2024'].sum()/g.emp2024.sum()))
pd.DataFrame(summary).to_csv(O/'within_group_variation.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(12,4.8),gridspec_kw={'width_ratios':[1,1.2]})
colors={'13':'#3975bb','15':'#ae8131','41':'#d6696d','43':'#7b9d42'}
labels={'13':'Business & financial','15':'Computer & mathematical','41':'Sales','43':'Office & administrative'}
for k in focus:
 g=f[f.major==k];r=a[a.code==k].iloc[0]
 axs[0].scatter(r.observed_exposure*100,r.growth,s=r.emp2024/25000,color=colors[k],alpha=.7)
 axs[0].annotate(labels[k],(r.observed_exposure*100,r.growth),xytext=(0,17 if k in ['15','41'] else -23),textcoords='offset points',ha='center',fontsize=9)
 axs[1].scatter(g.observed_exposure*100,g.growth,s=g.emp2024/22000,color=colors[k],alpha=.6,label=labels[k],edgecolors='white',linewidth=.4)
for ax in axs:
 ax.axhline(0,color='#888',lw=.7);ax.set_xlabel('AI exposure (%)');ax.set_ylabel('Projected employment growth, 2024–2034 (%)');ax.spines[['top','right']].set_visible(False)
axs[0].set_xlim(21,43);axs[0].set_ylim(-9,15);axs[0].set_title('Employment-weighted group averages')
axs[1].set_title('Detailed occupations reveal exceptions');axs[1].legend(fontsize=8,loc='upper right')
fig.text(.02,.01,'BLS 2024–2034 projections + Anthropic; matched sample only. Bubble area = 2024 employment; size scales differ by panel.',fontsize=9)
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(O/'group_and_occupation_comparison.png',dpi=180);plt.close(fig)
print(pd.DataFrame(comparisons).round(3).to_string(index=False));print(pd.DataFrame(regs).round(3).to_string(index=False));print(pd.DataFrame(summary).round(3).to_string(index=False))

# Sensitivity to the largest occupation and narrower definitions.
sensitivity=[]
for k,g in f.groupby('major'):
 largest=g.loc[g.emp2024.idxmax()]; h=g[g.code!=largest.code]
 sensitivity.append(dict(group=k,excluded=largest.title,n=len(h),exposure=np.average(h.observed_exposure,weights=h.emp2024),growth=(h.emp2034.sum()/h.emp2024.sum()-1)*100))
pd.DataFrame(sensitivity).to_csv(O/'exclude_largest_occupation.csv',index=False)
print(pd.DataFrame(sensitivity).round(3).to_string(index=False))
narrow=[]
for name,prefix in [('Financial operations','13-2'),('Computer occupations','15-12')]:
 g=d[d.code.str.startswith(prefix)]
 narrow.append(dict(group=name,n=len(g),exposure=np.average(g.observed_exposure,weights=g.emp2024),growth=(g.emp2034.sum()/g.emp2024.sum()-1)*100))
pd.DataFrame(narrow).to_csv(O/'narrow_groups.csv',index=False)
