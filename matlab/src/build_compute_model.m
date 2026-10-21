function [P, ix] = build_compute_model(par, st, sc, ev, opt)
%BUILD_COMPUTE_MODEL  IT-side scheduler used by the independent-recovery benchmark (IR-O, stage 1).
%   The IT scheduler sees only its own state (backlog), an IT power budget that keeps the facility
%   under the connection limit assuming storage is idle, the TOU price, and its own DR share
%   alpha*C_k as a per-step power-reduction target. It ignores storage recovery needs.
d = sys_derived(par); dt = par.dt; H = sc.H; t0 = st.t;
a = par.fac.a_aux; th = par.fac.theta;
m = lpb_new();
phi = 1 + a + th ./ sc.cop(:, 1);                       % facility MW per IT MW
for c = 1:3
    [m, Y{c}] = lpb_addvar(m, H, 0, Inf, dt * sc.price .* phi * d.pdyn);
    [m, B{c}] = lpb_addvar(m, H, 0, Inf, dt * par.qos.c_jct);
    [m, V{c}] = lpb_addvar(m, H, 0, Inf, dt * par.qos.c_late);
end
r = (1:H)'; one = ones(H,1);
capfree = par.it.u_max * par.it.Ngpu - sc.inf(:,1) - sc.fix(:,1);
m = lpb_addle(m, [r; r; r], [Y{1}; Y{2}; Y{3}], [one; one; one], capfree);
% IT power budget (compute has priority on the connection headroom)
base_it = d.Pfix + d.pdyn * (par.it.k_inf * sc.inf(:,1) + sc.fix(:,1));
qac = min(par.ac.cop * d.kh * opt.pgt_nom(:), par.ac.Qmax);
fac_other = (1 + a) * base_it + par.fac.P_aux0 + (th * base_it + par.fac.Q0 - qac) ./ sc.cop(:,1) ...
            - opt.pgt_nom(:) - sc.pv(:,1);
budget = d.Pcap - fac_other;
m = lpb_addle(m, [r; r; r], [Y{1}; Y{2}; Y{3}], repmat(phi * d.pdyn, 3, 1), max(budget, 0));
for c = 1:3
    L = d.lag(c); remc = st.rem(:, c); B0 = sum(remc);
    Dk = cumsum(remc); Dk = Dk(min(t0 + (0:H-1)', numel(Dk)));
    arr = sc.flex(:, c, 1) * dt; arr(1) = 0;
    A = B0 + cumsum(arr); Dn = zeros(H,1);
    if H > L, Dn(L+1:end) = cumsum(arr(1:H-L)); end
    Bmax = max(A - (Dk + Dn), 0);
    I = [r; r; (2:H)']; J = [B{c}; Y{c}; B{c}(1:end-1)]; Vv = [one; dt*one; -ones(H-1,1)];
    rhs = arr; rhs(1) = rhs(1) + B0;
    m = lpb_addeq(m, I, J, Vv, rhs);
    m = lpb_addle(m, [r; r], [B{c}; V{c}], [one; -one], Bmax);
end
% DR share of the IT side (per-step power-reduction target relative to nominal execution)
ynom = sum(sc.flex(:, :, 1), 2); ynom(1) = opt.ynom_now;
for k = 1:numel(ev)
    e = ev(k);
    if ~opt.visible(k) || e.e < t0 || e.s > t0 + H - 1, continue; end
    hk = (max(e.s, t0):min(e.e, t0 + H - 1)) - t0 + 1; nh = numel(hk);
    [m, SFC] = lpb_addvar(m, nh, 0, Inf, dt * e.price * (1 + par.dr.kappa_dev));
    tgt = opt.alpha * e.C;
    rr = (1:nh)';
    I = [rr; rr; rr; rr]; J = [Y{1}(hk); Y{2}(hk); Y{3}(hk); SFC];
    Vv = [repmat(phi(hk) * d.pdyn, 3, 1); -ones(nh,1)];
    m = lpb_addle(m, I, J, Vv, phi(hk) * d.pdyn .* ynom(hk) - tgt);
end
P = lpb_finalize(m);
ix.Y = Y; ix.B = B; ix.V = V; ix.H = H;
end
