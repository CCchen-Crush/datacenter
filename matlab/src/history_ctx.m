function c = history_ctx(ctx, d)
%HISTORY_CTX  Context in which the realised day is historical day d of the day-ahead pool (the weekdays
%   before the DR day): its deferrable and fixed training load, an inference day of the pool and the PV and
%   chiller COP of a pool weather day. Commitments, baseline, forecasts and the day-ahead preparation of the
%   benchmarks are those of ctx. Used for the closed-loop back-test of commitments (exp18).
c = ctx;
ni = size(ctx.inp.pool.inf, 2); nw = size(ctx.inp.pool.pv, 2); w = mod(d - 1, nw) + 1;
c.inp.real.flex = ctx.inp.pool.flex(:, :, d);
c.inp.real.fix  = ctx.inp.pool.fix(:, d);
c.inp.real.inf  = ctx.inp.pool.inf(:, mod(d - 1, ni) + 1);
c.inp.real.pv   = max(ctx.inp.pool.pv(:, w), 0);
c.inp.real.cop  = ctx.inp.pool.cop(:, w);
for k = 1:numel(c.ev)
    p = c.ev(k).prob;
    if p >= 1, c.ev(k).called = true; continue; end
    u = mod((d - 0.5) * 0.6180339887498949 + 0.37 * (k - 1), 1);
    c.ev(k).called = u < p;
end
c.ref_eval = run_nodr(c.par, c.inp, c.base);
end
