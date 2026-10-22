"""Build extensive bilingual Q&A DOCX for the DIAMOND talk."""

import docx
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x49, 0x7D)
RED = RGBColor(0xC0, 0x50, 0x4D)
GREEN = RGBColor(0x3B, 0x7A, 0x3B)
GRAY = RGBColor(0x59, 0x59, 0x59)
ORANGE = RGBColor(0xE8, 0x6A, 0x17)
BLACK = RGBColor(0x1A, 0x1A, 0x1A)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin = sec.bottom_margin = Cm(2.0)

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def p(text='', size=10, bold=False, italic=False, color=BLACK, align=None,
      space_after=4, space_before=0):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(space_after)
    par.paragraph_format.space_before = Pt(space_before)
    if align:
        par.alignment = align
    r = par.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = 'Calibri'
    r.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    return par


def h1(text):
    par = p(text, size=15, bold=True, color=NAVY, space_before=12, space_after=5)
    pPr = par._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:space'), '2'); bottom.set(qn('w:color'), '1F497D')
    pbdr.append(bottom)
    pPr.append(pbdr)
    return par


def h2(text):
    return p(text, size=12, bold=True, color=NAVY, space_before=8, space_after=3)


def q(zh, en):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(6)
    par.paragraph_format.space_after = Pt(2)
    r = par.add_run('Q' + zh + ' ')
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = RED
    r2 = par.add_run(en)
    r2.font.bold = True
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = GRAY


def a(zh, en):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(5)
    par.paragraph_format.left_indent = Cm(0.4)
    r = par.add_run('A' + zh + ' ')
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = GREEN
    r2 = par.add_run(en)
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = GRAY


def tip(text):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(4)
    par.paragraph_format.left_indent = Cm(0.4)
    r = par.add_run('💡 ')
    r.font.size = Pt(10)
    r2 = par.add_run(text)
    r2.font.size = Pt(10)
    r2.font.italic = True
    r2.font.color.rgb = ORANGE


