function [u, info] = planner_iro(st, data, ctx)
%PLANNER_IRO  Independent recovery, optimisation based (sequential / decentralised):
%   stage 1 - IT scheduler optimises compute alone (own DR share alpha*C, IT power budget, TOU);
%   stage 2 - facility EMS optimises storage + IES with the IT schedule fixed.
par = ctx.par; t0 = st.t;
H = min(ctx.H, par.Tsim - t0 + 1);
c1 = ctx; if strcmp(ctx.fmode, 'scenario'), c1.fmode = 'expected'; end
sc = make_scen(ctx.inp, par, ctx.base, t0, H, c1);
vis = t0 >= [ctx.ev.notice_step]' | ctx.all_visible;
o1 = struct('alpha', ctx.alpha, 'visible', vis, 'pgt_nom', ctx.pgt_nom(t0:t0+H-1), ...
            'ynom_now', sum(ctx.inp.real.flex(t0, :)));
[P1, ix1] = build_compute_model(par, st, sc, ctx.ev, o1);
s1 = solve_milp(P1, ctx.solver);
info.ok = s1.ok; info.time = s1.time; info.fallback = false;
if ~s1.ok, [u, ~] = planner_irr(st, data, ctx); info.fallback = true; return; end
yfix = [s1.x(ix1.Y{1}), s1.x(ix1.Y{2}), s1.x(ix1.Y{3})];
o2 = struct('milp', ctx.milp, 'nonant', true, 'fix_y', yfix, 'visible', vis);
[o2.terminal, o2.Eref_end, o2.Sref_end] = terminal_ref(ctx, t0 + H - 1);
[P2, ix2] = build_model(par, st, sc, ctx.ev, o2);
s2 = solve_milp(P2, ctx.solver);
info.time = info.time + s2.time;
if ~s2.ok, [u, ~] = planner_irr(st, data, ctx); info.fallback = true; info.ok = false; return; end
u = first_step(s2.x, ix2);
u.y = yfix(1, :);
info.sol = s2; info.ix = ix2;
end
