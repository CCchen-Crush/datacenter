function out = exp16_endogenous(ctx, root, Cs, N, tag)
%EXP16_ENDOGENOUS  Endogenous-commitment protocol (module 1, second protocol). Every strategy uses the
%   same day-ahead information (the S day-ahead scenario days) and the same objective (expected
%   comprehensive cost) to choose its own commitment, then operates with it on the N PAI test days.
%     back-test  uniform commitment C* = argmin over Cs of the strategy's mean cost on the day-ahead
%                scenarios (IR-O*: jointly with its static split, i.e. min over alpha of tune_alpha); the
%                full-delivery share on the scenarios is stored as well, so that the reliability-constrained
%                choice of Eq. (15) can be made for any rho (out-of-sample results: exp12 on the same days)
%     RA         recovery-aware two-stage stochastic commitment (dayahead_commit 'coupled'; event-wise
%                commitments, second stage = joint recovery model), operated by JR-D (proposed)
%     SE         conventional single-event capability assessment (dayahead_commit 'single'), operated
%                by IR-O* and IR-P (reference practice)
%   Writes results/exp16_dayahead<tag>.csv (expected day-ahead cost per strategy and C) and
%   results/exp16_endogenous<tag>.csv (one row per package, test day).
if nargin < 3 || isempty(Cs), Cs = 3:0.5:9; end
if nargin < 4 || isempty(N), N = 26; end
if nargin < 5, tag = ''; end
K = numel(ctx.ev); Sc = numel(ctx.sidx.flex);
S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'};
%% day-ahead: expected cost of each strategy on the day-ahead scenarios, for every uniform commitment
da = nan(numel(Cs), size(S, 1)); sh = da; astar = nan(numel(Cs), 1); t0 = tic;   % expected cost, full-delivery share
for j = 1:numel(Cs)
    c0 = apply_commit(ctx, Cs(j) * ones(1, K));
    [astar(j), tab] = tune_alpha(c0, 'expected', ctx.par.bench.alpha_grid);
    [da(j, 1), ja] = min(tab(:, 2)); sh(j, 1) = tab(ja, 5);
    c0.alpha_star = astar(j); c0.lambda_hr_da = dayahead_prices(c0);
    for k = 2:size(S, 1)
        v = zeros(Sc, 2);
        for s = 1:Sc, R = run_strategy(scenario_ctx(c0, s), S{k, 1}, S{k, 2}); v(s, :) = [R.M.net_cost_adj, R.M.all_full]; end
        da(j, k) = mean(v(:, 1)); sh(j, k) = mean(v(:, 2));
    end
    fprintf('  exp16%s day-ahead C=%4.1f alpha*=%.1f | expected cost (k) %s (%.0f min)\n', tag, Cs(j), astar(j), ...
        sprintf('%6.1f ', da(j, :) / 1000), toc(t0) / 60);
end
write_csv(fullfile(root, 'results', sprintf('exp16_dayahead%s.csv', tag)), ...
    [{'C', 'alpha_star'}, S(:, 3)', cellfun(@(x) ['full_' x], S(:, 3)', 'UniformOutput', false)], [Cs(:), astar, da, sh]);
%% commitment packages
[~, jb] = min(da, [], 1);
DA = dayahead_commit(ctx, 'coupled'); SE = dayahead_commit(ctx, 'single');
pk = {};
for k = 1:size(S, 1), pk(end+1, :) = {sprintf('BT|%s', S{k, 3}), Cs(jb(k)) * ones(1, K), k}; end %#ok<AGROW>
pk(end+1, :) = {'RA|JR-D', DA.C(:)', 4};
pk(end+1, :) = {'SE|IR-O*', SE.C(:)', 1};
pk(end+1, :) = {'SE|IR-P', SE.C(:)', 2};
fprintf('  exp16%s commitments: %s\n', tag, strjoin(cellfun(@(a, b) sprintf('%s %s', a, mat2str(round(b * 100) / 100)), pk(:, 1), pk(:, 2), 'UniformOutput', false), ' | '));
%% out-of-sample operation on the test days
rs = distinct_pai(ctx.inp.mc.label, N);
rows = []; hdr = {};
for p = 1:size(pk, 1)
    c0 = apply_commit(ctx, pk{p, 2}); k = pk{p, 3};
    if k <= 2, c0 = prepare_benchmarks(c0, struct('verbose', false)); end
    if ~isfield(c0, 'alpha_star'), c0.alpha_star = NaN; end
    for r = 1:numel(rs)
        cr = use_realization(c0, rs(r));
        R = run_strategy(cr, S{k, 1}, S{k, 2}); [row, hdr] = metrics_row(R.M);
        R0 = run_strategy(cr, 'NoDR');
        rows = [rows; p, pad3(pk{p, 2}), rs(r), c0.alpha_star, R0.M.net_cost_adj, row]; %#ok<AGROW>
    end
    q = rows(rows(:, 1) == p, :);
    fprintf('  exp16%s %-9s C=%-18s all-full %.2f benefit vs no-DR %.1f k (%.0f min)\n', tag, pk{p, 1}, mat2str(round(pk{p, 2} * 100) / 100), ...
        mean(q(:, 7 + find(strcmp(hdr, 'all_full')))), mean(q(:, 7) - q(:, 7 + find(strcmp(hdr, 'net_cost_adj')))) / 1000, toc(t0) / 60);
end
write_csv(fullfile(root, 'results', sprintf('exp16_endogenous%s.csv', tag)), ...
    [{'package', 'C1', 'C2', 'C3', 'realisation', 'alpha_star', 'nodr_net_cost_adj'}, hdr], rows);
write_csv(fullfile(root, 'results', sprintf('exp16_packages%s.csv', tag)), {'index'}, (1:size(pk, 1))', pk(:, 1));
out.rows = rows; out.hdr = hdr; out.packages = pk; out.dayahead = da;
end

function v = pad3(x)
v = [x(:)', nan(1, 3 - numel(x))];
end

function rs = distinct_pai(label, N)
key = cellfun(@(s) strtok(s, '_'), label, 'UniformOutput', false);
[~, first] = unique(key, 'first');
rs = sort(first(:))';
rs = rs(1:min(N, numel(rs)));
end
