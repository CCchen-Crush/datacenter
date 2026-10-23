function out = exp18_history(ctx, root, Cs, tag, S)
%EXP18_HISTORY  Closed-loop back-test of uniform commitments on the historical days of the day-ahead pool
%   (the weekdays before the DR day). For every commitment C the benchmarks are prepared day-ahead as on
%   the DR day, and every strategy is run in closed loop on every historical day. The capability xi_d of a
%   strategy on day d (largest C delivered in full for all C' <= C) feeds the sample-average and the
%   Wasserstein distributionally robust commitment (Proposition 3, tools/paper_numbers.py).
%   Writes results/exp18_history<tag>.csv (one row per C, day, strategy) and exp18_strategies<tag>.csv.
if nargin < 3 || isempty(Cs), Cs = 1:0.5:9; end
if nargin < 4, tag = ''; end
if nargin < 5 || isempty(S)
    S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'};
end
D = size(ctx.inp.pool.flex, 3); K = numel(ctx.ev);
rows = []; hdr = {}; t0 = tic;
for C = Cs
    c0 = apply_commit(ctx, C * ones(1, K));
    c0 = prepare_benchmarks(c0, struct('verbose', false));
    v = zeros(D, size(S, 1));
    for dd = 1:D
        c = history_ctx(c0, dd);
        for i = 1:size(S, 1)
            R = run_strategy(c, S{i, 1}, S{i, 2});
            [row, hdr] = metrics_row(R.M);
            rows = [rows; C, dd, i, c0.alpha_star, row]; %#ok<AGROW>
            v(dd, i) = R.M.all_full;
        end
    end
    fprintf('  exp18%s C=%4.1f alpha*=%.1f | all-full on %d historical days %s (%.0f min)\n', tag, C, c0.alpha_star, D, ...
        sprintf('%4.2f ', mean(v, 1)), toc(t0) / 60);
end
write_csv(fullfile(root, 'results', sprintf('exp18_history%s.csv', tag)), [{'C', 'day', 'strategy', 'alpha_star'}, hdr], rows);
write_csv(fullfile(root, 'results', sprintf('exp18_strategies%s.csv', tag)), {'index'}, (1:size(S, 1))', S(:, 3));
out.rows = rows; out.hdr = hdr;
end
