# 交接文档（Applied Energy 重构版，2026-10-23 05:00 UTC）

> 给下一位接手者（人或 AI）。**工作分支：`claude/ae-reliable-capacity`**（仓库 CCchen-Crush/datacenter）。
> 主线以 [`研究方案_AE重构.md`](研究方案_AE重构.md) 为准，写法与图表规范以 [`论文蓝图_AE.md`](论文蓝图_AE.md) 为准（对标 Zhang 等 2026，Applied Energy 128499）。
> 用户要求：保持主线，不再扩展实验种类；论文要“创新点明确、结果好、图表精美、问题真实紧迫”，不追求工程级认证；写作要主动自信，数据来源只在算例设置里交代一次，不反复自我否定结论量级。

> **2026-10-23 16:50 更新：全部实验完成，论文已写完。** batch7 的 25 个作业全部跑完（无报错），结果已合并入 `matlab/results/`；论文 `paper/manuscript.md` 的摘要（250 词）、Highlights、第 5 节（5.1–5.8）、第 6 节和 Table 4、Table 5 全部按最终结果写定，没有待补占位符；14 张正文图和 S1–S7 补充图已重新生成（`tools/refresh.sh`）。中文结果汇总见 [`实验结果_AE.md`](实验结果_AE.md)。剩余工作见第 6 节。

> **2026-10-23 12:30 更新（容器重启后）：** 11:42 UTC 容器重启，正在跑的作业全部丢失。现已改为“每个承诺水平 / 每个策略跑完即写 CSV”（exp12/14/18/19/20），重启只丢当前那一段；exp18 按承诺从小到大扫，某天第一次失败后不再跑该天（能力 ξ 只需要到第一次失败）；exp12/18/19 可用 `E*_ALPHA` 复用同场景已整定的 IR-O* 分摊比例（`src/bench_prepare.m`，tune_alpha 是确定性的，已核对一致）；exp20 新增 `E20_SET='region'`（第一事件固定 C1、二分法求第二事件可靠承诺，取代 exp14 区域网格）。
> 全部剩余作业在 `tools/jobs/batch7.txt`（25 个，4 核约 4 小时），在开发副本 `/home/user/dev` 中运行：`cd /home/user/dev && nohup setsid bash tools/run_queue.sh 4 tools/jobs/batch7.txt > matlab/results/queue_batch7.log 2>&1 &`。
> 结果汇总：`PY=<python> tools/refresh.sh`（= `collect_results.py` 把开发副本中的分段合并进 `matlab/results/`，不删分段、可重复执行 + `paper_numbers.py` + `plot_paper.py`）。旧的 S1/S2 合并文件已作为分段 `exp12_capacity_S1_ab.csv`、`S2_ab` 复制进开发副本。
> 论文第 5.3、5.4、5.5、5.7、5.8 节已按 S1/S2 定稿结果写好，待补处用 ⟨…⟩ 标出（`grep -n "⟨" paper/manuscript.md`）。

> **2026-10-23 07:40 更新：方向已调整为 v2，先读 [`方向调整_v2.md`](方向调整_v2.md)。** 新增四块（替代曲线、分布鲁棒承诺 + 命题 3、综合能源进入恢复故事、帕累托与 14 张图）及 IR-O 事后上界、暂停/恢复开销稳健性。
> 新实验 exp17–exp20 的代码已在仓库（`matlab/experiments/exp17_nodr.m`、`exp18_history.m`、`exp19_hindsight.m`、`exp20_capacity_configs.m`；`src/capacity_search.m`、`history_ctx.m`、`test_days.m`）。
> 作业清单：`tools/jobs/batch5.txt`（exp18/19/20）、`batch5b.txt`（电池替代曲线，固定接网上限重跑）、`batch6.txt`（资源消融、L_c、JR-S、补充实验、反弹）。
> 本容器中这三批作业在开发副本 `/home/user/dev/matlab` 里运行（结果在 `/home/user/dev/matlab/results`，作图脚本会同时读取该目录）；换容器后直接在仓库里运行 `tools/run_queue.sh P tools/jobs/batch5.txt` 等即可。
> 重要口径：电池、设备、资源、开销扫描都固定接网上限（`keep_Pcap`），否则接网上限会随典型日峰值变化（电池 12 MW 时 +1.04 MW）。

