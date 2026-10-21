function d = sys_derived(par)
%SYS_DERIVED  Derived constants used by all modules.
it = par.it;
d.pdyn   = it.p_peak - it.p_idle;                 % MW per busy GPU (dynamic part)
d.Pfix   = it.Ngpu * it.p_idle + it.P_other;      % MW IT power independent of scheduling
d.lag    = round(it.lag_h / par.dt);              % steps
d.kh     = par.gt.eta_h / par.gt.eta_e;           % recovered heat per MW_e
d.cop_design = par.fac.cop_ref - par.fac.cop_k * (35 - par.fac.T_ref);
Pit_max  = it.Ngpu * it.p_peak + it.P_other;
d.Pdesign = (1 + par.fac.a_aux) * Pit_max + par.fac.P_aux0 + (par.fac.theta * Pit_max + par.fac.Q0) / d.cop_design;
if isfield(par.cap, 'Pcap_abs') && ~isempty(par.cap.Pcap_abs)
    d.Pcap = par.cap.Pcap_abs;            % connection limit set from the typical-day peak
else
    d.Pcap = d.Pdesign;                   % before the baseline is known: design peak
end
d.nlagmax = max(d.lag);
d.eps_ref = (1 + par.fac.a_aux + par.fac.theta / d.cop_design) * d.pdyn;   % facility MWh per GPU-h
d.price_flat = par.price.nonfloat + par.price.purchase;
d.c_B_end = d.eps_ref * d.price_flat;          % CNY per GPU-h of backlog left at the end of the window
end
