function [G, sol, ix] = max_deliverable(ctx, st, evlist)
%MAX_DELIVERABLE  Largest constant reduction deliverable in the event(s) with mode 'max',
%   from state st, with all task deadlines met (no lateness) and the connection limit respected.
%   evlist: event struct array (modes 'hard' / 'max' / 'none'). Perfect information.
par = ctx.par; T = par.Tsim; t0 = st.t;
st = state_fit_events(st, numel(evlist));
c = ctx; c.fmode = 'oracle';
sc = make_scen(ctx.inp, par, ctx.base, t0, T - t0 + 1, c);
opt = struct('milp', false, 'visible', true(numel(evlist),1), 'no_late', true, 'terminal', false);
[P, ix] = build_model(par, st, sc, evlist, opt);
P.ub(ix.POV(:)) = 0;                       % connection limit is hard here
sol = solve_milp(P, ctx.solver);
G = NaN;
if sol.ok
    k = find(strcmp({evlist.mode}, 'max'), 1);
    G = sol.x(ix.ev(k).C);
end
end
