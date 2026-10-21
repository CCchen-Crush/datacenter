%MAIN_RUN_ALL  Reproduce all experiments of the paper
%   "Coordinated scheduling for consecutive demand response in AI data-center integrated energy
%    systems considering cross-event computing-storage recovery".
%
%   Runs in MATLAB (Optimization Toolbox, or Gurobi if on the path) or GNU Octave (glpk).
%   Results are written to matlab/results/*.csv, figures to matlab/figures/*.png.
%   Set QUICK = true for a fast smoke run (fewer Monte-Carlo samples / sweep points).
clc;
root = fileparts(mfilename('fullpath'));
addpath(fullfile(root, 'src')); addpath(fullfile(root, 'config')); addpath(fullfile(root, 'experiments'));
dcdr_setup_paths();
if ~exist('QUICK', 'var'), QUICK = false; end
if ~exist('RUN', 'var'), RUN = 1:7; end
diary(fullfile(root, 'results', 'run_log.txt'));
t_all = tic;
par = dcdr_params();
ctx = setup_case(par);
ctx.all_visible = true;   % E3 is pre-announced day-ahead (Jiangsu "fast" DR pre-notice), confirmed 3 h ahead
fprintf('== case: Pcap = %.2f MW (gamma %.2f x typical peak %.2f MW), alpha = %.2f\n', ctx.d.Pcap, par.cap.gamma, ctx.par.cap.Pbase_peak, ctx.alpha);
write_case_summary(ctx, root);

%% day-ahead commitments: coupled (proposed) and single-event (conventional)
DA = dayahead_commit(ctx, 'coupled');
SE = dayahead_commit(ctx, 'single');
fprintf('== day-ahead commitments  coupled: %s   single-event: %s\n', mat2str(round(DA.C' * 100) / 100), mat2str(round(SE.C' * 100) / 100));
save(fullfile(root, 'results', 'dayahead.mat'), 'DA', 'SE');

if any(RUN == 1)
    fprintf('== Exp1: mechanism (two events)\n');
    if QUICK, o1 = struct('gammas', [1.05 1.2], 'taus', [0.25 1 2]); else, o1 = struct(); end
    o1.CA = 6; o1.DA_h = 2; E1a = exp1_mechanism(ctx, root, o1);
    movefile(fullfile(root, 'results', 'exp1_mechanism.csv'), fullfile(root, 'results', 'exp1_mechanism_CA6_DA2.csv'));
    o1.CA = 6; o1.DA_h = 1; o1.DB_h = 2; E1b = exp1_mechanism(ctx, root, o1);
    movefile(fullfile(root, 'results', 'exp1_mechanism.csv'), fullfile(root, 'results', 'exp1_mechanism_CA6_DA1_DB2.csv'));
end
if any(RUN == 2), fprintf('== Exp2: main comparison\n'); E2 = exp2_main(ctx, root, DA); end
if any(RUN == 3)
    fprintf('== Exp3: sensitivity\n');
    if QUICK, o3 = struct('durations', [1 2], 'intervals', [0.5 1 2], 'gammas', [1.05 1.2], 'Cs', [4 6 8], 'map_gammas', [1.05 1.2], 'map_taus', [0.5 2]); else, o3 = struct(); end
    E3 = exp3_sensitivity(ctx, root, o3);
end
if any(RUN == 4)
    fprintf('== Exp4: Monte-Carlo closed loop\n');
    if QUICK, N = 3; else, N = 20; end
    E4 = exp4_uncertainty(ctx, root, DA, N);
end
if any(RUN == 5), fprintf('== Exp5: shadow prices\n'); E5 = exp5_shadow(ctx, root, DA); end
if any(RUN == 6), fprintf('== Exp6: commitment assessment\n'); E6 = exp6_commitment(ctx, root, DA, SE); end
if any(RUN == 7), fprintf('== Exp7: ablation\n'); E7 = exp7_ablation(ctx, root, [6 6 6]); end
fprintf('== all done in %.1f min\n', toc(t_all) / 60);
try
    plot_all(root);
catch err
    fprintf('plotting skipped (%s). Use tools/plot_results.py as an alternative.\n', err.message);
end
diary off;
