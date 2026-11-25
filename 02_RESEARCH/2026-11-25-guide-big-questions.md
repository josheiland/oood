---
title: Sources for two new deep-end topics
tags: [oood, website, research]
---

# November 25, 2026

**AI time horizons.** METR measures the length of tasks a human expert would take for the agent to meet a given success rate on its task suite. The Reddit discussion about TH1.1 foregrounded a common confusion between the model's actual running time and the human baseline. Other discussion questioned how well evidence from long software tasks carries over to ordinary work. The guide explains the measure and avoids extrapolating it to other tasks. [METR benchmark and caveats](https://metr.org/time-horizons/) · [Reddit analysis of TH1.1](https://www.reddit.com/r/MachineLearning/comments/1r60d0c/metr_th11_working_time_is_wildly_different_across/) · [Reddit discussion of benchmark validity](https://www.reddit.com/r/MachineLearning/comments/1tnhnh5/the_famous_metr_ai_time_horizons_graph_contains/) · [X discussion of an example result](https://x.com/i/trending/2044518642558423298)

**AI improving AI.** Karpathy's autoresearch lets an agent modify training code, run a small timed test and keep a change if validation loss improves. In his March 8 X post he reported one transfer to a deeper model. Practitioners on Reddit talked about running the loop on image classification and about testing finalists on data the loop never saw. Those are examples of the distinction between tuning a known score and finding an improvement that transfers. [Original project and limits](https://github.com/karpathy/autoresearch) · [Karpathy's X post](https://x.com/karpathy/status/2030777122223173639) · [Reddit reproduction](https://www.reddit.com/r/computervision/comments/1rwjpk7/autoresearch_on_cifar10/) · [Reddit discussion of a fresh check](https://www.reddit.com/r/BestGitHubRepos/comments/1wel62x/autoresearch_karpathys_overnight_ml_research_loop/)

Sources accessed 2026-11-25. The threads surface disagreements and practical questions. Neither establishes a consensus or a general prediction.
