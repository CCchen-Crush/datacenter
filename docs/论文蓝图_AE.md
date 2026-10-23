# 论文蓝图（对标 Applied Energy 范文 Zhang 等 2026，128499）

> 主线以 [`研究方案_AE重构.md`](研究方案_AE重构.md) 为准；本文件规定**写法、结构、算法包装和图表体系**，实验数字由 `tools/` 下的脚本从 `matlab/results/` 统一生成后填入。

## 0 写作基调（必须遵守）

1. **主动、自信地陈述结论。** 每个结果小节按“结论句 → 机理 → 定量 → 小结（These results demonstrate/confirm that …）”四步写。例：“JR-D raises the firm consecutive DR capacity from X MW to Y MW at 95 % reliability, because …”。
2. **数据来源与假设只在一处交代清楚。** 在 5.1 算例设置中用一段话说明：负载曲线由阿里 PAI 与 Azure LLM 公开轨迹缩放生成，气象取 ERA5，参数见附录表；多情景由 26 个 PAI 工作日与气象、推理日交叉组合生成。此后正文不再反复声明“仅为仿真”“不代表真实”之类的限定语。
3. **限定条件写成“适用条件”，不写成“自我否定”。** 例如不写“容量优势可能被高估”，而写“容量增益在短间隔和受限并网余量下最为显著（τ ≤ 1 h，γ ≤ 1.10）”。无优势工况作为“边界条件”正面呈现，它说明方法何时值得采用。
4. **不写“首次”。** 用 “To the best of our knowledge, few studies …” / “remains insufficiently explored”。
5. 局限性只在结论末段集中写 3–4 条，并与“未来工作”合写。

## 1 题目、Highlights、摘要

**题目**：Recovery-aware coordinated scheduling of computing workloads and energy storage for deliverable consecutive demand response in AI data centers

**Highlights（3–5 条，每条 ≤85 字符）**

- Heterogeneous computing–storage recovery debts compete for one grid recovery channel.
- Firm consecutive DR capacity is defined as a chance-constrained deliverability metric.
- A recovery-aware day-ahead commitment and intraday joint recovery MPC are proposed.
- Joint recovery raises firm DR capacity by X MW (Y %) at 95 % reliability.
- Gains concentrate at short event intervals and tight grid connection margins.

**摘要（单段，约 250 词，五层）**：真实挑战（AI 数据中心多次响应、恢复需求）→ 研究不足（单次事件评估与独立恢复）→ 方法（异质恢复模型、可靠可交付容量、日前承诺—日内恢复协同）→ 定量结果（对最强基准的可靠容量增益、兑现率、成本，及条件）→ 意义（为数据中心向电网承诺连续响应容量提供决策依据）。

**关键词**：AI data center; consecutive demand response; computing–storage recovery; firm deliverable capacity; chance-constrained commitment; model predictive control

## 2 符号表（三级）

- **Abbreviations**：AIDC, DR, IES, BESS, TES, CCHP, PV, COP, SLA, MILP, MPC, SAA, IR-O*, IR-P, JR-M, JR-D, JR-S, SE, RA
- **Parameters**：Δt, K, s_k/e_k, C_k, π_k, κ, η_c/η_d, E^min/E^max, P^BESS, Q^TES, L_c, P^cap, γ, ρ, P^base_t, φ_t（设施功率/IT 功率）……
- **Variables**：y_{c,t}, B_{c,t}, V_{c,t}, P^grid_t, P^ch/P^dis, E_t, S_t, P^GT, Q^AC, Q^EC, z_k（有效性 0–1）, R_k（计补贴削减）, u_{k,ω}（场景足额 0–1）……

## 3 引言结构（背景 → 三段综述 → 缺口 → 3 条贡献 → 文章结构）

