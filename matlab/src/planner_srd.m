function [u, info] = planner_srd(st, data, ctx)
%PLANNER_SRD  Staged recovery with the forecasts, event information and joint delivery of JR-D (benchmark SR-D).
%   During a known event the step is planned by JR-D. Outside events the recovery is executed in two stages at
%   every step, both over the JR-D horizon from the measured state: stage 1 plans the computing schedule with
%   the BESS and TES charging held at their no-DR (TOU) schedule, so that the deferred work is caught up first
%   through the whole recovery channel; stage 2 fixes the busy GPUs of the current step and plans the storage
%   and IES, which recharge in the headroom that is left. This is the recovery order of independent recovery in
%   Proposition 2 (computing debt first, storage debt after) with the same information as JR-D.
par = ctx.par; t0 = st.t; ev = ctx.ev;
known = event_known(ctx, t0)';
if any(known & t0 >= [ev.s] & t0 <= [ev.e]), [u, info] = planner_jr(st, data, ctx); return; end
H = min(ctx.H, par.Tsim - t0 + 1); tt = t0:t0 + H - 1;
sc = make_scen(ctx.inp, par, ctx.base, t0, H, ctx);
opt = struct('milp', ctx.milp, 'nonant', true);
opt.active = event_activity(ctx, t0, sc.S, 'ce'); opt.visible = any(opt.active, 2);
[opt.terminal, opt.Eref_end, opt.Sref_end] = terminal_ref(ctx, t0 + H - 1);
o1 = opt; o1.ch_ub = ctx.ref.log.pch(tt);
o1.qtc_ub = ctx.ref.log.qtc(tt) + par.tes.loss * par.tes.Smax / par.tes.eta_c;   % standing loss of the tank stays covered
[P1, ix1] = build_model(par, st, sc, ev, o1);
s1 = solve_milp(P1, ctx.solver);
info.ok = s1.ok; info.time = s1.time; info.fallback = false;
if ~s1.ok, [u, ~] = planner_irr(st, data, ctx); info.fallback = true; return; end
o2 = opt; o2.y1 = [s1.x(ix1.Y{1}(1, 1)), s1.x(ix1.Y{2}(1, 1)), s1.x(ix1.Y{3}(1, 1))];
if ~isempty(ix1.Zc), o2.z1 = [s1.x(ix1.Zc{1}(1, 1)), s1.x(ix1.Zc{2}(1, 1)), s1.x(ix1.Zc{3}(1, 1))]; end
[P2, ix2] = build_model(par, st, sc, ev, o2);
s2 = solve_milp(P2, ctx.solver);
info.time = info.time + s2.time;
if ~s2.ok, [u, ~] = planner_irr(st, data, ctx); info.fallback = true; info.ok = false; return; end
u = first_step(s2.x, ix2);
info.sol = s2; info.ix = ix2;
end
