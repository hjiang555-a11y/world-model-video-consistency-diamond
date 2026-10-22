"""Build the DIAMOND presentation deck (16:9, all-English)."""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

BASE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(BASE, "figs")

# ---- design system ----
NAVY = RGBColor(0x1F, 0x49, 0x7D)
NAVY_DARK = RGBColor(0x16, 0x2B, 0x4A)
BLUE = RGBColor(0x2D, 0x2D, 0x8A)
RED = RGBColor(0xC0, 0x50, 0x4D)
ORANGE = RGBColor(0xED, 0x7D, 0x31)
GREEN = RGBColor(0x6A, 0x9B, 0x3C)
GRAY = RGBColor(0x59, 0x59, 0x59)
LIGHT = RGBColor(0xEF, 0xF2, 0xF7)
LIGHTER = RGBColor(0xF7, 0xF8, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x1A, 0x1A, 0x1A)

BODY_FONT = "Calibri"
MONO_FONT = "Consolas"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

SW, SH = prs.slide_width, prs.slide_height


def add_slide():
    return prs.slides.add_slide(BLANK)


def rect(slide, x, y, w, h, fill=None, line=None, line_w=None, shadow=False):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sp.fill.background() if fill is None else sp.fill.solid()
    if fill is not None:
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = line_w or Pt(1)
    sp.shadow.inherit = False
    return sp


def textbox(slide, x, y, w, h, runs, size=18, color=BLACK, bold=False,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.0,
            space_after=0):
    """runs: str, or list of paragraphs; each paragraph is a list of (text, dict) runs."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    if isinstance(runs, str):
        runs = [[(runs, {})]]
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        if space_after:
            p.space_after = Pt(space_after)
        for text, style in para:
            r = p.add_run()
            r.text = text
            f = r.font
            f.name = style.get("font", BODY_FONT)
            f.size = Pt(style.get("size", size))
            f.bold = style.get("bold", bold)
            f.italic = style.get("italic", False)
            f.color.rgb = style.get("color", color)
    return tb


def title_bar(slide, title, kicker=None):
    """Standard content-slide header: navy band + title."""
    rect(slide, 0, 0, SW, Inches(0.86), fill=NAVY)
    rect(slide, 0, Inches(0.86), SW, Pt(2.6), fill=ORANGE)
    textbox(slide, Inches(0.55), Inches(0.10), Inches(11.6), Inches(0.68),
            title, size=27, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if kicker:
        textbox(slide, SW - Inches(3.3), Inches(0.13), Inches(2.9), Inches(0.62),
                kicker, size=13, color=RGBColor(0xC9, 0xD6, 0xE8),
                align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def footer(slide, text):
    textbox(slide, Inches(0.55), SH - Inches(0.38), Inches(10), Inches(0.3),
            text, size=10.5, color=GRAY)


def add_image(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(path, x, y, w, h)


def bullet_box(slide, x, y, w, h, items, size=17, gap=6, marker_color=ORANGE):
    """items: list of str, list of [str], or list of [(text, style), ...] run-lists."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.04
        # bullet marker
        r = p.add_run()
        r.text = "▸ "
        f = r.font
        f.name = BODY_FONT
        f.size = Pt(size)
        f.bold = True
        f.color.rgb = marker_color
        # normalize item: str | [str] | [(text, style), ...]
        if isinstance(item, str):
            item = [(item, {})]
        elif len(item) == 1 and isinstance(item[0], str):
            item = [(item[0], {})]
        for text, style in item:
            r2 = p.add_run()
            r2.text = text
            f2 = r2.font
            f2.name = style.get("font", BODY_FONT)
            f2.size = Pt(style.get("size", size))
            f2.bold = style.get("bold", False)
            f2.italic = style.get("italic", False)
            f2.color.rgb = style.get("color", BLACK)
    return tb


def card(slide, x, y, w, h, fill=LIGHTER, line=RGBColor(0xD8, 0xDE, 0xE8)):
    sp = rect(slide, x, y, w, h, fill=fill, line=line, line_w=Pt(1))
    return sp


