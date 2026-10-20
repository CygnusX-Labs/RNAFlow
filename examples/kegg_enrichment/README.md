# 独立版离线 KEGG 富集

从 RNAFlow 主流程中抽出的 KEGG 核心分析代码，不依赖 Snakemake 和流水线目录结构，可单独运行。

## 文件

| 文件 | 作用 |
| --- | --- |
| `kegg_enricher.r` | 核心分析脚本，按 UP/DOWN 分别做离线 KEGG ORA |
| `run_kegg_batch.py` | 批量调度，遍历 DEG 统计表中的所有比较组并调用 R 脚本 |

主流程中的原始位置：

- `src/src/Enrichments/kegg_enricher.r`
- `src/src/Enrichments/deg_enrich_wrapper.py`（KEGG 调度部分）
- `rules/10.DEG_Enrichments.smk`（`Enrichments` 规则）

## 依赖

R 环境需要 `optparse`、`clusterProfiler`、`KEGG.db`。KEGG.db 不在 conda 源中，需安装自己的离线包：

```r
install.packages("/path/to/KEGG.db_1.0.tar.gz", repos = NULL, type = "source")
library(KEGG.db)
library(clusterProfiler)
```

分析固定使用 `clusterProfiler::enrichKEGG(..., keyType = "kegg", use_internal_data = TRUE)`，不会回退到在线数据库。

## 输入

DEG 表（CSV 或 TAB 分隔，分隔符自动识别）必须包含：

- `--gene_col` 指定的基因 ID 列（默认 `ENSEMBL`）
- `padj`
- `log2FoldChange`

`--id_map` 为无表头两列 TSV，第一列与 DEG 基因列精确匹配（不自动去版本号），第二列是 KEGG 基因 ID（允许带 `sly:` 前缀）：

```text
Solyc00g160260.1.1	101261876
Solyc00g160270.1.1	101247603
```

如果 DEG 基因列本身就是 KEGG 基因 ID，可省略 `--id_map`。

## 单比较组运行

```bash
Rscript kegg_enricher.r \
  --table /path/to/A_vs_B_DEG.csv \
  --name A_vs_B \
  --out_dir /tmp/kegg_test \
  --organism sly \
  --gene_col ENSEMBL \
  --id_map /path/to/ITAG4.1.kegg.id \
  --padj_th 0.05 --lfc_th 1 --cutoff 0.05
```

## 批量运行

`--deg_info` 为差异分析汇总表，脚本读取第一列作为比较组名，并按 `--pattern` 定位每组 DEG 表：

```bash
python3 run_kegg_batch.py \
  --deg_info All_Contrast_DEG_Statistics.csv \
  --deg_dir 06.DEG/DESEQ2 \
  --out_dir 07.Enrichments \
  --organism sly \
  --gene_col ENSEMBL \
  --id_map /path/to/ITAG4.1.kegg.id \
  --padj_th 0.05 --lfc_th 1 --cutoff 0.05
```

ATAC 数据使用 `--pattern '{contrast}_Differential_Peaks.csv'`。任一比较组失败时脚本以非零状态退出。

## 输出

每个比较组产生两个文件：

- `{name}_KEGG_UP.csv`
- `{name}_KEGG_DOWN.csv`

列包括 `ID`、`Description`、`GeneRatio`、`BgRatio`、`pvalue`、`p.adjust`、`qvalue`、`geneID`、`Count`，以及：

- `Input_Gene_Count`：通过 padj/LFC 筛选的源基因数
- `Background_Match_Count`：映射后命中的 KEGG 基因数
- `Universe_Gene_Count`：背景基因数

无差异基因或无显著通路时输出 `Count = 0` 的占位行；缺包、物种无通路、背景完全不匹配会报错退出。
