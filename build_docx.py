"""Build concept primer DOCX for the DIAMOND talk (Chinese, English terms kept)."""

import docx
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x49, 0x7D)
RED = RGBColor(0xC0, 0x50, 0x4D)
GRAY = RGBColor(0x59, 0x59, 0x59)
GREEN = RGBColor(0x3B, 0x7A, 0x3B)
BLACK = RGBColor(0x1A, 0x1A, 0x1A)

doc = Document()

# page setup
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)

# base style
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def p(text='', size=10.5, bold=False, italic=False, color=BLACK, align=None,
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
    par = p(text, size=16, bold=True, color=NAVY, space_before=14, space_after=6)
    # bottom border
    pPr = par._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:space'), '2'); bottom.set(qn('w:color'), '1F497D')
    pbdr.append(bottom)
    pPr.append(pbdr)
    return par


def h2(text):
    return p(text, size=12.5, bold=True, color=NAVY, space_before=10, space_after=4)


def bullet(label, text, label_color=NAVY, indent=0.55):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(3)
    par.paragraph_format.left_indent = Cm(indent)
    r = par.add_run('▸ ')
    r.font.color.rgb = label_color
    r.font.bold = True
    r.font.size = Pt(10.5)
    r2 = par.add_run(label + '　')
    r2.font.bold = True
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = label_color
    r3 = par.add_run(text)
    r3.font.size = Pt(10.5)
    return par


def tip(text):
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(4)
    par.paragraph_format.left_indent = Cm(0.55)
    r = par.add_run('💡 ')
    r.font.size = Pt(10.5)
    r2 = par.add_run(text)
    r2.font.size = Pt(10.5)
    r2.font.italic = True
    r2.font.color.rgb = GRAY
    return par


# ================= TITLE =================
p('DIAMOND 技术汇报 · 概念导读手册', size=20, bold=True, color=NAVY,
  align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p('世界模型的视频一致性 —— Diffusion for World Modeling: Visual Details Matter in Atari (NeurIPS 2024)',
  size=11, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p('配套：world-model-video-consistency-diamond.pptx（12 页）+ speaker-script.md（10 分钟逐页讲稿）',
  size=9.5, italic=True, color=GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

# ================= 0 =================
h1('0. 一句话概括这篇论文')
p('DIAMOND 证明了一件事：把世界模型的“环境模拟器”从【离散 token 自回归模型】换成【连续潜空间的扩散模型】之后，'
  '想象出来的视频帧与帧之间不再出现细节跳变（视频一致性），而正是这些细节决定了强化学习智能体的成绩。'
  '结果是 Atari 100k 基准上 mean human-normalized score 达到 1.46，刷新“完全在世界模型内训练”的记录。')
tip('全篇逻辑链只有四步：问题（离散 token 丢细节）→ 手段（扩散世界模型）→ 机制（EDM 训练目标 + 3 步去噪保住稳定性）'
    '→ 验证（一致性带来分数提升，且在 CS:GO 上能扩展）。演讲时反复点这条线即可。')

# ================= 1 =================
h1('1. 背景：什么是世界模型（World Model）？')
h2('1.1 强化学习的样本效率问题')
bullet('强化学习 (RL)', '智能体通过“试错 + 奖励”学习策略。经典 Atari 智能体通常需要约 5000 万步环境交互（≈50M steps），'
       '相当于 500 倍于 DIAMOND 的 10 万步预算。样本效率低是 RL 落地真实世界（机器人、自动驾驶）的最大障碍。')
bullet('世界模型的基本想法', '先在离线数据上学一个“环境模拟器”（dynamics model），之后让智能体在这个模拟器里无限试错，'
       '只有数据收集阶段才接触真实环境。想象（imagination）里的每一步都不消耗真实交互。')
tip('演讲口径：世界模型 = 把“贵”的真实交互换成“便宜”的模拟交互；模拟器的质量决定了策略的上限。')
h2('1.2 传统世界模型怎么做（离散 token 路线）')
bullet('离散潜变量', '主流的 DreamerV3、IRIS、STORM 都用 VQ-VAE（vector-quantized variational autoencoder）把图像压缩成'
       '一组离散 token（类似图像的“词汇表”），再用 transformer 自回归地预测下一个 token。')
bullet('为什么要离散化', '离散表示能抑制长程 rollout 的误差累积（compounding error）——预测一个有限集合里的类别，'
       '比回归连续向量更“稳定”。')
bullet('代价', '量化是有损压缩：把一幅图压成几百个 token，必然丢掉少量像素级别的细节。'
       '敌人、奖励、得分这类恰好由“几个像素”构成的语义，最容易在重建中丢失或错位。')
tip('关键因果：细节丢失 → 相邻帧之间小物体时隐时现（视频不一致）→ 智能体看到的奖励信号被污染。'
    '这不是理论推演，论文 Figure 5 用 IRIS 的 rollout 直接展示了敌人↔奖励互换。')

# ================= 2 =================
h1('2. 预备知识：扩散模型（Diffusion Model）')
h2('2.1 核心思想：加噪—去噪')
bullet('前向过程', '给干净图像逐步加高斯噪声，最终变成纯噪声。')
bullet('反向过程（生成）', '训练一个神经网络学会“一步去噪”；生成时从纯噪声出发，逐步去噪得到图像。'
       'DIAMOND 把它用于“预测下一帧”：从噪声出发，去噪出 t+1 时刻的观测。')
h2('2.2 两个必须区分的框架：DDPM vs EDM（演讲重点！）')
bullet('DDPM（Ho et al. 2020）', '网络被训练来预测“噪声本身”ε。缺陷：当噪声占主导（σ_noise ≫ σ_data）时，'
       '最优预测退化成恒等映射 ξ(x) → x，采样一开始的 score 估计很差，误差沿 rollout 累积——'
       '这正是论文 Figure 3a 里画面逐渐腐蚀（颜色漂移）的原因。')
bullet('EDM（Karras et al. 2022）', '训练目标中“自适应混合信号与噪声”：噪声占主导时，网络被训练来直接预测'
       '“干净的图”x₀ 本身。于是几乎没有信号时也有很好的 score 估计，采样从一开始就稳定。'
       '论文 Figure 3b：EDM 世界模型即使只用 1 步去噪也稳定。')
tip('演讲金句：不是“扩散模型”天然适合世界模型，而是“EDM 这种扩散公式”才适合——DDPM 版会漂移。'
    '这是 DIAMOND 的第一个设计选择（Design Choice 1）。')
h2('2.3 为什么世界模型用扩散天然合理')
bullet('连续表示', '没有量化瓶颈，细节可以保留到像素级。')
bullet('天然采样', '去噪过程本身就是从“下一帧的分布”里采样——正好匹配环境转移的随机性。')
bullet('代价', '每生成一帧要跑一次完整的网络前向（1 个 NFE，number of function evaluations）；'
       'DIAMOND 用 3 步，仍是世界模型里的计算大头。')

# ================= 3 =================
h1('3. DIAMOND 方法拆解')
h2('3.1 三个组件')
bullet('① 扩散世界模型（核心）', '2D U-Net，基于 EDM。条件输入：过去 L 帧观测按通道拼接（channel-wise concatenation）'
       '到带噪的下一帧上；动作 a 通过残差块里的 adaptive group normalization 注入。')
bullet('② 奖励/终止模型 R', '单独的 CNN+LSTM，预测标量 reward 和 episode 是否结束（处理部分可观测性 POMDP）。')
bullet('③ 智能体（actor-critic）', '共享 CNN-LSTM；策略 π 用 REINFORCE + value baseline 训练，'
       '价值网络用 λ-returns（Bellman 误差）训练。与 IRIS 的智能体几乎相同——所以成绩差应归因于世界模型。')
h2('3.2 训练循环（Algorithm 1）')
p('收集真实数据 → 用全部已有数据更新世界模型 → 在更新后的世界模型里做 RL（纯想象）→ 重复。'
  '智能体只在“收集数据”这一步接触真实环境，与 DreamerV3/IRIS 的框架一致。', space_after=6)
h2('3.3 两个关键设计选择')
bullet('选择 1：EDM 而非 DDPM', '决定 rollout 会不会漂移（见 §2.2、§5）。')
bullet('选择 2：3 步去噪而非 1 步', '1 步时预测的是“下一帧分布的条件期望”。当环境部分可观测、'
       '下一帧分布多模态（例如 Boxing 里对手动作不可预测）时，期望本身就是一张“不在分布内”的模糊图（Figure 4 上行）。'
       '迭代 3 步会把采样驱动到某个具体模态，得到清晰一致的帧（Figure 4 下行）。'
       '消融：Top-10 游戏 mean HNS 从 3.05（n=3）跌到 1.96（n=1）。')

# ================= 4 =================
h1('4. 视频一致性问题（本场汇报的主题落点）')
bullet('定义（本 talk 语境）', '世界模型 rollout 出的相邻帧之间，同一语义实体（敌人/奖励/砖块/得分）保持身份、位置、外观连续，'
       '不出现身份互换、时隐时现、颜色跳变。')
bullet('IRIS 的反例（Figure 5）', 'Asterix：敌人（橙色）第二帧变成奖励（红色），第三帧又变回敌人；'
       'Breakout：砖块和分数在帧间不一致；Road Runner：路上的奖励蓝点时有时无。')
bullet('为什么致命', '世界模型里每一帧都是智能体的训练样本。一个“应该追奖励、躲敌人”的智能体，'
       '在 IRIS 里学到的样本中两者被互换——少几个像素的不一致，对策略学习来说就是标签噪声（label noise）。')
bullet('DIAMOND 的答案', '同样 64×64 分辨率、更少参数、每帧仅 3 NFE（IRIS 16 NFE），细节保持一致；'
       'Breakout 里打碎红砖后分数甚至可靠地 +7。')
tip('如果听众只记得一句话，应该是：视频一致性不是审美问题，是训练信号质量问题。')

# ================= 5 =================
h1('5. 稳定性的定量证据：像素漂移（Pixel Drift）')
bullet('实验设置（Figure 8）', 'Breakout，1000 步 rollout；同一个起始帧、同一组专家动作序列，'
       '对 400 条留出的参考轨迹取平均像素漂移（imagined vs reference 的平均像素差）。')
bullet('结论 1', 'DDPM 无论 1/3/10 步去噪，漂移都持续增大；10 步 DDPM 仍不如 1 步 EDM 稳定。')
bullet('结论 2', 'EDM 的残余漂移是“轨迹差异”（想象了一条同样合法但略不同的玩法），'
       '而不是 DDPM 那种病态的颜色腐蚀——即漂移的性质不同：一个是内容漂移，一个是渲染崩塌。')
tip('这页把“一致性”从观感变成可测的量，是演讲里最有说服力的一页，建议讲慢一点。')

# ================= 6 =================
h1('6. 实验与数字（务必背熟）')
h2('6.1 Atari 100k（Table 1）')
bullet('设定', '26 个游戏，每游戏 10 万环境步（≈2 小时人类游玩），5 个随机种子；'
       '每个 run 约 12GB 显存、单卡 RTX 4090 约 2.9 天，全基准共 1.03 GPU-years。')
bullet('主结果', 'Mean HNS = 1.46（人类=1.0），为“完全在世界模型内训练”方法的新纪录；'
       '26 个游戏里 11 个超人类（STORM/DreamerV3 10 个，IRIS 8 个）。IQM 0.64（与 STORM 持平，高于其余基线）。')
bullet('赢在哪', '恰好是细节决定成败的游戏：Asterix 3698（STORM 1028）、Breakout 132.5（IRIS 83.7）、'
       'Road Runner 20673（全场最高）。')
bullet('公平性', '智能体结构与 IRIS 等几乎相同 → 分数差距归因于世界模型的视觉一致性，而非更强的策略网络。')
h2('6.2 3D 扩展（Table 8）')
bullet('CS:GO', '87 小时静态人类对局（Dust II 地图），先降采样到 56×30 建模，再用第二个小扩散模型做超分上采样；'
       'U-Net 从 Atari 的 4M 参数扩到 381M。FVD 34.8（IRIS K=64 为 85.7，DreamerV3 509.1）。'
       '人可以实时用键鼠进入这个世界模型游玩（Figure 6）。')
bullet('驾驶', '美国高速路车载视频 3.6 小时训练。FVD 80.3（IRIS 276.9，DreamerV3 733.7）。')
bullet('速度', '动态模型仍只 3 步去噪；上采样器 10 步 + 随机采样（stochastic sampling）。'
       '整体约 10Hz（RTX 3090）。论文也坦承：靠近墙/丢失视野时模型会“忘记”当前状态，'
       '空中连跳会被错误允许（因为训练数据里罕见）。')

# ================= 7 =================
h1('7. 局限与开放问题')
bullet('分辨率', '64×64（Atari）/ 56×30+超分（CS:GO），离真实视觉丰富度还很远。')
bullet('采样速度', '每帧 3 NFE，约 10Hz；交互体验需要随机采样 + 更多上采样步数，实时高分辨率仍昂贵。')
bullet('计算量', '智能体是样本高效的，但世界模型不是：全基准 1.03 GPU-years。'
       '后续工作（latent diffusion world models，如 GameNGen/后续 DIAMOND 变体）正是冲着这个去的。')
bullet('单任务', '每个游戏一个世界模型，没有跨环境的泛化。')
bullet('视觉一致 ≠ 物理一致', '画面可以一直“看起来对”，但不遵守物理规律；长程漂移依然存在（Figure 8 的残余曲线）。'
       '这是当前世界模型研究的活跃前沿。')

# ================= 8 =================
h1('8. 术语速查表')
terms = [
    ('World model（世界模型）', '学习环境动态并用于“想象中训练”的模型。'),
    ('Rollout（展开/推演）', '世界模型按时间顺序连续生成多步未来帧的过程；也是误差累积发生的地方。'),
    ('Compounding error（误差累积）', '单步小误差沿 rollout 逐步放大，最终画面失真。'),
    ('VQ-VAE', '把图像编码为离散 token 的自编码器；离散世界模型（IRIS/DreamerV3）的基础。'),
    ('Quantization（量化）', '连续值映射到有限离散集合；稳定 rollout 但丢失细节。'),
    ('Token', '离散表示的基本单元（类似“词”）；图像被拆成一串 token。'),
    ('Autoregressive（自回归）', '逐 token 生成，用已生成的预测下一个。'),
    ('Diffusion model（扩散模型）', '加噪—去噪框架；生成时从噪声迭代去噪出样本。'),
    ('Denoising step / NFE', '一次网络前向（一步去噪）。NFE 越多生成越精细、越慢。'),
    ('EDM', 'Karras et al. 2022 的扩散框架；自适应混合信号与噪声，DIAMOND 用它。'),
    ('DDPM', 'Ho et al. 2020；预测噪声 ε。世界模型里会漂移（Figure 3a）。'),
    ('Score function（得分函数）', '数据对数密度对输入的梯度 ∇log p(x)；扩散采样要估计的量。'),
    ('Multimodal posterior（多模态后验）', '下一帧的分布有多个峰（如对手可能往左或往右）；1 步去噪只能给期望，会糊。'),
    ('Partial observability（部分可观测）', '智能体看不到完整状态，只能从观测推断（POMDP）。'),
    ('POMDP', 'Partially Observable Markov Decision Process；Atari 的正式设定。'),
    ('Actor-critic', '策略（actor）+ 价值（critic）双网络的 RL 算法族。'),
    ('REINFORCE', '经典策略梯度算法；DIAMOND 用它加 value baseline 训练策略。'),
    ('λ-returns', '多步回报的加权混合，用于训练价值网络。'),
    ('Adaptive group normalization', 'DIAMOND 把动作注入 U-Net 的机制（由动作调制归一化参数）。'),
    ('U-Net', '编码器-解码器带跳跃连接的卷积网络；DIAMOND 的扩散骨干。'),
    ('HNS（human-normalized score）', '把游戏得分映射为 随机=0、人类=1 的标准化分数；1.46 即平均超人类 46%。'),
    ('IQM（interquartile mean）', '去掉头尾 25% 后取均值，对离群游戏更稳健的聚合指标。'),
    ('FVD（Fréchet Video Distance）', '衡量生成视频与真实视频分布距离的指标，越低越好；带时间维度的 FID。'),
    ('LPIPS', '感知相似度损失，衡量两帧“看起来”的差异；越低越像。'),
    ('FID', 'Fréchet Inception Distance，只衡量单帧质量、不看时间维度。'),
    ('Stochastic sampling（随机采样）', '扩散采样时注入随机性；CS:GO 上采样器用它提升观感。'),
    ('Frame stacking（帧堆叠）', '把过去 L 帧直接拼在输入通道上作为条件。'),
    ('Cross-attention（交叉注意力）', 'DIAMOND 3D 实验里另一种条件注入方式；论文 Table 8 显示帧堆叠更优。'),
    ('Sample efficiency（样本效率）', '达到给定性能所需环境交互量；世界模型的核心卖点。'),
    ('Neural game engine（神经游戏引擎）', '用网络替代传统渲染引擎、可交互的生成式模拟器（DIAMOND 的 CS:GO demo）。'),
]
for t, d in terms:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(2)
    r = par.add_run('· ' + t + '：')
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = NAVY
    r2 = par.add_run(d)
    r2.font.size = Pt(10)

# ================= 9 =================
h1('9. 如果被问到（速答版）')
qa = [
    ('Q: 为什么不用更大的离散 VAE（如 IRIS 的 K=64）？',
     'A: 论文 3D 实验里 K=64 确实比 K=16 好，但 FVD 仍比 DIAMOND 差 2.5 倍。问题出在离散瓶颈本身，不只是它的大小。'),
    ('Q: 每帧 3 次网络前向不贵吗？',
     'A: 贵——论文明确说世界模型（而非智能体）是计算大头（约 10Hz、全基准 1.03 GPU-years）。后续的 latent 扩散世界模型就是为提速而生。'),
    ('Q: 随机环境能用吗？',
     'A: 能，扩散天然是采样。Boxing 一例正是“部分可观测 + 随机”时多步去噪把采样拉向具体模态。'),
    ('Q: 为什么是 Atari，不是更现代的基准？',
     'A: Atari 100k 是“样本效率”的标准战场（2 小时对 5000 万步），最适合检验世界模型；论文另用 CS:GO/驾驶证明方法可扩展到真实 3D 画面。'),
    ('Q: DIAMOND 和 Sora/Genie 什么关系？',
     'A: 同属“扩散/视频生成”谱系，但 DIAMOND 的贡献是把它做成闭环 RL 世界模型（可训练策略），而不仅是开环视频生成。'),
    ('Q: 为什么不用 transformer 直接预测连续潜变量？',
     'A: 这正是后续方向（latent world models）。DIAMOND 的选择是“扩散建模 + 少步采样”在细节保真与速度间取得平衡。'),
]
for q, a in qa:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(4)
    r = par.add_run(q)
    r.font.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = RED
    par2 = doc.add_paragraph()
    par2.paragraph_format.space_after = Pt(6)
    r2 = par2.add_run(a)
    r2.font.size = Pt(10.5)

# ================= 10 =================
h1('10. 演讲前一小时检查清单')
for item in [
    '能不看稿说出四步逻辑链（问题→手段→机制→验证）。',
    '能背出 1.46 / 11/26 / 3.05→1.96 / 3 vs 16 NFE / 34.8 / 80.3 这六组数字。',
    '能解释 DDPM 漂移的机制（噪声主导时预测坍缩为恒等映射）。',
    '能解释 1 步 vs 3 步去噪（多模态后验的期望 = 糊帧）。',
    '能指着 Figure 5 的白框说出至少两个具体不一致（敌人变奖励、砖块分数漂移）。',
    '准备好一句话回答“什么是视频一致性”：世界模型 rollout 的相邻帧之间，语义实体保持身份与外观连续；不一致 = 给策略的标签噪声。',
]:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(2)
    r = par.add_run('□ ')
    r.font.size = Pt(11)
    r2 = par.add_run(item)
    r2.font.size = Pt(10.5)

p()
p('来源：Alonso et al., "Diffusion for World Modeling: Visual Details Matter in Atari", NeurIPS 2024 (arXiv:2405.12399)。'
  '本文档为汇报辅助材料，所有数据取自论文原文。', size=9, italic=True, color=GRAY)

doc.save('diamond-concept-primer.docx')
print('saved diamond-concept-primer.docx')
