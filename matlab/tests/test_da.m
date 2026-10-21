here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
par = dcdr_params(); ctx = setup_case(par);
tic; DA = dayahead_commit(ctx, 'coupled'); fprintf('coupled: C=%s  valid_prob=%s  (%.1fs)\n', mat2str(round(DA.C'*100)/100), mat2str(DA.valid_prob'), toc);
tic; SE = dayahead_commit(ctx, 'single');  fprintf('single : C=%s  (%.1fs)\n', mat2str(round(SE.C'*100)/100), toc);
for v = {DA, SE}
    c2 = ctx; for k = 1:3, c2.ev(k).C = v{1}.C(k); end
    for nm = {'IR-R', 'IR-O', 'JR'}
        R = run_strategy(c2, nm{1}, 'open'); M = R.M;
        fprintf('%s %-5s fulfil=%.3f valid=%d red=%s rb=%s maxrb=%.2f net=%.0f\n', v{1}.mode, nm{1}, M.fulfil_rate, M.n_valid, ...
            mat2str(round(M.avg_red'*100)/100), mat2str(round(M.rebound'*100)/100), M.max_rebound, M.net_cost);
    end
end
