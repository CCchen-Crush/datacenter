function out = exp9_price(ctx, root, C, prices, kappas)
%EXP9_PRICE  Sensitivity to the DR unit price (day-ahead price cap 1-3 CNY/kWh in the Jiangsu rules)
%   and to the shortfall assessment coefficient kappa (review issue 4c). Uniform commitments,
%   benchmarks re-tuned for every combination.
if nargin < 3 || isempty(C), C = [6 6 6]; end
if nargin < 4 || isempty(prices), prices = [1000 2000 3000]; end
if nargin < 5 || isempty(kappas), kappas = [0.5 1 2]; end
S = bench_list('core');
rows = []; hdr = {};
for p = prices
    for kp = kappas
        c = ctx; c.par.dr.price_da = p; c.par.dr.kappa_dev = kp;
        for k = 1:numel(c.ev), c.ev(k).price = c.ev(k).price / ctx.par.dr.price_da * p; end
        c = apply_commit(c, C);
        c = prepare_benchmarks(c, struct('grid', [0.4 0.6 0.8 1.0]));
        [r, hdr] = run_list(c, S, sprintf('exp9 p=%4g k=%3.1f ', p, kp));
        rows = [rows; repmat([p, kp], size(r, 1), 1), (1:size(r, 1))', repmat(c.alpha_star, size(r, 1), 1), r]; %#ok<AGROW>
    end
end
write_csv(fullfile(root, 'results', 'exp9_price.csv'), [{'price', 'kappa', 'strategy', 'alpha_star'}, hdr], rows);
write_csv(fullfile(root, 'results', 'exp9_strategies.csv'), {'index'}, (1:size(S, 1))', S(:, 3));
out.rows = rows; out.hdr = hdr;
end
