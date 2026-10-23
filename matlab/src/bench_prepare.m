function c = bench_prepare(c, names, C, alpha_tab)
%BENCH_PREPARE  Day-ahead preparation of the benchmarks among the strategies names (after apply_commit):
%   IR-O* gets the static split alpha* tuned on the day-ahead scenarios (tune_alpha), or the value of
%   alpha_tab = [C, alpha*] rows when C is listed (splits tuned before for the same scenario; tune_alpha is
%   deterministic); IR-P gets the day-ahead channel price (dayahead_prices). Others need no preparation.
c.alpha_star = NaN;
if any(strcmp(names, 'IR-O*'))
    k = [];
    if nargin >= 4 && ~isempty(alpha_tab), k = find(abs(alpha_tab(:, 1) - C) < 1e-9, 1); end
    if isempty(k), c.alpha_star = tune_alpha(c, 'expected', c.par.bench.alpha_grid); else, c.alpha_star = alpha_tab(k, 2); end
end
if any(strcmp(names, 'IR-P')), c.lambda_hr_da = dayahead_prices(c); end
end
