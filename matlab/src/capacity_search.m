function [Cr, E] = capacity_search(ctx, strat, rho, o)
%CAPACITY_SEARCH  Firm capacity C_rho of one strategy by bisection over the uniform commitment C.
%   ctx   case with the event scenario and the system parameters already set
%   strat {name, forecast mode, label}; rho target reliability (share of test days with full delivery)
%   o     .lo, .hi bracket (MW), .tol resolution (MW), .rs test realisations
%   At every evaluated C the benchmarks are prepared day-ahead (IR-O*: split tuned on the day-ahead
%   scenarios; IR-P: channel price). The evaluation stops as soon as more days have failed than rho
%   allows. The share of days with full delivery is non-increasing in C for the joint strategies; for
%   the benchmarks the bisection returns the reliability boundary it brackets.
%   Returns Cr (NaN if the share at o.lo is below rho, o.hi if it is reached at o.hi) and the evaluated
%   points E = [C, share of days with full delivery (an upper bound if stopped early), days evaluated,
%   stopped early].
nfail_max = floor((1 - rho) * numel(o.rs) + 1e-9);
E = zeros(0, 4);
[ok, row] = evaluate(ctx, strat, o.lo, o.rs, nfail_max); E(end + 1, :) = row;
if ~ok, Cr = NaN; return; end
[ok, row] = evaluate(ctx, strat, o.hi, o.rs, nfail_max); E(end + 1, :) = row;
if ok, Cr = o.hi; return; end
lo = o.lo; hi = o.hi;
while hi - lo > o.tol + 1e-9
    mid = o.tol * round((lo + hi) / 2 / o.tol);
    if mid <= lo + 1e-9 || mid >= hi - 1e-9, break; end
    [ok, row] = evaluate(ctx, strat, mid, o.rs, nfail_max); E(end + 1, :) = row;
    if ok, lo = mid; else, hi = mid; end
end
Cr = lo;
end

function [ok, row] = evaluate(ctx, strat, C, rs, nfail_max)
c0 = apply_commit(ctx, C * ones(1, numel(ctx.ev)));
switch strat{1}
    case 'IR-O*', c0.alpha_star = tune_alpha(c0, 'expected', ctx.par.bench.alpha_grid);
    case 'IR-P',  c0.lambda_hr_da = dayahead_prices(c0);
end
nf = 0; n = 0;
for j = 1:numel(rs)
    R = run_strategy(use_realization(c0, rs(j)), strat{1}, strat{2});
    n = n + 1; nf = nf + (R.M.all_full < 0.5);
    if nf > nfail_max, break; end
end
ok = nf <= nfail_max;
row = [C, 1 - nf / numel(rs), n, nf > nfail_max];
end
