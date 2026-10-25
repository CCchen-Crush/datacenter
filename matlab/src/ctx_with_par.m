function c = ctx_with_par(ctx, mods)
%CTX_WITH_PAR  Same case study with modified system parameters (sensitivity and ablation). The DR
%   baseline, connection limit, no-DR reference and nominal SOC trajectories are rebuilt with the new
%   parameters (setup_case on the already loaded data), the events and scenario of ctx are kept.
%   mods fields (all optional):
%     gamma      connection limit / typical-day peak import
%     lag_scale  factor on the lag bounds L_c of the deferrable classes (0 = no compute flexibility)
%     bess_P     BESS power (MW); energy follows at the base 2-h ratio (0 = no BESS)
%     tes_on     false = no chilled-water storage
%     gt_on      false = no gas engine (and therefore no recovered heat for the absorption chiller)
%     ac_on      false = no absorption chiller
%     overhead   extra work per unit of deferred work (pause/resume overhead, plant only)
%     keep_Pcap  true = keep the connection limit of ctx (equipment changes do not resize the connection)
%     c_rb       rebound assessment (CNY/MW per event)
%     flex_share part of the training and batch work that is deferrable (Flex 1-3); the inputs are reloaded
%     idle_frac  idle GPU power as a share of the peak GPU power (the dynamic part is the rest)
%     price_da   day-ahead DR unit price (CNY/MWh); the intraday notice coefficients are kept
%     c_jct      delay price of deferred work (CNY per GPU-h per h)
%     horizon_h  MPC prediction horizon (h)
%     kappa      shortfall assessment factor (kappa_dev; 0 = no monetary assessment, the Jiangsu rules)
par = ctx.par; reload = false;
if isfield(mods, 'flex_share'), par.it.flex_share = mods.flex_share; reload = true; end
if isfield(mods, 'idle_frac'), par.it.p_idle = mods.idle_frac * par.it.p_peak; end
if isfield(mods, 'price_da'), par.dr.price_da = mods.price_da; end
if isfield(mods, 'c_jct'), par.qos.c_jct = mods.c_jct; end
if isfield(mods, 'horizon_h'), par.mpc.H = round(mods.horizon_h / par.dt); end
if isfield(mods, 'kappa'), par.dr.kappa_dev = mods.kappa; end
if isfield(mods, 'gamma'), par.cap.gamma = mods.gamma; end
if isfield(mods, 'lag_scale'), par.it.lag_h = par.it.lag_h * mods.lag_scale; end
if isfield(mods, 'bess_P')
    P = mods.bess_P; E = 2 * P;
    if P <= 0
        par.bess.Pmax = 0; par.bess.Emin = 0.1; par.bess.Emax = 0.1 + 1e-6; par.bess.Ecap = 0.1; par.bess.E0 = 0.1;
    else
        par.bess.Pmax = P; par.bess.Ecap = E; par.bess.Emax = 0.95 * E; par.bess.Emin = 0.10 * E; par.bess.E0 = 0.5 * E;
    end
end
if isfield(mods, 'tes_on') && ~mods.tes_on, par.tes.Qmax = 0; end
if isfield(mods, 'gt_on') && ~mods.gt_on, par.gt.Pmax = 0; end
if isfield(mods, 'ac_on') && ~mods.ac_on, par.ac.Qmax = 0; end
if isfield(mods, 'overhead'), par.it.overhead = mods.overhead; end
if isfield(mods, 'c_rb'), par.dr.c_rb = mods.c_rb; end
if isfield(mods, 'keep_Pcap') && mods.keep_Pcap, par.cap.Pcap_fix = ctx.d.Pcap; end
if reload, c = setup_case(par); else, c = setup_case(par, ctx.inp); end
K = numel(ctx.ev); E = ctx.par.ev;                 % event definition (start, end, notice) of ctx
c = set_events(c, [E.t0], [E.t1] - [E.t0], [ctx.ev.C], [E.notice], [ctx.ev.prob]);
for k = 1:K, c.ev(k).called = ctx.ev(k).called; end
if isfield(ctx, 'scen'), c.scen = ctx.scen; end
end
