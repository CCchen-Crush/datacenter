function out = exp2_main(ctx, root, DA, tag)
%EXP2_MAIN  Main comparison on the case day under identical commitments and service requirements.
%   Case A: commitments from the coupled day-ahead model; Case B: uniform 6 MW per event.
%   Strategies (bench_list 'main'): IR-R, IR-O (static split), IR-O* (split tuned day-ahead), IR-P
%   (day-ahead shadow-price coordination), JR-M (joint, event by event), JR-D / JR-S (proposed,
%   deterministic / scenario MPC), JR-oracle (perfect information) and the no-DR operation.
%   tag: suffix of the output files (e.g. '_crb0' for the run without rebound assessment).
if nargin < 4, tag = ''; end
S = bench_list('main');
cases = {'DAcommit', DA.C; 'uniform6', [6 6 6]};
out = struct();
for ci = 1:size(cases, 1)
    c = apply_commit(ctx, cases{ci, 2}, DA);
    c = prepare_benchmarks(c);
    [rows, hdr, Rs] = run_list(c, S, sprintf('exp2%s %-8s ', tag, cases{ci, 1}));
    for i = 1:size(S, 1)
        save_timeseries(fullfile(root, 'results', sprintf('ts_%s_%s%s.csv', cases{ci, 1}, strrep(strrep(S{i, 3}, '-', ''), '*', 's'), tag)), Rs{i}, c);
        out.(cases{ci, 1}).(strrep(strrep(S{i, 3}, '-', '_'), '*', 's')) = Rs{i}.M;
    end
    R0 = run_strategy(c, 'NoDR'); row0 = metrics_row(R0.M);
    save_timeseries(fullfile(root, 'results', sprintf('ts_%s_NoDR%s.csv', cases{ci, 1}, tag)), R0, c);
    write_csv(fullfile(root, 'results', sprintf('exp2_%s%s.csv', cases{ci, 1}, tag)), hdr, [rows; row0], [S(:, 3)', {'NoDR'}]);
    write_csv(fullfile(root, 'results', sprintf('exp2_alpha_%s%s.csv', cases{ci, 1}, tag)), ...
        {'alpha', 'mean_net_cost_adj', 'mean_fulfil_pct', 'share_all_valid'}, c.alpha_tab);
    write_csv(fullfile(root, 'results', sprintf('exp2_lambda_%s%s.csv', cases{ci, 1}, tag)), {'hour', 'lambda_hr', 'value_el'}, ...
        [(0:c.par.Tsim-1)' * c.par.dt, c.lambda_hr_da, c.lambda_info.value]);
    out.(cases{ci, 1}).alpha_star = c.alpha_star;
end
write_csv(fullfile(root, 'results', sprintf('exp2_commitments%s.csv', tag)), {'E1', 'E2', 'E3'}, [DA.C(:)'; 6 6 6], {'DAcommit', 'uniform6'});
end
