here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
par = dcdr_params();
ctx = setup_case(par); for k = 1:numel(ctx.ev), ctx.ev(k).C = 6; end
for fm = {'expected', 'scenario'}
    tic; R = run_strategy(ctx, 'JR', fm{1}); M = R.M;
    fprintf('JR-%s: %.0fs (solver %.0fs, fallbacks %d) fulfil=%.3f valid=%d red=%s rb=%s net=%.0f late=%.1f\n', fm{1}, toc, M.solve_time, M.fallbacks, ...
        M.fulfil_rate, M.n_valid, mat2str(round(M.avg_red'*100)/100), mat2str(round(M.rebound'*100)/100), M.net_cost, M.lateness);
end