## 0 一句话现状

模型、全部实验（exp1–exp20）、作图、取数和论文全文均已完成并推送（分支 `claude/ae-reliable-capacity`）。主要结论：JR-D 可靠容量 S1/S2 7.5 MW、S3 6.5 MW，独立基准 1 MW 都不可靠；预见价值 15 min 4.0 MW → 3 h 0；预见价值相当于 9.3 MWh 电池（5.6 百万元），加接网也换不来；成本最优鲁棒承诺 7 MW 样本外 100% 足额，完美追索两阶段承诺只有 85%；两事件可靠可行域中 JR-D 接近物理能力边界，JR-M 低 2.6–4.3 MW，而完美信息下三种控制器的物理能力相同。

## 1 文档与代码索引

| 内容 | 位置 |
|---|---|
| 研究方案（主线，用户提供） | `docs/研究方案_AE重构.md` |
| 论文蓝图（结构、Highlights、贡献、算法包装、Table 2、八张图、写作规则） | `docs/论文蓝图_AE.md` |
| 论文初稿（英文；第 1–4 节、符号表、附录 A 已写，第 5–6 节和摘要待填数） | `paper/manuscript.md` |
| 本交接文档 | `docs/交接文档_AE.md` |
| 判定实验 G1（旧版三事件结果，已被本轮取代，作历史记录） | `docs/判定实验G1.md`，结果在 `matlab/results/legacy_G1/` |
| 理论证明（命题 1、原定理 1 = 现命题 2） | `docs/理论推导.md` |
| 参数 | `matlab/config/dcdr_params.m`（每项标注 [S]/[D]/[A]） |
| 实验入口与全部选项 | `matlab/main_run_all.m`（文件头注释） |
| 作业清单 | `tools/jobs/checkpoint.txt`、`batch2.txt`、`batch3.txt` |
| 并行运行、合并、取数、作图 | `tools/run_queue.sh`、`tools/merge_all.sh`、`tools/paper_numbers.py`、`tools/plot_paper.py`（样式在 `tools/paper_style.py`） |

旧分支：`claude/pensive-goodall-wm35vr`（P0 与 G1 阶段，已全部包含在新分支中）；`Firstthinking`（v1 初稿，勿改）。

## 2 已完成的工作

### 2.1 模型与程序修正（方案第七节 P0）

| 修正 | 位置 | 说明 |
|---|---|---|
| NoDR 无承诺结算 | `src/evaluate_run.m`（参数 `settle`）、`src/run_strategy.m` | 不计补贴与考核，只报物理指标 |
| 反弹考核默认 0 | `config/dcdr_params.m` | 3 元/kW 作为政策敏感性（exp8） |
| 足额与用户侧指标 | `src/evaluate_run.m`、`src/metrics_row.m` | `all_full`（每次 ≥98% 承诺）、`mean_delay_h`、`sla_use_pct`、`c3_carry_GPUh` 等 |
| 冷机 COP 用预测气温 | `src/load_inputs.m`、`src/make_scen.m` | 前 3 日均值，与光伏同源；`par.mpc.cop_fc='perfect'` 可恢复旧设定 |
| **结算约束 big-M** | `src/build_model.m`（'settle'、'commit'） | “计补贴削减 ≤ 实际削减”和“≥80% 有效”只对有效事件生效。原写法在事件已判无效时仍强制负荷不高于基线，使独立基准在高负荷日（第 17 日）储能阶段无可行解、回退到规则控制 |
| **回放不越限** | `src/plant_step.m` | 储能、蓄冷之后仍越限时削减可延后算力（先未到期、再到期，后者计逾期）；修正了 `grid` 匿名函数捕获旧 `pit` 的问题。原来 JR-M 有 0.2–0.5 MW 越限 |
| 场景 S1/S2/S3 | `src/set_scenario.m`、`dcdr_params.m` | S1 = 17、19 时两次约定响应（基础，符合江苏“每日不多于两次、累计不超过 2 h”）；`S2-<分钟>` = 第二次在第一次结束后若干分钟开始；S3 = 再加 21 时快速避峰（提前 3 h，系数 1.4），作压力扩展 |
| 日前机会约束选项 | `src/build_model.m`、`src/dayahead_commit.m`（参数 `rho`） | 场景足额指示变量 u_s，Σp_s u_s ≥ ρ |

