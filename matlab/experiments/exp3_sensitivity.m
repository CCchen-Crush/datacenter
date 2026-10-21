function out = exp3_sensitivity(ctx, root, opts)
%EXP3_SENSITIVITY  Event duration, interval, connection margin, commitment level; tau x gamma map.
%   Perfect-information plans (open loop) for IR-O / JR, closed-loop rules for IR-R, uniform C.
if nargin < 3, opts = struct(); end
C0 = getf(opts, 'C', 6);
strat = {'IR-R', 'rule'; 'IR-O', 'open'; 'JR', 'open'};
hdr = {'x', 'strategy', 'fulfil_pct', 'n_valid', 'max_rebound', 'net_cost', 'cost_op', 'lateness'};
% (a) duration
rows = [];
for D = getf(opts, 'durations', [0.5 1 1.5 2])
    c = set_events(ctx, [17, 17 + D + 1, 17 + 2 * (D + 1)], D, C0); c.all_visible = true;
    rows = [rows; run_set(c, strat, D)]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', 'exp3_duration.csv'), hdr, rows); out.duration = rows;
% (b) interval
rows = [];
for tau = getf(opts, 'intervals', [0.25 0.5 1 1.5 2 3])
    c = set_events(ctx, [17, 18 + tau, 19 + 2 * tau], 1, C0); c.all_visible = true;
    rows = [rows; run_set(c, strat, tau)]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', 'exp3_interval.csv'), hdr, rows); out.interval = rows;
% (c) connection margin
rows = [];
for g = getf(opts, 'gammas', [1.0 1.05 1.1 1.15 1.2 1.3])
    c = ctx_with_gamma(ctx, g); c = apply_commit(c, C0 * [1 1 1]); c.all_visible = true;
    rows = [rows; run_set(c, strat, g)]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', 'exp3_gamma.csv'), hdr, rows); out.gamma = rows;
% (d) commitment level
rows = [];
for C = getf(opts, 'Cs', [3 4 5 6 7 8 9])
    c = apply_commit(ctx, C * [1 1 1]); c.all_visible = true;
    rows = [rows; run_set(c, strat, C)]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', 'exp3_commitment.csv'), hdr, rows); out.commit = rows;
% (e) tau x gamma map
rows = [];
for g = getf(opts, 'map_gammas', [1.0 1.05 1.1 1.2 1.3])
    cg = ctx_with_gamma(ctx, g);
    for tau = getf(opts, 'map_taus', [0.25 0.5 1 1.5 2 3])
        c = set_events(cg, [17, 18 + tau, 19 + 2 * tau], 1, C0); c.all_visible = true;
        r = run_set(c, strat, tau);
        rows = [rows; repmat(g, size(r, 1), 1), r]; %#ok<AGROW>
    end
end
write_csv(fullfile(root, 'results', 'exp3_map.csv'), [{'gamma'}, hdr], rows); out.map = rows;
end

function rows = run_set(c, strat, x)
rows = [];
for i = 1:size(strat, 1)
    R = run_strategy(c, strat{i, 1}, strat{i, 2}); M = R.M;
    rows = [rows; x, i, 100 * M.fulfil_rate, M.n_valid, M.max_rebound, M.net_cost, M.cost_op, M.lateness]; %#ok<AGROW>
end
fprintf('  exp3 x=%-5g fulfil IR-R/IR-O/JR = %5.1f / %5.1f / %5.1f   maxRb = %.2f / %.2f / %.2f\n', x, rows(:, 3), rows(:, 5));
end

function v = getf(s, f, d)
if isfield(s, f), v = s.(f); else, v = d; end
end
