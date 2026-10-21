function [P, ix] = build_model(par, st, sc, ev, opt)
%BUILD_MODEL  Joint computing-storage recovery model of the AIDC-IES over a (rolling) horizon.
%
%   State at t0 = st.t (work arriving in t0 already in st.rem).  Scenario data sc:
%     sc.H, sc.S, sc.prob(Sx1), sc.flex(Hx3xS) nominal busy GPUs, sc.inf(HxS), sc.pv(HxS),
%     sc.cop(HxS), sc.price(Hx1) CNY/MWh, sc.Pb(Hx1) DR baseline (MW)
%   Events ev(k): s,e (absolute steps), C, price, win, Pbmax, and ev(k).mode in
%     'settle'  Jiangsu settlement (validity >= 80 %, pay <= 120 %), MILP if opt.milp
%     'hard'    reduction >= C in every step (capability analysis)
%     'max'     maximise a common reduction level (capability analysis)
%     'commit'  day-ahead: commitment C is a first-stage decision variable
%     'none'    ignored
%   opt: milp, nonant, fix_y (Hx3), terminal, Eref_end, Sref_end, no_late, visible (Kx1 logical),
%        Cmax (for 'commit'), w_max (weight of 'max')
%
%   Decision variables per step and scenario: y_c (busy GPUs, 3 classes), backlog B_c, overdue v_c,
%   grid pg, overflow pov, BESS pch/pdis/E, gas engine pgt, absorption heat hac, electric chiller qec,
%   TES qtc/qtd/S, PV ppv.
if nargin < 5, opt = struct(); end
opt = defaults(opt, numel(ev));
d = sys_derived(par); dt = par.dt; H = sc.H; S = sc.S; t0 = st.t;
pr = sc.prob(:)';
m = lpb_new();
W = @(c) dt * repmat(pr, H, 1) .* c;     % cost weight helper (c: HxS or scalar)

%% variables
for c = 1:3
    [m, Y{c}] = addb(m, H, S, 0, Inf, 0);
    [m, B{c}] = addb(m, H, S, 0, Inf, W(par.qos.c_jct));
    vub = Inf; if opt.no_late, vub = 0; end
    [m, V{c}] = addb(m, H, S, 0, vub, W(par.qos.c_late));
end
[m, PG]  = addb(m, H, S, par.cap.Pmin, Inf, W(repmat(sc.price(:), 1, S)));
[m, POV] = addb(m, H, S, 0, Inf, W(par.cap.c_over));
[m, PCH] = addb(m, H, S, 0, par.bess.Pmax, W(par.bess.c_deg));
[m, PDS] = addb(m, H, S, 0, par.bess.Pmax, W(par.bess.c_deg));
[m, E]   = addb(m, H, S, par.bess.Emin, par.bess.Emax, 0);
[m, PGT] = addb(m, H, S, 0, par.gt.Pmax, W(par.price.gas / par.gt.eta_e));
[m, HAC] = addb(m, H, S, 0, par.ac.Qmax / par.ac.cop, 0);
[m, QEC] = addb(m, H, S, 0, par.fac.Qec_max, 0);
[m, QTC] = addb(m, H, S, 0, par.tes.Qmax, 0);
[m, QTD] = addb(m, H, S, 0, par.tes.Qmax, 0);
[m, SS]  = addb(m, H, S, par.tes.Smin, par.tes.Smax, 0);
[m, PPV] = addb(m, H, S, 0, Inf, 0);
m.ub(PPV(:)) = max(sc.pv(:), 0);
if ~isempty(opt.fix_y)
    for c = 1:3
        v = repmat(opt.fix_y(:, c), 1, S);
        m.lb(Y{c}(:)) = v(:); m.ub(Y{c}(:)) = v(:);
    end
end
n = H * S; one = ones(n, 1); r = (1:n)';

%% GPU capacity
capfree = par.it.u_max * par.it.Ngpu - sc.inf - sc.fix;
m = lpb_addle(m, [r; r; r], [Y{1}(:); Y{2}(:); Y{3}(:)], [one; one; one], capfree(:));