- **背景**：IEA 945 TWh（2030）；AI 数据中心成为可调资源（Duke 研究、英国 National Grid–Emerald AI–NVIDIA 试验 5 天 200 余次事件）；江苏细则允许约定响应每日两次、并有快速避峰类事件。
- **综述一：数据中心需求响应与算力柔性**（AE 2025 126095 负荷建模、液冷需求响应 AE 2026、Liu/Wierman 系列、Chen & Zheng 2026、Lu 等 2026 储能辅助）。收尾句：现有研究多以单次事件的削减量为目标，事件后的恢复状态及其对后续能力的影响仍未被系统研究。
- **综述二：算电协同与综合能源系统运行规划**（Zhang 等 2026 128499、AE 2026 127904 柔性与可靠性、IES 调度文献）。收尾句：现有研究刻画了算力—电力—热力耦合，但很少把计算积压与储能 SOC 作为跨事件继承的状态。
- **综述三：灵活性资源的可交付能力与恢复保证**（Evans 等 TSG 2022 恢复保证、储能聚合可用容量、机会约束承诺）。收尾句：恢复保证研究针对同质储能，不含带截止期限的计算欠账与有损储能欠账在同一并网通道中的竞争。
- **缺口段**：三点合并为“短间隔连续事件下，异质恢复需求如何决定后续可交付容量，以及如何把这一影响纳入多事件承诺决策”。
- **贡献（编号 3 条，对应 A/B/C）**：
  1. **机理与模型**：建立带期限的分类计算积压与有损储能欠账共享并网恢复通道的跨事件异质恢复模型；给出后续可交付能力上界（命题 1）与联合恢复的价值条件和最小恢复间隔闭式解（命题 2，即原定理 1）。
  2. **能力量化**：提出“可靠可交付连续响应容量”C_ρ^firm 这一机会约束指标及其多事件可行域，并给出基于场景样本的求解方法（单调性 → 承诺网格二分/场景序统计量）。
  3. **决策方法与验证**：构建“恢复感知日前承诺（两阶段随机 MILP，江苏结算有效性用 big-M 线性化）+ 日内跨事件联合恢复 MPC”的协同框架；在 S1–S4 场景、26 个运行日和四类强基准下验证容量、经济性与适用条件。

## 4 方法章节的算法包装

- **模型层**：算侧积压方程与期限约束、储侧 SOC、电—冷平衡（电制冷、吸收式制冷、蓄冷、燃气内燃机、光伏）、并网上限、江苏结算（80% 有效、120% 补贴上限、偏差考核），结算有效性为 0–1 变量，用 big-M 线性化（只在有效事件上约束“计补贴削减 ≤ 实际削减”）。
- **承诺层（日前）**：两阶段随机规划，第一阶段为各事件承诺 C_k，第二阶段为各场景下的联合恢复调度；可靠容量用场景足额指示变量 u_ω 与 Σ p_ω u_ω ≥ ρ 表达（SAA）。统一承诺时，场景可行性对 C 单调，机会约束退化为承诺网格上的二分/序统计量。
- **调度层（日内）**：滚动时域 MPC（H = 18 h，Δt = 15 min），终端 SOC 参考与积压终端价值保证可比性；JR-D 为确定性等价，JR-S 为场景树（事件调用不确定）。
- **Table 1（算法伪代码）**：Algorithm 1 “Recovery-aware commitment and rolling joint recovery”：输入（场景集、承诺网格、ρ）→ 日前：逐 C 求场景可行性与期望成本 → 机会约束与成本最小选 C* → 日内：每步更新状态、修正预测、求解 MILP、执行首步、仿真器回放（越限时依次调储能、蓄冷、可延后算力）→ 输出承诺与运行轨迹。
- **理论**：命题 1（可交付能力上界：通道宽度、任务时限、储能能量共同决定）；命题 2（联合恢复存在优势的条件与最小恢复间隔差 τ*(IR) − τ*(JR) = min(X, p_f(L − D_B))/h）。影子价格只作一段经济解释。

## 5 算例与结果章节

**5.1 算例设置**：16 000 GPU AIDC、IES 参数（附录表 A1–A3）、数据来源一段话、场景 S1–S4 表、四种策略。

