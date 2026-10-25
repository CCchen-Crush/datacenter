function [u, info] = planner_irpd(st, data, ctx)
%PLANNER_IRPD  Independent recovery coordinated by an iteratively updated channel price (benchmark IR-PD,
%   two-way price feedback, renewed at every step from the measured state). The facility first prices the
%   recovery channel from the joint plan over the horizon (dual of the electric balance with the binaries fixed,
%   minus the TOU price, as for IR-P). The IT scheduler then schedules the computing work alone at that price
%   (build_compute_model), the facility re-optimises with this IT schedule fixed and returns the marginal value
%   of IT power under its own best response, and the price is moved towards it with damping beta:
%       lambda(k+1) = lambda(k) + beta * (lambda_fac(k) - lambda(k)),   k = 1..K.
%   The IT schedules of rounds k0..K are averaged (primal averaging of the price iteration), the IT applies the
%   first step of the averaged schedule and the facility energy-management system follows with it fixed.
%   ctx.irpd = struct('K', 12, 'beta', 0.5, 'k0', 7) sets the rounds, the damping and the first averaged round.
par = ctx.par; t0 = st.t; dt = par.dt;
K = 12; beta = 0.5; k0 = 7;                     % rounds, damping, first round in the average
if isfield(ctx, 'irpd')
    if isfield(ctx.irpd, 'K'), K = ctx.irpd.K; end
    if isfield(ctx.irpd, 'beta'), beta = ctx.irpd.beta; end
    if isfield(ctx.irpd, 'k0'), k0 = ctx.irpd.k0; end
end
H = min(ctx.H, par.Tsim - t0 + 1);
c1 = ctx; if strcmp(ctx.fmode, 'scenario'), c1.fmode = 'expected'; end
sc = make_scen(ctx.inp, par, ctx.base, t0, H, c1);
act = event_activity(ctx, t0, sc.S, 'ce'); vis = any(act, 2);
[on, Ee, Se] = terminal_ref(ctx, t0 + H - 1);
fac = struct('milp', ctx.milp, 'nonant', true, 'visible', vis, 'active', act, 'terminal', on, 'Eref_end', Ee, 'Sref_end', Se);
info.ok = true; info.time = 0; info.fallback = false;
% round 0: channel price of the joint plan
[lam, ok, tt] = channel_price(par, st, sc, ctx, fac); info.time = info.time + tt;
if ~ok, lam = zeros(H, 1); end
o1 = struct('alpha', ctx.alpha, 'visible', vis, 'pgt_nom', ctx.pgt_nom(t0:t0+H-1), ...
            'ynom_now', sum(ctx.inp.real.flex(t0, :)), 'use_share', false);
Ysum = zeros(H, 3); Zsum = []; n = 0;
for k = 1:K
    o1.lambda = lam;
    [P1, ix1] = build_compute_model(par, st, sc, ctx.ev, o1);
    s1 = solve_milp(P1, ctx.solver); info.time = info.time + s1.time;
    if ~s1.ok, break; end
    y = [s1.x(ix1.Y{1}), s1.x(ix1.Y{2}), s1.x(ix1.Y{3})];
    z = []; if ~isempty(ix1.Zc), z = [s1.x(ix1.Zc{1}), s1.x(ix1.Zc{2}), s1.x(ix1.Zc{3})]; end
    if k >= min(k0, K)
        Ysum = Ysum + y; n = n + 1;
        if ~isempty(z), if isempty(Zsum), Zsum = z; else, Zsum = Zsum + z; end, end
    end
    if k == K, break; end
    f2 = fac; f2.fix_y = y; f2.fix_z = z;
    [lf, ok, tt] = channel_price(par, st, sc, ctx, f2); info.time = info.time + tt;
    if ~ok, break; end
    lam = lam + beta * (lf - lam);
end
if n == 0, [u, ~] = planner_irr(st, data, ctx); info.fallback = true; info.ok = false; return; end
yfix = Ysum / n; zfix = []; if ~isempty(Zsum), zfix = Zsum / n; end
o2 = fac; o2.fix_y = yfix; o2.fix_z = zfix;
[P2, ix2] = build_model(par, st, sc, ctx.ev, o2);
s2 = solve_milp(P2, ctx.solver); info.time = info.time + s2.time;
if ~s2.ok, [u, ~] = planner_irr(st, data, ctx); info.fallback = true; info.ok = false; return; end
u = first_step(s2.x, ix2);
u.y = yfix(1, :); if ~isempty(zfix), u.z = zfix(1, :); end
info.sol = s2; info.ix = ix2; info.lambda = lam;
end

function [lam, ok, tt] = channel_price(par, st, sc, ctx, opt)
% premium of the electric balance over the TOU price (CNY/MWh) of the facility plan (binaries fixed, LP duals)
[P, ix] = build_model(par, st, sc, ctx.ev, opt);
s1 = solve_milp(P, ctx.solver); tt = s1.time; lam = []; ok = false;
if ~s1.ok, return; end
P2 = P; xi = round(s1.x(P.intcon)); P2.lb(P.intcon) = xi; P2.ub(P.intcon) = xi; P2.intcon = [];
s2 = solve_milp(P2, ctx.solver); tt = tt + s2.time;
if ~s2.ok || isempty(s2.marg_eq), return; end
mv = s2.marg_eq(ix.row_el) / par.dt;
lam = max(mv(:), 0) - sc.price(:); ok = true;
end
