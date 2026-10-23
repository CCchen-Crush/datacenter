function out = exp18_history(ctx, root, Cs, tag, S, active, alpha_tab)
%EXP18_HISTORY  Closed-loop back-test of uniform commitments on the historical days of the day-ahead pool
%   (the weekdays before the DR day). The commitments Cs are visited in increasing order; for every C the
%   benchmarks a strategy needs are prepared day-ahead as on the DR day (IR-O*: split tuned on the day-ahead
%   scenarios; IR-P: channel price), and every strategy is run in closed loop on every historical day on which
%   it has delivered every smaller commitment in full. The capability xi_d of a strategy on day d (largest C
%   delivered in full for all C' <= C) feeds the sample-average and the Wasserstein distributionally robust
%   commitment (Proposition 3, tools/paper_numbers.py); a day is not run again above its first failure.
%   Writes results/exp18_history<tag>.csv (one row per C, day, strategy run) and exp18_strategies<tag>.csv
%   after every commitment. active (indices into S, default all) selects the strategies run in this part;
%   the strategy index in the output always refers to the full list S, so parts can be concatenated.
%   alpha_tab = [C, alpha*] rows reuses splits already tuned day-ahead for the same scenario (Exp12).
if nargin < 3 || isempty(Cs), Cs = 1:0.5:9; end
if nargin < 4, tag = ''; end
if nargin < 5 || isempty(S)
    S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'};
end
if nargin < 6 || isempty(active), active = 1:size(S, 1); end
if nargin < 7, alpha_tab = []; end
D = size(ctx.inp.pool.flex, 3); K = numel(ctx.ev);
alive = false(D, size(S, 1)); alive(:, active) = true;
rows = []; hdr = {}; t0 = tic;
write_csv(fullfile(root, 'results', sprintf('exp18_strategies%s.csv', tag)), {'index'}, (1:size(S, 1))', S(:, 3));
for C = sort(Cs)
    if ~any(alive(:)), break; end
    c0 = bench_prepare(apply_commit(ctx, C * ones(1, K)), S(any(alive, 1), 1), C, alpha_tab);
    for dd = 1:D
        if ~any(alive(dd, :)), continue; end
        c = history_ctx(c0, dd);
        for i = find(alive(dd, :))
            R = run_strategy(c, S{i, 1}, S{i, 2});
            [row, hdr] = metrics_row(R.M);
            rows = [rows; C, dd, i, c0.alpha_star, row]; %#ok<AGROW>
            alive(dd, i) = R.M.all_full > 0.5;
        end
    end
    fprintf('  exp18%s C=%4.1f alpha*=%.1f | full at every C'' <= C on %d historical days %s (%.0f min)\n', tag, C, ...
        c0.alpha_star, D, sprintf('%4.2f ', mean(alive(:, active), 1)), toc(t0) / 60);
    write_csv(fullfile(root, 'results', sprintf('exp18_history%s.csv', tag)), [{'C', 'day', 'strategy', 'alpha_star'}, hdr], rows);
end
out.rows = rows; out.hdr = hdr;
end
