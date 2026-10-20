# 离线 KEGG 富集

KEGG 接在现有 GO 批量比较组流程中，分别分析 UP、DOWN。
R 使用 `clusterProfiler::enrichKEGG(..., keyType="kegg", use_internal_data=TRUE)`，不回退到在线数据库。

## 环境

在运行富集规则的 R 环境中安装自己的 KEGG.db 离线包：

```r
install.packages("/path/to/KEGG.db_1.0.tar.gz", repos=NULL, type="source")
library(KEGG.db)
library(clusterProfiler)
```

现有 `envs/go_enrich_r.yaml` 没有包含 KEGG.db，需要在实际运行的环境安装，不能只安装到其他 R 环境。
内部库的物种覆盖和注释新旧由提供的 KEGG.db 决定。缺包、物种无通路、背景基因完全不匹配会报错。

## 启用番茄

编辑 `config/reference.yaml` 对应基因组配置（已提供默认关闭的示例）：

```yaml
deg_enrich_wrapper:
  ITAG4.1:
    gene_col: ENSEMBL  # 原有 GO 配置
    kegg:
      enabled: true
      organism: sly
      gene_col: ENSEMBL
      id_map: ITAG4.1/ITAG4.1.kegg.id
```

`id_map` 相对 `reference_path` 解析，也可以填写绝对路径。文件无表头，两列 TAB 分隔：

```text
Solyc00g160260.1.1	101261876
Solyc00g160270.1.1	101247603
```

第一列与 DEG 的 `gene_col` 精确匹配，不自动删除版本号；第二列是该物种 KEGG 基因 ID，接受带 `sly:` 前缀。
如果 DEG 基因列本来就是 KEGG 基因 ID，可以省略 `id_map`。
不使用在线 ID 转换，因此第二列需事先确认与内部数据库一致。

## 单独测试

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

完整流程按原来的 RNAFlow 命令运行即可。DEG 阈值来自 `parameter.DEG.PVAL/LFC`，富集阈值来自 `parameter.Enrichments.cutoff`（默认 0.05）。
背景是 DEG 全表中 padj 非 NA、LFC 有限的基因，映射后与 KEGG 注释取交集；映射为同一目标 ID 的基因只计算一次。

## 输出

- GO 保留原来的 `{contrast}_UP.csv`、`{contrast}_DOWN.csv`。
- KEGG 输出 `07.Enrichments/{contrast}_KEGG_UP.csv`、`{contrast}_KEGG_DOWN.csv`。
- `geneID` 为 KEGG 基因 ID；Input_Gene_Count 为筛选后的源基因数，Background_Match_Count 为注释匹配后的目标基因数，Universe_Gene_Count 为背景目标基因数。
- 无差异基因或无显著通路输出 Count=0 的占位行；运行错误以非零状态退出。
- 两份报告模板均读取 KEGG 的 UP/DOWN 表，沿用现有气泡图。

本地已检查脚本/规则/报告语法、wrapper 调度、阈值传递和失败传播；当前环境缺少 KEGG.db，尚未验证真实数据库富集及完整报告渲染。
