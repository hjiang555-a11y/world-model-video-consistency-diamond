# Speaker Script — World Models and Video Consistency: DIAMOND

**Talk length:** ~8 minutes (about 150 words per minute; total ≈ 1,170 words, leaving buffer within a 10-min slot)
**Deck:** `world-model-video-consistency-diamond.pptx` (12 slides)

---

## Slide 1 — Title (0:00–0:20)

> Good morning. Today: world models, and the one property that decides whether they work —
> **video consistency**. The paper is *Diffusion for World Modeling: Visual Details Matter in
> Atari* — DIAMOND — from NeurIPS 2024. It was the first work to make diffusion usable as a
> world model for reinforcement learning, and it did so by fixing a consistency problem. I'll
> show you the problem, the fix, and the numbers.

---

## Slide 2 — Motivation (0:20–1:10)

> Two problems. **One:** RL is sample-hungry — a classic Atari agent needs ~50 million steps.
> World models fix this: learn the dynamics from data, then train the agent *in imagination*
> with only ~100k real steps, about two hours of play.
>
> **Two:** current world models — IRIS, DreamerV3, STORM — encode frames as *discrete tokens*.
> Quantization keeps rollouts stable, but throws away few-pixel details. Enemies flicker,
> rewards vanish, scores drift — and these errors compound. The agent trains on corrupted video.
>
> **The bridge:** diffusion operates in a continuous space, no quantization bottleneck. The
> paper's question: can a diffusion model *be* the world model — and does keeping the visual
> details actually make the agent better? Both answers: yes.

---

## Slide 3 — DIAMOND: A Diffusion Model as the Environment (1:10–1:55)

> This is the full system — the paper's Figure 1: at each step, a diffusion model denoises the
> next frame, conditioned on past observations and actions.
>
> Three components. **The world model:** a 2D U-Net built on EDM. Past frames are concatenated
> channel-wise to the noisy next frame; actions enter through adaptive group-normalization.
> EDM's noise schedule is what makes sampling stable in just one to three steps.
>
> **A reward/termination model:** a small CNN-LSTM predicting scalar reward and episode end —
> it handles partial observability.
>
> **The agent:** an actor-critic, shared CNN-LSTM, trained with REINFORCE plus a value
> baseline, entirely inside imagination.
>
> The loop is standard: collect real data, retrain the world model, train the agent inside it,
> repeat.

---

## Slide 4 — Design Choice 1: EDM Beats DDPM (1:55–2:35)

> First design choice: which diffusion framework? DDPM looks natural — but on the left, its
> trajectories corrupt: colors shift, error compounds.
>
> Why: DDPM predicts the *noise*. When noise dominates, the optimal prediction collapses to the
> identity map — the model has a terrible score estimate at the start of sampling, and the
> error accumulates over rollout.
>
> EDM adaptively mixes signal and noise: when noise dominates, the network predicts the *clean
> image* — a good score estimate even with almost no signal. On the right: stable, even with
> one denoising step.
>
> First consistency lesson: **the diffusion formulation itself determines how fast imagined
> video drifts.**

---

## Slide 5 — Design Choice 2: 3 Steps, Not 1 (2:35–3:15)

> But one step isn't always enough. Boxing: the opponent's moves are unpredictable — partial
> observability. With one step, the model predicts the *expectation* over possible next frames;
> when that distribution is multimodal, the expectation is an out-of-distribution blur — the
> top row.
>
> Three iterative steps drive sampling into one specific mode — crisp and consistent, bottom
> row. The ablation confirms it: on the ten best games, mean human-normalized score drops from
> 3.05 with three steps to 1.96 with one.
>
> Note the tension: each step is a full network pass, and a world model renders thousands of
> frames per episode. DIAMOND's achievement is being stable enough that three steps suffice.

---

## Slide 6 — The Core Result: Consistent Videos (3:15–4:00)

> Now the paper's central comparison: the same imagined trajectories from IRIS and DIAMOND.
>
> Watch the white boxes — IRIS. Asterix: an enemy becomes a reward and back. Breakout: bricks
> and score drift. Road Runner: rewards flicker in and out.
>
> None of this happens with DIAMOND. And it's *not* bought with compute: same 64×64
> resolution, three network evaluations per frame versus sixteen for IRIS, fewer parameters.
>
> Why it matters: every imagined frame is a training sample. An agent that should chase
> rewards and avoid enemies is, in IRIS, literally trained on frames where the two are swapped.
> Few-pixel inconsistency is **label noise for the policy**.