%% workload backlog (computing recovery state) with lag-bounded deadlines
for c = 1:3
    L = d.lag(c);
    remc = st.rem(:, c);
    B0 = sum(remc);
    Dk = cumsum(remc); Dk = Dk(min(t0 + (0:H-1)', numel(Dk)));      % known work due by end of step
    arr = squeeze(sc.flex(:, c, :)) * dt; if S == 1, arr = arr(:); end
    arr(1, :) = 0;                                                     % arrivals of t0 already in backlog
    A = B0 + cumsum(arr, 1);
    Dn = zeros(H, S);
    if H > L, Dn(L+1:end, :) = cumsum(arr(1:H-L, :), 1); end
    Bmax = A - (Dk + Dn);
    Bmax = max(Bmax, 0);
    % B(h) - B(h-1) + dt*y(h) = arr(h)
    Bc = B{c}; rhs = arr; rhs(1, :) = rhs(1, :) + B0;
    I = [r; r]; J = [Bc(:); Y{c}(:)]; Vv = [one; dt * one];
    prev = Bc(1:end-1, :); cur = (2:H)' + (0:S-1) * H;
    I = [I; cur(:)]; J = [J; prev(:)]; Vv = [Vv; -ones(numel(prev), 1)];
    [m, ix.row_B{c}] = lpb_addeq(m, I, J, Vv, rhs(:));
    [m, ix.row_Bmax{c}] = lpb_addle(m, [r; r], [Bc(:); V{c}(:)], [one; -one], Bmax(:));
    ix.Bmax{c} = Bmax;
end

%% cooling balance:  qec + COP_ac*hac + qtd - qtc - theta*pdyn*sum(y) = theta*(Pfix + pdyn*k_inf*inf) + Q0
th = par.fac.theta; a = par.fac.a_aux;
base_it = d.Pfix + d.pdyn * (par.it.k_inf * sc.inf + sc.fix);
I = [r; r; r; r; r; r; r]; J = [QEC(:); HAC(:); QTD(:); QTC(:); Y{1}(:); Y{2}(:); Y{3}(:)];
Vv = [one; par.ac.cop * one; one; -one; -th * d.pdyn * [one; one; one]];
m = lpb_addeq(m, I, J, Vv, th * base_it(:) + par.fac.Q0);

%% electric balance: pg + ppv + pgt + pdis - pch - qec/cop - (1+a)*pdyn*sum(y) = (1+a)*base_it + P_aux0
I = repmat(r, 9, 1);
J = [PG(:); PPV(:); PGT(:); PDS(:); PCH(:); QEC(:); Y{1}(:); Y{2}(:); Y{3}(:)];
Vv = [one; one; one; one; -one; -1 ./ sc.cop(:); -(1 + a) * d.pdyn * [one; one; one]];
m = lpb_addeq(m, I, J, Vv, (1 + a) * base_it(:) + par.fac.P_aux0);

%% grid connection limit
[m, ix.row_cap] = lpb_addle(m, [r; r], [PG(:); POV(:)], [one; -one], d.Pcap * one);

%% storage dynamics
[m, ix.row_E] = add_store(m, E,  PCH, PDS, par.bess.eta_c, 1 / par.bess.eta_d, 1, st.E, dt, H, S);
[m, ix.row_S] = add_store(m, SS, QTC, QTD, par.tes.eta_c,  1 / par.tes.eta_d, 1 - par.tes.loss * dt, st.S, dt, H, S);

%% gas engine heat recovery and ramping
m = lpb_addle(m, [r; r], [HAC(:); PGT(:)], [one; -d.kh * one], zeros(n, 1));
cur = (2:H)' + (0:S-1) * H; cur = cur(:); nr = numel(cur); rr = (1:nr)';
if nr > 0
    m = lpb_addle(m, [rr; rr], [PGT(cur); PGT(cur - 1)], [ones(nr,1); -ones(nr,1)], par.gt.ramp * ones(nr,1));
    m = lpb_addle(m, [rr; rr], [PGT(cur); PGT(cur - 1)], [-ones(nr,1); ones(nr,1)], par.gt.ramp * ones(nr,1));
end
m.ub(PGT(1, :)) = min(par.gt.Pmax, st.pgt_prev + par.gt.ramp);
m.lb(PGT(1, :)) = max(0, st.pgt_prev - par.gt.ramp);

%% non-anticipativity of the first-step decisions
if S > 1 && opt.nonant
    X = {Y{1}, Y{2}, Y{3}, PCH, PDS, PGT, HAC, QEC, QTC, QTD, PPV};
    for q = 1:numel(X)
        xx = X{q}; ns = S - 1; rr = (1:ns)';
        m = lpb_addeq(m, [rr; rr], [xx(1, 2:S)'; repmat(xx(1, 1), ns, 1)], [ones(ns,1); -ones(ns,1)], zeros(ns,1));
    end
end

%% demand-response events (Jiangsu settlement), rebound windows
ix.ev = struct('R', {}, 'Z', {}, 'SF', {}, 'MX', {}, 'RHO', {}, 'C', {}, 'row_rb', {}, 'hw', {});
tend = t0 + H - 1;
for k = 1:numel(ev)
    e = ev(k); ix.ev(k).C = [];
    if strcmp(e.mode, 'none') || ~opt.visible(k), continue; end
    % ---- event window ----
    if e.e >= t0 && e.e <= tend
        hk = (max(e.s, t0):e.e) - t0 + 1; nk = e.e - e.s + 1; Dh = nk * dt;
        rhs0 = (st.ev_r(k) + sum(sc.Pb(hk))) / nk;
        nh = numel(hk);
        switch e.mode
            case 'settle'
                [m, R]  = addb(m, 1, S, 0, par.dr.pay_hi * e.C, -e.price * Dh * pr);
                [m, Z]  = addb(m, 1, S, 0, 1, 0); m.isint(Z) = opt.milp;
                [m, SF] = addb(m, 1, S, 0, Inf, par.dr.kappa_dev * e.price * Dh * pr);
                [m, MX] = addb(m, 1, S, 0, Inf, par.dr.c_maxload * pr);
                if st.ev_mx(k) > e.Pbmax + 1e-6, m.ub(Z) = 0; end
                for s = 1:S
                    pgk = PG(hk, s);
                    m = lpb_addle(m, ones(nh+1,1), [R(s); pgk], [1; ones(nh,1)/nk], rhs0);
                    m = lpb_addle(m, [1; 1], [R(s); Z(s)], [1; -par.dr.pay_hi * e.C], 0);
                    m = lpb_addle(m, ones(nh+1,1), [Z(s); pgk], [par.dr.valid_lo * e.C; ones(nh,1)/nk], rhs0);
                    m = lpb_addle(m, ones(nh+1,1), [SF(s); pgk], [-1; ones(nh,1)/nk], rhs0 - e.C);
                    m = lpb_addle(m, [(1:nh)'; (1:nh)'], [pgk; repmat(MX(s), nh, 1)], [ones(nh,1); -ones(nh,1)], e.Pbmax * ones(nh,1));
                end
                ix.ev(k).R = R; ix.ev(k).Z = Z; ix.ev(k).SF = SF; ix.ev(k).MX = MX;
            case 'commit'
                [m, Cv] = addb(m, 1, 1, 0, opt.Cmax, -par.dr.eps_commit);
                [m, R]  = addb(m, 1, S, 0, Inf, -e.price * Dh * pr);
                [m, Z]  = addb(m, 1, S, 0, 1, 0); m.isint(Z) = opt.milp;
                [m, Wv] = addb(m, 1, S, 0, opt.Cmax, 0);
                [m, SF] = addb(m, 1, S, 0, Inf, par.dr.kappa_dev * e.price * Dh * pr);
                [m, MX] = addb(m, 1, S, 0, Inf, par.dr.c_maxload * pr);
                Cm = opt.Cmax;
                for s = 1:S
                    pgk = PG(hk, s);
                    m = lpb_addle(m, [1;1], [Wv(s); Z(s)], [1; -Cm], 0);
                    m = lpb_addle(m, [1;1], [Wv(s); Cv], [1; -1], 0);
                    m = lpb_addle(m, [1;1;1], [Cv; Wv(s); Z(s)], [1; -1; Cm], Cm);
                    m = lpb_addle(m, ones(nh+1,1), [R(s); pgk], [1; ones(nh,1)/nk], rhs0);
                    m = lpb_addle(m, [1;1], [R(s); Wv(s)], [1; -par.dr.pay_hi], 0);
                    m = lpb_addle(m, ones(nh+1,1), [Wv(s); pgk], [par.dr.valid_lo; ones(nh,1)/nk], rhs0);
                    m = lpb_addle(m, ones(nh+2,1), [Cv; SF(s); pgk], [1; -1; ones(nh,1)/nk], rhs0);
                    m = lpb_addle(m, [(1:nh)'; (1:nh)'], [pgk; repmat(MX(s), nh, 1)], [ones(nh,1); -ones(nh,1)], e.Pbmax * ones(nh,1));
                end
                ix.ev(k).R = R; ix.ev(k).Z = Z; ix.ev(k).SF = SF; ix.ev(k).MX = MX; ix.ev(k).C = Cv;
            case 'hard'
                for s = 1:S
                    m.ub(PG(hk, s)) = min(m.ub(PG(hk, s)), max(sc.Pb(hk) - e.C, 0));
                end
            case 'max'
                [m, Cv] = addb(m, 1, 1, 0, Inf, -opt.w_max);
                for s = 1:S
                    m = lpb_addle(m, [(1:nh)'; (1:nh)'], [PG(hk, s); repmat(Cv, nh, 1)], ones(2*nh,1), sc.Pb(hk));
                end
                ix.ev(k).C = Cv;
        end
    end
    % ---- post-event rebound window ----
    if any(strcmp(e.mode, {'settle', 'commit'})) && ~isempty(e.win)
        w = e.win(e.win >= t0 & e.win <= tend);
        if ~isempty(w) && e.e <= tend
            hw = w - t0 + 1; nw = numel(hw);
            [m, RHO] = addb(m, 1, S, max(st.rb(k), 0), Inf, par.dr.c_rb * pr);
            rows_rb = zeros(nw, S);
            for s = 1:S
                [m, rows_rb(:, s)] = lpb_addle(m, [(1:nw)'; (1:nw)'], [PG(hw, s); repmat(RHO(s), nw, 1)], [ones(nw,1); -ones(nw,1)], sc.Pb(hw));
            end
            ix.ev(k).RHO = RHO; ix.ev(k).row_rb = rows_rb; ix.ev(k).hw = hw;
        end
    end
end

%% terminal state values (rolling horizon shorter than the simulation)
if opt.terminal
    [m, eE] = addb(m, 1, S, 0, Inf, par.term.c_E * pr);
    [m, eS] = addb(m, 1, S, 0, Inf, par.term.c_S * pr);
    for s = 1:S
        m = lpb_addle(m, [1;1], [E(H, s); eE(s)], [-1; -1], -opt.Eref_end);
        m = lpb_addle(m, [1;1], [SS(H, s); eS(s)], [-1; -1], -opt.Sref_end);
    end
end

P = lpb_finalize(m);
ix.Y = Y; ix.B = B; ix.V = V; ix.PG = PG; ix.POV = POV; ix.PCH = PCH; ix.PDS = PDS; ix.E = E;
ix.PGT = PGT; ix.HAC = HAC; ix.QEC = QEC; ix.QTC = QTC; ix.QTD = QTD; ix.SS = SS; ix.PPV = PPV;
ix.H = H; ix.S = S; ix.t0 = t0;
end

%% ----------------------------------------------------------------------
function [m, X] = addb(m, H, S, lb, ub, f)
if numel(f) == 1, f = f * ones(H*S, 1); end
[m, id] = lpb_addvar(m, H*S, lb, ub, f(:));
X = reshape(id, H, S);
end

function [m, rows] = add_store(m, X, PC, PD, eta_c, inv_eta_d, keep, X0, dt, H, S)
% X(h) - keep*X(h-1) - eta_c*dt*PC(h) + dt/eta_d*PD(h) = 0 ; X(0) = X0
n = H*S; r = (1:n)'; one = ones(n,1);
I = [r; r; r]; J = [X(:); PC(:); PD(:)]; V = [one; -eta_c*dt*one; inv_eta_d*dt*one];
cur = (2:H)' + (0:S-1) * H; prev = X(1:end-1, :);
I = [I; cur(:)]; J = [J; prev(:)]; V = [V; -keep * ones(numel(prev), 1)];
rhs = zeros(H, S); rhs(1, :) = keep * X0;
[m, rows] = lpb_addeq(m, I, J, V, rhs(:));
end

function opt = defaults(opt, K)
f = {'milp', true; 'nonant', true; 'fix_y', []; 'terminal', false; 'Eref_end', 0; 'Sref_end', 0; ...
     'no_late', false; 'visible', true(K,1); 'Cmax', 15; 'w_max', 1e7};
for i = 1:size(f,1)
    if ~isfield(opt, f{i,1}), opt.(f{i,1}) = f{i,2}; end
end
if numel(opt.visible) == 1, opt.visible = repmat(opt.visible, K, 1); end
end
