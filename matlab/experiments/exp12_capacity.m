function out = exp12_capacity(ctx, root, Cs, N, tag, S)
%EXP12_CAPACITY  Reliably deliverable consecutive-DR capacity (review issues 1-2): uniform commitment C
%   swept over Cs; for every C the benchmarks are re-tuned day-ahead and each strategy is run on the
%   first N Monte-Carlo realisations. For each strategy this gives the share of days on which all
%   events are valid, the mean fulfilment and the mean net cost, hence (i) the largest commitment that
%   is delivered on >= 95 % of the days and (ii) the commitment that maximises the expected profit.
if nargin < 3 || isempty(Cs), Cs = [4 5 6 7 8 9]; end
if nargin < 4 || isempty(N), N = 20; end
if nargin < 5, tag = ''; end
if nargin < 6 || isempty(S), S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR', 'expected', 'JR-D'}; end
N = min(N, ctx.inp.mc.N);
rows = []; hdr = {}; t0 = tic;
for C = Cs
    c0 = apply_commit(ctx, C * [1 1 1]);
    c0 = prepare_benchmarks(c0, struct('verbose', false));
    q = zeros(size(S, 1), 3);
    for i = 1:size(S, 1)
        v = zeros(N, 3);
        for r = 1:N
            c = use_realization(c0, r);
            R = run_strategy(c, S{i, 1}, S{i, 2});
            [row, hdr] = metrics_row(R.M);
            rows = [rows; C, r, i, c0.alpha_star, row]; %#ok<AGROW>
            v(r, :) = [100 * R.M.fulfil_rate, R.M.all_valid, R.M.net_cost_adj];
        end
        q(i, :) = mean(v, 1);
    end
    fprintf('  exp12%s C=%g alpha*=%.1f | fulfil %s| all-valid %s| net_adj(k) %s (%.0f min)\n', tag, C, c0.alpha_star, ...
        sprintf('%5.1f ', q(:, 1)), sprintf('%4.2f ', q(:, 2)), sprintf('%5.0f ', q(:, 3) / 1000), toc(t0) / 60);
end
write_csv(fullfile(root, 'results', sprintf('exp12_capacity%s.csv', tag)), [{'C', 'realisation', 'strategy', 'alpha_star'}, hdr], rows);
write_csv(fullfile(root, 'results', sprintf('exp12_strategies%s.csv', tag)), {'index'}, (1:size(S, 1))', S(:, 3));
out.rows = rows; out.hdr = hdr;
end
