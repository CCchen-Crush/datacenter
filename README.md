# Firm consecutive demand response of AI data centers through cross-event computing–storage recovery

Recovery-aware coordinated scheduling of computing workloads and energy storage for deliverable
consecutive demand response (DR) in an AI data-center integrated energy system (AIDC-IES) —
reproducible MATLAB / GNU Octave study prepared for *Applied Energy*.

* **Manuscript:** source [`paper/manuscript_source.md`](paper/manuscript_source.md) (symbolic equation and reference keys) → numbered [`paper/manuscript.md`](paper/manuscript.md) · two-column PDF [`paper/latex/manuscript.pdf`](paper/latex/manuscript.pdf) · Word [`paper/word/`](paper/word) · numbers: [`paper/numbers.md`](paper/numbers.md) · figures: [`paper/figures/`](paper/figures)
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
| Mechanism | How do the recovery debts of one event limit the next? | `exp15_mechanism`, `exp1_mechanism`, `exp11_stylized` | Fig. 3, 4, 5; S3, S4 |
| Firm capacity | How much more can the same equipment commit? | `exp12_capacity` (S1-S3, 1-9 MW x 26 days), `exp20` (region), `exp13_region` | Fig. 6, 7, S1; Table 5 |
| Value decomposition | Coordination vs cross-event foresight, conditions | `exp20_capacity_configs` (tau), `exp14_sweep` (tau_gamma, single) | Fig. 8, 9 |
| System-level insight | Equivalent battery energy and connection capacity, for every target firm capacity | `exp20_capacity_configs` (bess, bessM, gamma) | Fig. 10 |
| Commitment | Distributionally robust firm capacity (Proposition 4) | `exp18_history`, `exp16_endogenous` | Fig. 11, S2; Table 6 |
| Integrated energy system | Who provides the recovery channel; device contribution; PUE and CO2 | `exp15` time series, `exp20` (ies, resources), `exp17_nodr` | Fig. 5, 12; Section 5.7.3 |
| Users and economics | Service quality, costs, benefit versus commitment, multi-day statistics | `exp12`, `exp17_nodr` | Fig. 13, 14, 15 |
| Uncertainty and rebound | Event-call uncertainty (JR-S), post-event rebound as a policy parameter | `exp4_montecarlo`, `exp8_rebound` | Fig. 16; Section 5.9 |
| Robustness | Static split in hindsight, pause/resume overhead, lag bounds | `exp19_hindsight`, `exp20` (overhead), `exp14_sweep` (single) | Section 5.8.4, Fig. 9d |
| Supplementary | Physical capability regions, commitment methods, propositions, channel price | `exp13_region`, `exp16`, `exp1`, `exp11`, `exp5_shadow` | Fig. S1-S5 |

## Reproduce

```bash
# experiments (GNU Octave 8 + glpk; each job is one process, P jobs run in parallel; every experiment writes its CSV
# after each commitment or strategy, so an interrupted job keeps its finished part)
tools/run_queue.sh 4 tools/jobs/checkpoint.txt     # firm-capacity sweeps S1, S2 (3-9 MW) and S3 (8-9 MW)
tools/run_queue.sh 4 tools/jobs/batch3.txt         # typical-day mechanism (mech)
tools/run_queue.sh 4 tools/jobs/batch2.txt         # endogenous commitment (exp16), interval x connection margin
tools/run_queue.sh 4 tools/jobs/batch5b.txt        # BESS substitution (connection kept); batch5c: JR-M on the BESS sweep
tools/run_queue.sh 4 tools/jobs/batch7.txt         # everything else: low commitments, S3, historical back-test (DRO),
                                                    # connection margin, IES devices, interval, two-event region,
                                                    # hindsight split, overhead, lag bounds, JR-S, supplementary
# collect the parts, then numbers and figures (Python 3 with numpy, pandas, scipy, matplotlib, tabulate)
PY=python3 tools/refresh.sh                         # collect_results.py + paper/numbers.md + Fig. 1-16, S1-S5
python3 tools/plot_paper.py GA                      # graphical abstract (13 x 5 cm)
# manuscript: edit paper/manuscript_source.md, then
python3 tools/resolve_manuscript.py                 # numbers equations and references -> paper/manuscript.md, paper/labels.json
python3 tools/plot_paper.py 2                       # Fig. 2 reads its equation numbers from paper/labels.json
python3 tools/build_latex.py                        # two-column PDF in paper/latex/ (pdflatex, pandoc >= 3)
python3 tools/build_word.py                         # two-column Word files in paper/word/ (pandoc >= 3); WORD_LAYOUT=floats
                                                    # places full-width figures and tables in text boxes at the page top
```

`tools/collect_results.py` merges the parts of a run copy (`DCDR_RUN_RESULTS`, default `/home/user/dev/matlab/results`)
into `matlab/results/` without deleting them; run the queues from such a copy when the code may change while they run.

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
paper/                        manuscript source and numbered Markdown, labels.json, numbers, figures
paper/latex/                  two-column PDF and its LaTeX source (built by tools/build_latex.py)
paper/word/                   Word files: manuscript.docx (two columns), highlights.docx, supplementary_material.docx,
                              graphical_abstract.{pdf,png,tif} (built by tools/build_word.py)
```

## Data licences and citations

PAI trace: cite Weng et al., NSDI 2022. Azure LLM inference trace 2024: CC-BY 4.0, cite Stojkovic et al.,
HPCA 2025. Weather: Open-Meteo / ERA5, CC-BY 4.0. Only aggregated 15-min profiles derived from these sources
are stored in this repository.
