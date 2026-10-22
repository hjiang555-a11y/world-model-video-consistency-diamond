# Speaker Script — World Models and Video Consistency: DIAMOND

**Talk length:** ~10 minutes (about 150 words per minute; total ≈ 1,450 words)
**Deck:** `world-model-video-consistency-diamond.pptx` (12 slides)
**Timing marks:** each slide shows the target timestamp you should have reached.

---

## Slide 1 — Title (0:00–0:30)

> Good morning. Today I want to talk about world models and one specific property that decides
> whether they work at all: **video consistency**.
>
> The paper I'll walk you through is *Diffusion for World Modeling: Visual Details Matter in
> Atari* — DIAMOND for short — by Alonso, Jelley and colleagues, published at NeurIPS 2024.
> DIAMOND was the first work to make diffusion models usable as world models for reinforcement
> learning, and it did that by solving a consistency problem. In the next ten minutes I'll show
> you what the problem was, how diffusion fixed it, and what the numbers say.

---

## Slide 2 — Motivation: Two Problems, One Paper (0:30–1:40)

> Let me set up two problems.
>
> **Problem one: reinforcement learning is sample-hungry.** A classic Atari agent needs around
> fifty million environment steps. A world model fixes this by first learning the environment's
> dynamics from data, and then letting the agent train *inside the model's imagination* — only
> about one hundred thousand real steps, roughly two hours of gameplay.
>
> **Problem two: the current world models lose visual details.** The state of the art — IRIS,
> DreamerV3, STORM — all encode images as *discrete tokens* with a VQ-VAE, and then model the
> sequence with a transformer. Quantization is what keeps their rollouts stable, but it throws
> away fine-grained, few-pixel details. Enemies flicker, rewards vanish, scores drift — and
> these errors compound as the model imagines further into the future. So the "video" the world
> model generates is inconsistent, and the agent is trained on corrupted signal.
>
> **The bridge is diffusion.** Diffusion models dominate image generation, and they operate in a
> continuous latent space — no quantization bottleneck. The paper's question is exactly: can a
> diffusion model be the environment simulator of a world model, and does keeping the visual
> details actually produce a better agent? The answer to both is yes.

---

## Slide 3 — DIAMOND: A Diffusion Model as the Environment (1:40–2:40)

> Here is the full system. This is the paper's Figure 1: the model unrolls imagination over
> time. At each environment step, a diffusion model **D** denoises the next frame, conditioned
> on the history of past observations and actions.
>
> DIAMOND has three components.
>
> **First, the diffusion world model itself.** It's a 2D U-Net built on the EDM framework. Past
> frames are concatenated channel-wise to the noisy next frame; actions are injected through
> adaptive group-normalization layers. EDM's noise schedule is what makes the model stable
> enough to sample in just one to three denoising steps — that turns out to be crucial.
>
> **Second, a reward and termination model** — a standard CNN-LSTM that predicts the scalar
> reward and the end of episode, which handles partial observability.
>
> **Third, the agent** — an actor-critic with a shared CNN-LSTM. The policy is trained with
> REINFORCE plus a value baseline; the value with lambda-returns. All of this happens *entirely
> inside imagination*.
>
> The training loop is the standard world-model recipe: collect data in the real environment,
> retrain the world model on everything collected so far, train the agent inside the updated
> model, repeat.

---

## Slide 4 — Design Choice 1: EDM Beats DDPM for Stability (2:40–3:30)

> The first design decision: which diffusion framework? The natural candidate would be DDPM,
> but look at the left panel — DDPM-based trajectories corrupt over time, colors shift, and the
> error compounds.
>
> The reason is subtle. DDPM is trained to predict the *noise*. When the noise level dominates,
> the optimal prediction collapses toward the identity map — so at the beginning of sampling,
> the model has a terrible estimate of the score. That bad estimate compounds across rollout
> steps.
>
> EDM instead adaptively mixes signal and noise in its training objective: when noise
> dominates, the network is trained to predict the *clean image itself*. That gives a much
> better score estimate even with almost no signal — and, as the right panel shows, the
> trajectory stays stable even with a single denoising step.
>
> This is the first consistency result of the talk: **the choice of diffusion formulation
> directly determines how fast imagined video drifts.**

---

## Slide 5 — Design Choice 2: 3 Denoising Steps, Not 1 (3:30–4:20)

> But one step is not always enough. Look at Boxing: the black opponent's movement is
> unpredictable — the environment is partially observable. With one denoising step, the model
> predicts the *expectation* over possible next frames, and when that posterior is multimodal,
> the expectation itself is an out-of-distribution blur. You can see it in the top row.
>
> With three iterative steps, shown in the bottom row, sampling gets driven toward one specific
> mode — a crisp, consistent frame.
>
> The ablation confirms it: across the ten best games, mean human-normalized score drops from
> 3.05 with three steps to 1.96 with one. Visual stability translates directly into agent
> performance.
>
> Note the tension here: every denoising step is a full network forward pass, and a world
> model must render thousands of frames per training episode. DIAMOND's achievement is being
> stable enough that three steps suffice.

---

## Slide 6 — The Core Result: Consistent Videos, Game by Game (4:20–5:20)

