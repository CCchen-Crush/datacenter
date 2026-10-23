function ctx = use_realization(ctx, r)
%USE_REALIZATION  Replace the realised DR-day data by Monte-Carlo realisation r (forecasts, baseline,
%   scenarios and commitments are kept: they were fixed before the day). The no-DR reference on the
%   realised data is recomputed (for the true-reduction / payback metrics), and events that are only
%   called with probability prob < 1 are drawn with a deterministic low-discrepancy sequence, so that
%   a fraction ~prob of the realisations calls them (reproducible without a random generator).
mc = ctx.inp.mc;
ctx.inp.real.flex = mc.flex(:, :, r); ctx.inp.real.fix = mc.fix(:, r); ctx.inp.real.inf = mc.inf(:, r);
ctx.inp.real.pv = mc.pv(:, r); ctx.inp.real.cop = mc.cop(:, r);   % the COP forecast stays the day-ahead one
for k = 1:numel(ctx.ev)
    p = ctx.ev(k).prob;
    if p >= 1, ctx.ev(k).called = true; continue; end
    u = mod((r - 0.5) * 0.6180339887498949 + 0.37 * (k - 1), 1);
    ctx.ev(k).called = u < p;
end
ctx.ref_eval = run_nodr(ctx.par, ctx.inp, ctx.base);
end
