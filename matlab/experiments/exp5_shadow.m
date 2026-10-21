function out = exp5_shadow(ctx, root, C, tag)
%EXP5_SHADOW  Shadow prices of the recovery channel and of the two recovery states
%   (perfect-information joint model; binaries fixed at the MILP optimum, LP re-solved for duals),
%   and a numerical check of Proposition 2 (equal marginal value / single channel price):
%     storage charging interior     :  eta_c * nu(t)        = lambda_el(t) + c_deg
%     storage discharging interior  :  nu(t) / eta_d        = lambda_el(t) - c_deg
%     compute catch-up interior     :  mu_c(t)              = eps(t) * lambda_el(t)
%   with lambda_el the dual of the electric balance (CNY/MWh), nu the value of stored energy,
%   mu_c the marginal cost of backlog of class c (CNY/GPU-h), eps(t) = pdyn (1 + a + theta/COP(t)).
if nargin < 4, tag = ''; end
c = apply_commit(ctx, C);
par = c.par; dt = par.dt; T = par.Tsim; d = c.d;
st = state_init(par, numel(c.ev)); st = add_arrivals(st, c.inp.real.flex(1, :), par);
cc = c; cc.fmode = 'oracle';
sc = make_scen(c.inp, par, c.base, 1, T, cc);
act = event_activity(c, 1, 1, 'oracle');
opt = struct('milp', true, 'visible', any(act, 2), 'active', act, 'terminal', true, 'Eref_end', c.Eref(end), 'Sref_end', c.Sref(end));
[P, ix] = build_model(par, st, sc, c.ev, opt);
s1 = solve_milp(P, c.solver);
P2 = P; P2.lb(P.intcon) = round(s1.x(P.intcon)); P2.ub(P.intcon) = round(s1.x(P.intcon)); P2.intcon = [];
s2 = solve_milp(P2, c.solver);
lam_el = s2.marg_eq(ix.row_el) / dt;               % marginal value of facility electricity (CNY/MWh)
lam_cap = -s2.marg_ineq(ix.row_cap) / dt;          % CNY per MWh of extra connection capacity
lam_rb = zeros(T, 1);                              % CNY per MWh of extra rebound allowance (post-event windows)
for k = 1:numel(ix.ev)
    if isfield(ix.ev(k), 'row_rb') && ~isempty(ix.ev(k).row_rb)
        lam_rb(ix.ev(k).hw) = lam_rb(ix.ev(k).hw) - s2.marg_ineq(ix.ev(k).row_rb(:, 1)) / dt;
    end
end
val_E = -s2.marg_eq(ix.row_E);                     % CNY per MWh stored in the BESS
val_S = -s2.marg_eq(ix.row_S);                     % CNY per MWh_th stored in the TES
cost_B = zeros(T, 3); dl_B = zeros(T, 3);
for k = 1:3
    cost_B(:, k) = s2.marg_eq(ix.row_B{k});        % CNY per extra GPU-h of backlog
    dl_B(:, k) = -s2.marg_ineq(ix.row_Bmax{k});    % CNY per GPU-h of extra deadline slack
end
%% Proposition 2 check (interior decisions only)
x = s2.x; tol = 1e-4;
pch = x(ix.PCH); pds = x(ix.PDS); y = [x(ix.Y{1}), x(ix.Y{2}), x(ix.Y{3})]; qec = x(ix.QEC);
eps_t = d.pdyn * (1 + par.fac.a_aux + par.fac.theta ./ sc.cop(:, 1));
capfree = par.it.u_max * par.it.Ngpu - sc.inf(:, 1) - sc.fix(:, 1);
ich = pch > tol & pch < par.bess.Pmax - tol & pds < tol;
idis = pds > tol & pds < par.bess.Pmax - tol & pch < tol;
r_ch = par.bess.eta_c * val_E(ich) - (lam_el(ich) + par.bess.c_deg);
r_dis = val_E(idis) / par.bess.eta_d - (lam_el(idis) - par.bess.c_deg);
ok_it = sum(y, 2) < capfree - 1 & qec > tol & qec < par.fac.Qec_max - tol;
r_y = [];
for k = 1:3
    iy = ok_it & y(:, k) > tol;
    r_y = [r_y; (cost_B(iy, k) - eps_t(iy) .* lam_el(iy)) ./ max(abs(cost_B(iy, k)), 1)]; %#ok<AGROW>
end
kkt = [numel(r_ch), max_abs(r_ch); numel(r_dis), max_abs(r_dis); numel(r_y), max_abs(r_y)];
h = (0:T-1)' * dt;
M = [h, s2.x(ix.PG), c.base, lam_cap, lam_rb, lam_cap + lam_rb, val_E, val_S, cost_B, dl_B, c.d.Pcap * ones(T, 1), ...
     lam_el, sc.price(:), eps_t, pch, pds, y];
hdr = {'hour', 'pg', 'base', 'lambda_cap', 'lambda_rb', 'lambda_headroom', 'value_E', 'value_S', 'cost_B1', 'cost_B2', 'cost_B3', ...
       'deadline_B1', 'deadline_B2', 'deadline_B3', 'Pcap', 'lambda_el', 'price', 'eps', 'pch', 'pdis', 'y1', 'y2', 'y3'};
write_csv(fullfile(root, 'results', sprintf('exp5_shadow%s.csv', tag)), hdr, M);
write_csv(fullfile(root, 'results', sprintf('exp5_kkt%s.csv', tag)), {'n_steps', 'max_abs_residual'}, kkt, ...
    {'BESS_charge (CNY/MWh)', 'BESS_discharge (CNY/MWh)', 'compute_catchup (relative)'});
gaps = false(T, 1); ev = c.ev;
for k = 1:numel(ev) - 1, gaps(ev(k).e + 1:ev(k+1).s - 1) = true; end
fprintf('  exp5%s MILP %.1fs / LP %.1fs; gaps: max lambda_cap = %.0f, max lambda_rb = %.0f CNY/MWh; value_E at event starts = %s\n', ...
    tag, s1.time, s2.time, max([lam_cap(gaps); 0]), max([lam_rb(gaps); 0]), mat2str(round(val_E([ev.s] - 1)')));
fprintf('  exp5%s Prop.2 residuals: charge %d steps max %.2g | discharge %d steps max %.2g | catch-up %d steps max %.2g\n', tag, kkt');
out.M = M; out.hdr = hdr; out.kkt = kkt;
end

function v = max_abs(r)
if isempty(r), v = NaN; else, v = max(abs(r)); end
end
