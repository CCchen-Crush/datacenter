function out = exp19_hindsight(ctx, root, Cs, alphas, tag, N)
%EXP19_HINDSIGHT  Upper bound of independent recovery with a static split: on every test day and for every
%   uniform commitment C the IR-O controller is run with the splits alpha of the grid until one delivers
%   every event in full (the split tuned day-ahead, alpha*, is tried first). A day on which no split
%   succeeds cannot be delivered by any static split, so the share of successful days bounds IR-O* from
%   above (best split in hindsight). Writes results/exp19_hindsight<tag>.csv (one row per C, day, split tried).
if nargin < 3 || isempty(Cs), Cs = [1 2 3 4 5 6 7 7.5]; end
if nargin < 4 || isempty(alphas), alphas = 0.2:0.2:1.0; end
if nargin < 5, tag = ''; end
if nargin < 6 || isempty(N), N = 26; end
rs = test_days(ctx, N); K = numel(ctx.ev);
rows = []; hdr = {}; t0 = tic;
for C = Cs
    c0 = apply_commit(ctx, C * ones(1, K));
    astar = tune_alpha(c0, 'expected', ctx.par.bench.alpha_grid);
    order = [astar, alphas(abs(alphas - astar) > 1e-9)];
    best = zeros(numel(rs), 1);
    for j = 1:numel(rs)
        cr = use_realization(c0, rs(j));
        for a = order
            c = cr; c.alpha = a;
            R = run_strategy(c, 'IR-O', 'expected');
            [row, hdr] = metrics_row(R.M);
            rows = [rows; C, rs(j), a, astar, row]; %#ok<AGROW>
            if R.M.all_full > 0.5, best(j) = 1; break; end
        end
    end
    fprintf('  exp19%s C=%4.1f alpha*=%.1f | full delivery with the best split in hindsight on %.2f of the days (%.0f min)\n', ...
        tag, C, astar, mean(best), toc(t0) / 60);
end
write_csv(fullfile(root, 'results', sprintf('exp19_hindsight%s.csv', tag)), [{'C', 'realisation', 'alpha', 'alpha_star'}, hdr], rows);
out.rows = rows; out.hdr = hdr;
end