# ================= TITLE =================
p('DIAMOND 演讲答辩 · 详尽问答手册', size=19, bold=True, color=NAVY,
  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p('Extensive Bilingual Q&A — Diffusion for World Modeling: Visual Details Matter in Atari (NeurIPS 2024)',
  size=10.5, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p('七个板块：架构 / 细节技术 / 结果质疑 / 改进方案 / 未来方向 / 应用 / 对比与快问快答 · 共 60+ 问',
  size=9.5, italic=True, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

# ================= 1 =================
h1('一、架构询问 Architecture Questions')

h2('1.1 扩散世界模型本身')
q('为什么选 2D U-Net 而不是 3D U-Net 或 DiT？',
  'Why a 2D U-Net instead of a 3D U-Net or a DiT?')
a('DIAMOND 逐帧自回归生成：每步只预测“下一帧”，把过去 L=4 帧按通道拼到输入上，'
  '因此单帧 2D 卷积就够，不需要 3D 卷积批量生成一段视频（附录 M 里对比了 3D U-Net，'
  '帧堆叠 2D U-Net 更稳更快）。DiT 是后续工作（如 GameNGen）的路线，论文发表时 U-Net 是低分辨率下的自然选择。',
  'DIAMOND generates frames autoregressively: each step predicts only the next frame, with the past L=4 frames '
  'concatenated channel-wise onto the input, so a per-frame 2D CNN suffices. Appendix M compares a 3D U-Net that '
  'diffuses a whole block of frames at once; the 2D frame-stacked U-Net was more stable and cheaper. DiT-style '
  'transformers are the route taken by later work (e.g., GameNGen); at 64x64 the U-Net was the natural choice.')
tip('答这类题的要害：先说清“条件方式”（帧堆叠），再点“自回归 vs 整段生成”的区别。')

q('模型多大？跟基线比如何？',
  'How large is the model, and how does it compare with baselines?')
a('Atari 版 D_θ 约 4M 参数（U-Net：残差块层数 [2,2,2,2]、通道 [64,64,64,64]、条件维度 256）；'
  '整个 DIAMOND（含 R 与 actor-critic）13M 参数——比 IRIS 的 30M、DreamerV3 的 18M 都少（Table 4）。'
  'CS:GO 版扩到 381M（含 51M 超分器）。',
  'The Atari diffusion model D_theta has ~4M parameters (U-Net with residual-block layers [2,2,2,2], channels '
  '[64,64,64,64], conditioning dim 256). The full DIAMOND (including the reward/termination model and actor-critic) '
  'is 13M — fewer than IRIS (30M) and DreamerV3 (18M), see Table 4. The CS:GO variant scales to 381M '
  '(including a 51M upsampler).')

q('过去的观测和动作是怎么进入模型的？',
  'How are past observations and actions fed into the model?')
a('观测：帧堆叠（frame stacking）——把最近 L=4 帧直接按通道拼到“带噪的下一帧”上；'
  '动作与扩散时间 τ：都通过残差块里的自适应组归一化（adaptive group normalization）注入，'
  '即用动作/时间的嵌入去调制归一化层的 scale 与 shift（附录 D、Table 2）。',
  'Observations: frame stacking — the last L=4 frames are concatenated channel-wise with the noised next frame. '
  'Actions and the diffusion time tau: both are injected via adaptive group normalization inside the residual blocks '
  '(their embeddings modulate the normalization scale/shift). See Appendix D and Table 2.')
tip('注意区分两条“时间轴”：环境时间 t（自回归帧序）与扩散时间 τ（单帧内去噪进度）。二者都是条件。')

q('L（条件帧数）取多少？为什么？',
  'What is L (the number of conditioning frames) and why?')
a('Atari 用 L=4；3D 实验用 L=6。L 是“记忆窗口”：越大看到的过去越长，但输入与显存开销越大。'
  '论文在 3D 实验里直接比较了帧堆叠与交叉注意力两种条件方式，帧堆叠反而更好（FVD 34.8 vs 81.4）——'
  '作者猜测逐帧直接输入带来的归纳偏置更适合自回归生成。',
  'L=4 for Atari; L=6 for the 3D experiments. L is the memory window: larger L sees more history but costs more '
  'input channels and memory. In the 3D experiments frame stacking beat cross-attention (FVD 34.8 vs 81.4); the '
  'authors conjecture the per-frame inductive bias suits autoregressive generation.')

q('为什么不用一个显式的记忆/循环模块（如 RNN）？',
  'Why no explicit memory module (e.g., an RNN) in the world model?')
a('帧堆叠本身就是最简单的记忆机制。论文“Limitations”里明确说这是 minimal mechanism，'
  '建议后续用 autoregressive transformer（如 DiT 式）整合更长的环境时间记忆；'
  '附录 M 的 cross-attention 初步实验没带来收益，所以保持简单。',
  'Frame stacking is itself the minimal memory mechanism. The Limitations section says exactly this and suggests '
  'integrating an autoregressive transformer over environment time (DiT-style) for longer-term memory; the early '
  'cross-attention experiments in Appendix M did not help, so they kept it simple.')

h2('1.2 奖励/终止模型与智能体')
q('奖励和终止为什么要单独一个模型？',
  'Why is the reward/termination model separate?')
a('奖励/终止是标量预测问题，用一个轻量 CNN+LSTM（残差块 [2,2,2,2]、通道 32、LSTM 维度 512，'
  '动作经自适应组归一化注入）就够了，没必要让生成模型同时输出。论文把“把 reward 预测并入扩散模型”'
  '列为 future work——从扩散模型里抽表示再预测并不 trivial（Luo et al. 2023; Xu et al. 2023）。',
  'Reward/termination are scalar prediction problems; a light CNN+LSTM (blocks [2,2,2,2], channels 32, LSTM dim '
  '512, actions via adaptive group norm) suffices. The paper lists merging reward prediction into the diffusion model '
  'as future work — extracting representations from diffusion models is non-trivial (Luo et al. 2023; Xu et al. 2023).')

q('智能体（actor-critic）的结构和训练目标？',
  'What are the agent architecture and training objectives?')
a('策略 π 与价值 V 共享 CNN+LSTM（残差块 [1,1,1,1]、通道 [32,32,64,64]、LSTM 维度 512），只有最后一层分开。'
  '策略用 REINFORCE + 价值基线（减少梯度方差）+ 熵正则（η=0.001）；价值网络用 λ-returns（λ=0.95）做回归目标，'
  '期望平方误差（附录 F，Eq. 14-16）。想象视野 H=15，折扣 γ=0.985。',
  'Policy pi and value V share a CNN+LSTM (blocks [1,1,1,1], channels [32,32,64,64], LSTM dim 512); only the last '
  'layer differs. The policy is trained with REINFORCE plus a value baseline (variance reduction) and an entropy bonus '
  '(eta=0.001); the value net regresses lambda-returns (lambda=0.95) with expected squared error (Appendix F, Eqs. '
  '14-16). Imagination horizon H=15, discount gamma=0.985.')
tip('如果被追问为什么这么“朴素”：因为世界模型提供无限便宜的 on-policy 样本，REINFORCE 就够了，'
    '不需要 PPO 那套复杂的 off-policy 修正。')

q('“burn-in”是什么意思？',
  'What does "burn-in" mean?')
a('开始想象前，先用真实缓冲里的最近 L=4 帧把 R 和 actor-critic 的 LSTM 隐藏态/细胞态跑热，'
  '再进入纯想象。否则 LSTM 从零隐藏态出发会给出错误的初始预测。',
  'Before imagination, the most recent L=4 real frames are fed through R and the actor-critic to warm up their LSTM '
  'hidden/cell states (Kapturowski et al. 2018). Otherwise the LSTM starts from zero state and makes bad initial '
  'predictions.')

h2('1.3 训练循环与算力')
q('训练循环长什么样？',
  'Describe the training loop.')
a('Algorithm 1：每 epoch 用当前策略（ε=0.01 贪心）收集 100 环境步放入 replay 缓冲 → '
  '分别更新扩散模型（400 步/epoch）、奖励终止模型（400 步）、actor-critic（400 步，每步含 15 步想象 rollout）→ 重复 1000 epochs。'
  '批大小 32，AdamW（lr 1e-4，D 与 R 的 weight decay 1e-2，actor-critic 为 0）。',
  'Algorithm 1: each epoch collects 100 environment steps with the current policy (epsilon-greedy 0.01) into a replay '
  'buffer, then updates the diffusion model (400 steps/epoch), the reward/termination model (400), and the actor-critic '
  '(400, each containing a 15-step imagined rollout), repeated for 1000 epochs. Batch size 32, AdamW with lr 1e-4; '
  'weight decay 1e-2 for D and R, 0 for the actor-critic.')

q('一次训练要多久？时间都花在哪？',
  'How long does training take, and where does the time go?')
a('单卡 RTX 4090：每个 run 约 2.9 天（2.5 天训练 + 0.4 天收集/评估/存点），全基准 5 种子×26 游戏 = 1.03 GPU-years。'
  '分解（Table 5）：一次完整更新 543ms = 扩散 88ms + 奖励 115ms + actor-critic 340ms；'
  'actor-critic 里一次想象步 20.4ms（其中预测下一帧 12.7ms = 3 步去噪 × 4.2ms）。'
  '可见“世界模型预测”是想象训练的计算核心。',
  'On a single RTX 4090: ~2.9 days per run (2.5 days training + 0.4 for collection/eval/checkpointing); the full '
  'benchmark is 5 seeds x 26 games = 1.03 GPU-years. Breakdown (Table 5): one full update = 543ms = diffusion 88ms + '
  'reward 115ms + actor-critic 340ms; one imagination step is 20.4ms, of which next-frame prediction is 12.7ms = 3 '
  'denoising steps x 4.2ms. World-model prediction dominates imagination training.')

# ================= 2 =================
h1('二、细节技术询问 Detailed Technical Questions')

h2('2.1 扩散与采样')
q('DDPM 为什么会漂移？请从数学上讲清。',
  'Why does DDPM drift? Explain mathematically.')
a('DDPM 训练网络 ξ 预测“所加的噪声 ε”。当噪声占主导（σ_noise ≫ σ_data）时，最优预测退化为 ξ(x) → x，'
  '即网络学的是“恒等映射”。于是采样起始（纯噪声端）的 score 估计极差：score s(x) = -ε/σ ≈ 0 或方向错误。'
  '反过来，EDM 的预条件化把网络目标写成 (x₀ - c_skip·x)/c_out，σ 大时 c_skip → 0，'
  '目标退化为“直接预测干净图 x₀”——几乎没有信号时也给出有意义的 score 估计（论文 §5.1、Eq. 7）。',
  'DDPM trains the network xi to predict the added noise epsilon. When noise dominates (sigma_noise >> sigma_data) the '
  'optimal prediction collapses to the identity map xi(x) -> x, so at the start of sampling (the pure-noise end) the '
  'score estimate is terrible — score s(x) = -epsilon/sigma is near zero or wrongly oriented. In EDM, preconditioning '
  'writes the training target as (x0 - c_skip x)/c_out; for large sigma, c_skip -> 0, so the target becomes "predict '
  'the clean image x0" — a meaningful score estimate even with almost no signal (Sec. 5.1, Eq. 7).')
tip('这题大概率被问。记住三要素：恒等坍缩 → 起始 score 差 → 误差沿 rollout 累积。')

q('为什么是 Euler 采样而不是 Heun/DPM-Solver 等高阶方法？',
  'Why Euler sampling instead of Heun or DPM-Solver?')
a('论文“codebase supports a variety of sampling schemes”，最终选 Euler：'
  '高阶求解器每步要多算 NFE，而世界模型对推理成本极度敏感（3 步 vs 2 步都会显著影响训练吞吐）。'
  '在 n=3 这种极端低 NFE 设定下，Euler 已够用，收益被复杂度抵消。',
  'The codebase supports several schemes; Euler was chosen because higher-order solvers cost extra NFEs per step, and '
  'the world model is extremely inference-sensitive. At n=3 the quality gain of higher-order methods does not justify '
  'the added cost and complexity.')

q('去噪步数 n 的权衡到底是什么？',
  'What exactly is the trade-off in the number of denoising steps?')
a('n=1：单步预测是最优重建的“期望”（等价于 L2 自编码器）；后验多模态时，期望落在模态之间 → 糊帧、'
  '不在分布内（Figure 4 上行，Boxing）。n≥3：迭代求解驱动采样收敛到某个具体模态 → 清晰一致（下行）。'
  '代价：每步一次网络前向。消融：Top-10 游戏 mean HNS 3.05（n=3）→ 1.96（n=1）。'
  '所以选 n=3 是“一致性 vs 速度”的折中。',
  'n=1: the single-step prediction is the expectation over reconstructions (equivalent to an L2 autoencoder); when the '
  'posterior is multimodal the expectation sits between modes — blurry, out-of-distribution frames (Fig. 4 top, Boxing). '
  'n>=3: the iterative solver drives sampling into one mode — crisp, consistent frames (bottom). Cost: one forward pass '
  'per step. Ablation: mean HNS over the top-10 games drops from 3.05 (n=3) to 1.96 (n=1). n=3 is the consistency-vs-speed '
  'sweet spot.')

q('为什么不用 DDIM/一致性模型（consistency models）一步生成？',
  'Why not DDIM or consistency models for one-step generation?')
a('DDIM 仍属 DDPM 系的目标（预测噪声），漂移问题不变；且一致性模型（Song et al. 2023）在 DIAMOND 写作时'
  '刚出现，尚未验证其长程稳定性。现在这是活跃方向：少步/一步采样扩散世界模型正是后续工作（如 '
  'latent world models 与蒸馏路线）在做的事。',
  'DDIM shares the DDPM noise-prediction objective, so the drift problem remains. Consistency models (Song et al. 2023) '
  'were just emerging at the time and their long-rollout stability was untested. This is now an active direction: '
  'few-step/one-step diffusion world models via distillation or latent diffusion.')

q('训练时噪声水平 σ 怎么采样？',
  'How is the noise level sigma sampled during training?')
a('按 EDM 的设置：log σ 从对数正态分布 N(P_mean, P_std²) 采样（论文 Algorithm 1），'
  '把训练集中在中等噪声区——因为目标在噪声极值处方差大。',
  'Following EDM: log sigma is sampled from a log-normal distribution N(P_mean, P_std^2) (Algorithm 1), concentrating '
  'training on medium noise levels, where the objective has manageable variance.')

h2('2.2 一致性与漂移')
q('怎么定量测量“视频一致性”？',
  'How is "video consistency" measured quantitatively?')
a('三层证据：① 像素漂移（Figure 8）：同一初始帧 + 同一动作序列下，1000 步想象轨迹与 400 条专家参考轨迹的'
  '平均像素差，看随 rollout 长度如何增长；② FVD（Fréchet Video Distance）：生成视频与真实视频的分布距离'
  '（CS:GO 34.8 vs IRIS-K64 85.7 vs DreamerV3 509.1）；③ FID/LPIPS 辅助单帧与感知质量。',
  'Three levels: (1) pixel drift (Fig. 8) — for the same start frame and action sequence, the average pixel difference '
  'between 1000-step imagined trajectories and 400 expert reference trajectories, plotted against rollout length; '
  '(2) FVD — distribution distance between generated and real videos (CS:GO 34.8 vs IRIS-K64 85.7 vs DreamerV3 509.1); '
  '(3) FID/LPIPS as auxiliary single-frame/perceptual metrics.')

q('EDM 的残余漂移从哪来？能不能彻底消除？',
  'Where does EDM\'s residual drift come from? Can it be eliminated?')
a('残余漂移来自“轨迹分岔”：扩散采样是随机的，同一动作序列下模型可能想象出一条同样合法但不同的玩法，'
  '逐帧对齐后自然有像素差（Figure 8 的 EDM 曲线是内容漂移而非渲染崩塌）。'
  '理论上不能完全消除——环境本身有随机性（stochasticity），这正是扩散模型“采样”语义的体现；'
  '能做的是让它不增长、不崩塌，DIAMOND 做到了。',
  'The residual drift is trajectory divergence: diffusion sampling is stochastic, so under the same action sequence the '
  'model may imagine an equally valid but different play; frame-wise alignment then yields pixel differences. This is '
  'content drift, not rendering collapse. It cannot be fully eliminated because environments are stochastic — it is the '
  'sampling semantics of diffusion. What DIAMOND achieves is that it does not grow or collapse.')

q('为什么帧堆叠比交叉注意力好？这不是反直觉吗？',
  'Why is frame stacking better than cross-attention? Isn\'t that counter-intuitive?')
a('作者也认为 surprising（附录 M）。猜测：自回归逐帧生成时，把历史帧“原样拼进输入”给了模型很强的'
  '逐像素对齐归纳偏置，利于保持一致性；交叉注意力把历史压成抽象特征，反而丢了这种空间对齐。'
  '量化：CS:GO FVD 34.8 vs 81.4、驾驶 FVD 80.3 vs 299.9。总体排序：DIAMOND 帧堆叠 > DIAMOND 交叉注意力'
  '≈ IRIS-64 > IRIS-16 > DreamerV3。',
  'The authors find it surprising too (Appendix M). Conjecture: in autoregressive generation, feeding history frames '
  'pixel-aligned into the input gives the model a strong spatial-alignment inductive bias that preserves consistency, '
  'while cross-attention compresses history into abstract features and loses that alignment. Numbers: CS:GO FVD 34.8 vs '
  '81.4; driving 80.3 vs 299.9. Ordering: DIAMOND frame-stack > DIAMOND cross-attn ~ IRIS-64 > IRIS-16 > DreamerV3.')

h2('2.3 表示与动作')
q('为什么说“离散 token 丢细节”？细节丢在哪一步？',
  'Why do discrete tokens lose details, and where exactly?')
a('丢在 VQ-VAE 的编码-量化-解码全过程：把 64×64 图像压成 K=16 个 token 是一种强有损压缩，'
  '每个 token 要同时承载空间位置与语义；量化误差优先“牺牲”小物体、细纹理、高频变化——'
  '而 Atari 里敌人、奖励、子弹、得分恰好都是几个像素的实体。重建时这些实体就可能错位、互换、消失。'
  'IRIS 的想象轨迹（Figure 5）直接展示了敌人↔奖励互换。',
  'The loss happens across the VQ-VAE encode-quantize-decode pipeline: compressing a 64x64 image into K=16 tokens is '
  'heavy lossy compression where each token must carry both spatial position and semantics; quantization error '
  'sacrifices small objects, fine textures, and high-frequency change first — and in Atari, enemies, rewards, bullets and '
  'scores are exactly few-pixel entities. Reconstruction can then misplace, swap or drop them, as IRIS trajectories '
  'show in Figure 5.')

q('DIAMOND 用的“连续表示”到底是什么？跟 Stable Diffusion 的 latent 一样吗？',
  'What continuous representation does DIAMOND use? Is it like Stable Diffusion\'s latent?')
a('注意：DIAMOND 直接在“像素空间”做扩散（64×64×3），没有用 VAE 压缩成低维 latent——'
  '它的“连续”指扩散潜变量（噪声扰动后的像素/去噪轨迹）是连续的，而不是图像被量化成 token。'
  'Stable Diffusion 是 latent diffusion（在 VAE 潜空间扩散）；把 latent diffusion 用到世界模型'
  '是 DIAMOND 之后的改进方向（更省算力）。',
  'DIAMOND diffuses directly in pixel space (64x64x3) — no VAE compression into a low-dimensional latent. Its '
  '"continuity" refers to the diffusion latent (the noised/denoised pixels) being continuous, as opposed to quantized '
  'tokens. Stable Diffusion is latent diffusion (diffusing in a VAE latent); applying latent diffusion to world models '
  'is the post-DIAMOND efficiency direction.')

q('动作是怎么“进”扩散模型的？为什么用自适应组归一化？',
  'How do actions enter the diffusion model, and why adaptive group norm?')
a('把动作向量过一个嵌入层，然后在每个残差块的组归一化层，用该嵌入调制 scale（γ）和 shift（β）：'
  'y = GN(x) ⊙ γ(a) + β(a)。好处：条件是“全局调制”而非空间拼接，不会干扰图像的逐像素结构；'
  '扩散时间 τ 用同一机制注入（Table 2）。',
  'The action is embedded and modulates the scale (gamma) and shift (beta) of the group-normalization layer in every '
  'residual block: y = GN(x) * gamma(a) + beta(a). The condition acts as global modulation rather than spatial '
  'concatenation, so it does not disturb the per-pixel structure; the diffusion time tau is injected the same way '
  '(Table 2).')

q('为什么要做 reward clipping 和 frameskip？',
  'Why reward clipping and frameskip?')
a('都是 Atari 世界模型的标准操作：reward clipping 把奖励截到 {-1,0,1}，让奖励模型的分类预测（符号）'
  '稳定、跨游戏可比；frameskip=4 指每 4 帧取 1 帧 + 重复上一动作，降低序列长度与算力，'
  '同时让动作的影响在单帧上更明显。',
  'Both are standard Atari world-model practices: reward clipping to {-1,0,1} makes the reward model\'s sign '
  'classification stable and comparable across games; frameskip=4 keeps 1 of every 4 frames (repeating the last '
  'action), shrinking sequence length and compute while making action effects more visible in a single frame.')

# ================= 3 =================
h1('三、结果与实验质疑 Questions About Results & Experiments')

q('HNS 1.46 意味着什么？怎么算的？',
  'What does HNS 1.46 mean and how is it computed?')
a('HNS = (score - score_random) / (score_human - score_random)，把每款游戏映射到“随机=0、人类=1”的标尺，'
  '26 款游戏取均值。1.46 = 平均达到人类水平的 1.46 倍，即“平均意义上超人类 46%”。'
  '这是 Atari 100k 社区的标准指标（与 IQM 互补，IQM 去掉头尾 25% 更稳健：DIAMOND 0.64）。',
  'HNS = (score - random_score) / (human_score - random_score), mapping each game onto a "random=0, human=1" scale, '
  'then averaged over 26 games. 1.46 = on average 46% above human level. This is the standard Atari-100k metric; IQM '
  '(trimming the top/bottom 25%) is the robust complement, where DIAMOND scores 0.64.')

q('DIAMOND 的“超人类”集中在哪些游戏？失败在哪些？',
  'Where is DIAMOND superhuman, and where does it fail?')
a('11/26 超人类。大胜集中在细节敏感游戏：Asterix 3698（STORM 1028）、Breakout 132.5（IRIS 83.7）、'
  'Road Runner 20673（全场最高）、Assault 1526、Kangaroo 5382、CrazyClimber 99168。'
  '弱项：BankHeist 19.7（DreamerV3 649）、BattleZone 4702（STORM 13540）、PrivateEye 114.3（STORM 7781）、'
  'Seaquest 551。失败原因论文没有逐游戏分析，合理推测：需要长程记忆/计数/稀疏奖励的游戏对“帧级一致性”'
  '不敏感，扩散世界的开销反而没带来收益。',
  'Superhuman on 11/26, concentrated in detail-sensitive games: Asterix 3698 (STORM 1028), Breakout 132.5 (IRIS 83.7), '
  'Road Runner 20673 (best on the board), Assault 1526, Kangaroo 5382, CrazyClimber 99168. Weak spots: BankHeist 19.7 '
  '(DreamerV3 649), BattleZone 4702 (STORM 13540), PrivateEye 114.3 (STORM 7781), Seaquest 551. The paper does not '
  'analyze these per game; plausible: games needing long memory/counting/sparse rewards gain little from frame-level '
  'consistency, and the diffusion cost buys nothing there.')

q('会不会只是 5 个种子碰运气？',
  'Is this just luck from 5 seeds?')
a('有方差，但结论稳健：① 全基准每个游戏都跑满 5 种子，报告均值；② 1.46 vs STORM 1.266 的差距'
  '（约 0.19 HNS）远超典型种子波动；③ 结构性的证据是“赢在细节敏感游戏”这一模式与视觉分析（Figure 5）'
  '互相印证；④ 与人类/基线一致的评测协议（2 小时体验、官方 human scores）。',
  'There is variance, but the conclusion is robust: (1) every game uses all 5 seeds and reports the mean; (2) the gap '
  'to STORM (1.46 vs 1.266, ~0.19 HNS) far exceeds typical seed noise; (3) the pattern "wins where details matter" '
  'cross-validates the visual analysis (Fig. 5); (4) the evaluation protocol (2h experience, official human scores) is '
  'identical across methods.')

q('公平吗？扩散世界模型每帧更贵，是不是在“算力作弊”？',
  'Is the comparison fair given diffusion costs more per frame?')
a('公平性论文自己做了正面回应：同分辨率（64×64）、DIAMOND 参数更少（13M vs IRIS 30M）、'
  '每帧 NFE 更少（3 vs IRIS 16）、训练时间更短（2.9 天 vs IRIS 4.1 天，Table 4）。'
  '每帧单次前向更大是事实，但总训练算力并不占优，所以“算力作弊”不成立。',
  'The paper answers this head-on: same resolution (64x64), fewer parameters (13M vs IRIS 30M), fewer NFE per frame '
  '(3 vs IRIS 16), and shorter training time (2.9 days vs IRIS 4.1 days, Table 4). Each forward pass is bigger, but the '
  'total training compute is not larger, so the "compute cheating" objection does not hold.')

q('IQM 只跟 STORM 打平，怎么解释？',
  'IQM only ties STORM — how do you explain that?')
a('IQM 对离群游戏稳健：DIAMOND 在少数游戏（BankHeist、BattleZone、PrivateEye）明显弱，拉低了 IQM；'
  '均值指标则被 Road Runner、CrazyClimber 等大分拉动。两个指标描述同一分布的两个侧面，'
  '报告两者恰是严谨做法。答辩口径：均值第 1 + IQM 并列第 1 + 参数/时间更少 = 综合占优。',
  'IQM is robust to outlier games: DIAMOND is clearly weaker on a few (BankHeist, BattleZone, PrivateEye), which drags '
  'IQM down, while the mean is lifted by huge scores like Road Runner and CrazyClimber. The two metrics describe two '
  'sides of the same distribution — reporting both is the rigorous choice. Bottom line: best mean, tied-best IQM, with '
  'fewer parameters and less training time.')

q('像素漂移实验为什么要用“专家动作序列”而不是智能体自己的策略？',
  'Why use expert action sequences for the pixel-drift experiment?')
a('为了“控制变量”：如果让不同世界模型各自按自己的策略行动，轨迹会迅速分岔，像素差里会混入'
  '“策略不同”的噪声，无法归因于世界模型。固定同一组动作序列后，漂移只可能来自模型本身的误差累积。',
  'To isolate the world model: if each model rolled out with its own policy, trajectories would diverge for policy '
  'reasons and the pixel difference would confound model error with policy difference. Fixing the action sequence makes '
  'the drift attributable solely to the world model\'s compounding error.')

q('CS:GO 的 10Hz 是“实时”吗？够不够？',
  'Is 10Hz "real-time" for CS:GO, and is it enough?')
a('论文称 real-time neural game engine 是指“可交互游玩”意义上的实时（RTX 3090 上 10Hz，'
  '动态模型 3 步 + 上采样器 10 步 + 随机采样）。10Hz 对 FPS 游戏偏低（原生 60+Hz），'
  '但作为“世界模型作为可玩引擎”的概念验证已经足够。论文坦承多种失败模式（靠墙忘记状态、空中连跳被错误允许）。',
  '"Real-time" here means interactively playable (10Hz on an RTX 3090 with 3-step dynamics + 10-step upsampler + '
  'stochastic sampling), not 60Hz game-engine real-time. It is low for an FPS but sufficient as a proof-of-concept of a '
  'playable neural game engine. The paper is candid about failure modes (forgetting state near walls, wrongly allowing '
  'mid-air jumps).')

q('为什么 CS:GO 不做 RL，只测视觉质量？',
  'Why no RL in CS:GO — only visual quality?')
a('因为没有标准化的 CS:GO RL 协议/奖励定义（不像 Atari 有官方 human scores 和 100k 协议）。'
  '所以论文把世界模型“单独”当作生成模型评测（FVD/FID/LPIPS/采样率），展示其建模复杂 3D 环境的能力，'
  'RL 集成留给未来。',
  'There is no standardized CS:GO RL protocol or reward definition (unlike Atari\'s official human scores and 100k '
  'protocol). So the world model is evaluated standalone as a generative model (FVD/FID/LPIPS/sample rate) to show it '
  'can model complex 3D environments; RL integration is left to future work.')

# ================= 4 =================
h1('四、改进方案询问 Improvement Questions')

q('如果让你改进 DIAMOND，最先做什么？',
  'If you were to improve DIAMOND, what first?')
a('优先级排序（结合论文 Limitation + 后续工作）：① 换 latent diffusion（在 VAE 潜空间扩散），'
  '显著降算力、提分辨率（GameNGen 已示范）；② 把帧堆叠换成 transformer 记忆（DiT/自回归条件），'
  '解决长程记忆；③ 蒸馏成 1-2 步采样（一致性模型/蒸馏），缓解 3 NFE 瓶颈；'
  '④ 合并 reward/终止预测进扩散模型（论文列为 future work）；⑤ 连续动作空间适配（机器人）。',
  'In order (based on the paper\'s Limitations plus follow-up work): (1) latent diffusion (diffuse in a VAE latent) to cut '
  'compute and raise resolution — GameNGen demonstrated this; (2) replace frame stacking with transformer memory '
  '(DiT/autoregressive conditioning) for long-term memory; (3) distill to 1-2 step sampling (consistency models/'
  'distillation) to relieve the 3-NFE bottleneck; (4) merge reward/termination prediction into the diffusion model (the '
  'paper\'s stated future work); (5) adapt to continuous action spaces for robotics.')

q('能不能把 3 步再降到 1 步而不损失一致性？',
  'Can you reduce 3 steps to 1 without losing consistency?')
a('论文自己的答案：能，但要付出代价——n=1 的 mean HNS 从 3.05 跌到 1.96（Top-10）。'
  '真正可行的路线是“训练时多步、推理时蒸馏”：用 3 步模型当教师，蒸馏一个单步学生'
  '（或训练一致性模型），这是当前少步扩散的通用做法。',
  'The paper\'s own answer: yes, at a cost — mean HNS drops from 3.05 to 1.96 (top-10) at n=1. The viable route is '
  'train-many/infer-few: use the 3-step model as teacher to distill a one-step student (or train a consistency model), '
  'the standard few-step diffusion recipe.')

q('如何把分辨率从 64×64 提上去？',
  'How would you raise the resolution beyond 64x64?')
a('三条路：① latent diffusion（潜空间扩散，最主流）；② 级联/超分（DIAMOND 自己在 CS:GO 上'
  '已经用了 51M 上采样器，56×30 → 280×150）；③ patch 化 + transformer 骨干（DiT）。'
  '注意：分辨率不只是“画质”问题——小物体（敌人/奖励）在低分辨率下恰好只有几个像素，'
  '提分辨率本质是在给一致性上保险。',
  'Three routes: (1) latent diffusion — the mainstream answer; (2) cascade/upsampling — DIAMOND itself already used a '
  '51M upsampler for CS:GO (56x30 -> 280x150); (3) patchify + transformer backbone (DiT). Note resolution is not just '
  '"picture quality": small entities (enemies/rewards) are exactly a few pixels at low resolution, so raising resolution '
  'is itself a consistency insurance.')

q('动作空间是连续的怎么办（机器人）？',
  'What about continuous action spaces (robotics)?')
a('论文承认主评估限于离散控制。机制上并不难：动作本来就是连续向量经自适应组归一化注入，'
  '连续动作同样适用；真正的难点是连续控制任务的“世界模型误差成本”更高（接触、碰撞、高频动态），'
  '对一致性/物理合理性要求更严。这也是后续 latent world model + 机器人工作的方向。',
  'The paper acknowledges its main evaluation is discrete control. Mechanically it transfers: actions already enter as '
  'continuous vectors via adaptive group norm. The real difficulty is that continuous-control tasks punish world-model '
  'error harder (contacts, collisions, high-frequency dynamics), demanding stronger consistency/physical plausibility — '
  'the direction taken by later latent-world-model robotics work.')

q('可以把 DIAMOND 和 PPO/off-policy 结合吗？',
  'Can DIAMOND be combined with PPO/off-policy RL?')
a('可以，且没有冲突：世界模型只负责提供“环境”，想象数据本质是 on-policy（由当前策略生成），'
  '所以 DIAMOND 用 REINFORCE+基线就够。但把想象数据当成 off-policy 经验、上 PPO/SAC 的'
  'importance sampling 或 replay 复用，理论上可行，还能提高样本利用率——代价是超参与偏差风险。',
  'Yes, without conflict: the world model only provides the environment; imagined data is on-policy (generated by the '
  'current policy), so REINFORCE+baseline suffices. Using imagined data as off-policy experience with PPO/SAC-style '
  'importance sampling or replay reuse is theoretically possible and could raise sample utilization — at the cost of '
  'hyperparameter sensitivity and bias risk.')

# ================= 5 =================
h1('五、未来方向询问 Future Direction Questions')

q('DIAMOND 之后这个领域怎么演化的？',
  'How did the field evolve after DIAMOND?')
a('三条主线：① 高效化：latent diffusion world models（在 VAE 潜空间做世界模型）成为主流，'
  '代表性的有后续的 GameNGen（DOOM，潜空间扩散模拟器）、IRIS 团队与各家的 latent 世界模型；'
  '② 规模化：Sora/Genie 2/Genie 3 把“视频生成作为世界模型”推向开放世界，'
  '“world simulator”概念升温；③ 评测化：出现了大量“视频世界模型一致性/物理合理性”基准'
  '（Physics-IQ、VideoPhy-2、T2VPhysBench 等），把 DIAMOND 关注的“细节一致性”'
  '扩展为“物理一致性”的系统研究。',
  'Three lines: (1) efficiency — latent diffusion world models became the mainstream (GameNGen\'s latent-space DOOM '
  'simulator; latent world models from the IRIS team and others); (2) scale — Sora / Genie 2 / Genie 3 pushed '
  '"video generation as world simulation" toward open worlds; (3) evaluation — a wave of benchmarks for video world-model '
  'consistency and physical plausibility (Physics-IQ, VideoPhy-2, T2VPhysBench, etc.), turning DIAMOND\'s "detail '
  'consistency" concern into a systematic study of physical consistency.')

q('世界模型的终极目标是什么？DIAMOND 在其中的位置？',
  'What is the endgame for world models, and where does DIAMOND sit?')
a('终极目标是“可交互、可规划、物理可信、可跨任务泛化的环境模拟器”，支撑智能体在想象中'
  '安全、低成本地学习与决策（LeCun 的 JEPA/世界模型愿景）。DIAMOND 的位置是“架构拐点”：'
  '第一个证明“扩散 = 更好的世界模型动力学”的工作，把“视觉一致性”确立为世界模型的核心质量维度；'
  '但它只是单任务、低分辨率、像素空间的起点。',
  'The endgame is an interactive, plan-able, physically plausible, cross-task simulator that lets agents learn and decide '
  'safely and cheaply in imagination (the LeCun JEPA/world-model vision). DIAMOND sits at an architectural turning point: '
  'the first work proving "diffusion = better world-model dynamics" and establishing visual consistency as a core quality '
  'dimension — but it is only the single-task, low-resolution, pixel-space starting point.')

q('“视觉一致性”够了吗？是不是应该直接追求物理一致性？',
  'Is visual consistency enough? Should we chase physical consistency directly?')
a('DIAMOND 的答案是“视觉一致性是必要条件、性能上已见红利”，但它明确不是充分条件：'
  '视觉一致不保证物理正确（守恒律、碰撞、因果）。后续基准（Physics-IQ 等）已证明'
  '“视觉真实 ≠ 物理正确”。合理的立场：分层递进——先视觉一致（DIAMOND），'
  '再物理一致（显式物理约束/神经-求解器耦合），最终走向可依赖的模拟器。这也是我自己的研究方向。',
  'DIAMOND\'s answer: visual consistency is necessary and already pays off in performance, but it is explicitly not '
  'sufficient — visually consistent does not mean physically correct (conservation, collisions, causality). Later '
  'benchmarks (Physics-IQ et al.) confirm "visually real != physically right". The reasonable stance is layered: visual '
  'consistency first (DIAMOND), then physical consistency (explicit constraints / neural-solver coupling), toward '
  'dependable simulators. This is also my own research direction.')

q('世界模型会不会替代游戏引擎 / 仿真器？',
  'Will world models replace game engines / simulators?')
a('短期不会，长期部分会。DIAMOND 展示了“从视频学出可玩引擎”的可行性（GameNGen 进一步把 DOOM'
  '做到了更高分辨率），但当前在保真度、可控性、确定性、成本上与手工引擎差距巨大。'
  '更有现实意义的定位是互补：数据驱动组件负责难以手工建模的部分（视觉多样性、风格），'
  '物理/逻辑层仍由传统引擎保证。',
  'Not in the short term, partially in the long term. DIAMOND showed a playable engine learned from video is feasible '
  '(GameNGen pushed DOOM further), but fidelity, controllability, determinism and cost still trail hand-built engines by '
  'far. The realistic positioning is complementary: data-driven components for what is hard to hand-model (visual '
  'variety, style), with physics/logic layers still guaranteed by traditional engines.')

q('这个方向的开放性研究问题有哪些？',
  'What are the open research questions in this direction?')
a('列几个可展开的：① 长程一致性（rollout 超过千步不漂移）与记忆机制；'
  '② 少步采样与实时性（1-2 NFE、10Hz → 60Hz+）；③ 高分辨率与 latent 表示的最优解耦；'
  '④ 物理一致性：如何在扩散世界模型里注入守恒/约束；'
  '⑤ 多任务/跨环境共享世界模型（一个模型模拟多个游戏/场景）；'
  '⑥ 评测：什么指标才算“好的世界模型”（FVD 与智能体成绩并不总是正相关）；'
  '⑦ 安全：用想象训练的真实机器人部署时的 sim-to-real 差距。',
  'Several: (1) long-horizon consistency (beyond 1000 steps) and memory mechanisms; (2) few-step sampling and real-time '
  'performance (1-2 NFE; 10Hz -> 60Hz+); (3) high resolution and the optimal latent representation; (4) physical '
  'consistency — injecting conservation/constraints into diffusion world models; (5) multi-task/cross-environment shared '
  'world models; (6) evaluation — what metric defines a "good" world model (FVD does not always correlate with agent '
  'score); (7) safety — sim-to-real gaps when deploying imagination-trained agents on real robots.')

# ================= 6 =================
h1('六、应用询问 Application Questions')

q('DIAMOND 的方法能用到自动驾驶吗？',
  'Can this approach be used for autonomous driving?')
a('论文已做“弱验证”：用真实高速路驾驶视频训练世界模型（FVD 80.3，LPIPS 0.058，明显优于 IRIS/DreamerV3）。'
  '但注意那只是“视频质量”评测，没有闭环决策。真正落地自动驾驶需要：连续动作、安全关键场景的一致性'
  '（碰撞、极端天气）、可控性（给定自车动作）与实时性，这些 DIAMOND 都还没解决。',
  'The paper offers a "weak validation": a world model trained on real motorway footage (FVD 80.3, LPIPS 0.058, clearly '
  'better than IRIS/DreamerV3). But that is video-quality evaluation only, no closed-loop decision-making. Real '
  'deployment needs continuous actions, consistency in safety-critical scenarios (collisions, extreme weather), '
  'controllability given ego actions, and real-time speed — all open in DIAMOND.')

q('在机器人上能用吗？',
  'What about robotics?')
a('原则上能（世界模型 + 想象中训练正是机器人样本效率痛点的解法），但 DIAMOND 版需要改造：'
  '连续动作、状态含本体感受（不只是像素）、接触/碰撞的物理一致性要求远高于 Atari。'
  '后续 latent world models 与基于视频的机器人预训练正是在这个方向上推进。',
  'In principle yes — world models trained in imagination target exactly robotics\' sample-efficiency pain. But the '
  'DIAMOND recipe needs adaptation: continuous actions, proprioceptive state (not just pixels), and far stricter '
  'physical consistency around contacts/collisions. Later latent world models and video-based robot pretraining advance '
  'this direction.')

q('除了游戏和开车，还能想到哪些应用？',
  'What other applications can you imagine?')
a('① 数据增强：为下游感知/规划模型合成稀有、危险场景（事故、极端天气）的训练视频；'
  '② 智能体评测：在想象世界里做大规模、可复现的策略评估；'
  '③ 数字孪生/仿真：用真实视频重建可交互场景（工厂、城市、手术室）；'
  '④ 视频压缩/传输：世界模型 + 动作 = 极低带宽的“可玩视频流”；'
  '⑤ 内容创作：可交互的电影/游戏资产原型。',
  '(1) data augmentation — synthesize rare, dangerous scenarios (accidents, extreme weather) for downstream perception/'
  'planning; (2) agent evaluation — large-scale reproducible policy testing inside imagined worlds; (3) digital twins/'
  'simulation — reconstruct interactive scenes from real video (factories, cities, ORs); (4) video compression/'
  'streaming — world model + actions as an ultra-low-bandwidth "playable video stream"; (5) content creation — '
  'interactive film/game asset prototyping.')

q('商业上为什么这个方向重要？',
  'Why does this direction matter commercially?')
a('因为“真实交互太贵”：机器人数据 1 小时可能数千美元，自动驾驶路测受法规与安全限制，'
  '而世界模型把这些成本换成 GPU 时间。谁先拥有高保真、可控、一致的世界模拟器，'
  '谁就拥有训练智能体的“数据工厂”。这也是特斯拉、Wayve（GAIA-1/2）、DeepMind（Genie）重金投入的原因。',
  'Because real interaction is expensive: an hour of robot data can cost thousands of dollars; driving tests are legally '
  'and safety constrained. World models swap those costs for GPU time. Whoever owns a high-fidelity, controllable, '
  'consistent world simulator owns a "data factory" for training agents. This is why Tesla, Wayve (GAIA-1/2) and '
  'DeepMind (Genie) invest heavily.')

# ================= 7 =================
h1('七、对比与快问快答 Comparisons & Rapid Fire')

h2('7.1 与其他工作对比')
q('DIAMOND vs DreamerV3：本质区别？',
  'DIAMOND vs DreamerV3: the essential difference?')
a('DreamerV3 的动力学是离散潜变量 RSSM（循环状态空间模型）+ 离散表征，图像重建是辅助任务；'
  'DIAMOND 把“生成下一帧”本身变成主任务（扩散去噪），没有离散瓶颈，细节保真。'
  '代价：DreamerV3 训练快得多（<1 天 vs 2.9 天），但视觉质量与一致性远差（CS:GO FVD 509 vs 34.8）。',
  'DreamerV3\'s dynamics is a recurrent state-space model (RSSM) over discrete latents, with image reconstruction as an '
  'auxiliary task. DIAMOND makes "generate the next frame" the primary task via diffusion denoising — no discrete '
  'bottleneck, full detail fidelity. The cost: DreamerV3 trains much faster (<1 day vs 2.9) but its visual quality is far '
  'worse (CS:GO FVD 509 vs 34.8).')

q('DIAMOND vs IRIS：IRIS 也是世界模型智能体，差在哪？',
  'DIAMOND vs IRIS: what exactly differs?')
a('IRIS：VQ-VAE 离散 token + 自回归 transformer（16 token/帧，16 步生成）。'
  'DIAMOND：像素空间扩散（3 NFE/帧）。同分辨率、同智能体结构、同训练数据下，'
  'DIAMOND 参数更少、训练更快、分数更高（HNS 1.46 vs 1.046），且想象视频无细节跳变。',
  'IRIS: VQ-VAE discrete tokens + autoregressive transformer (16 tokens/frame, 16 steps). DIAMOND: pixel-space '
  'diffusion (3 NFE/frame). At equal resolution, agent architecture and training data, DIAMOND has fewer parameters, '
  'trains faster, scores higher (HNS 1.46 vs 1.046), and its imagined video has no detail flicker.')

q('DIAMOND vs GameNGen？',
  'DIAMOND vs GameNGen?')
a('GameNGen（Google, 2024）晚于 DIAMOND：在 VAE 潜空间扩散模拟 DOOM，分辨率更高（可到 720p 级），'
  '但重点是“仿真器本身”而非训练 RL 智能体；DIAMOND 是像素空间 + 闭环 RL（想象中训练策略）。'
  '两者互补：DIAMOND 提出问题与闭环训练范式，GameNGen 示范了 latent 扩散的效率路线。',
  'GameNGen (Google, 2024) came after DIAMOND: it diffuses in a VAE latent space to simulate DOOM at much higher '
  'resolution, but its focus is the simulator itself, not training an RL agent. DIAMOND is pixel-space with closed-loop '
  'RL (policy trained in imagination). They are complementary: DIAMOND poses the problem and the closed-loop paradigm; '
  'GameNGen demonstrates the latent-diffusion efficiency route.')

q('DIAMOND vs Genie / Sora？',
  'DIAMOND vs Genie / Sora?')
a('定位不同：Sora 是开环文生视频（不用于闭环决策）；Genie 用视频学出“可控”的交互世界'
  '（从图像提示生成可玩环境），偏生成式交互而非 RL 训练；DIAMOND 的独特贡献是把扩散世界模型'
  '放进闭环 RL 训练循环并证明性能收益。三者共同推动“生成模型 = 世界模型”的范式。',
  'Different positioning: Sora is open-loop text-to-video (no closed-loop decision-making); Genie learns controllable '
  'interactive worlds from video (playable environments from image prompts), aimed at generative interaction rather than '
  'RL training; DIAMOND\'s unique contribution is putting a diffusion world model inside the closed-loop RL training '
  'loop and proving the performance gain. Together they push the "generative model = world model" paradigm.')

q('为什么不用 transformer 直接生成像素（如 Image GPT）？',
  'Why not a transformer generating pixels directly (Image GPT style)?')
a('像素级自回归 transformer 的序列太长（64×64×3 的 token 序列），推理极慢，'
  '且离散化像素同样面临量化/似然建模问题。扩散在连续空间做“并行去噪”，'
  '在低分辨率下又快又稳，这正是 DIAMOND 的论证。',
  'Pixel-level autoregressive transformers face sequence lengths of 64x64x3 tokens — far too slow at inference — and '
  'pixel discretization still has quantization/likelihood issues. Diffusion denoises in parallel in continuous space: '
  'fast and stable at low resolution, which is DIAMOND\'s argument.')

h2('7.2 快问快答 Rapid Fire')
q('“Imagination”在论文里具体指什么？',
  'What does "imagination" concretely mean here?')
a('指智能体不接触真实环境，仅在扩散世界模型生成的状态序列上计算奖励、终止并更新策略/价值的过程'
  '（每次想象视野 H=15 步）。',
  'The process where the agent, without touching the real environment, rolls out H=15 steps inside the diffusion world '
  'model, gets rewards/terminations from R, and updates policy and value.')

q('为什么 HNS 用“人类=1”标尺？',
  'Why the "human=1" scale?')
a('26 款游戏的原始得分量纲差异极大（几十分到几万分），直接平均会被大分游戏主导；'
  '按人类水平归一化后各游戏权重可比，是 Atari 100k 社区惯例（Mnih et al. 2015 起）。',
  'Raw scores span orders of magnitude across the 26 games; averaging them directly lets big-score games dominate. '
  'Human-normalization makes games comparable — the community standard since Mnih et al. 2015.')

q('随机种子对扩散世界模型影响大吗？',
  'Do random seeds matter a lot for the diffusion world model?')
a('论文每个游戏跑 5 种子并报告均值；扩散模型训练本身较稳定，'
  '波动主要来自 RL 训练与数据收集的随机性。消融实验（n=1）只跑单种子，论文自己也标注了方差风险。',
  'The paper runs 5 seeds per game and reports means. Diffusion-model training itself is fairly stable; variance comes '
  'mostly from RL and data collection. The n=1 ablation uses a single seed, and the paper flags its higher variance.')

q('一个“世界模型”好坏的唯一标准是什么？',
  'What is the single criterion for a good world model?')
a('对 DIAMOND 而言：rollout 的一致性 × 训练出的策略成绩。二者互为印证——'
  'FVD/漂移是代理指标，最终裁判是想象中训练出的智能体在真实环境的得分。',
  'For DIAMOND: rollout consistency x downstream policy score. They validate each other — FVD/drift are proxies; the '
  'final judge is how well an agent trained in imagination performs in the real environment.')

q('如果评委问“DIAMOND 的贡献到底是一个还是三个”，怎么答？',
  'If asked "is DIAMOND one contribution or three?", how to answer?')
a('一句话：一个核心主张（扩散是更好的世界模型动力学），由三个支撑构成——'
  '① 设计选择的分析（EDM vs DDPM、去噪步数）；② Atari 100k 实证（1.46）；'
  '③ 可交互神经游戏引擎的规模化演示（CS:GO）。三者缺一不可。',
  'One core claim (diffusion is the better world-model dynamics) supported by three pillars: (1) the design-choice '
  'analysis (EDM vs DDPM, denoising steps); (2) the Atari-100k evidence (1.46); (3) the scalable interactive neural game '
  'engine (CS:GO). All three together make the case.')

q('给非本领域听众的一句话版答案是什么？',
  'One-sentence version for a general audience?')
a('“以前的世界模型把画面压成粗糙的‘缩写’，智能体在失真的想象里学习；DIAMOND 改用扩散模型'
  '逐像素地‘画’出下一帧，想象世界不再闪烁，智能体成绩随之刷新纪录。”',
  '"Older world models compressed each frame into a rough shorthand, so agents learned in distorted imagination; '
  'DIAMOND uses a diffusion model to paint the next frame pixel by pixel — the imagined world stops flickering, and the '
  'agent sets a new record."')

p()
p('说明：本手册中所有数字与论断均核对自论文原文（arXiv:2405.12399）及其附录（Table 2-5、附录 B/D/E/F/M）。'
  '部分“推测性”回答（如失败游戏原因、商业分析）已明确标注为推测，答辩时请相应措辞。',
  size=9, italic=True, color=GRAY)

doc.save('diamond-qa-handbook.docx')
print('saved diamond-qa-handbook.docx')
