function [lam, info] = dayahead_prices(ctx)
%DAYAHEAD_PRICES  Day-ahead "recovery-channel" price signal for the price-coordinated independent
%   benchmark IR-P. The facility solves the deterministic day-ahead joint plan (historical-mean
%   forecasts), fixes the binaries and re-solves the LP; the dual of the electric balance is the
%   marginal value of facility electricity (CNY/MWh). lam = that value minus the TOU price, i.e. the
%   extra value of one MW of IT power at t (connection limit, rebound windows, DR events) that the IT
%   scheduler then adds to its energy price. The signal is fixed day-ahead (one-way, not updated).
par = ctx.par; dt = par.dt; T = par.Tsim; K = numel(ctx.ev);
c = ctx; c.fmode = 'expected'; c.da = true;
sc = make_scen(ctx.inp, par, ctx.base, 1, T, c);
st = state_init(par, K); st = add_arrivals(st, sc.flex(1, :, 1), par);
act = event_activity(ctx, 1, 1, 'ce');
[on, Ee, Se] = terminal_ref(ctx, T);
opt = struct('milp', true, 'visible', any(act, 2), 'active', act, 'terminal', on, 'Eref_end', Ee, 'Sref_end', Se);
[P, ix] = build_model(par, st, sc, ctx.ev, opt);
s1 = solve_milp(P, ctx.solver);
if ~s1.ok, error('dayahead_prices:milp', 'day-ahead joint plan not solved'); end
P2 = P; xi = round(s1.x(P.intcon)); P2.lb(P.intcon) = xi; P2.ub(P.intcon) = xi; P2.intcon = [];
s2 = solve_milp(P2, ctx.solver);
if ~s2.ok || isempty(s2.marg_eq), error('dayahead_prices:lp', 'no duals from the fixed-binary LP'); end
mv = s2.marg_eq(ix.row_el) / dt;
lam = max(mv(:), 0) - sc.price(:);
info.value = mv(:); info.time = s1.time + s2.time;
end
