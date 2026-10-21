function out = exp6_commitment(ctx, root, DA, SE)
%EXP6_COMMITMENT  Coupled (proposed) vs single-event (conventional) day-ahead capability assessment.
S = {'IR-O', 'expected'; 'JR', 'scenario'; 'JR', 'open'};
lab = {'IR-O', 'JR-S', 'JR-oracle'};
rows = []; rl = {};
for v = 1:2
    if v == 1, X = DA; nm = 'coupled'; else, X = SE; nm = 'single-event'; end
    c = apply_commit(ctx, X.C, DA); c.all_visible = true;
    for i = 1:size(S, 1)
        R = run_strategy(c, S{i, 1}, S{i, 2}); M = R.M;
        rows = [rows; v, X.C(:)', sum(X.C), 100 * M.fulfil_rate, M.n_valid, M.dr_pay, M.pen_dev, M.net_cost, M.max_rebound]; %#ok<AGROW>
        rl{end+1} = sprintf('%s|%s', nm, lab{i}); %#ok<AGROW>
        fprintf('  exp6 %-12s %-9s C=%s fulfil=%.1f%% valid=%d pay=%.0f net=%.0f\n', nm, lab{i}, mat2str(round(X.C'*100)/100), 100*M.fulfil_rate, M.n_valid, M.dr_pay, M.net_cost);
    end
end
hdr = {'assessment', 'C1', 'C2', 'C3', 'C_total', 'fulfil_pct', 'n_valid', 'dr_pay', 'pen_dev', 'net_cost', 'max_rebound'};
write_csv(fullfile(root, 'results', 'exp6_commitment.csv'), hdr, rows, rl);
out.rows = rows; out.labels = rl;
end
