function ref = run_nodr(par, inp, base)
%RUN_NODR  Nominal (no-DR) operation on the realised data inp.real: TOU storage schedule,
%   ASAP computing, economic gas-engine rule. Used as the reference for the "true" reduction,
%   the pre-event load-up and the payback metrics, and for the nominal SOC references.
noev = struct('s', {}, 'e', {}, 'win', {});
ref = run_closed_loop(par, inp.real, base, noev, @nominal_wrap, struct('par', par, 'inp', inp));
end

function [u, info] = nominal_wrap(st, data, ctx)
u = planner_nominal(st, ctx.par, data, ctx.inp.price(st.t));
info.ok = true; info.time = 0; info.fallback = false;
end
