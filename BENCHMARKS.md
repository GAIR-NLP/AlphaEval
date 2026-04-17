# Benchmark Comparison (Living Document)

This is a living comparison of AlphaEval with existing agent and LLM benchmarks across seven dimensions that characterize production-level evaluation. The paper version is frozen; this file is meant to keep growing.

**Want your benchmark listed?** Open a PR editing this file. We'll periodically sync additions into future paper revisions.

## Dimensions

| Flag | Meaning |
|:--|:--|
| **Production** | Tasks sourced from real commercial deployments with paying customers |
| **Multi-Modal** | Requires processing multi-modal heterogeneous inputs (PDFs, spreadsheets, images) |
| **Underspec.** | Tasks deliberately preserve production-level requirement ambiguity |
| **Diverse Eval** | Employs three or more distinct evaluation paradigms |
| **Expert Val.** | Evaluation criteria co-developed and validated with domain experts |
| **Dynamic** | Benchmark designed for continuous evolution rather than static one-time release |
| **Cross-Domain** | Spans three or more distinct professional domains |

**Eval Type legend:** `Rule` = rule-based / exact match / code execution · `Model` = LLM-as-Judge · `Human` = human evaluation · `R+M+H` / `Rule+Model` = combinations.

## How to add your benchmark

1. Pick the section that best matches your benchmark's primary domain (or add a new one if none fit).
2. Add one row in alphabetical order within the section, following the existing format.
3. Include a citation link (arXiv / paper URL / project page).
4. For each dimension, use ✓ or ✗ — err on the strict side; reviewers may push back.
5. Open a PR with a brief description and a link to your paper.

---

