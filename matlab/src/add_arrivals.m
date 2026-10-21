function st = add_arrivals(st, a, par)
%ADD_ARRIVALS  Nominal work of step st.t (a: 1x3 busy GPUs) enters the backlog with deadline t+L_c.
d = sys_derived(par);
for c = 1:3
    st.rem(st.t + d.lag(c), c) = st.rem(st.t + d.lag(c), c) + a(c) * par.dt;
end
end
