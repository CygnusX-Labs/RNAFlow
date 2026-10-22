# KEGG 模块调查与双路径建议

调查日期：2026-10-21。范围：当前 RNAFlow 工作树、主流程和独立 skill 入口、官方接口与统计约定。此文交付调查结论和实施设计，不代表双路径功能已经实现。

## 结论

建议保留两条显式选择的注释路径：有合适官方物种注释时使用 KEGG 官方数据；非模式生物或项目基因组与官方注释不匹配时使用项目自己的注释。两条路径统一到 pathway → 项目基因的 TERM2GENE，再使用一致的 ORA、背景和 BH 校正策略。

选择依据应是“官方物种覆盖、参考基因组版本和 ID 映射质量”，不能仅依据“是否模式物种”。例如番茄有 KEGG 代码 sly，旧 KEGG.db 包是否包含 sly，不能用来判断官方数据库是否支持番茄。

当前代码尚未实现这套双路径。现有文档与代码存在明显差异，不能依据文档里的历史验证数字认定当前模块已经离线、已经使用 TERM2GENE 或背景已经正确。

## 当前实现证据

仓库 HEAD：`1eb4ee765245fe96ddb9bcdd532e9902e8359cda`；src 子模块 HEAD：`044e470c592e9bfa06e78a8081df0c109cf1fff5`。调查以实际文件为准；工作树原有其他修改未纳入本次改动。

| 环节 | 实际行为 | 含义 |
| --- | --- | --- |
| `config/run_parameter.yaml`、`rules/10.DEG_Enrichments.smk` | 默认执行 `src/src/Enrichments/deg_enrich_wrapper.py` 与 `kegg_enricher.r` | 这是本次调查的主执行链 |
| `config/reference.yaml` 的 ITAG4.1 | 配置了 organism、id_map、term2gene、term2name | 配置出现不等于算法消费了该字段 |
| 主 wrapper 的 `main()` | 要求 organism，只转发 organism、gene_col、id_map 和部分阈值；不转发 term2gene/term2name，也未转发 KEGG gene_regex、min/maxGSSize | 自定义注释未接通，配置可能被静默忽略 |
| R 的 `command_line_main()` | 没有 term2gene/term2name 或数据源选择参数 | 文档中的这些命令不能由此入口执行 |
| R 的 `run_kegg_enrichment()` | 直接调用 `enrichKEGG()`，没有设置 `use_internal_data=TRUE` | 按该函数默认约定使用在线 KEGG；不能称为纯离线或 KEGG.db 模式 |
| R 的 `run_kegg_deg_table()` | 背景传入 `unique(id_map$ncbi)` | 有 id_map 时使用整张映射表的目标 ID，可能包含本次没有参加 DEG 检验的基因 |
| R 的 ID 处理 | 无条件去版本号、去前缀，`distinct(symbol, .keep_all=TRUE)` 后使用 `match()` | 不是文档所称“先精确匹配、低匹配率再回退”；歧义和一对多关系可能被静默截断 |
| R 的统计参数 | UP/DOWN 分开；BH；默认 minGSSize=10、maxGSSize=Inf；主表按 p.adjust 筛选 | 文档所列 maxGSSize=500 不是当前 CLI 默认；阈值应显式记录 |
| R 的空结果分支 | 部分分支仅输出占位主表，不写全量表；没有映射时 warning 后返回 | 应区分无 DEG、映射失败、无可检验通路与无显著结果 |
| 输出与摘要 | 当前 R 写 `{contrast}_UP_enrichments.csv` 等；摘要优先寻找含 `_KEGG_` 的名字，但支持旧名回退 | 当前可被兼容读取，但不是文档宣称的统一命名；不可误报为完全无法读取 |
| `src/skills/enrichments/scripts/run_enrichment.py` 及其 wrapper | single/batch 均围绕 GO，目录中无 KEGG R 脚本 | skill 与主流程能力尚未同步 |
| `src/src/KEGG_pull/kegg_pull/core.py` | 可下载官方物种 gene→pathway、gene→KO、通路名，产出 GMT、TSV 和时间/来源摘要 | 可复用官方数据准备能力；其带表头、多列 TSV 不能直接当两列无表头 TERM2GENE |
| `rules/utils/project_summary.py` | KEGG method 固定写 enrichKEGG；缺少注释文件校验值、来源模式和覆盖统计 | 双路径后需要报告实际来源和实际算法 |

