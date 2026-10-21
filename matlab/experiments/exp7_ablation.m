function out = exp7_ablation(ctx, root, C)
%EXP7_ABLATION  Value of each flexibility source in joint recovery, and the best static split for IR-O.
if nargin < 3, C = [6 6 6]; end
base = apply_commit(ctx, C); base.all_visible = true;
cfg = {'full', @(p) p; 'no_compute_flex', @no_flex; 'no_BESS', @no_bess; 'no_TES', @no_tes};
rows = []; rl = {};
for i = 1:size(cfg, 1)
    c = base; c.par = cfg{i, 2}(c.par); c.d = sys_derived(c.par);
    for nm = {'IR-O', 'JR'}
        R = run_strategy(c, nm{1}, 'open'); M = R.M;
        rows = [rows; i, 100 * M.fulfil_rate, M.n_valid, M.max_rebound, M.net_cost]; %#ok<AGROW>
        rl{end+1} = sprintf('%s|%s', cfg{i, 1}, nm{1}); %#ok<AGROW>
        fprintf('  exp7 %-16s %-4s fulfil=%.1f%% valid=%d maxRb=%.2f net=%.0f\n', cfg{i,1}, nm{1}, 100*M.fulfil_rate, M.n_valid, M.max_rebound, M.net_cost);
    end
end
write_csv(fullfile(root, 'results', 'exp7_ablation.csv'), {'config', 'fulfil_pct', 'n_valid', 'max_rebound', 'net_cost'}, rows, rl);
% best static compute share for the independent (sequential) strategy
rows2 = [];
for a = 0.1:0.1:0.9
    c = base; c.alpha = a;
    R = run_strategy(c, 'IR-O', 'open'); M = R.M;
    rows2 = [rows2; a, 100 * M.fulfil_rate, M.n_valid, M.max_rebound, M.net_cost]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', 'exp7_alpha.csv'), {'alpha', 'fulfil_pct', 'n_valid', 'max_rebound', 'net_cost'}, rows2);
[~, ib] = min(rows2(:, 5));
fprintf('  exp7 best static split alpha*=%.1f: fulfil=%.1f%% net=%.0f\n', rows2(ib, 1), rows2(ib, 2), rows2(ib, 5));
out.rows = rows; out.alpha = rows2;
end

function p = no_flex(p)
p.it.lag_h = [0 0 0];
end

function p = no_bess(p)
p.bess.Pmax = 0; p.bess.Emax = p.bess.Emin + 1e-6; p.bess.E0 = p.bess.Emin;
end

function p = no_tes(p)
p.tes.Qmax = 0;
end
