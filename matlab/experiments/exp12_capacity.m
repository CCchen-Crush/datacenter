function out = exp12_capacity(ctx, root, Cs, N, tag, S, active, alpha_tab, rs)
%EXP12_CAPACITY  Reliably deliverable consecutive-DR capacity (decision experiment G1a): uniform
%   commitment C swept over Cs; for every C the benchmarks are re-tuned day-ahead and each strategy is
%   run in closed loop on N Monte-Carlo realisations that use N different PAI weekdays. For each
%   strategy this gives the share of days on which (i) all called events are valid (Jiangsu 80 % rule)
%   and (ii) every event is delivered in full (>= par.dr.full_lo of the commitment), the mean
%   fulfilment and the mean net cost; the reliable capacity C_rho is the largest C whose share >= rho.
%   Strategies: IR-O*, IR-P (strongest independent benchmarks), JR-M (joint, event by event) and
%   JR-D (joint, cross-event, deterministic MPC). active (indices into S, default all) selects the strategies
%   run in this part (the strategy index of the output refers to S); alpha_tab = [C, alpha*] rows reuses splits
%   already tuned day-ahead for the same scenario (tune_alpha is deterministic), other C are tuned.
%   rs (optional) lists the test realisations explicitly (default: the first N with different PAI weekdays).
if nargin < 3 || isempty(Cs), Cs = 3:0.5:9; end
if nargin < 4 || isempty(N), N = 26; end
if nargin < 5, tag = ''; end
if nargin < 6 || isempty(S)
    S = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'};
end
if nargin < 7 || isempty(active), active = 1:size(S, 1); end
if nargin < 8, alpha_tab = []; end
if nargin < 9 || isempty(rs), rs = distinct_pai(ctx.inp.mc.label, N); end   % rs: explicit test realisations
rows = []; hdr = {}; t0 = tic;
for C = Cs
    c0 = bench_prepare(apply_commit(ctx, C * ones(1, numel(ctx.ev))), S(active, 1), C, alpha_tab);
    v = zeros(numel(rs), 4, size(S, 1));
    for j = 1:numel(rs)
        c = use_realization(c0, rs(j));
        for i = active
            R = run_strategy(c, S{i, 1}, S{i, 2});
            [row, hdr] = metrics_row(R.M);
            rows = [rows; C, rs(j), i, c0.alpha_star, row]; %#ok<AGROW>
            v(j, :, i) = [100 * R.M.fulfil_rate, R.M.all_valid, R.M.all_full, R.M.net_cost_adj];
        end
    end
    q = reshape(mean(v(:, :, active), 1), 4, []);
    fprintf('  exp12%s C=%4.1f alpha*=%.1f | fulfil %s| all-valid %s| all-full %s| net_adj(k) %s (%.0f min)\n', tag, C, c0.alpha_star, ...
        sprintf('%5.1f ', q(1, :)), sprintf('%4.2f ', q(2, :)), sprintf('%4.2f ', q(3, :)), sprintf('%5.0f ', q(4, :) / 1000), toc(t0) / 60);
    write_csv(fullfile(root, 'results', sprintf('exp12_capacity%s.csv', tag)), [{'C', 'realisation', 'strategy', 'alpha_star'}, hdr], rows);
    write_csv(fullfile(root, 'results', sprintf('exp12_strategies%s.csv', tag)), {'index'}, (1:size(S, 1))', S(:, 3));
end
out.rows = rows; out.hdr = hdr;
end

function rs = distinct_pai(label, N)
% first N realisations with pairwise different PAI weekdays (label 'pai<day>_<azure>_<weather>')
key = cellfun(@(s) strtok(s, '_'), label, 'UniformOutput', false);
[~, first] = unique(key, 'first');
rs = sort(first(:))';
rs = rs(1:min(N, numel(rs)));
end
