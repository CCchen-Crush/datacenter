function ctx = prepare_benchmarks(ctx, opts)
%PREPARE_BENCHMARKS  Day-ahead preparation of the strengthened benchmarks (review issue 2):
%   ctx.alpha_star   tuned static split of IR-O*   (tune_alpha, back-test on day-ahead scenarios)
%   ctx.lambda_hr_da price signal of IR-P          (dayahead_prices, duals of the day-ahead joint plan)
%   Call after the commitments are applied (apply_commit), because both depend on them.
if nargin < 2, opts = struct(); end
if ~isfield(opts, 'fmode'), opts.fmode = 'expected'; end
if ~isfield(opts, 'grid'), opts.grid = ctx.par.bench.alpha_grid; end
if ~isfield(opts, 'verbose'), opts.verbose = true; end
t = tic;
[ctx.alpha_star, ctx.alpha_tab] = tune_alpha(ctx, opts.fmode, opts.grid);
[ctx.lambda_hr_da, info] = dayahead_prices(ctx);
ctx.lambda_info = info;
if opts.verbose
    fprintf('  benchmarks: alpha* = %.2f (static share %.2f), max lambda_hr = %.0f CNY/MWh (%.0fs)\n', ...
        ctx.alpha_star, ctx.alpha, max(ctx.lambda_hr_da), toc(t));
end
end
