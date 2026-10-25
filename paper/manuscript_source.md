# Recovery-aware coordinated scheduling of computing workloads and energy storage for deliverable consecutive demand response in AI data centers

> Source of the manuscript for *Applied Energy*. Equations carry `\label{eq:…}` keys and are cited with `\eqref{…}`, references are cited with `[@key]`; `tools/resolve_manuscript.py` numbers both in order of appearance and writes `paper/manuscript.md` and `paper/labels.json`. The numbers of the Abstract, Section 5 and Section 6 come from `tools/paper_numbers.py` applied to `matlab/results/` (see `paper/numbers.md`), and all figures from `tools/plot_paper.py` (`paper/figures/`).

## Highlights

- Model computing backlog and storage deficit as debts sharing one recovery channel.
- Commit firm consecutive DR capacity from closed-loop capability with Wasserstein DRO.
- Deliver 7.5 MW firmly by cross-event joint recovery, 94 % of physical capability.
- Show that foresight adds up to 4.0 MW of firm capacity at short event intervals.
- Quantify a 9.3 MWh battery saving from foresight that connection cannot replace.

## Abstract

AI data centers (AIDCs) are becoming large flexible loads that are called upon several times within one evening peak. However, each demand-response (DR) event leaves deferred computing work and depleted storage that compete for grid headroom before the next event, so the capacity an AIDC can firmly commit is decided during recovery. This study develops a recovery-aware coordinated scheduling framework for consecutive DR of an AIDC integrated energy system. A cross-event recovery model couples deadline-bound computing backlogs, battery and cold-storage deficits and combined cooling, heating and power through one recovery channel, and bounds the next deliverable reduction in closed form. The firm consecutive DR capacity, the largest uniform commitment delivered in full in every event with a prescribed probability, is certified day-ahead from the controller's closed-loop capability within a Wasserstein ambiguity set, solved exactly by sorting through its dual, and delivered by an intraday cross-event joint recovery model predictive controller. Case studies on a 16 000-GPU data center under the Jiangsu DR rules, over 26 operating days from public traces, show that cross-event joint recovery firmly delivers 7.5 MW with two events, 94 % of the physical capability, and 6.5 MW with three, whereas tuned and price-coordinated independent recovery is not firm even at 1 MW. Cross-event foresight adds up to 4.0 MW at short intervals and substitutes 9.3 MWh of battery. The cost-optimal robust commitment is delivered in full on every operating day, against 85 % for a perfect-recourse two-stage commitment, and earns 43–45 thousand CNY per day.

**Keywords:** AI data center; consecutive demand response; computing–energy coupling; firm deliverable capacity; distributionally robust optimisation; integrated energy system

## Nomenclature

Symbols used only within one proof are defined where they appear.

**Abbreviations**

| | |
|---|---|
| AIDC | AI data center |
| BESS | Battery energy storage system |
| CCHP | Combined cooling, heating and power |
| CI | Confidence interval |
| COP | Coefficient of performance |
| DR | Demand response |
| DRO | Distributionally robust optimisation |
| GPU | Graphics processing unit |
| IES | Integrated energy system |
| IR-O\* | Independent recovery with a day-ahead tuned static split |
| IR-P | Independent recovery with day-ahead channel-price coordination |
| IR-PD | Independent recovery with iterative two-way channel-price coordination |
| JR-D | Cross-event joint recovery, deterministic MPC (proposed) |
| JR-M | Event-by-event joint recovery |
| JR-S | Cross-event joint recovery, scenario MPC |
| KKT | Karush–Kuhn–Tucker |
| LP | Linear programming |
| MILP | Mixed-integer linear programming |
| MPC | Model predictive control |
| PUE | Power usage effectiveness |
| PV | Photovoltaic |
| SAA | Sample average approximation |
| SLA | Service-level agreement |
| SOC | State of charge |
| SR-D | Staged recovery with the information and joint delivery of JR-D |
| TES | Thermal (chilled-water) energy storage |
| TOU | Time of use |

**Parameters**

| | |
|---|---|
| $\Delta t$ | Time step (0.25 h) |
| $T_H$ | MPC horizon (18 h) |
| $T$ | Last step of the optimisation horizon |
| $\mathcal K$ | Set of DR events |
| $\mathcal T_k$ | Steps of event $k$ |
| $D_k$ | Duration of event $k$ (h) |
| $s_k$ | First step of event $k$ |
| $e_k$ | Last step of event $k$ |
| $\tau$ | Interval between two consecutive events (h) |
| $C_k$ | DR commitment of event $k$ (MW) |
| $\pi_t$ | TOU energy price (CNY/MWh) |
| $\pi_k$ | DR unit price of event $k$ (CNY/MWh) |
| $\kappa$ | Shortfall assessment coefficient |
| $c^{rb}$ | Rebound assessment price (CNY/MW per event) |
| $\mathcal W_k$ | Post-event window of event $k$ (2 h) |
| $\delta^{val}$ | Planning margin above the validity threshold (MW) |
| $M$ | Big-M constant |
| $P^{base}_t$ | DR baseline (MW) |
| $P^{noDR}_t$ | Import of the no-DR operation on the realised data (MW) |
| $\hat P$ | Typical-day peak import (MW) |
| $\gamma$ | Connection margin over the typical-day peak |
| $P^{cap}$ | Grid connection limit, $\gamma\hat P$ (MW) |
| $P^{min}$ | Minimum grid import (MW) |
| $N^{GPU}$ | Number of GPUs |
| $p^{idle}$ | Idle power per GPU (MW) |
| $p^{dyn}$ | Dynamic power per busy GPU (MW) |
| $P^{oth}$ | Other IT power (MW) |
| $P^{fix}$ | Schedule-independent IT power (MW) |
| $\kappa^{inf}$ | Dynamic-power factor of inference |
| $u^{max}$ | Maximum schedulable GPU fraction |
| $a_{c,t}$ | Arrival rate of deferrable work of class $c$ (busy GPUs) |
| $L_c$ | Lag bound (deadline) of class $c$ (h) |
| $\bar B_{c,t}(L_c)$ | Class-$c$ work that arrived within the last $L_c$ hours (GPU·h) |
| $G^{inf}_t$ | Busy GPUs of online inference |
| $G^{fix}_t$ | Busy GPUs of non-deferrable training |
| $\zeta$ | Distribution and air-handling losses as a share of the IT power |
| $P^{aux}$ | Auxiliary facility power (MW) |
| $\theta$ | Heat to be removed per unit of IT power |
| $Q_0$ | Base cooling load (MW~th~) |
| $\mathrm{COP}_t$ | Electric chiller COP (temperature dependent) |
| $\mathrm{COP}^{AC}$ | Absorption chiller COP |
| $\bar Q^{EC}$ | Cooling capacity of the electric chillers (MW~th~) |
| $\bar Q^{AC}$ | Cooling capacity of the absorption chiller (MW~th~) |
| $\bar Q^{T}$ | TES power rating (MW~th~) |
| $\bar P^{GT}$ | Gas-engine rating (MW) |
| $R^{GT}$ | Gas-engine ramp limit per step (MW) |
| $k^h$ | Recoverable heat per unit of gas-engine output |
| $\eta^{GT}$ | Gas-engine electrical efficiency |
| $c^{gas}$ | Gas price (CNY/MWh of fuel) |
| $\bar P^{PV}_t$ | Available PV power (MW) |
| $\eta_c$ | BESS charging efficiency |
| $\eta_d$ | BESS discharging efficiency |
| $c^{deg}$ | BESS degradation cost (CNY/MWh) |
| $\underline E$ | Lower bound of the BESS energy (MWh) |
| $\bar E$ | Upper bound of the BESS energy (MWh) |
| $\bar P^{B}$ | BESS power rating (MW) |
| $\eta^T_c$ | TES charging efficiency |
| $\eta^T_d$ | TES discharging efficiency |
| $\sigma$ | TES hourly loss rate |
| $\underline S$ | Lower bound of the TES energy (MWh~th~) |
| $\bar S$ | Upper bound of the TES energy (MWh~th~) |
| $c^{jct}$ | Delay price of deferred work (CNY per GPU·h·h) |
| $c^{late}$ | Lateness price of overdue work (CNY per GPU·h·h) |
| $c^{E}$ | Terminal value of the BESS deficit (CNY/MWh) |
| $c^{S}$ | Terminal value of the TES deficit (CNY/MWh~th~) |
| $c^{B}$ | Terminal value of the remaining backlog (CNY per GPU·h) |
| $E^{ref}_t$ | BESS energy of the no-DR operation planned day-ahead (MWh) |
| $S^{ref}_t$ | TES energy of the no-DR operation planned day-ahead (MWh~th~) |
| $e^{grid}$ | Grid emission factor (t CO~2~/MWh) |
| $e^{gas}$ | Emission factor of natural gas (t CO~2~/MWh of fuel) |
| $\alpha$ | Compute share of the reduction in the static split of IR-O\* |
| $\rho$ | Target reliability of the firm capacity |
| $\epsilon_f$ | Metering tolerance of full delivery (2 %) |
| $\mathcal G$ | Commitment grid |
| $\Delta_{\mathcal G}$ | Step of the commitment grid (MW) |
| $\Omega^{DA}$ | Historical days used day-ahead |
| $\Omega$ | Operating (test) days |
| $N$ | Number of historical days |
| $\varepsilon$ | Radius of the 1-Wasserstein ambiguity set (MW) |
| $\varepsilon_N$ | Expected 1-Wasserstein estimation error (MW) |
| $\epsilon^{C}$ | Weight of the commitment in the two-stage model (CNY/MW) |
| $p_\omega$ | Probability of scenario $\omega$ |
| $\eta$ | Round-trip efficiency of recharging |
| $g$ | Additional gas-engine output available for recovery (MW) |
| $L$ | Lag bound of the single-class model of Proposition 2 (h) |
| $h$ | Constant channel width in Proposition 2 (MW) |

**Variables**

