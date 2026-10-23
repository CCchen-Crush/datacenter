# Firm consecutive demand response of AI data centers through cross-event computing–storage recovery

Recovery-aware coordinated scheduling of computing workloads and energy storage for deliverable
consecutive demand response (DR) in an AI data-center integrated energy system (AIDC-IES) —
reproducible MATLAB / GNU Octave study prepared for *Applied Energy*.

* **Manuscript draft:** [`paper/manuscript.md`](paper/manuscript.md) · numbers: [`paper/numbers.md`](paper/numbers.md) · figures: [`paper/figures/`](paper/figures)
* **Research plan:** [`docs/研究方案_AE重构.md`](docs/研究方案_AE重构.md), current direction [`docs/方向调整_v2.md`](docs/方向调整_v2.md) · writing blueprint: [`docs/论文蓝图_AE.md`](docs/论文蓝图_AE.md) · results: [`docs/实验结果_AE.md`](docs/实验结果_AE.md) · theory: [`docs/理论推导.md`](docs/理论推导.md) · handover: [`docs/交接文档_AE.md`](docs/交接文档_AE.md)
* **Data (derived from public traces):** [`data/`](data), provenance in [`data_prep/README.md`](data_prep/README.md)

## Research question

Each DR event leaves two recovery debts — deadline-bound deferred computing work and a lossy storage
deficit — that are repaid through the same grid headroom before the next event. The study quantifies how
these debts limit the next deliverable reduction and how much **firm consecutive DR capacity**
$C^{firm}_\rho$ (largest uniform commitment delivered in full in every event with probability $\rho$) an
AIDC can offer with cross-event joint recovery, compared with tuned independent recovery (IR-O\*),
price-coordinated independent recovery (IR-P) and event-by-event joint recovery (JR-M).

## Scenarios and modules

| Scenario | Events | Role |
|---|---|---|
| S1 | 17–18 h and 19–20 h, agreed DR | base case (Jiangsu: ≤ 2 agreed events and ≤ 2 h per day) |
| S2 | second event 30 min after the first | short interval, strongest recovery competition |
| S3 | + rapid peak-shaving call 21–22 h (3 h notice) | high-stress extension |
| S4 | 26 operating days (PAI weekdays × weather × inference) and event-call uncertainty | reliability and economics |

| Module | Question | Experiment | Paper figure |
|---|---|---|---|
| Mechanism | How do the recovery debts of one event limit the next? | `exp15_mechanism`, `exp1_mechanism`, `exp11_stylized` | Fig. 3, 4, 11; S1, S2 |
| Firm capacity | How much more can the same equipment commit? | `exp12_capacity` (S1-S3, 1-9 MW x 26 days), `exp14_sweep` region | Fig. 5, 6 |
| Value decomposition | Coordination vs cross-event foresight, conditions | `exp20_capacity_configs` (tau), `exp14_sweep` (tau_gamma, single) | Fig. 7, 8 |
| System-level insight | Equivalent battery energy and connection capacity | `exp20_capacity_configs` (bess, gamma) | Fig. 9 |
| Commitment | Distributionally robust firm capacity (Proposition 3) | `exp18_history`, `exp16_endogenous` | Fig. 10, S7 |
| Integrated energy system | Who provides the recovery channel; device contribution | `exp15` time series, `exp20` (ies, resources) | Fig. 11, 12 |
| Users and economics | Service quality, costs, multi-day statistics | `exp12`, `exp17_nodr`, `exp4_montecarlo` (JR-S) | Fig. 13, 14, S4 |
| Robustness | Static split in hindsight, pause/resume overhead | `exp19_hindsight`, `exp20` (overhead) | text, supplementary |
| Supplementary | Physical capability regions, rebound policy, shadow prices | `exp13_region`, `exp8_rebound`, `exp5_shadow` | Fig. S3, S5, S6 |

## Reproduce

```bash
# experiments (GNU Octave 8 + glpk; each job is one process, P jobs run in parallel)
tools/run_queue.sh 4 tools/jobs/checkpoint.txt     # firm-capacity sweeps S1, S2, S3
tools/run_queue.sh 4 tools/jobs/batch2.txt         # endogenous commitment, sensitivity, ablation, uncertainty, supplementary
tools/run_queue.sh 4 tools/jobs/batch3.txt         # reliability region, typical-day mechanism
tools/run_queue.sh 4 tools/jobs/batch4.txt         # firm-capacity sweeps below 3 MW
tools/run_queue.sh 6 tools/jobs/batch5.txt         # historical back-test (DRO), substitution, interval, IES, overhead, hindsight
tools/run_queue.sh 2 tools/jobs/batch5b.txt        # BESS substitution with the connection kept (rerun)
tools/run_queue.sh 2 tools/jobs/batch6.txt         # resource ablation, lag bounds, JR-S uncertainty, supplementary
# merge parallel parts, then numbers and figures (Python 3 with numpy, pandas, scipy, matplotlib, tabulate)
tools/merge_all.sh
python3 tools/paper_numbers.py > paper/numbers.md
python3 tools/plot_paper.py                         # Fig. 1-14 and S1-S7 -> paper/figures/*.pdf|svg|png
```

Single experiments run from MATLAB/Octave with `cd matlab; RUN = 12; E12_SCEN = 'S2-30'; main_run_all`
(options are documented at the top of `matlab/main_run_all.m`).

Requirements: MATLAB R2019b+ with Optimization Toolbox, or Gurobi's MATLAB interface, or GNU Octave 6+
(built-in `glpk`). All randomness is replaced by deterministic scenario selection.

## Layout

```
data/                         derived inputs (PAI GPU trace, Azure LLM trace, ERA5 weather)
matlab/config/dcdr_params.m   parameters, each tagged [S] source / [D] data-derived / [A] assumption
matlab/src/build_model.m      joint computing-storage recovery MILP (backlog classes, IES, Jiangsu settlement)
matlab/src/dayahead_commit.m  day-ahead commitment (perfect-recourse stochastic MILP, optional chance constraint)
matlab/src/planner_jr.m       intraday cross-event joint recovery MPC (JR-D / JR-S / JR-M)
matlab/src/planner_iro.m      independent recovery benchmarks (IR-O*, IR-P)
matlab/src/plant_step.m       plant replay (EDF execution, IES balances, connection-limit enforcement)
matlab/src/set_scenario.m     event scenarios S1, S2-<min>, S3
matlab/experiments/           exp1 ... exp20 (exp17 no-DR reference, exp18 historical back-test, exp19 hindsight split, exp20 firm capacity by bisection)
matlab/results/               all result CSVs (see docs/实验结果_AE.md)
tools/                        job queue, merge, numbers and figure scripts
paper/                        manuscript draft, numbers, figures
```

## Data licences and citations

PAI trace: cite Weng et al., NSDI 2022. Azure LLM inference trace 2024: CC-BY 4.0, cite Stojkovic et al.,
HPCA 2025. Weather: Open-Meteo / ERA5, CC-BY 4.0. Only aggregated 15-min profiles derived from these sources
are stored in this repository.
