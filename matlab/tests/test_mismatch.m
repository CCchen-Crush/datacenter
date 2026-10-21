here = fileparts(mfilename('fullpath')); addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
dcdr_setup_paths(); par = dcdr_params();
for crb = [0 3000]
  par.dr.c_rb = crb; ctx = setup_case(par);
  cases = {set_events(ctx, [17, 20, 23], 2, 6), apply_commit(ctx, [6 6 6])};
  for i = 1:2
    c = cases{i}; c.alpha_star = alpha_hindsight(c);
    for nm = {'JR', 'IR-O*'}
      R = run_strategy(c, nm{1}, 'open'); L = R.log;
      jct = par.qos.c_jct * par.dt * sum(L.backlog(:));
      fprintf('crb=%d case%d %-5s net_adj(incl delay) %.0f  jct %.0f  E_end %.2f S_end %.2f term_adj %.0f  net_adj+jct %.0f\n', crb, i, nm{1}, R.M.net_cost_adj, jct, L.E(end), L.S(end), R.M.term_adj, R.M.net_cost_adj + jct);
    end
  end
end
