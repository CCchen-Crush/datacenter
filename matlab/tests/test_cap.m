here = fileparts(mfilename('fullpath')); addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
dcdr_setup_paths(); par = dcdr_params();
for on = [false true]
    par.it.cap_on = on; ctx = setup_case(par);
    for C = [6 8]
        c = apply_commit(ctx, C * [1 1 1]); c.alpha_star = 0.9; c.lambda_hr_da = dayahead_prices(c);
        for nm = {'IR-O*', 'IR-P', 'JR'}
            R = run_strategy(c, nm{1}, 'expected');
            fprintf('cap=%d C=%d %-5s ful=%6.2f valid=%d fb=%d capped(GPU-h in events)=%.0f B_E2start=%.0f net_adj=%.0f\n', on, C, nm{1}, ...
                100*R.M.fulfil_rate, R.M.n_valid, R.M.fallbacks, sum(sum(R.log.z))*par.dt, sum(R.M.B_start(2,:)), R.M.net_cost_adj);
        end
    end
end
