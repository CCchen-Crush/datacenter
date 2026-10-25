function out = exp24_timing(ctx, root, scen, C)
%EXP24_TIMING  Per-step solver time of the controllers on the DR day (Table 5): one closed-loop day of every
%   strategy at the uniform commitment C. Writes results/exp24_timing.csv (strategy, mean and maximum solver
%   time per MPC step, solver time per day, steps).
if nargin < 3 || isempty(scen), scen = 'S1'; end
if nargin < 4 || isempty(C), C = 7; end
c = set_scenario(ctx, scen); c0 = apply_commit(c, C * ones(1, numel(c.ev)));
S = {'JR', 'JR-D'; 'JR-M', 'JR-M'; 'IR-O*', 'IR-O*'; 'IR-PD', 'IR-PD'; 'SR-D', 'SR-D'};
c0.alpha_star = tune_alpha(c0, 'expected', ctx.par.bench.alpha_grid);
rows = zeros(size(S, 1), 4);
for i = 1:size(S, 1)
    R = run_strategy(c0, S{i, 1}, 'expected'); st = R.log.solve_time(:);
    rows(i, :) = [mean(st), max(st), sum(st), numel(st)];
    fprintf('  exp24 %-6s solver time per step mean %.3f s, max %.3f s, per day %.1f s (%d steps)\n', S{i, 2}, rows(i, :));
end
write_csv(fullfile(root, 'results', 'exp24_timing.csv'), {'mean_step_s', 'max_step_s', 'day_s', 'steps'}, rows, S(:, 2)');
out.rows = rows;
end
