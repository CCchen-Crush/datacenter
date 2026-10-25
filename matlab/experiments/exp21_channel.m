function out = exp21_channel(ctx, root, C, N)
%EXP21_CHANNEL  Nominal versus actual recovery channel on the operating days. For every test day and window
%   (event interval and 2-h post-event window of S1 and S2) it compares
%     H_nom  = sum max(Pcap - P_base, 0) dt     nominal channel of (1), measured against the DR baseline
%     H_act  = sum max(Pcap - P_noDR, 0) dt     actual channel of the realised day (no-DR import on the realised
%                                               loads, PV and COP, with the TOU storage schedule)
%     H_idle = the same with the BESS and TES of the no-DR operation held idle (assumption H1)
%   JR-D is then run at the uniform commitment C in both scenarios; the channel it draws on is
%     U = sum (P_grid - P_noDR) dt over the interval (energy imported above the no-DR operation),
%   which is set against H_nom and H_act. Writes results/exp21_channel.csv and results/exp21_channel_jrd.csv.
if nargin < 3 || isempty(C), C = 7; end
if nargin < 4 || isempty(N), N = 26; end
par = ctx.par; dt = par.dt; Pcap = ctx.d.Pcap; rs = test_days(ctx, N);
W = {'S1_int', [18 19]; 'S1_post', [20 22]; 'S2_int', [18 18.5]; 'S2_post', [19.5 21.5]};
stp = @(h) round(h(1) / dt) + 1 : round(h(2) / dt);          % steps of [h1, h2) (step 1 = 00:00-00:15)
rows = []; t0 = tic;
for j = 1:numel(rs)
    c = use_realization(ctx, rs(j)); L = c.ref_eval.log;
    pidle = L.pg + L.pdis - L.pch + (L.qtd - L.qtc) ./ L.cop;   % no-DR import with storage idle (chiller at the COP)
    for w = 1:size(W, 1)
        tt = stp(W{w, 2});
        hn = sum(max(Pcap - ctx.base(tt), 0)) * dt; ha = sum(max(Pcap - L.pg(tt), 0)) * dt;
        hi = sum(max(Pcap - pidle(tt), 0)) * dt;
        dev = L.pg(tt) - ctx.base(tt);
        rows = [rows; rs(j), w, hn, ha, hi, mean(dev), max(dev), mean(L.pdis(tt) - L.pch(tt))]; %#ok<AGROW>
    end
end
write_csv(fullfile(root, 'results', 'exp21_channel.csv'), ...
    {'realisation', 'window', 'H_nom_MWh', 'H_act_MWh', 'H_idle_MWh', 'dev_mean_MW', 'dev_max_MW', 'bess_net_dis_MW'}, rows);
fprintf('  exp21 channel: %d days (%.1f min)\n', numel(rs), toc(t0) / 60);
J = []; scen = {'S1', 'S2-30'}; win = {[18 19], [18 18.5]};
for q = 1:2
    c0 = apply_commit(set_scenario(ctx, scen{q}), C * [1 1]);
    tt = stp(win{q});
    for j = 1:numel(rs)
        c = use_realization(c0, rs(j)); L0 = c.ref_eval.log;
        R = run_strategy(c, 'JR', 'expected'); L = R.log;
        hn = sum(max(Pcap - ctx.base(tt), 0)) * dt; ha = sum(max(Pcap - L0.pg(tt), 0)) * dt;
        U = sum(L.pg(tt) - L0.pg(tt)) * dt;
        J = [J; q, rs(j), hn, ha, U, max(L.pg(tt)), R.M.all_full, R.M.avg_red(1), R.M.avg_red(2)]; %#ok<AGROW>
    end
    fprintf('  exp21 JR-D %s at %.1f MW done (%.1f min)\n', scen{q}, C, toc(t0) / 60);
    write_csv(fullfile(root, 'results', 'exp21_channel_jrd.csv'), ...
        {'scenario', 'realisation', 'H_nom_MWh', 'H_act_MWh', 'U_MWh', 'pg_max_MW', 'all_full', 'red1_MW', 'red2_MW'}, J);
end
out.rows = rows; out.jrd = J;
end
