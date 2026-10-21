function out = exp1_mechanism(ctx, root, opts)
%EXP1_MECHANISM  How the dual recovery demand left by event A limits the deliverable capability of
%   event B, as a function of the interval tau and the connection margin gamma.
%   Cases:  G0   single-event capability of B (no event A)
%           IR   A delivered by the independent split, then independent (ASAP, compute-first) recovery
%           IRJ  same post-A state as IR, but joint (optimised) recovery
%           JR   A delivery and recovery jointly optimised
%           BND  analytical bound of Proposition 1 evaluated at the IR post-A state
if nargin < 3, opts = struct(); end
taus   = getf(opts, 'taus',   [0.25 0.5 0.75 1 1.5 2 3 4]);
gammas = getf(opts, 'gammas', [1.0 1.05 1.1 1.2 1.3]);
CA = getf(opts, 'CA', 9); tA = 17; DA_h = getf(opts, 'DA_h', 1); DB_h = getf(opts, 'DB_h', 1);
par0 = ctx.par; d0 = ctx.d; dt = par0.dt;
rows = []; 
for g = gammas
    c = ctx; c.par.cap.Pcap_abs = g * par0.cap.Pbase_peak; c.d = sys_derived(c.par);
    % prepared state at the start of A: nominal operation, storage topped up for the event
    c0 = c; c0.t_stop = round(tA / dt);
    o = run_closed_loop(c.par, c.inp.real, c.base, struct('s', {}, 'e', {}, 'win', {}), @nominal_wrap, c0);
    XA = o.st; XA.E = c.par.bess.Emax; XA.S = c.par.tes.Smax;
    for tau = taus
        tB = tA + DA_h + tau;
        cc = set_events(c, [tA tB], [DA_h DB_h], [CA 1], [24 24]);
        evA = cc.ev(1); evB = cc.ev(2);
        % single-event capability of B
        e0 = cc.ev; e0(1).mode = 'none'; e0(2).mode = 'max';
        G0 = max_deliverable(cc, XA, e0);
        % fully joint
        ej = cc.ev; ej(1).mode = 'hard'; ej(2).mode = 'max';
        GJ = max_deliverable(cc, XA, ej);
        % independent: simulate A + recovery with the rule-based controller
        ci = cc; ci.st0 = XA; ci.t_stop = evA.e; ci.ev = cc.ev(1); ci.ev(1).C = CA; ci.all_visible = true;
        oA = run_closed_loop(cc.par, cc.inp.real, cc.base, ci.ev, @planner_irr, ci);
        stA = oA.st;                                   % state at e_A + 1
        redA = mean(cc.base(evA.s:evA.e) - oA.log.pg(evA.s:evA.e));
        ci.st0 = stA; ci.t_stop = evB.s - 1; ci.ev = cc.ev; ci.ev(2).C = max(G0, 0);
        oR = run_closed_loop(cc.par, cc.inp.real, cc.base, ci.ev, @planner_irr, ci);
        eb = cc.ev; eb(1).mode = 'none'; eb(2).mode = 'max';
        GI = max_deliverable(cc, oR.st, eb);
        % same post-A state, joint recovery
        GIJ = max_deliverable(cc, stA, eb);
        % recovery demand at e_A and Proposition-1 bound
        [Rc, Rs, Hh, bnd] = recovery_terms(cc, stA, evB, G0);
        rows = [rows; g, tau, CA, redA, G0, GI, GIJ, GJ, bnd, Rc, Rs, Hh]; %#ok<AGROW>
        fprintf('  exp1 gamma=%.2f tau=%.2f  G0=%.2f IR=%.2f IRJ=%.2f JR=%.2f bound=%.2f (Rc=%.1f Rs=%.1f H=%.1f MWh)\n', ...
            g, tau, G0, GI, GIJ, GJ, bnd, Rc, Rs, Hh);
    end
end
hdr = {'gamma', 'tau_h', 'C_A', 'red_A', 'G0', 'G_IR', 'G_IRJ', 'G_JR', 'G_bound', 'Rcomp_MWh', 'Rstor_MWh', 'Headroom_MWh'};
write_csv(fullfile(root, 'results', 'exp1_mechanism.csv'), hdr, rows);
out.rows = rows; out.hdr = hdr;
end

