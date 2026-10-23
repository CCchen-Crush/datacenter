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
%                                  E12_SCEN = 'S1' | 'S2-30' | 'S3' -> event scenario of Exp12 (set_scenario), E12_N days
%   Base case: Jiangsu settlement rules alone (no gap-rebound assessment, c_rb = 0). The rebound
%   assessment is a policy parameter: Exp8 sweeps it, RB_SENS repeats the main experiments at 3 CNY/kW.
clc;
root = fileparts(mfilename('fullpath'));
addpath(fullfile(root, 'src')); addpath(fullfile(root, 'config')); addpath(fullfile(root, 'experiments'));
dcdr_setup_paths();
if ~exist('QUICK', 'var'), QUICK = false; end
if ~exist('RUN', 'var'), RUN = 1:16; end
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
    if ~exist('E12_CS', 'var'), E12_CS = 3:0.5:9; end
    if ~exist('E12_TAG', 'var'), E12_TAG = ''; end
    S12 = [];                                   % default: deterministic MPC (forecasts)
    if exist('E12_FMODE', 'var')                % e.g. 'oracle': same controllers with perfect forecasts
        S12 = {'IR-O*', E12_FMODE, 'IR-O*'; 'IR-P', E12_FMODE, 'IR-P'; 'JR-M', E12_FMODE, 'JR-M'; 'JR', E12_FMODE, 'JR-D'};
    end
    c12 = ctx; if exist('E12_SCEN', 'var'), c12 = set_scenario(ctx, E12_SCEN); end   % S1 (default) | S2-<min> | S3
    if ~exist('E12_N', 'var'), E12_N = 26; end                                       % distinct PAI test weekdays
    if QUICK, E12 = exp12_capacity(c12, root, [6 8], 2, E12_TAG, S12); else, E12 = exp12_capacity(c12, root, E12_CS, E12_N, E12_TAG, S12); end
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
if any(RUN == 14)
    % closed-loop sweeps on the PAI test days (exp14_sweep). E14_SET selects the study:
    %   'tau_gamma'  sensitivity map: two one-hour events, interval x connection margin, uniform C = E14_C
    %   'single'     single-factor sensitivity at S1: lag bounds L_c x 0.5-1.5 (connection limit kept)
    %   'ablation'   resource / coordination ablation (JR-D controller), commitment sweep
    %   'region'     two-event reliability region: (C1, C2) grid, scenario E14_SCEN
    if ~exist('E14_SET', 'var'), E14_SET = 'tau_gamma'; end
    if ~exist('E14_C', 'var'), E14_C = 7; end
    if ~exist('E14_TAG', 'var'), E14_TAG = ''; end
    o14 = struct('N', 26); if exist('E14_N', 'var'), o14.N = E14_N; end
    cf = struct('name', {}, 'scen', {}, 'gap', {}, 'mods', {}, 'C', {}, 'S', {});
    switch E14_SET
        case 'tau_gamma'
            if ~exist('E14_GAPS', 'var'), E14_GAPS = [0.25 0.5 1 2 3]; end
            if ~exist('E14_GAMMAS', 'var'), E14_GAMMAS = [1.00 1.05 1.10 1.20]; end
            for g = E14_GAMMAS
                for gap = E14_GAPS
                    cf(end+1) = struct('name', sprintf('gap%.2f_g%.2f', gap, g), 'scen', '', 'gap', gap, ...
                                       'mods', struct('gamma', g), 'C', E14_C, 'S', []); %#ok<SAGROW>
                end
            end
        case 'single'        % lag bounds (the BESS size is swept by Exp20 'bess'); connection limit kept
            for ls = [0.5 0.75 1.25 1.5]
                cf(end+1) = struct('name', sprintf('lag%.2f', ls), 'scen', 'S1', 'gap', [], 'mods', struct('lag_scale', ls, 'keep_Pcap', true), 'C', E14_C, 'S', []); %#ok<SAGROW>
            end
        case 'ablation'
            if ~exist('E14_CS', 'var'), E14_CS = 1:0.5:8; end
            Sj = {'JR', 'expected', 'JR-D'};
            cf(1) = struct('name', 'BESS_only', 'scen', 'S1', 'gap', [], 'mods', struct('lag_scale', 0, 'tes_on', false), 'C', E14_CS(:), 'S', {Sj});
            cf(2) = struct('name', 'compute_only', 'scen', 'S1', 'gap', [], 'mods', struct('bess_P', 0, 'tes_on', false), 'C', E14_CS(:), 'S', {Sj});
            cf(3) = struct('name', 'compute_BESS', 'scen', 'S1', 'gap', [], 'mods', struct('tes_on', false), 'C', E14_CS(:), 'S', {Sj});
            if exist('E14_ABL', 'var'), cf = cf(E14_ABL); end
        case 'region'
            if ~exist('E14_SCEN', 'var'), E14_SCEN = 'S2-30'; end
            if ~exist('E14_CG', 'var'), E14_CG = 4:9; end
            [a1, a2] = ndgrid(E14_CG, E14_CG);
            cf(1) = struct('name', E14_SCEN, 'scen', E14_SCEN, 'gap', [], 'mods', [], 'C', [a1(:), a2(:)], ...
                           'S', {{'IR-O*', 'expected', 'IR-O*'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'}});
            if exist('E14_ALPHA', 'var')            % alpha* of IR-O* from the uniform sweep: [C, alpha*] rows
                o14.alpha_fix = @(C) interp1(E14_ALPHA(:, 1), E14_ALPHA(:, 2), C, 'nearest', 'extrap');
            end
            if exist('E14_PAIRS', 'var'), cf(1).C = cf(1).C(E14_PAIRS, :); end
    end
    if exist('E14_SUB', 'var'), cf = cf(E14_SUB); end      % subset of the configurations (parallel parts)
    fprintf('== Exp14: closed-loop sweep %s (%d configurations)\n', E14_SET, numel(cf));
    E14 = exp14_sweep(ctx, root, cf, [E14_SET E14_TAG], o14);
end
if any(RUN == 15)
    fprintf('== Exp15: recovery mechanism on typical days\n');
    if ~exist('E15_CASES', 'var'), E15_CASES = {'S2-30', 7, 0, 'short'; 'S2-180', 7, 0, 'long'}; end
    E15 = exp15_mechanism(ctx, root, E15_CASES);
end
if any(RUN == 16)
    if ~exist('E16_SCEN', 'var'), E16_SCEN = 'S1'; end
    fprintf('== Exp16: endogenous commitment protocol (%s)\n', E16_SCEN);
    E16 = exp16_endogenous(set_scenario(ctx, E16_SCEN), root, [], 26, ['_' E16_SCEN]);
end
if any(RUN == 17)
    fprintf('== Exp17: no-DR reference on the test days\n');
    E17 = exp17_nodr(ctx, root, 26);
end
if any(RUN == 18)
    % closed-loop back-test on the historical days of the day-ahead pool (distributionally robust commitment)
    if ~exist('E18_SCEN', 'var'), E18_SCEN = 'S1'; end
    if ~exist('E18_CS', 'var'), E18_CS = 1:0.5:9; end
    if ~exist('E18_TAG', 'var'), E18_TAG = ['_' E18_SCEN]; end
    fprintf('== Exp18: back-test on the historical days (%s)\n', E18_SCEN);
    E18 = exp18_history(set_scenario(ctx, E18_SCEN), root, E18_CS, E18_TAG);
end
if any(RUN == 19)
    % upper bound of static-split independent recovery (best split in hindsight on every test day)
    if ~exist('E19_SCEN', 'var'), E19_SCEN = 'S1'; end
    if ~exist('E19_CS', 'var'), E19_CS = [1 2 3 4 5 6 7 7.5]; end
    if ~exist('E19_TAG', 'var'), E19_TAG = ['_' E19_SCEN]; end
    fprintf('== Exp19: IR-O with the best split in hindsight (%s)\n', E19_SCEN);
    E19 = exp19_hindsight(set_scenario(ctx, E19_SCEN), root, E19_CS, [], E19_TAG);
end
if any(RUN == 20)
    % firm capacity by bisection for system configurations: E20_SET = 'bess' | 'gamma' | 'ies' | 'resources' | 'tau' | 'overhead'
    if ~exist('E20_SET', 'var'), E20_SET = 'bess'; end
    if ~exist('E20_SCEN', 'var'), E20_SCEN = 'S2-30'; end
    if ~exist('E20_TAG', 'var'), E20_TAG = ''; end
    o20 = struct('rho', 0.95, 'tol', 0.25, 'N', 26);
    SD = {'JR', 'expected', 'JR-D'}; SM = {'JR-M', 'expected', 'JR-M'}; SI = {'IR-O*', 'expected', 'IR-O*'};
    cf = struct('name', {}, 'scen', {}, 'mods', {}, 'S', {}, 'lo', {}, 'hi', {});
    switch E20_SET
        case 'bess'          % BESS power (energy at the 2-h ratio): substitution curve
            for P = [0 3 6 9 12]
                S = [SD; SI]; if P == 6, S = [SD; SM; SI]; end
                cf(end+1) = struct('name', sprintf('bess%g', P), 'scen', E20_SCEN, 'mods', struct('bess_P', P, 'keep_Pcap', true), 'S', {S}, 'lo', 1, 'hi', 16); %#ok<SAGROW>
            end
        case 'gamma'         % connection margin: substitution curve (gamma 1.10 = base, in 'bess')
            for g = [1.00 1.05 1.20 1.30]
                cf(end+1) = struct('name', sprintf('g%.2f', g), 'scen', E20_SCEN, 'mods', struct('gamma', g), 'S', {[SD; SI]}, 'lo', 1, 'hi', 16); %#ok<SAGROW>
            end
        case 'ies'           % contribution of the IES devices to the firm capacity of JR-D
            cf(1) = struct('name', 'noGT', 'scen', E20_SCEN, 'mods', struct('gt_on', false, 'keep_Pcap', true), 'S', {SD}, 'lo', 1, 'hi', 12);
            cf(2) = struct('name', 'noTES', 'scen', E20_SCEN, 'mods', struct('tes_on', false, 'keep_Pcap', true), 'S', {SD}, 'lo', 1, 'hi', 12);
            cf(3) = struct('name', 'noAC', 'scen', E20_SCEN, 'mods', struct('ac_on', false, 'keep_Pcap', true), 'S', {SD}, 'lo', 1, 'hi', 12);
            cf(4) = struct('name', 'noIES', 'scen', E20_SCEN, 'mods', struct('gt_on', false, 'tes_on', false, 'ac_on', false, 'keep_Pcap', true), ...
                           'S', {SD}, 'lo', 1, 'hi', 12);
        case 'resources'     % resource ablation (JR-D controller, connection kept): BESS only, compute only, compute + BESS
            cf(1) = struct('name', 'BESS_only', 'scen', E20_SCEN, 'mods', struct('lag_scale', 0, 'tes_on', false, 'keep_Pcap', true), 'S', {SD}, 'lo', 1, 'hi', 12);
            cf(2) = struct('name', 'compute_only', 'scen', E20_SCEN, 'mods', struct('bess_P', 0, 'tes_on', false, 'keep_Pcap', true), 'S', {SD}, 'lo', 1, 'hi', 12);
            cf(3) = struct('name', 'compute_BESS', 'scen', E20_SCEN, 'mods', struct('tes_on', false, 'keep_Pcap', true), 'S', {SD}, 'lo', 1, 'hi', 12);
        case 'tau'           % firm capacity vs event interval (30 min is the bess6 configuration of 'bess')
            for mins = [15 60 120 180]
                cf(end+1) = struct('name', sprintf('tau%d', mins), 'scen', sprintf('S2-%d', mins), 'mods', [], ...
                                   'S', {[SD; SM; SI]}, 'lo', 1, 'hi', 12); %#ok<SAGROW>
            end
        case 'overhead'      % robustness: pause/resume overhead of deferred work
            for ov = [0.02 0.05]
                cf(end+1) = struct('name', sprintf('ovh%.2f', ov), 'scen', E20_SCEN, 'mods', struct('overhead', ov, 'keep_Pcap', true), ...
                                   'S', {[SD; SM; SI]}, 'lo', 1, 'hi', 12); %#ok<SAGROW>
            end
    end
    if exist('E20_SUB', 'var'), cf = cf(E20_SUB); end
    if exist('E20_N', 'var'), o20.N = E20_N; end
    if exist('E20_LOHI', 'var'), for i = 1:numel(cf), cf(i).lo = E20_LOHI(1); cf(i).hi = E20_LOHI(2); end, end
    fprintf('== Exp20: firm capacity by bisection, set %s (%d configurations)\n', E20_SET, numel(cf));
    E20 = exp20_capacity_configs(ctx, root, cf, [E20_SET E20_TAG], o20);
end
fprintf('== all done in %.1f min\n', toc(t_all) / 60);
diary off;
