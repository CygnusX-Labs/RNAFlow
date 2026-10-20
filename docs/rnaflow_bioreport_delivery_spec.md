# RNAFlow → BioReport JSON 对接规范

规范版本：`2.0.0`

本文档定义 RNAFlow 向 BioReport 工作区交付 RNA-seq 项目结果时使用的 JSON 契约、路径规则、软件版本记录、富集结果状态和报告输出参数。

## 1. 交付目录

推荐的交付目录如下：

```text
report_data/
├── project_summary.json
└── data/
    ├── index/
    │   ├── sample.csv
    │   ├── contrasts.csv
    │   ├── merge_rsem_tpm.tsv
    │   ├── multiqc_qc_general_stats.txt
    │   └── multiqc_mapping_general_stats.txt
    ├── fastp_trim_report/
    ├── fastq_screen_report/
    ├── QualiMap/multiqc_data/
    └── res/
        ├── DEG/
        └── Enrichments/
```

JSON 顶层必须声明：

```json
{
  "schema_version": "2.0.0",
  "path_base": "."
}
```

`path_base` 固定为 `.`。`input_files`、富集结果中的 `table/full_table` 均相对于 JSON 文件所在目录解析。上游交付只使用包内相对路径，不写原机器绝对路径、URL、反斜杠或 `..`；移动整个交付目录后仍应可读取。

## 2. 顶层 JSON 结构

| 字段 | 要求 |
| --- | --- |
| `schema_version` | 必填，固定为 `2.0.0` |
| `path_base` | 必填，固定为 `.` |
| `project` | 必填，项目元信息 |
| `input_files` | 必填，输入文件和目录路径 |
| `software_versions` | 必填，至少一条真实软件版本记录 |
| `enrichment` | 必填，包含 `go` 和 `kegg` |
| `stats` | 可选，样本和分组统计 |
| `analysis` | 可选，报告统计和展示参数 |
| `report` | 可选，报告类型、布局和输出格式 |
| `ai` | 可选，AI 分析开关 |

新交付使用 `project`，不要使用旧的 `project_meta`。新交付不在 GO/KEGG 中写入 `terms`，完整分析数据放在 CSV/TSV 文件中。

## 3. 项目信息

```json
{
  "project": {
    "project_id": "X101SC26098749-Z01-J001",
    "client": "jzhang",
    "species": "Solanum lycopersicum",
    "genome_version": "ITAG4.1",
    "pipeline_version": "0.2.0",
    "analysis_date": "2026-10-20"
  }
}
```

`project_id` 必须为非空字符串，用于项目标识、日志、溯源和报告命名；不能用 `project_name` 替代。`analysis_date` 是分析日期，`report_date` 是可选的报告生成日期，二者含义不同。

## 4. 输入路径

完整 RNA-seq 报告推荐声明以下字段：

| 字段 | 类型/内容 |
| --- | --- |
| `data_dir` | 数据目录，推荐 `data` |
| `qc_file` | QC 汇总 TSV，包含 `Sample` 和实际 MultiQC 指标列 |
| `mapping_file` | 比对汇总 TSV，包含 `Sample` 和实际 MultiQC 指标列 |
| `tpm_file` | 第一列为基因 ID，其余列为样本 TPM |
| `sample_file` | CSV，推荐列为 `sample,sample_name,group`，样本标识唯一 |
| `contrasts_file` | CSV，必须包含 `Control,Treat` |
| `deg_dir` | 各比较组 DEG CSV 目录 |
| `fastp_stats_file` | fastp 汇总统计 TSV |
| `fastp_report_dir` | 包含 MultiQC `multiqc_data.json` 的目录 |
| `fastq_screen_r1_dir` | R1 FastQ Screen MultiQC 数据目录 |
| `fastq_screen_r2_dir` | R2 FastQ Screen MultiQC 数据目录 |
| `qualimap_dir` | QualiMap/STAR 等 MultiQC 数据目录 |

比较名由 `contrasts.csv` 的 `Treat` 和 `Control` 组成：
`Treat_vs_Control`。比较名必须与 DEG 和富集文件中的比较名一致。

## 5. 软件版本

软件版本直接写入 JSON：

```json
{
  "software_versions": [
    {"Software": "fastp", "Version": "1.0.1"},
    {"Software": "Samtools", "Version": "1.22.1"},
    {"Software": "FastQ Screen", "Version": "0.16.0"},
    {"Software": "MultiQC", "Version": "1.31"}
  ]
}
```

- `Software` 和 `Version` 必须为非空字符串，版本号必须加引号。
- 软件名不能重复，比较时不区分大小写。
- `Link` 可选，填写时应使用 HTTP/HTTPS 官网链接。
- 只填写本次运行中能够核验的真实版本，不得使用示例值补造版本。
- 推荐尽可能记录 STAR、RSEM、DESeq2、clusterProfiler 等实际使用的软件版本。

## 6. GO/KEGG 结果引用

JSON 只描述结果状态和文件位置，不嵌入富集条目：

