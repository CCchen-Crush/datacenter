here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
for g = [1.0 1.05 1.10 1.20]
    par = dcdr_params(); par.cap.gamma = g;
    ctx0 = setup_case(par);
    for C = [5 6 7]
        ctx = ctx0; for k = 1:numel(ctx.ev), ctx.ev(k).C = C; end
        for nm = {'IR-R', 'IR-O', 'JR'}
            R = run_strategy(ctx, nm{1}, 'open'); M = R.M;
            fprintf('g=%.2f C=%d %-5s fulfil=%.3f valid=%d red=%s rb=%s maxrb=%.2f net=%.0f op=%.0f\n', g, C, nm{1}, M.fulfil_rate, M.n_valid, ...
                mat2str(round(M.avg_red'*100)/100), mat2str(round(M.rebound'*100)/100), M.max_rebound, M.net_cost, M.cost_op);
        end
    end
end
