function [alpha_star, tab] = tune_alpha(ctx, fmode, grid)
%TUNE_ALPHA  Day-ahead tuning of the static compute share alpha of the independent strategy IR-O:
%   alpha* = argmin over grid of the mean adjusted net cost of the IR-O controller (run with the
%   same forecasting mode it uses on the DR day) back-tested on the S day-ahead scenarios
%   (historical pool days). No information of the DR day itself is used.
if nargin < 2 || isempty(fmode), fmode = 'expected'; end
if nargin < 3 || isempty(grid), grid = ctx.par.bench.alpha_grid; end
S = numel(ctx.sidx.flex);
cs = cell(1, S); for s = 1:S, cs{s} = scenario_ctx(ctx, s); end
tab = zeros(numel(grid), 5);              % alpha, mean net_cost_adj, mean fulfil (%), share all valid, share all full
for i = 1:numel(grid)
    v = zeros(S, 4);
    for s = 1:S
        c = cs{s}; c.alpha = grid(i);
        R = run_strategy(c, 'IR-O', fmode);
        v(s, :) = [R.M.net_cost_adj, 100 * R.M.fulfil_rate, R.M.all_valid, R.M.all_full];
    end
    tab(i, :) = [grid(i), mean(v, 1)];
end
[~, j] = min(tab(:, 2));
alpha_star = grid(j);
end
