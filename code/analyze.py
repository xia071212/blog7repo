"""Blog 7: descriptive AI exposure versus occupational employment estimates.
Run with Python 3.12; paths are relative to this script, never the shell cwd.
"""
from pathlib import Path
import gzip, re, zipfile, json, io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; DATA=ROOT/'data/processed'; OUT=ROOT/'results'
for p in [DATA,OUT]: p.mkdir(parents=True,exist_ok=True)
def save(df,name,folder=OUT): df.to_csv(folder/name,index=False)
def wcorr(x,y,w):
 x=np.asarray(x,float);y=np.asarray(y,float);w=np.asarray(w,float)
 x=x-np.average(x,weights=w);y=y-np.average(y,weights=w)
 return np.sum(w*x*y)/np.sqrt(np.sum(w*x*x)*np.sum(w*y*y))
stats=[]
def summary(d,label,weight='emp2022'):
 for variant,t in [('all',d),('baseline >= 10000',d[d[weight]>=10000]),('trim growth 1-99 pct',d[d.growth.between(d.growth.quantile(.01),d.growth.quantile(.99))])]:
  if len(t)<3:continue
  x=t.observed_exposure;y=t.growth
  stats.append(dict(sample=label,variant=variant,n=len(t),pearson=x.corr(y),spearman=x.corr(y,method='spearman'),baseline_weighted_pearson=wcorr(x,y,t[weight])))
 if label.endswith(('_all_cells','_one_soc','_fullcoverage','_same_census')): return
 # Leave-one-occupation-out changes reveal influential observations without deleting them.
 full=d.observed_exposure.corr(d.growth)
 influence=[]
 for idx,r in d.iterrows():
  t=d.drop(idx); rr=t.observed_exposure.corr(t.growth)
  influence.append(dict(code=r['code'],title=r['title'],growth=r.growth,baseline=r[weight],correlation_without=rr,change=rr-full))
 save(pd.DataFrame(influence).sort_values('change',key=abs,ascending=False),label+'_influence.csv')
 save(d.sort_values('growth').head(15),label+'_largest_declines.csv')
 save(d.sort_values('growth',ascending=False).head(15),label+'_largest_increases.csv')

def scatter(d,label):
 fig=px.scatter(d,x='observed_exposure',y='growth',color='major',size='emp2022',size_max=35,
  hover_name='title',hover_data={'code':True,'emp2022':':,.0f','emp2025':':,.0f','observed_exposure':':.3f','growth':':.1f','major':False},
  labels={'observed_exposure':'Observed AI exposure (0–1; later snapshot)','growth':'Employment estimate change, 2022–2025 (%)','major':'SOC major group'},
  title=label+' | AI exposure and employment change',template='plotly_white')
 fig.add_hline(y=0,line_color='#777');fig.update_layout(height=670,legend_title='Click groups to filter',margin=dict(t=80,b=70))
 fig.write_html(OUT/(label+'_interactive.html'),include_plotlyjs=True)
 plt.figure(figsize=(10,6));plt.scatter(d.observed_exposure,d.growth,s=12+80*np.sqrt(d.emp2022/d.emp2022.max()),alpha=.5,c='#247c91',edgecolors='none');plt.axhline(0,color='gray',lw=.7)
 plt.xlabel('Observed AI exposure (0–1; later snapshot)');plt.ylabel('Employment estimate change, 2022–2025 (%)');plt.title(label+' | descriptive occupational association');plt.figtext(.02,.01,'Sources: Anthropic Economic Index; BLS OEWS / Census CPS. Association does not identify an AI effect.',fontsize=8);plt.tight_layout(rect=(0,.03,1,1));plt.savefig(OUT/(label+'_scatter.png'),dpi=180);plt.close()

