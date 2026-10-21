function c = scenario_ctx(ctx, s)
%SCENARIO_CTX  Context in which the "realised" day is day-ahead scenario s (a historical pool day).
%   Used for day-ahead tuning of the benchmarks: only information available before the DR day.
%   Events with prob < 1 are called in the scenarios given by scen_called (same tree as the MPC).
c = ctx; S = numel(ctx.sidx.flex);
c.inp.real.flex = ctx.inp.pool.flex(:, :, ctx.sidx.flex(s));
c.inp.real.fix  = ctx.inp.pool.fix(:, ctx.sidx.flex(s));
c.inp.real.inf  = ctx.inp.pool.inf(:, ctx.sidx.inf(s));
c.inp.real.pv   = max(ctx.inp.pool.pv(:, ctx.sidx.pv(s)), 0);
for k = 1:numel(c.ev)
    if c.ev(k).prob >= 1, c.ev(k).called = true; else, w = scen_called(c.ev(k).prob, S); c.ev(k).called = w(s); end
end
c.ref_eval = run_nodr(c.par, c.inp, c.base);
end
