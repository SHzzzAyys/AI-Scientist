# AI-Scientist 架构笔记（读码 + 与本地 .claude skills 对比）

复刻 SakanaAI/AI-Scientist（8.4k★）的只读研究产出。**没实跑**（全流程需 GPU + LaTeX + API，
单篇 ~$15，本机 CPU-only 跑不动 NanoGPT 实验）。本笔记提炼其 agent 编排，并对比用户已有的研究技能。

## 一、5 阶段流水线（`launch_scientist.py::do_idea`）

```
template → [1]idea生成 → [2]novelty查重 → [3]实验迭代 → [4]写论文 → [5]自动review →（可选）改进 → paper.pdf
```

核心模块（`ai_scientist/`，本地 clone 已验证一致）：
| 模块 | 职责 | 关键机制 |
|------|------|----------|
| `generate_ideas.py` | idea 生成 + 学术查重 | 反思循环（≤5 轮，可"I am done"提前退出）；生成 ≤50 idea，自评 Interestingness/Feasibility/Novelty；`check_idea_novelty` 用 **Semantic Scholar / OpenAlex API** 多轮搜索查重（≤10 轮），标 `idea['novel']`。**无 ELO** |
| `perform_experiments.py` | idea→可跑代码 | **Aider** 当 coding agent；`MAX_RUNS=5` × `MAX_ITERS=4` 重试预算；`python experiment.py --out_dir=run_i`，2h 超时；失败把 stderr 末 1500 字喂回 Aider |
| `perform_writeup.py` | 结果→LaTeX→PDF | 8 节分写（Abstract…Related Work）；引用走 SemanticScholar 二阶段搜索+校验（禁止幻觉引用）；`pdflatex×3 + bibtex`；chktex ≤5 轮修 LaTeX bug |
| `perform_review.py` | LLM 自动审稿 | **NeurIPS 审稿表**（Originality/Quality/Clarity/Significance 1-4，Overall 1-10，Decision Accept/Reject）；可集成多审稿人（temp 0.75）取 meta；neg/pos system prompt 控宽严 |
| `llm.py` | provider 抽象 | `create_client()` 路由 Claude/GPT/DeepSeek/Gemini/OpenRouter；统一 `get_response_from_llm()` |

## 二、与本地 .claude/skills 的对应（关键发现：几乎一一映射，且本地更细）

| AI-Scientist 阶段 | 对应本地 skill | 本地更强之处 |
|-------------------|----------------|--------------|
| idea 生成 + 自评 | `research-ideation` | 本地有 **3 persona（innovator/pragmatist/critic）+ ELO 锦标赛排序**；AI-Scientist 只有单链反思、无 ELO |
| novelty 查重 | `paper-navigator` | 两者都查文献；AI-Scientist 直接 API 自动判 novel |
| 实验迭代 + 重试预算 | `experiment-pipeline`（4 阶段+预算+gate）+ `experiment-craft`（5 步诊断） | 本地把"实验"拆成 baseline→调参→验证→消融四阶段，比 AI-Scientist 的"5run×4retry"更结构化 |
| 写论文 8 节 | `paper-writing` + `paper-planning` + `latex-paper-en` | 本地 planning 有 mock rejection letter、ablation-first 等反直觉战术 |
| 自动 review | `paper-review`（reject-first 对抗自审） | 本地是"自审己稿"，AI-Scientist 是"审 AI 产出"，思路同源 |
| 跨周期记忆 | `evo-memory`（M_I/M_E + IDE/IVE/ESE） | **AI-Scientist 无持久记忆**；本地能跨 idea/实验循环积累"什么可行/什么失败" |

## 三、最值得借鉴 / 已被本地覆盖

- **可借鉴**：① novelty 查重直接调 Semantic Scholar/OpenAlex API 自动判重的工程化做法；② Aider + `MAX_RUNS×MAX_ITERS` 预算 + stderr 截断喂回的实验自愈循环；③ 写论文阶段"禁止幻觉引用/数值必须来自实验"的 LaTeX 校验清单。
- **本地已更优**：persona 多轨 + ELO 排序、四阶段实验、evo-memory 持久记忆——这些 AI-Scientist 都没有。

## 四、跑起来的硬性门槛（为何没实跑）
Linux（官方强制）+ NVIDIA GPU + CUDA + PyTorch + texlive-full；至少一个 LLM key；Semantic Scholar key（可选）。Claude 3.5 单篇 < $15。CPU-only Windows 上 NanoGPT/diffusion 实验不可行。