# =====================================================================
# Slide 1 — Title
# =====================================================================
s = add_slide()
rect(s, 0, 0, SW, SH, fill=WHITE)
rect(s, 0, 0, SW, Inches(0.16), fill=NAVY)
textbox(s, Inches(1.0), Inches(2.15), Inches(11.33), Inches(1.7),
        [[("World Models and Video Consistency", {"size": 46, "bold": True, "color": NAVY})]],
        align=PP_ALIGN.CENTER)
textbox(s, Inches(1.0), Inches(3.15), Inches(11.33), Inches(0.9),
        [[("Diffusion for World Modeling: Visual Details Matter in Atari", {"size": 25, "color": GRAY})]],
        align=PP_ALIGN.CENTER)
textbox(s, Inches(1.0), Inches(3.62), Inches(11.33), Inches(0.55),
        [[("Alonso, Jelley, Micheli, Kanervisto, Storkey, Pearce, Fleuret — NeurIPS 2024 (arXiv:2405.12399)",
           {"size": 16, "italic": True, "color": ORANGE})]],
        align=PP_ALIGN.CENTER)
rect(s, Inches(5.42), Inches(4.35), Inches(2.5), Pt(2.2), fill=NAVY)
textbox(s, Inches(1.0), Inches(4.62), Inches(11.33), Inches(0.5),
        [[("A technical presentation on the DIAMOND world model", {"size": 18, "color": BLACK})]],
        align=PP_ALIGN.CENTER)
# small illustrative strip: DDPM drift vs EDM stability
im_w = Inches(2.4)
add_image(s, os.path.join(FIGS, "fig3_ddpm.png"), Inches(3.15), Inches(5.35), w=im_w)
add_image(s, os.path.join(FIGS, "fig3_edm.png"), Inches(5.75), Inches(5.35), w=im_w)
textbox(s, Inches(3.15), Inches(6.32), Inches(2.4), Inches(0.3),
        "DDPM — drifting, colors corrupt", size=11, color=RED, align=PP_ALIGN.CENTER)
textbox(s, Inches(5.75), Inches(6.32), Inches(2.4), Inches(0.3),
        "EDM (DIAMOND) — stable", size=11, color=GREEN, align=PP_ALIGN.CENTER)
textbox(s, Inches(8.6), Inches(5.6), Inches(3.9), Inches(0.9),
        [[("Diffusion world models keep",
           {"size": 14, "color": BLACK, "bold": True})],
         [("the visual details consistent —",
           {"size": 14, "color": BLACK, "bold": True})],
         [("and that consistency wins games.",
           {"size": 14, "color": BLACK, "bold": True})]],
        align=PP_ALIGN.LEFT)

# =====================================================================
# Slide 2 — Motivation
# =====================================================================
s = add_slide()
title_bar(s, "Motivation: Two Problems, One Paper", kicker="1 / 11")
card(s, Inches(0.55), Inches(1.15), Inches(6.0), Inches(2.55))
textbox(s, Inches(0.8), Inches(1.32), Inches(5.5), Inches(0.5),
        [[("Problem 1 — RL is sample-hungry", {"size": 19, "bold": True, "color": NAVY})]])
bullet_box(s, Inches(0.8), Inches(1.85), Inches(5.5), Inches(1.8),
           ["Classic Atari agents: ~50M environment steps to master a game.",
            "World models: learn dynamics from data, then train the agent \"in imagination\" — 100k steps (~2 h) instead.",
            "World model = simulated video of the environment; agent never touches the real env during training."],
           size=15, gap=5)
card(s, Inches(6.85), Inches(1.15), Inches(6.0), Inches(2.55))
textbox(s, Inches(7.1), Inches(1.32), Inches(5.5), Inches(0.5),
        [[("Problem 2 — discrete latents lose visual details", {"size": 19, "bold": True, "color": NAVY})]])