| | |
|---|---|
| $y_{c,t}$ | Busy GPUs executing class-$c$ work |
| $B_{c,t}$ | Backlog of class $c$ (GPU·h) |
| $v_{c,t}$ | Overdue work of class $c$ (GPU·h) |
| $P^{IT}_t$ | IT power (MW) |
| $P^{grid}_t$ | Grid import (MW) |
| $P^{ch}_t$ | BESS charging power (MW) |
| $P^{dis}_t$ | BESS discharging power (MW) |
| $E_t$ | Energy stored in the BESS (MWh) |
| $Q^{TC}_t$ | TES charging (MW~th~) |
| $Q^{TD}_t$ | TES discharging (MW~th~) |
| $S_t$ | Cold stored in the TES (MWh~th~) |
| $P^{GT}_t$ | Gas-engine output (MW) |
| $H^{AC}_t$ | Heat supplied to the absorption chiller (MW~th~) |
| $Q^{EC}_t$ | Electric chiller output (MW~th~) |
| $P^{PV}_t$ | PV output (MW) |
| $\psi_t$ | Facility energy per GPU·h of catch-up (MWh) |
| $X_t$ | Computing debt (MWh) |
| $\mathbf x_{e_k}$ | Recovery state at the end of event $k$ |
| $H_k$ | Nominal recovery channel between events $k$ and $k+1$ (MWh) |
| $H^{act}_k$ | Actual, state-dependent recovery channel (MWh) |
| $D^E_t$, $D^S_t$ | Storage debts of the BESS (MWh) and the TES (MWh~th~) |
| $\mathrm{PUE}(\mathcal T')$ | Electric power usage effectiveness over the period $\mathcal T'$ |
| $\bar r_k$ | Average reduction of event $k$ against the baseline (MW) |
| $z_k$ | Validity indicator of event $k$ |
| $R_k$ | Paid reduction of event $k$ (MW) |
| $s^{f}_k$ | Shortfall of event $k$ (MW) |
| $\Delta P^{rb}_k$ | Peak post-event rebound of event $k$ (MW) |
| $J$ | Comprehensive cost of the DR day (CNY) |
| $J^{op}$ | Operating cost of electricity, gas and storage degradation (CNY) |
| $J^{qos}$ | Service-quality cost of delayed and overdue work (CNY) |
| $J^{DR}$ | DR revenue (CNY) |
| $J^{sf}$ | Shortfall assessment (CNY) |
| $J^{rb}$ | Rebound assessment (CNY) |
| $J^{term}$ | Terminal value of the remaining debts (CNY) |
| $\mathrm{CO_2}$ | Daily CO~2~ emissions (t) |
| $u_\omega(C)$ | Full-delivery indicator of realisation $\omega$ at commitment $C$ |
| $C^{firm}_\rho$ | Firm consecutive DR capacity at reliability $\rho$ (MW) |
| $\hat C^{firm}_\rho$ | SAA estimate of the firm capacity (MW) |
| $\mathcal C_\rho$ | Reliability region of the commitments |
| $\Delta C_\rho$ | Capacity gain between two strategies (MW) |
| $\Gamma_B$ | Deliverable reduction of event B (MW) |
| $\Gamma^0_B$ | Single-event capability of event B (MW) |
| $\Gamma^E$ | Energy bound of Proposition 1 (MW) |
| $\Gamma^P$ | Power bound of Proposition 1 (MW) |
| $H^{eff}$ | Effective recovery channel (MWh) |
| $\mathcal H$ | Feasible allocations of the channel to catch-up and recharge |
| $X^{due}_A$ | Part of the computing debt of event A that falls due before the end of event B (MWh) |
| $\bar X_B$ | Deadline-limited virtual capacity at the end of event B (MWh) |
| $E_s$ | Dischargeable energy of the BESS and the TES after event A (MWh) |
| $P_s$ | Discharge power of the BESS and the TES (MW) |
| $p_f$ | Deferrable power that can be paused in event B (MW) |
| $c^*$ | Necessary catch-up before the next event (MWh) |
| $s^{req}$ | Necessary recharge before the next event (MWh) |
| $\lambda^{el}_t$ | Multiplier of the electric balance, the channel price (CNY/MWh) |
| $\chi_t$ | Multiplier of the cooling balance (CNY/MWh~th~) |
| $\lambda^{cap}_t$ | Multiplier of the connection limit (CNY/MWh) |
| $\lambda^{ev}_t$ | Marginal settlement value of the import in event steps (CNY/MWh) |
| $\nu_t$ | Multiplier of the BESS balance (CNY/MWh) |
| $\mu_{c,t}$ | Multiplier of the class-$c$ backlog balance (CNY per GPU·h) |
| $\mathcal L$ | Lagrangian of the joint recovery model |
| $\xi_d$ | Closed-loop capability of the controller on day $d$ (MW) |
| $J_d(C)$ | Cost of the controller on day $d$ at commitment $C$ (CNY) |
| $\bar J(C)$ | Mean back-tested cost at commitment $C$ (CNY) |
| $\hat P_N$ | Empirical distribution of the capability |
| $\mathcal B_\varepsilon(\hat P_N)$ | 1-Wasserstein ambiguity set |
| $\mathcal D_C$ | Days that deliver commitment $C$ |
| $\delta_d(C)$ | Capability margin of day $d$ (MW) |
| $n(C)$ | Number of days that deliver commitment $C$ |
| $q(C)$ | Slack $n(C)-\rho N$ |
| $w_d$ | Probability mass moved from day $d$ |
| $m^*_C(\varepsilon)$ | Largest probability mass removable within the transport budget |
| $\lambda$ | Multiplier of the transport budget |
| $C^{DRO}_\rho(\varepsilon)$ | Distributionally robust firm capacity (MW) |
| $\Phi_\rho(C)$ | Robust reliability margin (MW) |
| $C^*$ | Cost-optimal day-ahead commitment (MW) |
| $\hat{\mathbf x}_t$ | Measured recovery state at step $t$ |
| $\hat{\mathbf w}_{\cdot|t}$ | Forecasts available at step $t$ |
| $\mathbf u$ | Decisions of the MPC over its horizon |
| $\mathcal U_t$ | Feasible set of the MPC problem at step $t$ |

## 1. Introduction

The rapid growth of artificial intelligence (AI) is reshaping electricity demand. The International Energy Agency projects global data-center consumption to rise from about 415 TWh in 2024 to about 945 TWh by 2030 [@iea2025], and data centers already account for 4.4 % of electricity use in the United States [@shehabi2024]. Grid connection capacity has become the binding constraint for new AI campuses [@kim2026], and load flexibility is increasingly treated as a condition for faster interconnection: curtailing large loads for 0.25–1 % of the year would accommodate 76–126 GW of new load in 22 US balancing areas [@norris2025]. AI data centers (AIDCs) are already operated as grid-interactive assets. A field demonstration in Phoenix reduced the power of a production GPU cluster by 25 % for three hours without violating service levels [@colangelo2026], and utilities have signed demand-response (DR) agreements that target machine-learning workloads [@google2025]. DR programs reward this flexibility at increasing frequency. In Jiangsu, China, the 2024 implementation rules allow up to two agreed DR events per day plus rapid peak-shaving calls at short notice, settled on the average reduction against a five-day baseline [@jiangsu2024]. Consecutive events within one evening peak are therefore the normal operating condition of a DR-participating AIDC.

Each event leaves recovery debts behind. Deferred training and batch work accumulates as a backlog that must be completed before its service deadline, and the storage that covered part of the reduction must be recharged. Both debts are repaid by drawing power above the baseline through the same grid headroom before the next event starts. The reduction that an AIDC can deliver in the next event is therefore decided by how it recovers from the previous one, and this cross-event coupling determines how much flexibility the grid can count on.

In the area of data-center DR and computing flexibility, workload shifting and local generation were introduced by Liu et al. [@liu2013] and reviewed in [@wierman2014; @chen2020]. Recent studies quantify the flexibility of AI workloads: Acun et al. reported 18–55 % power flexibility of AI data centers [@acun2026], Wang et al. reshaped the power profiles of large language model workloads to provide load flexibility [@wang2025llm], Du et al. added inference quantization as a DR lever [@du2026], Chen and Zheng showed that deferring workloads reduces interconnection cost with diminishing returns in the delay window [@chenzheng2026], and Williams et al. framed power-flexible AI data centers as grid-responsive compute [@williams2026]. In *Applied Energy*, data-center load models for DR [@zhou2025], the DR potential of liquid-cooled data centers [@chen2026], a four-level joint dispatch of data-center DR [@han2024], energy sharing in data-center clusters with integrated demand response [@bian2025] and multi-energy portfolios of zero-carbon data-center buildings under proactive DR programs [@xu2023] have been developed. Overall, existing studies evaluate the curtailment capability of a single event, whereas the recovery state that one event passes on to the next remains insufficiently explored.

In the area of computing–energy coupling in data-center integrated energy systems (IES), data centers increasingly operate with combined cooling, heating and power (CCHP), cold storage and batteries [@lin2025; @fan2026]. Zhang et al. coupled computing and electricity in a bi-level capacity planning model of a data-center cluster under supply–demand uncertainty [@zhang2026], Liu scheduled an internet data center together with a regional integrated energy system through electricity–heat–water coupling [@liu2024], and the cooling and waste-heat recovery of data centers have been optimised with model predictive control and thermal storage [@hou2023] and with physics-guided reinforcement learning and aquifer thermal storage [@zhangy2026]. Batteries support the online operation of distributed data centers under uncertain workloads and prices [@sun2023], the risk-aware coordinated scheduling of AI data centers with decoupled multi-layer workload models [@xie2027] and the operation of hyperscale AI data centers under connect-and-manage interconnection [@lu2026], and the reliability impact of energy-system flexibility on data centers has been quantified in [@yu2026]. These studies capture the coupling between computing, power and heat within a scheduling period. Overall, they treat the computing backlog and the state of charge as internal operating states rather than as debts that are inherited across DR events and decide the next deliverable reduction.

In the area of deliverability and commitment of flexible resources, aggregate flexibility models describe the power–energy envelope of homogeneous devices [@hao2015], and Evans et al. derived recovery guarantees for aggregated energy storage that must be restored between service requests [@evans2022]. Li distinguished eligible AI workloads from dependable load relief [@li2026], and the scenario approach provides probabilistic guarantees for closed-loop constraint satisfaction [@schildbach2014]. The delivered reduction is measured against a customer baseline, whose estimation error enters the settlement directly [@wangz2024; @wangy2026]. Distributionally robust chance constraints over Wasserstein ambiguity sets offer data-driven reliability guarantees [@esfahani2018; @duan2018] and secure end-user flexibility for independent aggregators [@paredes2026]. Their two-stage form, solved by column-and-constraint generation [@zeng2013], evaluates the second stage with perfect recourse and therefore measures physical capability rather than the deliverability of the controller that operates the resource. Overall, recovery guarantees have been developed for one type of resource with one type of debt, whereas an AIDC holds two heterogeneous debts at once: computing debt is lossless but deadline-bound, storage debt is lossy but has no deadline, and both compete for the same recovery channel.

Despite substantial progress in data-center DR, computing–energy coupling and flexibility commitment, three research gaps remain. First, the heterogeneous recovery debts that one DR event leaves for the next, and their competition for a shared grid connection, have not been modelled in an AIDC integrated energy system. Second, no capacity metric quantifies what a given controller delivers in every event of a DR day, and commitments derived from physical capability overstate it. Third, coordinated scheduling that exploits cross-event foresight during recovery is lacking, and its value relative to coordination alone, the conditions under which it is valuable and its equivalent in battery and connection capacity are unknown. Consequently, a framework that sizes and delivers the consecutive DR commitments of an AIDC from its recovery is still lacking. Table 1 contrasts this study with the three closest research directions.

**Table 1.** Positioning of this study against the closest research directions.

| Research direction | Focus of existing studies | Increment of this study |
|---|---|---|
| AI workload modelling and computing–storage scheduling | Power flexibility of AI workloads in a single event and real-time regulation of computing and batteries [@acun2026; @wang2025llm; @du2026; @xie2027] | Recovery state that one event passes on to the next, and its effect on the next deliverable reduction |
| Flexibility envelopes and recovery guarantees | Power–energy envelopes and recovery guarantees for one type of resource and debt [@hao2015; @evans2022], dependable AI load relief [@li2026] | Two heterogeneous debts, deadline-bound computing and lossy storage, sharing one recovery channel with CCHP and cold storage |
| Dependable operation and commitments of data centers | Computing service under supply limits [@lu2026; @yu2026]; chance-constrained and two-stage commitments with perfect recourse [@esfahani2018; @zeng2013; @paredes2026] | Consecutive DR commitments sized by the closed-loop capability of the controller that delivers them |

To address these gaps, this paper develops a recovery-aware coordinated scheduling framework for consecutive DR of an AIDC integrated energy system. The framework models the recovery debts of every event, commits the firm consecutive capacity of the controller day-ahead and delivers it with cross-event joint recovery in real time. The main contributions are summarised as follows.

(1) A cross-event heterogeneous recovery model of the AIDC integrated energy system is developed. Deadline-bound computing backlogs of three workload classes and lossy battery and cold-storage deficits are modelled as recovery debts that share one grid recovery channel, coupled with the electric, cooling and heat balances of the CCHP-based energy system and the Jiangsu settlement rules. Three propositions bound the deliverable reduction of the next event, give the closed-form minimum recovery interval together with the conditions under which joint recovery is valuable, and show from the Karush–Kuhn–Tucker conditions that a single channel price values both debts.

(2) A firm consecutive DR capacity metric and its distributionally robust commitment are proposed. The firm capacity is the largest uniform commitment delivered in full in every event with a prescribed probability, generalised to a multi-event reliability region. The day-ahead commitment is derived from the closed-loop capability of the controller on historical days with a distributionally robust chance constraint over a 1-Wasserstein ambiguity set; a fractional-knapsack representation and its linear-programming dual reformulate the worst-case failure probability, and Proposition 4 solves the robust capacity exactly by sorting. Wasserstein ambiguity sets are an established tool [@esfahani2018], and controller-dependent deliverability has been studied for aggregated storage [@evans2022] and AI workloads [@li2026]; the contribution here is to apply the robust commitment to the closed-loop capability of a controller that delivers consecutive events with heterogeneous debts. Unlike a perfect-recourse two-stage commitment, which measures physical capability, the robust commitment refers to the controller that operates the resource, and its reliability is reported at three levels: the guarantee within the ambiguity set, the full-delivery share on independent operating days and the statistical confidence bound of that share.

(3) A recovery-aware coordinated scheduling framework is established and validated at the system level. The robust commitment is coupled with an intraday cross-event joint recovery model predictive controller (MPC). A controlled comparison with tuned and price-coordinated independent recovery and event-by-event joint recovery on 26 operating days separates the value of coordination from that of cross-event foresight, converts the capacity gain into equivalent battery energy and connection capacity, and quantifies the contribution of the gas engine, absorption chiller and cold storage together with the energy efficiency and emissions of the facility.

## 2. System architecture and consecutive demand response problem

### 2.1. Physical architecture of the AIDC integrated energy system

The AIDC integrated energy system considered in this paper couples computing, power, heat and cooling (Fig. 1a). It consists of four subsystems. The energy supply subsystem comprises the grid connection with limit $P^{cap}$ and 8 MWp of rooftop and adjacent PV. The energy conversion and storage subsystem comprises a 3 MW gas engine whose recovered heat drives a single-effect absorption chiller (CCHP) and a 6 MW/12 MWh BESS. The cooling subsystem comprises electric chillers, whose COP depends on the ambient temperature, the absorption chiller and a 10 MWh chilled-water TES. The computing subsystem hosts 16 000 H100-class GPUs in 2 000 eight-GPU nodes; its load consists of online inference and non-deferrable training (Flex 0) and three classes of deferrable training and batch work (C1–C3) that tolerate a delay up to their lag bounds $L_c$ = 0.5, 1.5 and 3 h, following the flexibility tiers of industrial AI-DR programs [@colangelo2026]. A dispatch layer sets the day-ahead DR commitments and operates all flexible resources in real time.

### 2.2. Computing–energy–thermal coupling mechanism

The four subsystems are coupled through three energy flows that close one loop (markers 1–4 in Fig. 1a). (i) Computing–electricity: every busy GPU draws dynamic power, so the scheduling of deferrable work sets the IT power, and every deferred GPU·h acts as a lossless virtual discharge that must be recharged before its deadline. (ii) Electricity–cooling: the IT power is dissipated as heat, which the electric chillers, the absorption chiller and the TES remove; the chiller power, divided by a COP that falls with the ambient temperature, returns to the electric balance. (iii) Heat recovery: the exhaust heat of the gas engine drives the absorption chiller, so one MW of engine output displaces both grid import and chiller power. Through these flows, deferring computing work, discharging the BESS, discharging the TES and running the gas engine all act on the same grid import, which is the quantity that the DR operator settles, and all draw on the same headroom when the debts are repaid. The recovery channel is therefore a system-level resource that the four subsystems share.

### 2.3. Consecutive DR events and recovery debts

A DR operator confirms events $k\in\mathcal K$ with commitments $C_k$. Under the Jiangsu rules [@jiangsu2024], an event is valid when the average reduction against the five-day baseline reaches 80 % of the commitment, and the payment is proportional to the reduction up to 120 % of the commitment. The unit price of agreed response is cleared by bidding below a cap of 3 CNY/kWh, which the base case assumes. The rules pay nothing for an invalid event and levy no monetary penalty on a shortfall; to represent the cost of non-performance, this paper assesses a shortfall at $\kappa$ times the event price, a modelling assumption ($\kappa$ = 1 in the base case; Section 5.10.3 examines lower prices, higher delay costs and $\kappa$ = 0). Three event scenarios are studied (Section 5.1): two agreed one-hour events at 17:00 and 19:00 (S1, the rule-compliant base case), the same events with the interval shortened to 30 min (S2), and a high-stress extension with a third, rapid peak-shaving event at 21:00 announced 3 h ahead (S3).

During event $k$, the AIDC defers class-$c$ work and discharges storage. At the end of the event it holds the recovery state $\mathbf x_{e_k}=(B_{1},B_{2},B_{3},E,S)$: the backlogs are deadline-bound computing debts, and the deficits of the stored energy and cold below their no-DR reference trajectories (Section 3.2) are lossy storage debts. Both are repaid between events by importing power above the baseline (Fig. 1b), so both compete for the recovery channel
$$H_k=\sum_{t=e_k+1}^{s_{k+1}-1}\max\{P^{cap}-P^{base}_t,\,0\}\,\Delta t. \label{eq:channel}$$
Because it is measured against the baseline, which is known day-ahead, $H_k$ is the nominal channel. The channel that is physically available on the operating day is the state-dependent actual channel
$$H^{act}_k=\sum_{t=e_k+1}^{s_{k+1}-1}\max\{P^{cap}-P^{noDR}_t,\,0\}\,\Delta t, \label{eq:actchannel}$$
where $P^{noDR}_t$ is the import of the no-DR operation on the realised computing load, inference load, PV output and chiller COP. The two coincide when the no-DR import equals the baseline and otherwise differ by the baseline error; Section 5.1.3 compares them on the operating days. The scheduling problem is to decide which debt to repay first so that the reduction deliverable in event $k+1$ is maximised; the commitment problem is to determine how much consecutive capacity the AIDC can firmly offer when recovery is coordinated across events.

## 3. Cross-event recovery model of the AIDC integrated energy system

This section formulates the operation of the AIDC integrated energy system over a DR day as a mixed-integer linear program (MILP) with a 15-min step $\Delta t$. The model underlies both the intraday controller and the closed-loop capability of Section 4, and its theoretical properties (Section 3.7) explain how the recovery of one event shapes the next.

### 3.1. IT power and computing backlog model

The IT power follows the number of busy GPUs. With the idle and other IT power collected in $P^{fix}=N^{GPU}p^{idle}+P^{oth}$, it is
$$\begin{aligned}P^{IT}_t={}&P^{fix}+p^{dyn}\Big(\kappa^{inf}G^{inf}_t+G^{fix}_t\\&+\textstyle\sum_{c}y_{c,t}\Big),\end{aligned} \label{eq:it}$$
where online inference draws the fraction $\kappa^{inf}$ of the dynamic power of a training GPU. Deferred work of class $c$ accumulates in the backlog
$$B_{c,t}=B_{c,t-1}+\big(a_{c,t}-y_{c,t}\big)\Delta t, \label{eq:backlog}$$
which is bounded by the deadlines of the work,
$$0\le B_{c,t}\le\bar B_{c,t}(L_c)+v_{c,t},\qquad v_{c,t}\ge0, \label{eq:deadline}$$
where $\bar B_{c,t}(L_c)$ is the work that arrived within the last $L_c$ hours and is therefore not yet due, and $v_{c,t}$ is overdue work priced at $c^{late}$. The schedulable GPUs are limited by the utilisation cap $u^{max}$,
$$\textstyle\sum_c y_{c,t}\le u^{max}N^{GPU}-G^{inf}_t-G^{fix}_t . \label{eq:gpu}$$
Each GPU·h of backlog requires the facility energy
$$\psi_t=\big(1+\zeta+\theta/\mathrm{COP}_t\big)\,p^{dyn} \label{eq:psi}$$
when it is caught up, including distribution losses and cooling, so the computing debt
$$X_t=\psi_t\textstyle\sum_cB_{c,t} \label{eq:debt}$$
behaves like the discharge of a lossless virtual storage whose recharge has deadlines.

### 3.2. Electrochemical and cold storage model

The BESS evolves as
$$E_t=E_{t-1}+\Big(\eta_cP^{ch}_t-\frac{P^{dis}_t}{\eta_d}\Big)\Delta t, \label{eq:bess}$$
$$\underline E\le E_t\le\bar E,\qquad 0\le P^{ch}_t,\,P^{dis}_t\le\bar P^{B}, \label{eq:bessbound}$$
and the chilled-water TES as
$$\begin{aligned}S_t={}&(1-\sigma\Delta t)\,S_{t-1}\\&+\Big(\eta^T_cQ^{TC}_t-\frac{Q^{TD}_t}{\eta^T_d}\Big)\Delta t,\end{aligned} \label{eq:tes}$$
$$\underline S\le S_t\le\bar S,\qquad 0\le Q^{TC}_t,\,Q^{TD}_t\le\bar Q^{T}. \label{eq:tesbound}$$
The storage debts are measured against the reference trajectories $E^{ref}_t$ and $S^{ref}_t$ of the no-DR operation planned day-ahead,
$$D^E_t=\max\{E^{ref}_t-E_t,\,0\},\qquad D^S_t=\max\{S^{ref}_t-S_t,\,0\}, \label{eq:sdebt}$$
so that only the energy and cold that DR has drawn below normal operation count as debt, not the free room up to $\bar E$ and $\bar S$. These debts are lossy: every MWh drawn for recharging returns only the round-trip efficiency in the next event.

### 3.3. CCHP, cooling supply and grid interaction model

The heat of the IT equipment, $\theta P^{IT}_t$, and the base cooling load $Q_0$ are removed by the electric chillers, the absorption chiller driven by recovered heat and the TES,
$$\begin{aligned}&Q^{EC}_t+\mathrm{COP}^{AC}H^{AC}_t+Q^{TD}_t-Q^{TC}_t\\&\qquad=\theta P^{IT}_t+Q_0,\end{aligned} \label{eq:cool}$$
where the heat supplied to the absorption chiller is limited by the recoverable heat of the gas engine,
$$H^{AC}_t\le k^hP^{GT}_t . \label{eq:heat}$$
The electric balance includes the distribution losses, the auxiliary load and the chiller power,
$$\begin{aligned}&P^{grid}_t+P^{PV}_t+P^{GT}_t+P^{dis}_t-P^{ch}_t\\&\qquad=(1+\zeta)P^{IT}_t+P^{aux}+\frac{Q^{EC}_t}{\mathrm{COP}_t}.\end{aligned} \label{eq:elec}$$
The grid import respects the connection limit and a minimum import,
$$P^{min}\le P^{grid}_t\le P^{cap}, \label{eq:grid}$$
the gas engine its rating and ramp limit,
$$0\le P^{GT}_t\le\bar P^{GT},\qquad \big|P^{GT}_t-P^{GT}_{t-1}\big|\le R^{GT}, \label{eq:gt}$$
the PV the available power,
$$0\le P^{PV}_t\le\bar P^{PV}_t, \label{eq:pv}$$
and the chillers their capacities,
$$0\le Q^{EC}_t\le\bar Q^{EC},\qquad 0\le\mathrm{COP}^{AC}H^{AC}_t\le\bar Q^{AC}. \label{eq:chill}$$
Through \eqref{eq:cool}–\eqref{eq:chill}, deferring computing work lowers both the IT power and the chiller power, and recovered heat and stored cold widen the headroom $P^{cap}-P^{grid}_t$ on which recovery draws. The coupling of the computing debt to the electric balance through $\psi_t$ is what makes the backlog compete with the storage for the recovery channel \eqref{eq:channel}.

### 3.4. Settlement of consecutive DR events

The average reduction of event $k$ against the baseline is
$$\bar r_k=\frac{1}{D_k}\sum_{t\in\mathcal T_k}\big(P^{base}_t-P^{grid}_t\big)\Delta t . \label{eq:rbar}$$
With the validity indicator $z_k\in\{0,1\}$, the paid reduction $R_k$ and the shortfall $s^{f}_k$, the Jiangsu settlement reads
$$\bar r_k\ge z_k\,(0.8\,C_k+\delta^{val})-M(1-z_k), \label{eq:valid}$$
$$0\le R_k\le1.2\,C_kz_k,\qquad R_k\le\bar r_k+M(1-z_k), \label{eq:pay}$$
$$s^{f}_k\ge C_k-\bar r_k,\qquad s^{f}_k\ge0, \label{eq:short}$$
where $\delta^{val}$ is a planning margin above the 80 % threshold and the big-M terms deactivate the payment constraints of an invalid event. The Jiangsu rules contain no post-event assessment. To examine one as a policy parameter (Section 5.9.2), the peak rebound of event $k$ above the baseline in the post-event window $\mathcal W_k$ (2 h) is bounded by
$$\Delta P^{rb}_k\ge P^{grid}_t-P^{base}_t\quad\forall t\in\mathcal W_k,\qquad \Delta P^{rb}_k\ge0, \label{eq:rebound}$$
and priced at $c^{rb}$ per event, with $c^{rb}=0$ in the base case. The rule that the load during an event may not exceed the baseline maximum and the connection limit \eqref{eq:grid} carry slacks with large penalties in the planning model, which keep every MPC step feasible under forecast errors; the plant replay enforces the physical limits (Section 4.2).

### 3.5. Comprehensive cost objective and energy–carbon indicators

The operator minimises the comprehensive cost of the DR day,
$$J=J^{op}+J^{qos}-J^{DR}+J^{sf}+J^{rb}+J^{term}, \label{eq:obj}$$
which comprises the operating cost of electricity, gas and storage degradation,
$$\begin{aligned}J^{op}=\sum_t\Big[&\pi_tP^{grid}_t+\frac{c^{gas}}{\eta^{GT}}P^{GT}_t\\&+c^{deg}\big(P^{ch}_t+P^{dis}_t\big)\Big]\Delta t,\end{aligned} \label{eq:jop}$$
the service-quality cost of delayed and overdue work,
$$J^{qos}=\sum_t\sum_c\big(c^{jct}B_{c,t}+c^{late}v_{c,t}\big)\Delta t, \label{eq:jqos}$$
the DR revenue, the shortfall assessment and the rebound assessment,
$$\begin{aligned}&J^{DR}=\textstyle\sum_k\pi_kD_kR_k,\qquad J^{sf}=\textstyle\sum_k\kappa\,\pi_kD_ks^{f}_k,\\&J^{rb}=c^{rb}\textstyle\sum_k\Delta P^{rb}_k,\end{aligned} \label{eq:jdr}$$
and the terminal value of the remaining debts at the last step $T$ of the horizon,
$$\begin{aligned}J^{term}={}&c^{E}D^E_T+c^{S}D^S_T+c^{B}\textstyle\sum_cB_{c,T}.\end{aligned} \label{eq:jterm}$$
The storage debts are those of \eqref{eq:sdebt} at the end of the horizon; $c^{E}$ and $c^{S}$ lie just above the recharge costs of the BESS and the TES at the valley price, and $c^{B}$ values the backlog left at the end of the evaluation window at its energy cost, so that no strategy can shift cost beyond the window. The reported costs value the end state of every strategy relative to the no-DR operation in the same way.

Two indicators describe the energy efficiency and the emissions of the facility; they are evaluated on the closed-loop trajectories and do not enter the objective. The electric power usage effectiveness over a period $\mathcal T'$ is the ratio of the electricity consumed by the facility to that of the IT equipment,
$$\mathrm{PUE}(\mathcal T')=\frac{\sum_{t\in\mathcal T'}\big[(1+\zeta)P^{IT}_t+P^{aux}+Q^{EC}_t/\mathrm{COP}_t\big]}{\sum_{t\in\mathcal T'}P^{IT}_t}, \label{eq:pue}$$
and the CO~2~ emissions of the evaluation window are
$$\mathrm{CO_2}=\sum_t\Big(e^{grid}P^{grid}_t+\frac{e^{gas}}{\eta^{GT}}P^{GT}_t\Big)\Delta t, \label{eq:co2}$$
with the average emission factor of the East China grid, $e^{grid}$ = 0.5617 t/MWh [@mee2024], and the default factor of natural gas, $e^{gas}$ = 56.1 t/TJ = 0.202 t/MWh of fuel [@ipcc2006].

### 3.6. Firm consecutive DR capacity

Let $\omega\in\Omega$ denote a realisation of computing arrivals, inference load, weather and event calls, and $\bar r_{k,\omega}(C)$ the reduction delivered in event $k$ by a given operating strategy when the uniform commitment $C$ is in force. Every event is delivered in full when
$$u_\omega(C)=\begin{cases}1,&\bar r_{k,\omega}(C)\ge(1-\epsilon_f)\,C\ \ \forall k\in\mathcal K,\\0,&\text{otherwise},\end{cases} \label{eq:ind}$$
with a metering tolerance $\epsilon_f$ = 2 %. The **firm consecutive DR capacity** at reliability $\rho$ is the largest uniform commitment that the strategy delivers in full in every event with probability $\rho$,
$$C^{firm}_\rho=\max\big\{C:\ \mathbb E_\omega\big[u_\omega(C)\big]\ge\rho\big\}. \label{eq:firm}$$
Its multi-event generalisation is the reliability region
$$\begin{aligned}\mathcal C_\rho=\Big\{&(C_1,\dots,C_K):\\&\Pr_\omega\big[\bar r_{k,\omega}\ge(1-\epsilon_f)\,C_k\ \forall k\big]\ge\rho\Big\},\end{aligned} \label{eq:region}$$
which shows how a higher commitment in one event compresses the deliverable space of the next. $C^{firm}_\rho$ is a deliverability metric for the grid and is reported separately from the settlement validity \eqref{eq:valid}.

Because a larger commitment can only tighten the delivery requirement, the indicator \eqref{eq:ind} is non-increasing in $C$ for a fixed realisation, and \eqref{eq:firm} is evaluated by sample average approximation (SAA). For every $C$ on a grid $\mathcal G$, the strategy is simulated in closed loop on the realisations $\omega\in\Omega$, and
$$\begin{aligned}\hat C^{firm}_\rho=\max\Big\{&C\in\mathcal G:\ \frac{1}{|\Omega|}\sum_{\omega\in\Omega}u_\omega(C')\ge\rho\\&\forall C'\in\mathcal G,\ C'\le C\Big\}.\end{aligned} \label{eq:saa}$$
Confidence intervals of $\hat C^{firm}_\rho$ and of the capacity gain $\Delta C_\rho$ between two strategies are obtained by a block bootstrap over operating days.

The SAA share is an estimate, so three levels of reliability evidence are distinguished. (i) Within the ambiguity set of Section 4.1, Proposition 4 guarantees the full-delivery probability $\rho$ for every capability distribution in the Wasserstein ball around the historical days; the guarantee carries over to the operating days only if their distribution lies in the ball. (ii) On independent operating days, the empirical full-delivery share defines $\hat C^{firm}_\rho$. (iii) Under the unknown true distribution and independent operating days, the one-sided Clopper–Pearson bound converts the share into a confidence statement: if all $n$ operating days are delivered in full, the full-delivery probability exceeds $0.05^{1/n}$ with 95 % confidence, which is 0.891 for $n$ = 26 and 0.962 for $n$ = 78, so at least 59 days without failure are needed to support $\rho$ = 0.95 at this confidence. The firm capacities of Section 5 are estimates in the sense of (ii); Section 5.6 reports (i) and (iii) alongside them.

### 3.7. Theoretical properties of cross-event recovery

This section derives three properties of the model \eqref{eq:it}–\eqref{eq:jterm} for two consecutive events A and B: a bound on the reduction deliverable in B (Proposition 1), the value of repaying the debts in the right order (Proposition 2) and the price that couples the two debts (Proposition 3). The proofs are given in Appendix B, and Table 2 lists the assumptions, the scope, the differences from the full model and the numerical verification of these propositions and of Proposition 4 (Section 4.1.2).

#### 3.7.1. Capability bound of the next event

Let $\mathcal I=(e_A,s_B)$ be the interval of length $\tau$ between the events and $\mathcal T_B$ the steps of event B with duration $D_B$. Two assumptions are made. (H1) Without DR the grid import equals the baseline and the storage is idle in $\mathcal I\cup\mathcal T_B$. (H2) $\psi_t$ and $\mathrm{COP}_t$ are constant in $\mathcal I\cup\mathcal T_B$; otherwise all bounds below hold with the largest $\psi_t$ of the interval. (H1) is not needed in its strict form. If the no-DR operation imports $P^{noDR}_t\ne P^{base}_t$ or uses its storage, as in the case study, where the BESS shaves the evening peak, all relations below hold with $P^{base}_t$ replaced by $P^{noDR}_t$, the storage actions counted as deviations from the no-DR storage schedule and the channel taken as the actual channel \eqref{eq:actchannel}; the bound then applies to the true reduction against $P^{noDR}_t$, and the settled reduction differs from it by the baseline error $P^{base}_t-P^{noDR}_t$. Under (H1), the balances \eqref{eq:it}, \eqref{eq:cool} and \eqref{eq:elec} give the deviation of any schedule from the baseline,
$$\begin{aligned}&P^{grid}_t-P^{base}_t=\psi\textstyle\sum_c\big(y_{c,t}-a_{c,t}\big)\\&\quad+P^{ch}_t-P^{dis}_t+\dfrac{Q^{TC}_t-Q^{TD}_t}{\mathrm{COP}}-\Delta g_t,\end{aligned} \label{eq:dev}$$
where the first term is catch-up (positive) or deferral (negative) of computing work and $0\le\Delta g_t\le g$ is the additional gas-engine output including its absorption-chiller equivalent. Every reduction in B and every MWh of recovery in $\mathcal I$ therefore passes through the same import.

Event A leaves the computing debt $X_A=\psi\sum_cB_c(e_A)$, of which the part $X^{due}_A$ falls due before $e_B$, and the dischargeable storage energy $E_s=\eta_d(E_A-\underline E)+\eta^T_d(S_A-\underline S)/\mathrm{COP}$ with the discharge power $P_s=\bar P^{B}+\bar Q^{T}/\mathrm{COP}$. The recovery channel $H$ adds the additional gas-engine output $g\tau$ to \eqref{eq:channel}. Further, $\bar X_B=\psi\sum_c\bar B_c(e_B)$ is the deadline-limited virtual capacity at the end of B, $p_f=\psi\sum_c\bar a_{c,B}\min(L_c,D_B)/D_B$ the deferrable power that can still be paused in B, $G^{free}$ the number of GPUs free for catch-up in the interval, $W^{sw}$ the work arriving in $\mathcal I$ with a deadline after $e_B$, which earliest-deadline-first execution can swap with due backlog, $\eta$ the round-trip efficiency of recharging and $\Gamma^0_B$ the single-event capability of B.

**Proposition 1 (capability bound of the next event).** Under (H1) and (H2), the reduction deliverable in event B satisfies
$$\Gamma_B\le\min\big\{\Gamma^0_B,\ \Gamma^E,\ \Gamma^P\big\}, \label{eq:bound}$$
with the energy bound
$$\Gamma^E=\frac{\bar X_B-X_A+E_s+H^{eff}}{D_B}+g, \label{eq:ge}$$
in which the effective channel
$$H^{eff}=\begin{cases}H,&H\le X_A,\\X_A+\eta\,(H-X_A),&H>X_A\end{cases} \label{eq:heff}$$
credits catch-up one to one and recharge at the round-trip efficiency, and the power bound
$$\begin{aligned}\Gamma^P=\max_{(H_c,H_s)\in\mathcal H}\Big\{&p_f-\frac{\max\{X^{due}_A-H_c-W^{sw},\,0\}}{D_B}\\&+\min\Big(P_s,\ \frac{E_s+\eta H_s}{D_B}\Big)\Big\}+g\end{aligned} \label{eq:gp}$$
over the feasible allocations of the channel to catch-up ($H_c$) and recharge ($H_s$),
$$\begin{aligned}\mathcal H=\big\{(H_c,H_s):\ &H_c+H_s\le H,\\&0\le H_c\le\psi G^{free}\tau,\ 0\le H_s\le\bar P^{B}\tau\big\}.\end{aligned} \label{eq:hset}$$

The energy bound \eqref{eq:ge} states that the channel, the task deadlines and the stored energy jointly determine the next deliverable reduction, and the power bound \eqref{eq:gp} accounts for the backlog of A that falls due within B. The bound is tight when the backlogs reach their deadline limits at the end of B, the storage is empty at the end of B and the channel is used in the order catch-up, then recharge. In the mechanism experiment on the DR day (80 combinations of interval, connection margin and event durations, each evaluated at the state that event A leaves), the bound is never violated. It lies within 0.05 MW of the optimal deliverable reduction in 60 % and 55 % of the cases of the two event layouts, mostly where the single-event capability $\Gamma^0_B$ binds, and up to 2.0 MW above it otherwise (supplementary Fig. S3), so it is valid but not always tight.

#### 3.7.2. Value of joint recovery

The bound \eqref{eq:ge} credits catch-up before recharge, but only the part of the debt that would otherwise fall due in B needs to be caught up. Proposition 2 quantifies this in a single-class model with constant arrival power $p_f$, lag bound $L\ge D_B$, debt $X\le p_fL$ at the start of the interval and a constant channel width $h\le\bar P^{B}$, so that $H=h\tau$. The necessary catch-up is
$$c^*=\max\{X-p_f(L-D_B),\,0\}, \label{eq:cstar}$$
the work that would fall due before the end of B.

**Proposition 2 (value of joint recovery).** Joint recovery repays only the necessary catch-up and uses the rest of the channel for recharge, whereas independent recovery repays the full debt first:
$$\begin{aligned}c_{JR}&=\min\{H,c^*\},\quad s_{JR}=\max\{H-c^*,0\},\\c_{IR}&=\min\{H,X\},\quad s_{IR}=\max\{H-X,0\}.\end{aligned} \label{eq:alloc}$$
The joint allocation maximises the deliverable reduction of B, and the minimum intervals after which B regains its single-event capability differ by
$$\tau^*_{IR}-\tau^*_{JR}=\frac{\min\{X,\ p_f(L-D_B)\}}{h}. \label{eq:tau}$$
Joint recovery has no value when the deadline is not longer than the next event ($L\le D_B$), when B needs no storage, or when the channel is either too narrow for more than the necessary catch-up or wide enough to repay both debts within the interval.

Proposition 2 underlies the mechanism of Section 5.2: long-deadline work need not be caught up immediately, which frees the recovery channel for the storage that the next event needs. With several classes, the necessary catch-up is $\sum_c\max\{X_c-p_{f,c}(L_c-D_B),0\}$, so the long-deadline class C3 is carried across events first.

#### 3.7.3. Single price of the recovery channel

For fixed validity indicators $z_k$, the model \eqref{eq:it}–\eqref{eq:jterm} is a linear program whose Lagrangian, restricted to the balances that couple the two debts, is
$$\begin{aligned}\mathcal L={}&J+\sum_t\lambda^{el}_t\Big[(1+\zeta)P^{IT}_t+P^{aux}+\frac{Q^{EC}_t}{\mathrm{COP}_t}\\&\qquad+P^{ch}_t-P^{grid}_t-P^{PV}_t-P^{GT}_t-P^{dis}_t\Big]\Delta t\\&+\sum_t\chi_t\big[\theta P^{IT}_t+Q_0-Q^{EC}_t\\&\qquad-\mathrm{COP}^{AC}H^{AC}_t-Q^{TD}_t+Q^{TC}_t\big]\Delta t\\&+\sum_t\lambda^{cap}_t\big(P^{grid}_t-P^{cap}\big)\Delta t\\&+\sum_t\nu_t\Big[E_t-E_{t-1}-\Big(\eta_cP^{ch}_t-\frac{P^{dis}_t}{\eta_d}\Big)\Delta t\Big]\\&+\sum_{c,t}\mu_{c,t}\big[B_{c,t-1}+(a_{c,t}-y_{c,t})\Delta t-B_{c,t}\big]+\mathcal L^{rest},\end{aligned} \label{eq:lagr}$$
where $\lambda^{el}_t$, $\chi_t$, $\lambda^{cap}_t\ge0$, $\nu_t$ and $\mu_{c,t}$ are the multipliers of the electric balance \eqref{eq:elec}, the cooling balance \eqref{eq:cool}, the connection limit \eqref{eq:grid}, the BESS balance \eqref{eq:bess} and the backlog balance \eqref{eq:backlog}, and $\mathcal L^{rest}$ collects the remaining constraints, among them the settlement \eqref{eq:valid}–\eqref{eq:short}.

**Proposition 3 (single channel price).** Let $\lambda^{ev}_t\ge0$ be the marginal settlement value of the import in the steps of an event (zero outside events). When the minimum import does not bind, the Karush–Kuhn–Tucker (KKT) conditions of \eqref{eq:lagr} give
$$\begin{aligned}\lambda^{el}_t&=\pi_t+\lambda^{cap}_t+\lambda^{ev}_t,\\\eta_c\,\nu_t&=\lambda^{el}_t+c^{deg}\quad\text{(interior charging)},\\\mu_{c,t}&=\psi_t\,\lambda^{el}_t\quad\text{(interior execution)}.\end{aligned} \label{eq:kkt}$$
When catch-up and recharge are both interior in step $t$,
$$\frac{\mu_{c,t}}{\psi_t}=\lambda^{el}_t=\eta_c\,\nu_t-c^{deg}, \label{eq:price}$$
so one price of the recovery channel values both debts.

The channel price $\lambda^{el}_t$ exceeds the energy price by the scarcity of the connection, $\lambda^{cap}_t$, and by the settlement value of the next event, $\lambda^{ev}_t$. Independent recovery schedules catch-up against $\pi_t$ or against its own share of the commitment, ignores $\lambda^{cap}_t$ and breaks the equality \eqref{eq:price}. Proposition 3 characterises the prices at a joint optimum; it does not imply that a price alone coordinates the subsystems. The response of a linear IT model to a given price is generally not unique, and the validity indicators make the full model mixed-integer. Section 4.3 therefore includes two price-coordinated benchmarks, the one-way day-ahead price of IR-P and the iteratively updated two-way price of IR-PD.

**Table 2.** Assumptions, scope and numerical verification of the propositions.

| Proposition | Assumptions | Scope of the result | Difference from the full model | Numerical verification |
|---|---|---|---|---|
| 1 Capability bound | (H1) reductions measured against the no-DR operation; (H2) constant $\psi$ and COP in $\mathcal I\cup\mathcal T_B$ | Upper bound on the reduction deliverable in B by any controller, given the state after A | Time-varying COP, PV and inference load; the bound uses the largest $\psi_t$ of the interval | Never violated in 80 cases on the DR day; within 0.05 MW in 55–60 % of them (Section 3.7.1, Fig. S3) |
| 2 Value of joint recovery | One class, constant arrivals $p_f$, $L\ge D_B$, constant channel width $h\le\bar P^{B}$ | Allocation of the channel to catch-up and recharge; minimum recovery interval | Three classes and a time-varying channel; the benchmarks of Section 4.3 optimise their recovery instead of repaying the whole debt first | C3 carried across events, 57 % of the channel to the BESS (Section 5.2); foresight value vanishes at 2–3 h (Section 5.4.1); staged benchmark SR-D (Section 5.3.4) |
| 3 Single channel price | Validity indicators fixed (LP); interior catch-up and recharge; minimum import not binding | Marginal values of both debts at a joint optimum | Mixed-integer settlement; non-unique LP responses to a price | One-way (IR-P) and iterative two-way (IR-PD) price coordination (Section 5.3.4, Fig. S5) |
| 4 Exact robust capacity | Empirical capability distribution on the grid; 1-Wasserstein ball of radius $\varepsilon$ | Robust capacity for every distribution within the ball | No guarantee for distributions outside the ball | Out-of-sample calibration on the 26 operating days (Section 5.6.2) |

## 4. Recovery-aware coordinated scheduling framework

The framework comprises two layers (Fig. 2). The day-ahead layer derives the commitments from the closed-loop capability of the intraday controller on historical days, and the intraday layer operates the AIDC with cross-event joint recovery. Algorithm 1 in Table 3 summarises both layers.

### 4.1. Day-ahead recovery-aware commitment

#### 4.1.1. Closed-loop capability on historical days

The commitment of every event must anticipate the recovery state that the preceding events leave behind, as delivered by the controller that operates the AIDC. The day-ahead layer therefore measures the capability of that controller in closed loop. For every historical day $d$ of $\Omega^{DA}$ and every candidate commitment $C$ of the grid $\mathcal G$, the intraday controller of Section 4.2 is simulated with the realised data of day $d$, which yields the comprehensive cost $J_d(C)$, the full-delivery indicator $u_d(C)$ of \eqref{eq:ind} and the capability
$$\begin{aligned}\xi_d={}&\max\big\{C\in\mathcal G:\ u_d(C')=1\ \forall C'\in\mathcal G,\ C'\le C\big\}\\&+\tfrac12\Delta_{\mathcal G},\end{aligned} \label{eq:capability}$$
the midpoint between the largest uniform commitment that the controller delivers in full on day $d$ and the next commitment of the grid (step $\Delta_{\mathcal G}$), at which delivery first fails. The back-test visits the commitments in increasing order and stops simulating a day after its first failure; it yields every $\xi_d$, and every $J_d(C)$ for $C\le\min_d\xi_d$, with about half of the closed-loop runs of the full grid.

#### 4.1.2. Wasserstein ambiguity set and dual reformulation

The empirical distribution $\hat P_N=\frac1N\sum_d\delta_{\xi_d}$ summarises the deliverability of the controller on the $N$ historical days. Because the operating day can differ from them, the commitment is protected against all distributions within the 1-Wasserstein ball $\mathcal B_\varepsilon(\hat P_N)=\{Q:\ W_1(Q,\hat P_N)\le\varepsilon\}$ [@esfahani2018],
$$C^{DRO}_\rho(\varepsilon)=\max\Big\{C\in\mathcal G:\ \inf_{Q\in\mathcal B_\varepsilon(\hat P_N)}Q(\xi\ge C)\ge\rho\Big\}, \label{eq:dro}$$
the distributionally robust counterpart of \eqref{eq:firm}. The radius $\varepsilon$ (MW) is the largest average shift of the capability that the commitment must withstand.

The inner problem of \eqref{eq:dro} is an optimisation over probability distributions. For a commitment $C$, let $\mathcal D_C=\{d:\xi_d\ge C\}$ be the days that deliver it, $n(C)=|\mathcal D_C|$, and $\delta_d(C)=\xi_d-C$ their capability margins. The least favourable distribution moves the probability mass $w_d\in[0,1/N]$ from the atoms in $\mathcal D_C$ to just below $C$, at the transport cost $\delta_d(C)$ per unit of mass, so that the worst-case failure probability is
$$\sup_{Q\in\mathcal B_\varepsilon(\hat P_N)}Q(\xi<C)=\frac{N-n(C)}{N}+m^*_C(\varepsilon), \label{eq:worst}$$
where the largest mass that the transport budget can remove is the fractional knapsack problem
$$\begin{aligned}m^*_C(\varepsilon)=\max_{w}\Big\{&\sum_{d\in\mathcal D_C}w_d:\ \sum_{d\in\mathcal D_C}w_d\,\delta_d(C)\le\varepsilon,\\&0\le w_d\le\frac1N\ \ \forall d\in\mathcal D_C\Big\}.\end{aligned} \label{eq:knap}$$
With the multiplier $\lambda\ge0$ of the transport budget and $\upsilon_d\ge0$ of the upper bounds, the linear-programming dual of \eqref{eq:knap} is $\min\{\lambda\varepsilon+\frac1N\sum_d\upsilon_d:\ \upsilon_d\ge1-\lambda\delta_d(C),\ \upsilon_d\ge0\}$. Eliminating $\upsilon_d=\max\{1-\lambda\delta_d(C),0\}$ gives the one-dimensional problem
$$\begin{aligned}m^*_C(\varepsilon)=\min_{\lambda\ge0}\Big\{&\lambda\varepsilon\\&+\frac1N\sum_{d\in\mathcal D_C}\max\{1-\lambda\,\delta_d(C),\,0\}\Big\},\end{aligned} \label{eq:dual}$$
where strong duality holds because \eqref{eq:knap} is a feasible and bounded linear program and $\lambda$ is the shadow price of the transport budget. The objective of \eqref{eq:dual} is convex and piecewise linear in $\lambda$ with breakpoints at $\lambda=1/\delta_d(C)$, so the infinite-dimensional inner problem of \eqref{eq:dro} reduces to sorting the capability margins.

**Proposition 4 (exact distributionally robust firm capacity).** For a commitment $C$, let $\delta_{(1)}(C)\le\delta_{(2)}(C)\le\dots$ be the sorted margins of the days in $\mathcal D_C$ and $q(C)=n(C)-\rho N$. The robust constraint in \eqref{eq:dro} holds if and only if $q(C)\ge0$ and
$$\begin{aligned}\Phi_\rho(C)=\frac1N\Big[&\sum_{j=1}^{\lfloor q\rfloor}\delta_{(j)}(C)\\&+\big(q-\lfloor q\rfloor\big)\,\delta_{(\lfloor q\rfloor+1)}(C)\Big]\ge\varepsilon .\end{aligned} \label{eq:phi}$$
Hence (i) $C^{DRO}_\rho(\varepsilon)=\max\{C\in\mathcal G:\ q(C)\ge0,\ \Phi_\rho(C)\ge\varepsilon\}$ is obtained by sorting; (ii) for $\varepsilon=0$ it equals the sample-average capacity, the empirical $(1-\rho)$-quantile of $\xi$; (iii) it is non-increasing in $\varepsilon$, and it is insensitive to the radius when the days just above the commitment keep a large margin, i.e. when the capability distribution is concentrated.

$\Phi_\rho(C)$ is the smallest average capability loss (MW) that would push the full-delivery probability below $\rho$; it is the robust reliability margin of the commitment.

#### 4.1.3. Radius selection and cost-optimal commitment

The radius is set to the expected 1-Wasserstein estimation error of the empirical distribution [@delbarrio1999],
$$\varepsilon_N=\frac{1}{\sqrt N}\int\sqrt{\hat F_N(\xi)\big(1-\hat F_N(\xi)\big)}\,\mathrm d\xi, \label{eq:radius}$$
where $\hat F_N$ is the empirical distribution function of the capability. The radius is small for a concentrated capability distribution and large for a dispersed one. It is a calibrated choice rather than a finite-sample guarantee: for $N$ = 14, radii that contain the true distribution with high confidence exceed the spread of the capability itself (Appendix B). Its out-of-sample validity is therefore tested on the operating days, and a leave-one-out choice on $\Omega^{DA}$ serves as a check (Section 5.6.2). Among the robustly deliverable commitments, the operator selects the one with the lowest mean back-tested cost
$$\bar J(C)=\frac1N\sum_{d\in\Omega^{DA}}J_d(C), \label{eq:jbar}$$
$$C^*=\arg\min\big\{\bar J(C):\ C\in\mathcal G,\ C\le C^{DRO}_\rho(\varepsilon)\big\}. \label{eq:commit}$$
Every strategy can be paired with this procedure, which makes the endogenous-commitment comparison of Section 5.6 fair: all strategies use the same days, the same objective and the same reliability target.

#### 4.1.4. Perfect-recourse benchmark commitment

For comparison, the commitments can also be obtained from a two-stage stochastic MILP with perfect recourse, in which $\mathbf C=(C_1,\dots,C_K)$ is the first-stage decision and the joint recovery model \eqref{eq:it}–\eqref{eq:jterm} of every scenario $\omega$ with probability $p_\omega$ is the second stage,
$$\min_{\mathbf C}\ -\epsilon^{C}\textstyle\sum_kC_k+\sum_{\omega}p_\omega J_\omega(\mathbf C), \label{eq:ra-obj}$$
$$\begin{aligned}&\bar r_{k,\omega}\ge(1-\epsilon_f)\,C_k-M(1-u_\omega)\quad\forall k,\omega,\\&\textstyle\sum_\omega p_\omega u_\omega\ge\rho,\qquad u_\omega\in\{0,1\}.\end{aligned} \label{eq:ra-cc}$$
Because the recourse of \eqref{eq:ra-obj}–\eqref{eq:ra-cc} knows each scenario in advance, it measures the physical consecutive capability; in the case study it returns the single-event capabilities (8.18/7.98 MW in S1). Two-stage distributionally robust models solved by column-and-constraint generation [@zeng2013] share this recourse structure, whereas the closed-loop capability \eqref{eq:capability} measures what the controller actually delivers.

### 4.2. Intraday cross-event joint recovery MPC

Every 15 min the controller measures the state $\hat{\mathbf x}_t$ (backlogs, stored energy and cold, gas-engine output, event status), corrects the forecasts $\hat{\mathbf w}_{\cdot|t}$ of arrivals, inference load, PV and chiller COP by the latest observed errors, and solves
$$\mathbf u^*_{\cdot|t}\in\arg\min_{\mathbf u\in\mathcal U_t(\hat{\mathbf x}_t,\,\hat{\mathbf w}_{\cdot|t})}J_{[t,\,t+T_H]}(\mathbf u),\qquad \mathbf u_t=\mathbf u^*_{t|t}, \label{eq:mpc}$$
where $\mathcal U_t$ is the feasible set of \eqref{eq:it}–\eqref{eq:short} and \eqref{eq:rebound} over the 18-h horizon and $J_{[t,\,t+T_H]}$ the objective \eqref{eq:obj} over the same horizon, with the terminal value \eqref{eq:jterm} of the storage debts and the backlog (JR-D). Because all confirmed events are visible within the horizon, the controller decides at every step which debt to repay first: it carries long-deadline backlog across events when doing so frees the channel for the storage that the next event needs, and it repays the debts that would otherwise fall due. An event that is not yet confirmed is treated as called if its call probability is at least 0.5 (certainty equivalence). The scenario variant JR-S replaces the forecast by a scenario tree with non-anticipative first-step decisions, in which an event that is not yet confirmed appears only in the scenarios in which it is called. The plant replay enforces the physical limits in the order storage, cold storage and deferrable computing, so that the grid import never exceeds $P^{cap}$.

**Table 3.** Pseudocode of the recovery-aware commitment and the cross-event joint recovery.

| **Algorithm 1** Recovery-aware commitment and cross-event joint recovery |
|---|
| **Input:** historical days $\Omega^{DA}$ ($N$ days), operating days $\Omega$, commitment grid $\mathcal G$ (step $\Delta_{\mathcal G}$), reliability $\rho$, event set $\mathcal K$, horizon $T_H$, plant parameters (Table A1) |
| **Output:** cost-optimal commitment $C^*$, firm capacity $\hat C^{firm}_\rho$, closed-loop trajectories |
| ***Stage I: day-ahead recovery-aware commitment (Section 4.1)*** |
| 1: **for** $C\in\mathcal G$ in increasing order and every day $d\in\Omega^{DA}$ that delivered all smaller $C$ **do** |
| 2: $\quad$ run Stage III on day $d$ with commitment $C$ → cost $J_d(C)$ and indicator $u_d(C)$ \eqref{eq:ind} |
| 3: capability $\xi_d$ of every day \eqref{eq:capability}; empirical distribution $\hat P_N$; radius $\varepsilon\leftarrow\varepsilon_N$ \eqref{eq:radius} |
| 4: **for** $C\in\mathcal G$ **do** sort the margins $\delta_d(C)$, $d\in\mathcal D_C$; $q(C)\leftarrow n(C)-\rho N$; margin $\Phi_\rho(C)$ \eqref{eq:phi} |
| 5: $C^{DRO}\leftarrow\max\{C\in\mathcal G:\ q(C)\ge0,\ \Phi_\rho(C)\ge\varepsilon\}$ \eqref{eq:dro}; $C^*\leftarrow\arg\min\{\bar J(C):\ C\le C^{DRO}\}$ \eqref{eq:commit} |
| ***Stage II: firm capacity on the operating days (Section 3.6)*** |
| 6: **for** every $C\in\mathcal G$ and $\omega\in\Omega$ **do** run Stage III with commitment $C$ |
| 7: $\hat C^{firm}_\rho\leftarrow$ largest $C$ whose full-delivery share is at least $\rho$ for all $C'\le C$ \eqref{eq:saa}; bootstrap confidence intervals over days |
| ***Stage III: intraday cross-event joint recovery MPC (Section 4.2), every $\Delta t$ = 15 min*** |
| 8: measure $\hat{\mathbf x}_t=(B_{1,t},B_{2,t},B_{3,t},E_t,S_t)$, the gas-engine state, the event status and the loads |
| 9: correct the forecasts with the latest observed errors (JR-S: build the scenario tree) |
| 10: solve the joint recovery MILP \eqref{eq:mpc} over $t,\dots,t+T_H$ with all confirmed events |
| 11: apply the first-step decisions; replay the plant (storage → TES → compute throttling) |
| 12: update the backlogs by earliest-deadline-first execution and the settlement \eqref{eq:rbar}–\eqref{eq:short} |
| 13: **return** $C^*$, $\hat C^{firm}_\rho$ and the trajectories |

### 4.3. Benchmarks and controlled scenario matrix

All strategies face the same commitments, service deadlines, physical limits and settlement rules, and all use the forecasts, event information, 15-min step and 18-h horizon of JR-D: the benchmarks differ from JR-D in how the subsystems coordinate, not in what they know. Table 4 lists the controlled scenario matrix, which isolates the contribution of each resource, each device and each layer of coordination.

- **IR-O\*** — independent recovery with an optimised static split. The IT scheduler plans its own share $\alpha C_k$ of every event and its catch-up with priority on the connection headroom; the facility energy-management system then optimises storage and IES with the IT schedule fixed. The split $\alpha$ is tuned day-ahead on the historical scenarios over $\alpha\in[0.2,1.0]$ for every commitment level.
- **IR-P** — price-coordinated independent recovery. Instead of a fixed share, the IT scheduler prices its facility energy at the channel price $\lambda^{el}_t$ of the day-ahead joint plan (Proposition 3), i.e. at the TOU price plus the premium $\lambda^{cap}_t+\lambda^{ev}_t$, a one-way, day-ahead price signal.
- **IR-PD** — independent recovery with iterative two-way price coordination, renewed at every step. The facility prices the channel from the joint plan at the measured state; the IT scheduler answers with its own schedule at that price; the facility re-optimises with this schedule fixed and returns the marginal value of IT power under its best response, towards which the price moves with damping 0.5. After 12 rounds the IT applies the average of the schedules of rounds 7–12 (primal averaging of the price iteration), and the facility follows with it fixed.
- **SR-D** — staged recovery with the forecasts and the joint delivery of JR-D. During an event SR-D acts as JR-D. Outside events, at every step, the computing schedule is planned first with the storage charging held at the no-DR schedule, so that the deferred work is caught up through the whole channel, and the storage and IES are planned afterwards with this computing schedule fixed. SR-D thus executes the recovery order of independent recovery in Proposition 2, computing debt first and storage debt after, with the information of JR-D.
- **JR-M** — event-by-event joint recovery. The joint model is used, but only the current or next event is visible, which represents single-event DR scheduling and isolates the value of cross-event foresight.
- **JR-oracle** — joint recovery with perfect information (reference).

**Table 4.** Controlled scenario matrix (✓ included, × excluded, – not applicable). The resource and device configurations are operated by the JR-D controller with the connection limit of the base case.

| Configuration | Compute flexibility | BESS | Cold storage | Gas engine | Absorption chiller | Joint recovery | Cross-event foresight |
|---|---|---|---|---|---|---|---|
| R1 BESS only | × | ✓ | × | ✓ | ✓ | – | ✓ |
| R2 Compute only | ✓ | × | × | ✓ | ✓ | – | ✓ |
| R3 Compute + BESS | ✓ | ✓ | × | ✓ | ✓ | ✓ | ✓ |
| D1 w/o gas engine | ✓ | ✓ | ✓ | × | × (no heat) | ✓ | ✓ |
| D2 w/o absorption chiller | ✓ | ✓ | ✓ | ✓ | × | ✓ | ✓ |
| D3 w/o cold storage | ✓ | ✓ | × | ✓ | ✓ | ✓ | ✓ |
| D4 w/o all three | ✓ | ✓ | × | × | × | ✓ | ✓ |
| IR-O\* / IR-P / IR-PD | ✓ | ✓ | ✓ | ✓ | ✓ | × | ✓ |
| SR-D | ✓ | ✓ | ✓ | ✓ | ✓ | × (staged) | ✓ |
| JR-M | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | × |
| JR-D (proposed) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### 4.4. Implementation and computational performance

The models are implemented in GNU Octave 8.4 and solved with GLPK 5.0 on one core of an Intel Xeon processor at 2.8 GHz; the implementation also supports Gurobi and the MATLAB solvers `linprog` and `intlinprog`. Table 5 lists the size of the optimisation models and their solution times. With the full 18-h horizon and two visible events, the MILP of JR-D has 1 524 variables, of which two are binary (one validity indicator per event), and its solution takes 0.04 s on average; a closed-loop day of 120 MPC steps takes 5.2 s. The scenario variant JR-S, with five scenarios, is five times larger and takes 60.1 s per day. Every MILP of the more than 18 000 closed-loop runs reported in Section 5 is solved to proven optimality (GLPK status optimal, zero relative gap), and no step requires the fallback controller. The controller therefore runs well within the 15-min step of the MPC.

**Table 5.** Size and solution time of the optimisation models (S1, 7 MW, full 18-h horizon with both events visible). Closed-loop day: mean solver time per day over the closed-loop runs of S1 (26 operating days, all commitments).

| Controller | Model solved every 15 min | Variables (binary) | Constraints (inequality / equality) | Solution time per step, mean / max (s) | Closed-loop day (s) |
|---|---|---|---|---|---|
| JR-D | joint recovery MILP | 1 524 (2) | 604 / 504 | 0.04 / 0.08 ^a^ | 5.2 |
| JR-S | scenario MILP, 5 scenarios | 7 620 (10) | 3 020 / 2 564 | 0.93 / 1.20 ^a^ | 60.1 ^b^ |
| JR-M | joint recovery MILP, one event visible | 1 519 (1) | 588 / 504 | 0.04 / 0.08 ^a^ | 4.7 |
| IR-O\* / IR-P | IT scheduling LP, then facility MILP | 656 (0) + 1 524 (2) | 368 / 216 + 604 / 504 | 0.02 / 0.03 ^a^ | 2.1 |

^a^ Typical day; for JR-S the first 30 steps, which solve the full horizon. ^b^ Runs with event-call uncertainty (S4-U, 26 days).

## 5. Case studies

### 5.1. Case description

#### 5.1.1. AIDC integrated energy system and data

The AIDC of Section 2.1 operates under the Jiangsu two-part TOU tariff and DR rules; its parameters are listed in Table A1. All load and weather profiles are derived from public data: the deferrable training and batch work from the Alibaba PAI GPU cluster trace [@weng2022], split by task runtime into the classes C1–C3; the online inference load from the Azure LLM inference trace 2024 [@stojkovic2025]; and the PV output and chiller COP from ERA5 reanalysis weather of Suzhou in the summer of 2024. The DR day is a hot weekday (5 August 2024, maximum temperature 38.3 °C). The DR baseline is the average of the five preceding workdays [@jiangsu2024; @chao2011], and the connection limit is $P^{cap}$ = 16.03 MW, 1.10 times the typical-day peak of 14.57 MW. Without DR the AIDC imports up to this limit when the BESS recharges in the valley hours (mean daily peak 15.82 MW over the operating days), whereas during the evening events the baseline is 9.4–9.8 MW. The recovery channel \eqref{eq:channel} is therefore about 6.4 MW wide: it repays both debts of a 7-MW event within a 3-h interval but only part of them within 30 min. The forecasts use the mean of the preceding weekdays for computing, of the available inference days for inference, and of the preceding three days for PV and temperature.

#### 5.1.2. Event scenarios and operating days

Table 6 lists the event scenarios. The commitment is uniform across events ($C_k=C$), which corresponds to the standard DR product; non-uniform commitments are examined through the reliability region in Section 5.3.3. The historical days $\Omega^{DA}$ are the 14 weekdays of the trace before the DR day; the deterministic forecasts and the IR-O\* split are tuned on five of them, selected at the 10–90 % quantiles of the daily deferrable load. The operating-day set $\Omega$ (scenario S4) contains 26 days, each combining a different PAI weekday after the DR day with a hot summer day and an Azure inference day. On 16 of the 26 days the load without DR deviates from the baseline by more than 1 MW during at least one event, on 14 of them upwards (range −1.45 to +3.30 MW), so the commitments must be delivered under realistic baseline errors.

All strategies of Section 4.3 use the same MPC settings (15-min step, 18-h horizon), the same commitments and the same settlement rules (Table 4). The static split of IR-O\* is re-tuned on $\Omega^{DA}$ for every commitment level ($\alpha^*$ between 0.2 and 0.9), so that the benchmark always operates in its best day-ahead configuration. Every strategy is simulated in closed loop on every operating day, and all statistics are reported with 95 % block-bootstrap confidence intervals over days.

**Table 6.** Event scenarios.

| Scenario | Events (h) | Notice | Price coefficient | Purpose |
|---|---|---|---|---|
| S1 | 17–18, 19–20 | day-ahead | 1.0 | base case (Jiangsu: ≤ 2 agreed events, ≤ 2 h per day) |
| S2 | 17–18, 18.5–19.5 | day-ahead | 1.0 | short interval τ = 30 min (15 min–3 h in Section 5.4) |
| S3 | 17–18, 19–20, 21–22 | day-ahead, day-ahead, 3 h | 1.0, 1.0, 1.4 | high stress: additional rapid peak-shaving call |
| S4 | S1–S3 on the 26 operating days | as S1–S3 | as S1–S3 | statistics and economics |
| S4-U | 17–18, 19–20, 21–22; third event called with probability 0.6 | day-ahead, day-ahead, 1 h | 1.0, 1.0, 1.6 | event-call uncertainty |

### 5.2. Recovery mechanism on a typical day

Figs. 3, 4 and 5 trace the two events of S2 on a representative operating day with a uniform commitment of 7 MW and contrast them with the same events 3 h apart. With the 30-min interval, JR-D delivers 8.18 MW in the first and 8.02 MW in the second event, IR-O\* delivers 7.00 MW and 6.84 MW and misses full delivery in the second event, and JR-M drops to 4.64 MW in the second event (Fig. 3a–b). With the 3-h interval all three strategies deliver both events in full (Fig. 4). On this day the shortfall of IR-O\* is small (2 % of the commitment); on another operating day it reaches 17 %, and there too the 3-h interval restores full delivery. The difference therefore arises entirely from how the debts of the first event are incurred and repaid.

#### 5.2.1. Selection of the deferred work

JR-D defers the long-deadline class C3 during the first event: at its end, 3.0×10³ GPU·h of C3 work are deferred, against 2.0×10³ GPU·h under IR-O\* (Fig. 4a). Because C3 does not fall due before the end of the second event, this debt can be carried across it. This is the mechanism of Proposition 2: the necessary catch-up \eqref{eq:cstar} is limited to the work that would fall due in the next event.

#### 5.2.2. Allocation of the recovery channel

In the 30-min interval the grid import of all strategies reaches the connection limit. IR-O\* spends the channel on catch-up and recharges the BESS by only 0.16 MWh, whereas JR-D recharges it by 0.73 MWh and starts the second event with 6.22 MWh instead of 5.91 MWh (Fig. 3c–d). Measured against the no-DR operation, in which the BESS discharges to shave the evening peak, JR-D devotes 57 % of the recovery energy drawn in the interval to the BESS instead of 32 % (Fig. 5). JR-M, which plans each event alone, over-delivers the first event to collect the 120 % payment and empties the BESS to 1.27 MWh; the backlog it leaves cannot be deferred again, and the second event fails.

#### 5.2.3. Contribution of the integrated energy system to the channel

The gas engine and the absorption chiller provide 85 % of the energy that recovery draws through the channel (Fig. 5). The gas engine runs at full output with and without DR, so it adds no energy during recovery but lowers the import by 3 MW and thereby widens the headroom $P^{cap}-P^{base}_t$; Section 5.7 quantifies these roles. These results confirm that the deliverable reduction of the second event is decided by the recovery state that the first event leaves behind, and that joint recovery shapes this state through both the choice of deferred work and the allocation of the channel.

### 5.3. Firm consecutive DR capacity

#### 5.3.1. Firm capacity of the controllers

Fig. 6 shows the share of the 26 operating days on which every event is delivered in full, as a function of the uniform commitment, and Table 7 lists the firm capacities. JR-D firmly delivers 7.5 MW in S1 and in S2 (95 % CI 7.5–8 MW), 94 % of the single-event capability of the second event (7.98 MW). Above this level its share drops to 81 % at 8 MW and to zero at 8.5 MW, where the commitment exceeds what the AIDC can reduce below the baseline at the minimum import of 1.5 MW; this limit is physical, not a recovery limit. JR-M firmly delivers 6.5 MW in S1 but only 4.5 MW in S2, so cross-event foresight adds 1.0 MW (95 % CI 0.5–1.5) with the 1-h interval and 3.0 MW (2.5–3.0) with the 30-min interval. The third, rapid event of S3 makes the evening more demanding: JR-D firmly delivers 6.5 MW per event (4.5–7.0) and JR-M 4.5 MW (1.5–5.0), so foresight adds 2.0 MW (2.0–3.0), while the independent benchmarks deliver all three events in full on at most 77 % of the days at any commitment.

**Table 7.** Firm consecutive DR capacity $C^{firm}_{0.95}$ (MW) on the 26 operating days, with 95 % block-bootstrap confidence intervals, evaluated on the commitment grid with 0.5 MW steps (Sections 5.4–5.5 use bisection with 0.25 MW resolution, so 7.75 MW there corresponds to 7.5 MW on the grid); "< 1" means that full delivery on 95 % of the days is not reached even at 1 MW.

| Scenario | IR-O\* | IR-P | JR-M | JR-D | Foresight gain JR-D − JR-M |
|---|---|---|---|---|---|
| S1 | < 1 | < 1 | 6.5 [6.0, 7.0] | 7.5 [7.5, 8.0] | +1.0 [+0.5, +1.5] |
| S2 | < 1 | < 1 | 4.5 [4.5, 5.0] | 7.5 [7.5, 8.0] | +3.0 [+2.5, +3.0] |
| S3 | < 1 | < 1 | 4.5 [1.5, 5.0] | 6.5 [4.5, 7.0] | +2.0 [+2.0, +3.0] |

#### 5.3.2. Effect of baseline deviations on independent recovery

The independent benchmarks do not reach 95 % at any commitment, not even at 1 MW, where IR-O\* and IR-P deliver in full on 69 % of the days in S1 and 73 % in S2. Their failures concentrate on the days on which the load without DR exceeds the baseline, by more than 1 MW on 14 of the 26 days and by up to 3.3 MW (Section 5.1.2); a reduction measured against the baseline then requires a correspondingly larger true reduction. The IT scheduler of independent recovery defers only its planned share of the commitment, so the whole deviation falls on the storage, which must also serve the second event. On the day with the largest deviation, IR-O\* defers 4.9×10³ GPU·h at 3 MW in S2, less than on an average day, and delivers 1.26 MW and 2.35 MW instead of 3 MW; JR-D defers 9.5×10³ GPU·h, 2.8 times its average, and delivers both events in full. In S1 the facility controller of IR-O\* also charges the BESS only for its own share (7.6 MWh on average at the start of the first event at 3 MW, against 11.3 MWh under JR-D). The firm capacity of independent recovery is therefore limited by baseline uncertainty long before the recovery channel binds, and Section 5.8.4 shows that no static split, not even the best one in hindsight, removes this limit. Under the 80 % settlement rule the ordering is the same: on at least 95 % of the days JR-D is valid up to 9 MW, the top of the grid, in S1 and S2 and up to 7.5 MW in S3, JR-M up to 8.5, 5.5 and 5.0 MW, and the independent benchmarks not even at 1 MW. Even the payment validity of independent recovery cannot be guaranteed.

#### 5.3.3. Two-event firm region

Fig. 7 extends the uniform commitment to the two-event region \eqref{eq:region} of S2: for a fixed first-event commitment $C_1$, it shows the largest second-event commitment that is delivered in full in both events on at least 95 % of the days. The boundary of JR-D is almost flat: JR-D firmly delivers 8.0 MW in the second event after a first event of 2 or 4 MW and still 7.75 MW after 6–8 MW, so a large first event barely reduces the deliverable capacity of the second one. The boundary of JR-M falls from 5.5 MW at $C_1$ = 2 MW to 3.75 MW at $C_1$ = 8 MW. Even a small first event limits JR-M, because an event-by-event plan prepares the storage only for the event at hand: with $C_1$ = 2 MW and $C_2$ = 6 MW (five sampled operating days), JR-M starts the first event with 4.4–5.9 MWh in the BESS, against 11.4 MWh under JR-D, and the second event with 4.1 MWh and up to 2.4×10³ GPU·h of backlog, whereas JR-D starts it with 7.4–7.7 MWh and no backlog. The independent benchmarks have no firm pair at all, since they are not firm even at (1, 1) MW.

With perfect information on the DR day (dashed in Fig. 7, supplementary Fig. S1), the second event can deliver 8.1 MW, expressed as a commitment delivered in full, whatever the first commitment, and this physical capability is the same for joint, event-by-event and independent recovery with the best static split. Physical capability therefore does not distinguish the controllers; firm capacity does. JR-D comes within 0.1–0.3 MW of the physical boundary, whereas JR-M stays 2.6–4.3 MW below it: the gap is created by operating in closed loop under forecast and baseline errors, which is exactly what a perfect-recourse assessment leaves out.

### 5.4. Capacity-gain decomposition and multidimensional sensitivity analysis

#### 5.4.1. Coordination value and foresight value

Fig. 8 decomposes the firm capacity over the event interval τ, from 15 min to 3 h (two one-hour events, base system, bisection on the 26 operating days). JR-D firmly delivers 7.50–8.00 MW at every interval: with cross-event foresight the firm capacity hardly depends on how soon the next event follows. Without foresight it does. The firm capacity of JR-M rises from 3.50 MW at 15 min to 4.75 MW at 30 min, 6.75 MW at 1 h and 7.75 MW at 2 h and 3 h, so the foresight value, the gain of JR-D over JR-M, is 4.0, 3.0, 1.0, 0.25 and 0 MW. It vanishes once the interval is long enough to repay both debts, the condition of Proposition 2. IR-O\* stays below 1 MW at every interval, so the coordination value, the gain of JR-M over IR-O\*, is at least 2.5 MW at 15 min and grows to at least 6.75 MW at 2 h and 3 h. Coordination is therefore valuable at every interval, because it lets one controller re-plan all resources on the measured state, while foresight adds its value precisely where coordination alone falls short, at short intervals.

#### 5.4.2. Event interval and connection margin

At a fixed commitment of 7 MW, the interval–margin map (Fig. 9a–c) confirms the conditions of Proposition 2. JR-D delivers in full on 96–100 % of the days in all 20 combinations of τ and γ. JR-M delivers in full on 0–31 % of the days when the interval is 15 or 30 min and on 88–100 % from 1 h on, whatever the connection margin, so the foresight gain is 69–100 percentage points for τ ≤ 0.5 h, 0–12 points at 1 h and 0–4 points for τ ≥ 2 h (Fig. 9c). A wider connection does not restore the firm capacity of JR-M at short intervals: JR-M enters the interval with the battery that it emptied in the first event, and within 30 min the battery can take back at most 3 MWh at its 6-MW rating, whatever the connection (Section 5.5). Once the interval is long enough to repay both debts, the order of repayment no longer matters, and the advantage of joint recovery vanishes, as Proposition 2 predicts. The gain of JR-D over the best independent benchmark (12–54 points, Fig. 9b) shows no trend in τ, consistent with independent recovery failing on baseline deviations rather than on the channel.

#### 5.4.3. Lag bounds of the deferrable work

The lag bounds of the deferrable work decide how much debt can be carried (Fig. 9d; S1, 7 MW, connection kept). With all lag bounds scaled by 0.5, 0.75, 1, 1.25 and 1.5, JR-D delivers both events in full on 96–100 % of the days, whereas JR-M does so on 19, 46, 92, 100 and 100 %. Shorter deadlines shrink the debt that may be carried, $\min\{X,p_f(L-D_B)\}$ in \eqref{eq:tau}, so event-by-event recovery exhausts the admissible delay, while cross-event foresight still finds a feasible order of repayment; longer deadlines let even an event-by-event plan wait. Independent recovery is unaffected (85 % for IR-O\*, 12 % for IR-P at every scale), consistent with its failures stemming from baseline deviations rather than from deadlines.

### 5.5. Equivalent battery and connection capacity

#### 5.5.1. Battery energy

Fig. 10 translates the capacity gain into the battery energy and the connection capacity that it substitutes. The firm capacities are found by bisection on the 26 operating days of S2 (resolution 0.25 MW). With the connection limit kept at its base value, the firm capacity of JR-D rises from 3.75 MW without a BESS to 6.00 MW with 6 MWh and 7.75 MW with the base 12 MWh (Fig. 10a). JR-M gains much less from the same battery (3.75, 4.50 and 4.75 MW) and never exceeds 5.25 MW, and IR-O\* stays below 1 MW at every size: a battery reserved for a fixed share of the reduction cannot absorb the baseline deviations that make independent recovery fail. Cross-event foresight therefore substitutes battery energy. JR-D needs 2.7 MWh to firmly deliver the 4.75 MW that JR-M reaches with 12 MWh, a saving of 9.3 MWh, or about 5.6 million CNY at a system cost of 0.6 CNY/Wh, and no battery size lets JR-M reach the firm capacity of JR-D. Beyond 12 MWh the firm capacity of JR-D declines (7.50 MW at 18 MWh and 6.75 MW at 24 MWh). This decline stems from the baseline rule, not from recovery: a larger battery shaves the evening peak in normal operation, which lowers the five-day baseline and with it the reduction that can be shown against it.

#### 5.5.2. Connection capacity

The connection margin matters much less (Fig. 10b). Raising the connection limit from 14.57 MW ($\gamma$ = 1.00) to 18.94 MW ($\gamma$ = 1.30) adds only 0.5 MW to the firm capacity of JR-D (7.50 → 8.00 MW) and of JR-M (4.50 → 5.00 MW), and IR-O\* stays below 1 MW. Connection expansion alone cannot compensate for the lack of cross-event foresight: with 4.4 MW more connection than JR-D at $\gamma$ = 1.00, JR-M still firmly delivers 2.5 MW less. Conversely, JR-D at the smallest margin tested (14.57 MW) firmly delivers more than JR-M at the base connection of 16.03 MW, with 1.46 MW less connection. At a 30-min interval the binding limit is the recharge rate of the battery (6 MW, at most 3 MWh within the interval), not the width of the channel: JR-M empties the battery in the first event and cannot restore it whatever the connection, whereas JR-D keeps the energy that the second event needs.

#### 5.5.3. Substitution across target firm capacities

Fig. 10c and d generalise the substitution to every firm capacity that JR-M can reach, by interpolating the curves of Fig. 10a and b. The battery saved by cross-event foresight grows with the target: JR-D needs 0.67 MWh instead of 2.00 MWh to firmly deliver 4.0 MW, 2.00 instead of 6.00 MWh for 4.5 MW, 2.67 instead of 12.00 MWh for 4.75 MW and 4.0 instead of 18.0 MWh for 5.25 MW, savings of 1.33, 4.00, 9.33 and 14.0 MWh; no battery size lets JR-M exceed 5.25 MW (Fig. 10c). The connection saved is zero up to 4.5 MW, which JR-M reaches at the smallest margin tested, and grows to at least 0.73 MW at 4.75 MW, for which JR-M needs 15.30 MW ($\gamma$ = 1.05), and to at least 2.91 MW at 5.0 MW, for which it needs 17.49 MW ($\gamma$ = 1.20) (Fig. 10d); these savings are lower bounds, because JR-D exceeds every such target already at $\gamma$ = 1.00. The value of cross-event foresight therefore rises steeply as the commitment approaches the limit of event-by-event recovery, where hardware substitutes for foresight only at a growing cost.

### 5.6. Distributionally robust day-ahead commitment

#### 5.6.1. Closed-loop capability on historical and operating days

Fig. 11a and d show the closed-loop capability $\xi_d$ \eqref{eq:capability} of every controller on the 14 historical days and on the 26 operating days. In S1, independent recovery has a dispersed, bimodal capability: IR-O\* fails already at 1 MW on 4 of the 14 historical days and reaches 7.75–8.25 MW on the others, and the same pattern recurs on the operating days (8 of 26 below 1 MW). The capability of JR-M lies at 7.75–8.25 MW on the historical days and spreads down to 6.25 MW on the operating days. JR-D reaches 8.25 MW, the midpoint between the last delivered and the first failed commitment at its physical limit, on every historical day and on 21 of the 26 operating days.

#### 5.6.2. Robust firm capacity and calibration

With $\rho$ = 0.95 and $N$ = 14, the sample-average capacity is the smallest historical capability rounded down to the grid (Table 8). The robust capacity \eqref{eq:dro} lowers it by the robust margin \eqref{eq:phi}: because a 5 % share of the days may lose its whole margin, every 0.025 MW of radius costs 0.5 MW of commitment when all days lie above it (Fig. 11b, e). In S1 the radius \eqref{eq:radius} is 0.91 MW for IR-O\*, 0.066 MW for JR-M and zero for JR-D, whose capability does not vary. For JR-M it lowers the commitment from 7.5 to 6.0 MW and corrects the over-confidence of the sample average: out of sample, 7.5 MW is delivered in full on 77 % of the days and 6.0 MW on all of them, and the worst-case probabilities within the ball, 0.74, 0.91 and 0.95 at 7.5, 7.0 and 6.5 MW, match the realised shares of 0.77, 0.92 and 0.96 (Fig. 11c). For IR-O\* the radius even exceeds the actual distance between the historical and the operating capabilities ($W_1$ = 0.81 MW), and no commitment of 1 MW or more is robust. For JR-D the robust capacity equals the sample-average 8.0 MW, its physical limit, which is delivered in full on only 81 % of the operating days, so the robust commitment misses its target out of sample. The operating days are more loaded than the historical ones: during the first event the load without DR exceeds the baseline by 0.78 MW on average, against −0.16 MW on the historical days, and the five days on which JR-D misses 8 MW, each time in the second event, all have the load above the baseline in both events (by 0.9–1.9 MW in the first and 0.8–2.8 MW in the second). The capability distribution of the operating days therefore lies outside the Wasserstein ball around the historical days: the radius covers the estimation error of 14 samples but not a systematic shift of the baseline error, so the guarantee of Proposition 4 does not carry over (level (i) of Section 3.6). The full delivery of the cost-optimal 7 MW on every operating day stems from the margin of 1 MW that the cost criterion keeps below the capability limit, not from the robust step (Section 5.6.3). With 26 failure-free days, its full-delivery probability exceeds 0.89 with 95 % confidence (Table 8); Section 5.10.4 extends the test to 78 realisations and to a DR day in another month.

In S2 the capability of JR-D varies slightly (one historical day at 7.75 MW, the others at 8.25 MW). The radius is 0.034 MW and the robust capacity of 7.0 MW is delivered in full on every operating day; at 8 MW the robust probability of full delivery, 0.79, matches the realised share of 0.81, where the sample average predicts 0.93 (Fig. 11f). The capability of JR-M is dispersed between 5.25 and 7.75 MW; its radius of 0.25 MW leaves no robust commitment of 1 MW or more, whereas the sample average commits 5.0 MW and delivers it in full on only 92 % of the days. The price of robustness thus scales with the dispersion of the capability: it is negligible for the concentrated capability of JR-D and excludes any commitment for the dispersed capability of JR-M, which is a second reason, besides the larger capability itself, why cross-event joint recovery can commit more.

A leave-one-out choice of the radius, the smallest radius at which the commitment computed from 13 historical days is delivered on the held-out day in at least 95 % of the 14 cases, measures only how consistent the historical days are with one another. In S1 it is zero for every controller and would keep the sample-average 7.5 MW of JR-M, which is delivered in full on only 77 % of the operating days; in S2 it is 0.015 MW and gives the same 7.0 MW for JR-D and 4.5 MW for JR-M. The expected estimation error \eqref{eq:radius} therefore errs on the side of reliability, which is the purpose of a firm commitment.

#### 5.6.3. Cost-optimal commitment and comparison with physical capability

The commitment \eqref{eq:commit} minimises the back-tested cost below the robust capacity. It selects 7 MW for JR-D in both scenarios and 6 MW for JR-M in S1, which are delivered in full on all 26 operating days, with benefits of 44.8 (S1) and 43.1 k CNY/day (S2) for JR-D and 35.8 k CNY/day for JR-M (Table 8). For JR-D the cost minimum lies below the capability limit: the payment, capped at 120 % of the commitment, grows with the commitment only until the reduction reaches its physical maximum of about 8 MW, beyond which a larger commitment adds shortfall risk but no revenue; in S1 the robust margin at 7 MW is 0.063 MW, five times the margin at 8.0 MW. Independent recovery receives no robust commitment in either scenario, consistent with its out-of-sample performance: at 1 MW it delivers in full on only 69–73 % of the operating days.

Commitments derived from physical capability are not deliverable. The perfect-recourse model \eqref{eq:ra-obj}–\eqref{eq:ra-cc} commits the single-event capabilities of 8.18/7.98 MW in S1, which JR-D delivers in full on 85 % of the days; operated by independent recovery, as in conventional single-event practice, the share falls to 27 % (IR-O\*) and 0 % (IR-P). Supplementary Fig. S2 places all commitment methods in the plane of out-of-sample reliability and benefit.

**Table 8.** Day-ahead commitment from the 14 historical days and its out-of-sample performance on the 26 operating days ($\rho$ = 0.95). $\varepsilon$: radius (MW); $\Phi$: robust reliability margin \eqref{eq:phi} at the commitment (MW); lower 95 % bound: one-sided Clopper–Pearson bound of the full-delivery probability from the 26 operating days (Section 3.6).

| Scenario | Commitment method | Operated by | Commitment (MW) | $\varepsilon$ | $\Phi$ | Days with full delivery (%) | Lower 95 % bound | Benefit vs no DR (k CNY/day) |
|---|---|---|---|---|---|---|---|---|
| S1 | Perfect-recourse MILP \eqref{eq:ra-obj} | JR-D | 8.18 / 7.98 | – | – | 85 | 0.68 | 44.7 |
|  | Single-event capability | IR-O\* / IR-P | 8.18 / 7.98 | – | – | 27 / 0 | 0.13 / 0 | 37.2 / 1.8 |
|  | Sample average | IR-O\*, IR-P | none ≥ 1 | 0 | – | – | – | – |
|  |  | JR-M | 7.5 | 0 | 0.013 | 77 | 0.60 | 36.9 |
|  |  | JR-D | 8.0 | 0 | 0.013 | 81 | 0.64 | 44.6 |
|  | Robust \eqref{eq:dro} | IR-O\*, IR-P | none ≥ 1 | 0.91 / 0.90 | – | – | – | – |
|  |  | JR-M | 6.0 | 0.066 | 0.088 | 100 | 0.89 | 35.8 |
|  |  | JR-D | 8.0 | 0 | 0.013 | 81 | 0.64 | 44.6 |
|  | Cost-optimal \eqref{eq:commit} | JR-M | 6.0 | 0.066 | 0.088 | 100 | 0.89 | 35.8 |
|  |  | **JR-D** | **7.0** | **0** | **0.063** | **100** | **0.89** | **44.8** |
| S2 | Sample average | IR-O\*, IR-P | none ≥ 1 | 0 | – | – | – | – |
|  |  | JR-M | 5.0 | 0 | 0.013 | 92 | 0.78 | 29.3 |
|  |  | JR-D | 7.5 | 0 | 0.013 | 100 | 0.89 | 43.1 |
|  | Robust \eqref{eq:dro} | IR-O\*, IR-P | none ≥ 1 | 0.73 / 0.83 | – | – | – | – |
|  |  | JR-M | none ≥ 1 | 0.25 | – | – | – | – |
|  |  | JR-D | 7.0 | 0.034 | 0.038 | 100 | 0.89 | 43.1 |
|  | Cost-optimal \eqref{eq:commit} | **JR-D** | **7.0** | **0.034** | **0.038** | **100** | **0.89** | **43.1** |

### 5.7. Role of the integrated energy system

#### 5.7.1. Composition of the recovery channel

The integrated energy system provides the recovery channel. In the two recovery windows of the typical day, the 30-min interval and the two hours after the second event, the no-DR import lies on average 4.8 and 5.3 MW below the connection limit (Fig. 12b). The gas engine, which runs at full output from 14:00 to 22:00 with and without DR, accounts for 3.0 MW of this channel, the absorption chiller, which moves part of the cooling load off the electric chillers, for 0.5 MW, and the cold storage for 0.2 MW; the BESS adds 1.2 MW by shaving the evening peak in normal operation, but under DR it serves the events instead. A grid-only AIDC with the same connection would have almost no channel left (on average −0.3 and +0.4 MW in the two windows). Of the energy that recovery draws through the channel, the gas engine and the absorption chiller provide 85 % (Fig. 5). The cold storage is pre-charged before the events, covers part of the cooling load during both events and is recharged at night, so its own debt never enters the channel.

#### 5.7.2. Device and resource ablation

Fig. 12a quantifies these roles as firm capacities of JR-D in S2 with the connection limit of the base case. Without the gas engine, and therefore without heat for the absorption chiller, the evening baseline rises by 3.5 MW. This would allow a deeper reduction, but the channel narrows by the same amount and binds first: the firm capacity falls from 7.75 to 5.75 MW. Without the cold storage it falls to 7.50 MW. Without the absorption chiller alone it rises slightly, to 8.00 MW, because the 0.5 MW higher baseline allows a deeper reduction while the channel remains wide enough. Without all three devices the firm capacity is 4.75 MW, 3.0 MW below the full system and as much as cross-event foresight adds at this interval.

The resource ablation shows that computing flexibility and storage are complements rather than substitutes. With the BESS alone (no computing flexibility, no cold storage), no commitment of 1 MW or more is firm; with computing flexibility alone the firm capacity is 3.00 MW; with both, still without the cold storage, it is 7.50 MW, nearly twice what the two resources achieve separately (less than 4 MW together). Joint recovery is what turns the two resources into firm capacity: the battery covers the events while the deferred work waits, and the deferred work frees the channel to recharge the battery.

#### 5.7.3. Energy efficiency and carbon emissions

Consecutive DR leaves the energy efficiency and the emissions of the facility almost unchanged. Without DR the AIDC emits 229.6 t of CO~2~ per evaluation window \eqref{eq:co2}, averaged over the 26 operating days. At 7 MW the emissions change by +0.35 t (+0.15 %) under JR-D in S1 and by +0.28 t (+0.12 %) in S2, by +0.05/+0.03 t under IR-O\*, +0.38/+0.31 t under JR-M and +0.17/+0.04 t under IR-P, below 0.2 % for every controller: DR shifts the consumption of the facility in time but hardly changes its amount. The electric PUE \eqref{eq:pue} of the typical day is 1.253 with and without DR for every controller. It is lower during the gas-engine hours, 1.217 from 14:00 to 22:00 against 1.271 in the other hours, although the chiller COP is lower then (5.16 against 5.33), because the absorption chiller covers 19.5–19.6 % and the cold storage 7.8–7.9 % of the cooling load in these hours. The CCHP devices that widen the recovery channel therefore also lower the electricity that cooling requires during the evening peak, when recovery needs the headroom most.

### 5.8. Service quality and economics

#### 5.8.1. Service quality of the computing users

The deadline constraints \eqref{eq:deadline} are soft only for feasibility: overdue work is priced at $c^{late}$ = 1000 CNY per GPU·h·h, 2000 times the delay price, so it occurs only when no schedule meets every deadline. In S1 and S2 no strategy leaves work overdue on any day or at any commitment, so every deferred task completes within its lag bound (at most 3 h, for C3). In S3 overdue work occurs on one operating day: under IR-O\* at 6–9 MW (up to 2.4×10^4^ GPU·h·h) and under JR-M at 7–9 MW (up to 27 GPU·h·h), never under JR-D. Recovery is also not shifted beyond the evaluation window: at 7 MW, JR-D and JR-M end the window with no backlog in all scenarios, and their end-of-window storage differs from the no-DR level by at most 0.7 k CNY of recharge value (on average it lies slightly above it), whereas IR-O\* and IR-P leave 310–440 GPU·h of backlog on average in S1 and S2 (up to 7.7×10^3^ GPU·h). The reported costs value every end state relative to the no-DR operation (Section 3.5). What DR costs the computing users is the extra completion time of the deferred work (Fig. 13). At every commitment JR-D defers work for less time than the other controllers that deliver: at 7 MW the mean extra completion time is 0.68 h in S1 and 0.90 h in S2, against 0.85 h and 1.12 h for IR-O\* and 1.35 h and 1.26 h for JR-M, and JR-D uses 36 % and 46 % of the SLA slack against 60–75 % for IR-O\* and 60–64 % for JR-M. JR-D defers the long-deadline class, which has slack to spare, whereas IR-O\* catches up its own share at once and JR-M over-delivers the first event and must defer more in the second. IR-P defers least (0.52 h in S1) because it delivers least. The firm operating points of JR-D therefore form the capacity–service front in both scenarios: a larger firm commitment does not come at the expense of the computing users.

#### 5.8.2. Daily cost and benefit

Fig. 14 compares the daily costs at 7 MW, a commitment that all strategies can attempt and the cost-optimal commitment of JR-D (Section 5.6.3). JR-D yields the largest benefit relative to no DR participation, 44.8 k CNY/day in S1 and 43.1 k CNY/day in S2. Its DR revenue of 48.3 k CNY reaches 96 % of the payment cap of the two events and is offset mainly by the delay cost of the deferred work (4.4–6.4 k CNY/day); the electricity and gas costs fall slightly because consumption is shifted out of the evening peak. IR-O\* gains 40.3 and 38.5 k CNY/day with a higher delay cost (5.9–7.6 k CNY/day). JR-M gains 37.3 k CNY/day in S1 but only 19.1 k CNY/day in S2: there the second event finds the AIDC with 4.1×10³ GPU·h of backlog and 3.4 MWh of stored energy (JR-D: 2.2×10³ GPU·h and 6.0 MWh), so its revenue drops to 32.2 k CNY and a shortfall assessment of 4.7 k CNY is levied. IR-P gains 17.8 and 29.8 k CNY/day. On a paired basis JR-D is cheaper than every benchmark on all 26 days in both scenarios; its mean advantage is 4.5 k CNY/day over IR-O\* (95 % CI 2.5–7.6) and 7.6 k CNY/day over JR-M (6.4–8.8) in S1, and 4.6 k CNY/day (2.7–7.4) and 24.1 k CNY/day (19.6–28.5) in S2. The worst-event delivery ratio (Fig. 14c) shows why: the delivery of JR-D is concentrated just above full delivery, whereas the benchmarks spread down to the validity threshold and below it.

#### 5.8.3. Benefit versus commitment

Fig. 15 resolves the benefit over the commitment. For JR-D the DR revenue grows almost linearly with the commitment, at the 120 % payment cap, up to 6.5 MW and saturates at 48.3 k CNY/day from 7 MW on, when the reduction reaches its physical maximum; the delay cost grows convexly, to 4.4 k CNY/day in S1 and 6.4 k CNY/day in S2 at 7 MW, and the shortfall assessment starts at 8 MW (0.2 k CNY/day, rising to 5.7 k CNY/day at 9 MW). The benefit therefore peaks at 7–7.5 MW, with 44.8 k CNY/day in S1 and 43.1 k CNY/day in S2, exactly where the day-ahead layer places the cost-optimal commitment and where the firm capacity lies (Fig. 15a, b). At every commitment from 1 to 9 MW, JR-D yields the largest benefit of the four controllers in both scenarios (Fig. 15c, d): its firm capacity and its economic optimum coincide.

#### 5.8.4. Robustness to the benchmark design and to computing overheads

Two checks confirm that the ranking does not depend on the design of the benchmarks or on idealised computing. First, choosing for every operating day the best static split after the fact bounds every independent recovery with a static split from above. At 1 MW this bound delivers in full on 69 % (S1) and 73 % (S2) of the days, exactly as the split tuned day-ahead: on the other days no split covers the baseline deviation, because independent recovery prepares the storage only for its share of a small commitment. The bound rises with the commitment (92 % and 88 % at 5 MW) and covers all days at 7 MW, but the successful split differs from day to day and cannot be chosen in advance; the split tuned day-ahead delivers in full on 85 % and 81 % of the days. Even with hindsight, independent recovery is therefore not firm at any commitment in the sense of \eqref{eq:saa}, which requires full delivery at every smaller commitment as well. Second, if every deferred GPU·h requires 2 % or 5 % of additional work when it is resumed, an effect the controllers see only through the measured backlog, the firm capacity of JR-D in S2 is 7.75 and 7.50 MW (7.75 MW without overhead), that of JR-M 4.75 MW in both cases, and IR-O\* stays below 1 MW: the foresight gain of 2.75–3.0 MW is unchanged.

### 5.9. Event-call uncertainty and post-event rebound

#### 5.9.1. Event-call uncertainty

A rapid peak-shaving event may be called at short notice or not at all. In S4-U the third event of S3 is called only with probability 0.6 and confirmed 1 h ahead (6 MW per event; called on 15 of the 26 days). JR-D plans for the uncertain event as if it were called, because its call probability exceeds one half, and re-plans once the call is confirmed or cancelled; its scenario-based variant JR-S carries the event in its scenario tree instead. Both deliver every called event in full on all days, whether the third event is called or cancelled, at a daily cost within 0.9 k CNY of the perfect-information oracle (Fig. 16a, b). JR-S saves only 0.3 k CNY/day over JR-D, so the deterministic controller with feedback suffices. IR-O\*, JR-M and IR-P deliver in full on 81 %, 69 % and 27 % of the days and cost 10.8–21.5 k CNY/day more.

#### 5.9.2. Post-event rebound as a policy parameter

Recovery draws power above the baseline after the events. Under the Jiangsu rules alone, the peak rebound after the events of the DR day is 6.4–6.6 MW for every strategy (S1, 6 MW per event), because every controller uses the channel that the connection leaves. A rebound assessment \eqref{eq:rebound} lets the grid operator trade this rebound off against the cost of the AIDC (Fig. 16c, d). At 3 CNY/kW per event, JR-D cuts the peak rebound to 0.17 MW and still delivers both events in full, by holding deferred work longer (delay cost +17.9 k CNY) and over-delivering less (DR revenue −4.4 k CNY), whereas IR-O\* keeps a rebound of 6.4 MW while its fulfilment falls to 91 %. Joint recovery thus also gives the grid a controllable recovery profile, at a price that the assessment can set.

## 6. Conclusions

AI data centers are increasingly called upon for consecutive DR events, and the capacity that they can firmly commit is decided during recovery. This paper developed a recovery-aware coordinated scheduling framework for consecutive DR of an AI data-center integrated energy system, which comprises a cross-event heterogeneous recovery model, the firm consecutive DR capacity with its distributionally robust commitment and an intraday cross-event joint recovery MPC. The framework was tested on a 16 000-GPU data center under the Jiangsu rules with 26 operating days built from public computing traces. The main conclusions are summarised as follows.

(1) Deliverability is decided during recovery, and cross-event joint recovery makes it firm. Computing backlog and storage deficit compete for one recovery channel. Joint recovery carries the long-deadline backlog across the next event and spends the channel on recharging, devoting 57 % of the recovery energy to storage within a 30-min interval instead of 32 % under independent recovery. It firmly delivers 7.5 MW in the two-event scenarios, 94 % of the physical capability of the second event, and 6.5 MW with a third, rapid event. Independent recovery, with a day-ahead tuned split or with price coordination, is not firm at any commitment down to 1 MW, because baseline deviations of up to 3.3 MW fall on storage that serves a fixed share of the reduction.

(2) Cross-event foresight is most valuable at short intervals and substitutes hardware. Foresight adds 4.0 MW of firm capacity at a 15-min, 3.0 MW at a 30-min and 1.0 MW at a 1-h interval (2.0 MW with three events) and vanishes at 2–3 h, as Proposition 2 predicts, whereas coordination adds at least 2.5–6.75 MW at every interval. With foresight, 2.7 MWh of battery firmly deliver what event-by-event joint recovery needs 12 MWh for, a saving of 9.3 MWh or about 5.6 million CNY, and the saving rises to 14.0 MWh as the target approaches the limit of event-by-event recovery. Connection expansion cannot replace foresight: with 4.4 MW more connection, event-by-event recovery still firmly delivers 2.5 MW less, because at short intervals the recharge rate, not the connection, limits how much storage can be restored.

(3) The commitment must reflect what the controller delivers. A closed-loop back-test on 14 historical days refuses to commit independent recovery, which fails at 1 MW on 2–4 of them, and its Wasserstein-robust version, solved exactly by sorting, corrects over-confident sample-average commitments (event-by-event recovery in S1: 7.5 → 6.0 MW, full delivery out of sample 77 → 100 %). Robustness costs little for the concentrated capability of cross-event joint recovery and much for dispersed ones. The cost-optimal commitment of cross-event joint recovery, 7 MW, is delivered in full on every operating day and earns 43–45 thousand CNY per day, whereas a perfect-recourse two-stage model commits the single-event capabilities (8.18/7.98 MW), which are delivered in full on only 85 % of the days.

(4) The integrated energy system provides the recovery channel at almost no energy or carbon cost. The gas engine and the absorption chiller supply 85 % of the energy drawn through the recovery channel; without the gas engine the firm capacity falls by 2.0 MW and without all three CCHP and cold-storage devices by 3.0 MW, as much as cross-event foresight adds. Computing flexibility and storage are complements: 3.0 MW and below 1 MW alone, 7.5 MW together. Consecutive DR changes the CO~2~ emissions by less than 0.2 % and leaves the daily electric PUE at 1.253, and the CCHP devices lower the evening PUE to 1.217.

For DR practice, these results support sizing consecutive-event contracts of AI data centers by the firm capacity of the controller that operates them rather than by physical capability, and they allow grid operators to accept larger firm commitments from data centers that coordinate computing and storage recovery across events. Future work will extend the framework to geographically distributed data centers that shift work between sites, to the thermal inertia of the server halls as a further recovery resource, and to the co-planning of batteries, connection capacity and DR contracts over the life of the data center.

## Appendix A. Case-study parameters and data

**Table A1.** Parameters of the case study ([S] taken from a cited source, [D] derived from public data, [A] modelling assumption).

| Subsystem | Parameter | Value | Source |
|---|---|---|---|
| Computing | GPUs; node peak power | 16 000 H100-class GPUs in 2 000 eight-GPU nodes; 8.4 kW per node | [@latif2025] [S] |
| | Idle and dynamic power per GPU $p^{idle}$, $p^{dyn}$ | 0.26 kW (25 % of peak) and 0.79 kW | [@fan2007] [A] |
| | Other IT power $P^{oth}$; schedulable fraction $u^{max}$ | 0.6 MW; 0.95 | [A] |
| | Inference dynamic-power factor $\kappa^{inf}$ | 0.65 | [@patel2024] [A] |
| | Workload shares | 25 % of GPUs busy with online inference; 40 % with training and batch work, 75 % of it deferrable; profile shapes from [@weng2022; @stojkovic2025] | [A] |
| | Deferrable classes; lag bounds $L_c$ | C1/C2/C3 by PAI runtime ≤ 1 h, 1–12 h, > 12 h; 0.5/1.5/3 h | [@weng2022] [D]; [@colangelo2026] [A] |
| | Delay and lateness prices $c^{jct}$, $c^{late}$ | 0.5 CNY per GPU·h·h, the loss of value of a delayed job (1 and 2 in Section 5.10.3); 1000 CNY per GPU·h·h, which makes overdue work a last resort | [A] |
| Facility and cooling | Losses $\zeta$; auxiliary power $P^{aux}$ | 5 % of the IT power (UPS, distribution, air handling); 0.3 MW | [A] |
| | Heat per unit of IT power $\theta$; base cooling load $Q_0$ | 1.0; 0.3 MW~th~ | [A] |
| | Electric chillers $\mathrm{COP}_t$, $\bar Q^{EC}$ | 6.0 at 25 °C, −0.12 per °C (bounds 3–7); 30 MW~th~ | [A] |
| CCHP | Gas engine $\bar P^{GT}$, $\eta^{GT}$, heat efficiency, $R^{GT}$ | 3 MW; 0.38; 0.45 ($k^h$ = 1.18); 1.5 MW per 15 min | [A] |
| | Absorption chiller $\mathrm{COP}^{AC}$, $\bar Q^{AC}$ | 0.75; 2.7 MW~th~ | [A] |
| | Gas price $c^{gas}$ | 3.6 CNY/Nm³ at 9.89 kWh/Nm³, i.e. 364 CNY/MWh of fuel | [A] |
| Storage | BESS $\bar P^{B}$, capacity, $\underline E$–$\bar E$, $\eta_c$/$\eta_d$, $c^{deg}$ | 6 MW; 12 MWh; SOC 10–95 % (initial 50 %); 0.95/0.95; 60 CNY/MWh | [@xu2018] [A] |
| | TES $\underline S$–$\bar S$, $\bar Q^{T}$, $\eta^T_c$/$\eta^T_d$, $\sigma$ | 1–10 MWh~th~ (initial 5); 4 MW~th~; 0.98/0.98; 0.5 %/h | [A] |
| Supply | PV | 8 MWp; PVWatts losses 14 %; −0.37 %/°C; NOCT 45 °C | [@dobos2014] [S]; [A] |
| | Weather | ERA5 / Open-Meteo, Suzhou-Wujiang, summer 2024; DR day 5 August 2024 (38.3 °C) | [D] |
| | Grid connection $P^{cap}$; minimum import $P^{min}$ | 1.10 × typical-day peak (16.03 MW); 1.5 MW | [A] |
| Emissions | Emission factors $e^{grid}$, $e^{gas}$ | 0.5617 t CO~2~/MWh (East China grid, 2022); 56.1 t CO~2~/TJ, i.e. 0.202 t CO~2~/MWh of fuel | [@mee2024] [S]; [@ipcc2006] [S] |
| Market | Tariff | Jiangsu two-part TOU: peak 14–22 h ×1.8 and valley ×0.35 on the purchase price | [@ndrc2016] [S] |
| | DR settlement | agreed response cleared by bidding below a cap of 3 CNY/kWh (base case at the cap; 1 and 2 CNY/kWh in Section 5.10.3); ×1.4 (2–4 h notice), ×1.6 (0.5–2 h); valid ≥ 80 %, paid ≤ 120 % | [@jiangsu2024] [S] |
| | Shortfall coefficient $\kappa$ (no monetary shortfall penalty in the Jiangsu rules; 0 in Section 5.10.3); planning margin $\delta^{val}$; full delivery; reliability $\rho$ | 1; 0.1 MW; $\bar r_k\ge 0.98C_k$ ($\epsilon_f$ = 2 %); 0.95 | [A] |
| | Rebound window $\mathcal W_k$; assessment $c^{rb}$ | 2 h after every event; 0 (Jiangsu rules), 0–3 CNY/kW per event in Section 5.9.2 | [A] |
| Method | Terminal values $c^{E}$, $c^{S}$, $c^{B}$ | 500 CNY/MWh of BESS and 100 CNY/MWh~th~ of TES deficit; backlog at its energy cost at the flat price | [A] |
| | MPC | $\Delta t$ = 15 min, $T_H$ = 18 h; evaluation window 00:00–06:00 of the next day (30 h); JR-S with 5 scenarios | [A] |
| | Static split of IR-O\* | $\alpha\in\{0.2,0.3,\dots,1.0\}$, tuned day-ahead for every commitment | [A] |
| | Two-stage model \eqref{eq:ra-obj}–\eqref{eq:ra-cc} | $\epsilon^{C}$ = 100 CNY/MW | [A] |
| | Days | 26 operating days: PAI weekdays after the DR day, each paired with a hot day and an Azure inference day; 14 historical days: the weekdays of the trace before the DR day (five of them, at the 10–90 % quantiles of the deferrable load, for forecasts and benchmark tuning) | [@weng2022; @stojkovic2025] [D] |

## Appendix B. Proofs

**Proof of Proposition 1.** (i) Restricting a feasible schedule of the two-event problem to event B gives a feasible schedule of the single-event problem with the same initial state, so $\Gamma_B\le\Gamma^0_B$.

(ii\) Summing \eqref{eq:dev} over $\mathcal T_B$ gives
$$\begin{aligned}\Gamma_BD_B={}&\psi\textstyle\sum_c\big[B_c(e_B)-B_c(s_B^-)\big]\\&+\sum_{t\in\mathcal T_B}\Big(P^{dis}_t-P^{ch}_t+\frac{Q^{TD}_t-Q^{TC}_t}{\mathrm{COP}}\Big)\Delta t\\&+\sum_{t\in\mathcal T_B}\Delta g_t\,\Delta t .\end{aligned} \label{eqB:sum}$$
By the deadline constraint \eqref{eq:deadline} the first term is at most $\bar X_B-X(s_B^-)$, the second is at most the dischargeable energy $E_s(s_B^-)$ at the start of B, and the third is at most $gD_B$. In the interval, let $c_{\mathcal I}$ be the net catch-up energy and $s_{\mathcal I}$ the net energy drawn by the storage. Summing \eqref{eq:dev} over $\mathcal I$ with $P^{grid}_t\le P^{cap}$ gives the channel constraint $c_{\mathcal I}+s_{\mathcal I}\le H$. The states evolve as $X(s_B^-)=X_A-c_{\mathcal I}\ge0$ and $E_s(s_B^-)\le E_s+\phi(s_{\mathcal I})$ with $\phi(x)=\eta x$ for $x\ge0$ and $\phi(x)=x$ for $x<0$, because every MWh drawn for recharging returns only $\eta$ MWh in B. Hence
$$\begin{aligned}\Gamma_BD_B-gD_B\le{}&\bar X_B-X_A+E_s\\&+\max_{c+s\le H,\ c\le X_A}\big\{c+\phi(s)\big\}.\end{aligned} \label{eqB:max}$$
Catch-up has the marginal value 1 and recharge the marginal value $\eta<1$, so the maximum is attained by $\hat c=\min\{H,X_A\}$ and $\hat s=\max\{H-X_A,0\}$, whose value is $H^{eff}$ in \eqref{eq:heff}. Dividing by $D_B$ gives \eqref{eq:ge}.

(iii\) The computing reduction in B equals the backlog increase in B. Work arriving in B can be deferred by at most $\min(L_c,D_B)$, which contributes at most $p_fD_B$. The debt $X^{due}_A$ is either caught up in the interval ($H_c$), swapped with later-deadline work (at most $W^{sw}$), or executed in B, where it offsets the reduction one to one. The storage contribution is limited by $P_sD_B$ and by $E_s+\eta H_s$. Maximising over the allocations $(H_c,H_s)\in\mathcal H$ of \eqref{eq:hset}, subject to the free GPU and charging-power limits, gives \eqref{eq:gp}. ∎

**Proof of Proposition 2.** Assume, in addition, full pausing of deferrable work in B, the dischargeable energy $\eta_dE_A$ and no gas engine. With catch-up $c\in[0,X]$ and recharge $s\ge0$ in the interval, $c+s\le H$, the deliverable reduction energy of B is
$$\begin{aligned}G(c,s)={}&\min\big\{p_fD_B,\ p_fL-(X-c)\big\}\\&+\min\big\{P_sD_B,\ \eta_dE_A+\eta s\big\}.\end{aligned} \label{eqB:G}$$
Let $c^*$ be the necessary catch-up \eqref{eq:cstar} and $s^{req}=\max\{P_sD_B-\eta_dE_A,0\}/\eta$ the necessary recharge. The first term of $G$ is concave with slope 1 for $c<c^*$ and slope 0 afterwards; the second is concave with slope $\eta$ for $s<s^{req}$ and 0 afterwards. Maximising the sum of two separable concave functions under $c+s\le H$ allocates the channel greedily by marginal value: catch-up up to $c^*$, then recharge up to $s^{req}$. This is the joint allocation of \eqref{eq:alloc}. Independent recovery repays the whole debt first and spends $X-c^*$ of the channel on catch-up of zero marginal value. Substituting both allocations,
$$\begin{aligned}G_{JR}-G_{IR}=\eta\Big[&\min\big\{s^{req},\max\{H-c^*,0\}\big\}\\&-\min\big\{s^{req},\max\{H-X,0\}\big\}\Big]\ge0,\end{aligned} \label{eqB:diff}$$
with the maximum $\eta\min\{X,\,p_f(L-D_B),\,s^{req}\}$. The single-event capability $p_fD_B+P_sD_B$ is restored if and only if $c\ge c^*$ and $s\ge s^{req}$, which requires the channel energy $c^*+s^{req}$ under joint and $X+s^{req}$ under independent recovery. Dividing by $h$ and using $X-c^*=\min\{X,p_f(L-D_B)\}$ gives \eqref{eq:tau}. The difference \eqref{eqB:diff} vanishes if and only if $L\le D_B$ or $X=0$ (no debt can be carried), $s^{req}=0$ (B needs no storage), $H\le c^*$ (the channel only suffices for necessary catch-up) or $H\ge X+s^{req}$ (the channel repays both debts). ∎

Two consequences are used in Section 5. First, the minimum recovery energy $\tau^*h$ is fixed, so iso-capability curves are hyperbolas in the plane of the interval and the channel width: a longer interval and a larger connection margin substitute for each other, and joint recovery shifts the curve by the carried debt $\min\{X,p_f(L-D_B)\}$. Second, with several classes the necessary catch-up is $\sum_c\max\{X_c-p_{f,c}(L_c-D_B),0\}$, so the long-deadline class C3 is carried across events first. The closed form is verified against a discrete-time LP on 68 cases ($p_f$ = 5 MW, $D_B$ = 1 h, $X$ = 5 MWh, $h$ = 3 MW, $L\in\{1,1.5,2,3\}$ h, $\tau\in[0,4]$ h); the two agree to within $10^{-5}$ MW, the rounding of the stored results, and the interval reductions are 0, 0.83, 1.67 and 1.67 h, as given by \eqref{eq:tau} (supplementary Fig. S4).

**Proof of Proposition 3.** For fixed $z_k$ all constraints are linear, so the KKT conditions of \eqref{eq:lagr} are necessary and sufficient for optimality. Stationarity with respect to $P^{grid}_t$ gives $(\pi_t-\lambda^{el}_t+\lambda^{cap}_t+\lambda^{ev}_t)\Delta t=0$ when the minimum import does not bind; here $\lambda^{ev}_t\Delta t$ collects the derivatives of the settlement terms in $\mathcal L^{rest}$, because a step of event $k$ enters $\bar r_k$ in \eqref{eq:rbar} with the weight $-\Delta t/D_k$, so that the multipliers of \eqref{eq:valid}–\eqref{eq:short} divided by $D_k$ form $\lambda^{ev}_t\ge0$. Stationarity with respect to $P^{ch}_t$ gives $(c^{deg}+\lambda^{el}_t-\eta_c\nu_t)\Delta t=0$ when $0<P^{ch}_t<\bar P^{B}$. Stationarity with respect to $Q^{EC}_t$ gives $\chi_t=\lambda^{el}_t/\mathrm{COP}_t$ when the electric chillers operate between their bounds, and stationarity with respect to $y_{c,t}$, through \eqref{eq:it}, gives $\big[(1+\zeta)\lambda^{el}_t+\theta\chi_t\big]p^{dyn}-\mu_{c,t}=0$ when $y_{c,t}$ is interior; substituting $\chi_t$ and \eqref{eq:psi} yields $\mu_{c,t}=\psi_t\lambda^{el}_t$. These are the conditions \eqref{eq:kkt}, and combining the last two gives \eqref{eq:price}. ∎

The channel price of the day-ahead joint plan and the backlog multipliers of the three classes are shown in supplementary Fig. S5; they coincide whenever catch-up and recharge are both interior.

**Proof of Proposition 4.** Write the empirical distribution as $N$ atoms of mass $1/N$ at $\xi_d$. Any $Q\in\mathcal B_\varepsilon(\hat P_N)$ is the image of a transport plan with average displacement at most $\varepsilon$. Moving mass between points on the same side of $C$, or upwards, does not reduce $Q(\xi\ge C)$, so a least favourable plan only moves mass $w_d\in[0,1/N]$ from the atoms of $\mathcal D_C$ to points arbitrarily close below $C$, at the cost $w_d\,\delta_d(C)$; the supremum in \eqref{eq:worst} is therefore the value of the knapsack \eqref{eq:knap}, approached by such plans. The optimum of \eqref{eq:knap} removes the atoms with the smallest margins first. The worst-case probability $\inf_QQ(\xi\ge C)=n(C)/N-m^*_C(\varepsilon)$ therefore stays at least $\rho$ if and only if removing the mass $q(C)/N$, i.e. the $\lfloor q\rfloor$ atoms with the smallest margins and the fraction $q-\lfloor q\rfloor$ of the next one, costs at least $\varepsilon$, which is \eqref{eq:phi}. For $\varepsilon=0$ the condition reduces to $n(C)\ge\rho N$, the sample-average constraint. $\Phi_\rho(C)$ is non-increasing in $C$, because $n(C)$ and all margins decrease with $C$, so the feasible commitments form a lower set and $C^{DRO}_\rho(\varepsilon)$ is non-increasing in $\varepsilon$. When the atoms just above $C$ have large margins, $\Phi_\rho(C)$ is large and a moderate radius does not change the commitment. ∎

If the radius exceeds the finite-sample concentration radius $\varepsilon_{N,\beta}$ of the 1-Wasserstein distance [@esfahani2018], the true capability distribution lies in $\mathcal B_\varepsilon(\hat P_N)$ with confidence $1-\beta$, and the commitment $C^{DRO}_\rho$ is delivered in full with probability at least $\rho$. For $N=14$ such radii exceed the spread of the capability itself, so the case study uses the expected estimation error \eqref{eq:radius}, which scales with the dispersion of the capability, and compares it with a leave-one-out choice (Section 5.6.2).

## Figure captions

**Fig. 1.** Physical architecture and recovery channel. (a) AI data-center integrated energy system with its energy supply (grid connection, PV), conversion and storage (gas engine with heat recovery, BESS), cooling supply (absorption chiller, electric chillers, chilled-water TES) and computing (online inference and non-deferrable training, three deferrable classes C1–C3 with lag bounds 0.5, 1.5 and 3 h) subsystems on one AC bus; the DR operator, the day-ahead commitment and the intraday controller form the dispatch layer. Markers 1–4 on the flow paths trace the closed computing–energy–thermal loop: (1) deferrable work sets the IT power, (2) the IT heat sets the cooling load, (3) chiller power and recovered heat return to the electric balance and (4) the grid import is settled against the baseline. (b) Two consecutive DR events: after the first event, computing catch-up and storage recharge are repaid through one recovery channel between the baseline and the connection limit (nominal channel \eqref{eq:channel}; the actual channel \eqref{eq:actchannel} is measured against the no-DR import of the day).

**Fig. 2.** Recovery-aware coordinated scheduling framework. Day-ahead layer: closed-loop back-test of the intraday controller on the historical days, capability per day \eqref{eq:capability}, Wasserstein-robust capacity by sorting the capability margins (Proposition 4) and cost-optimal commitment \eqref{eq:commit}. Intraday layer: cross-event joint recovery MPC \eqref{eq:mpc} with a 15-min step and an 18-h horizon over all confirmed events. Mini schematics show the historical days, the back-test grid (delivered until the first failure), the empirical capability distribution, the sorted capability margins, the back-tested cost, the measured state, the forecasts, the rolling horizon over the events and the settlement; badges give the lines of Algorithm 1 in Table 3.

**Fig. 3.** Power balance on the typical day (S2, 30-min interval, 7 MW, operating day r21) under (a) IR-O\* and (b) JR-D: supply (grid import, PV, gas engine, BESS discharge) above zero and demand below zero; events shaded. (c, d) Use of the recovery channel $P^{cap}-P^{base}_t$ for compute catch-up and storage recharge, with the energies drawn in the interval between the events.

**Fig. 4.** Recovery states on the typical day for the 30-min (a, c) and the 3-h interval (b, d): (a, b) backlog of the deferrable classes under JR-D and total backlog under IR-O\* and JR-M; (c, d) energy in the BESS and the cold storage.

**Fig. 5.** Sources and uses of the recovery energy on the typical day (S2, 7 MW), relative to the no-DR operation of the same day, under (a) IR-O\* and (b) JR-D: grid energy drawn through the channel is attributed to the connection margin, gas engine, absorption chiller, PV and cold storage; uses are catch-up and recharge in the interval and after the events.

**Fig. 6.** Share of the 26 operating days on which every event is delivered in full (a–c) and on which every event is valid under the 80 % rule (d–f) versus the uniform commitment (grid step 0.5 MW; base system; forecasts of Section 5.1.1 for all controllers), for S1, S2 and S3; bands: 95 % block-bootstrap intervals; ticks: firm capacities at 95 %; arrows: gain of JR-D over the best independent benchmark, a lower bound because neither independent benchmark is firm at 1 MW.

**Fig. 7.** Two-event firm region in S2 (30-min interval, reliability 95 %): largest second-event commitment delivered in full for a fixed first-event commitment, for JR-D and JR-M (bisection on the 26 operating days), and the physical capability with perfect information on the DR day (dashed), which is the same for joint, event-by-event and independent recovery.

**Fig. 8.** Firm capacity versus the event interval (two one-hour events, base system, $\rho$ = 0.95, bisection on the 26 operating days with 0.25 MW resolution): (a) firm capacity of IR-O\*, JR-M and JR-D with the coordination and foresight values shaded; (b) decomposition into the coordination value (JR-M − IR-O\*, a lower bound where IR-O\* stays below 1 MW, hatched) and the cross-event foresight value (JR-D − JR-M).

**Fig. 9.** Sensitivity at a uniform commitment of 7 MW (26 operating days, base devices): (a) full-delivery share of JR-D over the event interval and the connection margin; (b) gain of JR-D over the best independent benchmark; (c) gain over JR-M (percentage points); (d) full-delivery share versus the scale of the lag bounds (S1).

**Fig. 10.** System-level value of joint recovery in S2 (firm capacity by bisection, resolution 0.25 MW): (a) firm capacity versus BESS energy (2-h rating, connection fixed); (b) versus the connection limit; (c) battery energy and (d) connection capacity saved by cross-event foresight for every firm capacity that JR-M reaches (hatched: lower bound, because JR-D exceeds the target already at the smallest connection tested).

**Fig. 11.** Distributionally robust commitment in S1 (a–c) and S2 (d–f): (a, d) closed-loop capability per day on the 14 historical days (filled) and the 26 operating days (hollow); (b, e) robust firm capacity versus the Wasserstein radius, star at the radius $\varepsilon_N$ \eqref{eq:radius}; (c, f) predicted versus realised full-delivery probability for every commitment of the grid, sample average (hollow) and robust (filled).

**Fig. 12.** Role of the integrated energy system (S2, connection limit of the base case; firm capacity at $\rho$ = 0.95 by bisection, 0.25 MW resolution): (a) firm capacity of JR-D without the gas engine, the absorption chiller, the cold storage or all three, and for the resource ablation; (b) composition of the evening recovery channel $P^{cap}-P^{grid}_{noDR}$ on the typical day.

**Fig. 13.** Capacity–service trade-off in S1 (a, b) and S2 (c, d) on the 26 operating days (base system, same commitment for all controllers): uniform commitment versus the mean extra completion time of deferred work (a, c) and the SLA slack used (b, d); filled markers: firm operating points (full delivery on ≥ 95 % of the days); dashed: front of the firm points.

**Fig. 14.** Economics at the same fixed commitment of 7 MW for every controller (26 operating days, base system, DR price 3 CNY/kWh, $\kappa$ = 1): (a) daily cost components relative to no DR, labelled with the share of days with full delivery; (b) paired daily cost differences between JR-D and each benchmark over the 26 operating days; (c) distribution of the worst-event delivery ratio in S2.

**Fig. 15.** Daily benefit relative to no DR versus the uniform commitment, which is the same for every controller at each point, on the 26 operating days in S1 (a, c) and S2 (b, d) (DR price 3 CNY/kWh, $\kappa$ = 1): (a, b) contributions of the cost groups for JR-D, with the DR revenue and the energy savings stacked above and the task delay, storage degradation and shortfall assessment stacked below zero, and the net benefit (line); dashed: cost-optimal day-ahead commitment $C^*$; dash-dotted: firm capacity $C^{firm}_{0.95}$; shaded: commitments delivered in full on at least 95 % of the days; (c, d) net benefit of all controllers, filled markers where full delivery is reached on at least 95 % of the days at that commitment.

**Fig. 16.** Event-call uncertainty and post-event rebound. (a, b) S4-U, third event called with probability 0.6 and confirmed 1 h ahead, 6 MW per event: (a) mean daily cost and (b) mean fulfilment on the days on which the third event is called or cancelled. (c, d) Rebound assessment as a policy parameter (S1, 6 MW, DR day): (c) cost under the Jiangsu rules alone versus the peak post-event rebound; (d) peak rebound versus the assessment price $c^{rb}$.

**Fig. S1.** Two-event capability regions with perfect information on the DR day for different event durations and intervals, and for three events (E1 = E2 = $C_1$, E3 maximised), for joint recovery, event-by-event joint recovery, independent recovery with the best static split and the independent post-event state with joint recovery.

**Fig. S2.** Day-ahead commitment methods in the plane of out-of-sample full delivery and daily benefit (Table 8): closed-loop back-test with sample-average, robust and cost-optimal commitments, and commitments from physical capability (perfect-recourse MILP, single-event capability).

**Fig. S3.** Proposition 1 on the DR day: deliverable capability of event B relative to its single-event capability versus the interval, for joint response and recovery, independent recovery, the independent post-event state with joint recovery and the bound \eqref{eq:bound}, for (a) a 2-h first event and (b) a 2-h second event; (c) capability gain of joint recovery over the interval and the connection margin.

**Fig. S4.** Proposition 2: deliverable reduction of the next event versus the interval in the single-class model, closed form (lines) and discrete-time LP (markers), for lag bounds of 1, 1.5, 2 and 3 h.

**Fig. S5.** Single channel price (Proposition 3): (a) multiplier of the electric balance (channel price $\lambda^{el}_t$) and TOU price; (b) multipliers of the backlog balances of the three classes, which coincide with the channel price when catch-up and recharge are both interior.

## References

[@iea2025]: International Energy Agency. Energy and AI. Paris: IEA; 2025.
[@shehabi2024]: Shehabi A, Smith SJ, Hubbard A, et al. 2024 United States data center energy usage report. Berkeley: Lawrence Berkeley National Laboratory; 2024.
[@kim2026]: Kim D, Dong L, Singh C, et al. Theoretical limits and reform needed for AI data center–grid interconnection. Cell Rep Sustain 2026;3(9):100788.
[@norris2025]: Norris TH, Profeta T, Patiño-Echeverri D, et al. Rethinking load growth: assessing the potential for integration of large flexible loads in US power systems. Durham: Nicholas Institute for Energy, Environment & Sustainability, Duke University; 2025.
[@colangelo2026]: Colangelo P, Coskun AK, Megrue J, et al. AI data centres as grid-interactive assets. Nat Energy 2026;11(2):254–61.
[@google2025]: Google. Demand response agreements with Indiana Michigan Power and the Tennessee Valley Authority targeting machine-learning workloads. Google blog; 4 August 2025.
[@jiangsu2024]: Jiangsu Provincial Development and Reform Commission. Implementation rules for electricity demand response in Jiangsu Province (effective 14 July 2024). Nanjing; 2024 [in Chinese].
[@liu2013]: Liu Z, Wierman A, Chen Y, et al. Data center demand response: avoiding the coincident peak via workload shifting and local generation. Perform Eval 2013;70(10):770–91.
[@wierman2014]: Wierman A, Liu Z, Liu I, et al. Opportunities and challenges for data center demand response. In: Proceedings of the International Green Computing Conference (IGCC); 2014. p. 1–10.
[@chen2020]: Chen M, Gao C, Song M, et al. Internet data centers participating in demand response: a comprehensive review. Renew Sust Energ Rev 2020;117:109466.
[@acun2026]: Acun F, Hankendi C, Levine E, et al. Investigating power consumption flexibility of AI data centers for demand response participation. In: Proceedings of the 17th ACM International Conference on Future and Sustainable Energy Systems (e-Energy); 2026. p. 344–8.
[@wang2025llm]: Wang Y, Guo Q, Chen M. Providing load flexibility by reshaping power profiles of large language model workloads. Adv Appl Energy 2025;19:100232.
[@du2026]: Du B, Fan X, Du E, et al. From tokens to energy flexibility: quantization-enabled demand response for data centers with LLM inference workloads. arXiv:2606.18851; 2026.
[@chenzheng2026]: Chen Y, Zheng X. To defer or to shift? The role of AI data center flexibility on grid interconnection. In: Proceedings of the 2026 ACM Sustainability Week; 2026. p. 322–7.
[@williams2026]: Williams C, Colangelo P, Coskun AK, et al. Power-flexible AI data centers: a new paradigm for grid-responsive compute. arXiv:2606.25098; 2026.
[@zhou2025]: Zhou Y, Wei F, Li S, et al. Data center load modeling through optimal energy consumption characteristics: a path to simultaneously enhance energy efficiency and demand response quality. Appl Energy 2025;393:126095.
[@chen2026]: Chen C, Ye C, Ding Y, et al. Exploring the demand response potential of liquid-cooled data centers. Appl Energy 2026;412:127679.
[@han2024]: Han O, Ding T, Yang M, et al. A novel 4-level joint optimal dispatch for demand response of data centers with district autonomy realization. Appl Energy 2024;358:122590.
[@bian2025]: Bian Y, Xie L, Ma L, et al. A novel two-stage energy sharing model for data center cluster considering integrated demand response of multiple loads. Appl Energy 2025;384:125454.
[@xu2023]: Xu D, Xiang S, Bai Z, et al. Optimal multi-energy portfolio towards zero carbon data center buildings in the presence of proactive demand response programs. Appl Energy 2023;350:121806.
[@lin2025]: Lin J, Han J, Wang Y, et al. Planning and operation optimization of a low-carbon data-center computing integrated energy system considering exergy efficiency. J Shanghai Jiaotong Univ 2025;59(9):1327–37 [in Chinese].
[@fan2026]: Fan H, Chen S, Luo H, et al. Optimal operation of data centers considering multi-energy complementarity of cooling, heating and power and spatio-temporal adjustable loads. South Power Syst Technol 2026;20(5):28–36 [in Chinese].
[@zhang2026]: Zhang S, Ding S, Li Y, et al. A bi-level planning model of integrated energy capacity configuration for data center cluster considering computing-electricity coupling operation and supply-demand uncertainties. Appl Energy 2026;425:128499.
[@liu2024]: Liu X. Research on collaborative scheduling of internet data center and regional integrated energy system based on electricity-heat-water coupling. Energy 2024;292:130462.
[@hou2023]: Hou J, Li H, Nord N, et al. Model predictive control for a university heat prosumer with data centre waste heat and thermal energy storage. Energy 2023;267:126579.
[@zhangy2026]: Zhang Y, Wang Z, Filonenko K, et al. Physics-guided deep reinforcement learning for optimized data center cooling and waste heat recovery utilizing aquifer thermal energy storage. Appl Energy 2026;402:126984.
[@sun2023]: Sun J, Chen S, You P, et al. Battery-assisted online operation of distributed data centers with uncertain workload and electricity prices. IEEE Trans Cloud Comput 2023;11(2):1303–14.
[@xie2027]: Xie X, Huang C, Hu Q, et al. Risk-aware coordinated scheduling of battery storage and AI data centers with decoupled multi-layer AI workload models. Appl Energy 2027;427:128836.
[@lu2026]: Lu X, Qiu J, Lin J, et al. Battery-assisted operation of hyperscale AI data centers under connect-and-manage interconnection practices. arXiv:2605.14105; 2026.
[@yu2026]: Yu Y, Shan K, Li H, et al. Quantitative impacts of energy system flexibility provision and design/operation on data center reliability and the key influential parameters. Appl Energy 2026;415:127904.
[@hao2015]: Hao H, Sanandaji BM, Poolla K, et al. Aggregate flexibility of thermostatically controlled loads. IEEE Trans Power Syst 2015;30(1):189–98.
[@evans2022]: Evans MP, Tindemans SH, Angeli D. Flexibility framework with recovery guarantees for aggregated energy storage devices. IEEE Trans Smart Grid 2022;13(5):3519–31.
[@li2026]: Li M. Beyond scalar flexibility: from eligible AI workloads to dependable load relief. arXiv:2609.05406; 2026.
[@schildbach2014]: Schildbach G, Fagiano L, Frei C, et al. The scenario approach for stochastic model predictive control with bounds on closed-loop constraint violations. Automatica 2014;50(12):3009–18.
[@wangz2024]: Wang Z, Zhang H. Customer baseline load estimation for virtual power plants in demand response: an attention mechanism-based generative adversarial networks approach. Appl Energy 2024;357:122544.
[@wangy2026]: Wang Y, Zhang X, Cai M, et al. Physics-informed baseline load estimation for high-frequency demand response. Appl Energy 2026;405:127155.
[@esfahani2018]: Mohajerin Esfahani P, Kuhn D. Data-driven distributionally robust optimization using the Wasserstein metric: performance guarantees and tractable reformulations. Math Program 2018;171(1–2):115–66.
[@duan2018]: Duan C, Fang W, Jiang L, et al. Distributionally robust chance-constrained approximate AC-OPF with Wasserstein metric. IEEE Trans Power Syst 2018;33(5):4924–36.
[@paredes2026]: Paredes Á, Zhou Y, Aguado JA, et al. Independent aggregators securing end user Wasserstein distributionally robust flexibility through bilevel incentives. Appl Energy 2026;409:127484.
[@zeng2013]: Zeng B, Zhao L. Solving two-stage robust optimization problems using a column-and-constraint generation method. Oper Res Lett 2013;41(5):457–61.
[@mee2024]: Ministry of Ecology and Environment, National Bureau of Statistics. Announcement on the release of the 2022 electricity carbon dioxide emission factors. Beijing; 2024 [in Chinese].
[@ipcc2006]: Intergovernmental Panel on Climate Change. 2006 IPCC guidelines for national greenhouse gas inventories, vol. 2: energy. Hayama: Institute for Global Environmental Strategies; 2006.
[@delbarrio1999]: del Barrio E, Giné E, Matrán C. Central limit theorems for the Wasserstein distance between the empirical and the true distributions. Ann Probab 1999;27(2):1009–71.
[@weng2022]: Weng Q, Xiao W, Yu Y, et al. MLaaS in the wild: workload analysis and scheduling in large-scale heterogeneous GPU clusters. In: Proceedings of the 19th USENIX Symposium on Networked Systems Design and Implementation (NSDI); 2022. p. 945–60.
[@stojkovic2025]: Stojkovic J, Zhang C, Goiri Í, et al. DynamoLLM: designing LLM inference clusters for performance and energy efficiency. In: Proceedings of the IEEE International Symposium on High Performance Computer Architecture (HPCA); 2025. p. 1348–62.
[@chao2011]: Chao H. Demand response in wholesale electricity markets: the choice of customer baseline. J Regul Econ 2011;39(1):68–88.
[@latif2025]: Latif I, Newkirk AC, Carbone MR, et al. Single-node power demand during AI training: measurements on an 8-GPU NVIDIA H100 system. IEEE Access 2025;13:61740–7.
[@fan2007]: Fan X, Weber W-D, Barroso LA. Power provisioning for a warehouse-sized computer. In: Proceedings of the 34th Annual International Symposium on Computer Architecture (ISCA); 2007. p. 13–23.
[@patel2024]: Patel P, Choukse E, Zhang C, et al. Characterizing power management opportunities for LLMs in the cloud. In: Proceedings of the 29th ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS); 2024. p. 207–22.
[@xu2018]: Xu B, Zhao J, Zheng T, et al. Factoring the cycle aging cost of batteries participating in electricity markets. IEEE Trans Power Syst 2018;33(2):2248–59.
[@dobos2014]: Dobos AP. PVWatts version 5 manual. Technical Report NREL/TP-6A20-62641. Golden: National Renewable Energy Laboratory; 2014.
[@ndrc2016]: General Office of the National Development and Reform Commission. Notice on improving the implementation of the capacity charge for two-part tariff users (Fagai Ban Jiage [2016] No. 1583). Beijing; 2016 [in Chinese].
