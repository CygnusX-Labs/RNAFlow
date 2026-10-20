# 离线 KEGG 富集

KEGG 接在现有 GO 批量比较组流程中，分别分析 UP、DOWN。
全程不做在线查询：要么使用 KEGG.db（`enrichKEGG(..., use_internal_data=TRUE)`），要么使用本地的 TERM2GENE/TERM2NAME 注释（`enricher()`）。

## 两种注释模式

### 1. KEGG.db 模式

适用于 KEGG.db 覆盖的物种。KEGG.db 3.2.4 只包含 20 个物种（aga、ath、bta、cel、cfa、dme、dre、eco、ecs、gga、hsa、mcc、mmu、pfa、ptr、rno、sce、ssc、xla），**不包含番茄 sly**。

在运行富集规则的 R 环境中安装 KEGG.db：

```r
install.packages("/path/to/KEGG.db_3.2.4.tar.gz", repos=NULL, type="source")
library(KEGG.db)
library(clusterProfiler)
```

现有 `envs/go_enrich_r.yaml` 不包含 KEGG.db，需要安装到实际运行的环境。缺包、物种无通路、背景基因完全不匹配都会报错。

### 2. TERM2GENE 模式（适用于 sly 等未覆盖物种）

直接从 KEGG REST 下载注释并保存为两列表格（无表头，TAB 分隔），运行时完全不联网。

```bash
# pathway -> KEGG gene ID
curl -s https://rest.kegg.jp/link/pathway/sly | sed 's/^path://' > ITAG4.1.kegg.term2gene.tsv
# pathway ID -> pathway name
curl -s https://rest.kegg.jp/list/pathway/sly > ITAG4.1.kegg.term2name.tsv
```

提供 `term2gene` 后 `organism` 不再使用，也不再要求安装 KEGG.db。

## 启用番茄（ITAG4.1）

`config/reference.yaml` 中已启用：

```yaml
deg_enrich_wrapper:
  ITAG4.1:
    gene_col: ENSEMBL  # 原有 GO 配置
    kegg:
      enabled: true
      organism: sly
      gene_col: ENSEMBL
      id_map: ITAG4.1/ITAG4.1.kegg.id
      term2gene: ITAG4.1/ITAG4.1.kegg.term2gene.tsv
      term2name: ITAG4.1/ITAG4.1.kegg.term2name.tsv
```

`id_map`、`term2gene`、`term2name` 相对 `reference_path` 解析，也可以填写绝对路径。

`id_map` 无表头，两列 TAB 分隔：

```text
Solyc00g160260.1.1	101261876
Solyc00g160270.1.1	101247603
```

DEG 表（ITAG4.1）的 `ENSEMBL` 列不带版本号，而 `id_map` 第一列带版本号。脚本先尝试精确匹配，匹配率低时自动去掉 `(\.\d+)+$` 版本后缀重试，并输出两种匹配数量。如果 DEG 基因列本来就是 KEGG 基因 ID，可以省略 `id_map`。

## 单独测试

```bash
Rscript src/src/Enrichments/kegg_enricher.r \
  --table /path/to/A_vs_B_DEG.csv \
  --name A_vs_B \
  --out_dir /tmp/kegg_test \
  --organism sly \
  --gene_col ENSEMBL \
  --id_map /path/to/ITAG4.1.kegg.id \
  --term2gene /path/to/ITAG4.1.kegg.term2gene.tsv \
  --term2name /path/to/ITAG4.1.kegg.term2name.tsv \
  --padj_th 0.05 --lfc_th 1 --cutoff 0.05
```

完整流程按原来的 RNAFlow 命令运行即可。DEG 阈值来自 `parameter.DEG.PVAL/LFC`，富集阈值来自 `parameter.Enrichments.cutoff`（默认 0.05）。
背景是 DEG 全表中 padj 非 NA、LFC 有限的基因，映射后与 KEGG 注释取交集；映射为同一目标 ID 的基因只计算一次。

## 输出

- GO 输出 `07.Enrichments/{contrast}_GO_UP.csv`、`{contrast}_GO_DOWN.csv`。
- KEGG 输出 `07.Enrichments/{contrast}_KEGG_UP_enrichments.csv`、`{contrast}_KEGG_DOWN_enrichments.csv`；全量表以 `_enrichments_full.csv` 结尾。
- `geneID` 为 KEGG 基因 ID；Input_Gene_Count 为筛选后的源基因数，Background_Match_Count 为注释匹配后的目标基因数，Universe_Gene_Count 为背景目标基因数。
- 无差异基因或无显著通路输出 Count=0 的占位行；运行错误以非零状态退出。

## 验证结果（2026-10-20，X101SC26098749-Z01-J001）

在番茄 ITAG4.1、`Salt_vs_AC` 真实数据上通过 Snakemake 规则完整运行：

- 背景基因 21,723，版本号回退匹配 20,993，KEGG 注释内背景 4,902。
- UP：1,646 个 DEG，映射 1,555，5 条显著通路（sly00052、sly04016、sly00280、sly04075、sly00330）。
- DOWN：2,503 个 DEG，映射 2,369，10 条显著通路（sly03010 核糖体，p.adjust 8.88e-22 等）。

## 显著通路数量说明（2026-10-20）

在 `Salt_vs_AC` 上复核了“显著通路偏少”的原因，主要来自注释覆盖、通路规模和显著性阈值三方面：

- KEGG 番茄注释共 165 条通路；`ITAG4.1.kegg.id` 覆盖 11,961 个 KEGG 通路基因中的 5,376 个。
- 能映射进 KEGG 的 DEG：UP 330/1,646，DOWN 699/2,503，因此实际参与富集的基因数远小于 DEG 总数。
- `clusterProfiler::enricher()` 默认 `minGSSize=10, maxGSSize=500`，会排除番茄的大通路。
- 当前流程按 `p < 0.05` 且 BH `p.adjust < 0.05` 输出。

不同阈值下的结果对比：

| 方向 | 当前输出（maxGSSize=500, FDR<0.05） | maxGSSize=Inf, FDR<0.05 | maxGSSize=Inf, nominal p<0.05 |
|---|---|---|---|
| UP | 5 | 6（新增 sly01110） | 15 |
| DOWN | 10 | 12（新增 sly01100、sly01110） | 25 |

说明与建议：

- `sly01100`（Metabolic pathways）和 `sly01110`（Biosynthesis of secondary metabolites）在番茄注释中分别有 2,604 和 1,478 个基因，属于宽泛通路，是否纳入取决于报告定位。
- 当前主表保持 FDR<0.05 更稳妥；若需要更多条目，建议额外输出一张 nominal p<0.05 的全量表并保留 `p.adjust` 列，而不是直接放宽主表。
- 坐标法只能把约 600 个缺失的 KEGG 通路基因映射回 ITAG4.1（6,477 个缺失基因中），因此短期内通过扩大 `id_map` 提升覆盖的空间有限。
- GO 结果条数远多于 KEGG 是因为 GO 条目数量本身大得多，两者数量不可直接比较。

## 已知限制

- 旧内置报告已弃用，不适配新文件名；外部报告应读取 `project_summary.json` 中 GO/KEGG 各自的 `table` / `full_table`，不要自行猜测文件名。
- KEGG.db 3.2.4 的番茄等物种必须走 TERM2GENE 模式。
