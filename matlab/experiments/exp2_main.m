function out = exp2_main(ctx, root, DA)
%EXP2_MAIN  Main comparison under identical commitments and service requirements.
%   Case A: commitments from the coupled day-ahead model; Case B: uniform 6 MW per event.
S = {'IR-R', 'rule'; 'IR-O', 'expected'; 'JR', 'expected'; 'JR', 'scenario'; 'JR', 'open'};
lab = {'IR-R', 'IR-O', 'JR-D', 'JR-S', 'JR-oracle'};
cases = {'DAcommit', DA.C; 'uniform6', [6 6 6]};
out = struct();
for ci = 1:size(cases, 1)
    c = apply_commit(ctx, cases{ci, 2}, DA); c.all_visible = true;
    rows = []; 
    for i = 1:size(S, 1)
        tic; R = run_strategy(c, S{i, 1}, S{i, 2}); el = toc;
        [row, hdr] = metrics_row(R.M); rows = [rows; row]; %#ok<AGROW>
        save_timeseries(fullfile(root, 'results', sprintf('ts_%s_%s.csv', cases{ci, 1}, strrep(lab{i}, '-', ''))), R, c);
        fprintf('  exp2 %-9s %-10s fulfil=%6.2f%% valid=%d maxRb=%.2f net=%.0f late=%.1f (%.0fs)\n', cases{ci,1}, lab{i}, ...
            100 * R.M.fulfil_rate, R.M.n_valid, R.M.max_rebound, R.M.net_cost, R.M.lateness, el);
        out.(strrep(cases{ci,1}, '-', '')).(strrep(lab{i}, '-', '_')) = R.M;
    end
    R0 = run_strategy(c, 'NoDR'); [row0] = metrics_row(R0.M);
    save_timeseries(fullfile(root, 'results', sprintf('ts_%s_NoDR.csv', cases{ci, 1})), R0, c);
    write_csv(fullfile(root, 'results', sprintf('exp2_%s.csv', cases{ci, 1})), hdr, [rows; row0], [lab, {'NoDR'}]);
end
write_csv(fullfile(root, 'results', 'exp2_commitments.csv'), {'E1', 'E2', 'E3'}, [DA.C(:)'; 6 6 6], {'DAcommit', 'uniform6'});
end
