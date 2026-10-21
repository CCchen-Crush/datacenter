here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
par = dcdr_params();
tic; ctx = setup_case(par); fprintf("setup %.1fs, Pcap=%.2f MW (design %.2f), alpha=%.2f, cap_comp=%.2f cap_stor=%.2f\n", toc, ctx.d.Pcap, ctx.d.Pdesign, ctx.alpha, ctx.cap_comp, ctx.cap_stor);
b = ctx.base; fprintf('baseline: min %.2f mean %.2f max %.2f; at events: %s\n', min(b(1:96)), mean(b(1:96)), max(b(1:96)), mat2str(round([mean(b(69:72)) mean(b(77:80)) mean(b(85:88))]*100)/100));
names = {'NoDR', 'IR-R', 'IR-O', 'JR'};
for i = 1:numel(names)
    tic; R = run_strategy(ctx, names{i}, 'open'); M = R.M;
    fprintf('%-5s t=%5.1fs fulfil=%.3f valid=%d red=%s rb=%s maxRb=%.2f Estart=%s cost_op=%.0f pay=%.0f net=%.0f late=%.1f peak=%.2f viol=%.3f\n', ...
        names{i}, toc, M.fulfil_rate, M.n_valid, mat2str(round(M.avg_red'*100)/100), mat2str(round(M.rebound'*100)/100), M.max_rebound, ...
        mat2str(round(M.E_start'*10)/10), M.cost_op, M.dr_pay, M.net_cost, M.lateness, M.peak_grid, M.cap_violation);
end
