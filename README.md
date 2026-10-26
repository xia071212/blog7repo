# Blog 7: Closer to AI, Easier to Replace?

[Read the blog](https://xia071212.github.io/myrepo/blog/posts/post7/) | [Repository](https://github.com/xia071212/blog7repo)

## Reproduce the current article

The article uses BLS 2024-2034 employment projections, Anthropic occupational exposure, and task breadth matched against O*NET 30.0. It includes 722 detailed occupations. The historical OEWS/CPS analyses documented below are earlier explorations, not the current article's outcome variable.

Install the versions in `requirements.txt`, then run `code/build_interactive_sample.py`, `code/check_projection_patterns.py`, and `code/regress_projections.py` in that order. Paths resolve relative to the scripts. The BLS archive, exposure CSV, and matched task tables required for these steps are included. To rebuild the task matching itself, use `code/analyze_tasks.py` with the retained raw inputs.

- `results/interactive_sample.html`: offline Plotly chart; employment-weighted group bubbles and equal-sized detailed occupation dots, with occupation search and linked task details.
- `data/processed/projections_2024_2034_task_sample.csv` and `projections_major_groups.csv`: detailed and aggregated chart data.
- `results/projection_patterns/regressions.csv` and `regression_table.md`: separate exposure/breadth regressions and HC3 intervals.
- `code/build_blog_assets.py`: optional publishing helper. It writes English chart assets to the sibling website directory `myrepo1/blog/posts/post7/`; it is not required to reproduce the analysis.

The employment-weighted slopes are negative, but turn positive with group controls or equal occupation weights; the displayed 95% intervals include zero. These are descriptive associations with projected net employment, not measured AI replacement rates.

Large CPS monthly raw files are excluded from Git but remain available through `code/download.py`. Derived historical results are retained for comparison. Anthropic data are attributed under the source's CC-BY terms; see `data/raw/` and `data/sources.json` for source documentation.

## Earlier historical-employment analysis

## 当前结果

更高的 AI 暴露与 2022–2025 职业就业变化之间，**没有在两个调查中同时出现强、稳定的负向关系**。OEWS 有弱负关联；CPS 普通相关接近零，就业加权相关为弱负。不能把这解读为 AI 没有影响，也不能由个别下降职业推出 AI 导致岗位消失。

| 样本 | 职业数 | Pearson | Spearman | 基期就业加权 Pearson |
|---|---:|---:|---:|---:|
| OEWS 详细职业 | 754 | −0.077 | −0.032 | −0.192 |
| CPS 全部就业者，主样本 | 364 | 0.027 | 0.028 | −0.051 |
| CPS 工资薪金就业者，主样本 | 348 | 0.012 | 0.020 | −0.064 |

CPS 主样本要求两个端点各至少 100 条人月记录；不是 100 个独立受访者，也不是统计精度保证。保留全部 467 个匹配职业、仅单一 SOC 职业、要求 100% 暴露覆盖、去掉增长率两端各 1% 的结果均见 `results/correlations.csv`。所有相关系数均为描述性统计，不附未考虑调查设计的显著性星号。

OEWS 的程序员就业估计下降 30.5%，数据录入员下降 19.3%；金融和投资分析师增长 24.2%，市场研究分析师及营销专员增长 12.6%。这些都是高暴露职业，但变化方向不同。

极端值不能忽略：CPS 工资薪金样本的上门销售等职业增长约 374.6%，而 OEWS 同类职业下降约 68.1%。从 CPS 主样本单独去掉这一点，普通相关由 0.012 变成 −0.008，仍接近零。OEWS 中去掉数据科学家或程序员会改变相关系数，但未形成强相关。`*_influence.csv` 给出每个职业的留一法检查；`*_largest_declines.csv` 和 `*_largest_increases.csv` 保留端点人数与变化。

同一组 348 个 Census 职业的 OEWS 与 CPS 增长率普通相关仅 0.016，约 64.9% 的职业变化方向一致。这项比较仍存在调查对象、参考期和小样本差异；不适合把职业排名当成可靠的裁员排名。以该共同样本分析 OEWS，暴露与增长的普通相关为 −0.160；其加权版本为方便共同样本比较使用 CPS 2022 基期权重。

固定职业样本的 CPS 工资薪金就业指数显示，2022–2025 零暴露组增长约 2.42%，暴露度 >0.30 组约 2.49%。分组阈值是便于探索的分析设定，不是原论文的四分位处理组，也不是因果检验。

## 数据来源与时间口径

- [Anthropic 官方 Economic Index 数据集](https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main/labor_market_impacts)：`job_exposure.csv`，756 个 SOC 职业，字段 `occ_code`、`title`、`observed_exposure`。下载固定版本 `4e5f69fab13a9c3f7d0dcc31a6f893a9818738f6`；输入文件保留原样。
- [Anthropic 方法原文](https://www.anthropic.com/research/labor-market-impacts)，2026-03-05。该指标结合理论可行性与 **2025 年 8 月、11 月 Claude 使用数据**；自动化工作流赋全权重、增强型赋半权重，再按职业任务时间权重汇总。0–1 数值不是被裁员概率，不是企业采用率；0 表示未达到该观测指标的覆盖门槛，不表示 AI 永远无法做这些工作。
- [BLS OEWS 官方下载页](https://www.bls.gov/oes/tables.htm)：May 2022 和 May 2025 全国文件 `oesm22nat.zip`、`oesm25nat.zip`。本次直接 HTTP 返回 403，已通过官方页面浏览器下载原包。使用实际就业估计，不使用 2034 年就业预测。
- [Census CPS Basic Monthly](https://www2.census.gov/programs-surveys/cps/datasets/)：2022–2024 各 12 月，2025 共 11 月，合计 47 个文件。官方目录没有 2025 年 10 月文件；不填补、不假定为零。因此主对照各年均取 1–9、11–12 月均值；额外保留 2022–2024 完整 12 月均值与 2025 可用 11 月均值，后者不能统称为完全可比的全年均值。
- [2018 Census occupation code list and crosswalk](https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-occupation-code-list-and-crosswalk.xlsx)：使用 `2018 Census Occ Code List` 页的 Census 和 SOC 编码。CPS 是当前主职职业，不用 ASEC 上年主要职业或收入权重。

来源 URL、文件大小和 SHA-256 保存在 `data/sources.json`。官方方法网页文本、年度 CPS 字典及目录快照在 `data/raw/`。原始数据约 464 MB；不默认提交到 Git。Anthropic 数据按其 README 为 CC-BY，代码 MIT；这里保留来源归属，未作公开再发布。

## 清洗、匹配与权重

**OEWS：**仅保留全国 `AREA=99`、跨行业 `NAICS=0`、总所有制 `OWN_CODE=1235`、`O_GROUP=detailed`，不把职业大类、子类和详细职业重复相加。两个年份各 830 个详细发布类别。SOC 字符串精确连接，不按名称模糊匹配，不把缺少暴露的数据当作零。有效配对 754 个，占 2022 年发布职业的 **90.84%**，覆盖其详细职业就业估计的 **91.01%**；占 Anthropic 756 个职业的 **99.74%**。Legislators 和 Prosthodontists 未形成完整端点就业配对。缺失和未匹配清单分别输出。

就业百分比变化为 `100 × (E2025 / E2022 − 1)`；同时保存绝对变化和对数变化。主表不删极端值。就业加权 Pearson 使用 2022 基期职业就业人数，避免结果期权重随就业变化调整。

**CPS：**使用 `PRTAGE>=16`、`PEMLR` 为 1 或 2、`PWCMPWGT>0`。`PWCMPWGT` 为 BLS 劳动力统计使用的 composited final weight，定宽文件带四位隐含小数，除以 10,000；职业字段为 `PTIO1OCD`。工资薪金子样本限 `PEIO1COW=1..5`，排除公司化与非公司化自雇及无酬家属劳动，作为更接近 OEWS 的比较口径；它仍不是 OEWS 完全一致的人群。

先按月求职业内个人权重之和，再对相同 11 个月取均值；不能把跨月权重直接相加解释成人数。记录数是人月数，轮换样本会重复观察同一人。某职业在某月没有样本时，该月样本估计贡献为零，分母仍使用所有可用月份。

**SOC → Census：**先匹配明确 SOC，再展开末尾 0 的层级代码与 X 残余代码；更具体的代码优先，残余类只接收未由更具体类别吸收的 SOC，同分歧义排除并输出。每个 SOC 最多进入一个 Census 职业。以 OEWS 2022 就业人数为固定权重，在 Census 类别内部汇总暴露度；这一步的权重与 CPS 的个人调查权重用途不同。

覆盖率分母为可映射到该 Census 类别的 2022 OEWS 就业人数。仅当有暴露值的就业权重占比至少 90% 时纳入，未覆盖部分不填零，而在有覆盖部分内归一化。该覆盖率不衡量 OEWS 本身未覆盖的自雇及农业等人口。另报告 100% 覆盖和单一 SOC 类别敏感性。CPS 与 Census 标准编码表仍有未匹配发布类别，全部保留在 `cps_*_all_matches.csv`，没有强行赋值。

CPS 两个端点各观察到 525 个职业类别，467 个达到暴露覆盖门槛，职业匹配率 **88.95%**。全部就业者人数覆盖率为 2022 年 **90.86%**、2025 年 **90.29%**；工资薪金子样本为 **90.39%**、**89.83%**。随后按人月数筛选得到 364/348 个主样本职业，不能将筛选前覆盖率误称为最终绘图样本覆盖率。最终绘图样本覆盖率见 `cps_plot_coverage.csv`：全部就业者为 89.53% / 88.91%，工资薪金为 88.72% / 88.12%（2022 / 2025）。

## 文件与复现

- `code/download.py`：获取官方输入并记录来源。已有文件优先使用，避免覆盖原始快照；Anthropic URL 固定版本。BLS 若再次拒绝 HTTP，按官方链接下载同名 ZIP 放入 `data/raw/`。
- `code/analyze.py`：读取、清洗、匹配、权重汇总、相关性、极端值检查、输出图表。全部路径相对脚本，无需使用特定工作目录。
- `data/raw/`：原始压缩文件、crosswalk、字典与方法快照。注意 Census 的 `jan24pub.dat.gz` 实际为 ZIP 容器；代码按文件签名识别，不改原始文件。
- `data/processed/`：OEWS 清洗及匹配表、SOC–Census 展开表、Census 暴露值、CPS 月度及年度职业表、完整匹配状态与最终样本。
- `results/OEWS_interactive.html`、`CPS_all_employed_interactive.html`、`CPS_wage_salary_interactive.html`：独立 Plotly 散点图，可悬停查职业、就业基数与变化，点击图例筛选 SOC 大类，框选放大。全部嵌入 Plotly，无需 CDN。
- `results/survey_comparison.html`：同职业两调查变化的比较。`cps_exposure_group_trend.html`：固定职业和暴露分组的 2022–2025 就业指数。
- `results/*_scatter.png`：静态预览；其余 CSV 为相关性、匹配覆盖、极端值及影响度表；`summary.json` 为机器可读摘要。

使用 Python 3.12，安装 `requirements.txt` 所列依赖，然后运行 `code/analyze.py` 即可从已有原始文件重建结果；重新获取输入时先运行 `code/download.py`。这份包保留了复现所需数据，不依赖临时计算环境。`code/verify.py` 执行输入完整性、端点计算和单月权重交叉核验。

## 方法局限与下一步判断

1. **这不是因果分析。** 暴露指标来自 2025 年后期、发表于 2026 年，不能当作 2022 年预先观测的处理变量。技术趋势、行业需求、疫情后恢复、教育组成等可同时关联暴露和就业变化。
2. **OEWS 不是精确年度岗位流量。** [BLS 官方 FAQ](https://www.bls.gov/oes/oes_ques.htm#other) 不鼓励把 OEWS 当时间序列；每期混合六个半年面板。2022 和 2025 的面板窗口不重叠，但 2022 窗口跨疫情，且估计仍依赖职业结构与基准更新假设。两个年份都采用 2018 SOC、2022 NAICS 和 MB3，有助于减少部分可比性问题，但不能消除它们。
3. **CPS 更及时但详细职业噪声较大。** 当前计算没有复杂抽样方差、复制权重或轮换组相关调整，也未消除人口控制更新造成的跨年断点。100 人月门槛、截尾和留一法只是诊断，不能替代标准误；不作显著性结论。
4. **两套调查估计不同对象。** OEWS 为机构岗位，CPS 为个人主职；自雇、农业、私人家庭、多个工作及参考期差异仍存在。Census 聚合暴露使用 OEWS 内部职业结构，可能不代表 CPS 同类人的结构。
5. **缺失具有选择性。** 约 9% 的 OEWS 就业和部分 CPS 职业未纳入。共同职业比较中的 OEWS 增长也只覆盖有完整暴露与两端就业的 SOC，而 CPS 类别可能更宽；请结合覆盖表阅读。

适合继续探索的问题是“高暴露职业是否真的都在萎缩，以及哪些职业例外”，而不是先定下“AI 已经导致就业下降”的结论。图中可检验到的结果支持前一个问题。

## 已完成核验

47 个原始月度文件通过压缩完整性检查，来源 SHA-256 一致；独立定宽解析复核了 2022 年 1 月 CPS 总人数及样本记录数。已检查唯一匹配键、就业变化计算和共同 11 月分母。OEWS 交互图在浏览器正常显示 754 个点，点击 11 类图例后变为 720 个点，验证筛选生效；静态图已目视检查。其余交互图已生成，但未逐一进行浏览器操作测试。

## 新增：任务结构分析与 Anthropic 原文对照

本扩展使用 `code/analyze_tasks.py`，输出在 `results/tasks/`。**任务结构指标未揭示强而稳定的就业负关联；它提供了指标解释上的发现，而非就业变化原因的识别。**

### 对应表与指标

使用 [O*NET 30.0 Task Statements](https://www.onetcenter.org/dl_files/database/db_30_0_excel/Task%20Statements.xlsx)，与 Anthropic 同一固定版本的 `task_penetration.csv` 连接。仓库旧版任务表包含 2010 SOC 编码，未用于最终分析。新版表按小写、空格标准化任务文本匹配，不做语义模糊匹配；重复渗透文本先确认数值一致再去重。O*NET 子职业折叠到六位 SOC 后，同一职业中的相同任务只计一次。

去重后的 18,773 个 SOC–任务组合中，18,660 个有对应渗透值（99.40%）。缺失不是零。主分析要求一个职业至少 95% 的任务可匹配，另用 80%、100% 门槛检验。以任务数而非劳动时间计权；不能复原 Anthropic 的时间权重，也不声称复现其原始指标。

- **覆盖广度**：匹配任务中 penetration > 0 的比例。全部正值至少为 0.5，因此 ≥0.5 的比例与该指标相同，并非独立检验。
- **高渗透比例**：匹配任务中 penetration ≥0.8 的比例，0.8 是分析阈值，不是官方经济含义边界。
- **平均渗透值**：匹配任务的简单平均。
- **集中度**：对任务渗透值归一化后的 HHI，再按任务数归一化，公式为 `(sum((p/sum(p))²)−1/n)/(1−1/n)`。全部任务为零或只有一个匹配任务时无定义，不赋零。集中度在 OEWS 有正渗透的职业内分析，不直接转成 CPS 广义职业的任务集中度。

CPS 的广度、平均值与高渗透比例按固定 OEWS 2022 职业就业权重汇总；要求 Census 类别至少 90% 的可映射 OEWS 就业来自任务匹配达标的职业。仍保留原来的 CPS 端点人月数筛选。

### 主要结果

| 主样本（任务匹配≥95%） | 职业数 | 任务广度与就业变化 Pearson | 基期就业加权 Pearson |
|---|---:|---:|---:|
| OEWS | 721 | −0.0215 | −0.1518 |
| CPS 全部就业者 | 344 | 0.0515 | −0.0411 |
| CPS 工资薪金 | 330 | 0.0411 | −0.0514 |

不同任务匹配门槛下，OEWS 普通相关约 −0.021 至 −0.032，CPS 工资薪金约 0.038 至 0.044。没有因换用覆盖广度而出现强负关联。主样本中，广度与官方职业暴露度的普通相关为 OEWS 0.798、CPS 工资薪金 0.928，新增指标与原指标有大量重叠信息。

把广度和就业变化分别对官方暴露度、职业大类进行线性残差化后，残差相关为 OEWS −0.032、CPS 工资薪金 0.044；就业加权对应约 0.021、−0.011。此为描述性条件关联，不是因果控制，也未验证样本外预测力。

OEWS 主样本中 379 个职业有可定义的集中度；控制官方暴露度、任务广度及职业大类后，集中度与就业变化的残差相关约 −0.093，就业加权为 −0.048。未支持“暴露集中在少数任务可解释就业更有韧性”的清晰正向关系，也不足以证明相反机制。匹配门槛和截尾敏感性结果完整保留在 `associations.csv`，不进行多重探索后的显著性宣称。

一个有意义的例子：数据录入员 9 项列示任务中只有 1 项有正渗透值，广度 11.1%，但官方时间加权职业暴露度为 67.1%；程序员为 10/17 项（58.8%），官方暴露度为 74.5%。不能把任务数比例解释成工作时间比例，也不能从这些数字断言具体哪项任务占了多少时间。O*NET 子职业任务取并集还会影响分母；这些并不是每个劳动者实际执行的任务清单。

### 与 Anthropic 研究的关系

对照 [2026-03-05 原文](https://www.anthropic.com/research/labor-market-impacts)：

1. Figure 4 研究的是 **BLS 2024–2034 就业预测**，报告暴露度每增加 10 个百分点，预测增长下降约 0.6 个百分点。我们分析的是 **2022–2025 已发布就业估计的变化**；不能直接比较系数，弱负或近零结果不否定预测结果。
2. Figure 6 使用 CPS 研究高暴露组相对零暴露组的 **失业率**，未发现 ChatGPT 发布后系统性上升。我们未发现广泛而强的职业就业负关联，与其谨慎的整体判断不矛盾，但不是失业率结果的复现。就业减少、失业增加并非同一个指标。
3. Figure 7 对 **22–25 岁的新就业进入**发现提示性放缓，约 14% 的相对下降，作者称仅勉强达到统计显著，并讨论其他解释。我们的全年龄就业存量不能检验或排除这种年龄特定的招聘流量变化。

适合博客的措辞是：我们的描述性结果与 Anthropic 尚未发现广泛失业上升的结果相容，但考察了不同的结果变量；不能声称验证其因果结论，更不能说 AI 没有劳动力市场影响。

任务扩展的用途：在正文或悬停提示中解释“任务暴露≠任务数占比≠裁员概率”。现有结果不足以把任务集中程度作为文章已证实的机制。`task_breadth.html` 为补充交互图；`examples.csv` 保留实际例子，`task_matches.csv` 保留所有匹配和缺失明细。

## Projection-based interactive sample

The sample builder now uses official BLS 2024-2034 archived occupation.xlsx Table 1.2, Line item rows, joined by SOC to exposure and task metrics with >=95% task matching: 722 occupations. Employment is converted from thousands to persons; growth uses the published percentage, not a recalculation from rounded levels. Historical OEWS/CPS outputs remain unchanged. The horizon matches Anthropic Figure 4, but the sample restrictions differ; this is not an exact replication.

The interface uses 22 category colors, removes the four example shortcuts, and restricts occupation search to the selected major group. A category change selects its first occupation if the existing selection is outside that group. X ranges use the global maximum for the active metric plus padding (77% exposure; 67% breadth). Group filtering preserves scales.

The prototype defaults to 22 SOC major-group bubbles. AI exposure and task breadth are weighted by 2024 employment within the same matched sample; group growth is the percentage change in summed employment, and bubble area represents sample employment in 2024. Hover reports sample employment coverage relative to the official group total (coverage varies by group). Click a bubble to see its detailed occupations; the occupation search narrows to that group. The level controls precede the group filter. Aggregates are saved in `data/processed/projections_major_groups.csv`; rebuilding the prototype regenerates both aggregation and HTML.

### Detailed bubble sizes and group-pattern checks

Detailed occupations use equal-sized dots to limit overlap; selection adds an outline. Major-group bubble area still represents 2024 employment. Selecting an occupation name or SOC filters the chart to one dot, clearing the search restores the group, and changing the group resets the occupation filter. BLS occupation-title indentation is stripped before matching search values.

Run `python code/check_projection_patterns.py` after rebuilding the sample. Outputs are in `results/projection_patterns/`: group summaries, exposure-bin comparisons, descriptive slopes, within-group variation, narrower-group checks, exclusion of each group's largest occupation, and a two-panel figure.

The comparisons use 5- and 10-percentage-point exposure bins. For each target group versus sales, only shared bins are retained; both groups are standardized to the same pooled 2024 employment weights across those bins. Within-bin growth is employment-weighted using published detailed growth percentages. These are approximate exposure comparisons, not causal matching or significance tests. Shared-bin coverage is reported relative to each group's matched sample. Computer/mathematical coverage falls to 68.6% in the 5-point comparison, so results do not represent every occupation in that group.

Business/financial growth exceeds sales by 7.14–7.62 percentage points after bin standardization; computer/mathematical exceeds sales by 13.62–14.39 points. Excluding each group's largest occupation preserves the positive versus negative group-growth pattern. Nevertheless, 10 of 19 sales occupations grow, while 3 of 18 computer/mathematical occupations decline. The narrower financial-operations sample has 4.56% projected growth; computer occupations have 8.75%. Group averages are not statements about every member, and category codes do not measure technical skill.

Across all 722 occupations, the descriptive employment-weighted exposure slope changes from -0.53 growth points per 10 exposure points to +0.43 after including major-group indicators (unweighted slopes: +0.11 and -0.07). The direction is sensitive to weighting and occupational composition. BLS projections describe expected employment demand, not observed job changes or an estimated AI treatment effect. Complementarity, substitution, and demand shifts are possible explanations requiring additional evidence, not conclusions identified by these comparisons.

### Blog 7 draft assets

`code/build_blog_assets.py` creates an English version of the same interactive chart and a focused replication ZIP under the sibling website's `blog/posts/post7/` folder. Run it after `build_interactive_sample.py`. The Quarto article source lives in that website folder; the analysis and historical OEWS/CPS outputs remain here. The article uses the projection comparisons, not a measured AI replacement rate. The focused download includes the existing processed task-match inputs rather than re-downloading and re-matching O*NET.

### Regressions in the article

`code/regress_projections.py` estimates separate regressions of published 2024–2034 percentage employment growth on exposure and task breadth, using all 722 matched occupations. Each coefficient is per 10 percentage points of its indicator. Baseline WLS uses 2024 employment weights; sensitivity checks use major-group intercepts and equal occupation weights. HC3 covariance is calculated on the transformed WLS design, with Student-t intervals using N minus the design rank degrees of freedom. These are model-based cross-occupation intervals, not BLS forecast intervals or causal AI displacement estimates; within-group error dependence is not modeled. Outputs are `results/projection_patterns/regressions.csv` and `regression_table.md`. The article table is copied programmatically by `build_blog_assets.py` and included by Quarto. Run this regression script before building the article assets.
