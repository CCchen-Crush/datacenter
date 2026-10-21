function r = rule_common(st, par, data, price_t)
%RULE_COMMON  Quantities shared by the rule-based controllers for the current step.
d = sys_derived(par); dt = par.dt; t = st.t;
h = mod((t - 1) * dt, 24);
r.h = h;
r.is_peak = (h >= 14 && h < 22);
r.is_valley = (h < 6) || (h >= 11 && h < 13);
if h < 6, r.valley_left = 6 - h; elseif h >= 11 && h < 13, r.valley_left = 13 - h; else, r.valley_left = 0; end
if r.is_peak, r.peak_left = 22 - h; else, r.peak_left = 0; end
r.due = sum(st.rem(1:t, :), 1) / dt;          % GPUs needed now to meet deadlines
r.avail = sum(st.rem, 1) / dt;
r.gfree = par.it.u_max * par.it.Ngpu - data.inf - data.fix;
% gas engine: economic rule (on in peak hours, ramp from 13:30)
if (h >= 13.5 && h < 22), tgt = par.gt.Pmax; else, tgt = 0; end
r.pgt = min(max(tgt, st.pgt_prev - par.gt.ramp), st.pgt_prev + par.gt.ramp);
r.hac = min(d.kh * r.pgt, par.ac.Qmax / par.ac.cop);
r.phi = 1 + par.fac.a_aux + par.fac.theta / data.cop;   % facility MW per MW of IT power
end