### 2.2 实验代码（方案第五节五个模块）

| 模块 | 代码 | 输出 |
|---|---|---|
| 模块二 可靠容量（核心） | `experiments/exp12_capacity.m`（`E12_SCEN`、26 个不重复 PAI 测试日、承诺 3–9 MW） | `exp12_capacity_S1/S2/S3.csv` |
| 模块二 两事件可靠可行域 | `experiments/exp14_sweep.m`（`E14_SET='region'`） | `exp14_region_S2-30.csv` |
| 模块三 恢复机理 | `experiments/exp15_mechanism.m`（短间隔 S2-30 与长间隔 S2-180 对照） | `ts15_short_*.csv`、`ts15_long_*.csv`、`exp15_mechanism.csv` |
| 模块一 内生承诺 | `experiments/exp16_endogenous.m`（各策略用相同 5 个日前场景和相同目标回测自选统一承诺；记录日前期望成本与足额率；另有完美追索 MILP 与单事件评估作参照） | `exp16_dayahead_S1.csv`、`exp16_endogenous_S1.csv`、`exp16_packages_S1.csv` |
| 模块一 固定承诺 | 直接取 `exp12_capacity_*.csv` 中某一承诺的 26 日结果 | — |
| 模块四 敏感性 | `exp14_sweep.m`：`tau_gamma`（τ ∈ {0.25,0.5,1,2,3} h × γ ∈ {1.00,1.05,1.10,1.20}，C = 7 MW）、`single`（L_c ×0.5/0.75/1.25/1.5，BESS 0/2/4 MW） | `exp14_tau_gamma.csv`、`exp14_single.csv` |
| 消融（Table 2） | `exp14_sweep.m` `ablation`：仅 BESS、仅算力、算力+BESS（JR-D 控制器，承诺 1–8 MW）；其余档位取 exp12 的 IR/JR-M/JR-D | `exp14_ablation.csv` |
| 模块五 不确定性 | `exp4_montecarlo.m`（S3，E3 以 0.6 概率被调用、提前 1 h 确认；含 JR-S、JR-oracle；26 日） | `exp4_e3uncertain.csv` |
| 补充材料 | exp1（机理上界）、exp5（影子价格，S1）、exp8（反弹考核扫描）、exp11（命题 2 闭式解）、exp13（完美信息能力域） | 同名 CSV |

辅助函数：`src/ctx_with_par.m`（改参数后重建基线、并网上限、不响应参照）。

### 2.3 作图、取数与论文

- `tools/plot_paper.py`：Fig. 1–8 与 Fig. S1–S6，英文、Liberation Serif（Times 等宽替代）、PDF/SVG/PNG 输出到 `paper/figures/`。Fig. 1（系统与恢复通道示意）已生成。其余图的版式已用旧数据试画并调好（置信带、ΔC 标注、裁剪轴标注、山脊图、小提琴图等）。
- `tools/paper_numbers.py`：输出论文要用的全部数字（C_ρ、ΔC_ρ、I_ρ 及按测试日区组自助法的 95% 区间；固定承诺对比表；内生承诺表；敏感性、消融汇总）到 `paper/numbers.md`。
- `paper/manuscript.md`：Highlights、符号表（三级）、引言（背景 → 三段综述 → 缺口 → 三条编号贡献）、第 2–4 节（模型、可靠容量定义、命题、方法、Algorithm 1）、Table 2（✓/✕ 情景矩阵）、附录 A 参数表。

## 3 实验运行（换容器后必须重跑）

### 3.1 环境

```bash
apt-get install -y --no-install-recommends octave fonts-liberation fonts-noto-cjk
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install numpy pandas scipy matplotlib tabulate
```

系统自带的 python3 是 3.13，而 Ubuntu 的 matplotlib 包是为 3.12 编译的，直接 import 会报错，所以作图和取数要用 venv 里的 python。

### 3.2 运行顺序与耗时（4 核）

