# Recovery-aware coordinated scheduling of computing workloads and energy storage for deliverable consecutive demand response in AI data centers

> Draft for *Applied Energy*, complete. The numbers of the Abstract, Section 5 and Section 6 come from `tools/paper_numbers.py` applied to `matlab/results/` (see `paper/numbers.md`), and all figures from `tools/plot_paper.py` (`paper/figures/`).

## Highlights

- Model computing backlog and storage deficit as debts sharing one recovery channel.
- Certify firm consecutive DR capacity from closed-loop capability via Wasserstein DRO.
- Deliver 7.5 MW firmly by cross-event joint recovery, 94 % of physical capability.
- Show that foresight adds up to 4.0 MW of firm capacity at short event intervals.
- Quantify a 9.3 MWh battery saving from foresight that extra connection cannot buy.

## Abstract

AI data centers (AIDCs) are becoming large flexible loads that are called upon several times within one evening peak. However, each demand-response (DR) event leaves deferred computing work and depleted storage that compete for grid headroom before the next event, so the capacity an AIDC can firmly commit is decided during recovery. This study develops a recovery-aware coordinated scheduling framework for consecutive DR of an AIDC integrated energy system. A cross-event recovery model couples deadline-bound computing backlogs, battery and cold-storage deficits and combined cooling, heating and power through one recovery channel, and bounds the next deliverable reduction in closed form. The firm consecutive DR capacity, the largest uniform commitment delivered in full in every event with a prescribed probability, is certified day-ahead from the controller's closed-loop capability within a Wasserstein ambiguity set, solved exactly by sorting through its dual, and delivered by an intraday cross-event joint recovery model predictive controller. Case studies on a 16 000-GPU data center under the Jiangsu DR rules, over 26 operating days from public traces, show that cross-event joint recovery firmly delivers 7.5 MW with two events, 94 % of the physical capability, and 6.5 MW with three, whereas tuned and price-coordinated independent recovery is not firm even at 1 MW. Cross-event foresight adds up to 4.0 MW at short intervals and substitutes 9.3 MWh of battery. The cost-optimal robust commitment is delivered in full on every operating day, against 85 % for a perfect-recourse two-stage commitment, and earns 43–45 thousand CNY per day.

**Keywords:** AI data center; consecutive demand response; computing–energy coupling; firm deliverable capacity; distributionally robust optimisation; integrated energy system

## Nomenclature

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
| IR-O\* / IR-P | Independent recovery with a day-ahead tuned static split / with day-ahead channel-price coordination |
| JR-D / JR-M / JR-S | Joint recovery: cross-event deterministic MPC (proposed) / event-by-event / scenario MPC |
| KKT | Karush–Kuhn–Tucker |
| LP / MILP | Linear programming / mixed-integer linear programming |
| MPC | Model predictive control |
| PV | Photovoltaic |
| SAA | Sample average approximation |
| SLA | Service-level agreement |
| SOC | State of charge |
| TES | Thermal (chilled-water) energy storage |
| TOU | Time of use |

**Parameters**

| | |
|---|---|
| $\Delta t$, $T_H$ | Time step (0.25 h); MPC horizon (18 h) |
| $\mathcal K$, $\mathcal T_k$, $D_k$ | Set of DR events; steps and duration of event $k$ |
| $s_k$, $e_k$, $\tau$ | First and last step of event $k$; interval between two events (h) |
| $C_k$ | DR commitment of event $k$ (MW) |
| $\pi_t$, $\pi_k$ | TOU energy price; DR unit price of event $k$ (CNY/MWh) |
| $\kappa$ | Shortfall assessment coefficient |
| $\delta^{val}$, $M$ | Planning margin above the validity threshold (MW); big-M constant |
| $P^{base}_t$ | DR baseline (MW) |
| $P^{cap}=\gamma\hat P$, $P^{min}$ | Grid connection limit, with margin $\gamma$ over the typical-day peak $\hat P$; minimum import (MW) |
| $N^{GPU}$, $p^{idle}$, $P^{oth}$ | Number of GPUs; idle power per GPU; other IT power (MW) |
| $p^{dyn}$, $\kappa^{inf}$, $P^{fix}$ | Dynamic power per busy GPU; dynamic-power factor of inference; schedule-independent IT power (MW) |
| $u^{max}$ | Maximum schedulable GPU fraction |
| $a_{c,t}$ | Arrival rate of deferrable work of class $c$ (busy GPUs) |
| $L_c$, $\bar B_{c,t}(L_c)$ | Lag bound (deadline) of class $c$ (h); class-$c$ work that arrived within the last $L_c$ hours (GPU·h) |
| $G^{inf}_t$, $G^{fix}_t$ | Busy GPUs of online inference and non-deferrable training |
| $\zeta$, $P^{aux}$ | Distribution and air-handling losses as a share of the IT power; auxiliary facility power (MW) |
| $\theta$, $Q_0$ | Heat to be removed per unit of IT power; base cooling load (MW~th~) |
| $\mathrm{COP}_t$, $\mathrm{COP}^{AC}$ | Electric chiller COP (temperature dependent); absorption chiller COP |
| $\bar Q^{EC}$, $\bar Q^{AC}$, $\bar Q^{T}$ | Cooling capacity of the electric and absorption chillers; TES power rating (MW~th~) |
| $\bar P^{GT}$, $R^{GT}$, $k^h$ | Gas-engine rating; ramp limit per step (MW); recoverable heat per unit of output |
| $\eta^{GT}$, $c^{gas}$ | Gas-engine electrical efficiency; gas price (CNY/MWh of fuel) |
| $\bar P^{PV}_t$ | Available PV power (MW) |
| $\eta_c$, $\eta_d$, $c^{deg}$ | BESS charging / discharging efficiency; degradation cost (CNY/MWh) |
| $\underline E$, $\bar E$, $\bar P^{B}$ | BESS energy bounds (MWh) and power rating (MW) |
| $\eta^T_c$, $\eta^T_d$, $\sigma$ | TES charging / discharging efficiency; hourly loss rate |
| $\underline S$, $\bar S$ | TES energy bounds (MWh~th~) |
| $c^{jct}$, $c^{late}$ | Delay and lateness prices of deferred work (CNY per GPU·h·h) |
| $\alpha$ | Compute share of the reduction in the static split of IR-O\* |
| $\rho$, $\epsilon_f$ | Target reliability of the firm capacity; metering tolerance of full delivery (2 %) |
| $\mathcal G$, $\Delta_{\mathcal G}$ | Commitment grid and its step (MW) |
| $\Omega^{DA}$, $\Omega$, $N$ | Historical days used day-ahead; operating (test) days; number of historical days |
| $\varepsilon$, $\varepsilon_N$ | Radius of the 1-Wasserstein ambiguity set; expected estimation error (MW) |
| $\epsilon^{C}$, $p_\omega$ | Weight of the commitment and probability of scenario $\omega$ in the two-stage model |

**Variables**

| | |
|---|---|
| $y_{c,t}$ | Busy GPUs executing class-$c$ work |
| $B_{c,t}$, $v_{c,t}$ | Backlog and overdue work of class $c$ (GPU·h) |
| $P^{IT}_t$, $P^{grid}_t$ | IT power; grid import (MW) |
| $P^{ch}_t$, $P^{dis}_t$, $E_t$ | BESS charging, discharging power and stored energy |
| $Q^{TC}_t$, $Q^{TD}_t$, $S_t$ | TES charging, discharging and stored cold |
| $P^{GT}_t$, $H^{AC}_t$, $Q^{EC}_t$, $P^{PV}_t$ | Gas-engine output, heat to the absorption chiller, electric chiller output, PV output |
| $\psi_t$, $X_t$ | Facility energy per GPU·h of catch-up (MWh); computing debt (MWh) |
| $\mathbf x_{e_k}$, $H_k$ | Recovery state at the end of event $k$; recovery channel between events $k$ and $k+1$ (MWh) |
| $\bar r_k$, $\Gamma_k$ | Average reduction of event $k$ w.r.t. the baseline; deliverable reduction of event $k$ (MW) |
| $z_k$, $R_k$, $s^{f}_k$ | Validity indicator, paid reduction and shortfall of event $k$ |
| $J$, $J^{term}$ | Comprehensive cost of the DR day; terminal value of the remaining debts (CNY) |
| $u_\omega$ | Indicator that every event is delivered in full in scenario $\omega$ |
| $C^{firm}_\rho$, $\hat C^{firm}_\rho$, $\mathcal C_\rho$ | Firm consecutive DR capacity at reliability $\rho$, its SAA estimate (MW); reliability region |
| $\xi_d$, $J_d(C)$, $\bar J(C)$ | Closed-loop capability of the controller on day $d$ (MW); its cost on day $d$ and mean cost at commitment $C$ |
| $\hat P_N$, $\mathcal B_\varepsilon(\hat P_N)$ | Empirical distribution of the capability; 1-Wasserstein ambiguity set |
| $\delta_d(C)$, $n(C)$, $q(C)$ | Capability margin of day $d$; number of days delivering $C$; slack $n(C)-\rho N$ |
| $w_d$, $\lambda$ | Probability mass moved from day $d$; dual variable of the transport budget |
| $C^{DRO}_\rho(\varepsilon)$, $\Phi_\rho(C)$ | Distributionally robust firm capacity; certified reliability margin (MW) |
| $C^*$ | Cost-optimal day-ahead commitment (MW) |

## 1. Introduction

The rapid growth of artificial intelligence (AI) is reshaping electricity demand. The International Energy Agency projects global data-center consumption to rise from about 415 TWh in 2024 to about 945 TWh by 2030 [1], and data centers already account for 4.4 % of electricity use in the United States [2]. Grid connection capacity has become the binding constraint for new AI campuses, and load flexibility is increasingly treated as a condition for faster interconnection: curtailing large loads for 0.25–1 % of the year would accommodate 76–126 GW of new load in 22 US balancing areas [3]. AI data centers (AIDCs) are already operated as grid-interactive assets. A field demonstration in Phoenix reduced the power of a production GPU cluster by 25 % for three hours without violating service levels [4], and utilities have signed demand-response (DR) agreements that target machine-learning workloads [5]. DR programs reward this flexibility at increasing frequency. In Jiangsu, China, the 2024 implementation rules allow up to two agreed DR events per day plus rapid peak-shaving calls at short notice, settled on the average reduction against a five-day baseline [6]. Consecutive events within one evening peak are therefore the normal operating condition of a DR-participating AIDC.

Each event leaves recovery debts behind. Deferred training and batch work accumulates as a backlog that must be completed before its service deadline, and the storage that covered part of the reduction must be recharged. Both debts are repaid by drawing power above the baseline through the same grid headroom before the next event starts. The reduction that an AIDC can deliver in the next event is therefore decided by how it recovers from the previous one, and this cross-event coupling determines how much flexibility the grid can count on.

In the area of data-center DR and computing flexibility, workload shifting and local generation were introduced by Liu et al. [7] and reviewed in [8,9]. Recent studies quantify the flexibility of AI workloads: Acun et al. reported 18–55 % power flexibility of AI data centers [10], Du et al. added inference quantization as a DR lever [11], Chen and Zheng showed that deferring workloads reduces interconnection cost with diminishing returns in the delay window [12], and Williams et al. framed power-flexible AI data centers as grid-responsive compute [13]. In *Applied Energy*, data-center load models for DR [14], the DR potential of liquid-cooled data centers [15] and a four-level joint dispatch of data-center DR [16] have been developed. Overall, existing studies evaluate the curtailment capability of a single event, whereas the recovery state that one event passes on to the next remains insufficiently explored.

In the area of computing–energy coupling in data-center integrated energy systems (IES), data centers increasingly operate with combined cooling, heating and power (CCHP), cold storage and batteries [17,18]. Zhang et al. coupled computing and electricity in a bi-level capacity planning model of a data-center cluster under supply–demand uncertainty [19], Lu et al. studied battery-assisted operation of hyperscale AI data centers [20], and the reliability impact of energy-system flexibility on data centers has been quantified in [21]. These studies capture the coupling between computing, power and heat within a scheduling period. Overall, they treat the computing backlog and the state of charge as internal operating states rather than as debts that are inherited across DR events and decide the next deliverable reduction.

In the area of deliverability and commitment of flexible resources, aggregate flexibility models describe the power–energy envelope of homogeneous devices [22], and Evans et al. derived recovery guarantees for aggregated energy storage that must be restored between service requests [23]. Li distinguished eligible AI workloads from dependable load relief [24], and the scenario approach provides probabilistic guarantees for closed-loop constraint satisfaction [25]. Distributionally robust chance constraints over Wasserstein ambiguity sets offer data-driven reliability guarantees [26,27] and are widely used for flexibility commitments. Their two-stage form, solved by column-and-constraint generation [28], evaluates the second stage with perfect recourse and therefore certifies physical capability rather than the deliverability of the controller that operates the resource. Overall, recovery guarantees have been developed for one type of resource with one type of debt, whereas an AIDC holds two heterogeneous debts at once: computing debt is lossless but deadline-bound, storage debt is lossy but has no deadline, and both compete for the same recovery channel.

