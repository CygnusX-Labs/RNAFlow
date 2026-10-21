# RNAFlow 开发计划 (Roadmap)

[English Version](ROADMAP.md) | [返回 README](README_zh.md)

以下内容仍为后续开发计划，不代表 v0.2.0 已实现的功能。

## 计划中的分析扩展 (Planned Analysis Extensions)
- **动态网页报告生成**:
    - 实现不同分析流程与模块最终网页报告的动态生成。
    - **实现逻辑**：
        1. **模块状态感知**：在 `project_summary.json` 中记录 `DEG`、`rMATS`、`Variant` 等模块的开启状态。
        2. **动态导航构建**：在 Quarto 渲染前，通过 Python 脚本根据模块状态动态生成 `_quarto.yml`，自动隐藏未运行分析的标签页。
        3. **条件内容渲染**：在 `.qmd` 模板中使用 Python 逻辑判断，实现结果章节的动态加载与展示。

- **WGCNA (加权基因共表达网络分析)**:
    - 实现基因模块聚类与表型关联分析，识别核心 Hub Gene。
    - 导出网络文件，支持 Cytoscape 可视化。
- **GSVA (基因集变异分析)**:
    - 为每个样本计算通路活性分数，实现通路的差异化分析与可视化（热图/相关性）。
- **TF 调控网络预测 (Transcription Factor)**:
    - 针对植物（莴苣等）集成 **PlantRegMap / PlantTFDB**，预测差异基因的上游转录因子调控逻辑。
- **细胞组分去卷积 (Deconvolution)**:
    - 引入 CIBERSORTx/MuSiC 算法，利用单细胞参考集解析组织样本中的细胞类型比例。

## 计划中的 LncRNA 与云端参考扩展 (Planned LncRNA and Cloud Reference Extensions)
- **LncRNA 预测与分析**:
    - 集成 CPAT/CPC2/LncFinder，鉴定新 LncRNA 并构建 LncRNA-mRNA 共表达网络。
- **云原生参考基因组管理 (Cloud-Native Reference Management)**:
    - 采用 **BYOC (Bring Your Own Cloud)** 策略，赋能用户构建属于自己的生物数据中心，实现"无状态迁移" (Stateless Portability)。
    - **Reference Factory**: 提供独立的 Snakemake 构建流程，支持自动同步至 S3/OSS/MinIO。

## 高级差异分析模块 (Advanced Experimental Design)
- 为了支持更复杂的生物学实验设计（如时间序列分析、双因素交互作用），计划重构 DEG 模块，支持自定义设计公式 (`design_formula`)。

## AI 引擎增强 (AI Engine Enhancement)
进一步提升 AI 在生物信息学分析中的应用能力：

1. **多模态分析**：结合基因表达、变异、剪接等多种数据类型，提供综合性的生物学解释。
2. **实时学习**：引入在线学习机制，使 AI 模型能够根据最新文献不断更新知识库。
3. **个性化解读**：根据用户的专业背景和研究兴趣，定制化生成分析报告内容。
