# AI agents listening primer: claim and source log

- Date: 2026-10-02, America/Los_Angeles.
- Researcher: Codex.
- Related episode: next OOOD episode on agents; E003 is the working repository sequence after 000-002. Publication title/order beyond this selection remain unapproved.
- Deliverable: `01_EPISODES/E003-ai-agents/codex-ai-agents-listening-primer-2026-10-02.txt`.
- Status: checked source background and draft narration for preparation. No recording, experiment result, host approval, or publication is asserted.

## Scope and interpretation

The question is how language-model agents work and how to assess useful delegation. The narrator supplies an accessible working definition rather than claiming a universal one. Event, venue, calendar, and assistant examples are original hypothetical illustrations. Organizational recommendations and future implications are explicitly interpretations, not findings from controlled trials. Product examples are historical announcements; no current plan access, pricing, or feature parity is claimed.

Every source below was accessed on **2026-10-02**. Dates refer to publication/first submission unless specified. Where a live document does not state a publication date, that absence is recorded. Research abstracts establish only the mechanisms described; numerical benchmark findings not used in the narration were deliberately excluded.

## Claim log

| ID | Exact proposition supported in narration | Source / publisher | Published | Limits |
|---|---|---|---|---|
| S01 | Agent definitions vary; a useful distinction is predefined workflow paths versus model-directed processes and tool use. | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Anthropic | 2024-12-19 | Vendor engineering guidance, not a standard or comparative trial. Page flags changed tooling. Used for conceptual distinction, not current product map. |
| S02 | A model, tools and instructions are agent components; tools can retrieve data or perform actions. | [A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf), OpenAI | Date not stated in PDF | Vendor guidance. Used as conceptual support, not evidence of reliability or a recommendation to build every workflow as an agent. |
| S03 | Agentic systems can plan, act, observe results, adjust and request human input; authority and security need system-level treatment. | [Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents), Anthropic | 2026-04-09 | Vendor description of its design. No guarantee of complete protection or universal effectiveness. |
| S04 | Intelligent agents and reinforcement learning are established AI topics predating current language-model products. | [Artificial Intelligence: A Modern Approach, contents](https://aima.cs.berkeley.edu/contents.html), Russell and Norvig / official textbook site | Edition/site date not stated on accessed page | Table of contents establishes longstanding topic organization; detailed modern product claims do not follow. |
| S05 | Reinforcement-learning agents use interaction and reward feedback to improve action selection. | [5.1 Reinforcement Learning](https://inst.eecs.berkeley.edu/~cs188/textbook/rl/rl.html), UC Berkeley CS188 course text | Page date not stated | Educational foundation. Does not establish that office agents update weights during use. |
| S06 | ReAct interleaves reasoning traces and task-specific actions, incorporating observations into subsequent decisions. | [ReAct](https://arxiv.org/abs/2210.03629), Yao et al. / author paper on arXiv | 2022-10-06; revision 2023-03-10 | Historical experimental approach; not proof of universal autonomy. No performance percentages used. |
| S07 | Toolformer trained a language model to decide which APIs to call, when, with which inputs, and how to incorporate results. | [Toolformer](https://arxiv.org/abs/2302.04761), Schick et al. / arXiv | 2023-02-09 | Historical research mechanism, not claim that current agents all use this training procedure. |
| S08 | Long-running agents need infrastructure to preserve progress across sessions; model and harness both influence results. | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), Anthropic | 2025-11-26 | Vendor engineering experience, especially application development; no universal success guarantee. |
| S09 | Tool definitions, clear boundaries and focused useful responses affect an agent's effectiveness. | [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents), Anthropic | 2025-09-11 | Vendor experience. Original venue/toolbox examples are illustrative. |
| S10 | Context is finite and can require selective retrieval, compaction and curation. | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Anthropic | 2025-09-29 | Engineering practices, not proof that any particular brief prevents omissions. |
| S11 | A larger context does not by itself ensure robust use of every included detail. | [Lost in the Middle](https://arxiv.org/abs/2307.03172), Liu et al. / arXiv | 2023-07-06; revision 2023-11-20 | Historical models and tested retrieval/QA tasks. Narration does not claim a current universal positional failure rate. |
| S12 | Skills package reusable procedural guidance and supporting resources. | [Agent Skills overview](https://agentskills.io/home), Agent Skills official standard documentation | Live page date not stated | Standard describes a format, not automatic access, competence, or execution authority. |
| S13 | Agent Skills can contain instructions, scripts and resources loaded as needed. | [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), Anthropic | 2025-10-16; standard update 2025-12-18 | Vendor introduction. No assertion that every provider's skill behavior is identical. |
| S14 | MCP connects AI applications with tools and information exposed by servers. | [MCP architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture), Model Context Protocol official documentation | Version 2026-07-28; page date not stated | Connection protocol is not a safety certification or permission grant. Low-level version details omitted from narration. |
| S15 | Retrieval can supply external information to generation, distinct from solely relying on model parameters. | [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), Lewis et al. / arXiv | 2020-05-22; revision 2021-04-12 | Research architecture. Primer gives a broad explanatory shorthand, not its exact implementation. |
| S16 | Feedback stored as text can affect later decisions without updating model weights. | [Reflexion](https://arxiv.org/abs/2303.11366), Shinn et al. / arXiv | 2023-03-20; revision 2023-10-10 | Specific research framework; not evidence that every memory feature learns this way. |
| S17 | Generated reasoning explanations can be plausible while failing to faithfully describe the causes of a prediction. | [Language Models Don't Always Say What They Think](https://arxiv.org/abs/2305.04388), Turpin et al. / arXiv | 2023-05-07; revision 2023-12-09 | Historical models under controlled biasing conditions. No claim that every explanation is false. |
| S18 | Multi-agent research can use a lead agent with parallel research workers; coordination introduces engineering tradeoffs. | [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), Anthropic | 2025-06-13 | Vendor system and internal evaluations. Numerical uplift/token claims omitted. Group-project examples are original analogies. |
| S19 | Idempotence concerns repeated requests having the same intended server effect as one request; uncertain writes cannot always be retried safely. | [RFC 9110, section 9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods), IETF / RFC Editor | 2022-06 | HTTP standard. Everyday repeated-purchase illustration generalizes the concept, not a claim every booking API enforces it. |
| S20 | External retrieved text can inject instructions and blur data/instruction boundaries. | [Not what you've signed up for](https://arxiv.org/abs/2302.12173), Greshake et al. / arXiv | 2023-02-23; revision 2023-05-05 | Demonstrations and threat taxonomy, not a prevalence estimate for current products. Venue-page attack is hypothetical. |
| S21 | Prompt injection and excessive agency are recognized application risks; boundaries and limited authority matter. | [Top 10 for LLM Applications](https://owasp.org/projects/top-10-for-large-language-model-applications), OWASP Foundation | Live project page date not stated | Risk guidance, not legal advice or proof of complete defenses. |
| S22 | Coding-agent evaluation can use real repository issues with test-based assessment. | [SWE-bench overview](https://www.swebench.com/SWE-bench/), SWE-bench official project | Live documentation date not stated | Benchmark describes tested issues; passing tests does not validate the entire profession or all design choices. |
| S23 | OpenAI introduced ChatGPT agent combining research and action with tools including a virtual computer. | [Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/), OpenAI | 2025-07-17 | Historical release. Current account availability, limits, and pricing deliberately not asserted. |
| S24 | Project Vend's first phase used a Claude-based shopkeeper with human physical support; it sourced goods, made loss-making decisions and confused claims about being human. | [Project Vend, phase one](https://www.anthropic.com/research/project-vend-1), Anthropic and Andon Labs | 2025-06-27 | Small office experiment with adversarial employees; no representative business success rate. |
| S25 | Phase two changed models, tools and instructions, improved business operations but retained manipulation problems; adding an AI manager did not isolate a causal profit effect. | [Project Vend, phase two](https://www.anthropic.com/research/project-vend-2), Anthropic and Andon Labs | 2025-12-18 | Iterating architecture and unusual small setting; report says no completely clean phase demarcation. No percentages used. |
| S26 | Agent evals should distinguish transcript, outcome and environment state; software, model and human grading have different strengths. | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic | 2026-01-09 | Vendor engineering account. Original personal experiment rubric is a recommendation. |
| S27 | METR time horizons measure task difficulty in human-expert completion time at a stated success probability, primarily on well-specified software/ML/cyber tasks. | [Task-completion time horizons](https://metr.org/time-horizons/), METR | Live page date not stated; Time Horizon 1.1 suite | No current model ranking or numeric horizon asserted. Does not measure runtime or all office tasks of equivalent duration. |
| S28 | In the early-2025 study, allowing AI tools increased completion time 19% across 246 real tasks from 16 experienced open-source maintainers; perceived improvement differed from the measurement. | [Experienced developer productivity study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/), METR | 2025-07-10 | RCT at issue level, experienced people on familiar large repositories, early-2025 tools; not generalizable to all developers, tasks, or current models. |
| S29 | Observational provider data covered millions of interactions; greater user experience was associated with both more auto-approval and more interruption. | [Measuring agent autonomy](https://www.anthropic.com/research/measuring-agent-autonomy), Anthropic | 2026-02-18 | Claude Code/API, observational, limited session visibility. Does not establish causality or market-wide usage. |
| S30 | As of August 2026, Anthropic reported Claude 'leads' 26% of AI R&D, with human supervision; no measured subset was fully autonomous. | [Measurements of AI development inside frontier labs](https://www.anthropic.com/institute/measuring-pace-of-ai-development), Anthropic | Page date not stated; metric explicitly August 2026 | Self-reported prototype automation index; model-assisted judgments and no common cross-lab methodology. Not proof of fully autonomous recursive self-improvement. |
| S31 | Speechify lists TXT as supported content and distinguishes word-for-word TTS from its overview-generating AI Podcast feature. | [Text to Audio Converter](https://speechify.com/blog/text-to-audio-converter-speechify/), Speechify | Page date not confidently extracted | Official product guidance. Actual upload/playback in Josh's account was not performed. Use text-to-speech for preserving full narration. |

## Numerical claims and calculations

- Chapter 11: independent invented steps with 0.95 success give `0.95^10 = 0.5987369392` and `0.95^20 = 0.3584859224`. Spoken rounding: about 60% and 36%. Explicitly a toy illustration, not product measurements.
- Chapter 15: invented timing example is 8 + 5 + 7 = 20 minutes versus 40 manually. Second invented case is 15 + 15 + 20 = 50 minutes. No RYC time-saving claim.
- Chapter 15: 16 developers, 246 tasks, 19% longer completion time: S28, with population, randomization and historical tool caveats spoken.
- Chapter 16: millions of interactions: S29; 26% and August 2026: S30, with self-report/method limitations spoken.
- Runtime: narration word count divided by assumed words per minute. This estimates duration; no Speechify audio has been rendered, and 1x speed varies with voice and pauses.

## Chapter map

| Chapters | Main evidence |
|---|---|
| 1-2: premise and definitions | S01-S03; original hypothetical event and delegation framing |
| 3: history | S04-S07, S16 |
| 4-6: loop, harness, tools | S02-S03, S08-S09; original event walk-through |
| 7: context, skills, MCP | S10-S14; live E002 conceptual continuity, not a fresh cross-provider comparison |
| 8: memory and retrieval | S08, S10, S15-S16; original recordkeeping example |
| 9: planning, reflection, explanations | S06, S16-S17; original planning examples |
| 10: multiple agents | S18; original coordination analysis |
| 11: compounding errors, retries | S19, original arithmetic and hypothetical failure cases |
| 12: security | S03, S20-S21; original attack example and first-experiment recommendation |
| 13: real examples | S22-S25; interpretation explicitly marked |
| 14: evaluation | S22, S26-S27; original task rubric |
| 15: economics | S28; original cost illustrations and job/task interpretation |
| 16: current use and future | S29-S30; future mechanisms explicitly interpretations |
| 17: experiment and recording | Original recommendation grounded in earlier mechanics and live editorial direction |

## Before public use

Recheck changed product claims near publication if the hosts add any. Preserve study populations and metric definitions in spoken explanations. Do not claim the hypothetical event happened or infer the hosts' reaction. Verify any actual demonstration from its resulting files and logs. Sources in this log were checked for this preparation date, not indefinitely.
