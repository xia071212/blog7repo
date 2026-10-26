"""Create the English embedded chart and a focused replication download for Blog 7."""
from pathlib import Path
import re, zipfile
R=Path(__file__).resolve().parents[1]
DEST=R.parent/'myrepo1/blog/posts/post7'
DEST.mkdir(parents=True,exist_ok=True)
s=(R/'results/interactive_sample.html').read_text()
# Remove the prototype's duplicate article heading and footer, preserving chart and task panel.
s=re.sub(r'<main><div class="eyebrow">.*?<section class="card">','<main><section class="card">',s,count=1,flags=re.S)
s=re.sub(r'<p class="footer">.*?</p></main>','</main>',s,count=1,flags=re.S)
translations={
'AI 暴露度：Anthropic 按任务时间及使用方式等因素构造的职业指标，不是裁员概率。':'AI exposure: Anthropic’s task-based occupational measure; not a layoff probability.',
'任务覆盖广度：有正渗透值的任务数 ÷ 已匹配任务数；各项任务等权计数。':'Task breadth: tasks with positive penetration / matched tasks; each task counts equally.',
' 大类横轴按 2024 年就业人数加权。':' Group averages use 2024 employment weights.',
'详细职业圆点等大小；黑色描边为选中职业。选择职业后只显示该点，清空搜索恢复该大类。悬停查看就业人数。':'Detailed dots are equal-sized; black outline marks the selection. Search isolates one occupation; clear it to restore the group. Hover for employment.',
'气泡面积正比于纳入样本的 2024 年就业人数；大类预测增长由样本就业人数总和计算。横纵轴与气泡大小使用同一批职业，不能等同于完整大类；悬停可查看就业覆盖率。':'Bubble area represents sample employment in 2024. Group growth uses summed employment. All measures use the matched sample, not necessarily the full group; hover for coverage.',
'悬停识别大类并查看数据；点击气泡进入详细职业。点击“职业大类”返回全景。':'Hover to identify groups; click a bubble to explore its occupations. Choose “Groups” to return.',
'搜索英文职业名或 SOC 编码，选择后查看任务':'Search occupation or SOC; select to isolate one dot',
'条形表示 Anthropic 的任务渗透指标，不是任务时间占比或裁员概率。任务按渗透值降序排列；任务名称保留官方英文。':'Bars show Anthropic task penetration, not time shares or layoff probabilities. Tasks are sorted by penetration.',
'任务数量比例 ≠ 工作时间比例。O*NET 子职业任务合并后去重，并不代表每位劳动者都执行全部任务。零值表示此指标未观测到覆盖；未匹配表示数据缺失，两者分开列示。':'Task counts are not time shares. Tasks are deduplicated across O*NET suboccupations; not every worker performs every task. Zero denotes no observed penetration; unmatched denotes missing data.',
'点击主图中的另一个点即可切换':'Click another dot to inspect its tasks',
'哪些任务出现了正渗透值？':'Which tasks show AI penetration?',
'。切换横轴可比较两个指标。':'. Switch the horizontal axis to compare measures.',
'点击查看该类内部职业':'Click to explore occupations in this group',
'职业大类颜色图例':'Group color legend',
'全部职业大类':'All occupational groups',
'职业大类':'Groups','详细职业':'Occupations','查看层级':'View level','搜索职业':'Search occupations',
'任务覆盖广度':'Task breadth','AI 暴露度':'AI exposure','预测就业增长':'Projected employment growth',
'2024–2034 预测就业增长 (%)':'Projected employment growth, 2024–2034 (%)',
'2024 样本就业人数':'2024 sample employment','2034 样本预测就业人数':'2034 projected sample employment',
'样本预测就业增长':'Sample projected growth','加权 AI 暴露度':'Weighted AI exposure','加权任务覆盖广度':'Weighted task breadth',
'占大类基期就业人数':'Share of official group employment','官方大类基期就业人数':'Official group employment, 2024',
'2024 基期就业人数':'2024 employment','2034 预测就业人数':'2034 projected employment',
'正渗透任务 / 匹配任务':'Positive / matched tasks','正渗透 / 匹配任务':'Positive / matched tasks',
'纳入详细职业':'Included occupations','就业加权 ':'Employment-weighted ',
'2024 就业人数（面积比例）':'2024 employment (bubble area)',
'当前选中：':'Selected: ','任务匹配：':'Task matches: ','2024 就业 ':'2024 employment: ','2034 预测就业 ':'2034 projected employment: ',
'展开全部 ':'Show all ',' 项任务':' tasks','收起任务':'Show fewer tasks','未匹配':'Unmatched',
' 个职业大类':' groups',' 个详细职业':' occupations',' 个':'',' 人':' people','；':'; ','。':'. ',
'管理':'Management','商业与金融':'Business & finance','计算机与数学':'Computer & math','建筑与工程':'Architecture & engineering','生命、自然与社会科学':'Sciences','社区与社会服务':'Community services','法律':'Legal','教育与图书馆':'Education','艺术与媒体':'Arts & media','医疗专业':'Healthcare professionals','医疗支持':'Healthcare support','保护服务':'Protective services','餐饮':'Food service','清洁与园林':'Cleaning & grounds','个人服务':'Personal services','销售':'Sales','办公室与行政':'Office & admin','农林渔业':'Farming','建筑施工':'Construction','安装与维修':'Installation & repair','生产':'Production','运输与搬运':'Transportation'
}
# Longest matches first so complete sentences override component labels.
pattern=re.compile('|'.join(re.escape(k) for k in sorted(translations,key=len,reverse=True)))
s=pattern.sub(lambda m:translations[m.group()],s).replace('lang="zh-CN"','lang="en"')
s=s.replace('main{max-width:1160px;margin:auto;padding:38px 24px}','main{max-width:1160px;margin:auto;padding:0 4px}').replace('main{padding:22px 12px}','main{padding:0 4px}')
(DEST/'interactive.html').write_text(s)
files=['code/build_interactive_sample.py','code/check_projection_patterns.py','code/regress_projections.py','requirements.txt','data/raw/job_exposure.csv','data/raw/bls_projections_2024_2034.zip','results/tasks/soc_task_metrics.csv','results/tasks/task_matches.csv']
files += [str(p.relative_to(R)) for p in (R/'data/processed').glob('projections*.csv')]
files += [str(p.relative_to(R)) for p in (R/'results/projection_patterns').glob('*')]
readme='''# Blog 7: AI exposure and employment outlook

This focused package reproduces the 722-occupation chart and descriptive comparisons.
Install requirements.txt, then run code/build_interactive_sample.py and code/check_projection_patterns.py and code/regress_projections.py in that order. Paths resolve relative to the scripts. The first produces results/interactive_sample.html, a self-contained Plotly chart, and the processed projection samples. The second writes results/projection_patterns/.

Sources: BLS official 2024–2034 archive https://www.bls.gov/emp/projections-archive/2024-34.zip (occupation.xlsx, Table 1.2); Anthropic job_exposure.csv and task_penetration.csv from https://www.anthropic.com/research/labor-market-impacts; O*NET 30.0 task descriptions https://www.onetcenter.org/database.html. The task tables are retained inputs from the task-matching stage; see the main README included below for that stage's methods. Employment is converted from thousands to people. Use detailed Line item rows, match SOC, and retain task coverage >=95%.

Group exposure/breadth use 2024 employment weights; group growth uses summed employment levels. Detailed growth uses the published BLS percentages. Detailed dots have equal sizes. Group bubbles encode sample employment. Coverage is relative to official major-group employment. Search isolates one occupation; clearing restores the group. The chart uses Chinese labels; the article's embedded copy translates the same chart into English.

The bin comparisons use only shared exposure intervals and pooled employment weights across intervals; they are descriptive, not causal or significance tests. Output CSVs report sample coverage. Predictions are not realized employment or AI replacement rates.
'''
with zipfile.ZipFile(DEST/'replication.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(R/f,f)
 z.writestr('README.md',readme)
 z.write(R/'README.md','full_analysis_README.md')
(DEST/'regression_table.md').write_text((R/'results/projection_patterns/regression_table.md').read_text())
print(DEST/'interactive.html')
