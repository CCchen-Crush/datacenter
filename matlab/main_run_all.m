%MAIN_RUN_ALL  Reproduce all experiments of the paper
%   "Coordinated scheduling for consecutive demand response in AI data-center integrated energy
%    systems considering cross-event computing-storage recovery" (revised version).
%
%   Runs in MATLAB (Optimization Toolbox, or Gurobi if on the path) or GNU Octave (glpk).
%   Results are written to matlab/results/*.csv, figures by tools/plot_results.py.
%   Options (set before calling):  QUICK = true  -> smoke run (tiny samples / grids)
%                                  RUN = [...]   -> subset of experiments (default 1:12)
%                                  NMC = n       -> Monte-Carlo realisations (default: all, 52)
%                                  MC_PART = 'certain' | 'uncertain' | 'all' (parts of Exp4; default 'all')
%                                  RB_SENS = true -> also repeat Exp2-6 with c_rb = 3 CNY/kW (tag '_crb3')
%                                  E12_CS = [...], E12_TAG = '_p1' -> commitment levels / file tag of Exp12
%                                  (to split the capacity sweep over parallel processes)
%                                  E12_FMODE = 'oracle' -> Exp12 with perfect forecasts (information diagnostic)
%   Base case: Jiangsu settlement rules alone (no gap-rebound assessment, c_rb = 0). The rebound
%   assessment is a policy parameter: Exp8 sweeps it, RB_SENS repeats the main experiments at 3 CNY/kW.
clc;
root = fileparts(mfilename('fullpath'));
addpath(fullfile(root, 'src')); addpath(fullfile(root, 'config')); addpath(fullfile(root, 'experiments'));
dcdr_setup_paths();
if ~exist('QUICK', 'var'), QUICK = false; end
if ~exist('RUN', 'var'), RUN = 1:13; end
if ~exist('NMC', 'var'), NMC = []; end
if ~exist('MC_PART', 'var'), MC_PART = 'all'; end
if ~exist('LOGTAG', 'var'), LOGTAG = ''; end
if ~exist('RB_SENS', 'var'), RB_SENS = false; end
diary(fullfile(root, 'results', sprintf('run_log%s.txt', LOGTAG)));
t_all = tic;
par = dcdr_params();
if QUICK, par.bench.alpha_grid = [0.6 1.0]; end
ctx = setup_case(par);
ctx3 = ctx; ctx3.par.dr.c_rb = 3000;          % policy sensitivity: gap-rebound assessment 3 CNY/kW per event
fprintf('== case: Pcap = %.2f MW (gamma %.2f x typical peak %.2f MW), static split alpha = %.2f, MC realisations = %d\n', ...
    ctx.d.Pcap, par.cap.gamma, ctx.par.cap.Pbase_peak, ctx.alpha, ctx.inp.mc.N);
if any(RUN == 1), write_case_summary(ctx, root); end

%% day-ahead commitments: coupled (proposed) and single-event (conventional)
if any(ismember(RUN, [2 6]))
    DA = dayahead_commit(ctx, 'coupled');  SE = dayahead_commit(ctx, 'single');
    fprintf('== day-ahead commitments (c_rb = %g)  coupled: %s   single-event: %s\n', ctx.par.dr.c_rb, ...
        mat2str(round(DA.C' * 100) / 100), mat2str(round(SE.C' * 100) / 100));
    if RB_SENS
        DA3 = dayahead_commit(ctx3, 'coupled'); SE3 = dayahead_commit(ctx3, 'single');
        fprintf('== day-ahead commitments (c_rb = 3000)  coupled: %s   single-event: %s\n', ...
            mat2str(round(DA3.C' * 100) / 100), mat2str(round(SE3.C' * 100) / 100));
        save(fullfile(root, 'results', 'dayahead.mat'), 'DA', 'SE', 'DA3', 'SE3');
    else
        save(fullfile(root, 'results', 'dayahead.mat'), 'DA', 'SE');
    end
end

if any(RUN == 1)
    fprintf('== Exp1: mechanism (two events)\n');
    if QUICK, o1 = struct('gammas', [1.05 1.2], 'taus', [0.25 1 2]); else, o1 = struct(); end
    o1.CA = 6; o1.DA_h = 2; E1a = exp1_mechanism(ctx, root, o1);
    movefile(fullfile(root, 'results', 'exp1_mechanism.csv'), fullfile(root, 'results', 'exp1_mechanism_CA6_DA2.csv'));
    o1.CA = 6; o1.DA_h = 1; o1.DB_h = 2; E1b = exp1_mechanism(ctx, root, o1);
    movefile(fullfile(root, 'results', 'exp1_mechanism.csv'), fullfile(root, 'results', 'exp1_mechanism_CA6_DA1_DB2.csv'));
end
if any(RUN == 2)
    fprintf('== Exp2: main comparison (c_rb = %g)\n', ctx.par.dr.c_rb); E2 = exp2_main(ctx, root, DA);
    if RB_SENS, fprintf('== Exp2: main comparison (c_rb = 3000)\n'); E2b = exp2_main(ctx3, root, DA3, '_crb3'); end
end
if any(RUN == 3)
    if QUICK, o3 = struct('durations', [1 2], 'intervals', [0.5 1], 'gammas', [1.05 1.2], 'Cs', [6 8], 'map_gammas', [1.05], 'map_taus', [0.5 2]); else, o3 = struct(); end
    fprintf('== Exp3: sensitivity (perfect information, c_rb = %g)\n', ctx.par.dr.c_rb); E3 = exp3_sensitivity(ctx, root, o3);
    if RB_SENS, fprintf('== Exp3: sensitivity (perfect information, c_rb = 3000)\n'); E3b = exp3_sensitivity(ctx3, root, o3, '_crb3'); end
end
if any(RUN == 4)
    if QUICK, N = 2; elseif isempty(NMC), N = ctx.inp.mc.N; else, N = NMC; end
    if any(strcmp(MC_PART, {'all', 'certain'}))
        fprintf('== Exp4a: Monte-Carlo, all events certain (c_rb = %g), N = %d\n', ctx.par.dr.c_rb, N);
        E4a = exp4_montecarlo(ctx, root, [6 6 6], N, '_certain', bench_list('mc'));
        if RB_SENS
            fprintf('== Exp4b: Monte-Carlo, all events certain (c_rb = 3000), N = %d\n', N);
            E4b = exp4_montecarlo(ctx3, root, [6 6 6], N, '_certain_crb3', bench_list('mc'));
        end
    end
    if any(strcmp(MC_PART, {'all', 'uncertain'}))
        % E3 pre-announced day-ahead as possible (call probability 0.6), confirmed or cancelled 1 h before
        % its start (Jiangsu speed coefficient 1.6 for 0.5-2 h notice)
        cu = set_events(ctx, [17 19 21], 1, 6, [24 24 1], [1 1 0.6]);
        fprintf('== Exp4c: Monte-Carlo with event-call uncertainty (E3 p = 0.6, notice 1 h), N = %d\n', N);
        E4c = exp4_montecarlo(cu, root, [6 6 6], N, '_e3uncertain', bench_list('mc_unc'));
    end
end
if any(RUN == 5)
    fprintf('== Exp5: shadow prices and Proposition 2 check\n');
    E5 = exp5_shadow(ctx, root, [6 6 6]);
    E5c = exp5_shadow(ctx_with_gamma(ctx, 1.0), root, [6 6 6], '_gamma100');
    if RB_SENS
        E5b = exp5_shadow(ctx3, root, [6 6 6], '_crb3');
        E5d = exp5_shadow(ctx_with_gamma(ctx3, 1.0), root, [6 6 6], '_gamma100_crb3');
    end
end
if any(RUN == 6)
    if QUICK, N6 = 2; th6 = [0.8 1.0]; else, N6 = 20; th6 = []; end
    fprintf('== Exp6: commitment-operation pairing (c_rb = %g)\n', ctx.par.dr.c_rb); E6 = exp6_commitment(ctx, root, DA, SE, N6, '', th6);
    if RB_SENS, fprintf('== Exp6: commitment-operation pairing (c_rb = 3000)\n'); E6b = exp6_commitment(ctx3, root, DA3, SE3, N6, '_crb3', th6); end
end
if any(RUN == 7), fprintf('== Exp7: ablation\n'); E7 = exp7_ablation(ctx, root, [6 6 6]); end
if any(RUN == 8)
    fprintf('== Exp8: rebound assessment as a policy parameter\n');
    if QUICK, E8 = exp8_rebound(ctx, root, [6 6 6], [0 3000]); else, E8 = exp8_rebound(ctx, root, [6 6 6]); end
end
if any(RUN == 9)
    fprintf('== Exp9: DR price and shortfall coefficient\n');
    if QUICK, E9 = exp9_price(ctx, root, [6 6 6], 3000, 1); else, E9 = exp9_price(ctx, root, [6 6 6]); end
end
if any(RUN == 10), fprintf('== Exp10: realism (liquid cooling, IT ramp limits, load-up charge)\n'); E10 = exp10_realism(ctx, root, [6 6 6]); end
if any(RUN == 11), fprintf('== Exp11: stylised theorem check\n'); E11 = exp11_stylized(root); end
if any(RUN == 12)
    fprintf('== Exp12: reliably deliverable capacity (c_rb = %g, Monte-Carlo commitment sweep)\n', ctx.par.dr.c_rb);
    if ~exist('E12_CS', 'var'), E12_CS = 4:0.5:9; end
    if ~exist('E12_TAG', 'var'), E12_TAG = ''; end
    S12 = [];                                   % default: deterministic MPC (forecasts)
    if exist('E12_FMODE', 'var')                % e.g. 'oracle': same controllers with perfect forecasts
        S12 = {'IR-O*', E12_FMODE, 'IR-O*'; 'IR-P', E12_FMODE, 'IR-P'; 'JR-M', E12_FMODE, 'JR-M'; 'JR', E12_FMODE, 'JR-D'};
    end
    if QUICK, E12 = exp12_capacity(ctx, root, [6 8], 2, E12_TAG, S12); else, E12 = exp12_capacity(ctx, root, E12_CS, 20, E12_TAG, S12); end
end
if any(RUN == 13)
    fprintf('== Exp13: two-event capacity region (perfect information)\n');
    if QUICK, o13 = struct('taus', 0.5, 'C1', [0 4 8]); else, o13 = struct(); end
    E13 = exp13_region(ctx, root, o13);                                   % A, B 1 h each (main)
    if ~QUICK
        E13b = exp13_region(ctx, root, struct('DB_h', 2, 'tag', '_DB2'));   % sensitivity: B lasts 2 h
        E13c = exp13_region(ctx, root, struct('DA_h', 2, 'tag', '_DA2'));   % sensitivity: A lasts 2 h
        E13d = exp13_region(ctx, root, struct('t0s', [17 19 21], 'tag', '_K3'));   % main-case timing: E1 = E2 = C1, max E3
    end
end
fprintf('== all done in %.1f min\n', toc(t_all) / 60);
diary off;
