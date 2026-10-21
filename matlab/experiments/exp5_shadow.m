function out = exp5_shadow(ctx, root, DA, tag)
%EXP5_SHADOW  Shadow prices of the connection limit, stored energy and computing backlog
%   (perfect-information joint model; binaries fixed at the MILP optimum, LP re-solved for duals).
if nargin < 4, tag = ''; end
c = apply_commit(ctx, DA.C, DA); c.all_visible = true;
par = c.par; dt = par.dt; T = par.Tsim;
st = state_init(par, numel(c.ev)); st = add_arrivals(st, c.inp.real.flex(1, :), par);
cc = c; cc.fmode = 'oracle';
sc = make_scen(c.inp, par, c.base, 1, T, cc);
opt = struct('milp', true, 'visible', true(numel(c.ev),1), 'terminal', true, 'Eref_end', c.Eref(end), 'Sref_end', c.Sref(end));
[P, ix] = build_model(par, st, sc, c.ev, opt);
s1 = solve_milp(P, c.solver);
P2 = P; P2.lb(P.intcon) = round(s1.x(P.intcon)); P2.ub(P.intcon) = round(s1.x(P.intcon)); P2.intcon = [];
s2 = solve_milp(P2, c.solver);
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
h = (0:T-1)' * dt;
M = [h, s2.x(ix.PG), c.base, lam_cap, lam_rb, lam_cap + lam_rb, val_E, val_S, cost_B, dl_B, c.d.Pcap * ones(T, 1)];
hdr = {'hour', 'pg', 'base', 'lambda_cap', 'lambda_rb', 'lambda_headroom', 'value_E', 'value_S', 'cost_B1', 'cost_B2', 'cost_B3', 'deadline_B1', 'deadline_B2', 'deadline_B3', 'Pcap'};
write_csv(fullfile(root, 'results', sprintf('exp5_shadow%s.csv', tag)), hdr, M);
fprintf('  exp5%s MILP %.1fs / LP %.1fs; max lambda_cap = %.0f, max lambda_rb = %.0f CNY/MWh; mean value_E at event starts = %.0f\n', tag, s1.time, s2.time, max(lam_cap), max(lam_rb), mean(val_E([c.ev.s])));
out.M = M; out.hdr = hdr;
end
