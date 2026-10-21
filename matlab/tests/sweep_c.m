here = fileparts(mfilename('fullpath'));
addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'config'));
par = dcdr_params();
if ~exist("CLIST","var"), CLIST = [4 6 8 10]; end
if exist('GAMMA','var'), par.cap.gamma = GAMMA; end
ctx0 = setup_case(par);
fprintf('Pcap=%.2f (base peak %.2f) alpha=%.2f\n', ctx0.d.Pcap, ctx0.par.cap.Pbase_peak, ctx0.alpha);
for C = CLIST
    ctx = ctx0; for k = 1:numel(ctx.ev), ctx.ev(k).C = C; end
    for nm = {'IR-R', 'IR-O', 'JR'}
        R = run_strategy(ctx, nm{1}, 'open'); M = R.M;
        fprintf('C=%d %-5s fulfil=%.3f valid=%d red=%s rb=%s Estart=%s Bstart=%s net=%.0f op=%.0f late=%.1f\n', C, nm{1}, M.fulfil_rate, M.n_valid, ...
            mat2str(round(M.avg_red'*100)/100), mat2str(round(M.rebound'*100)/100), mat2str(round(M.E_start'*10)/10), ...
            mat2str(round(sum(M.B_start,2)')), M.net_cost, M.cost_op, M.lateness);
    end
end
