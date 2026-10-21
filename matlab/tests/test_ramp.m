here = fileparts(mfilename('fullpath')); addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
dcdr_setup_paths(); par = dcdr_params(); ctx = setup_case(par);
for rm = [Inf 2 1]
    c = ctx; c.par.it.ramp_max = rm; c.d = sys_derived(c.par);
    c = apply_commit(c, [6 6 6]); c.alpha_star = 0.9; c.lambda_hr_da = dayahead_prices(c);
    for nm = {'IR-R', 'IR-O*', 'IR-P', 'JR'}
        if strcmp(nm{1}, 'IR-R'), fm = 'rule'; else, fm = 'expected'; end
        R = run_strategy(c, nm{1}, fm); y = sum(R.log.y, 2) * c.d.pdyn;
        fprintf('ramp %g  %-5s ful=%6.2f valid=%d fallbacks=%d max|dP_IT|=%.2f MW late=%.1f net_adj=%.0f\n', rm, nm{1}, ...
            100*R.M.fulfil_rate, R.M.n_valid, R.M.fallbacks, max(abs(diff(y))), R.M.lateness, R.M.net_cost_adj);
    end
end
