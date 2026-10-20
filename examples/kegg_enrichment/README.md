# KEGG 富集运行示例

本目录只保留批量运行入口，不再维护 R 脚本副本。统一调用仓库中的 `src/src/Enrichments/kegg_enricher.r`，无需启动 Snakemake。

## 文件

| 文件 | 作用 |
| --- | --- |
| `run_kegg_batch.py` | 批量调度，遍历 DEG 统计表中的所有比较组并调用 R 脚本 |

共用脚本与主流程入口：

- `src/src/Enrichments/kegg_enricher.r`
- `src/src/Enrichments/deg_enrich_wrapper.py`（KEGG 调度部分）
- `rules/10.DEG_Enrichments.smk`（`Enrichments` 规则）

## 依赖

请使用主脚本所需的 R 环境，依赖说明见 `src/src/Enrichments/README.md`。当前脚本调用 `clusterProfiler::enrichKEGG()`，通路查询依赖网络/缓存状态，并非固定使用离线 KEGG.db。

## 输入

DEG 表（CSV 或 TAB 分隔，分隔符自动识别）必须包含：

- `--gene_col` 指定的基因 ID 列（默认 `ENSEMBL`）
- `padj`
- `log2FoldChange`

`--id_map` 为无表头两列 TSV，第一列为输入基因 ID，第二列是 KEGG 基因 ID（允许带 `sly:` 前缀）。主脚本会清理物种前缀和末尾版本号：

```text
Solyc00g160260.1.1	101261876
Solyc00g160270.1.1	101247603
```

如果 DEG 基因列本身就是 KEGG 基因 ID，可省略 `--id_map`。

## 单比较组运行

以下命令均从 RNAFlow 仓库根目录运行：

```bash
Rscript src/src/Enrichments/kegg_enricher.r \
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
python3 examples/kegg_enrichment/run_kegg_batch.py \
  --deg_info All_Contrast_DEG_Statistics.csv \
  --deg_dir 06.DEG/DESEQ2 \
  --out_dir 07.Enrichments \
  --organism sly \
  --gene_col ENSEMBL \
  --id_map /path/to/ITAG4.1.kegg.id \
  --padj_th 0.05 --lfc_th 1 --cutoff 0.05
```

ATAC 数据使用 `--pattern '{contrast}_Differential_Peaks.csv'`。任一比较组失败时脚本以非零状态退出。

批量入口根据自身位置定位主 R 脚本，不依赖当前工作目录；也可使用 `--kegg_rscript` 显式指定脚本路径。

## 输出

每个比较组按 UP/DOWN 分别输出：

- `{name}_KEGG_UP_enrichments.csv`、`{name}_KEGG_DOWN_enrichments.csv`：按 `p.adjust < --cutoff` 筛选后的主结果。
- `{name}_KEGG_UP_enrichments_full.csv`、`{name}_KEGG_DOWN_enrichments_full.csv`：完整测试结果，有可测试结果时生成。

列包括 `ID`、`Description`、`GeneRatio`、`BgRatio`、`pvalue`、`p.adjust`、`qvalue`、`geneID`、`Count`，以及：

- `Input_Gene_Count`：通过 padj/LFC 筛选的源基因数
- `Background_Match_Count`：映射后命中的 KEGG 基因数

输出细节以共用 R 脚本为准，不再沿用已移除副本的文件命名和离线分析约定。