```bash
cd <repo>
nohup tools/run_queue.sh 4 tools/jobs/checkpoint.txt > matlab/results/queue_checkpoint.log 2>&1 &
# 可同时排队（总吞吐不变，只是各自变慢）：
nohup tools/run_queue.sh 4 tools/jobs/batch2.txt > matlab/results/queue_batch2.log 2>&1 &
nohup tools/run_queue.sh 4 tools/jobs/batch3.txt > matlab/results/queue_batch3.log 2>&1 &
# 进度：grep -h "exp12_S\|exp14\|exp16" matlab/results/stdout_*.txt ；完成：queue_*.log 出现 "queue done"
tools/merge_all.sh
/tmp/venv/bin/python tools/paper_numbers.py > paper/numbers.md
cd tools && /tmp/venv/bin/python plot_paper.py       # 全部图；也可只画某几张：plot_paper.py 3 5
```

| 作业 | 内容 | CPU 时间（约） |
|---|---|---|
| checkpoint（8 段） | S1、S2、S3 × 13 个承诺 × 26 日 × 4 策略 | 6.5 h |
| batch2 `e16S1` | 内生承诺 S1（**已完成入库，已注释掉**） | 1.6 h |
| batch2 `tg*`（4 段） | τ×γ 图 20 个工况 | 3.3 h |
| batch2 `sg*`、`ab*` | 单因素 7 工况；消融 3 工况 × 15 承诺 | 1.2 h + 1.3 h |
| batch2 `jrs`、`supp`、`rb` | JR-S 不确定性；exp1/5/11/13；反弹扫描 | 约 1.5 h |
| batch3 `reg*`（4 段）、`mech` | 两事件可靠可行域 25 对；典型日时序 | 3.3 h + 0.1 h |

合计约 19 CPU 小时，4 核约 5 小时。单次确定性闭环约 4 s/日，JR-S 约 60 s/日，每个承诺水平的 IR-O* 日前调优约 3 min。

### 3.3 运行注意

- `run_queue.sh` 会把作业文件路径转成绝对路径，空作业文件不会启动任何进程（之前因为相对路径读不到作业文件，空参数启动了全套 `main_run_all`）。
- 结束某个作业要按 PID 结束（`kill <pid>`）。不要用 `pkill -f <宽泛模式>`，它可能匹配到自己所在的 shell。
- Octave 运行中会重新加载被修改的 `.m` 文件。要么改代码前确认没有作业在跑，要么只做向后兼容的改动。
- `matlab/results/` 下的 `stdout_*.txt`、`queue_*.log` 和分段 CSV 已写进本地 `.git/info/exclude`（不随仓库走）；新容器里注意别把它们 `git add` 进去。
- 结果分段文件（`*_S1_a.csv`、`*_g100.csv`、`*_p1.csv` 等）由 `merge_all.sh` 合并并删除，不要提交分段文件。

## 4 结果

### 4.1 初步结果（运行日志摘录，2026-10-23 04:56；非最终，供判断方向）

每次事件均足额（≥98%）的天数占比，26 个测试日；列顺序 IR-O* / IR-P / JR-M / JR-D：

| 承诺 | S1（间隔 1 h） | S2（间隔 30 min） |
|---|---|---|
| 3.0 MW | 0.88 / 0.85 / 1.00 / 1.00 | 0.81 / 0.85 / 1.00 / 1.00 |
| 4.0 MW | 0.88 / 0.58 / 1.00 / 1.00 | 0.73 / 0.62 / 1.00 / 1.00 |
| 4.5 MW | 0.77 / 0.69 / 1.00 / 1.00 | 0.65 / 0.50 / 1.00 / 1.00 |
| 6.5 MW | 0.69 / 0.27 / 0.96 / 1.00 | 0.92 / 0.38 / 0.27 / 1.00 |
| 7.0 MW | 0.85 / 0.12 / 0.92 / 1.00 | 0.81 / 0.27 / 0.15 / 1.00 |
| 7.5 MW | 0.42 / 0.04 / 0.77 / 1.00 | 0.38 / 0.23 / 0.00 / 1.00 |
| 8.0 MW | 0.27 / 0.00 / 0.27 / 0.81 | 0.23 / 0.19 / 0.00 / 0.81 |