**Table 2（受控情景矩阵，✓/✕）**

| 情景 | 计算柔性 | 电储能 | 蓄冷 | 联合恢复 | 跨事件预见 |
|---|---|---|---|---|---|
| A0 不参与 | ✕ | ✕ | ✕ | ✕ | ✕ |
| A1 仅储能 | ✕ | ✓ | ✕ | — | ✓ |
| A2 仅算力 | ✓ | ✕ | ✕ | — | ✓ |
| A3 算力 + 储能 | ✓ | ✓ | ✕ | ✓ | ✓ |
| IR-O* / IR-P | ✓ | ✓ | ✓ | ✕ | ✓ |
| JR-M | ✓ | ✓ | ✓ | ✓ | ✕ |
| JR-D（本文） | ✓ | ✓ | ✓ | ✓ | ✓ |

**结果小节**：5.2 可靠可交付容量（核心，S1/S2/S3）→ 5.3 恢复机理（典型日 + 长间隔对照）→ 5.4 方法对比（固定承诺 / 内生承诺两套协议）→ 5.5 敏感性（τ、γ、L_c、储能功率；τ×γ 热力图）→ 5.6 多情景与经济性（区组自助法、JR-S、成本构成）→ 5.7 消融（Table 2）。

## 6 图表体系（主图 8 张 + 补充图）

| 图 | 内容 | 形式（参照范文） |
|---|---|---|
| Fig. 1 | 系统结构与双状态恢复通道 | 系统示意图（能流 + 算力流，恢复通道高亮） |
| Fig. 2 | 典型日调度时序 | 四联：功率平衡堆叠柱（供给为正、负荷为负，范文 Fig. 6 式）；分类积压堆叠面积；BESS/TES 充放电柱（范文 Fig. 7 式）与 SOC 线；恢复通道分配（补算 vs 回充，堆叠面积） |
| Fig. 3 | 可靠容量曲线 | 足额可靠率–承诺曲线 + 自助法置信带，标出 ΔC_ρ；S1/S2/S3 三联 |
| Fig. 4 | 两事件可靠可行域 | C1–C2 网格上的可行区域阶梯边界，四种策略叠加 |
| Fig. 5 | 方法性能对比 | 双轴堆叠成本柱（电费、燃气、退化、延迟、偏差 − 补贴）+ 兑现率折线（范文 Fig. 5 式） |
| Fig. 6 | 敏感性 | τ×γ 容量/可靠率增益热力图 + L_c、储能功率单因素折线 |
| Fig. 7 | 消融 | Table 2 情景的可靠容量瀑布图；算力与储能贡献的镜像柱图（范文 Fig. 17“替代效应”式） |
| Fig. 8 | 多情景统计 | 逐日配对差的小提琴/箱线图 + 山脊图（各策略足额交付率随承诺的分布，范文 Fig. 18 式） |
| 补充 | 机理上界（原 fig02）、命题 2 闭式解与 LP 对照、反弹政策扫描、完美预测对照、影子价格 | |

统一风格：Times New Roman / 宋体，正文 8–9 pt；色系固定（JR-D 蓝、IR-O* 橙、IR-P 绿、JR-M 粉）；PDF + SVG 矢量输出；所有图由 `tools/plot_paper.py` 一次生成。

## 7 结论（编号 4–5 条）

每条“发现 + 数字 + 条件”。例：(1) 前序事件的恢复欠账使末次事件成为瓶颈……；(2) 在 95% 可靠率下，JR-D 将可靠可交付容量提高 X MW……；(3) 增益在 τ ≤ … 与 γ ≤ … 时显著，通道充足时消失（命题 2 的条件）；(4) 恢复感知承诺使期望净收益提高 …；(5) 局限与展望（作业级模型、大模型轨迹、配电网约束、多数据中心）。

## 8 附录

A1 设备参数表；A2 负载与气象数据处理；A3 结算参数（江苏细则条款）；A4 命题证明；A5 补充图。
