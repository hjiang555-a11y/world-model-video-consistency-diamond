# World Models and Video Consistency — DIAMOND

A 10-minute technical presentation on the paper

> **Diffusion for World Modeling: Visual Details Matter in Atari**
> Eloi Alonso, Adam Jelley, Vincent Micheli, Anssi Kanervisto, Amos Storkey, Tim Pearce, François Fleuret
> *NeurIPS 2024* — [arXiv:2405.12399](https://arxiv.org/abs/2405.12399)

## Contents

| File | Description |
|------|-------------|
| `world-model-video-consistency-diamond.pptx` | The presentation deck (12 slides, 16:9, all-English) |
| `speaker-script.md` | Full speaker script with per-slide timing marks (≈10 min at ~150 wpm) + backup Q&A |
| `build_ppt.py` | Script that regenerates the deck from `figs/` (python-pptx) |
| `figs/` | Figure crops extracted from the paper (PyMuPDF) |
| `assets/diamond_paper.pdf` | The original paper PDF |

## Talk structure (12 slides / ~10 min)

| # | Slide | Time |
|---|-------|------|
| 1 | Title | 0:00 |
| 2 | Motivation: Two Problems, One Paper | 0:30 |
| 3 | DIAMOND: A Diffusion Model as the Environment | 1:40 |
| 4 | Design Choice 1: EDM Beats DDPM for Stability | 2:40 |
| 5 | Design Choice 2: 3 Denoising Steps, Not 1 | 3:30 |
| 6 | The Core Result: Consistent Videos, Game by Game | 4:20 |
| 7 | Atari 100k: A New Best Among World-Model Agents | 5:20 |
| 8 | Stability, Measured: Pixel Drift over 1000 Steps | 6:20 |
| 9 | Scaling Up: An Interactive Neural Game Engine | 6:50 |
| 10 | Limitations and Open Questions | 7:40 |
| 11 | What to Remember | 8:40 |
| 12 | Thank You | 9:30 |

## Key facts covered

- **Problem:** world-model RL agents (IRIS, DreamerV3, STORM) encode frames as discrete
  tokens; quantization destroys few-pixel visual details → frame-to-frame inconsistency in
  imagined rollouts → noisy training signal for the policy.
- **Method:** DIAMOND uses an EDM-based diffusion model as the environment dynamics model —
  a continuous latent space with no quantization bottleneck. Past frames are concatenated
  channel-wise; actions are injected via adaptive group norm.
- **Design choices:** EDM's adaptive signal/noise mixing (vs. DDPM noise prediction) keeps
  rollouts stable, even at 1 denoising step; 3 steps are used to resolve multimodality under
  partial observability.
- **Results:** mean human-normalized score **1.46** on Atari 100k (superhuman on 11/26
  games, new best among world-model-only agents); IQM 0.64.
- **Efficiency:** 3 NFE/frame vs. 16 for IRIS, at the same 64×64 resolution, fewer parameters.
- **Scaling:** standalone diffusion world model trained on static CS:GO (FVD **34.8**) and
  motorway driving (FVD **80.3**) — humans played the CS:GO world live with keyboard & mouse.
- **Limitations:** 64×64 resolution, ~10 FPS sampling, world model is compute-hungry
  (~1.03 GPU-years for the benchmark), single-task per game, visual ≠ physical consistency.

## Rebuilding the deck

```bash
# requirements: python-pptx
python3 build_ppt.py
```

## Attribution

All figures are reproduced from the paper (arXiv:2405.12399) for presentation purposes.
Original code, agents and playable world models: <https://diamond-wm.github.io>
