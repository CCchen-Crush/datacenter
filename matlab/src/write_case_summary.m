function write_case_summary(ctx, root)
%WRITE_CASE_SUMMARY  Key case data (baseline, prices, PV, COP, load shares) for the paper's case section.
par = ctx.par; inp = ctx.inp; T = par.Tsim; h = (0:T-1)' * par.dt;
M = [h, ctx.base, inp.price, inp.real.pv, inp.real.cop, inp.real.T, inp.real.inf, inp.real.fix, inp.real.flex, ...
     ctx.ref.log.pg, ctx.ref.log.pit];
write_csv(fullfile(root, 'results', 'case_profiles.csv'), {'hour', 'baseline', 'price', 'pv', 'cop', 'temp', 'gpu_inf', ...
    'gpu_flex0', 'gpu_c1', 'gpu_c2', 'gpu_c3', 'pg_noDR', 'pit_noDR'}, M);
fid = fopen(fullfile(root, 'results', 'case_summary.txt'), 'w');
fprintf(fid, 'Pdesign %.3f MW, typical peak %.3f MW, Pcap %.3f MW (gamma %.2f)\n', ctx.d.Pdesign, par.cap.Pbase_peak, ctx.d.Pcap, par.cap.gamma);
fprintf(fid, 'alpha (IR compute share) %.3f, compute capability %.2f MW, storage capability %.2f MW\n', ctx.alpha, ctx.cap_comp, ctx.cap_stor);
fprintf(fid, 'flex scale %.4f, PAI DR day %d, baseline days %s, Azure DR day %s\n', inp.info.scale_flex, inp.info.pai_day, mat2str(inp.info.pai_prev), inp.info.azure_date);
u = (sum(inp.real.flex, 2) + inp.real.fix + inp.real.inf) / par.it.Ngpu;
fprintf(fid, 'GPU utilisation DR day: mean %.3f max %.3f; IT power mean %.2f MW; facility no-DR mean %.2f MW\n', mean(u(1:96)), max(u(1:96)), mean(ctx.ref.log.pit(1:96)), mean(ctx.ref.log.pg(1:96)));
fprintf(fid, 'PUE (no-DR, day D): %.3f\n', sum(ctx.ref.log.pg(1:96) + ctx.ref.log.pgt(1:96) + ctx.ref.log.ppv(1:96) + ctx.ref.log.pdis(1:96) - ctx.ref.log.pch(1:96)) / sum(ctx.ref.log.pit(1:96)));
for k = 1:numel(ctx.ev)
    fprintf(fid, 'event %d: %.2f-%.2f h, price %.0f CNY/MWh, baseline mean %.2f MW\n', k, (ctx.ev(k).s-1)*par.dt, ctx.ev(k).e*par.dt, ctx.ev(k).price, mean(ctx.base(ctx.ev(k).s:ctx.ev(k).e)));
end
fclose(fid);
end