Despite substantial progress in data-center DR, computing–energy coupling and flexibility commitment, three research gaps remain. First, the heterogeneous recovery debts that one DR event leaves for the next, and their competition for a shared grid connection, have not been modelled in an AIDC integrated energy system. Second, no capacity metric certifies what a given controller delivers in every event of a DR day, and commitments derived from physical capability overstate it. Third, coordinated scheduling that exploits cross-event foresight during recovery is lacking, and its value relative to coordination alone, the conditions under which it pays off and its equivalent in battery and connection capacity are unknown. Consequently, a framework that sizes and delivers the consecutive DR commitments of an AIDC from its recovery is still lacking.

To address these gaps, this paper develops a recovery-aware coordinated scheduling framework for consecutive DR of an AIDC integrated energy system. The framework models the recovery debts of every event, certifies the firm consecutive capacity of the controller day-ahead and delivers it with cross-event joint recovery in real time. The main contributions are summarised as follows.

(1) A cross-event heterogeneous recovery model of the AIDC integrated energy system is developed. Deadline-bound computing backlogs of three workload classes and lossy battery and cold-storage deficits are modelled as recovery debts that share one grid recovery channel, coupled with the electric, cooling and heat balances of the CCHP-based energy system and the Jiangsu settlement rules. Two propositions bound the deliverable reduction of the next event and give the closed-form minimum recovery interval together with the conditions under which joint recovery is valuable.

(2) A firm consecutive DR capacity metric and its distributionally robust commitment are proposed. The firm capacity is the largest uniform commitment delivered in full in every event with a prescribed probability, generalised to a multi-event reliability region. The day-ahead commitment is certified from the closed-loop capability of the controller on historical days within a 1-Wasserstein ambiguity set; a linear-programming dual reformulates the worst-case failure probability, and Proposition 3 solves the robust capacity exactly by sorting. Unlike a perfect-recourse two-stage commitment, which measures physical capability, the certified commitment is deliverable by the controller that operates the resource.

(3) A recovery-aware coordinated scheduling framework is established and validated at the system level. The robust commitment is coupled with an intraday cross-event joint recovery model predictive controller (MPC). A controlled comparison with tuned and price-coordinated independent recovery and event-by-event joint recovery on 26 operating days separates the value of coordination from that of cross-event foresight, converts the capacity gain into equivalent battery energy and connection capacity, and quantifies the contribution of the gas engine, absorption chiller and cold storage.

## 2. System architecture and consecutive demand response problem

### 2.1 Physical architecture of the AIDC integrated energy system

The AIDC integrated energy system considered in this paper couples computing, power, heat and cooling (Fig. 1a). It consists of four subsystems. The energy supply subsystem comprises the grid connection with limit $P^{cap}$ and 8 MWp of rooftop and adjacent PV. The energy conversion and storage subsystem comprises a 3 MW gas engine whose recovered heat drives a single-effect absorption chiller (CCHP) and a 6 MW/12 MWh BESS. The cooling subsystem comprises electric chillers, whose COP depends on the ambient temperature, the absorption chiller and a 10 MWh chilled-water TES. The computing subsystem hosts 16 000 H100-class GPUs in 2 000 eight-GPU nodes; its load consists of online inference and non-deferrable training (Flex 0) and three classes of deferrable training and batch work (C1–C3) that tolerate a delay up to their lag bounds $L_c$ = 0.5, 1.5 and 3 h, following the flexibility tiers of industrial AI-DR programs [4]. A dispatch layer sets the day-ahead DR commitments and operates all flexible resources in real time.

### 2.2 Computing–energy–thermal coupling mechanism

The four subsystems are coupled through three energy flows that close one loop. (i) Computing–electricity: every busy GPU draws dynamic power, so the scheduling of deferrable work sets the IT power, and every deferred GPU·h acts as a lossless virtual discharge that must be recharged before its deadline. (ii) Electricity–cooling: the IT power is dissipated as heat, which the electric chillers, the absorption chiller and the TES remove; the chiller power, divided by a COP that falls with the ambient temperature, returns to the electric balance. (iii) Heat recovery: the exhaust heat of the gas engine drives the absorption chiller, so one MW of engine output displaces both grid import and chiller power. Through these flows, deferring computing work, discharging the BESS, discharging the TES and running the gas engine all act on the same grid import, which is the quantity that the DR operator settles, and all draw on the same headroom when the debts are repaid. The recovery channel is therefore a system-level resource that the four subsystems share.

### 2.3 Consecutive DR events and recovery debts

A DR operator confirms events $k\in\mathcal K$ with commitments $C_k$. Under the Jiangsu rules [6], an event is valid when the average reduction against the five-day baseline reaches 80 % of the commitment; the payment is proportional to the reduction up to 120 % of the commitment, and a shortfall is assessed at $\kappa$ times the event price. Three event scenarios are studied (Section 5.1): two agreed one-hour events at 17:00 and 19:00 (S1, the rule-compliant base case), the same events with the interval shortened to 30 min (S2), and a high-stress extension with a third, rapid peak-shaving event at 21:00 announced 3 h ahead (S3).

During event $k$, the AIDC defers class-$c$ work and discharges storage. At the end of the event it holds the recovery state $\mathbf x_{e_k}=(B_{1},B_{2},B_{3},E,S)$: the backlogs are deadline-bound computing debts, and the deficits $\bar E-E$ and $\bar S-S$ are lossy storage debts. Both are repaid between events by importing power above the baseline (Fig. 1b), so both compete for the recovery channel
$$H_k=\sum_{t=e_k+1}^{s_{k+1}-1}\max\{P^{cap}-P^{base}_t,\,0\}\,\Delta t. \tag{1}$$
The scheduling problem is to decide which debt to repay first so that the reduction deliverable in event $k+1$ is maximised; the commitment problem is to determine how much consecutive capacity the AIDC can firmly offer when recovery is coordinated across events.

## 3. Cross-event recovery model of the AIDC integrated energy system

This section formulates the operation of the AIDC integrated energy system over a DR day as a mixed-integer linear program (MILP) with a 15-min step. The model underlies both the intraday controller and the closed-loop capability of Section 4.

### 3.1 IT power and computing backlog model

The IT power follows the number of busy GPUs. With the idle and other IT power collected in $P^{fix}=N^{GPU}p^{idle}+P^{oth}$, it is
$$P^{IT}_t=P^{fix}+p^{dyn}\Big(\kappa^{inf}G^{inf}_t+G^{fix}_t+\sum_{c}y_{c,t}\Big). \tag{2}$$
Deferred work of class $c$ accumulates in the backlog
$$B_{c,t}=B_{c,t-1}+\big(a_{c,t}-y_{c,t}\big)\Delta t,\qquad 0\le B_{c,t}\le \bar B_{c,t}(L_c)+v_{c,t}, \tag{3}$$
where $\bar B_{c,t}(L_c)$ is the work that arrived within the last $L_c$ hours and is therefore not yet due, and $v_{c,t}\ge 0$ is overdue work priced at $c^{late}$. The schedulable GPUs are limited by the utilisation cap $u^{max}$,
$$\textstyle\sum_c y_{c,t}\le u^{max}N^{GPU}-G^{inf}_t-G^{fix}_t. \tag{4}$$
Each GPU·h of backlog requires $\psi_t=(1+\zeta+\theta/\mathrm{COP}_t)\,p^{dyn}$ MWh of facility energy when it is caught up, including distribution losses and cooling. The computing debt $X_t=\psi_t\sum_cB_{c,t}$ therefore behaves like the discharge of a lossless virtual storage whose recharge has deadlines.

### 3.2 Electrochemical and cold storage model

The BESS and the TES evolve as
$$E_t=E_{t-1}+\Big(\eta_cP^{ch}_t-\frac{P^{dis}_t}{\eta_d}\Big)\Delta t,\quad \underline E\le E_t\le\bar E,\quad 0\le P^{ch}_t,P^{dis}_t\le\bar P^{B}, \tag{5}$$
$$S_t=(1-\sigma\Delta t)S_{t-1}+\Big(\eta^T_cQ^{TC}_t-\frac{Q^{TD}_t}{\eta^T_d}\Big)\Delta t,\quad \underline S\le S_t\le\bar S,\quad 0\le Q^{TC}_t,Q^{TD}_t\le\bar Q^{T}. \tag{6}$$
Their deficits $\bar E-E_t$ and $\bar S-S_t$ are lossy debts: every MWh drawn for recharging returns only the round-trip efficiency in the next event.

### 3.3 CCHP, cooling supply and grid interaction model

The heat of the IT equipment, $\theta P^{IT}_t$, and the base cooling load $Q_0$ are removed by the electric chillers, the absorption chiller driven by recovered heat and the TES,
$$Q^{EC}_t+\mathrm{COP}^{AC}H^{AC}_t+Q^{TD}_t-Q^{TC}_t=\theta P^{IT}_t+Q_0,\qquad H^{AC}_t\le k^hP^{GT}_t, \tag{7}$$
where $k^h$ is the recoverable heat per unit of gas-engine output. The electric balance includes the distribution losses, the auxiliary load and the chiller power,
$$P^{grid}_t+P^{PV}_t+P^{GT}_t+P^{dis}_t-P^{ch}_t=(1+\zeta)P^{IT}_t+P^{aux}+\frac{Q^{EC}_t}{\mathrm{COP}_t}. \tag{8}$$
The grid import respects the connection limit and a minimum import,
$$P^{min}\le P^{grid}_t\le P^{cap}, \tag{9}$$
and the gas engine, the PV and the chillers respect their ratings, the ramp limit of the engine and the available PV power,
$$\begin{aligned}&0\le P^{GT}_t\le\bar P^{GT},\qquad |P^{GT}_t-P^{GT}_{t-1}|\le R^{GT},\qquad 0\le P^{PV}_t\le\bar P^{PV}_t,\\&0\le Q^{EC}_t\le\bar Q^{EC},\qquad 0\le\mathrm{COP}^{AC}H^{AC}_t\le\bar Q^{AC}.\end{aligned} \tag{10}$$
Through (7)–(10), deferring computing work lowers both the IT power and the chiller power, and recovered heat and stored cold widen the headroom $P^{cap}-P^{grid}_t$ on which recovery draws.

### 3.4 Settlement of consecutive DR events

The average reduction of event $k$ is $\bar r_k=\frac{1}{D_k}\sum_{t\in\mathcal T_k}(P^{base}_t-P^{grid}_t)\Delta t$. With the validity indicator $z_k\in\{0,1\}$, the paid reduction $R_k$ and the shortfall $s^{f}_k$, the Jiangsu settlement reads
$$\bar r_k\ge z_k\,(0.8C_k+\delta^{val})-M(1-z_k),\quad R_k\le 1.2C_kz_k,\quad R_k\le\bar r_k+M(1-z_k),\quad s^{f}_k\ge C_k-\bar r_k, \tag{11}$$
where $\delta^{val}$ is a planning margin above the 80 % threshold and the big-M terms deactivate the payment constraints of an invalid event. The rule that the load during an event may not exceed the baseline maximum is enforced as a soft constraint, and a post-event rebound assessment, which the Jiangsu rules do not contain, is examined as a policy parameter in Section 5.8.

### 3.5 Comprehensive cost objective

The operator minimises the comprehensive cost of the DR day,
$$J=\sum_t\Big[\pi_tP^{grid}_t+\frac{c^{gas}}{\eta^{GT}}P^{GT}_t+c^{deg}(P^{ch}_t+P^{dis}_t)+c^{jct}\sum_cB_{c,t}+c^{late}\sum_cv_{c,t}\Big]\Delta t-\sum_k\pi_kD_kR_k+\sum_k\kappa\pi_kD_ks^{f}_k+J^{term}, \tag{12}$$
which comprises electricity, gas, storage degradation, delay of deferred work and shortfall assessment, net of the DR revenue. The terminal term $J^{term}$ values the backlog left at the end of the window at its energy cost and the storage deficit at its recharge cost, so that no strategy can shift cost beyond the evaluation window.

### 3.6 Firm consecutive DR capacity

Let $\omega\in\Omega$ denote a realisation of computing arrivals, inference load, weather and event calls, and $\bar r_{k,\omega}(C)$ the reduction delivered in event $k$ by a given operating strategy when the uniform commitment $C$ is in force. The **firm consecutive DR capacity** at reliability $\rho$ is
$$C^{firm}_\rho=\max\Big\{C:\ \Pr_\omega\big[\bar r_{k,\omega}(C)\ge (1-\epsilon_f)C,\ \forall k\in\mathcal K\big]\ge\rho\Big\}, \tag{13}$$
with a metering tolerance $\epsilon_f$ = 2 %. Its multi-event generalisation is the reliability region $\mathcal C_\rho=\{(C_1,\dots,C_K):\Pr[\bar r_{k,\omega}\ge(1-\epsilon_f)C_k\ \forall k]\ge\rho\}$, which shows how a higher commitment in one event compresses the deliverable space of the next. $C^{firm}_\rho$ is a deliverability metric for the grid and is reported separately from the settlement validity ($\bar r_k\ge 0.8C_k$).

