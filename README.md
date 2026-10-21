# 计及跨事件算储联合恢复的数据中心综合能源系统连续需求响应优化调度

Coordinated scheduling for consecutive demand response (DR) in AI data-center integrated energy
systems (AIDC-IES) considering cross-event computing-storage recovery — reproducible MATLAB study.

* **Paper idea, model, proposition, experiment design and results (Chinese):** [`docs/论文主要思路.md`](docs/论文主要思路.md)
* **MATLAB code:** [`matlab/`](matlab) — runs in MATLAB (Optimization Toolbox, or Gurobi) or GNU Octave (glpk)
* **Data (derived from public traces):** [`data/`](data), provenance in [`data_prep/README.md`](data_prep/README.md)
* **Figures:** [`matlab/figures/`](matlab/figures) (regenerate with `tools/plot_results.py` or `plot_all.m`)

## Key results (reproduced by `main_run_all`)

Same DR commitments and task SLAs for all strategies; Jiangsu settlement rules; 16 000-GPU AI data center
with PV, gas engine + absorption chiller, chilled-water storage and a 6 MW / 12 MWh battery.

| Joint recovery (scenario MPC) vs independent recovery | Fulfillment | Peak rebound | Comprehensive cost |
|---|---|---|---|
| 20 operating days, vs optimisation-based independent | **+12.7 pp** (99.1 % vs 86.4 %) | **−37.8 %** | **−15.7 %** |
| 20 operating days, vs rule-based independent | +25.5 pp | −42.7 % | −30.5 % |

* Mechanism: after a 6 MW × 2 h event, independent recovery leaves only 38–39 % of the next event's
  stand-alone capability for gaps ≤ 1 h; joint recovery from the *same* post-event state restores 96 %
  within 0.75 h (it repays only what the next event needs and carries long-deadline backlog).
* An analytical upper bound on the next event's deliverable capability (Proposition 1) holds in all 80
  tested cases and is within 0.05 MW of the optimum in 47 of them.
* Single-event day-ahead capability assessment over-commits by 35 %; under independent recovery those
  commitments are only 66.6 % fulfilled.

![mechanism](matlab/figures/fig02_mechanism.png)

## Quick start

```matlab
cd matlab
main_run_all          % all 7 experiments (MATLAB: ~10 min; Octave/glpk: ~35 min)
% QUICK = true; RUN = [2 5]; main_run_all   % fast subset
```

or from a shell: `octave --no-gui --eval "run('matlab/main_run_all.m')"`, then
`python3 tools/plot_results.py` for the figures (needs numpy, pandas, matplotlib).

Verification status: every experiment was run end-to-end in GNU Octave 8.4 + glpk (the committed
`matlab/results/*.csv` and `run_output.txt` come from that run, about 28 min). The figures in
`matlab/figures/` were rendered with `tools/plot_results.py`; `plot_all.m` (MATLAB graphics) could not be
rendered in the headless test environment, so check it on first use in MATLAB.

Requirements: MATLAB R2019b+ with Optimization Toolbox (`linprog`, `intlinprog`), or Gurobi's MATLAB
interface on the path, or GNU Octave 6+ (built-in `glpk`). No other toolboxes. All randomness is
replaced by deterministic scenario selection, so MATLAB and Octave give the same results up to solver
tolerances.

## Layout

```
data/                       derived inputs (PAI GPU trace, Azure LLM trace, ERA5 weather)
data_prep/prepare_data.py   rebuilds data/ from the raw public traces
matlab/main_run_all.m       entry point: runs Exp1-Exp7, writes results/*.csv and figures/*.png
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
matlab/experiments/         exp1 mechanism ... exp7 ablation
matlab/tests/               solver unit test and smoke tests
tools/plot_results.py       figure rendering from the CSV results
```

## Experiments

| # | Script | Question |
|---|---|---|
| 1 | `exp1_mechanism` | How the dual recovery demand of event A limits event B's deliverable capability vs interval τ and connection margin γ (+ Proposition 1 bound) |
| 2 | `exp2_main` | Joint vs independent recovery under identical commitments and SLAs (closed-loop MPC) |
| 3 | `exp3_sensitivity` | Event duration, interval, connection margin, commitment level; τ × γ map |
| 4 | `exp4_uncertainty` | 20 Monte-Carlo days (other trace days / hot days): deterministic vs scenario MPC |
| 5 | `exp5_shadow` | Shadow prices of the connection limit, stored energy and backlog |
| 6 | `exp6_commitment` | Coupled vs single-event day-ahead capability assessment |
| 7 | `exp7_ablation` | Value of each flexibility source; best static split for the independent strategy |

## Data licences and citations

PAI trace: please cite Weng et al., NSDI 2022. Azure LLM inference trace 2024: CC-BY 4.0, cite
Stojkovic et al., HPCA 2025. Weather: Open-Meteo / ERA5, CC-BY 4.0. Only aggregated 15-min profiles
derived from these sources are stored in this repository.
