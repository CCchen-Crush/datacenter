function out = exp15_mechanism(ctx, root, cases)
%EXP15_MECHANISM  Recovery mechanism on typical days (module 3): time series of grid import, class
%   backlogs, BESS / TES state and the shared recovery headroom for the four strategies, the perfect-
%   information reference and the no-DR operation. cases: rows {scenario, C (MW), realisation (0 =
%   case day), tag}; e.g. a short interval case and a long interval contrast.
%   Writes results/ts15_<tag>_<strategy>.csv and results/exp15_mechanism.csv (one metrics row each).
S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; ...
     'JR', 'expected', 'JR-D'; 'JR', 'open', 'JR-oracle'; 'NoDR', 'open', 'NoDR'};
rows = []; rl = {}; hdr = {};
for i = 1:size(cases, 1)
    c = set_scenario(ctx, cases{i, 1}); c = apply_commit(c, cases{i, 2} * ones(1, numel(c.ev)));
    c = prepare_benchmarks(c, struct('verbose', false));
    if cases{i, 3} > 0, c = use_realization(c, cases{i, 3}); end
    for k = 1:size(S, 1)
        R = run_strategy(c, S{k, 1}, S{k, 2}); [row, hdr] = metrics_row(R.M);
        save_timeseries(fullfile(root, 'results', sprintf('ts15_%s_%s.csv', cases{i, 4}, strrep(strrep(S{k, 3}, '-', ''), '*', 's'))), R, c);
        rows = [rows; i, cases{i, 2}, cases{i, 3}, c.alpha_star, row]; %#ok<AGROW>
        rl{end+1} = sprintf('%s|%s', cases{i, 4}, S{k, 3}); %#ok<AGROW>
        fprintf('  exp15 %-10s %-9s ful=%6.2f full=%d/%d net_adj=%.0f\n', cases{i, 4}, S{k, 3}, 100 * R.M.fulfil_rate, ...
            R.M.n_full, R.M.n_called, R.M.net_cost_adj);
    end
end
write_csv(fullfile(root, 'results', 'exp15_mechanism.csv'), [{'case', 'C', 'realisation', 'alpha_star'}, hdr], rows, rl);
out.rows = rows; out.labels = rl;
end
