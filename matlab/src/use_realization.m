function ctx = use_realization(ctx, r)
%USE_REALIZATION  Replace the realised DR-day data by Monte-Carlo realisation r (forecasts, baseline,
%   scenarios and commitments are kept: they were fixed before the day).
mc = ctx.inp.mc;
ctx.inp.real.flex = mc.flex(:, :, r); ctx.inp.real.fix = mc.fix(:, r); ctx.inp.real.inf = mc.inf(:, r);
ctx.inp.real.pv = mc.pv(:, r); ctx.inp.real.cop = mc.cop(:, r);
ctx.inp.fc.cop = mc.cop(:, r);
end
