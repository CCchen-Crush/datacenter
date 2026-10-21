function [a_best, tab] = alpha_hindsight(ctx, grid)
%ALPHA_HINDSIGHT  Best static compute share of IR-O chosen with hindsight on the evaluated day itself
%   (open-loop, perfect information). An upper bound of what any static split can achieve; used in the
%   perfect-information sensitivity studies so that the independent benchmark is as strong as possible.
if nargin < 2 || isempty(grid), grid = ctx.par.bench.alpha_grid; end
tab = zeros(numel(grid), 3);
for i = 1:numel(grid)
    c = ctx; c.alpha = grid(i);
    R = run_strategy(c, 'IR-O', 'open');
    tab(i, :) = [grid(i), R.M.net_cost_adj, 100 * R.M.fulfil_rate];
end
[~, j] = min(tab(:, 2)); a_best = grid(j);
end