`rules/utils/reference_update.py` 已包含 term2gene/term2name 路径处理，Snakemake 也将文件列为输入，但这些并不能证明 R 端读取了注释。

## 路径 A：KEGG 官方物种注释

适用条件：KEGG 有该物种；项目基因 ID 能可靠对应官方基因；参考组装/注释版本差异可以解释。

推荐流程：

1. 在数据库准备阶段通过 KEGG REST 或现有 KEGG_pull 下载 gene→pathway、通路名及必要的 ID 转换数据。
2. 保存原始响应、下载日期、来源 URL、物种、参考版本、文件 SHA256 和软件版本，形成可复用快照。
3. 将项目基因映射到官方基因，再反向生成 pathway→项目基因的 TERM2GENE，保留映射证据和歧义记录。
4. 富集阶段读取固定快照，在项目基因层面计数，并用共同的背景和统计参数运行 `enricher()`。

直接在线 `enrichKEGG()` 也可以使用官方注释，但每次运行可能遇到数据库更新和网络差异。作为探索方式可以保留；可复现生产分析优先固定快照。旧 KEGG.db 不能替代“当前官方数据库快照”的概念。

KEGG 官方 API 提供 `link/pathway/<org>`、`list/pathway/<org>` 和 ID 转换操作；官方基因 ID 可能是 NCBI GeneID，也可能是 locus tag，不能统一假设为 Entrez 数字。[KEGG API 手册](https://www.genome.jp/kegg/rest/keggapi.html)

## 路径 B：项目自定义注释

适用条件：没有合适官方物种数据，或项目参考基因组与官方版本差异较大。模式物种的特殊品系、重新组装基因组也可以使用这条路径。

支持两种输入来源：

- 已有可信的 gene→pathway 注释：转换为 TERM2GENE，保留原始基因 ID。
- 已有 gene→KO 注释：连接固定版本的 KO→pathway 表，展开为 pathway→项目基因；保留所有有效多对多关系，再对相同 pathway/gene 对去重。

不能把 K00001 等 KO 当作目标基因直接提交给按基因计数的 ORA。一个 KO 可能对应多个项目基因；每条通路内按唯一项目基因计数，避免把 KO 数或注释行数当成基因数。

最低文件契约建议为：

```text
# term2gene.tsv：无表头，两列 TAB；示意数据
map00010	project_gene_A
map00010	project_gene_B
map00020	project_gene_A

# term2name.tsv：无表头，两列 TAB
map00010	Glycolysis / Gluconeogenesis
map00020	Citrate cycle (TCA cycle)
```

上方注释行仅为说明，真实输入不含说明行。通路 ID 命名应统一，不能混用 map00010、ko00010 和物种通路后再重复计数。

KO→pathway 属于参考层面的功能对应。非模式植物出现疾病命名通路等结果时，需要检查保守基因共享关系；不能据名称推断该物种发生了人类疾病。若使用物种类群筛选，必须保存筛选依据与被排除清单。

自定义注释的可靠性取决于注释工具、版本、参考库、覆盖度和质量阈值；双路径本身不会自动保证结果可靠。`enricher()` 提供自定义 TERM2GENE/TERM2NAME 接口。[clusterProfiler 官方手册](https://bioconductor.org/packages/release/bioc/manuals/clusterProfiler/man/clusterProfiler.pdf)

## 共同的可靠性要求

1. **明确背景。** ORA 查询集是 DEG 子集；背景应来自本次有机会进入所用 DEG 筛选的基因，再与有效通路注释取交集。若按 padj 筛选，需要明确如何处理 DESeq2 independent filtering、padj=NA、outlier 和低表达过滤。不能默认使用整张 id_map 或所有基因组注释。若希望采用其他背景，须提供显式输入和理由。
2. **一致的计数单位。** 两条路径都优先采用项目基因；一个基因对同一通路只计一次。官方 ID 折叠会改变计数单位，应记录；转录本级结果应先约定如何聚合到基因级。
3. **映射可审计。** 默认精确匹配；前缀和版本号清洗显式配置，同时作用于背景与查询。发现清洗碰撞或一对多歧义时输出明细并按约定处理，不能直接取第一条。查询和背景完全无注释匹配应报错，不能伪装成“无显著富集”。
4. **报告覆盖。** 每个比较组和方向输出输入基因数、合格背景数、映射数、通路注释命中数、最终背景数、未映射列表和歧义数。低覆盖提示解释边界，不为了增加显著通路放宽阈值。
5. **统计口径固定。** 记录 DEG 阈值、min/maxGSSize、BH 校正和实际检验通路数；主表按预先约定的 FDR 筛选，全量表保留原始 p 与 p.adjust。UP/DOWN 默认各自校正，需注明未控制跨方向/跨比较组的整体 FDR。
6. **数据源显式。** 分析前校验必需字段和 ID 命名空间。官方路径失败不得自动静默切换到自定义或其他物种。可以同时跑两种来源作敏感性比较，但分别输出来源和统计结果，不能合并显著项后继续声称具有原来的 FDR 控制。
7. **结果状态完整。** 无 DEG、映射失败、无可检验通路、无显著通路、执行失败分别记录；所有成功分支都按固定 schema 写主表和全量表。摘要 method/source 与实际执行一致。

## 建议配置契约（设计草案，当前不可直接使用）

```yaml
kegg:
  enabled: true
  source: official  # official 或 custom；显式选择
  organism: sly    # official 必填；custom 不要求伪造物种代码
  gene_col: ENSEMBL
  term2gene: ITAG4.1/kegg/term2gene.tsv
  term2name: ITAG4.1/kegg/term2name.tsv
  annotation_metadata: ITAG4.1/kegg/metadata.json
  min_gs: 10
  max_gs: 0        # 0 表示不限制，必须在结果中记录
```

两种来源都先准备为项目基因空间的文件；official 在准备阶段另外使用 id_map 及其质量记录，custom 可在准备阶段由 gene→KO 展开。分析入口不应因为 custom 缺少 organism 而拒绝执行。是否兼容直接在线模式可另设显式配置，不与离线快照含混共用。

## 实施顺序及验收

| 顺序 | 要完成的改动 | 验收证据 |
| --- | --- | --- |
| 1 | 主 wrapper、R CLI 接通 source 和 TERM2GENE/TERM2NAME；custom 不要求 organism；校验失败明确退出 | 无 organism 的自定义小数据能端到端运行；缺文件、非法列、零注释交集明确失败 |
| 2 | 统一项目基因空间和背景；显式处理 ID 清洗及歧义 | 添加大量未参加检验的映射基因不改变背景/结果；版本号碰撞有明细；多对多注释无丢失、无重复计数 |
| 3 | 接入 KEGG_pull 快照、格式转换及 metadata | 官方物种真实数据完整跑通；同一快照断网重复运行得到相同数值结果；摘要可追溯原始文件及校验值 |
| 4 | 统一主流程、独立 skill、文件命名和项目摘要 | 两种来源在 UP/DOWN 和全量/主表中均可读取；实际 source/method 正确；旧名兼容单独验证 |
| 5 | 数值和状态验收 | 用小型已知背景手工核对超几何 p 值与 BH；核对 GeneRatio/BgRatio；覆盖空 DEG、无显著、映射失败等分支 |

## 本次验证边界

已检查主流程配置、规则、wrapper、R 实现、下载器和摘要入口，并以 Python AST/源码检查确认：wrapper 未转发 TERM2GENE，R 无对应 CLI，无显式离线开关，背景使用整张映射表，ID 清洗后仅保留首项。已核对 KEGG 与 Bioconductor 官方文档。

本次没有重新运行真实项目，也没有验证既有文档中 Salt_vs_AC 的统计数字；这些数字只视为历史记录。此调查不宣称双路径已经实现或真实分析结果已通过验收。
