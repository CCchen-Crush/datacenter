function [u, info] = planner_jr(st, data, ctx)
%PLANNER_JR  Joint computing-storage recovery (proposed): solve the joint model on a rolling horizon
%   and apply the first-step decisions. ctx.fmode chooses oracle / expected / scenario forecasts.
par = ctx.par; t0 = st.t;
H = min(ctx.H, par.Tsim - t0 + 1);
sc = make_scen(ctx.inp, par, ctx.base, t0, H, ctx);
opt = struct('milp', ctx.milp, 'nonant', true);
opt.visible = t0 >= [ctx.ev.notice_step]' | ctx.all_visible;
[opt.terminal, opt.Eref_end, opt.Sref_end] = terminal_ref(ctx, t0 + H - 1);
[P, ix] = build_model(par, st, sc, ctx.ev, opt);
sol = solve_milp(P, ctx.solver);
info.ok = sol.ok; info.time = sol.time;
if ~sol.ok
    [u, ~] = planner_irr(st, data, ctx); info.fallback = true; return;
end
info.fallback = false;
u = first_step(sol.x, ix);
info.sol = sol; info.ix = ix;
end
