<p align="center">
  <img src="assets/logo.png" width="120" alt="AlphaEval Logo">
  <h1 align="center">AlphaEval：在生产环境中评估 AI 智能体</h1>
  <p align="center">
    <a href="https://alphaeval.ai"><img src="assets/logo.png" height="16">&nbsp;<b>官网</b></a> &nbsp;|&nbsp;
    <a href="paper/AlphaEval_v0.pdf">📄&nbsp;<b>论文</b></a> &nbsp;|&nbsp;
    <a href="https://github.com/GAIR-NLP/AlphaEval"><img src="https://github.githubassets.com/favicons/favicon.svg" height="16">&nbsp;<b>GitHub</b></a> &nbsp;|&nbsp;
    <a href="README.md">🌐&nbsp;<b>English</b></a>
  </p>
</p>

<p align="center">
  面向生产环境的 AI 智能体评测框架<br>
  来自 <b>7 家公司</b>的 <b>94 个真实任务</b>，横跨 <b>6 个 <a href="https://www.onetonline.org/find/descriptor/browse/2.A">O*NET</a> 职业领域</b>
</p>

---

<p align="center">
  <img src="assets/overview.png" width="85%" alt="AlphaEval 概览">
  <br><em>AlphaEval 概览：弥合研究基准测试与生产现实之间的鸿沟</em>
</p>

## 亮点

- **从需求到 Benchmark** — 将真实生产需求系统化地转化为全自动、可复现的评测任务。任何业务需求都能快速转化为严格的 benchmark。
- **基于生产环境的任务** — 94 个保留了真实世界复杂性的任务：模糊的需求规格、多模态输入（PDF、Excel、代码、图片）、隐式约束、以及领域专家的评判标准。
- **多范式组合评估** — 多种评估范式（参考答案验证、形式逻辑验证、Rubric 评估、执行验证）按任务组合（平均每任务 2.8 种），配合 Docker 沙箱执行和 LLM-as-Judge 跨范式语义评估。
- **评估完整智能体产品** — 评估的是 Claude Code、Codex、GitHub Copilot、Cursor 等完整产品，而非单独的模型。脚手架（scaffold）的选择与模型本身同等重要。

<p align="center">
  <img src="assets/pipeline.png" width="90%" alt="需求到Benchmark构建框架">
  <br><em>需求到 Benchmark 的构建框架：合作伙伴对接 → 需求获取 → 任务形式化 → 迭代评估</em>
</p>

## 核心结果

最佳配置（Claude Code + Opus 4.6）平均分仅 **64.41/100**，揭示了研究与生产之间的巨大差距。

| 智能体产品 | 模型 | 平均分 |
|:--|:--|--:|
| Claude Code | Claude Opus 4.6 | **64.41** |
| Cursor | Claude Opus 4.6 | 61.85 |
| GitHub Copilot | Claude Opus 4.6 | 61.31 |
| GitHub Copilot | GPT-5.2 | 54.91 |
| Codex | Claude Opus 4.6 | 53.45 |

**核心发现：**
- **脚手架与模型同等重要**：同一个 Opus 4.6 模型，通过 Claude Code 得 64.41，通过 Codex 仅得 53.45 —— 相差 11 分
- **领域差异极端**：技术研究（平均 62.0）vs 人力资源（平均 30.0）
- **单一分数无法衡量生产就绪度**：域间排名相关性在统计上往往不显著
- **六种生产特有失败模式**：级联依赖失败、主观判断崩溃、信息检索失败、跨章节逻辑不一致、约束规格误读、格式合规失败 —— 在编程类 benchmark 中完全不可见

## 任务领域

任务按 [O*NET](https://www.onetonline.org/find/descriptor/browse/2.A) 职业分类体系归类：

| 领域 | 任务数 | 说明 |
|:--|--:|:--|
| 人力资源 | 11 | 简历筛选与岗位匹配 |
| 金融与投资 | 22 | 投资研究、路演辅导、金融数据提取 |
| 采购与运营 | 23 | BOM 成本优化、采购数据分析 |
| 软件工程 | 11 | 全栈小程序开发 |
| 医疗与生命科学 | 16 | 临床试验 eCRF 管理、医保政策分析 |
| 技术研究 | 11 | AI 行业深度调研、技术分析 |

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/GAIR-NLP/AlphaEval.git
cd AlphaEval

# 配置
cp config/config.example.yaml config.yaml
# 编辑 config.yaml 填入 API key

# 安装依赖
pip install openai pyyaml

# 运行评测
./run_eval.sh claude-code <task_id>
```

## 评估模板

提供 6 种开箱即用的评估模板，复制后即可定制：

```bash
cp -r tasks/.templates/llm_judge tasks/my-new-task
# 编辑 task.yaml, query.md 和 .eval/rubric.json
```

| 模板 | 适用场景 | 评估方式 |
|:--|:--|:--|
| `code_exec` | 可验证的数值/结构化输出 | 提取答案 → 对比期望值 |
| `llm_judge` | 主观质量评估 | LLM 逐条判断 rubric 覆盖 |
| `exact_match` | 单一正确答案 | 字符串或数值匹配 |
| `f1_match` | 从集合中选择条目 | Precision / Recall / F1 |
| `hybrid` | 数值准确性 + 定性质量 | 数值验证 + LLM-as-Judge |
| `ui_testing` | 智能体构建 Web/移动应用 | Playwright 无头浏览器 + 截图 |

<p align="center">
  <img src="assets/eval_taxonomy.png" width="85%" alt="评估分类体系">
  <br><em>AI 智能体评估方法论分类。AlphaEval 覆盖多种评估范式，按任务组合使用。</em>
</p>

详见 [任务创建指南](tasks/TASK_CREATION_GUIDE.md) 和 [示例任务](examples/)。

## 任务结构

```
tasks/<task-name>/
├── task.yaml              # 元数据：名称、类别、难度、评估配置
├── query.md               # 给智能体的任务提示
├── files/                 # 输入文件（PDF、Excel、图片、代码等）
└── .eval/
    ├── rubric.py          # 评估脚本
    ├── rubric.json        # Rubric 评分点（llm_judge / hybrid）
    └── ground_truth.json  # 标准答案（f1_match / code_exec）
```

## 支持的智能体

| 智能体 | 类型 | 说明 |
|:--|:--|:--|
| Claude Code | CLI | Anthropic 的智能编程工具 |
| Codex | CLI | OpenAI 的编程智能体 |
| GitHub Copilot | CLI | GitHub 的编程智能体 |
| Cursor | CLI | Cursor 的 AI 编程智能体 |

所有智能体均通过 CLI 在 Docker 沙箱环境中调用，完整记录输出轨迹。

## 论文

📄 **[AlphaEval: Evaluating Agents in Production (v0)](paper/AlphaEval_v0.pdf)**

> 这是论文的早期版本，将持续修订完善。arXiv 版本即将发布。

## 引用

```bibtex
@article{alphaeval2026,
  title={AlphaEval: Evaluating Agents in Production},
  author={Anonymous},
  year={2026}
}
```

## 致谢

感谢 Keyu Li 和 Tianze Xu 对本项目的贡献。

## 联系方式

如有问题或合作意向，请联系：**lupengrui@sjtu.edu.cn**

## 许可证

MIT License — 详见 [LICENSE](LICENSE)。