## Software Engineering & Coding

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [SWE-bench](https://arxiv.org/abs/2310.06770) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [SWE-bench Multimodal](https://arxiv.org/abs/2410.03859) | Code | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [Multi-SWE-bench](https://arxiv.org/abs/2504.02605) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [SWE-Lancer](https://arxiv.org/abs/2502.12115) | Code | Rule | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [SWT-Bench](https://arxiv.org/abs/2406.12952) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [Terminal-bench](https://www.tbench.ai/) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [FeatBench](https://arxiv.org/abs/2509.23045) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [DevBench](https://arxiv.org/abs/2403.08604) | Code | R+M+H | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| [LongCLI-Bench](https://arxiv.org/abs/2601.08394) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [ProjDevBench](https://arxiv.org/abs/2601.09126) | Code | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Data Science & ML Engineering

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [DSBench](https://arxiv.org/abs/2409.07703) | Code | Model | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [MLE-bench](https://arxiv.org/abs/2410.07095) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [KernelBench](https://arxiv.org/abs/2502.10517) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [DAComp](https://arxiv.org/abs/2506.20807) | Code+Research | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Code Competition & Security

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [LiveCodeBench](https://arxiv.org/abs/2403.07974) | Code | Rule | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |
| [CodeElo](https://arxiv.org/abs/2501.01257) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [Aider Polyglot](https://aider.chat/docs/leaderboards/) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [CyBench](https://arxiv.org/abs/2408.08926) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [BountyBench](https://arxiv.org/abs/2505.15216) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [VimGolf-Gym](https://arxiv.org/abs/2509.01595) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [DPAI Arena](https://arxiv.org/abs/2509.14444) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [Spring AI Bench](https://arxiv.org/abs/2510.01234) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [AGENTS.md Eval](https://arxiv.org/abs/2601.05678) | Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Tool Use & Web Interaction

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [WebArena](https://arxiv.org/abs/2307.13854) | Web | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [AgentBench](https://arxiv.org/abs/2308.03688) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [AgentBoard](https://arxiv.org/abs/2401.13178) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [τ-bench](https://arxiv.org/abs/2406.12045) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [τ²-Bench](https://arxiv.org/abs/2506.07982) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [TheAgentCompany](https://arxiv.org/abs/2412.14161) | Tool | Rule+Model | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [Tool Decathlon](https://arxiv.org/abs/2509.20612) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [ACEBench](https://arxiv.org/abs/2501.12851) | Tool | Rule+Model | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| [MCP-Universe](https://arxiv.org/abs/2508.14704) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| [Context-Bench](https://arxiv.org/abs/2509.04593) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [Letta Evals](https://www.letta.com/) | Tool | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [EcomBench](https://arxiv.org/abs/2510.02145) | Tool | Model | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| [DeliveryBench](https://arxiv.org/abs/2510.11234) | Tool | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [WorFBench](https://arxiv.org/abs/2410.07869) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [BrowseComp](https://openai.com/index/browsecomp/) | Search | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [AgencyBench](https://arxiv.org/abs/2602.01234) | Code+Tool | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ |
| [HammerBench](https://arxiv.org/abs/2412.17587) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Operating System & GUI

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [GAIA](https://arxiv.org/abs/2311.12983) | OS | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [OSWorld](https://arxiv.org/abs/2404.07972) | OS | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [AppWorld](https://arxiv.org/abs/2407.18901) | OS | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [WebSuite](https://arxiv.org/abs/2406.01637) | OS | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [OSUniverse](https://arxiv.org/abs/2505.03570) | OS | R+M+H | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| [OdysseyBench](https://arxiv.org/abs/2510.08912) | OS | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [OfficeQA](https://arxiv.org/abs/2510.12876) | OS | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Scientific Research

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [EXP-Bench](https://arxiv.org/abs/2505.24785) | Research | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [PaperBench](https://arxiv.org/abs/2504.01848) | Research | Model | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| [CORE-Bench](https://arxiv.org/abs/2409.11363) | Research | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [Auto-Bench](https://arxiv.org/abs/2506.00115) | Research | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [ResearchCodeBench](https://arxiv.org/abs/2506.02314) | Research | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [AstaBench](https://arxiv.org/abs/2510.03437) | Research | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [AInsteinBench](https://arxiv.org/abs/2510.04124) | Code+Research | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [ResearchGym](https://arxiv.org/abs/2602.07890) | Research+Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Mathematics & Knowledge

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [MMLU](https://arxiv.org/abs/2009.03300) | Knowledge | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [GPQA Diamond](https://arxiv.org/abs/2311.12022) | Knowledge | Rule | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ |
| [MMMU](https://arxiv.org/abs/2311.16502) | Knowledge | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [MathVista](https://arxiv.org/abs/2310.02255) | Math | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [FrontierMath](https://arxiv.org/abs/2411.04872) | Math | Rule | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| [AIME](https://artofproblemsolving.com/wiki/index.php/AIME_Problems_and_Solutions) | Math | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [HMMT](https://www.hmmt.org/) | Math | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| [USAMO](https://artofproblemsolving.com/wiki/index.php/USAMO) | Math | Human | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| [MMMLU](https://huggingface.co/datasets/openai/MMMLU) | Knowledge | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [Video-MME](https://arxiv.org/abs/2405.21075) | Knowledge | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [OpenAI-MRCR](https://openai.com/index/introducing-gpt-4-5/) | Knowledge | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [HLE](https://arxiv.org/abs/2501.14249) | Knowledge | Rule | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| [ARC-AGI-2](https://arcprize.org/) | Reasoning | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [OODBench](https://arxiv.org/abs/2602.03141) | Knowledge | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

## Agent Product Evaluation

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [xbench](https://xbench.org/) | Recruit+Mkt | Model | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| [AgentIF-OneDay](https://arxiv.org/abs/2601.11203) | Daily Tasks | Model | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |

## Emerging Benchmarks (2026)

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| [Persona2Web](https://arxiv.org/abs/2602.00123) | Search | Model | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [AmbiBench](https://arxiv.org/abs/2602.00456) | OS | Model | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [PAHF](https://arxiv.org/abs/2602.00789) | Tool | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [AgenticShop](https://arxiv.org/abs/2602.01012) | Search | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [GAP Benchmark](https://arxiv.org/abs/2602.01345) | Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [AgentLAB](https://arxiv.org/abs/2602.01678) | Safety | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [STING](https://arxiv.org/abs/2602.01901) | Safety | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [GT-HarmBench](https://arxiv.org/abs/2602.02234) | Safety | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [ForesightSafety](https://arxiv.org/abs/2602.02567) | Safety | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [APST](https://arxiv.org/abs/2602.02890) | Safety | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [MemoryArena](https://arxiv.org/abs/2602.03123) | Search+Research | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [WebWorld-Bench](https://arxiv.org/abs/2602.03456) | Search+Code | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [Gaia2](https://arxiv.org/abs/2602.03789) | OS+Search | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [SkillsBench](https://arxiv.org/abs/2602.04012) | Code+Tool | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [MATEO](https://arxiv.org/abs/2602.04345) | Reasoning | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [SciAgentGym](https://arxiv.org/abs/2602.04678) | Research+Tool | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| [Drug Scouting](https://arxiv.org/abs/2602.04901) | Search+Research | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [AD-Bench](https://arxiv.org/abs/2602.05234) | Tool | Rule | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| [GUI-GENESIS](https://arxiv.org/abs/2602.05567) | OS | Rule | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [BookingArena](https://arxiv.org/abs/2602.05890) | Search | Rule+Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [BrowseComp-V³](https://arxiv.org/abs/2602.06123) | Search | Rule | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ |
| [Collective Behavior](https://arxiv.org/abs/2602.06456) | Research | Rule | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [Unsafer](https://arxiv.org/abs/2602.06789) | Tool | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| [Proxy State Eval](https://arxiv.org/abs/2602.07012) | Tool | Model | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

---

## AlphaEval (Ours)

| Benchmark | Domain | Eval Type | Production | Multi-Modal | Underspec. | Diverse Eval | Expert Val. | Dynamic | Cross-Domain |
|:--|:--|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **[AlphaEval](https://arxiv.org/abs/2604.12162)** | **6 Domains** | **Rule+Model** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

*Note: citation links reflect the best-known public URL at the time of listing. Some arXiv IDs in the "Emerging Benchmarks (2026)" section are placeholders from the paper's bibliography — contributors are encouraged to replace them with verified links via PR.*
