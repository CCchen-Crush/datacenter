function out = exp23_horizon_diag(ctx, root, scen, hzs, Cs, tag)
%EXP23_HORIZON_DIAG  Day-by-day diagnosis of the prediction horizon of JR-D (Section 5.10.2): every
%   operating day is run at every horizon hzs (h; 18 h is the base case) and uniform commitment Cs (MW),
%   without the early stop of the bisection, so that the state of the storage and the backlog at the start
%   of each event can be compared with the base case. Writes results/exp23_horizon<tag>.csv (one metrics
%   row per horizon, commitment and day).
if nargin < 6, tag = ''; end
rs = test_days(ctx, 26); c1 = set_scenario(ctx, scen); K = numel(c1.ev);
rows = []; hdr = {}; t0 = tic;
for hz = hzs
    c = c1; if abs(hz - 18) > 1e-9, c = ctx_with_par(c1, struct('horizon_h', hz)); end
    for C = Cs
        c0 = apply_commit(c, C * ones(1, K));
        for j = 1:numel(rs)
            R = run_strategy(use_realization(c0, rs(j)), 'JR', 'expected');
            [row, hdr] = metrics_row(R.M);
            rows = [rows; hz, C, rs(j), row]; %#ok<AGROW>
        end
        k = size(rows, 1) - numel(rs) + 1:size(rows, 1); af = rows(k, 3 + find(strcmp(hdr, 'all_full')));
        fprintf('  exp23%s horizon %4.1f h, C = %4.2f MW: full delivery on %d of %d days (%.0f min)\n', tag, hz, C, ...
            sum(af > 0.5), numel(rs), toc(t0) / 60);
        write_csv(fullfile(root, 'results', sprintf('exp23_horizon%s.csv', tag)), [{'horizon_h', 'C', 'realisation'}, hdr], rows);
    end
end
out.rows = rows; out.hdr = hdr;
end