# 1. Load exposure and the national, all-ownership detailed OEWS estimates.
ai=pd.read_csv(RAW/'job_exposure.csv').rename(columns={'occ_code':'code'})
assert ai.code.is_unique and ai.observed_exposure.between(0,1).all()
bls={}; flow=[]
for year in [2022,2025]:
 z=zipfile.ZipFile(RAW/f'oesm{str(year)[2:]}nat.zip');d=pd.read_excel(z.open(next(n for n in z.namelist() if n.endswith('.xlsx'))))
 d=d[(d.AREA==99)&(d.OWN_CODE==1235)&(d.NAICS==0)&(d.O_GROUP=='detailed')].copy()
 d=d.rename(columns={'OCC_CODE':'code','OCC_TITLE':'title','TOT_EMP':f'emp{year}'})
 d[f'emp{year}']=pd.to_numeric(d[f'emp{year}'],errors='coerce')
 assert d.code.is_unique
 bls[year]=d[['code','title',f'emp{year}','EMP_PRSE']]
 save(bls[year],f'oews_{year}.csv',DATA)
 flow.append(dict(stage=f'OEWS {year} detailed occupations',n=len(d),employment=d[f'emp{year}'].sum()))
pair=bls[2022].merge(bls[2025][['code','emp2025']],on='code',how='outer',indicator=True,validate='one_to_one')
save(pair[pair._merge!='both'],'oews_year_unmatched.csv')
pair=pair.drop(columns='_merge');d=pair.merge(ai[['code','observed_exposure']],on='code',how='left',validate='one_to_one')
save(d[d.observed_exposure.isna()],'oews_missing_exposure.csv')
save(d[d[['emp2022','emp2025']].isna().any(axis=1)],'oews_missing_employment.csv')
save(ai[~ai.code.isin(pair.code)],'exposure_missing_oews.csv')
d=d.dropna(subset=['emp2022','emp2025','observed_exposure']);d=d[(d.emp2022>0)&(d.emp2025>0)].copy()
d['growth']=100*(d.emp2025/d.emp2022-1);d['log_change']=100*np.log(d.emp2025/d.emp2022);d['absolute_change']=d.emp2025-d.emp2022;d['major']=d.code.str[:2]
flow.append(dict(stage='OEWS both years with exposure and positive employment',n=len(d),employment=d.emp2022.sum()))
save(d,'oews_matched.csv',DATA);summary(d,'OEWS');scatter(d,'OEWS')
# Major-group descriptive aggregates; growth of employment totals, not mean individual growth.
g=d.assign(exposure_numerator=d.emp2022*d.observed_exposure).groupby('major').agg(emp2022=('emp2022','sum'),emp2025=('emp2025','sum'),exposure_numerator=('exposure_numerator','sum'),n=('code','size')).reset_index()
g['observed_exposure']=g.exposure_numerator/g.emp2022;g['growth']=100*(g.emp2025/g.emp2022-1);save(g,'oews_major_groups.csv')

# 2. Census 2018 to SOC 2018 crosswalk. Resolve explicit codes before residual X groups.
cw=pd.read_excel(RAW/'occupation_crosswalk.xlsx',sheet_name='2018 Census Occ Code List',header=4,dtype=str);cw.columns=cw.columns.str.strip()
cw=cw[cw['2018 Census Code'].str.fullmatch(r'\d{4}',na=False)].copy();cw=cw.rename(columns={'2018 Census Code':'census','2018 Census Title':'census_title','2018 SOC Code':'soc_pattern'})
cw=cw[~cw.census.str.startswith(('98','99'))]
universe=bls[2022].copy();maps=[];amb=[]
for soc in universe.code:
 candidates=[]
 for _,r in cw.iterrows():
  pattern=str(r.soc_pattern).strip()
  if pattern==soc: score=100
  elif 'X' in pattern and re.fullmatch(pattern.replace('X','[0-9]'),soc):score=7-pattern.count('X')
  elif pattern.endswith('0') and soc.startswith(pattern.rstrip('0')):score=len(pattern.rstrip('0'))
  else:continue
  candidates.append((score,r.census,r.census_title,pattern))
 if candidates:
  top=max(x[0] for x in candidates);best=[x for x in candidates if x[0]==top]
  if len(best)==1:
   _,c,title,patt=best[0];maps.append(dict(code=soc,census=c,census_title=title,soc_pattern=patt,exact=(top==100)))
  else:amb.append(dict(code=soc,candidates=str(best)))
