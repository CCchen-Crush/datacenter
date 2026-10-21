function c = ctx_with_gamma(ctx, g)
%CTX_WITH_GAMMA  Same case with connection limit gamma * typical-day peak (re-runs the no-DR reference).
c = ctx; c.par.cap.gamma = g; c.par.cap.Pcap_abs = g * ctx.par.cap.Pbase_peak; c.d = sys_derived(c.par);
c.ref = run_nodr(c.par, c.inp, c.base); c.ref_eval = c.ref;
c.pgt_nom = c.ref.log.pgt; c.Eref = c.ref.log.E; c.Sref = c.ref.log.S;
end