Because a larger commitment can only tighten the delivery requirement, the delivery indicator is monotone in $C$ for a fixed realisation, and (13) is evaluated by sample average approximation (SAA): for every $C$ on a grid $\mathcal G$, the strategy is simulated in closed loop on the realisations $\omega\in\Omega$, and
$$\hat C^{firm}_\rho=\max\Big\{C\in\mathcal G:\ \frac{1}{|\Omega|}\sum_{\omega}\mathbb 1\big[\bar r_{k,\omega}(C')\ge(1-\epsilon_f)C'\ \forall k\big]\ge\rho\ \ \forall C'\le C,\ C'\in\mathcal G\Big\}. \tag{14}$$
Confidence intervals of $\hat C^{firm}_\rho$ and of the capacity gain $\Delta C_\rho$ between two strategies are obtained by a block bootstrap over operating days.

### 3.7 Theoretical properties of cross-event recovery

**Proposition 1 (capability bound of the next event).** Let event A leave the computing debt $X_A$ and the storage state $E_s$, and let $H$ be the recovery channel before event B of duration $D_B$. The reduction deliverable in B satisfies $\Gamma_B\le\min\{\Gamma^0_B,\Gamma^E,\Gamma^P\}$, where $\Gamma^0_B$ is the single-event capability, the energy bound is $\Gamma^E=(\bar X_B-X_A+E_s+H^{eff})/D_B+g$ with $H^{eff}=H$ if $H\le X_A$ and $X_A+\eta(H-X_A)$ otherwise, $\eta$ is the round-trip efficiency of recharging and $g$ the additional gas-engine output, and the power bound $\Gamma^P$ accounts for the backlog of A that falls due within B and for work that can be swapped past the end of B. The channel width, the task deadlines and the stored energy therefore jointly determine the next deliverable reduction.

**Proposition 2 (value of joint recovery).** In a single-class model with constant arrivals and a constant channel width $h$, joint recovery repays only the computing debt $c^*=[X-p_f(L-D_B)]^+$ that would fall due before the end of the next event and uses the rest of the channel for recharge, whereas independent recovery repays the full debt $X$ first. The minimum full-recovery intervals differ by
$$\tau^*_{IR}-\tau^*_{JR}=\frac{\min\{X,\ p_f(L-D_B)\}}{h}. \tag{15}$$
Joint recovery has no value when the deadline is not longer than the next event ($L\le D_B$), when storage does not need recharging, or when the channel is either too narrow or wide enough to repay both debts within the interval.

The proofs are given in Appendix B, which also shows from the Karush–Kuhn–Tucker conditions of (2)–(12) that a single channel price values both debts when catch-up and recharge are interior (Remark B.1); this is the price that IR-P passes to the IT scheduler (Section 4.3). Proposition 2 underlies the mechanism of Section 5.2: long-deadline work need not be caught up immediately, which frees the recovery channel for the storage that the next event needs.

## 4. Recovery-aware coordinated scheduling framework

The framework comprises two layers (Fig. 2). The day-ahead layer certifies the commitments from the closed-loop capability of the intraday controller on historical days, and the intraday layer operates the AIDC with cross-event joint recovery. Algorithm 1 in Table 1 summarises both layers.

### 4.1 Day-ahead recovery-aware commitment

#### 4.1.1 Closed-loop capability on historical days

The commitment of every event must anticipate the recovery state that the preceding events leave behind, as delivered by the controller that operates the AIDC. The day-ahead layer therefore measures the capability of that controller in closed loop. For every historical day $d$ of $\Omega^{DA}$ and every candidate commitment $C$ of the grid $\mathcal G$, the intraday controller of Section 4.2 is simulated with the realised data of day $d$, which yields the comprehensive cost $J_d(C)$ and the capability
$$\xi_d=\max\big\{C\in\mathcal G:\ \bar r_{k,d}(C')\ge(1-\epsilon_f)C'\ \ \forall k,\ \forall C'\le C,\ C'\in\mathcal G\big\}+\tfrac12\Delta_{\mathcal G}, \tag{16}$$
the midpoint between the largest uniform commitment that the controller delivers in full on day $d$ and the next commitment of the grid (step $\Delta_{\mathcal G}$), at which delivery first fails. The back-test visits the commitments in increasing order and stops simulating a day after its first failure; it yields every $\xi_d$, and every $J_d(C)$ for $C\le\min_d\xi_d$, with about half of the closed-loop runs of the full grid.

#### 4.1.2 Wasserstein ambiguity set and dual reformulation

The empirical distribution $\hat P_N=\frac1N\sum_d\delta_{\xi_d}$ summarises the deliverability of the controller on the $N$ historical days. Because the operating day can differ from them, the commitment is protected against all distributions within the 1-Wasserstein ball $\mathcal B_\varepsilon(\hat P_N)=\{Q:\ W_1(Q,\hat P_N)\le\varepsilon\}$ [26]:
$$C^{DRO}_\rho(\varepsilon)=\max\Big\{C\in\mathcal G:\ \inf_{Q\in\mathcal B_\varepsilon(\hat P_N)}Q(\xi\ge C)\ge\rho\Big\}, \tag{17}$$
the distributionally robust counterpart of (13). The radius $\varepsilon$ (MW) is the largest average shift of the capability that the commitment must withstand.

The inner problem of (17) is an optimisation over probability distributions. For a commitment $C$, let $\mathcal D_C=\{d:\xi_d\ge C\}$ be the days that deliver it, $n(C)=|\mathcal D_C|$, and $\delta_d(C)=\xi_d-C$ their capability margins. The least favourable distribution moves the probability mass $w_d\in[0,1/N]$ from the atoms in $\mathcal D_C$ to just below $C$ at the transport cost $\delta_d(C)$ per unit of mass, which turns the worst-case failure probability into a fractional knapsack problem ((B.4) in Appendix B). Its linear-programming dual is the one-dimensional problem
$$\sup_{Q\in\mathcal B_\varepsilon(\hat P_N)}Q(\xi<C)=\frac{N-n(C)}{N}+\min_{\lambda\ge0}\Big\{\lambda\varepsilon+\frac1N\sum_{d\in\mathcal D_C}\max\{1-\lambda\,\delta_d(C),\,0\}\Big\}, \tag{18}$$
where $\lambda$ is the shadow price of the transport budget. The objective of (18) is convex and piecewise linear in $\lambda$ with breakpoints at $\lambda=1/\delta_d(C)$, so the infinite-dimensional inner problem of (17) reduces to sorting the capability margins.

**Proposition 3 (exact distributionally robust firm capacity).** For a commitment $C$, let $\delta_{(1)}(C)\le\delta_{(2)}(C)\le\dots$ be the sorted margins of the days in $\mathcal D_C$ and $q(C)=n(C)-\rho N$. The robust constraint in (17) holds if and only if $q(C)\ge0$ and
$$\Phi_\rho(C)=\frac1N\Big[\sum_{j=1}^{\lfloor q\rfloor}\delta_{(j)}(C)+\big(q-\lfloor q\rfloor\big)\,\delta_{(\lfloor q\rfloor+1)}(C)\Big]\ \ge\ \varepsilon . \tag{19}$$
Hence (i) $C^{DRO}_\rho(\varepsilon)=\max\{C\in\mathcal G:\ q(C)\ge0,\ \Phi_\rho(C)\ge\varepsilon\}$ is obtained by sorting; (ii) for $\varepsilon=0$ it equals the sample-average capacity, the empirical $(1-\rho)$-quantile of $\xi$; (iii) it is non-increasing in $\varepsilon$, and it is insensitive to the radius when the days just above the commitment keep a large margin, i.e. when the capability distribution is concentrated. $\Phi_\rho(C)$ is the smallest average capability loss (MW) that would push the full-delivery probability below $\rho$; it is the certified reliability margin of the commitment. The proof is given in Appendix B.

#### 4.1.3 Radius selection and cost-optimal commitment

The radius is set to the expected 1-Wasserstein estimation error of the empirical distribution [29],
$$\varepsilon_N=\frac{1}{\sqrt N}\int\sqrt{\hat F_N(\xi)\big(1-\hat F_N(\xi)\big)}\,d\xi, \tag{20}$$
where $\hat F_N$ is the empirical distribution function of the capability. The radius is small for a concentrated capability distribution and large for a dispersed one; a leave-one-out validation on $\Omega^{DA}$ serves as a check (Section 5.6). Among the robustly deliverable commitments, the operator selects the one with the lowest back-tested cost,
$$C^*=\arg\min\big\{\bar J(C)=\tfrac1N\textstyle\sum_dJ_d(C):\ C\in\mathcal G,\ C\le C^{DRO}_\rho(\varepsilon)\big\}. \tag{21}$$
Every strategy can be paired with this procedure, which makes the endogenous-commitment comparison of Section 5.6 fair: all strategies use the same days, the same objective and the same reliability target.

#### 4.1.4 Perfect-recourse benchmark commitment

For comparison, the commitments can also be obtained from a two-stage stochastic MILP with perfect recourse, in which $\mathbf C$ is the first-stage decision and the joint recovery model (2)–(12) of every scenario is the second stage,
$$\min_{\mathbf C}\ -\epsilon^{C}\textstyle\sum_kC_k+\sum_{\omega}p_\omega J_\omega(\mathbf C),\qquad \bar r_{k,\omega}\ge(1-\epsilon_f)C_k-M(1-u_\omega)\ \forall k,\quad \sum_\omega p_\omega u_\omega\ge\rho. \tag{22}$$
Because the recourse of (22) knows each scenario in advance, it measures the physical consecutive capability; in the case study it returns the single-event capabilities (8.18/7.98 MW in S1). Two-stage distributionally robust models solved by column-and-constraint generation [28] share this recourse structure, whereas the closed-loop capability (16) certifies what the controller actually delivers.

### 4.2 Intraday cross-event joint recovery MPC

Every 15 min the controller solves the MILP (2)–(12) over an 18-h horizon with the measured state, forecasts corrected by the latest observed errors and the terminal state references of the day-ahead plan, and applies the first-step decisions (JR-D). Because all confirmed events are visible within the horizon, the controller decides at every step which debt to repay first: it carries long-deadline backlog across events when doing so frees the channel for the storage that the next event needs, and it repays the debts that would otherwise fall due. The scenario variant JR-S replaces the forecast by a scenario tree with non-anticipative first-step decisions, in which an event that is not yet confirmed appears only in the scenarios in which it is called. The plant replay enforces the physical limits in the order storage, cold storage and deferrable computing, so that the grid import never exceeds $P^{cap}$.

**Table 1.** Pseudocode of the recovery-aware commitment and the cross-event joint recovery.

```
Algorithm 1  Recovery-aware commitment and cross-event joint recovery
Input : historical days Ω_DA (N days), operating days Ω, commitment grid G (step Δ_G),
        reliability ρ, event set K, horizon T_H, plant parameters (Table A1)
Output: cost-optimal commitment C*, firm capacity Ĉ_ρ, closed-loop trajectories
Stage I   Day-ahead recovery-aware commitment (Section 4.1)
 1  for C ∈ G in increasing order and every day d ∈ Ω_DA that delivered all smaller C do
 2      run Stage III on day d with commitment C → cost J_d(C), full delivery of every event
 3  capability ξ_d of every day (16); empirical distribution P̂_N; radius ε ← ε_N (20)
 4  for C ∈ G do sort the margins δ_d(C), d ∈ D_C; q(C) ← n(C) − ρN; margin Φ_ρ(C) (18)–(19)
 5  C_DRO ← max{C ∈ G: q(C) ≥ 0, Φ_ρ(C) ≥ ε} (17); C* ← argmin{J̄(C): C ≤ C_DRO} (21)
Stage II  Firm capacity on the operating days (Section 3.6)
 6  for every C ∈ G and ω ∈ Ω do run Stage III with commitment C
 7  Ĉ_ρ ← largest C whose full-delivery share ≥ ρ for all C' ≤ C (14); bootstrap CIs over days
Stage III Intraday cross-event joint recovery MPC (Section 4.2), every Δt = 15 min
 8  measure x_t = (B_{1..3,t}, E_t, S_t), the gas-engine state, the event status and the loads
 9  correct the forecasts with the latest observed errors (JR-S: build the scenario tree)
10  solve the joint recovery MILP (2)–(12) over t, …, t+T_H with all confirmed events
11  apply the first-step decisions; replay the plant (storage → TES → compute throttling)
12  update the backlogs by earliest-deadline-first execution and the settlement (11)
13  return C*, Ĉ_ρ and the trajectories
```

### 4.3 Benchmarks and controlled scenario matrix

All strategies face the same commitments, service deadlines, physical limits and settlement rules. Table 2 lists the controlled scenario matrix, which isolates the contribution of each resource, each device and each layer of coordination.

- **IR-O\*** — independent recovery with an optimised static split. The IT scheduler plans its own share $\alpha C_k$ of every event and its catch-up with priority on the connection headroom; the facility energy-management system then optimises storage and IES with the IT schedule fixed. The split $\alpha$ is tuned day-ahead on the historical scenarios over $\alpha\in[0.2,1.0]$ for every commitment level.
- **IR-P** — price-coordinated independent recovery. Instead of a fixed share, the IT scheduler receives the channel shadow price of the day-ahead joint plan on top of the TOU price (a one-way, day-ahead price signal).
- **JR-M** — event-by-event joint recovery. The joint model is used, but only the current or next event is visible, which represents single-event DR scheduling and isolates the value of cross-event foresight.
- **JR-oracle** — joint recovery with perfect information (reference).

**Table 2.** Controlled scenario matrix (✓ included, × excluded, – not applicable). The resource and device configurations are operated by the JR-D controller with the connection limit of the base case.

| Configuration | Compute flexibility | BESS | Cold storage | Gas engine | Absorption chiller | Joint recovery | Cross-event foresight |
|---|---|---|---|---|---|---|---|
| R1 BESS only | × | ✓ | × | ✓ | ✓ | – | ✓ |
| R2 Compute only | ✓ | × | × | ✓ | ✓ | – | ✓ |
| R3 Compute + BESS | ✓ | ✓ | × | ✓ | ✓ | ✓ | ✓ |
| D1 w/o gas engine | ✓ | ✓ | ✓ | × | × (no heat) | ✓ | ✓ |
| D2 w/o absorption chiller | ✓ | ✓ | ✓ | ✓ | × | ✓ | ✓ |
| D3 w/o cold storage | ✓ | ✓ | × | ✓ | ✓ | ✓ | ✓ |
| D4 w/o all three | ✓ | ✓ | × | × | × | ✓ | ✓ |
| IR-O\* / IR-P | ✓ | ✓ | ✓ | ✓ | ✓ | × | ✓ |
| JR-M | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | × |
| JR-D (proposed) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### 4.4 Implementation

The models are implemented in MATLAB/GNU Octave and solved with GLPK (Gurobi and `intlinprog` are supported). The intraday MILP has about $10^4$ variables and one binary per event; the MILP solves of a closed-loop day take about 5 s for JR-D and about 60 s for JR-S on one CPU core.

## 5. Case studies

### 5.1 Case description

The AIDC of Section 2.1 operates under the Jiangsu two-part TOU tariff and DR rules; its parameters are listed in Table A1. All load and weather profiles are derived from public data: the deferrable training and batch work from the Alibaba PAI GPU cluster trace [30], split by task runtime into the classes C1–C3; the online inference load from the Azure LLM inference trace 2024 [31]; and the PV output and chiller COP from ERA5 reanalysis weather of Suzhou in the summer of 2024. The DR day is a hot weekday (5 August 2024, maximum temperature 38.3 °C). The DR baseline is the average of the five preceding workdays [6,32], and the connection limit is $P^{cap}$ = 16.03 MW, 1.10 times the typical-day peak of 14.57 MW. Without DR the AIDC imports up to this limit when the BESS recharges in the valley hours (mean daily peak 15.82 MW over the operating days), whereas during the evening events the baseline is 9.4–9.8 MW. The recovery channel (1) is therefore about 6.4 MW wide: it repays both debts of a 7-MW event within a 3-h interval but only part of them within 30 min. The forecasts use the mean of the preceding weekdays for computing, of the available inference days for inference, and of the preceding three days for PV and temperature. The historical days $\Omega^{DA}$ are the 14 weekdays of the trace before the DR day; the deterministic forecasts and the IR-O\* split are tuned on five of them, selected at the 10–90 % quantiles of the daily deferrable load.

The operating-day set $\Omega$ (scenario S4) contains 26 days, each combining a different PAI weekday after the DR day with a hot summer day and an Azure inference day. On 16 of the 26 days the load without DR deviates from the baseline by more than 1 MW during at least one event, on 14 of them upwards (range −1.45 to +3.30 MW), so the commitments must be delivered under realistic baseline errors. Every strategy is simulated in closed loop on every day, and all statistics are reported with 95 % block-bootstrap confidence intervals over days.

Table 3 lists the event scenarios. The commitment is uniform across events ($C_k=C$), which corresponds to the standard DR product; non-uniform commitments are examined through the reliability region in Section 5.3. All strategies of Section 4.3 use the same MPC settings (15-min step, 18-h horizon), the same commitments and the same settlement rules (Table 2). The static split of IR-O\* is re-tuned on $\Omega^{DA}$ for every commitment level ($\alpha^*$ between 0.2 and 0.9), so that the benchmark always operates in its best day-ahead configuration.

**Table 3.** Event scenarios.

| Scenario | Events (h) | Notice | Price coefficient | Purpose |
|---|---|---|---|---|
| S1 | 17–18, 19–20 | day-ahead | 1.0 | base case (Jiangsu: ≤ 2 agreed events, ≤ 2 h per day) |
| S2 | 17–18, 18.5–19.5 | day-ahead | 1.0 | short interval τ = 30 min (15 min–3 h in Section 5.4) |
| S3 | 17–18, 19–20, 21–22 | day-ahead, day-ahead, 3 h | 1.0, 1.0, 1.4 | high stress: additional rapid peak-shaving call |
| S4 | S1–S3 on the 26 operating days | as S1–S3 | as S1–S3 | statistics and economics |
| S4-U | 17–18, 19–20, 21–22; third event called with probability 0.6 | day-ahead, day-ahead, 1 h | 1.0, 1.0, 1.6 | event-call uncertainty |

### 5.2 Recovery mechanism on a typical day

Figs. 3, 4 and 5 trace the two events of S2 on a representative operating day with a uniform commitment of 7 MW, and contrast them with the same events 3 h apart. With the 30-min interval, JR-D delivers 8.18 MW in the first and 8.02 MW in the second event, IR-O\* delivers 7.00 MW and 6.84 MW and misses full delivery in the second event, and JR-M collapses to 4.64 MW in the second event (Fig. 3a–b). With the 3-h interval all three strategies deliver both events in full (Fig. 4). On this day the shortfall of IR-O\* is small (2 % of the commitment); on another operating day it reaches 17 %, and there too the 3-h interval restores full delivery. The difference therefore arises entirely from how the debts of the first event are incurred and repaid.

**Which debt to incur.** JR-D defers the long-deadline class C3 during the first event: at its end, 3.0×10³ GPU·h of C3 work are deferred, against 2.0×10³ GPU·h under IR-O\* (Fig. 4a). Because C3 does not fall due before the end of the second event, this debt can be carried across it, which is the mechanism of Proposition 2: the necessary catch-up $c^*$ is limited to the work that would fall due in the next event.

**How to use the channel.** In the 30-min interval the grid import of all strategies reaches the connection limit. IR-O\* spends the channel on catch-up and recharges the BESS by only 0.16 MWh, whereas JR-D recharges it by 0.73 MWh and starts the second event with 6.22 MWh instead of 5.91 MWh (Fig. 3c–d). Measured against the no-DR operation, in which the BESS discharges to shave the evening peak, JR-D devotes 57 % of the recovery energy drawn in the interval to the BESS instead of 32 % (Fig. 5). JR-M, which plans each event alone, over-delivers the first event to collect the 120 % payment and empties the BESS to 1.27 MWh; the backlog it leaves cannot be deferred again and the second event fails.

**Who provides the channel.** The gas engine and the absorption chiller provide 85 % of the energy that recovery draws through the channel (Fig. 5). The gas engine runs at full output with and without DR, so it adds no energy during recovery but lowers the import by 3 MW and thereby widens the headroom $P^{cap}-P^{base}$; Section 5.7 quantifies these roles.

These results confirm that the deliverable reduction of the second event is decided by the recovery state that the first event leaves behind, and that joint recovery shapes this state through both the choice of deferred work and the allocation of the channel.

### 5.3 Firm consecutive DR capacity

Fig. 6 shows the share of the 26 operating days on which every event is delivered in full, as a function of the uniform commitment, and Table 4 lists the firm capacities. JR-D firmly delivers 7.5 MW in S1 and in S2 (95 % CI 7.5–8 MW), 94 % of the single-event capability of the second event (7.98 MW). Above this level its share drops to 81 % at 8 MW and to zero at 8.5 MW, where the commitment exceeds what the AIDC can reduce below the baseline at the minimum import of 1.5 MW; this limit is physical, not a recovery limit. JR-M firmly delivers 6.5 MW in S1 but only 4.5 MW in S2, so cross-event foresight adds 1.0 MW (95 % CI 0.5–1.5) with the 1-h interval and 3.0 MW (2.5–3.0) with the 30-min interval. The third, rapid event of S3 makes the evening more demanding: JR-D firmly delivers 6.5 MW per event (4.5–7.0) and JR-M 4.5 MW (1.5–5.0), so foresight adds 2.0 MW (2.0–3.0), while the independent benchmarks deliver all three events in full on at most 77 % of the days at any commitment.

**Table 4.** Firm consecutive DR capacity $C^{firm}_{0.95}$ (MW) on the 26 operating days, with 95 % block-bootstrap confidence intervals; "< 1" means that full delivery on 95 % of the days is not reached even at 1 MW.

| Scenario | IR-O\* | IR-P | JR-M | JR-D | Foresight gain JR-D − JR-M |
|---|---|---|---|---|---|
| S1 | < 1 | < 1 | 6.5 [6.0, 7.0] | 7.5 [7.5, 8.0] | +1.0 [+0.5, +1.5] |
| S2 | < 1 | < 1 | 4.5 [4.5, 5.0] | 7.5 [7.5, 8.0] | +3.0 [+2.5, +3.0] |
| S3 | < 1 | < 1 | 4.5 [1.5, 5.0] | 6.5 [4.5, 7.0] | +2.0 [+2.0, +3.0] |

The independent benchmarks do not reach 95 % at any commitment, not even at 1 MW, where IR-O\* and IR-P deliver in full on 69 % of the days in S1 and 73 % in S2. Their failures concentrate on the days on which the load without DR exceeds the baseline, by more than 1 MW on 14 of the 26 days and by up to 3.3 MW (Section 5.1); a reduction measured against the baseline then requires a correspondingly larger true reduction. The IT scheduler of independent recovery defers only its planned share of the commitment, so the whole deviation falls on the storage, which must also serve the second event. On the day with the largest deviation, IR-O\* defers 4.9×10³ GPU·h at 3 MW in S2, less than on an average day, and delivers 1.26 MW and 2.35 MW instead of 3 MW; JR-D defers 9.5×10³ GPU·h, 2.8 times its average, and delivers both events in full. In S1 the facility controller of IR-O\* also charges the BESS only for its own share (7.6 MWh on average at the start of the first event at 3 MW, against 11.3 MWh under JR-D). The firm capacity of independent recovery is therefore limited by baseline uncertainty long before the recovery channel binds, and Section 5.8 shows that no static split, not even the best one in hindsight, removes this limit. Under the 80 % settlement rule the ordering is the same: on at least 95 % of the days JR-D is valid up to 9 MW, the top of the grid, in S1 and S2 and up to 7.5 MW in S3, JR-M up to 8.5, 5.5 and 5.0 MW, and the independent benchmarks not even at 1 MW. Even the payment validity of independent recovery cannot be guaranteed.

Fig. 7 extends the uniform commitment to the two-event region of S2: for a fixed first-event commitment $C_1$, it shows the largest second-event commitment that is delivered in full in both events on at least 95 % of the days. The boundary of JR-D is almost flat: JR-D firmly delivers 8.0 MW in the second event after a first event of 2 or 4 MW and still 7.75 MW after 6–8 MW, so a large first event costs the second one almost nothing. The boundary of JR-M falls from 5.5 MW at $C_1$ = 2 MW to 3.75 MW at $C_1$ = 8 MW. Even a small first event limits JR-M, because an event-by-event plan prepares the storage only for the event at hand: with $C_1$ = 2 MW and $C_2$ = 6 MW (five sampled operating days), JR-M starts the first event with 4.4–5.9 MWh in the BESS, against 11.4 MWh under JR-D, and the second event with 4.1 MWh and up to 2.4×10³ GPU·h of backlog, whereas JR-D starts it with 7.4–7.7 MWh and no backlog. The independent benchmarks have no firm pair at all, since they are not firm even at (1, 1) MW. With perfect information on the DR day (dashed in Fig. 7, supplementary Fig. S1), the second event can deliver 8.1 MW, expressed as a commitment delivered in full, whatever the first commitment, and this physical capability is the same for joint, event-by-event and independent recovery with the best static split. Physical capability therefore does not distinguish the controllers; firm capacity does. JR-D comes within 0.1–0.3 MW of the physical boundary, whereas JR-M stays 2.6–4.3 MW below it: the gap is created by operating in closed loop under forecast and baseline errors, which is exactly what a perfect-recourse assessment leaves out.

### 5.4 Capacity-gain decomposition and multidimensional sensitivity analysis

Fig. 8 decomposes the firm capacity over the event interval τ, from 15 min to 3 h (two one-hour events, base system, bisection on the 26 operating days). JR-D firmly delivers 7.50–8.00 MW at every interval: with cross-event foresight the firm capacity hardly depends on how soon the next event follows. Without foresight it does. The firm capacity of JR-M rises from 3.50 MW at 15 min to 4.75 MW at 30 min, 6.75 MW at 1 h and 7.75 MW at 2 h and 3 h, so the foresight value, the gain of JR-D over JR-M, is 4.0, 3.0, 1.0, 0.25 and 0 MW. It vanishes once the interval is long enough to repay both debts, the condition of Proposition 2. IR-O\* stays below 1 MW at every interval, so the coordination value, the gain of JR-M over IR-O\*, is at least 2.5 MW at 15 min and grows to at least 6.75 MW at 2 h and 3 h. Coordination is therefore valuable at every interval, because it lets one controller re-plan all resources on the measured state, while foresight adds its value precisely where coordination alone falls short, at short intervals.

At a fixed commitment of 7 MW, the interval–margin map (Fig. 9a–c) confirms the conditions of Proposition 2. JR-D delivers in full on 96–100 % of the days in all 20 combinations of τ and γ. JR-M delivers in full on 0–31 % of the days when the interval is 15 or 30 min and on 88–100 % from 1 h on, whatever the connection margin, so the foresight gain is 69–100 percentage points for τ ≤ 0.5 h, 0–12 points at 1 h and 0–4 points for τ ≥ 2 h (Fig. 9c). A wider connection does not rescue JR-M at short intervals: JR-M enters the interval with the battery that it emptied in the first event, and within 30 min the battery can take back at most 3 MWh at its 6-MW rating, whatever the connection (Section 5.5). Once the interval is long enough to repay both debts, the order of repayment no longer matters, and joint recovery loses its edge, exactly as Proposition 2 predicts. The gain of JR-D over the best independent benchmark (12–54 points, Fig. 9b) shows no trend in τ, consistent with independent recovery failing on baseline deviations rather than on the channel.

The lag bounds of the deferrable work decide how much debt can be carried (Fig. 9d; S1, 7 MW, connection kept). With all lag bounds scaled by 0.5, 0.75, 1, 1.25 and 1.5, JR-D delivers both events in full on 96–100 % of the days, whereas JR-M does so on 19, 46, 92, 100 and 100 %. Shorter deadlines shrink the debt that may be carried, $\min\{X,p_f(L-D_B)\}$ in Proposition 2, so event-by-event recovery runs out of room, while cross-event foresight still finds a feasible order of repayment; longer deadlines let even an event-by-event plan wait. Independent recovery is unaffected (85 % for IR-O\*, 12 % for IR-P at every scale), consistent with its failures stemming from baseline deviations rather than from deadlines.

### 5.5 Equivalent battery and connection capacity

Fig. 10 translates the capacity gain into the battery energy and the connection capacity that it substitutes. The firm capacities are found by bisection on the 26 operating days of S2 (resolution 0.25 MW). With the connection limit kept at its base value, the firm capacity of JR-D rises from 3.75 MW without a BESS to 6.00 MW with 6 MWh and 7.75 MW with the base 12 MWh (Fig. 10a). JR-M gains much less from the same battery (3.75, 4.50 and 4.75 MW) and never exceeds 5.25 MW, and IR-O\* stays below 1 MW at every size: a battery reserved for a fixed share of the reduction cannot absorb the baseline deviations that make independent recovery fail. Cross-event foresight therefore substitutes battery energy. JR-D needs 2.7 MWh to firmly deliver the 4.75 MW that JR-M reaches with 12 MWh, a saving of 9.3 MWh, or about 5.6 million CNY at a system cost of 0.6 CNY/Wh, and no battery size lets JR-M reach the firm capacity of JR-D. Beyond 12 MWh the firm capacity of JR-D declines (7.50 MW at 18 MWh and 6.75 MW at 24 MWh). This decline stems from the baseline rule, not from recovery: a larger battery shaves the evening peak in normal operation, which lowers the five-day baseline and with it the reduction that can be shown against it.

The connection margin matters much less (Fig. 10b). Raising the connection limit from 14.57 MW ($\gamma$ = 1.00) to 18.94 MW ($\gamma$ = 1.30) adds only 0.5 MW to the firm capacity of JR-D (7.50 → 8.00 MW) and of JR-M (4.50 → 5.00 MW), and IR-O\* stays below 1 MW. Event-by-event recovery cannot buy its way out with connection capacity: with 4.4 MW more connection than JR-D at $\gamma$ = 1.00, JR-M still firmly delivers 2.5 MW less. Conversely, JR-D firmly delivers what JR-M delivers at the base connection already at the smallest margin tested, i.e. with at least 1.46 MW less connection (Fig. 10c). At a 30-min interval the binding limit is the recharge rate of the battery (6 MW, at most 3 MWh within the interval), not the width of the channel: JR-M empties the battery in the first event and cannot restore it whatever the connection, whereas JR-D keeps the energy that the second event needs.

### 5.6 Distributionally robust day-ahead commitment

**Capabilities.** Fig. 11a and d show the closed-loop capability $\xi_d$ (16) of every controller on the 14 historical days and on the 26 operating days. In S1, independent recovery has a dispersed, bimodal capability: IR-O\* fails already at 1 MW on 4 of the 14 historical days and reaches 7.75–8.25 MW on the others, and the same pattern recurs on the operating days (8 of 26 below 1 MW). The capability of JR-M lies at 7.75–8.25 MW on the historical days and spreads down to 6.25 MW on the operating days. JR-D reaches 8.25 MW, the midpoint between the last delivered and the first failed commitment at its physical limit, on every historical day and on 21 of the 26 operating days.

**Robust capacity.** With $\rho$ = 0.95 and $N$ = 14, the sample-average capacity is the smallest historical capability rounded down to the grid (Table 5). The robust capacity (17) lowers it by the certified margin (19): because a 5 % share of the days may lose its whole margin, every 0.025 MW of radius costs 0.5 MW of commitment when all days lie above it (Fig. 11b, e). In S1 the radius (20) is 0.91 MW for IR-O\*, 0.066 MW for JR-M and zero for JR-D, whose capability does not vary. For JR-M it lowers the commitment from 7.5 to 6.0 MW and corrects the over-confidence of the sample average: out of sample, 7.5 MW is delivered in full on 77 % of the days and 6.0 MW on all of them, and the worst-case probabilities within the ball, 0.74, 0.91 and 0.95 at 7.5, 7.0 and 6.5 MW, match the realised shares of 0.77, 0.92 and 0.96 (Fig. 11c). For IR-O\* the radius even exceeds the actual distance between the historical and the operating capabilities ($W_1$ = 0.81 MW), and no commitment of 1 MW or more is robust. For JR-D the robust capacity equals the sample-average 8.0 MW, its physical limit, which is delivered in full on 81 % of the operating days. The operating days are more loaded than the historical ones: during the first event the load without DR exceeds the baseline by 0.78 MW on average, against −0.16 MW on the historical days, and the five days on which JR-D misses 8 MW, each time in the second event, all have the load above the baseline in both events (by 0.9–1.9 MW in the first and 0.8–2.8 MW in the second). The cost-optimal commitment absorbs this systematic shift with the margin that it keeps below the capability limit (see Commitment below).

In S2 the capability of JR-D varies slightly (one historical day at 7.75 MW, the others at 8.25 MW). The radius is 0.034 MW and the robust capacity of 7.0 MW is delivered in full on every operating day; at 8 MW the robust probability of full delivery, 0.79, matches the realised share of 0.81, where the sample average predicts 0.93 (Fig. 11f). The capability of JR-M is dispersed between 5.25 and 7.75 MW; its radius of 0.25 MW leaves no robust commitment of 1 MW or more, whereas the sample average commits 5.0 MW and delivers it in full on only 92 % of the days. The price of robustness thus scales with the dispersion of the capability: it is negligible for the concentrated capability of JR-D and prohibitive for the dispersed capability of JR-M, which is a second reason, besides the larger capability itself, why cross-event joint recovery can commit more.

**Commitment.** The commitment (21) minimises the back-tested cost below the robust capacity. It selects 7 MW for JR-D in both scenarios and 6 MW for JR-M in S1, which are delivered in full on all 26 operating days, with benefits of 44.8 (S1) and 43.1 k CNY/day (S2) for JR-D and 35.8 k CNY/day for JR-M (Table 5). For JR-D the cost minimum lies below the capability limit, because the payment is capped at 120 % of the commitment while the delay cost keeps growing with it; in S1 the certified margin at 7 MW is 0.063 MW, five times the margin at 8.0 MW. Independent recovery receives no robust commitment in either scenario, which is the right decision: at 1 MW it delivers in full on only 69–73 % of the operating days. Commitments derived from physical capability are not deliverable. The perfect-recourse model (22) commits the single-event capabilities of 8.18/7.98 MW in S1, which JR-D delivers in full on 85 % of the days; operated by independent recovery, as in conventional single-event practice, the share falls to 27 % (IR-O\*) and 0 % (IR-P); supplementary Fig. S2 places all commitment methods in the plane of out-of-sample reliability and benefit.

**Table 5.** Day-ahead commitment from the 14 historical days and its out-of-sample performance on the 26 operating days ($\rho$ = 0.95). $\varepsilon$: radius (MW); $\Phi$: certified reliability margin (19) at the commitment (MW).

| Scenario | Commitment method | Operated by | Commitment (MW) | $\varepsilon$ | $\Phi$ | Days with full delivery (%) | Benefit vs no DR (k CNY/day) |
|---|---|---|---|---|---|---|---|
| S1 | Perfect-recourse MILP (22) | JR-D | 8.18 / 7.98 | – | – | 85 | 44.7 |
| | Single-event capability | IR-O\* / IR-P | 8.18 / 7.98 | – | – | 27 / 0 | 37.2 / 1.8 |
| | Sample average | IR-O\*, IR-P | none ≥ 1 | 0 | – | – | – |
| | | JR-M | 7.5 | 0 | 0.013 | 77 | 36.9 |
| | | JR-D | 8.0 | 0 | 0.013 | 81 | 44.6 |
| | Robust (17) | IR-O\*, IR-P | none ≥ 1 | 0.91 / 0.90 | – | – | – |
| | | JR-M | 6.0 | 0.066 | 0.088 | 100 | 35.8 |
| | | JR-D | 8.0 | 0 | 0.013 | 81 | 44.6 |
| | Cost-optimal (21) | JR-M | 6.0 | 0.066 | 0.088 | 100 | 35.8 |
| | | **JR-D** | **7.0** | **0** | **0.063** | **100** | **44.8** |
| S2 | Sample average | IR-O\*, IR-P | none ≥ 1 | 0 | – | – | – |
| | | JR-M | 5.0 | 0 | 0.013 | 92 | 29.3 |
| | | JR-D | 7.5 | 0 | 0.013 | 100 | 43.1 |
| | Robust (17) | IR-O\*, IR-P | none ≥ 1 | 0.73 / 0.83 | – | – | – |
| | | JR-M | none ≥ 1 | 0.25 | – | – | – |
| | | JR-D | 7.0 | 0.034 | 0.038 | 100 | 43.1 |
| | Cost-optimal (21) | **JR-D** | **7.0** | **0.034** | **0.038** | **100** | **43.1** |

### 5.7 Role of the integrated energy system

The integrated energy system provides the recovery channel. In the two recovery windows of the typical day, the 30-min interval and the two hours after the second event, the no-DR import lies on average 4.8 and 5.3 MW below the connection limit (Fig. 12b). The gas engine, which runs at full output from 14:00 to 22:00 with and without DR, accounts for 3.0 MW of this channel, the absorption chiller, which moves part of the cooling load off the electric chillers, for 0.5 MW, and the cold storage for 0.2 MW; the BESS adds 1.2 MW by shaving the evening peak in normal operation, but under DR it serves the events instead. A grid-only AIDC with the same connection would have almost no channel left (on average −0.3 and +0.4 MW in the two windows). Of the energy that recovery draws through the channel, the gas engine and the absorption chiller provide 85 % (Fig. 5). The cold storage is pre-charged before the events, covers part of the cooling load during both events and is recharged at night, so its own debt never enters the channel.

Fig. 12a quantifies these roles as firm capacities of JR-D in S2 with the connection limit of the base case. Without the gas engine, and therefore without heat for the absorption chiller, the evening baseline rises by 3.5 MW. This would allow a deeper reduction, but the channel narrows by the same amount and binds first: the firm capacity falls from 7.75 to 5.75 MW. Without the cold storage it falls to 7.50 MW. Without the absorption chiller alone it rises slightly, to 8.00 MW, because the 0.5 MW higher baseline allows a deeper reduction while the channel remains wide enough. Without all three devices the firm capacity is 4.75 MW, 3.0 MW below the full system and as much as cross-event foresight adds at this interval. The resource ablation shows that computing flexibility and storage are complements rather than substitutes. With the BESS alone (no computing flexibility, no cold storage), no commitment of 1 MW or more is firm; with computing flexibility alone the firm capacity is 3.00 MW; with both, still without the cold storage, it is 7.50 MW, nearly twice what the two resources achieve separately (less than 4 MW together). Joint recovery is what turns the two resources into firm capacity: the battery covers the events while the deferred work waits, and the deferred work frees the channel to recharge the battery.

### 5.8 Service quality, economics and robustness

**Service quality.** No strategy leaves work overdue: the deadline constraints (3) and earliest-deadline-first execution keep every deferred task within its lag bound on all days and at all commitments. What DR costs the computing users is the extra completion time of the deferred work (Fig. 13). At every commitment JR-D defers work for less time than the other controllers that deliver: at 7 MW the mean extra completion time is 0.68 h in S1 and 0.90 h in S2, against 0.85 h and 1.12 h for IR-O\* and 1.35 h and 1.26 h for JR-M, and JR-D uses 36 % and 46 % of the SLA slack against 60–75 % for IR-O\* and 60–64 % for JR-M. JR-D defers the long-deadline class, which has slack to spare, whereas IR-O\* catches up its own share at once and JR-M over-delivers the first event and must defer more in the second. IR-P defers least (0.52 h in S1) because it delivers least. The firm operating points of JR-D therefore form the capacity–service front in both scenarios: a larger firm commitment does not come at the expense of the computing users.

**Economics.** Fig. 14 compares the daily costs at 7 MW, a commitment that all strategies can attempt and the cost-optimal commitment of JR-D (Section 5.6). JR-D yields the largest benefit relative to no DR participation, 44.8 k CNY/day in S1 and 43.1 k CNY/day in S2. Its DR revenue of 48.3 k CNY reaches 96 % of the payment cap of the two events and is offset mainly by the delay cost of the deferred work (4.4–6.4 k CNY/day); the electricity and gas costs fall slightly because consumption is shifted out of the evening peak. IR-O\* gains 40.3 and 38.5 k CNY/day with a higher delay cost (5.9–7.6 k CNY/day). JR-M gains 37.3 k CNY/day in S1 but only 19.1 k CNY/day in S2: there the second event finds the AIDC with 4.1×10³ GPU·h of backlog and 3.4 MWh of stored energy (JR-D: 2.2×10³ GPU·h and 6.0 MWh), so its revenue drops to 32.2 k CNY and a shortfall assessment of 4.7 k CNY is levied. IR-P gains 17.8 and 29.8 k CNY/day. On a paired basis JR-D is cheaper than every benchmark on all 26 days in both scenarios; its mean advantage is 4.5 k CNY/day over IR-O\* (95 % CI 2.5–7.6) and 7.6 k CNY/day over JR-M (6.4–8.8) in S1, and 4.6 k CNY/day (2.7–7.4) and 24.1 k CNY/day (19.6–28.5) in S2. The worst-event delivery ratio (Fig. 14c) shows why: the delivery of JR-D is concentrated just above full delivery, whereas the benchmarks spread down to the validity threshold and below it.

**Robustness.** Three checks confirm that the ranking does not depend on the design of the benchmarks or on idealised computing. (i) *Static split in hindsight.* Choosing, for every operating day, the best static split after the fact bounds every independent recovery with a static split from above. At 1 MW this bound delivers in full on 69 % (S1) and 73 % (S2) of the days, exactly as the split tuned day-ahead: on the other days no split covers the baseline deviation, because independent recovery prepares the storage only for its share of a small commitment. The bound rises with the commitment (92 % and 88 % at 5 MW) and covers all days at 7 MW, but the successful split differs from day to day and cannot be chosen in advance; the split tuned day-ahead delivers in full on 85 % and 81 % of the days. Even with hindsight, independent recovery is therefore not firm at any commitment in the sense of (14), which requires full delivery at every smaller commitment as well. (ii) *Pause/resume overhead.* If every deferred GPU·h requires 2 % or 5 % of additional work when it is resumed, an effect the controllers see only through the measured backlog, the firm capacity of JR-D in S2 is 7.75 and 7.50 MW (7.75 MW without overhead), that of JR-M 4.75 MW in both cases, and IR-O\* stays below 1 MW: the foresight gain of 2.75–3.0 MW is unchanged. (iii) *Event-call uncertainty.* When the third event of S3 is called only with probability 0.6 and confirmed 1 h ahead (S4-U, 6 MW per event, called on 15 of the 26 days), JR-D and its scenario-based variant JR-S deliver every called event in full on all days, at a daily cost within 0.9 k CNY of the perfect-information oracle (supplementary Fig. S3). JR-S saves only 0.3 k CNY/day over JR-D, so the deterministic controller with feedback suffices. IR-O\*, JR-M and IR-P deliver in full on 81 %, 69 % and 27 % of the days and cost 10.8–21.5 k CNY/day more.

**Post-event rebound.** Recovery draws power above the baseline after the events. Under the Jiangsu rules alone, the peak rebound after the events of the DR day is 6.4–6.6 MW for every strategy (S1, 6 MW per event). A rebound assessment lets the grid operator trade it off (supplementary Fig. S4): at 3 CNY/kW per event, JR-D cuts the peak rebound to 0.17 MW and still delivers both events in full, by holding deferred work longer (delay cost +17.9 k CNY) and over-delivering less (DR revenue −4.4 k CNY), whereas IR-O\* keeps a rebound of 6.4 MW while its fulfilment falls to 91 %. Joint recovery thus also gives the grid a controllable recovery profile, at a price that the assessment can set.

## 6. Conclusions

AI data centers are increasingly called upon for consecutive DR events, and the capacity that they can firmly commit is decided during recovery. This paper developed a recovery-aware coordinated scheduling framework for consecutive DR of an AI data-center integrated energy system, which comprises a cross-event heterogeneous recovery model, the firm consecutive DR capacity with its distributionally robust commitment and an intraday cross-event joint recovery MPC, and tested it on a 16 000-GPU data center under the Jiangsu rules with 26 operating days built from public computing traces. Through case studies and multidimensional sensitivity analyses, the main conclusions are summarised as follows.

(1) Deliverability is decided during recovery. Computing backlog and storage deficit compete for one recovery channel. Joint recovery carries the long-deadline backlog across the next event and spends the channel on recharging: with a 30-min interval it devotes 57 % of the recovery energy to storage instead of 32 % under independent recovery, and it delivers both 7 MW events in full where independent and event-by-event recovery fall short.

(2) Firm capacity requires joint recovery. Cross-event joint recovery firmly delivers 7.5 MW in the two-event scenarios, 94 % of the physical capability of the second event, and 6.5 MW with a third, rapid event. Independent recovery, with a day-ahead tuned split or with price coordination, is not firm at any commitment down to 1 MW, because baseline deviations of up to 3.3 MW fall on storage that serves a fixed share of the reduction.

(3) Foresight pays off at short intervals, and coordination pays off at every interval. Cross-event foresight adds 4.0 MW at a 15-min, 3.0 MW at a 30-min and 1.0 MW at a 1-h interval (2.0 MW with three events) and vanishes at 2–3 h, as Proposition 2 predicts; joint recovery with foresight keeps its firm capacity at 7.5–8.0 MW at every interval. Coordinating computing and storage in one controller adds at least 2.5–6.75 MW at every interval, because independent recovery is not firm at any of them.

(4) Joint recovery substitutes hardware. With cross-event foresight, 2.7 MWh of battery firmly deliver what event-by-event joint recovery needs 12 MWh for, a saving of 9.3 MWh or about 5.6 million CNY. Neither a larger battery nor 4.4 MW more connection lets event-by-event recovery reach the firm capacity of cross-event recovery: it empties the battery in the first event, and at short intervals the recharge rate, not the connection, limits how much can be restored. No battery size makes independent recovery firm, and batteries beyond 12 MWh erode the baseline and lower the firm capacity.

(5) The commitment must reflect what the controller delivers. A closed-loop back-test on 14 historical days refuses to commit independent recovery, which fails at 1 MW on 2–4 of them, and its Wasserstein-robust version corrects over-confident sample-average commitments (event-by-event recovery in S1: 7.5 → 6.0 MW, full delivery out of sample 77 → 100 %). Robustness is cheap for the concentrated capability of cross-event joint recovery and expensive for dispersed ones. The cost-optimal commitment of cross-event joint recovery, 7 MW, is delivered on every operating day, whereas a perfect-recourse two-stage model commits the single-event capabilities (8.18/7.98 MW), which are delivered in full on only 85 % of the days. The margin that the cost-optimal commitment keeps below the capability limit also absorbs a systematic shift of the operating conditions.

(6) The integrated energy system provides the recovery channel. The gas engine and the absorption chiller supply 85 % of the energy drawn through the recovery channel; without the gas engine the firm capacity falls by 2.0 MW and without all IES devices by 3.0 MW, as much as cross-event foresight adds. Computing flexibility and storage are complements: 3.0 MW and below 1 MW alone, 7.5 MW together.

For DR practice, these results support sizing consecutive-event contracts of AI data centers by the firm capacity of the controller that operates them rather than by physical capability, and they allow grid operators to accept larger firm commitments from data centers that coordinate computing and storage recovery across events. Future work will extend the framework to geographically distributed data centers that shift work between sites, to the thermal inertia of the server halls as a further recovery resource, and to the co-planning of batteries, connection capacity and DR contracts over the life of the data center.

## Appendix A. Case-study parameters and data

**Table A1.** Parameters of the case study ([S] taken from a cited source, [D] derived from public data, [A] modelling assumption).

| Subsystem | Parameter | Value | Source |
|---|---|---|---|
| Computing | GPUs; node peak power | 16 000 H100-class GPUs in 2 000 eight-GPU nodes; 8.4 kW per node | [33] [S] |
| | Idle and dynamic power per GPU $p^{idle}$, $p^{dyn}$ | 0.26 kW (25 % of peak) and 0.79 kW | [34] [A] |
| | Other IT power $P^{oth}$; schedulable fraction $u^{max}$ | 0.6 MW; 0.95 | [A] |
| | Inference dynamic-power factor $\kappa^{inf}$ | 0.65 | [35] [A] |
| | Workload shares | 25 % of GPUs busy with online inference; 40 % with training and batch work, 75 % of it deferrable; profile shapes from [30,31] | [A] |
| | Deferrable classes; lag bounds $L_c$ | C1/C2/C3 by PAI runtime ≤ 1 h, 1–12 h, > 12 h; 0.5/1.5/3 h | [30] [D]; [4] [A] |
| | Delay and lateness prices $c^{jct}$, $c^{late}$ | 0.5 and 1000 CNY per GPU·h·h | [A] |
| Facility and cooling | Losses $\zeta$; auxiliary power $P^{aux}$ | 5 % of the IT power (UPS, distribution, air handling); 0.3 MW | [A] |
| | Heat per unit of IT power $\theta$; base cooling load $Q_0$ | 1.0; 0.3 MW~th~ | [A] |
| | Electric chillers $\mathrm{COP}_t$, $\bar Q^{EC}$ | 6.0 at 25 °C, −0.12 per °C (bounds 3–7); 30 MW~th~ | [A] |
| CCHP | Gas engine $\bar P^{GT}$, $\eta^{GT}$, heat efficiency, $R^{GT}$ | 3 MW; 0.38; 0.45 ($k^h$ = 1.18); 1.5 MW per 15 min | [A] |
| | Absorption chiller $\mathrm{COP}^{AC}$, $\bar Q^{AC}$ | 0.75; 2.7 MW~th~ | [A] |
| | Gas price $c^{gas}$ | 3.6 CNY/Nm³ at 9.89 kWh/Nm³, i.e. 364 CNY/MWh of fuel | [A] |
| Storage | BESS $\bar P^{B}$, capacity, $\underline E$–$\bar E$, $\eta_c$/$\eta_d$, $c^{deg}$ | 6 MW; 12 MWh; SOC 10–95 % (initial 50 %); 0.95/0.95; 60 CNY/MWh | [36] [A] |
| | TES $\underline S$–$\bar S$, $\bar Q^{T}$, $\eta^T_c$/$\eta^T_d$, $\sigma$ | 1–10 MWh~th~ (initial 5); 4 MW~th~; 0.98/0.98; 0.5 %/h | [A] |
| Supply | PV | 8 MWp; PVWatts losses 14 %; −0.37 %/°C; NOCT 45 °C | [37] [S]; [A] |
| | Weather | ERA5 / Open-Meteo, Suzhou-Wujiang, summer 2024; DR day 5 August 2024 (38.3 °C) | [D] |
| | Grid connection $P^{cap}$; minimum import $P^{min}$ | 1.10 × typical-day peak (16.03 MW); 1.5 MW | [A] |
| Market | Tariff | Jiangsu two-part TOU: peak 14–22 h ×1.8 and valley ×0.35 on the purchase price | [38] [S] |
| | DR settlement | 3 CNY/kWh (agreed); ×1.4 (2–4 h notice), ×1.6 (0.5–2 h); valid ≥ 80 %, paid ≤ 120 % | [6] [S] |
| | Shortfall coefficient $\kappa$; planning margin $\delta^{val}$; full delivery; reliability $\rho$ | 1; 0.1 MW; $\bar r_k\ge 0.98C_k$ ($\epsilon_f$ = 2 %); 0.95 | [A] |
| | Terminal values $J^{term}$ | 500 CNY/MWh of BESS and 100 CNY/MWh~th~ of TES deficit; backlog at its energy cost at the flat price | [A] |
| Method | MPC | $\Delta t$ = 15 min, $T_H$ = 18 h; JR-S with 5 scenarios | [A] |
| | Static split of IR-O\* | $\alpha\in\{0.2,0.3,\dots,1.0\}$, tuned day-ahead for every commitment | [A] |
| | Two-stage model (22) | $\epsilon^{C}$ = 100 CNY/MW | [A] |
| | Days | 26 operating days: PAI weekdays after the DR day, each paired with a hot day and an Azure inference day; 14 historical days: the weekdays of the trace before the DR day (five of them, at the 10–90 % quantiles of the deferrable load, for forecasts and benchmark tuning) | [30,31] [D] |

## Appendix B. Proofs

**Notation and assumptions.** Let $\mathcal I=(e_A,s_B)$ be the interval of length $\tau$ between events A and B, and $\mathcal T_B$ the steps of event B with duration $D_B$. (H1) Without DR the grid import equals the baseline and the storage is idle in $\mathcal I\cup\mathcal T_B$. (H2) $\psi_t$ and $\mathrm{COP}_t$ are constant in $\mathcal I\cup\mathcal T_B$; otherwise all bounds below hold with the largest $\psi_t$ of the interval. Under (H1) the deviation of any schedule from the baseline is
$$P^{grid}_t-P^{base}_t=\psi\sum_c\big(y_{c,t}-a_{c,t}\big)+P^{ch}_t-P^{dis}_t+\frac{Q^{TC}_t-Q^{TD}_t}{\mathrm{COP}}-\Delta g_t, \tag{B.1}$$
where the first term is catch-up (positive) or deferral (negative) of computing work and $0\le\Delta g_t\le g$ is the additional gas-engine output including its absorption-chiller equivalent.

**Quantities of Proposition 1.** $X_A=\psi\sum_cB_c(e_A)$ is the computing debt left by A and $X_A^{due}$ its part that falls due before $e_B$; $E_s=\eta_d(E_A-\underline E)+\eta^T_d(S_A-\underline S)/\mathrm{COP}$ and $P_s=\bar P^{B}+\bar Q^{TD}/\mathrm{COP}$ are the dischargeable energy and power of the storage; $H=\sum_{t\in\mathcal I}[\max\{P^{cap}-P^{base}_t,0\}+g]\Delta t$ is the recovery channel; $\bar X_B=\psi\sum_c\bar B_c(e_B)$ is the deadline-limited virtual capacity at the end of B; $p_f=\psi\sum_c\bar a_{c,B}\min(L_c,D_B)/D_B$ is the deferrable power that can still be paused in B; $G^{free}$ is the number of GPUs free for catch-up in the interval; $W^{sw}$ is the work arriving in $\mathcal I$ with a deadline after $e_B$, which earliest-deadline-first execution can swap with due backlog; $\Gamma^0_B$ is the single-event capability. The power bound of Proposition 1 is
$$\Gamma^P=\max_{\substack{H_c+H_s\le H\\H_c\le\psi G^{free}\tau,\ H_s\le\bar P^{B}\tau}}\Big\{p_f-\frac{(X_A^{due}-H_c-W^{sw})^+}{D_B}+\min\Big(P_s,\frac{E_s+\eta H_s}{D_B}\Big)\Big\}+g. \tag{B.2}$$

**Proof of Proposition 1.** (i) Restricting a feasible schedule of the two-event problem to event B gives a feasible schedule of the single-event problem with the same initial state, so $\Gamma_B\le\Gamma^0_B$.

(ii\) Summing (B.1) over $\mathcal T_B$,
$$\Gamma_BD_B=\psi\sum_c\big[B_c(e_B)-B_c(s_B^-)\big]+\sum_{t\in\mathcal T_B}\Big(P^{dis}_t-P^{ch}_t+\frac{Q^{TD}_t-Q^{TC}_t}{\mathrm{COP}}\Big)\Delta t+\sum_{t\in\mathcal T_B}\Delta g_t\Delta t .$$
By the deadline constraint (3) the first term is at most $\bar X_B-X(s_B^-)$, the second is at most the dischargeable energy $E_s(s_B^-)$ at the start of B, and the third is at most $gD_B$. In the interval, let $c_{\mathcal I}$ be the net catch-up energy and $s_{\mathcal I}$ the net energy drawn by the storage. Summing (B.1) over $\mathcal I$ with $P^{grid}_t\le P^{cap}$ gives the channel constraint $c_{\mathcal I}+s_{\mathcal I}\le H$. The states evolve as $X(s_B^-)=X_A-c_{\mathcal I}\ge0$ and $E_s(s_B^-)\le E_s+\phi(s_{\mathcal I})$ with $\phi(x)=\eta x$ for $x\ge0$ and $\phi(x)=x$ for $x<0$, because every MWh drawn for recharging returns only $\eta$ MWh in B. Hence
$$\Gamma_BD_B-gD_B\le\bar X_B-X_A+E_s+\max_{c+s\le H,\ c\le X_A}\{c+\phi(s)\}.$$
Catch-up has the marginal value 1 and recharge the marginal value $\eta<1$, so the maximum is attained by $\hat c=\min(H,X_A)$ and $\hat s=(H-X_A)^+$, whose value is $H^{eff}$. Dividing by $D_B$ gives $\Gamma^E$.

(iii\) The computing reduction in B equals the backlog increase in B. Work arriving in B can be deferred by at most $\min(L_c,D_B)$, which contributes at most $p_fD_B$. The debt $X_A^{due}$ is either caught up in the interval ($H_c$), swapped with later-deadline work (at most $W^{sw}$), or executed in B, where it offsets the reduction one to one. The storage contribution is limited by $P_sD_B$ and by $E_s+\eta H_s$. Maximising over the allocation $H_c+H_s\le H$, subject to the free GPU and charging-power limits, gives (B.2). ∎

The bound is tight when the backlogs reach their deadline limits at the end of B, the storage is empty at the end of B and the channel is fully used in the order catch-up, then recharge. In the mechanism experiment (supplementary Fig. S5) the bound is within 0.05 MW of the optimal deliverable reduction in most cases; it is looser only for intervals below 0.5 h, where the per-step channel width and the charging power cannot be shifted in time as the aggregate $H$ assumes.

**Proof of Proposition 2.** Assume one deferrable class with constant arrival power $p_f$ and lag bound $L\ge D_B$, a debt $X\le p_fL$ at the start of the interval, dischargeable energy $\eta_dE_A$, a constant channel width $h\le\bar P^{B}$ ($H=h\tau$), full pausing of deferrable work in B and no gas engine. With catch-up $c\in[0,X]$ and recharge $s\ge0$ in the interval, $c+s\le H$, the deliverable reduction energy of B is
$$G(c,s)=\min\big(p_fD_B,\ p_fL-(X-c)\big)+\min\big(P_sD_B,\ \eta_dE_A+\eta s\big).$$
Let $c^*=[X-p_f(L-D_B)]^+$ be the necessary catch-up and $s^{req}=[P_sD_B-\eta_dE_A]^+/\eta$ the necessary recharge. The first term of $G$ is concave with slope 1 for $c<c^*$ and slope 0 afterwards; the second is concave with slope $\eta$ for $s<s^{req}$ and 0 afterwards. Maximising the sum of two separable concave functions under $c+s\le H$ allocates the channel greedily by marginal value: catch-up up to $c^*$, then recharge up to $s^{req}$. This is the joint recovery $c_{JR}=\min(H,c^*)$, $s_{JR}=(H-c^*)^+$. Independent recovery repays the whole debt first, $c_{IR}=\min(H,X)$, $s_{IR}=(H-X)^+$, and spends $X-c^*$ of the channel on catch-up of zero marginal value. Substituting both allocations,
$$G_{JR}-G_{IR}=\eta\Big[\min\big(s^{req},(H-c^*)^+\big)-\min\big(s^{req},(H-X)^+\big)\Big]\ge0, \tag{B.3}$$
with the maximum $\eta\min\{X,\,p_f(L-D_B),\,s^{req}\}$. The single-event capability $p_fD_B+P_sD_B$ is restored if and only if $c\ge c^*$ and $s\ge s^{req}$, which requires the channel energy $c^*+s^{req}$ under joint and $X+s^{req}$ under independent recovery. Dividing by $h$ and using $X-c^*=\min\{X,p_f(L-D_B)\}$ gives (15). The difference (B.3) vanishes if and only if $L\le D_B$ or $X=0$ (no debt can be carried), $s^{req}=0$ (B needs no storage), $H\le c^*$ (the channel only suffices for necessary catch-up) or $H\ge X+s^{req}$ (the channel repays both debts). ∎

Two consequences are used in Section 5. First, the minimum recovery energy $\tau^*h$ is fixed, so iso-capability curves are hyperbolas in the plane of the interval and the channel width: a longer interval and a larger connection margin substitute for each other, and joint recovery shifts the curve by the carried debt $\min\{X,p_f(L-D_B)\}$. Second, with several classes the necessary catch-up is $\sum_c[X_c-p_{f,c}(L_c-D_B)]^+$, so the long-deadline class C3 is carried across events first. The closed form is verified against a discrete-time LP on 68 cases ($p_f$ = 5 MW, $D_B$ = 1 h, $X$ = 5 MWh, $h$ = 3 MW, $L\in\{1,1.5,2,3\}$ h, $\tau\in[0,4]$ h); the two agree to within $10^{-5}$ MW, the rounding of the stored results; the interval reductions are 0, 0.83, 1.67 and 1.67 h, as given by (15) (supplementary Fig. S6).

**Proof of Proposition 3.** Write the empirical distribution as $N$ atoms of mass $1/N$ at $\xi_d$. Any $Q\in\mathcal B_\varepsilon(\hat P_N)$ is the image of a transport plan with average displacement at most $\varepsilon$. Moving mass between points on the same side of $C$, or upwards, does not reduce $Q(\xi\ge C)$, so a least favourable plan only moves mass $w_d\in[0,1/N]$ from the atoms of $\mathcal D_C$ to points arbitrarily close below $C$, at the cost $w_d\,\delta_d(C)$. The worst case is therefore the fractional knapsack
$$\sup_{Q\in\mathcal B_\varepsilon(\hat P_N)}Q(\xi<C)=\frac{N-n(C)}N+\max_{w}\Big\{\sum_{d\in\mathcal D_C}w_d:\ \sum_{d\in\mathcal D_C}w_d\,\delta_d(C)\le\varepsilon,\ 0\le w_d\le\frac1N\Big\}. \tag{B.4}$$
With the multiplier $\lambda\ge0$ of the budget constraint and $\upsilon_d\ge0$ of the upper bounds, the LP dual of (B.4) is $\min\{\lambda\varepsilon+\frac1N\sum_d\upsilon_d:\ \upsilon_d\ge1-\lambda\delta_d(C),\ \upsilon_d\ge0\}$. Eliminating $\upsilon_d=\max\{1-\lambda\delta_d(C),0\}$ gives (18); strong duality holds because (B.4) is a feasible and bounded LP. The optimum of (B.4) removes the atoms with the smallest margins first. The worst-case probability $\inf_QQ(\xi\ge C)$ therefore stays at least $\rho$ if and only if removing the mass $q(C)/N$, i.e. the $\lfloor q\rfloor$ atoms with the smallest margins and the fraction $q-\lfloor q\rfloor$ of the next one, costs at least $\varepsilon$, which is (19). For $\varepsilon=0$ the condition reduces to $n(C)\ge\rho N$, the sample-average constraint. $\Phi_\rho(C)$ is non-increasing in $C$, because $n(C)$ and all margins decrease with $C$, so the feasible commitments form a lower set and $C^{DRO}_\rho(\varepsilon)$ is non-increasing in $\varepsilon$. When the atoms just above $C$ have large margins, $\Phi_\rho(C)$ is large and a moderate radius does not change the commitment. ∎

If the radius exceeds the finite-sample concentration radius $\varepsilon_{N,\beta}$ of the 1-Wasserstein distance [26], the true capability distribution lies in $\mathcal B_\varepsilon(\hat P_N)$ with confidence $1-\beta$, and the commitment $C^{DRO}_\rho$ is delivered in full with probability at least $\rho$. For $N=14$ such radii exceed the spread of the capability itself, so the case study uses the expected estimation error (20), which scales with the dispersion of the capability, and validates it by leave-one-out.

**Remark B.1 (single channel price).** For the joint model with fixed binaries, let $\lambda^{el}_t$ be the dual of the electric balance, $\nu_t$ that of the BESS energy equation and $\mu_{c,t}$ that of the backlog equation of class $c$. The KKT conditions give $\lambda^{el}_t=\pi_t+\lambda^{cap}_t+\lambda^{ev}_t$ when the import is interior, $\eta_c\nu_t=\lambda^{el}_t+c^{deg}$ for interior charging and $\mu_{c,t}=\psi_t\lambda^{el}_t$ for interior execution. When catch-up and recharge are both interior, $\mu_{c,t}/\psi_t=\lambda^{el}_t=\eta_c\nu_t-c^{deg}$: one channel price values both debts. Independent recovery schedules catch-up against $\pi_t$ or its own share, ignores $\lambda^{cap}_t$ and breaks this equality; IR-P restores the price part with a day-ahead signal but neither updates it with the realised state nor resolves the non-uniqueness of the IT response at that price (supplementary Fig. S7).

## Figure captions

**Fig. 1.** System and recovery channel. (a) AI data-center integrated energy system: grid connection, PV, gas engine with absorption chiller (CCHP), electric chillers, chilled-water storage (TES), BESS, and the GPU cluster with fixed load and three deferrable classes C1–C3 (lag bounds 0.5, 1.5 and 3 h); the day-ahead commitment and the intraday controller act on the flexible resources. (b) Two consecutive DR events: after the first event, computing catch-up and storage recharge are repaid through one recovery channel between the baseline and the connection limit.

**Fig. 2.** Recovery-aware coordinated scheduling framework. Day-ahead layer: closed-loop back-test of the intraday controller on the historical days, capability per day, Wasserstein-robust capacity (Proposition 3) and cost-optimal commitment (21). Intraday layer: cross-event joint recovery MPC with a 15-min step and an 18-h horizon.

**Fig. 3.** Power balance on the typical day (S2, 30-min interval, 7 MW, operating day r21) under (a) IR-O\* and (b) JR-D: supply (grid import, PV, gas engine, BESS discharge) above zero and demand below zero; events shaded. (c, d) Use of the recovery channel $P^{cap}-P^{base}$ for compute catch-up and storage recharge, with the energies drawn in the interval between the events.

**Fig. 4.** Recovery states on the typical day for the 30-min (a, c) and the 3-h interval (b, d): (a, b) backlog of the deferrable classes under JR-D and total backlog under IR-O\* and JR-M; (c, d) energy in the BESS and the cold storage.

**Fig. 5.** Sources and uses of the recovery energy on the typical day (S2, 7 MW), relative to the no-DR operation of the same day, under (a) IR-O\* and (b) JR-D: grid energy drawn through the channel is attributed to the connection margin, gas engine, absorption chiller, PV and cold storage; uses are catch-up and recharge in the interval and after the events.

**Fig. 6.** Share of the 26 operating days on which every event is delivered in full (a–c) and on which every event is valid under the 80 % rule (d–f) versus the uniform commitment, for S1, S2 and S3; bands: 95 % block-bootstrap intervals; ticks: firm capacities at 95 %; arrows: gain of JR-D over the best independent benchmark, a lower bound because neither independent benchmark is firm at 1 MW.

**Fig. 7.** Two-event firm region in S2 (30-min interval, reliability 95 %): largest second-event commitment delivered in full for a fixed first-event commitment, for JR-D and JR-M (bisection on the 26 operating days), and the physical capability with perfect information on the DR day (dashed), which is the same for joint, event-by-event and independent recovery.

**Fig. 8.** Firm capacity versus the event interval (two one-hour events, base system): (a) firm capacity of IR-O\*, JR-M and JR-D with the coordination and foresight values shaded; (b) decomposition into the coordination value (JR-M − IR-O\*, a lower bound where IR-O\* stays below 1 MW, hatched) and the cross-event foresight value (JR-D − JR-M).

**Fig. 9.** Sensitivity at a commitment of 7 MW: (a) full-delivery share of JR-D over the event interval and the connection margin; (b) gain of JR-D over the best independent benchmark; (c) gain over JR-M (percentage points); (d) full-delivery share versus the scale of the lag bounds (S1).

**Fig. 10.** System-level value of joint recovery in S2 (firm capacity by bisection, resolution 0.25 MW): (a) firm capacity versus BESS energy (2-h rating, connection fixed); (b) versus the connection limit; (c) battery energy and connection capacity saved by cross-event foresight at the firm capacity of JR-M (hatched: lower bound).

**Fig. 11.** Distributionally robust commitment in S1 (a–c) and S2 (d–f): (a, d) closed-loop capability per day on the 14 historical days (filled) and the 26 operating days (hollow); (b, e) robust firm capacity versus the Wasserstein radius, star at the radius $\varepsilon_N$ (20); (c, f) predicted versus realised full-delivery probability for every commitment of the grid, sample average (hollow) and robust (filled).

**Fig. 12.** Role of the integrated energy system (S2, connection limit of the base case): (a) firm capacity of JR-D without the gas engine, the absorption chiller, the cold storage or all three, and for the resource ablation; (b) composition of the evening recovery channel $P^{cap}-P^{grid}_{noDR}$ on the typical day.

**Fig. 13.** Capacity–service trade-off in S1 (a, b) and S2 (c, d): uniform commitment versus the mean extra completion time of deferred work (a, c) and the SLA slack used (b, d); filled markers: firm operating points (full delivery on ≥ 95 % of the days); dashed: front of the firm points.

**Fig. 14.** Economics at a fixed commitment of 7 MW: (a) daily cost components relative to no DR, labelled with the share of days with full delivery; (b) paired daily cost differences between JR-D and each benchmark over the 26 operating days; (c) distribution of the worst-event delivery ratio in S2.

**Fig. S1.** Two-event capability regions with perfect information on the DR day for different event durations and intervals, and for three events (E1 = E2 = $C_1$, E3 maximised), for joint recovery, event-by-event joint recovery, independent recovery with the best static split and the independent post-event state with joint recovery.

**Fig. S2.** Day-ahead commitment methods in the plane of out-of-sample full delivery and daily benefit (Table 5): closed-loop back-test with sample-average, robust and cost-optimal commitments, and commitments from physical capability (perfect-recourse MILP, single-event capability).

**Fig. S3.** Event-call uncertainty (S3 with the third event called with probability 0.6 and confirmed 1 h ahead, 6 MW per event): (a) mean daily cost and (b) mean fulfilment on the days on which the third event is called or cancelled.

**Fig. S4.** Post-event rebound as a policy parameter (S1, 6 MW, DR day): (a) cost under the Jiangsu rules alone versus the peak post-event rebound, (b) peak rebound versus the rebound assessment price.

**Fig. S5.** Proposition 1 on the DR day: deliverable capability of event B relative to its single-event capability versus the interval, for joint response and recovery, independent recovery, the independent post-event state with joint recovery and the bound of Proposition 1, for (a) a 2-h first event and (b) a 2-h second event; (c) capability gain of joint recovery over the interval and the connection margin.

**Fig. S6.** Proposition 2: deliverable reduction of the next event versus the interval in the single-class model, closed form (lines) and discrete-time LP (markers), for lag bounds of 1, 1.5, 2 and 3 h.

**Fig. S7.** Single channel price (Remark B.1): (a) dual of the electric balance (recovery-channel price) and TOU price; (b) duals of the backlog equations of the three classes, which coincide with the channel price when catch-up and recharge are both interior.

## References

[1] IEA. Energy and AI. Paris: International Energy Agency; 2025.
[2] Shehabi A, Smith SJ, Hubbard A, Newkirk A, Lei N, Siddik MAB, et al. 2024 United States Data Center Energy Usage Report. Berkeley: Lawrence Berkeley National Laboratory; 2024.
[3] Norris TH, Profeta T, Patiño-Echeverri D, Cowie-Haskell A. Rethinking load growth: assessing the potential for integration of large flexible loads in US power systems. Durham: Nicholas Institute for Energy, Environment & Sustainability, Duke University; 2025.
[4] Colangelo P, Coskun AK, Megrue J, et al. Turning AI data centers into grid-interactive assets: results from a field demonstration in Phoenix, Arizona. arXiv:2507.00909; 2025.
[5] Google. Demand response agreements with Indiana Michigan Power and the Tennessee Valley Authority targeting machine-learning workloads. Google blog, 4 August 2025.
[6] Jiangsu Provincial Development and Reform Commission. Implementation rules for electricity demand response in Jiangsu Province (effective 14 July 2024). Nanjing; 2024 (in Chinese).
[7] Liu Z, Wierman A, Chen Y, Razon B, Chen N. Data center demand response: avoiding the coincident peak via workload shifting and local generation. Performance Evaluation 2013;70(10):770–791.
[8] Wierman A, Liu Z, Liu I, Mohsenian-Rad H. Opportunities and challenges for data center demand response. In: International Green Computing Conference (IGCC); 2014.
[9] Chen M, Gao C, Song M, et al. Internet data centers participating in demand response: a comprehensive review. Renewable and Sustainable Energy Reviews 2020;117:109466.
[10] Acun F, Hankendi C, Levine E, Reynolds H, Bardwick J, Coskun AK. Investigating power consumption flexibility of AI data centers for demand response participation. In: 17th ACM International Conference on Future and Sustainable Energy Systems (e-Energy); 2026, p. 344–348.
[11] Du B, Fan X, Du E, Chen L, Han J, Hou Q, Zhang N, Kang C. From tokens to energy flexibility: quantization-enabled demand response for data centers with LLM inference workloads. arXiv:2606.18851; 2026.
[12] Chen Y, Zheng X. To defer or to shift? The role of AI data center flexibility on grid interconnection. arXiv:2604.05376; 2026.
[13] Williams C, Colangelo P, Coskun AK, et al. Power-flexible AI data centers: a new paradigm for grid-responsive compute. arXiv:2606.25098; 2026.
[14] Zhou Y, Wei F, Li S, Wang Z, Liu J, Yu D. Data center load modeling through optimal energy consumption characteristics: a path to simultaneously enhance energy efficiency and demand response quality. Applied Energy 2025;393:126095.
[15] Chen C, Ye C, Ding Y, Xiong K, Tang X. Exploring the demand response potential of liquid-cooled data centers. Applied Energy 2026;412:127679.
[16] Han O, Ding T, Yang M, et al. A novel 4-level joint optimal dispatch for demand response of data centers with district autonomy realization. Applied Energy 2024;358:122590.
[17] Lin J, Han J, Wang Y, et al. Planning and operation optimization of a low-carbon data-center computing integrated energy system considering exergy efficiency. Journal of Shanghai Jiao Tong University 2025;59(9):1327–1337 (in Chinese).
[18] Fan H, Chen S, Luo H, et al. Optimal operation of data centers considering multi-energy complementarity of cooling, heating and power and spatio-temporal adjustable loads. Southern Power System Technology 2026;20(5):28–36 (in Chinese).
[19] Zhang S, Ding S, Li Y, Wei M, Tan Q. A bi-level planning model of integrated energy capacity configuration for data center cluster considering computing-electricity coupling operation and supply-demand uncertainties. Applied Energy 2026;425:128499.
[20] Lu X, Qiu J, Lin J, An S, Sun M, Zhao J. Battery-assisted operation of hyperscale AI data centers under connect-and-manage interconnection practices. arXiv:2605.14105; 2026.
[21] Yu Y, Shan K, Li H, Wang S. Quantitative impacts of energy system flexibility provision and design/operation on data center reliability and the key influential parameters. Applied Energy 2026;415:127904.
[22] Hao H, Sanandaji BM, Poolla K, Vincent TL. Aggregate flexibility of thermostatically controlled loads. IEEE Transactions on Power Systems 2015;30(1):189–198.
[23] Evans MP, Tindemans SH, Angeli D. Flexibility framework with recovery guarantees for aggregated energy storage devices. IEEE Transactions on Smart Grid 2022;13(5):3519–3531.
[24] Li M. Beyond scalar flexibility: from eligible AI workloads to dependable load relief. arXiv:2609.05406; 2026.
[25] Schildbach G, Fagiano L, Frei C, Morari M. The scenario approach for stochastic model predictive control with bounds on closed-loop constraint violations. Automatica 2014;50(12):3009–3018.
[26] Mohajerin Esfahani P, Kuhn D. Data-driven distributionally robust optimization using the Wasserstein metric: performance guarantees and tractable reformulations. Mathematical Programming 2018;171:115–166.
[27] Duan C, Fang W, Jiang L, Yao L, Liu J. Distributionally robust chance-constrained approximate AC-OPF with Wasserstein metric. IEEE Transactions on Power Systems 2018;33(5):4924–4936.
[28] Zeng B, Zhao L. Solving two-stage robust optimization problems using a column-and-constraint generation method. Operations Research Letters 2013;41(5):457–461.
[29] del Barrio E, Giné E, Matrán C. Central limit theorems for the Wasserstein distance between the empirical and the true distributions. The Annals of Probability 1999;27(2):1009–1071.
[30] Weng Q, Xiao W, Yu Y, et al. MLaaS in the wild: workload analysis and scheduling in large-scale heterogeneous GPU clusters. In: 19th USENIX Symposium on Networked Systems Design and Implementation (NSDI); 2022.
[31] Stojkovic J, Zhang C, Goiri Í, Torrellas J, Choukse E. DynamoLLM: designing LLM inference clusters for performance and energy efficiency. In: IEEE International Symposium on High-Performance Computer Architecture (HPCA); 2025.
[32] Chao H. Demand response in wholesale electricity markets: the choice of customer baseline. Journal of Regulatory Economics 2011;39(1):68–88.
[33] Latif I, Newkirk AC, Carbone MR, et al. Empirical measurements of AI training power demand on a GPU-accelerated node. arXiv:2412.08602; 2024.
[34] Fan X, Weber W-D, Barroso LA. Power provisioning for a warehouse-sized computer. In: 34th International Symposium on Computer Architecture (ISCA); 2007.
[35] Patel P, Choukse E, Zhang C, et al. Characterizing power management opportunities for LLMs in the cloud. In: ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS); 2024, p. 207–222.
[36] Xu B, Zhao J, Zheng T, Litvinov E, Kirschen DS. Factoring the cycle aging cost of batteries participating in electricity markets. IEEE Transactions on Power Systems 2018;33(2):2248–2259.
[37] Dobos AP. PVWatts version 5 manual. NREL/TP-6A20-62641. Golden: National Renewable Energy Laboratory; 2014.
[38] General Office of the National Development and Reform Commission. Notice on improving the implementation of the capacity charge for two-part tariff users (Fagai Ban Jiage [2016] No. 1583). Beijing; 2016 (in Chinese).