---

## Slide 7 — Atari 100k Results (4:00–4:45)

> The benchmark: 26 games, 100k environment steps each — two hours of play — five seeds.
>
> DIAMOND reaches a **mean human-normalized score of 1.46**: superhuman on average, a new best
> among agents trained entirely inside a world model, and superhuman on 11 of 26 games.
>
> The wins concentrate where tiny details decide: Asterix 3,698 versus STORM's 1,028; Breakout
> 132 versus IRIS's 84; Road Runner 20,673 — best on the board.
>
> The fair comparison matters: the agent is essentially the same as prior work's, so the gap
> traces to the world model — to the consistency of the video it imagines.

---

## Slide 8 — Stability, Measured (4:45–5:10)

> Consistency, quantified: one thousand imagined steps of Breakout from the same start frame,
> same expert actions, averaged over four hundred reference trajectories.
>
> DDPM drifts more and more — even ten steps stay worse than one-step EDM. And EDM's residual
> drift is *trajectory difference* — an equally valid but different play — not the color
> corruption of DDPM.
>
> The point: consistency is not aesthetics. Inconsistency is noise on the agent's training
> signal, and it compounds with rollout length. DIAMOND attacks it at the source.

---

## Slide 9 — Scaling Up: CS:GO / Driving (5:10–5:45)

> Does the recipe survive reality? They trained the same diffusion world model — no RL, no
> engine — on static CS:GO footage and on motorway driving.
>
> People could *play inside it live*, keyboard and mouse, stable over minutes of interaction.
>
> Numbers: FVD **34.8** on CS:GO versus 85.7 for the best IRIS and 509 for DreamerV3. Driving:
> 80.3 versus 277 and 734.
>
> The same recipe that kept Asterix consistent keeps a first-person 3D world consistent.

---

## Slide 10 — Limitations (5:45–6:30)

> Being honest about the limits: 64×64 resolution; sampling at about 10 FPS; the *agent* is
> sample-efficient but the *world model* is not — about one GPU-year for the full benchmark;
> one world model per game.
>
> Most importantly: visual consistency is **not** physical consistency. Rollouts look right
> but are not physically grounded, and long-horizon drift remains — an active frontier, and
> the direction of my own ongoing project.

---

## Slide 11 — Takeaways (6:30–7:10)

> Five takeaways. One: **consistency is the bottleneck** — discrete tokens lose the few-pixel
> details the reward signal depends on. Two: **diffusion fixes it** — continuous, no
> quantization bottleneck, stable rollouts. Three: **consistency becomes performance** — 1.46,
> superhuman on 11 of 26. Four: **it scales** — CS:GO FVD 34.8 with interactive human play.
> Five: **the frontier is open** — resolution, speed, sample efficiency, physical grounding.

---

## Slide 12 — Thank You (7:10–7:40)

> Thank you. Code, agents, and playable world models are released at the project page. Happy
> to take questions.

---

## Backup: Likely Q&A

**Q: Why not just a bigger discrete VAE, like IRIS with 64 tokens?**
A: More tokens help a bit (IRIS K=64 in the 3D experiments), but it doesn't close the gap —
DIAMOND still achieves far lower FVD and LPIPS at comparable parameters. The issue is the
discrete bottleneck itself, not just its size.

**Q: Isn't 3 NFE per frame very expensive compared to a transformer step?**
A: Yes, and the paper is explicit that the world model — not the agent — is the
compute-hungry part (~10 FPS on Atari; 1.03 GPU-years total). Subsequent latent diffusion
world models address exactly this.

**Q: Does this work with stochastic environments?**
A: Yes — diffusion is a natural fit: the denoising process samples from the predictive
distribution. Boxing is precisely a partially observable, stochastic setting where multi-step
sampling resolves multimodality.

**Q: Why Atari — isn't it solved?**
A: Atari 100k is the standard *sample-efficiency* benchmark — 2 hours of gameplay instead of
50M steps. It's the right testbed for world-model agents, and the visual-detail failure mode
is cleanest to diagnose there. CS:GO/driving show the recipe scaling to real 3D footage.
