%SMOKE_REV  Smoke test of the revised strategies and metrics (review round 1).
here = fileparts(mfilename('fullpath')); addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
root = dcdr_setup_paths(); par = dcdr_params();
t = tic; ctx = setup_case(par); fprintf('setup %.1fs, Pcap %.2f, alpha %.2f\n', toc(t), ctx.d.Pcap, ctx.alpha);
c = apply_commit(ctx, [6 6 6]);
t = tic; [lam, info] = dayahead_prices(c); fprintf('lambda: max %.0f, mean %.0f (%.1fs)\n', max(lam), mean(lam), toc(t));
c.lambda_hr_da = lam; c.alpha_star = 0.9;
S = {'NoDR','open'; 'IR-R','rule'; 'IR-O','expected'; 'IR-O*','expected'; 'IR-P','expected'; 'JR-M','expected'; 'JR','expected'; 'JR','open'};
for i = 1:size(S,1)
    t = tic; R = run_strategy(c, S{i,1}, S{i,2}); M = R.M;
    fprintf('%-6s %-9s ful=%6.2f valid=%d/%d rb=%.2f rb6=%.2f pre=%.2f preN=%.2f payG=%.2f payA=%.2f termB=%.0f net=%.0f adj=%.0f exrb=%.0f co2=%.1f (%.0fs)\n', ...
        S{i,1}, S{i,2}, 100*M.fulfil_rate, M.n_valid, M.n_called, M.max_rebound, M.max_rebound6, M.preload_mean, M.preload_vs_nodr, ...
        M.payback_gap, M.payback_after, M.term_backlog, M.net_cost, M.net_cost_adj, M.net_cost_excl_rb, M.co2, toc(t));
end
