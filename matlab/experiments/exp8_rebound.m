function out = exp8_rebound(ctx, root, C, crbs)
%EXP8_REBOUND  Rebound assessment as a policy parameter (review issue 1): sweep c_rb and trace, for each
%   strategy, fulfilment, rebound (in-window and window independent) and the cost under the Jiangsu
%   rules alone (net_cost_excl_rb). The pairs (rebound, cost) form each strategy's trade-off curve;
%   a curve that lies below-left dominates. Benchmarks are re-tuned for every c_rb.
if nargin < 3 || isempty(C), C = [6 6 6]; end
if nargin < 4 || isempty(crbs), crbs = [0 500 1000 2000 3000 4000 6000]; end
S = [bench_list('core'); {'JR', 'open', 'JR-oracle'}];
rows = []; hdr = {};
for i = 1:numel(crbs)
    c = ctx; c.par.dr.c_rb = crbs(i);
    c = apply_commit(c, C);
    c = prepare_benchmarks(c);
    [r, hdr] = run_list(c, S, sprintf('exp8 c_rb=%-5g ', crbs(i)));
    rows = [rows; repmat(crbs(i), size(r, 1), 1), (1:size(r, 1))', repmat(c.alpha_star, size(r, 1), 1), r]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', 'exp8_rebound.csv'), [{'c_rb', 'strategy', 'alpha_star'}, hdr], rows);
write_csv(fullfile(root, 'results', 'exp8_strategies.csv'), {'index'}, (1:size(S, 1))', S(:, 3));
out.rows = rows; out.hdr = hdr; out.S = S;
end
