function M = evaluate_run(L, ev, base, par, inp, refL, settle)
%EVALUATE_RUN  Settlement (Jiangsu rules) and performance indicators of a simulated day.
%   L    : log of the run;  ev : events (only ev(k).called events are settled)
%   refL : log of the no-DR operation on the same realised data (optional). It gives the
%          "true" reduction, the pre-event load-up and the window-independent payback metrics.
%   settle: false for a run without any DR commitment (the no-DR reference): no DR payment, no
%          shortfall / rebound / load-up assessment; the event windows are still used to report the
%          physical indicators (reduction w.r.t. the baseline, rebound, payback). Default true.
%   Indicators added in the revision (review issue 3):
%     true_red      reduction w.r.t. the same day without DR (not w.r.t. the 5-day baseline)
%     preload_*     load-up in the pre_win_h hours before the first called event
%     rebound6      max(pg - baseline) in the payback_h hours after each event (window independent)
%     payback_*     energy drawn above the no-DR operation in the gaps / after the last event
%     ramp_up_max   largest 15-min increase of grid import;  peak_evening: max import 14-24 h
%     term_adj      value of the end state w.r.t. no-DR (leftover backlog at its energy cost,
%                   storage deficit at the valley price), added to the "_adj" costs
%     co2           grid electricity (East China factor) + natural gas burnt (t CO2)
%     cost_delay    service cost of deferred work c_jct * backlog-hours (+ lateness), part of net_cost
%   Indicators added for the reliable-capacity study:
%     full / all_full  event delivered in full: avg reduction >= par.dr.full_lo (98 %) of the commitment
%     delay_GPUh_h     time integral of the deferrable backlog (GPU-h * h), absolute
%     deferred_GPUh    work executed later than it arrived (sum over steps and classes of (arrival - executed)^+)
%     mean_delay_h     additional backlog-hours w.r.t. no-DR per deferred GPU-h (mean extra completion time)
%     sla_use          additional backlog-hours divided by the class lag L_c, per deferred GPU-h
%                      (work-weighted share of the SLA slack that the DR operation used)
%     c3_peak / c3_carry  largest C3 (long training) backlog between the first and the last event, and
%                      the largest C3 backlog carried into a later event (at its start)
dt = par.dt; d = sys_derived(par); T = numel(L.pg);
K = numel(ev);
if nargin < 6, refL = []; end
if nargin < 7 || isempty(settle), settle = true; end
M.settled = settle;
called = true(K, 1);
if isfield(ev, 'called'), for k = 1:K, called(k) = logical(ev(k).called); end, end
M.called = called;
M.avg_red = nan(K,1); M.true_red = nan(K,1); M.valid = false(K,1); M.full = false(K,1); M.pay = zeros(K,1); M.fulfil = nan(K,1);
M.short = zeros(K,1); M.rebound = zeros(K,1); M.rebound6 = zeros(K,1); M.E_start = nan(K,1); M.B_start = nan(K,3);
for k = 1:K
    s = ev(k).s; e = ev(k).e;
    if s > 1, M.E_start(k) = L.E(s-1); M.B_start(k,:) = L.backlog(s-1,:); else, M.E_start(k) = par.bess.E0; M.B_start(k,:) = 0; end
    if ~called(k), continue; end
    Dh = (e - s + 1) * dt;
    red = base(s:e) - L.pg(s:e);
    M.avg_red(k) = mean(red);
    if ~isempty(refL), M.true_red(k) = mean(refL.pg(s:e) - L.pg(s:e)); end
    M.valid(k) = settle && M.avg_red(k) >= par.dr.valid_lo * ev(k).C - 1e-6 && max(L.pg(s:e)) <= max(base(s:e)) + 1e-6;
    M.full(k) = settle && M.avg_red(k) >= par.dr.full_lo * ev(k).C - 1e-6;
    M.pay(k) = M.valid(k) * ev(k).price * min(M.avg_red(k), par.dr.pay_hi * ev(k).C) * Dh;
    M.fulfil(k) = min(max(M.avg_red(k), 0) / ev(k).C, 1);
    M.short(k) = settle * max(ev(k).C - M.avg_red(k), 0);
    if ~isempty(ev(k).win), M.rebound(k) = max(0, max(L.pg(ev(k).win) - base(ev(k).win))); end
    % window-independent rebound: payback_h after the event, until the next called event starts
    nxt = find(called & [ev.s]' > e, 1);
    w2 = min(T, e + round(par.dr.payback_h / dt));
    if ~isempty(nxt), w2 = min(w2, ev(nxt).s - 1); end
    if w2 > e, M.rebound6(k) = max(0, max(L.pg(e+1:w2) - base(e+1:w2))); end
end
kc = find(called);
Dk = ([ev.e] - [ev.s] + 1)' * dt; C = [ev.C]';
M.n_called = settle * numel(kc);                     % settled events (0 for the no-DR reference)
if isempty(kc) || ~settle
    M.fulfil_rate = NaN;
else
    M.fulfil_rate = sum(Dk(kc) .* min(max(M.avg_red(kc), 0), C(kc))) / sum(Dk(kc) .* C(kc));
end
M.n_valid = sum(M.valid);
M.n_full = sum(M.full);
if settle
    M.all_valid = M.n_valid == M.n_called;
    M.all_full = M.n_full == M.n_called;
else
    M.all_valid = NaN; M.all_full = NaN;
end
M.max_rebound = max([M.rebound; 0]);
M.max_rebound6 = max([M.rebound6; 0]);
%% costs (operating period of the run)
M.cost_energy = sum(inp.price(1:T) .* L.pg) * dt;
M.gas_MWh = sum(L.pgt) * dt;
M.cost_gas = M.gas_MWh * par.price.gas / par.gt.eta_e;
M.cost_deg = sum(L.pch + L.pdis) * dt * par.bess.c_deg;
M.cost_op = M.cost_energy + M.cost_gas + M.cost_deg;
% service cost of deferred work (the same delay price c_jct that every optimiser has in its objective)
M.cost_delay = par.qos.c_jct * dt * sum(L.backlog(:)) + par.qos.c_late * dt * sum(L.overdue);
M.dr_pay = sum(M.pay);
M.pen_dev = sum(par.dr.kappa_dev * [ev(kc).price]' .* M.short(kc) .* Dk(kc));
M.pen_rb = settle * par.dr.c_rb * sum(M.rebound);
%% pre-event load-up, payback, ramps, evening peak
if isempty(kc)
    pre = []; gaps = []; after = [];
else
    s1 = ev(kc(1)).s; eK = ev(kc(end)).e;
    pre = max(1, s1 - round(par.dr.pre_win_h / dt)):(s1 - 1);
    gaps = [];
    for j = 1:numel(kc) - 1, gaps = [gaps, (ev(kc(j)).e + 1):(ev(kc(j+1)).s - 1)]; end %#ok<AGROW>
    after = (eK + 1):min(T, eK + round(par.dr.payback_h / dt));
end
M.pen_pre = settle * par.dr.c_pre * sum(max(L.pg(pre) - base(pre), 0)) * dt;   % optional load-up assessment (0 by default)
M.net_cost = M.cost_op + M.cost_delay - M.dr_pay + M.pen_dev + M.pen_rb + M.pen_pre;
M.preload_mean = mean_or_nan(L.pg(pre) - base(pre));
M.preload_max = max_or_nan(L.pg(pre) - base(pre));
M.ramp_up_max = max([diff(L.pg); 0]);
hh = (0:T-1)' * dt;
M.peak_evening = max(L.pg(hh >= 14 & hh < 24));
M.peak_grid = max(L.pg);
if ~isempty(refL)
    M.preload_vs_nodr = mean_or_nan(L.pg(pre) - refL.pg(pre));
    M.payback_gap = sum(max(L.pg(gaps) - refL.pg(gaps), 0)) * dt;
    M.payback_after = sum(max(L.pg(after) - refL.pg(after), 0)) * dt;
    M.maxdev_after = max_or_nan(L.pg(after) - refL.pg(after));
    M.true_red_mean = mean_or_nan(M.true_red(kc));
else
    M.preload_vs_nodr = NaN; M.payback_gap = NaN; M.payback_after = NaN; M.maxdev_after = NaN; M.true_red_mean = NaN;
end
%% end-of-window state: leftover backlog and storage deficit w.r.t. no-DR
M.term_backlog = sum(L.backlog(T, :));
if ~isempty(refL)
    pval = min(inp.price(1:T));
    dB = M.term_backlog - sum(refL.backlog(T, :));
    dE = refL.E(T) - L.E(T); dS = refL.S(T) - L.S(T);
    M.term_adj = d.c_B_end * dB + (pval + par.bess.c_deg) * dE / par.bess.eta_c + pval * dS / (par.tes.eta_c * L.cop(T));
else
    M.term_adj = d.c_B_end * M.term_backlog;
end
M.cost_op_adj = M.cost_op + M.term_adj;
M.net_cost_adj = M.net_cost + M.term_adj;
M.net_cost_excl_rb = M.net_cost_adj - M.pen_rb - M.pen_pre;   % cost under the Jiangsu rules alone (no rebound / load-up charge)
%% carbon
M.co2 = sum(L.pg) * dt * par.co2.ef_grid + M.gas_MWh / par.gt.eta_e * par.co2.ef_gas;
%% service and diagnostics
M.lateness = sum(L.overdue) * dt;                    % GPU-h * h
M.cap_violation = max(L.over);
M.bess_throughput = sum(L.pch + L.pdis) * dt;
M.mean_backlog = mean(sum(L.backlog, 2));
%% user side: delay of the deferrable work, use of the SLA slack, long-training backlog across events
Dc = sum(L.backlog, 1) * dt;                                   % backlog-hours per class (GPU-h * h)
Dc_ref = zeros(1, 3); if ~isempty(refL), Dc_ref = sum(refL.backlog, 1) * dt; end
yeff = L.y; if isfield(L, 'z') && isfield(par.it, 'cap_on') && par.it.cap_on, yeff = L.y - par.it.cap_beta * par.it.cap_rho * L.z; end
Vc = sum(max(inp.real.flex(1:T, :) - yeff, 0), 1) * dt;        % deferred work per class (GPU-h)
M.delay_GPUh_h = sum(Dc);
M.deferred_GPUh = sum(Vc);
if M.deferred_GPUh > 1e-6
    M.mean_delay_h = sum(Dc - Dc_ref) / M.deferred_GPUh;
    M.sla_use = sum((Dc - Dc_ref) ./ par.it.lag_h(:)') / M.deferred_GPUh;
else
    M.mean_delay_h = 0; M.sla_use = 0;
end
M.c3_peak = 0; M.c3_carry = 0;
if ~isempty(kc)
    M.c3_peak = max(L.backlog(ev(kc(1)).s:ev(kc(end)).e, 3));
    for j = 2:numel(kc), M.c3_carry = max(M.c3_carry, L.backlog(ev(kc(j)).s - 1, 3)); end
end
M.fallbacks = sum(L.fallback);
M.solve_time = sum(L.solve_time);
M.Pcap = d.Pcap;
end

function v = mean_or_nan(x)
if isempty(x), v = NaN; else, v = mean(x); end
end

function v = max_or_nan(x)
if isempty(x), v = NaN; else, v = max(x); end
end
