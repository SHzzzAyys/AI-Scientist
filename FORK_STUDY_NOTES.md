# Fork 研究笔记 — AI-Scientist

> 本文件是 fork 所有者（@SHzzzAyys）的研究记录，**非上游内容**。上游说明见 [README.md](./README.md)。

## 为什么 fork

学习它「全自动科研」的 agent 编排，与自己已有的一套研究工作流工具对比。

## 关键认知

全流程实跑需 Linux + NVIDIA GPU + texlive-full + LLM API（单篇 ~$15，跑 NanoGPT/diffusion 真实训练），CPU-only Windows 跑不动。所以**只读码、不实跑**，详细架构分析见 [ARCHITECTURE_NOTES.md](./ARCHITECTURE_NOTES.md)。

## 提炼的 5 阶段编排

`generate_ideas`（反思循环 + Semantic Scholar/OpenAlex 查重）→ `perform_experiments`（Aider 当 coding agent，MAX_RUNS=5×MAX_ITERS=4 预算）→ `perform_writeup`（8 节 LaTeX，禁幻觉引用）→ `perform_review`（NeurIPS 审稿表）→ `llm.py`（多 provider 抽象）。

## 最值得借鉴

- novelty 查重直接调 Semantic Scholar/OpenAlex API 自动判重。
- Aider + 重试预算 + stderr 截断喂回的「实验自愈循环」。
- 写论文阶段「数值必须来自实验、禁止幻觉引用」的 LaTeX 校验清单。

详见 ARCHITECTURE_NOTES.md（含与各阶段对应工具的逐项对比）。
