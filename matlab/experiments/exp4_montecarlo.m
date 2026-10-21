function out = exp4_montecarlo(ctx, root, C, N, tag, S)
%EXP4_MONTECARLO  Monte-Carlo closed-loop test. Realised compute arrivals, inference load, PV and
%   temperature differ from the forecasts (52 realisations: later PAI weekdays x hot days x Azure days);
%   commitments, baseline, scenarios, the tuned split alpha* and the IR-P price signal are fixed
%   day-ahead. Events with call probability < 1 are drawn per realisation (use_realization).
%   Writes results/exp4_<tag>.csv: one row per (realisation, strategy) with all metrics.
if nargin < 4 || isempty(N), N = ctx.inp.mc.N; end
if nargin < 6 || isempty(S), S = bench_list('mc'); end
N = min(N, ctx.inp.mc.N);
c0 = apply_commit(ctx, C);
c0 = prepare_benchmarks(c0);
rows = []; hdr = {};
t0 = tic;
for r = 1:N
    c = use_realization(c0, r);
    called = [c.ev.called];
    q = zeros(size(S, 1), 3);
    for i = 1:size(S, 1)
        R = run_strategy(c, S{i, 1}, S{i, 2});
        [row, hdr] = metrics_row(R.M);
        rows = [rows; r, i, double(called), row]; %#ok<AGROW>
        q(i, :) = [100 * R.M.fulfil_rate, R.M.n_valid, R.M.net_cost_adj / 1000];
    end
    fprintf('  exp4%s r=%2d called=%s fulfil %s| valid %s| net(k) %s (%.0f min)\n', tag, r, sprintf('%d', called), ...
        sprintf('%5.1f ', q(:, 1)), sprintf('%d ', q(:, 2)), sprintf('%5.0f ', q(:, 3)), toc(t0) / 60);
end
K = numel(ctx.ev);
ch = arrayfun(@(k) sprintf('called_E%d', k), 1:K, 'UniformOutput', false);
write_csv(fullfile(root, 'results', sprintf('exp4%s.csv', tag)), [{'realisation', 'strategy'}, ch, hdr], rows);
write_csv(fullfile(root, 'results', sprintf('exp4%s_strategies.csv', tag)), {'index'}, (1:size(S, 1))', S(:, 3));
write_csv(fullfile(root, 'results', sprintf('exp4%s_bench.csv', tag)), {'alpha_star', 'C1', 'C2', 'C3'}, [c0.alpha_star, [c0.ev.C]]);
out.rows = rows; out.hdr = hdr; out.S = S;
end