平均综合成本（千元/日，同顺序）：S1 7 MW 215 / 238 / 218 / 211；S2 7.5 MW 220 / 229 / 238 / 212。

τ×γ（C = 7 MW，间隔 15 min）足额天数占比：γ=1.00 → 0.46 / 0.15 / 0.00 / 0.96；γ=1.05 → 0.69 / 0.15 / 0.00 / 1.00；γ=1.10 → 0.73 / 0.31 / 0.00 / 1.00。

**读法（写进论文的主线）：**

1. **可靠容量**：JR-D 在 S1、S2 的 95% 足额可靠容量约 7.5 MW。最强独立基准在 3 MW 也只有 81–88% 的天数足额，因此 C_0.95 低于 3 MW。JR-M 在 S1 约 6.5 MW，在 S2 约 5 MW（需补 5–6 MW 数据确认）。
2. **跨事件远见的价值随间隔缩短而上升**：S1 中 JR-M 接近 JR-D；S2（30 min）中 JR-M 在 6.5 MW 以上崩溃（7.5 MW 时为 0%）；间隔 15 min 时 JR-M 在 7 MW 全部失败，而 JR-D 为 96–100%。
3. **独立恢复的问题与间隔关系不大**：IR-O*、IR-P 在低承诺下也会失败。逐日诊断（见 `判定实验G1.md` 第 4、5 节）表明，失败日实际负荷比固定基线高 1–4.5 MW，固定分摊或日前价格无法把缺口实时转给算力。
4. **成本**：JR-D 在高承诺下每日成本最低（比最强基准低 4–26 千元），且补贴收入最高。
5. **完美追索的日前 MILP 给出的承诺等于单事件能力**（S1 为 8.18/7.98 MW，S3 为 8.18/7.98/7.90 MW），高估了闭环可兑现的容量。所以承诺层采用“闭环回测 + 可靠率约束”（论文式 (15)），这一点已写进 `paper/manuscript.md` 4.1 节。

### 4.2 内生承诺 exp16（S1，已完成，2026-10-23 06:40）

日前回测（5 个日前场景，统一承诺 C；期望成本千元/日，括号内为日前场景中每次均足额的比例），列顺序 IR-O* / IR-P / JR-M / JR-D：

| C (MW) | 期望成本 | 日前足额比例 |
|---|---|---|
| 5.0 | 209.1 / 209.0 / 209.6 / 208.1 | 1 / 1 / 1 / 1 |
| 6.0 | 203.1 / 209.7 / 204.9 / 201.8 | 1 / 0.4 / 1 / 1 |
| 7.0 | 199.1 / 207.8 / 202.5 / 197.7 | 1 / 0.2 / 1 / 1 |
| 7.5 | 199.3 / 217.1 / 202.5 / 197.7 | 1 / 0 / 1 / 1 |
| 8.0 | 199.3 / 227.2 / 203.1 / 197.8 | 0.8 / 0 / 0.6 / 1 |
| 8.5 | 202.1 / 234.1 / 205.3 / 200.3 | 0 / 0 / 0 / 0 |

各承诺方式自选承诺后的样本外结果（26 日）：

| 承诺方式 | 承诺 (MW) | 每次足额的天数占比 | 相对不响应的收益（千元/日） |
|---|---|---|---|
| 回测 BT\|IR-O* | 7 / 7 | 0.85 | 40.3 |
| 回测 BT\|IR-P | 6.5 / 6.5 | 0.27 | 23.8 |
| 回测 BT\|JR-M | 7 / 7 | 0.92 | 37.3 |
| **回测 BT\|JR-D** | **7 / 7** | **1.00** | **44.8** |
| 完美追索日前 MILP RA\|JR-D | 8.18 / 7.98 | 0.85 | 44.7 |
| 单事件能力 SE\|IR-O* | 8.18 / 7.98 | 0.27 | 37.2 |
| 单事件能力 SE\|IR-P | 8.18 / 7.98 | 0.00 | 1.8 |