bullet_box(s, Inches(7.1), Inches(1.85), Inches(5.5), Inches(1.8),
           ["SOTA world models (IRIS, DreamerV3, STORM) encode images as discrete tokens (VQ-VAE + transformer).",
            "Quantization discards fine-grained, few-pixel details — enemies flicker, rewards vanish, scores drift.",
            "Small visual errors compound over rollout → inconsistent \"video\" → suboptimal policy."],
           size=15, gap=5)
rect(s, Inches(0.55), Inches(4.05), Inches(12.3), Inches(2.85), fill=LIGHTER, line=RGBColor(0xD8, 0xDE, 0xE8))
textbox(s, Inches(0.8), Inches(4.2), Inches(11.8), Inches(0.5),
        [[("The bridge: diffusion models", {"size": 19, "bold": True, "color": NAVY})]])
bullet_box(s, Inches(0.8), Inches(4.72), Inches(11.8), Inches(2.0),
           [[("Diffusion models dominate image generation —", {}),
             (" they synthesize images in a continuous latent space, with no quantization bottleneck.", {"bold": True})],
            [("Question: ", {}),
             ("can a diffusion model serve as the environment simulator of a world model — and does preserving visual details actually make the agent better?", {"bold": True, "color": NAVY})],
            [("Answer (this paper): ", {}),
             ("yes — DIAMOND, a world-model RL agent with a diffusion dynamics model, sets a new Atari-100k record (mean HNS 1.46).", {"bold": True, "color": GREEN})]],
           size=15.5, gap=5)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 3 — Method overview
# =====================================================================
s = add_slide()
title_bar(s, "DIAMOND: A Diffusion Model as the Environment", kicker="2 / 11")
# left: fig 1
add_image(s, os.path.join(FIGS, "fig1_method.png"), Inches(0.35), Inches(1.15), w=Inches(5.6))
textbox(s, Inches(0.35), Inches(5.35), Inches(5.6), Inches(1.2),
        [[("Figure 1 (paper): unrolling imagination over time. A diffusion model D", {}),
          ("θ", {"font": BODY_FONT}),
          (" denoises the next frame conditioned on past observations and actions.", {})]],
        size=11, color=GRAY)
# right: numbered components
textbox(s, Inches(6.45), Inches(1.1), Inches(6.45), Inches(0.45),
        [[("The three components", {"size": 20, "bold": True, "color": NAVY})]])
