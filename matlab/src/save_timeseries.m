function save_timeseries(file, R, ctx)
%SAVE_TIMESERIES  Write the main time series of a run to CSV.
L = R.log; T = ctx.par.Tsim; h = ((0:T-1)' * ctx.par.dt);
hdr = {'hour', 'base', 'pg', 'pit', 'pch', 'pdis', 'E', 'S', 'pgt', 'qac', 'qec', 'qtc', 'qtd', 'ppv', ...
       'y1', 'y2', 'y3', 'B1', 'B2', 'B3', 'inf', 'price', 'Pcap', 'a1', 'a2', 'a3', 'fix', 'cop', 'overdue'};
% a1..a3: nominal (arrival) busy GPUs of the deferrable classes on the realised day, for the catch-up power
M = [h, ctx.base, L.pg, L.pit, L.pch, L.pdis, L.E, L.S, L.pgt, L.qac, L.qec, L.qtc, L.qtd, L.ppv, ...
     L.y, L.backlog, L.inf, ctx.inp.price, ctx.d.Pcap * ones(T,1), ctx.inp.real.flex(1:T, :), ctx.inp.real.fix(1:T), L.cop, L.overdue];
write_csv(file, hdr, M);
end