读法：同一套日前信息和同一目标下，JR-D 自选的 7 MW 在 26 日全部足额，收益最高；最强独立基准自选同样的 7 MW，但只有 85% 的天数足额，收益低 4.5 千元/日；按单事件能力承诺会严重超报（IR-P 几乎拿不到收益）。完美追索日前模型给出的承诺等于单事件能力，样本外足额率掉到 85%，支持论文式 (15) 的闭环回测承诺。注意：表中 BT 按式 (15) 取的是 ρ = 0 的最低期望成本承诺（脚本内置），ρ ∈ {0.8, 1.0} 的选法要按第 6 节第 4 步在 `paper_numbers.py` 里补。

## 5 关键决策记录（不要推翻）

- S1 双事件为基础算例，S3 三事件只作压力扩展；主算例不设反弹考核。
- 可靠容量用“每次事件均足额（≥98%）”口径，江苏 80% 有效口径另报。
- IR-O* 在每个承诺水平用日前场景回测重新调分摊比例 α，IR-P 用日前联合计划的通道影子价格，都是最强形态。
- 测试日是 DR 日之后的 26 个不重复 PAI 工作日（各配高温日气象与 Azure 推理日）；置信区间用按测试日的区组自助法。
- 两事件完美信息能力域（exp13）在 1 h 事件下几乎是矩形。可行域改用闭环可靠率口径（exp14 region），完美信息结果只放补充材料（Fig. S1），说明“物理能力相近、差别在运行与协调”。
- 不再新增实验种类；不开发新算法；不建作业级 GPU 仿真。

## 6 下一步清单（按顺序）

1. **通读全文**（英文润色、术语统一：IR-O\*/IR-P/JR-M/JR-D/JR-S、“firm capacity”“recovery channel”“debt”）；检查正文引用的图表编号与图题。
2. **参考文献**：已合并为 38 条、按首次引用顺序编号（未引用的旧条目已删去；中文文献已译为英文并注明 in Chinese）。2026-10-23 已用 Crossref / arXiv 核对：[14]、[15]、[20]、[21] 已补全作者、完整标题和卷号，[10] 补页码，[4]、[11]–[13]、[16]、[19]、[24]、[33] 标题与作者一致。仍需人工核对的只有 [17]、[18]（中文期刊，Crossref 未收录，请对照中文原文核对英文译名与卷期页码）。
3. **图题**：Fig. 1–14、S1–S7 的图题已写在 `paper/manuscript.md` 的 “Figure captions” 一节，图号按首次引用顺序编排（2026-10-23 晚调整：桑基图改为 Fig. 5，原 Fig. 5–10 顺延为 6–11；补充图依次为 S1 完美信息能力域、S2 承诺方法、S3 调用不确定、S4 反弹、S5 命题 1、S6 命题 2、S7 影子价格；`tools/plot_paper.py` 的函数名与输出文件名同步）；表格已按首次引用顺序编号（Table 1 场景、2 算法、3 场景矩阵、4 可靠容量、5 日前承诺）。
4. **投稿格式**：转 Elsevier LaTeX（elsarticle）或 Word；补 Graphical Abstract（可由 Fig. 1(b) 与 Fig. 7 拼成）；Highlights 每条 ≤ 85 字符（已满足）。
5. **可选补充**：S2 的完美追索两阶段承诺（exp16 目前只有 S1）；若审稿人追问半径选取，可在补充材料给出留一交叉验证半径的对照（`paper/numbers.md` 中 “eps LOO” 列已算好：S1 JR-M 0、S2 JR-M 0.015 MW → 4.5 MW）。
6. **复现**：换容器后若需重跑，用 `tools/jobs/batch7.txt`（约 4 小时，4 核）以及 checkpoint、batch2/3/5b/5c 中已完成的部分；结果用 `PY=python3 tools/refresh.sh` 汇总。

## 7 其他说明

- `matlab/figures/` 是 v1 和 G1 阶段的旧图（中文），论文用图一律在 `paper/figures/`。
- `tools/plot_results.py`、`tools/summarize_results.py`、`tools/g1_decision.py` 是旧版工具，只用于 `legacy_G1` 数据（如 `python3 tools/g1_decision.py matlab/results/legacy_G1`），新结果请用 `paper_numbers.py` 和 `plot_paper.py`。
- 参考论文 PDF（Zhang 等 2026）未入库（20 MB），其结构要点已整理进 `docs/论文蓝图_AE.md`。