steps = [
    ("1", "Diffusion world model (EDM)", "2D U-Net denoises next frame; past frames concatenated channel-wise; actions injected via adaptive group norm. EDM noise schedule → stable 1–3 step sampling."),
    ("2", "Reward / termination model", "Separate CNN + LSTM (R\u03C8) predicts scalar reward and episode end — handles partial observability."),
    ("3", "Agent (actor-critic)", "Shared CNN-LSTM; policy \u03C0 trained with REINFORCE + value baseline; value trained with \u03BB-returns — entirely inside imagination."),
]
y = 1.62
for num, head, body in steps:
    rect(s, Inches(6.45), Inches(y), Inches(0.44), Inches(0.44), fill=NAVY)
    textbox(s, Inches(6.45), Inches(y + 0.02), Inches(0.44), Inches(0.4),
            num, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    textbox(s, Inches(7.05), Inches(y - 0.03), Inches(5.85), Inches(0.4),
            [[(head, {"size": 16.5, "bold": True, "color": BLACK})]])
    textbox(s, Inches(7.05), Inches(y + 0.36), Inches(5.85), Inches(1.05),
            body, size=13, color=GRAY)
    y += 1.62
textbox(s, Inches(6.45), Inches(6.5), Inches(6.45), Inches(0.55),
        [[("Training loop: ", {"bold": True, "color": BLACK}),
          ("collect data in real env → update world model on all data → train agent in imagination → repeat (standard world-model RL recipe).", {"color": GRAY})]],
        size=13)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 4 — Design choice 1: EDM vs DDPM
# =====================================================================
s = add_slide()
title_bar(s, "Design Choice 1: EDM Beats DDPM for Stability", kicker="3 / 11")
add_image(s, os.path.join(FIGS, "fig3_ddpm.png"), Inches(0.4), Inches(1.15), w=Inches(5.9))
add_image(s, os.path.join(FIGS, "fig3_edm.png"), Inches(6.6), Inches(1.15), w=Inches(5.9))
textbox(s, Inches(0.4), Inches(4.35), Inches(5.9), Inches(0.35),
        "DDPM trajectories — color corrupts, error compounds", size=14, bold=True, color=RED, align=PP_ALIGN.CENTER)
textbox(s, Inches(6.6), Inches(4.35), Inches(5.9), Inches(0.35),
        "EDM trajectories — stable even with 1 denoising step", size=14, bold=True, color=GREEN, align=PP_ALIGN.CENTER)
card(s, Inches(0.4), Inches(4.85), Inches(12.35), Inches(1.95))
bullet_box(s, Inches(0.7), Inches(5.0), Inches(11.8), Inches(1.7),
           [[("Why: ", {"bold": True}),
             ("DDPM predicts the noise \u03B5; when noise dominates, this collapses toward the identity map \u2192 poor score estimate at the start of sampling \u2192 error compounds over rollout.", {})],
            [("EDM instead ", {"bold": True}),
             ("adaptively mixes signal and noise: when noise dominates, the net is trained to predict the clean image — a much better score estimate with almost no signal.", {})],
            [("Result: ", {"bold": True}),
             ("EDM-based world model stays consistent over long rollouts, even at n = 1 denoising step.", {"bold": True, "color": GREEN})]],
           size=14.5, gap=5)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 5 — Design choice 2: denoising steps
# =====================================================================
s = add_slide()
title_bar(s, "Design Choice 2: 3 Denoising Steps (Not 1)", kicker="4 / 11")
add_image(s, os.path.join(FIGS, "fig4_boxing.png"), Inches(0.4), Inches(1.2), w=Inches(8.2))
textbox(s, Inches(0.4), Inches(3.95), Inches(8.2), Inches(0.4),
        "Boxing: 1 step (top) vs 3 steps (bottom) — the black player's motion is unpredictable",
        size=12, color=GRAY, align=PP_ALIGN.CENTER)
card(s, Inches(8.95), Inches(1.2), Inches(3.95), Inches(3.15))
textbox(s, Inches(9.15), Inches(1.35), Inches(3.55), Inches(0.45),
        [[("1 vs 3 steps", {"size": 17, "bold": True, "color": NAVY})]])
bullet_box(s, Inches(9.15), Inches(1.85), Inches(3.55), Inches(2.4),
           [[("1 step = one denoising step: cheap, but the single-step predictor is the ", {}),
             ("expectation", {"italic": True}),
             (" over possible next frames.", {})],
            [("Partial observability ", {"bold": True}),
             ("makes that distribution multimodal → the expectation is an out-of-distribution blur.", {})],
            [("3 iterative steps ", {"bold": True, "color": GREEN}),
             ("drive sampling toward one specific mode → crisp, consistent frames.", {})]],
           size=13, gap=5)
textbox(s, Inches(0.4), Inches(4.55), Inches(12.35), Inches(0.55),
        [[("Ablation: mean HNS on top-10 games drops from 3.05 (n = 3) to 1.96 (n = 1) — visual stability translates directly into agent performance.", {"bold": True, "color": NAVY})]],
        size=15)
textbox(s, Inches(0.4), Inches(5.3), Inches(12.35), Inches(1.3),
        [[("The tension: ", {"bold": True, "color": BLACK}),
          ("each denoising step costs one full network forward pass; a world model must render thousands of frames per training episode. DIAMOND's trick is to be stable enough that 3 steps suffice — and it even samples at only ", {}),
          ("~10 FPS", {"bold": True}),
          (" with 3 NFE per frame.", {})]],
        size=14.5)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 6 — Visual consistency: IRIS vs DIAMOND
# =====================================================================
s = add_slide()
title_bar(s, "The Core Result: Consistent Videos, Game by Game", kicker="5 / 11")
add_image(s, os.path.join(FIGS, "fig5_iris.png"), Inches(0.35), Inches(1.1), w=Inches(6.0))
add_image(s, os.path.join(FIGS, "fig5_diamond.png"), Inches(6.55), Inches(1.1), w=Inches(6.0))
textbox(s, Inches(0.35), Inches(4.75), Inches(6.0), Inches(0.35),
        "IRIS (discrete tokens) — inconsistencies in white boxes",
        size=13.5, bold=True, color=RED, align=PP_ALIGN.CENTER)
textbox(s, Inches(6.55), Inches(4.75), Inches(6.0), Inches(0.35),
        "DIAMOND (diffusion) — the same details stay consistent",
        size=13.5, bold=True, color=GREEN, align=PP_ALIGN.CENTER)
bullet_box(s, Inches(0.55), Inches(5.25), Inches(12.35), Inches(1.7),
           [[("IRIS flickers: ", {"bold": True, "color": RED}),
             ("an enemy becomes a reward and back (Asterix); bricks and score drift (Breakout); road rewards vanish (Road Runner). Just a few pixels — but the agent learns from exactly those pixels.", {})],
            [("DIAMOND stays faithful: ", {"bold": True, "color": GREEN}),
             ("same resolution (64\u00D764), fewer parameters, and only 3 NFE/frame vs 16 for IRIS — the consistency is not bought with more compute.", {})],
            [("Consequence: ", {"bold": True}),
             ("the agent targets rewards and avoids enemies more reliably → higher scores on precisely these games.", {})]],
           size=14.5, gap=5)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 7 — Benchmark results
# =====================================================================
s = add_slide()
title_bar(s, "Atari 100k: A New Best Among World-Model Agents", kicker="6 / 11")
# left bar chart
add_image(s, os.path.join(FIGS, "fig2_bars.png"), Inches(0.4), Inches(1.25), w=Inches(5.6))
textbox(s, Inches(0.4), Inches(4.5), Inches(5.6), Inches(0.4),
        "Human-normalized score (HNS), mean & IQM", size=12, color=GRAY, align=PP_ALIGN.CENTER)
# right key numbers
card(s, Inches(6.35), Inches(1.25), Inches(6.55), Inches(1.55), fill=NAVY)
textbox(s, Inches(6.6), Inches(1.42), Inches(6.1), Inches(1.2),
        [[("Mean HNS 1.46", {"size": 34, "bold": True, "color": WHITE})],
         [("superhuman on average — a new best among agents trained entirely inside a world model", {"size": 13, "color": RGBColor(0xC9, 0xD6, 0xE8)})]])
bullet_box(s, Inches(6.6), Inches(3.1), Inches(6.2), Inches(3.4),
           [["11 of 26 games superhuman (vs 10 for STORM/DreamerV3; 8 IRIS; 1 SimPLe)."],
            ["IQM 0.64 — on par with STORM, above all other baselines."],
            [("Biggest wins where tiny details decide: ", {}),
             ("Asterix (3698 vs 1028 STORM), Breakout (132.5 vs 83.7 IRIS), Road Runner (20673).", {"bold": True})],
            ["Setup: 100k env steps (~2 h gameplay) per game, 5 seeds; ~2.9 days/run on one RTX 4090."]],
           size=14, gap=6)
textbox(s, Inches(6.6), Inches(6.6), Inches(6.2), Inches(0.6),
        [[("Take-away: ", {"bold": True, "color": NAVY}),
          ("with agent designs held similar, the score gap traces back to the world model's visual consistency.", {"color": BLACK})]],
        size=14)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 8 — Pixel drift
# =====================================================================
s = add_slide()
title_bar(s, "Stability, Measured: Pixel Drift over 1000 Steps", kicker="7 / 11")
add_image(s, os.path.join(FIGS, "fig8_drift.png"), Inches(0.4), Inches(1.2), w=Inches(7.6))
card(s, Inches(8.4), Inches(1.2), Inches(4.5), Inches(3.4))
textbox(s, Inches(8.6), Inches(1.35), Inches(4.1), Inches(0.45),
        [[("Quantifying compounding error", {"size": 17, "bold": True, "color": NAVY})]])
bullet_box(s, Inches(8.6), Inches(1.85), Inches(4.1), Inches(2.6),
           [["Breakout: 1000-step imagined rollouts from the same frame + same action sequence (400 expert refs)."],
            [("DDPM drifts ", {"bold": True}),
             ("more and more; even 10 denoising steps stay worse than EDM with 1.", {})],
            [("EDM's residual drift ", {"bold": True}),
             ("is trajectory difference, not the pathological color shift seen in DDPM.", {})]],
           size=12.5, gap=5)
textbox(s, Inches(0.4), Inches(5.55), Inches(12.4), Inches(1.2),
        [[("Why this matters for the talk's theme: ", {"bold": True, "color": NAVY}),
          ("\"video consistency\" is not aesthetics. In a world model, every generated frame is a training sample for the agent. Frame-to-frame inconsistency is label noise for policy learning — and it compounds with rollout length.", {})]],
        size=15)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 9 — Scaling: CS:GO / driving
# =====================================================================
s = add_slide()
title_bar(s, "Scaling Up: An Interactive Neural Game Engine", kicker="8 / 11")
add_image(s, os.path.join(FIGS, "fig6_csgo.png"), Inches(0.35), Inches(1.15), w=Inches(7.4))
textbox(s, Inches(0.35), Inches(4.15), Inches(7.4), Inches(0.4),
        "Humans playing inside DIAMOND's diffusion world model (CS:GO)",
        size=12, color=GRAY, align=PP_ALIGN.CENTER)
card(s, Inches(8.15), Inches(1.15), Inches(4.75), Inches(3.35))
bullet_box(s, Inches(8.35), Inches(1.3), Inches(4.35), Inches(3.1),
           [[("Trained only on static footage ", {"bold": True}),
             ("— no RL, no engine: 150k frames of CS:GO (Dust II, 64\u00D764) and 3.6 h of motorway driving.", {})],
            [("People ", {"bold": True}),
             ("played it live with keyboard & mouse — stable over minutes of interactive rollout.", {})],
            [("FVD 34.8 on CS:GO ", {"bold": True, "color": GREEN}),
             ("vs 85.7 for IRIS (K = 64) and 509.1 for DreamerV3; LPIPS 0.107 vs 0.116 / 0.173.", {})],
            [("Driving: FVD 80.3 ", {"bold": True, "color": GREEN}),
             ("(IRIS 276.9, DreamerV3 733.7) — coherent, actionable video from real footage.", {})]],
           size=12.5, gap=6)
textbox(s, Inches(0.4), Inches(4.75), Inches(12.4), Inches(0.6),
        [[("Same recipe, richer domain: ", {"bold": True}),
          ("the same EDM diffusion world model generalizes from 2D arcade pixels to 3D first-person environments — a step toward world models as general video-consistent environment simulators.", {})]],
        size=14.5)
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 10 — Limitations
# =====================================================================
s = add_slide()
title_bar(s, "Limitations and Open Questions", kicker="9 / 11")
lims = [
    ("Resolution & fidelity", "64\u00D764 images — far from real visual richness. Video consistency at scale is still open."),
    ("Sample efficiency of the model itself", "The agent is sample-efficient; the diffusion world model is not. Training DIAMOND took ~1.03 GPU-years across the benchmark."),
    ("Speed", "3 NFE/frame ≈ 10 FPS on Atari; interactive use required stochastic sampling & more steps. Real-time, high-res diffusion world models remain costly."),
    ("Single-task scope", "One world model per game/environment — no cross-environment generalization or open-ended \"one world\" claim."),
    ("Consistency ≠ physics", "Rollouts are visually consistent; they are not physically grounded. Long-horizon drift still exists (Fig. 8) — an active research frontier."),
]
y = 1.2
for head, body in lims:
    rect(s, Inches(0.55), Inches(y), Inches(0.18), Inches(0.9), fill=RED)
    textbox(s, Inches(0.95), Inches(y), Inches(3.1), Inches(0.9),
            [[(head, {"size": 15.5, "bold": True, "color": NAVY})]], anchor=MSO_ANCHOR.TOP)
    textbox(s, Inches(4.15), Inches(y), Inches(8.65), Inches(0.9),
            body, size=13.5, color=BLACK)
    y += 1.08
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 11 — Takeaways
# =====================================================================
s = add_slide()
title_bar(s, "What to Remember", kicker="10 / 11")
takeaways = [
    ("Consistency is the bottleneck", "Discrete-token world models lose few-pixel visual details; those details are exactly what the agent's reward signal depends on."),
    ("Diffusion fixes it", "A continuous diffusion world model (EDM) preserves visual details and stays stable over long rollouts — no quantization bottleneck."),
    ("Consistency → performance", "Mean HNS 1.46, superhuman on 11/26 Atari-100k games; the gains concentrate where visual detail matters."),
    ("It scales beyond games", "CS:GO FVD 34.8 and interactive human play; motorway driving FVD 80.3 — a general recipe for consistent video world models."),
    ("Open frontier", "Resolution, speed, sample efficiency, physical grounding — world-model video consistency is still a live research area."),
]
y = 1.3
for i, (head, body) in enumerate(takeaways, 1):
    rect(s, Inches(0.55), Inches(y), Inches(0.62), Inches(0.62), fill=NAVY)
    textbox(s, Inches(0.55), Inches(y + 0.04), Inches(0.62), Inches(0.55),
            str(i), size=22, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    textbox(s, Inches(1.45), Inches(y - 0.02), Inches(4.6), Inches(1.0),
            [[(head, {"size": 16.5, "bold": True, "color": NAVY})]], anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, Inches(6.3), Inches(y - 0.02), Inches(6.5), Inches(1.0),
            body, size=13.5, color=BLACK, anchor=MSO_ANCHOR.MIDDLE)
    y += 1.12
footer(s, "World Models and Video Consistency — DIAMOND")

# =====================================================================
# Slide 12 — Thanks / references
# =====================================================================
s = add_slide()
rect(s, 0, 0, SW, SH, fill=NAVY)
textbox(s, Inches(1.0), Inches(1.9), Inches(11.33), Inches(1.0),
        [[("Thank You", {"size": 44, "bold": True, "color": WHITE})]],
        align=PP_ALIGN.CENTER)
textbox(s, Inches(1.0), Inches(2.9), Inches(11.33), Inches(0.5),
        [[("World Models and Video Consistency — DIAMOND", {"size": 18, "color": RGBColor(0xC9, 0xD6, 0xE8)})]],
        align=PP_ALIGN.CENTER)
rect(s, Inches(5.42), Inches(3.6), Inches(2.5), Pt(2.2), fill=ORANGE)
textbox(s, Inches(1.0), Inches(4.0), Inches(11.33), Inches(2.4),
        [[("Paper: E. Alonso, A. Jelley, V. Micheli, A. Kanervisto, A. Storkey, T. Pearce, F. Fleuret.", {"size": 13.5, "color": RGBColor(0xD9, 0xE1, 0xEE)})],
         [("\"Diffusion for World Modeling: Visual Details Matter in Atari.\" NeurIPS 2024. arXiv:2405.12399", {"size": 13.5, "color": RGBColor(0xD9, 0xE1, 0xEE)})],
         [("Project page & playable world models: diamond-wm.github.io  \u00B7  Code: github.com/eloialonso/diamond", {"size": 13.5, "color": RGBColor(0xD9, 0xE1, 0xEE)})],
         [("", {"size": 6})],
         [("All figures reproduced from the paper (arXiv:2405.12399).", {"size": 11.5, "color": RGBColor(0x8F, 0x9F, 0xB8)})]],
        align=PP_ALIGN.CENTER)

OUT = os.path.join(BASE, "world-model-video-consistency-diamond.pptx")
prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))
