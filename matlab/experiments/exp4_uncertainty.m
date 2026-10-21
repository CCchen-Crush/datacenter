function out = exp4_uncertainty(ctx, root, DA, N)
%EXP4_UNCERTAINTY  Monte-Carlo closed-loop test: realised compute arrivals, inference load, PV and
%   temperature differ from forecasts; commitments, baseline and scenarios fixed day-ahead.
if nargin < 4, N = ctx.inp.mc.N; end
N = min(N, ctx.inp.mc.N);
S = {'IR-R', 'rule'; 'IR-O', 'expected'; 'JR', 'expected'; 'JR', 'scenario'};
c0 = apply_commit(ctx, DA.C, DA); c0.all_visible = true;
rows = [];
for r = 1:N
    c = use_realization(c0, r);
    for i = 1:size(S, 1)
        R = run_strategy(c, S{i, 1}, S{i, 2}); M = R.M;
        rows = [rows; r, i, 100 * M.fulfil_rate, M.n_valid, M.max_rebound, M.net_cost, M.cost_op, M.dr_pay, M.lateness, M.cap_violation]; %#ok<AGROW>
    end
    q = rows(end-3:end, :);
    fprintf('  exp4 r=%2d fulfil %5.1f/%5.1f/%5.1f/%5.1f  valid %d/%d/%d/%d  net %.0f/%.0f/%.0f/%.0f\n', r, q(:,3), q(:,4), q(:,6));
end
hdr = {'realisation', 'strategy', 'fulfil_pct', 'n_valid', 'max_rebound', 'net_cost', 'cost_op', 'dr_pay', 'lateness', 'cap_violation'};
write_csv(fullfile(root, 'results', 'exp4_montecarlo.csv'), hdr, rows);
out.rows = rows;
end
