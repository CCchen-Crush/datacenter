# 计及跨事件算储联合恢复的数据中心综合能源系统连续需求响应优化调度

Coordinated scheduling for consecutive demand response (DR) in AI data-center integrated energy
systems (AIDC-IES) considering cross-event computing-storage recovery — reproducible MATLAB study.

* **Research plan (Chinese):** [`docs/最终研究方案.md`](docs/最终研究方案.md); theory: [`docs/理论推导.md`](docs/理论推导.md); v1 paper text: branch `Firstthinking`
* **MATLAB code:** [`matlab/`](matlab) — runs in MATLAB (Optimization Toolbox, or Gurobi) or GNU Octave (glpk)
* **Data (derived from public traces):** [`data/`](data), provenance in [`data_prep/README.md`](data_prep/README.md)
* **Figures:** [`matlab/figures/`](matlab/figures) (regenerate with `tools/plot_results.py` or `plot_all.m`)

## Status (revision for Applied Energy)

The paper is being re-framed from "how much does joint recovery save" to **"how much consecutive-DR
capacity can the same equipment commit reliably"** (plan: [`docs/最终研究方案.md`](docs/最终研究方案.md)).
The draft-v1 numbers that used to be quoted here are withdrawn; v1 is kept on branch `Firstthinking`.

* Corrections P0 (done): no-DR reference settled without a commitment; rebound assessment off in the base
  case (`c_rb = 0`, Jiangsu rules alone; 3 CNY/kW is a policy sensitivity, files tagged `_crb3`); full-delivery
  and user-side indicators; chiller COP from the temperature forecast instead of the realised temperature;
  Proposition-1 bound paired with the curve it bounds in fig02.
* Decision experiment G1 (reliable-capacity curve Exp12, two-event capacity region Exp13): results and the
  resulting decision are in [`docs/判定实验G1.md`](docs/判定实验G1.md).

## Quick start

```matlab
cd matlab
main_run_all          % all 13 experiments (Octave/glpk, one process: several hours)
% QUICK = true; RUN = [2 5]; main_run_all   % fast subset
% RUN = 12; E12_CS = [4 4.5 5]; E12_TAG = '_p1'; main_run_all   % one part of the capacity sweep
```

or from a shell: `octave --no-gui --eval "run('matlab/main_run_all.m')"`; parts can run in parallel with
`tools/run_parallel.sh <tag> "RUN=[...];"`. Then `python3 tools/summarize_results.py`,
`python3 tools/g1_decision.py` and `python3 tools/plot_results.py` (need numpy, pandas, scipy, matplotlib).

Verification status: the committed `matlab/results/*.csv` come from GNU Octave 8.4 + glpk. Exp1, Exp3, Exp5
and Exp7 (perfect information) are from the previous code version and are not affected by the P0
corrections except that they lack the new indicator columns; Exp12 and Exp13 are from the current code.
All other experiments still have to be re-run. The figures in `matlab/figures/` are still the v1 figures.

Requirements: MATLAB R2019b+ with Optimization Toolbox (`linprog`, `intlinprog`), or Gurobi's MATLAB
interface on the path, or GNU Octave 6+ (built-in `glpk`). No other toolboxes. All randomness is
replaced by deterministic scenario selection, so MATLAB and Octave give the same results up to solver
tolerances.

## Layout

```
data/                       derived inputs (PAI GPU trace, Azure LLM trace, ERA5 weather)
data_prep/prepare_data.py   rebuilds data/ from the raw public traces
matlab/main_run_all.m       entry point: runs Exp1-Exp13, writes results/*.csv
matlab/config/dcdr_params.m all parameters, each tagged [S] source / [D] data-derived / [A] assumption
matlab/src/                 model and solvers
   build_model.m            joint computing-storage recovery MILP (dual state, IES, Jiangsu settlement)
   build_compute_model.m    IT-only scheduler (benchmark: independent recovery, stage 1)
   dayahead_commit.m        day-ahead two-stage stochastic commitment (coupled / single-event)
   planner_jr.m             proposed intraday scenario MPC (and deterministic / oracle variants)
   planner_iro.m            independent recovery, sequential optimisation (IT first, then storage)
   planner_irr.m            independent recovery, rule based (ASAP catch-up / recharge)
   plant_step.m             plant simulator (EDF backlog tracking, IES balances, limit enforcement)
   solve_milp.m             solver wrapper: Gurobi | linprog/intlinprog | Octave glpk
matlab/experiments/         exp1 mechanism ... exp13 two-event capacity region
matlab/tests/               solver unit test and smoke tests
tools/plot_results.py       figure rendering from the CSV results
tools/summarize_results.py  all numbers of the paper from the CSV results
tools/g1_decision.py        decision experiment G1: reliable capacity, capacity region, criteria
```

## Experiments

| # | Script | Question |
|---|---|---|
| 1 | `exp1_mechanism` | How the dual recovery demand of event A limits event B's deliverable capability vs interval τ and connection margin γ (+ Proposition 1 bound) |
| 2 | `exp2_main` | Joint vs independent recovery under identical commitments and SLAs (closed-loop MPC) |
| 3 | `exp3_sensitivity` | Event duration, interval, connection margin, commitment level; τ × γ map |
| 4 | `exp4_montecarlo` | 52 Monte-Carlo days (26 later PAI weekdays x 2 weather/inference days); event-call uncertainty of E3 |
| 5 | `exp5_shadow` | Shadow prices of the connection limit, stored energy and backlog |
| 6 | `exp6_commitment` | Coupled vs single-event day-ahead capability assessment |
| 7 | `exp7_ablation` | Value of each flexibility source; best static split for the independent strategy |
| 8 | `exp8_rebound` | Rebound assessment as a policy parameter (sweep of c_rb) |
| 9 | `exp9_price` | DR unit price x shortfall coefficient |
| 10 | `exp10_realism` | Liquid cooling, IT ramp limits, load-up charge, GPU power capping |
| 11 | `exp11_stylized` | Closed form of Theorem 1 vs LP |
| 12 | `exp12_capacity` | Reliable capacity: uniform commitment 4-9 MW x 20 PAI days, IR-O*, IR-P, JR-M, JR-D (G1a) |
| 13 | `exp13_region` | Two-event capacity region C2_max(C1): JR, IR post-state + joint recovery, JR-M, IR-O* (G1b) |

Base case: Jiangsu settlement rules alone (`c_rb = 0`). Result files without a tag use it; `_crb3`
marks the policy sensitivity with a gap-rebound assessment of 3 CNY/kW per event.

## Data licences and citations

PAI trace: please cite Weng et al., NSDI 2022. Azure LLM inference trace 2024: CC-BY 4.0, cite
Stojkovic et al., HPCA 2025. Weather: Open-Meteo / ERA5, CC-BY 4.0. Only aggregated 15-min profiles
derived from these sources are stored in this repository.
