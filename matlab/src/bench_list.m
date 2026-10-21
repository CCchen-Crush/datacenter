function S = bench_list(which)
%BENCH_LIST  Strategy sets used by the experiments: {strategy name, forecast mode, label}.
switch which
    case 'main'      % closed-loop comparison on the case day (incl. scenario MPC and perfect information)
        S = {'IR-R', 'rule', 'IR-R'; 'IR-O', 'expected', 'IR-O'; 'IR-O*', 'expected', 'IR-O*'; ...
             'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'; ...
             'JR', 'scenario', 'JR-S'; 'JR', 'open', 'JR-oracle'};
    case 'mc'        % Monte-Carlo (deterministic MPC variants)
        S = {'IR-R', 'rule', 'IR-R'; 'IR-O', 'expected', 'IR-O'; 'IR-O*', 'expected', 'IR-O*'; ...
             'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'};
    case 'mc_unc'    % Monte-Carlo with event-call uncertainty (adds the scenario MPC)
        S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; ...
             'JR', 'expected', 'JR-D'; 'JR', 'scenario', 'JR-S'; 'JR', 'open', 'JR-oracle'};
    case 'core'      % strongest benchmarks vs proposed (sweeps)
        S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; ...
             'JR', 'expected', 'JR-D'};
    case 'open'      % perfect-information (open-loop) capability comparison
        S = {'IR-R', 'rule', 'IR-R'; 'IR-O', 'open', 'IR-O'; 'IR-O*', 'open', 'IR-O*(hindsight)'; ...
             'IR-P', 'open', 'IR-P'; 'JR', 'open', 'JR'};
    otherwise
        error('bench_list:which', 'unknown list %s', which);
end
end
