function c = ctx_with_gamma(ctx, g)
%CTX_WITH_GAMMA  Same case with connection limit gamma * typical-day peak (re-runs the no-DR reference).
c = ctx; c.par.cap.gamma = g; c.par.cap.Pcap_abs = g * ctx.par.cap.Pbase_peak; c.d = sys_derived(c.par);
noev = struct('s', {}, 'e', {}, 'win', {});
c.ref = run_closed_loop(c.par, c.inp.real, c.base, noev, @nom, struct('par', c.par, 'inp', c.inp));
c.pgt_nom = c.ref.log.pgt; c.Eref = c.ref.log.E; c.Sref = c.ref.log.S;
end

function [u, info] = nom(st, data, ctx)
u = planner_nominal(st, ctx.par, data, ctx.inp.price(st.t));
info.ok = true; info.time = 0; info.fallback = false;
end
