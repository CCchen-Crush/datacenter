function out = exp20_capacity_configs(ctx, root, cfgs, tag, o)
%EXP20_CAPACITY_CONFIGS  Firm consecutive DR capacity C_rho (bisection over the uniform commitment, see
%   capacity_search) for system configurations: substitution curves of BESS size and connection margin,
%   contribution of the IES devices, pause/resume overhead of deferred work. Every configuration has
%     .name  label            .scen  event scenario (set_scenario)       .mods  ctx_with_par changes
%     .S     strategies {name, forecast mode, label}                     .lo, .hi  search bracket (MW)
%   Writes results/exp20_<tag>.csv (one capacity per configuration and strategy) and
%   results/exp20_<tag>_evals.csv (every evaluated commitment).
rho = getf(o, 'rho', 0.95); tol = getf(o, 'tol', 0.25); N = getf(o, 'N', 26);
rs = test_days(ctx, N);
caps = []; E = []; lc = {}; le = {}; t0 = tic;
for i = 1:numel(cfgs)
    cf = cfgs(i);
    c = set_scenario(ctx, cf.scen);
    if isfield(cf, 'mods') && ~isempty(cf.mods), c = ctx_with_par(c, cf.mods); end
    for k = 1:size(cf.S, 1)
        [Cr, Ek] = capacity_search(c, cf.S(k, :), rho, struct('lo', cf.lo, 'hi', cf.hi, 'tol', tol, 'rs', rs));
        caps = [caps; Cr, rho, size(Ek, 1)]; lc{end + 1} = sprintf('%s|%s', cf.name, cf.S{k, 3}); %#ok<AGROW>
        E = [E; Ek]; le = [le, repmat({sprintf('%s|%s', cf.name, cf.S{k, 3})}, 1, size(Ek, 1))]; %#ok<AGROW>
        fprintf('  exp20%s %-12s %-6s C_%.2f = %5.2f MW (%d evaluations, %.0f min)\n', tag, cf.name, cf.S{k, 3}, rho, Cr, ...
            size(Ek, 1), toc(t0) / 60);
    end
end
write_csv(fullfile(root, 'results', sprintf('exp20_%s.csv', tag)), {'C_rho', 'rho', 'n_eval'}, caps, lc);
write_csv(fullfile(root, 'results', sprintf('exp20_%s_evals.csv', tag)), {'C', 'share', 'days', 'stopped'}, E, le);
out.caps = caps; out.labels = lc;
end

function v = getf(s, f, d)
if isfield(s, f), v = s.(f); else, v = d; end
end
