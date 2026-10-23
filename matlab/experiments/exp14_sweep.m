function out = exp14_sweep(ctx, root, cfgs, tag, opts)
%EXP14_SWEEP  Closed-loop scenario sweep used by the sensitivity, ablation and reliability-region
%   studies. Every configuration cfgs(i) defines
%     .name   label
%     .scen   'S1' | 'S2-<min>' | 'S3' (set_scenario), or .gap (h) for two one-hour events 17 h and
%             18 h + gap
%     .mods   parameter changes for ctx_with_par (gamma, lag_scale, bess_P, tes_on), optional
%     .C      commitment vectors, one per row (K columns, or one column = uniform)
%     .S      strategies {name, forecast mode, label} (default: IR-O*, IR-P, JR-M, JR-D)
%   For every configuration and commitment the benchmarks are prepared day-ahead (alpha* of IR-O*
%   back-tested on the day-ahead scenarios, IR-P channel price) unless opts.alpha_fix is given, and
%   every strategy is run in closed loop on the PAI test days (opts.N distinct weekdays).
%   Writes results/exp14_<tag>.csv: one row per (configuration, commitment, day, strategy).
if nargin < 5, opts = struct(); end
N = getf(opts, 'N', 26);
rs = distinct_pai(ctx.inp.mc.label, N);
if isfield(opts, 'days'), rs = rs(opts.days); end
S0 = {'IR-O*', 'expected', 'IR-O*'; 'IR-P', 'expected', 'IR-P'; 'JR-M', 'expected', 'JR-M'; 'JR', 'expected', 'JR-D'};
rows = []; hdr = {}; names = {}; t0 = tic;
for i = 1:numel(cfgs)
    cf = cfgs(i); S = S0; if isfield(cf, 'S') && ~isempty(cf.S), S = cf.S; end
    names{i} = cf.name; %#ok<AGROW>
    if isfield(cf, 'gap') && ~isempty(cf.gap)
        c = set_events(ctx, [17, 18 + cf.gap], 1, 6, [24 24]); c.scen = sprintf('gap%.2f', cf.gap);
    else
        c = set_scenario(ctx, cf.scen);
    end
    if isfield(cf, 'mods') && ~isempty(cf.mods), c = ctx_with_par(c, cf.mods); end
    K = numel(c.ev); Cm = cf.C; if size(Cm, 2) == 1, Cm = repmat(Cm, 1, K); end
    needs_ir = any(strncmp(S(:, 1), 'IR', 2));
    for j = 1:size(Cm, 1)
        c0 = apply_commit(c, Cm(j, :));
        if needs_ir
            if isfield(opts, 'alpha_fix')
                c0.alpha_star = opts.alpha_fix(max(Cm(j, :))); c0.lambda_hr_da = dayahead_prices(c0);
            else
                c0 = prepare_benchmarks(c0, struct('verbose', false));
            end
        end
        if ~isfield(c0, 'alpha_star'), c0.alpha_star = NaN; end
        q = zeros(numel(rs), size(S, 1));
        for r = 1:numel(rs)
            cr = use_realization(c0, rs(r));
            for k = 1:size(S, 1)
                R = run_strategy(cr, S{k, 1}, S{k, 2});
                [row, hdr] = metrics_row(R.M);
                rows = [rows; i, j, pad3(Cm(j, :)), rs(r), k, c0.alpha_star, row]; %#ok<AGROW>
                q(r, k) = R.M.all_full;
            end
        end
        fprintf('  exp14%s %-12s C=%-14s alpha*=%.1f | all-full %s (%.0f min)\n', tag, cf.name, mat2str(Cm(j, :)), ...
            c0.alpha_star, sprintf('%4.2f ', mean(q, 1)), toc(t0) / 60);
        write_csv(fullfile(root, 'results', sprintf('exp14_%s.csv', tag)), ...
            [{'cfg', 'cj', 'C1', 'C2', 'C3', 'realisation', 'strategy', 'alpha_star'}, hdr], rows);
        write_csv(fullfile(root, 'results', sprintf('exp14_%s_cfg.csv', tag)), {'cfg'}, (1:numel(names))', names);
        write_csv(fullfile(root, 'results', sprintf('exp14_%s_strategies.csv', tag)), {'index'}, (1:size(S, 1))', S(:, 3));
    end
end
out.rows = rows; out.hdr = hdr;
end

function v = pad3(x)
v = [x(:)', nan(1, 3 - numel(x))];
end

function rs = distinct_pai(label, N)
key = cellfun(@(s) strtok(s, '_'), label, 'UniformOutput', false);
[~, first] = unique(key, 'first');
rs = sort(first(:))';
rs = rs(1:min(N, numel(rs)));
end

function v = getf(s, f, d)
if isfield(s, f), v = s.(f); else, v = d; end
end