mapdf=pd.DataFrame(maps);assert mapdf.code.is_unique
save(mapdf,'soc_census_crosswalk_expanded.csv',DATA);save(pd.DataFrame(amb,columns=['code','candidates']),'crosswalk_ambiguous.csv')
m=mapdf.merge(bls[2022][['code','emp2022']],on='code',validate='one_to_one').merge(ai[['code','observed_exposure']],on='code',how='left',validate='one_to_one')
m['covered_emp']=m.emp2022.where(m.observed_exposure.notna(),0);m['num']=m.covered_emp*m.observed_exposure.fillna(0)
ce=m.groupby('census').agg(census_title=('census_title','first'),oews_emp=('emp2022','sum'),covered_emp=('covered_emp','sum'),num=('num','sum'),n_soc=('code','size'),n_exposed=('observed_exposure','count')).reset_index()
ce['coverage']=ce.covered_emp/ce.oews_emp;ce['observed_exposure']=ce.num/ce.covered_emp
save(ce,'census_exposure.csv',DATA)

# 3. Read fixed-width CPS basic monthly public-use files. Four implied weight decimals.
# Positions independently checked in all four annual official dictionaries.
monthly=[];totals=[]
for path in sorted(RAW.glob('*pub.dat.gz')):
 year=2000+int(path.name[3:5]);rows=[]
 if zipfile.is_zipfile(path):
  archive=zipfile.ZipFile(path); stream=io.TextIOWrapper(archive.open(next(n for n in archive.namelist() if n.lower().endswith(('.dat','.txt')))),encoding='ascii',errors='replace')
 else: stream=gzip.open(path,'rt',encoding='ascii',errors='replace')
 with stream as f:
  for line in f:
   age=int(line[121:123]);status=int(line[179:181]);weight=int(line[845:855])/10000
   if age>=16 and status in (1,2) and weight>0:
    rows.append((line[859:863].strip().zfill(4),int(line[431:433]),weight))
 t=pd.DataFrame(rows,columns=['census','cow','weight']);month=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'].index(path.name[:3])+1
 for sample,v in [('all_employed',t),('wage_salary',t[t.cow.between(1,5)])]:
  a=v.groupby('census').agg(employment=('weight','sum'),n=('weight','size')).reset_index();a['year']=year;a['month']=month;a['sample']=sample;monthly.append(a)
  totals.append(dict(year=year,month=month,sample=sample,employment=v.weight.sum(),n=len(v)))
 print('Processed',path.name,flush=True)
monthly=pd.concat(monthly,ignore_index=True);save(monthly,'cps_monthly_occupation.csv',DATA);save(pd.DataFrame(totals),'cps_monthly_totals.csv')
monthsets=[set(monthly.loc[monthly.year==y,'month']) for y in range(2022,2026)];common=sorted(set.intersection(*monthsets));assert len(common)==11 and 10 not in common
annual=[]
for basis,months in [('common11',common),('all_available',list(range(1,13)))]:
 for (year,sample),t in monthly[monthly.month.isin(months)].groupby(['year','sample']):
  # Missing occupation-month cells contribute zero, not a reduced denominator.
  count=t.month.nunique();a=t.groupby('census').agg(employment=('employment','sum'),n=('n','sum')).reset_index();a.employment/=count;a['year']=year;a['sample']=sample;a['basis']=basis;a['months']=count;annual.append(a)
annual=pd.concat(annual,ignore_index=True);save(annual,'cps_annual_occupation.csv',DATA)
cps_datasets={};coverage=[]
for sample in ['all_employed','wage_salary']:
 t=annual[(annual.basis=='common11')&(annual['sample']==sample)]
 p=t.pivot(index='census',columns='year',values='employment').add_prefix('emp').reset_index();n=t.pivot(index='census',columns='year',values='n').add_prefix('n').reset_index();p=p.merge(n,on='census')
 p=p.merge(ce,on='census',how='left',validate='one_to_one');save(p,f'cps_{sample}_all_matches.csv',DATA)
 for y in [2022,2025]:
  valid=(p.coverage>=.9)&p.observed_exposure.notna();coverage.append(dict(sample=sample,year=y,n_total=p[f'emp{y}'].notna().sum(),n_matched=(valid&p[f'emp{y}'].notna()).sum(),total_employment=p[f'emp{y}'].sum(),matched_employment=p.loc[valid,f'emp{y}'].sum()))
 p=p[(p.coverage>=.9)&p.observed_exposure.notna()&(p.emp2022>0)&(p.emp2025>0)].copy();p['growth']=100*(p.emp2025/p.emp2022-1);p['code']=p.census;p['title']=p.census_title
 # Very small CPS cells are retained in data, flagged and excluded from the main comparison.
 p['reliable_cell']=(p.n2022>=100)&(p.n2025>=100);p['major']=p.census.map(mapdf.groupby('census').code.first().str[:2]);save(p,f'cps_{sample}_matched.csv',DATA)
 summary(p,'CPS_'+sample+'_all_cells');main=p[p.reliable_cell].copy();summary(main,'CPS_'+sample);scatter(main,'CPS_'+sample);cps_datasets[sample]=main
 summary(main[main.n_soc==1],'CPS_'+sample+'_one_soc')
 summary(main[main.coverage>=.999999],'CPS_'+sample+'_fullcoverage')
