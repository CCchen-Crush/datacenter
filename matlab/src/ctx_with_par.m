function c = ctx_with_par(ctx, mods)
%CTX_WITH_PAR  Same case study with modified system parameters (sensitivity and ablation). The DR
%   baseline, connection limit, no-DR reference and nominal SOC trajectories are rebuilt with the new
%   parameters (setup_case on the already loaded data), the events and scenario of ctx are kept.
%   mods fields (all optional):
%     gamma      connection limit / typical-day peak import
%     lag_scale  factor on the lag bounds L_c of the deferrable classes (0 = no compute flexibility)
%     bess_P     BESS power (MW); energy follows at the base 2-h ratio (0 = no BESS)
%     tes_on     false = no chilled-water storage
%     c_rb       rebound assessment (CNY/MW per event)
par = ctx.par;
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
if isfield(mods, 'c_rb'), par.dr.c_rb = mods.c_rb; end
c = setup_case(par, ctx.inp);
K = numel(ctx.ev); E = ctx.par.ev;                 % event definition (start, end, notice) of ctx
c = set_events(c, [E.t0], [E.t1] - [E.t0], [ctx.ev.C], [E.notice], [ctx.ev.prob]);
for k = 1:K, c.ev(k).called = ctx.ev(k).called; end
if isfield(ctx, 'scen'), c.scen = ctx.scen; end
end
