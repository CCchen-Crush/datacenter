function out = exp10_realism(ctx, root, C)
%EXP10_REALISM  Robustness to modelling choices questioned in review issue 6 / 3d:
%   liquid cooling (much higher, less temperature-sensitive cooling COP), limits on the swing of the
%   deferrable IT power (pause/resume of large jobs), and an assessment of pre-event load-up.
if nargin < 3 || isempty(C), C = [6 6 6]; end
cfg = {'base',            @(p) p;
       'liquid_cooling',  @liquid;
       'it_ramp_2MW',     @(p) setf(p, 'it', 'ramp_max', 2);
       'it_ramp_1MW',     @(p) setf(p, 'it', 'ramp_max', 1);
       'preload_charge',  @(p) setf(p, 'dr', 'c_pre', 1000);
       'power_capping',   @(p) setf(p, 'it', 'cap_on', true)};
S = [{'NoDR', 'open', 'NoDR'}; bench_list('core')];
rows = []; rl = {}; hdr = {};
for i = 1:size(cfg, 1)
    par = cfg{i, 2}(ctx.par);
    if strcmp(cfg{i, 1}, 'liquid_cooling')
        c = setup_case(par);                % COP series, baseline, connection limit and references all change
    else
        c = ctx; c.par = par; c.d = sys_derived(par);
    end
    c = apply_commit(c, C);
    c = prepare_benchmarks(c, struct('grid', [0.4 0.6 0.8 1.0]));
    for j = 1:size(S, 1)
        if strcmp(S{j, 1}, 'NoDR'), R = run_strategy(c, 'NoDR'); else, R = run_strategy(c, S{j, 1}, S{j, 2}); end
        [row, hdr] = metrics_row(R.M);
        rows = [rows; i, j, c.d.Pcap, c.alpha_star, row]; %#ok<AGROW>
        rl{end+1} = sprintf('%s|%s', cfg{i, 1}, S{j, 3}); %#ok<AGROW>
        fprintf('  exp10 %-15s %-6s ful=%6.2f%% valid=%d rb=%.2f pre=%.2f payG=%.2f net_adj=%.0f exrb=%.0f\n', cfg{i, 1}, S{j, 3}, ...
            100 * R.M.fulfil_rate, R.M.n_valid, R.M.max_rebound, R.M.preload_vs_nodr, R.M.payback_gap, R.M.net_cost_adj, R.M.net_cost_excl_rb);
    end
end
write_csv(fullfile(root, 'results', 'exp10_realism.csv'), [{'config', 'strategy', 'Pcap', 'alpha_star'}, hdr], rows, rl);
out.rows = rows; out.labels = rl;
end

function p = liquid(p)
% direct-to-chip liquid cooling with warm-water loops [A]: cooling-plant COP ~2.5x the air-cooled
% value at the reference temperature and still decreasing with the outdoor temperature
p.fac.cop_ref = 15; p.fac.cop_k = 0.25; p.fac.cop_min = 6; p.fac.cop_max = 20;
end

function p = setf(p, a, b, v)
p.(a).(b) = v;
end
