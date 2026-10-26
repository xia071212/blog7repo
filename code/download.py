"""Download official CPS fixed-width microdata and documentation; cache immutable inputs."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request, re, json, hashlib
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; RAW.mkdir(parents=True,exist_ok=True)
def get(item):
 name,url=item; p=RAW/name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=90) as r: b=r.read()
  p.write_bytes(b)
 print(name,p.stat().st_size,flush=True)
 return {'file':name,'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
if __name__=='__main__':
 jobs=[('task_penetration.csv','https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6/labor_market_impacts/task_penetration.csv'),('onet30_task_statements.xlsx','https://www.onetcenter.org/dl_files/database/db_30_0_excel/Task%20Statements.xlsx')]
 for year in range(2022,2026):
  base=f'https://www2.census.gov/programs-surveys/cps/datasets/{year}/basic/'
  html=urllib.request.urlopen(base,timeout=30).read().decode();(RAW/f'cps{year}_directory.html').write_text(html)
  links=re.findall(r'href="([^"]+\.dat\.gz)"',html)
  for file in links: jobs.append((file,base+file))
 with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(get,jobs))
 for file,url in [('job_exposure.csv','https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6/labor_market_impacts/job_exposure.csv'),('occupation_crosswalk.xlsx','https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-occupation-code-list-and-crosswalk.xlsx')]: results.append(get((file,url)))
 for year in range(2022,2026):
  results.append(get((f'cps{year}_layout.txt',f'https://www2.census.gov/programs-surveys/cps/datasets/{year}/basic/{year}_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt')))
 for y in [22,25]:
  p=RAW/f'oesm{y}nat.zip'
  if not p.exists(): get((p.name,f'https://www.bls.gov/oes/special-requests/oesm{y}nat.zip'))
  results.append({'file':p.name,'url':f'https://www.bls.gov/oes/special-requests/oesm{y}nat.zip','bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'retrieval':'Official BLS download through browser; direct HTTP returned 403'})
 results.append({'file':'anthropic_methods.txt','url':'https://www.anthropic.com/research/labor-market-impacts','retrieval':'Rendered official page saved through browser'})
 results.append({'file':'bls_faq.txt','url':'https://www.bls.gov/oes/oes_ques.htm','retrieval':'Official page, Expand All, saved through browser'})
 (ROOT/'data/sources.json').write_text(json.dumps(results,indent=2))