> Now the paper's central comparison: the same imagined trajectories rendered by IRIS and by
> DIAMOND, trained on the same data.
>
> Watch the white boxes on the left — that's IRIS. In Asterix, an enemy turns into a reward
> and back. In Breakout, the bricks and the score drift between frames. In Road Runner, the
> reward dots flicker in and out of existence.
>
> None of this happens with DIAMOND on the right. And this is *not* bought with more compute —
> both render at the same 64-by-64 resolution, DIAMOND needs only three network evaluations
> per frame versus sixteen for IRIS, and it has fewer parameters.
>
> Why does this matter? Because in a world model, every imagined frame is a training sample.
> An agent that should chase rewards and avoid enemies is, in IRIS, literally being trained on
> frames where the two are swapped. Few-pixel inconsistency is *label noise for the policy*.

---

## Slide 7 — Atari 100k: A New Best Among World-Model Agents (5:20–6:20)

> The benchmark: Atari 100k — twenty-six games, one hundred thousand environment steps per
> game, about two hours of human play, five seeds each.
>
> DIAMOND reaches a **mean human-normalized score of 1.46** — superhuman on average, and a new
> best among agents trained entirely inside a world model. It beats humans on eleven of the
> twenty-six games.
>
> The wins concentrate exactly where tiny visual details decide outcomes: Asterix at 3,698
> versus STORM's 1,028; Breakout 132 versus IRIS's 84; Road Runner 20,673 — the highest on the
> board.
>
> The fair comparison matters: the agent architectures are close to those of prior work, so
> the gap traces back to the world model itself — to the consistency of the video it imagines.

---

## Slide 8 — Stability, Measured: Pixel Drift over 1000 Steps (6:20–6:50)

> Consistency also has a quantitative form. Here the world model imagines one thousand steps
> of Breakout from the same start frame, following the same expert actions — averaged over
> four hundred reference trajectories.
>
> DDPM drifts more and more; even with ten denoising steps it's less stable than one-step EDM.
> And EDM's residual drift is *trajectory difference* — the model imagining a slightly
> different but valid play — not the pathological color corruption of DDPM.
>
> This slide ties the whole talk together: video consistency in a world model is not
> aesthetics. Inconsistency is noise on the agent's training signal, and it compounds with
> rollout length. DIAMOND attacks it at the source, with the diffusion formulation itself.

---

## Slide 9 — Scaling Up: An Interactive Neural Game Engine (6:50–7:40)

> Finally, does this recipe survive contact with the real world? The authors trained the same
> diffusion world model — with no RL, no game engine — on static footage of Counter-Strike:
> Global Offensive at 64-by-64, and on motorway driving video.
>
> The result: people could *play inside the world model live*, with keyboard and mouse, and
> the imagined world stayed stable over minutes of interaction.
>
> Quantitatively, DIAMOND reaches an FVD of **34.8** on CS:GO — versus 85.7 for the best IRIS
> variant and 509 for DreamerV3. On driving, FVD 80.3 versus 277 and 734.
>
> The same recipe that kept Asterix consistent keeps a first-person 3D environment consistent —
> a step toward world models as general, video-consistent environment simulators.

---

## Slide 10 — Limitations and Open Questions (7:40–8:40)

> Being honest about the limits. The model runs at 64-by-64 resolution — visual richness at
> scale is still open. The *agent* is sample-efficient, but the *world model* is not: the full
> benchmark took about one GPU-year on RTX 4090s. Sampling is around ten frames per second —
> interactive use required stochastic sampling and more steps. And each model is single-task:
> one world model per game, no cross-environment generalization.
>
> Most importantly, visual consistency is **not** physical consistency. Rollouts stay faithful
> visually, but they are not physically grounded, and long-horizon drift still exists — that's
> an active research frontier, and in fact the direction my own ongoing project explores.

---

## Slide 11 — What to Remember (8:40–9:30)

> Five takeaways.
>
> One: **consistency is the bottleneck.** Discrete-token world models lose few-pixel visual
> details, and those details are exactly what the agent's reward signal depends on.
>
> Two: **diffusion fixes it.** A continuous diffusion world model has no quantization
> bottleneck and stays stable over long rollouts.
>
> Three: **consistency becomes performance.** Mean HNS 1.46, superhuman on eleven of
> twenty-six games, with the gains concentrated where visual detail matters.
>
> Four: **it scales beyond games.** CS:GO FVD 34.8 with interactive human play; coherent
> driving video — a general recipe for consistent video world models.
>
> Five: **the frontier is open** — resolution, speed, sample efficiency, and physical
> grounding are all still unsolved.

---

## Slide 12 — Thank You (9:30–10:00)

> Thank you. The code, agents, and playable world models are all released at the project page
> shown here. I'm happy to take questions.

---

## Backup: Likely Q&A

**Q: Why not just use a bigger discrete VAE, like IRIS with 64 tokens?**
A: More tokens help a bit (the paper reports IRIS K=64 in the 3D experiments), but it doesn't
close the gap — DIAMOND still achieves far lower FVD and LPIPS at comparable parameters. The
issue is the discrete bottleneck itself, not just its size.

**Q: Isn't 3 NFE per frame very expensive compared to a transformer step?**
A: Yes, and the paper is explicit that the world model — not the agent — is the
compute-hungry part (~10 FPS on Atari; 1.03 GPU-years total). Subsequent work (latent
diffusion world models) addresses exactly this.

**Q: Does this work with stochastic environments?**
A: Yes — diffusion is a natural fit: the denoising process samples from the predictive
distribution. The Boxing example is precisely a partially observable, stochastic setting
where multi-step sampling resolves multimodality.

**Q: Why Atari — isn't it solved?**
A: Atari 100k is the standard *sample-efficiency* benchmark — 2 hours of gameplay instead of
50M steps. It's the right testbed for world-model agents, and the visual-detail failure mode
is cleanest to diagnose there. The CS:GO/driving section shows the same recipe scaling to
real 3D footage.
