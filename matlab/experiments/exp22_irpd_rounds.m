function out = exp22_irpd_rounds(ctx, root, scen, C, rs, Ks, tag)
%EXP22_IRPD_ROUNDS  Convergence check of the iterative price coordination IR-PD: the same operating days and uniform
%   commitment C are run with K rounds of price exchange per step (Ks, damping 0.5, the second half of the rounds
%   averaged) and with JR-D for reference. Writes results/exp22_irpd_rounds<tag>.csv (one row per day and K; K = 0 is JR-D).
if nargin < 7, tag = ''; end
c0 = apply_commit(set_scenario(ctx, scen), C * ones(1, numel(set_scenario(ctx, scen).ev)));
rows = []; hdr = {}; t0 = tic;
for j = 1:numel(rs)
    c = use_realization(c0, rs(j));
    R = run_strategy(c, 'JR', 'expected'); [row, hdr] = metrics_row(R.M);
    rows = [rows; rs(j), 0, row]; %#ok<AGROW>
    for K = Ks
        c.irpd = struct('K', K, 'beta', 0.5, 'k0', floor(K / 2) + 1);
        R = run_strategy(c, 'IR-PD', 'expected'); [row, hdr] = metrics_row(R.M);
        rows = [rows; rs(j), K, row]; %#ok<AGROW>
        fprintf('  exp22%s %s C=%.1f day %d K=%d: red %.2f / %.2f, all-full %d (%.0f min)\n', tag, scen, C, rs(j), K, R.M.avg_red(1), ...
            R.M.avg_red(2), R.M.all_full, toc(t0) / 60);
    end
    write_csv(fullfile(root, 'results', sprintf('exp22_irpd_rounds%s.csv', tag)), [{'realisation', 'K'}, hdr], rows);
end
out.rows = rows; out.hdr = hdr;
end
