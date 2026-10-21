here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
for crb = [0 2000 3000 4000 6000]
    par = dcdr_params(); par.dr.c_rb = crb;
    ctx = setup_case(par); for k = 1:numel(ctx.ev), ctx.ev(k).C = 6; end
    for nm = {'IR-R', 'IR-O', 'JR'}
        R = run_strategy(ctx, nm{1}, 'open'); M = R.M;
        fprintf('crb=%d %-5s fulfil=%.3f valid=%d red=%s rb=%s maxrb=%.2f net=%.0f op=%.0f\n', crb, nm{1}, M.fulfil_rate, M.n_valid, ...
            mat2str(round(M.avg_red'*100)/100), mat2str(round(M.rebound'*100)/100), M.max_rebound, M.net_cost, M.cost_op);
    end
end