```json
{
  "enrichment": {
    "go": {
      "enabled": true,
      "method": "clusterProfiler::enricher",
      "parameters": {
        "cutoff": 0.05,
        "padj_th": 0.05,
        "lfc_th": 1
      },
      "contrasts": {
        "Salt_A_vs_WTSalt": {
          "UP": {
            "status": "available",
            "table": "data/res/Enrichments/Salt_A_vs_WTSalt_GO_UP.csv"
          },
          "DOWN": {
            "status": "no_results",
            "term_count": 0,
            "messages": ["No significant GO enrichment"]
          }
        }
      }
    },
    "kegg": {
      "enabled": true,
      "method": "clusterProfiler::enrichKEGG",
      "parameters": {
        "cutoff": 0.05,
        "organism": "sly"
      },
      "contrasts": {
        "Salt_A_vs_WTSalt": {
          "UP": {
            "status": "available",
            "table": "data/res/Enrichments/Salt_A_vs_WTSalt_KEGG_UP_enrichments.csv",
            "full_table": "data/res/Enrichments/Salt_A_vs_WTSalt_KEGG_UP_enrichments_full.csv"
          },
          "DOWN": {
            "status": "unavailable",
            "messages": ["Result was not delivered"]
          }
        }
      }
    }
  }
}
```

每个启用的数据库必须列出全部交付比较组，每组必须包含 `UP` 和 `DOWN`。

### 字段要求

| 字段 | 要求 |
| --- | --- |
| `enabled` | 布尔值，是否执行该数据库分析 |
| `method` | 启用时必填，填写真实方法 |
| `parameters.cutoff` | 启用时必填，范围为 `0 < cutoff <= 1` |
| `parameters` | 可记录 `organism`、`padj_th`、`lfc_th` 等实际参数，不放大映射表 |
| `contrasts` | 启用时必填，键为比较名 |
| `status` | 每个方向必填 |
| `table` | `available` 时必填，指向报告使用的 CSV |
| `full_table` | 可选，指向未筛选完整 CSV，不自动作为绘图输入 |
| `term_count` | 可选；表示 `table` 的实际数据行数，不是 Top N 数量 |
| `messages` | 可选，说明空结果、未执行或失败原因 |

### 状态定义

| 状态 | 含义 |
| --- | --- |
| `available` | 已提供可用结果表 |
| `no_results` | 已执行，但按阈值没有显著结果 |
| `unavailable` | 该方向没有交付结果 |
| `disabled` | 本次分析未启用 |
| `failed` | 上游执行失败，需在 `messages` 中说明原因 |

`no_results` 不应把占位行当作真实条目。推荐不生成占位 `table`，但可以保留 `full_table`。如果为了兼容旧上游仍提供占位 CSV，BioReport 必须以 `status` 为准，不计入条目、不绘图。

## 7. 富集 CSV 契约

富集表使用 UTF-8 编码、英文逗号分隔，首行为列名，文本中的逗号或换行按标准 CSV 规则转义。

必需列：

| 列 | 要求 |
| --- | --- |
| `Description` | 功能条目或通路名称 |
| `GeneRatio` | `2/100` 等分数字符串，分母必须大于 0；也支持有限数值 |
| `Count` | 非负整数，表示实际命中基因数 |
| `p.adjust` | 数值，范围为 `0–1` |

推荐保留 `ID`、`BgRatio`、`pvalue`、`qvalue`、`geneID`、`RichFactor`、`FoldEnrichment`、`zScore` 等原始列。GO 的 `ONTOLOGY` 和 KEGG 的 `category/subcategory` 如果存在也可以保留，不要通过列名猜测缺失分类。

## 8. 报告参数

```json
{
  "analysis": {
    "enrichment": {"top_n": 12},
    "deg": {"log2fc_threshold": 1, "pvalue_threshold": 0.05}
  },
  "report": {
    "type": "rna-seq",
    "layout": "single",
    "output_format": ["pdf", "html"]
  },
  "ai": {"enabled": false}
}
```

当前 RNAFlow 默认同时输出 PDF 和 HTML，即：
`report.output_format: ["pdf", "html"]`。

富集筛选 cutoff 优先级为：

1. `analysis.enrichment.p_cutoff`；
2. 对应数据库的 `parameters.cutoff`；
3. 旧格式默认值 `0.1`。

报告按 `p.adjust < cutoff` 筛选，并按显著性稳定升序选择 Top N。`parameters.padj_th` 只记录富集输入基因筛选阈值，不改变 DEG 火山图使用的 `pvalue` 和 `|log2FoldChange|` 口径。

## 9. 校验与运行

RNAFlow 使用仓库内的 `schema/project_summary.schema.json` 对生成 JSON 进行 Draft 2020-12 校验：

```sh
python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

schema = json.loads(Path('schema/project_summary.schema.json').read_text())
data = json.loads(Path('report_data/project_summary.json').read_text())
Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
print('JSON contract valid')
PY
```

BioReport 还应检查：

- 所选报告模块需要的输入文件是否存在；
- `table/full_table` 声明的文件是否存在；
- 富集 CSV 是否包含必需列且数值合法；
- `term_count` 是否与源表实际数据行数一致；
- 样本集合、比较组完整性和参考版本等语义是否正确。

## 10. 外部消费者要求

外部报告仓库应：

1. 先校验 `schema_version` 和 JSON Schema；
2. 分别遍历 `enrichment.go.contrasts` 与 `enrichment.kegg.contrasts`；
3. 对每个比较组读取 `UP`/`DOWN`，先判断 `status`；
4. 仅对 `available` 状态读取 `table`，并相对于 JSON 所在目录解析路径；
5. 对 `no_results`、`unavailable`、`disabled`、`failed` 显示对应状态，不把占位行当作真实结果。

