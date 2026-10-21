function out = exp6_commitment(ctx, root, DA, SE, N, tag, thetas)
%EXP6_COMMITMENT  Commitment-operation pairing (review issue 1c/2): every strategy is evaluated with
%   its own day-ahead commitment as well as with the other one, on the case day and over N
%   Monte-Carlo realisations.
%     SE        conventional single-event capability assessment (each event alone)
%     SE-theta  single-event assessment scaled by theta*, the factor that maximises the expected
%               profit of IR-O* back-tested on the day-ahead scenarios (a cautious conventional operator)
%     DA        coupled two-stage stochastic assessment (proposed)
%   Operation: IR-O* (split re-tuned for each commitment vector) and JR-D.
if nargin < 5 || isempty(N), N = 20; end
if nargin < 6, tag = ''; end
if nargin < 7 || isempty(thetas), thetas = 0.5:0.1:1.0; end
N = min(N, ctx.inp.mc.N);
% cautious conventional commitment: theta * SE, theta chosen day-ahead for IR-O*
vt = zeros(numel(thetas), 2);
for i = 1:numel(thetas)
    c = apply_commit(ctx, thetas(i) * SE.C, DA);
    [a, tab] = tune_alpha(c, 'expected', [0.6 0.8 1.0]);
    vt(i, :) = [thetas(i), min(tab(:, 2))];
end
[~, j] = min(vt(:, 2)); th = thetas(j);
fprintf('  exp6%s cautious conventional commitment: theta* = %.1f -> C = %s\n', tag, th, mat2str(round(th * SE.C' * 100) / 100));
packs = {'SE', SE.C; 'SE-theta', th * SE.C; 'DA', DA.C};
ops = {'IR-O*', 'expected', 'IR-O*'; 'JR', 'expected', 'JR-D'};
rows = []; rl = {}; hdr = {};
for p = 1:size(packs, 1)
    c = apply_commit(ctx, packs{p, 2}, DA);
    c = prepare_benchmarks(c, struct('verbose', false));
    for i = 1:size(ops, 1)
        % case day
        R = run_strategy(c, ops{i, 1}, ops{i, 2}); [row, hdr] = metrics_row(R.M);
        % Monte-Carlo
        mc = zeros(N, numel(row));
        for r = 1:N
            cr = use_realization(c, r);
            Rr = run_strategy(cr, ops{i, 1}, ops{i, 2}); mc(r, :) = metrics_row(Rr.M);
        end
        allv = mean(mc(:, strcmp(hdr, 'all_valid')));
        rows = [rows; p, i, packs{p, 2}(:)', sum(packs{p, 2}), c.alpha_star, row, mean(mc, 1), allv]; %#ok<AGROW>
        rl{end+1} = sprintf('%s|%s', packs{p, 1}, ops{i, 3}); %#ok<AGROW>
        fprintf('  exp6%s %-9s %-6s C=%s | day: ful=%.1f%% valid=%d net_adj=%.0f | MC(%d): ful=%.1f%% allvalid=%.0f%% net_adj=%.0f\n', tag, ...
            packs{p, 1}, ops{i, 3}, mat2str(round(packs{p, 2}' * 100) / 100), 100 * R.M.fulfil_rate, R.M.n_valid, R.M.net_cost_adj, ...
            N, mean(mc(:, 1)), 100 * allv, mean(mc(:, strcmp(hdr, 'net_cost_adj'))));
    end
end
mh = cellfun(@(s) ['mc_' s], hdr, 'UniformOutput', false);
write_csv(fullfile(root, 'results', sprintf('exp6_commitment%s.csv', tag)), ...
    [{'package', 'operation', 'C1', 'C2', 'C3', 'C_total', 'alpha_star'}, hdr, mh, {'mc_share_all_valid'}], rows, rl);
write_csv(fullfile(root, 'results', sprintf('exp6_theta%s.csv', tag)), {'theta', 'IRO_star_mean_net_cost_adj'}, vt);
out.rows = rows; out.labels = rl; out.theta = th;
end