# 4. Compare both surveys at the same Census-occupation aggregation, same matched SOC set.
both=mapdf.merge(d[['code','emp2022','emp2025']],on='code').groupby('census')[['emp2022','emp2025']].sum();both['oews_growth']=100*(both.emp2025/both.emp2022-1)
p=cps_datasets['wage_salary'].merge(both[['oews_growth']],on='census');save(p,'survey_comparison.csv')
fig=px.scatter(p,x='oews_growth',y='growth',hover_name='title',color='observed_exposure',labels={'oews_growth':'OEWS change (%)','growth':'CPS wage/salary change (%)'},title='Same Census occupations, different surveys',template='plotly_white');fig.add_hline(y=0);fig.add_vline(x=0);fig.write_html(OUT/'survey_comparison.html',include_plotlyjs=True)
# Fixed cohort and fixed exposure groups across 2022-2025, common 11 months each year.
cohort=cps_datasets['wage_salary'][['census','observed_exposure']].copy()
cohort['exposure_group']=pd.cut(cohort.observed_exposure,[-.000001,0,.1,.3,1],labels=['Zero','>0 to 0.10','>0.10 to 0.30','>0.30'])
trend=annual[(annual.basis=='common11')&(annual['sample']=='wage_salary')].merge(cohort,on='census')
trend=trend.groupby(['year','exposure_group'],observed=True).employment.sum().reset_index()
base=trend[trend.year==2022].set_index('exposure_group').employment
trend['index_2022_100']=trend.employment/trend.exposure_group.map(base).astype(float)*100
save(trend,'cps_exposure_group_trend.csv')
fig=px.line(trend,x='year',y='index_2022_100',color='exposure_group',markers=True,template='plotly_white',title='CPS wage/salary employment | fixed occupation cohort',labels={'index_2022_100':'Employment index (2022 = 100)','exposure_group':'Later observed exposure'})
fig.update_xaxes(dtick=1);fig.write_html(OUT/'cps_exposure_group_trend.html',include_plotlyjs=True)
q=p.copy();q['growth']=q.oews_growth;summary(q,'OEWS_same_census')
save(pd.DataFrame(stats),'correlations.csv');save(pd.DataFrame(flow),'oews_sample_flow.csv');save(pd.DataFrame(coverage),'cps_match_coverage.csv')
metrics={'exposure_occupations':len(ai),'oews_matched':len(d),'oews_count_match_rate_2022':len(d)/len(bls[2022]),'oews_employment_coverage_2022':d.emp2022.sum()/bls[2022].emp2022.sum(),'common_months':common,'cps_files':len(list(RAW.glob('*pub.dat.gz'))),'survey_growth_correlation':p.oews_growth.corr(p.growth),'survey_same_sign_share':float(((p.oews_growth>0)==(p.growth>0)).mean()),'survey_comparison_n':len(p)}
(OUT/'summary.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2));print(pd.DataFrame(stats).to_string(index=False))
# Distinguish final plotting-sample coverage from exposure-match coverage.
plot_coverage=[]
for sample,dd in cps_datasets.items():
 for year in [2022,2025]:
  total=next(r['total_employment'] for r in coverage if r['sample']==sample and r['year']==year)
  plot_coverage.append(dict(sample=sample,year=year,n_plot_occupations=len(dd),plotted_employment=dd[f'emp{year}'].sum(),population_total=total,plotted_employment_coverage=dd[f'emp{year}'].sum()/total))
save(pd.DataFrame(plot_coverage),'cps_plot_coverage.csv')