function [Rc, Rs, Hh, bnd] = recovery_terms(c, st, evB, G0)
% Recovery demand left at the end of A and the bound of Proposition 1.
%   (i)  energy type : C_B*D_B <= Xbar_B - X_A + E_s + H_eff
%   (ii) power type  : C_B <= max_{Hc+Hs<=H} { p_f - (X_due - Hc - W_sw)^+/D_B + min(P_s, (E_s + eta*Hs)/D_B) }
%   (iii) C_B <= G0 (single-event capability).   bound = min of (i)-(iii).
%   Both (i) and (ii) add the spare gas-engine output (+ absorption cooling) if the engine is off in the baseline.
%   X = computing backlog in facility energy, p_f = deferrable power that can still be paused in B,
%   X_due = backlog of A that falls due before the end of B, W_sw = interval work that can be swapped
%   past e_B (EDF reordering frees GPUs for due work without extra headroom), P_s / E_s = storage power / energy.
par = c.par; d = c.d; dt = par.dt; t = st.t;
tB = evB.s:evB.e; DB = numel(tB) * dt; tau = (evB.s - t) * dt;
cop = mean(c.inp.real.cop(tB)); phi = 1 + par.fac.a_aux + par.fac.theta / cop;
eps_ = phi * d.pdyn;                                          % facility MWh per GPU-h
XA = eps_ * sum(st.rem(:)); Rc = XA;
Rs = (par.bess.Emax - st.E) / par.bess.eta_c + (par.tes.Smax - st.S) / (par.tes.eta_c * cop);
iv = t:(evB.s - 1);
Hh = sum(max(d.Pcap - c.base(iv), 0)) * dt;                   % recovery headroom energy H(tau)
Xbar = 0; pf = 0;
for k = 1:3
    L = d.lag(k) * dt; w = max(1, evB.e - d.lag(k) + 1):evB.e;
    Xbar = Xbar + eps_ * sum(c.inp.real.flex(w, k)) * dt;
    pf = pf + eps_ * mean(c.inp.real.flex(tB, k)) * min(L, DB) / DB;
end
Xdue = eps_ * sum(sum(st.rem(1:min(evB.e, size(st.rem,1)), :)));
Wsw = 0;                                                      % interval arrivals whose deadline is after e_B:
for k = 1:3                                                   % they can be deferred to free GPUs for due work
    late = iv(iv + d.lag(k) > evB.e);
    Wsw = Wsw + eps_ * sum(c.inp.real.flex(late, k)) * dt;
end
Es = par.bess.eta_d * (st.E - par.bess.Emin) + par.tes.eta_d * (st.S - par.tes.Smin) / cop;
Ps = par.bess.Pmax + par.tes.Qmax / cop;
eta = par.bess.eta_c * par.bess.eta_d;
gfree = mean(par.it.u_max * par.it.Ngpu - c.inp.real.inf(iv) - c.inp.real.fix(iv) - sum(c.inp.real.flex(iv, :), 2));
Hc_max = min(Hh, eps_ * max(gfree, 0) * tau);                 % catch-up limited by headroom and free GPUs
Hs_max = par.bess.Pmax * tau;                                 % recharge limited by charger power
gt_add = max(par.gt.Pmax - mean(c.pgt_nom(tB)), 0);          % gas engine not already running in the baseline
gt_eff = gt_add + min(d.kh * gt_add * par.ac.cop, par.ac.Qmax) / cop;
if Hh <= XA, Heff = Hh; else, Heff = XA + eta * (Hh - XA); end
b1 = (Xbar - XA + Es + Heff) / DB + gt_eff;
b2 = -Inf;
for Hc = linspace(0, Hc_max, 51)
    Hs = min(Hh - Hc, Hs_max);
    b2 = max(b2, pf - max(Xdue - Hc - Wsw, 0) / DB + min(Ps, (Es + eta * Hs) / DB) + gt_eff);
end
bnd = max(0, min([G0, b1, b2]));
end

function [u, info] = nominal_wrap(st, data, ctx)
u = planner_nominal(st, ctx.par, data, ctx.inp.price(st.t));
info.ok = true; info.time = 0; info.fallback = false;
end

function v = getf(s, f, d)
if isfield(s, f), v = s.(f); else, v = d; end
end
