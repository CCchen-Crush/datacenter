function out = exp13_region(ctx, root, opts)
%EXP13_REGION  Consecutive-event deliverable-capacity region (decision experiment G1b). Two events by
%   default: A lasts DA_h and B lasts DB_h hours, B starts tau hours after the end of A. For every
%   commitment C1 of A the largest constant reduction C2 deliverable in B is computed with perfect
%   information, all task deadlines met and the connection limit hard, from the same prepared state at
%   the start of A as in Exp1 (nominal operation, storage full). With opts.t0s (start hours of K >= 2
%   events) the first K-1 events are all committed at C1 and the last one is maximised (C2), e.g. the
%   three events of the main case. Boundaries C2_max(C1):
%     JR   all events and the recoveries jointly optimised (foresight of the last event)
%     IRJ  the first K-1 events and the recoveries between them by the independent split rule (IR),
%          then joint recovery: same post-event state as IR
%     JRM  each event planned cost-optimally when it is the next one, without knowledge of the later
%          events (event by event), the last event maximised once it is known
%     IRO  independent recovery with a static compute share alpha: the IT scheduler plans alone
%          (alpha * C of every event), then storage + IES with the IT schedule fixed; best alpha of
%          the grid for each C1 (hindsight, i.e. the strongest static split). The boundary of every
%          fixed alpha is stored as well (C2_IRO_a<100*alpha>)
%     IR   (reference) everything by the independent rule, the last event maximised from its start
%   opts: taus (h), gamma, DA_h, DB_h, C1 (grid; default 0:0.5:single-event capability of A), alphas,
%         t0s / durs (K-event configuration, replaces taus/DA_h/DB_h), tag (results/exp13_region<tag>.csv)
if nargin < 3, opts = struct(); end
g = getf(opts, 'gamma', ctx.par.cap.gamma);
alphas = getf(opts, 'alphas', ctx.par.bench.alpha_grid);
if isfield(opts, 't0s')
    cfgs = {opts.t0s(:)', getf(opts, 'durs', ones(1, numel(opts.t0s)))};
else
    DA_h = getf(opts, 'DA_h', 1); DB_h = getf(opts, 'DB_h', 1); tA = getf(opts, 'tA', 17);
    taus = getf(opts, 'taus', [0.5 1]);
    cfgs = cell(numel(taus), 2);
    for i = 1:numel(taus), cfgs(i, :) = {[tA, tA + DA_h + taus(i)], [DA_h DB_h]}; end
end
par0 = ctx.par; dt = par0.dt;
c = ctx; c.par.cap.Pcap_abs = g * par0.cap.Pbase_peak; c.d = sys_derived(c.par);
rows = []; t0 = tic;
for ic = 1:size(cfgs, 1)
    t0s = cfgs{ic, 1}; durs = cfgs{ic, 2}; K = numel(t0s);
    tau = t0s(K) - (t0s(K-1) + durs(K-1));                     % gap before the last event
    % prepared state at the start of the first event (as Exp1): nominal operation, storage topped up
    c0 = c; c0.t_stop = round(t0s(1) / dt);
    o = run_closed_loop(c.par, c.inp.real, c.base, struct('s', {}, 'e', {}, 'win', {}), @nominal_wrap, c0);
    XA = o.st; XA.E = c.par.bess.Emax; XA.S = c.par.tes.Smax;
    cc = set_events(c, t0s, durs, ones(1, K), 24 * ones(1, K));
    e0 = cc.ev; for k = 1:K, e0(k).mode = 'none'; end, e0(1).mode = 'max'; G0A = max_deliverable(cc, XA, e0);
    e0 = cc.ev; for k = 1:K, e0(k).mode = 'none'; end, e0(K).mode = 'max'; G0B = max_deliverable(cc, XA, e0);
    C1s = getf(opts, 'C1', [0:0.5:G0A, G0A - 1e-6]);
    C1s = unique(C1s(C1s <= G0A));
    eb = cc.ev; for k = 1:K-1, eb(k).mode = 'none'; end, eb(K).mode = 'max';
    for C1 = C1s
        % ---- JR: fully joint ----
        ej = cc.ev; for k = 1:K-1, ej(k).C = C1; ej(k).mode = amode(C1); end, ej(K).mode = 'max';
        GJ = max_deliverable(cc, XA, ej);
        % ---- IRJ / IR: the first K-1 events by the independent rule ----
        ci = cc; ci.st0 = XA; ci.t_stop = cc.ev(K-1).e; ci.ev = cc.ev(1:K-1); ci.all_visible = true;
        for k = 1:K-1, ci.ev(k).C = C1; end
        oA = run_closed_loop(cc.par, cc.inp.real, cc.base, ci.ev, @planner_irr, ci);
        redA = min(arrayfun(@(e) mean(cc.base(e.s:e.e) - oA.log.pg(e.s:e.e)), cc.ev(1:K-1)));
        okA = C1 == 0 || redA >= cc.par.dr.full_lo * C1 - 1e-6;
        GIJ = NaN; GI = NaN;
        if okA
            GIJ = max_deliverable(cc, oA.st, eb);
            cr = ci; cr.st0 = oA.st; cr.t_stop = cc.ev(K).s - 1; cr.ev = cc.ev; for k = 1:K-1, cr.ev(k).C = C1; end
            cr.ev(K).C = max(G0B, 0);
            oR = run_closed_loop(cc.par, cc.inp.real, cc.base, cr.ev, @planner_irr, cr);
            GI = max_deliverable(cc, oR.st, eb);
        end
        % ---- JRM: event by event (no events before the last: the last is the next one, = JR) ----
        GM = NaN;
        if C1 == 0
            GM = GJ;
        else
            st = XA;
            for k = 1:K-1
                st = myopic_state(cc, st, k, C1);
                if isempty(st), break; end
            end
            if ~isempty(st), GM = max_deliverable(cc, st, eb); end
        end
        % ---- IRO: static split, best alpha ----
        GO = NaN; aO = NaN; va = nan(1, numel(alphas));
        if ~isnan(GJ)
            for i = 1:numel(alphas)
                va(i) = iro_max(cc, XA, C1, alphas(i), GJ);
                if ~isnan(va(i)) && (isnan(GO) || va(i) > GO + 1e-9), GO = va(i); aO = alphas(i); end
            end
        end
        rows = [rows; tau, g, durs(1), durs(K), G0A, G0B, C1, GJ, GIJ, GM, GO, aO, GI, redA, K, va]; %#ok<AGROW>
        fprintf('  exp13 K=%d tau=%.2f C1=%5.2f  JR=%5.2f IRJ=%5.2f JRM=%5.2f IRO=%5.2f (alpha %.1f) IR=%5.2f  (%.1f min)\n', ...
            K, tau, C1, GJ, GIJ, GM, GO, aO, GI, toc(t0) / 60);
    end
end
hdr = [{'tau_h', 'gamma', 'DA_h', 'DB_h', 'G0A', 'G0B', 'C1', 'C2_JR', 'C2_IRJ', 'C2_JRM', 'C2_IRO', 'alpha_IRO', 'C2_IR', 'redA_IR', 'K'}, ...
       arrayfun(@(a) sprintf('C2_IRO_a%03d', round(100 * a)), alphas, 'UniformOutput', false)];
write_csv(fullfile(root, 'results', sprintf('exp13_region%s.csv', getf(opts, 'tag', ''))), hdr, rows);
out.rows = rows; out.hdr = hdr;
end

function m = amode(C)
if C > 0, m = 'hard'; else, m = 'none'; end
end

function st = myopic_state(cc, st0, k, C1)
% State at the end of event k when it is planned cost-optimally (commitment C1) from state st0 without
% knowledge of the later events (JR-M: only the next event is active).
par = cc.par; T = par.Tsim; t0 = st0.t; K = numel(cc.ev);
em = cc.ev; for j = 1:K, em(j).mode = 'none'; end
em(k).C = C1; em(k).mode = amode(C1);
s0 = state_fit_events(st0, K);
c = cc; c.fmode = 'oracle';
sc = make_scen(cc.inp, par, cc.base, t0, T - t0 + 1, c);
vis = false(K, 1); vis(k) = C1 > 0;
opt = struct('milp', false, 'visible', vis, 'no_late', true, 'terminal', true, ...
             'Eref_end', cc.Eref(end), 'Sref_end', cc.Sref(end));
[P, ix] = build_model(par, s0, sc, em, opt);
P.ub(ix.POV(:)) = 0;
sol = solve_milp(P, cc.solver);
st = [];
if ~sol.ok, return; end
c.plan = pad_plan(extract_plan(sol.x, ix), t0, T);
c.st0 = s0; c.t_stop = cc.ev(k).e;
o = run_closed_loop(par, cc.inp.real, cc.base, em, @planner_plan, c);
st = o.st;
end

function G = iro_max(cc, XA, C1, a, hi)
% Largest C2 that the static split alpha = a delivers in the last event together with C1 in the
% others (bisection on the feasibility of: IT plan with share a, then storage + IES with the IT plan
% fixed, all events hard).
G = NaN;
if ~iro_ok(cc, XA, C1, 0, a), return; end
lo = 0;
if iro_ok(cc, XA, C1, hi, a), G = hi; return; end
while hi - lo > 0.02
    mid = (lo + hi) / 2;
    if iro_ok(cc, XA, C1, mid, a), lo = mid; else, hi = mid; end
end
G = lo;
end

function ok = iro_ok(cc, XA, C1, C2, a)
par = cc.par; T = par.Tsim; t0 = XA.t; K = numel(cc.ev);
ev = cc.ev; for k = 1:K-1, ev(k).C = C1; end, ev(K).C = C2;
vis = [ev.C]' > 0;
s0 = state_fit_events(XA, K);
c = cc; c.fmode = 'oracle';
sc = make_scen(cc.inp, par, cc.base, t0, T - t0 + 1, c);
o1 = struct('alpha', a, 'visible', vis, 'pgt_nom', cc.pgt_nom(t0:T), 'ynom_now', sum(cc.inp.real.flex(t0, :)));
[P1, ix1] = build_compute_model(par, s0, sc, ev, o1);
s1 = solve_milp(P1, cc.solver);
ok = false;
if ~s1.ok, return; end
yfix = [s1.x(ix1.Y{1}), s1.x(ix1.Y{2}), s1.x(ix1.Y{3})];
e2 = ev; for k = 1:K, e2(k).mode = amode(ev(k).C); end
o2 = struct('milp', false, 'fix_y', yfix, 'visible', vis, 'no_late', true, 'terminal', false);
[P2, ix2] = build_model(par, s0, sc, e2, o2);
P2.ub(ix2.POV(:)) = 0;
s2 = solve_milp(P2, cc.solver);
ok = s2.ok;
end

function p = pad_plan(p, t0, T)
% plan rows 1..H of a model built at t0 -> absolute steps t0..T (as planner_plan indexes them)
f = fieldnames(p);
for i = 1:numel(f)
    v = p.(f{i}); w = zeros(T, size(v, 2)); w(t0:t0 + size(v, 1) - 1, :) = v; p.(f{i}) = w;
end
end

function [u, info] = nominal_wrap(st, data, ctx)
u = planner_nominal(st, ctx.par, data, ctx.inp.price(st.t));
info.ok = true; info.time = 0; info.fallback = false;
end

function v = getf(s, f, d)
if isfield(s, f), v = s.(f); else, v = d; end
end
