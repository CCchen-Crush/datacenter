function out = exp11_stylized(root, opts)
%EXP11_STYLIZED  Numerical check of Theorem 1 (stylised two-event recovery, see docs).
%   State at the start of the gap: compute backlog X (MWh-equivalent) and stored energy E_A. Gap tau
%   with a recovery channel of h MW of extra load (compute catch-up + storage charging, compute never
%   below its nominal rate), then event B of duration D_B. Constant deferrable arrival rate p_f, lag L
%   (backlog <= p_f*L), storage power P_s, efficiencies eta_c, eta_d.
%   Closed form (Theorem 1): c* = [X - p_f (L - D_B)]^+,  s_req = (P_s D_B - eta_d E_A) / (eta_c eta_d)
%     G_JR(H) = min(p_f D_B, p_f L - X + min(H, c*)) + min(P_s D_B, eta_d E_A + eta_c eta_d (H - c*)^+)
%     G_IR(H) = min(p_f D_B, p_f L - X + min(H, X)) + min(P_s D_B, eta_d E_A + eta_c eta_d (H - X)^+)
%     tau*_IR - tau*_JR = (X - c*) / h = min(X, p_f (L - D_B)) / h
%   Both are compared with a discrete-time LP of the same system (JR: joint LP; IR: lexicographic,
%   compute catch-up first, then storage).
if nargin < 2, opts = struct(); end
pf = 5; DB = 1; X = 5; Ps = 6; EA = 1.2; etc = 0.95; etd = 0.95; h = getf(opts, 'h', 3);
Ls = getf(opts, 'Ls', [1 1.5 2 3]); taus = getf(opts, 'taus', 0:0.25:4); del = 0.05;
rows = [];
for L = Ls
    cst = max(X - pf * (L - DB), 0); sreq = max(Ps * DB - etd * EA, 0) / (etc * etd);
    for tau = taus
        H = h * tau;
        gjr = min(pf * DB, pf * L - X + min(H, cst)) + min(Ps * DB, etd * EA + etc * etd * max(H - cst, 0));
        gir = min(pf * DB, pf * L - X + min(H, X)) + min(Ps * DB, etd * EA + etc * etd * max(H - X, 0));
        ljr = lp_capability(pf, DB, X, Ps, EA, etc, etd, h, L, tau, del, 'JR');
        lir = lp_capability(pf, DB, X, Ps, EA, etc, etd, h, L, tau, del, 'IR');
        rows = [rows; L, tau, H, gjr / DB, ljr / DB, gir / DB, lir / DB]; %#ok<AGROW>
    end
    tj = (cst + sreq) / h; ti = (X + sreq) / h;
    fprintf('  exp11 L=%.1f h: c*=%.2f s_req=%.2f MWh  tau*_JR=%.2f h  tau*_IR=%.2f h  (diff %.2f = min(X,p_f(L-D_B))/h = %.2f)\n', ...
        L, cst, sreq, tj, ti, ti - tj, min(X, pf * max(L - DB, 0)) / h);
end
err = max(abs([rows(:, 4) - rows(:, 5); rows(:, 6) - rows(:, 7)]));
fprintf('  exp11 max |closed form - LP| = %.3g MW over %d cases\n', err, size(rows, 1));
write_csv(fullfile(root, 'results', 'exp11_stylized.csv'), {'L_h', 'tau_h', 'H_MWh', 'G_JR_closed', 'G_JR_lp', 'G_IR_closed', 'G_IR_lp'}, rows);
out.rows = rows; out.err = err;
end

function G = lp_capability(pf, DB, X, Ps, EA, etc, etd, h, L, tau, del, mode)
% LP over gap (Ng steps) + event B (Nb steps). Variables per step: x (processing, MWh), Bk (backlog),
% pc, pd (MW), E (MWh). Returns the energy reduction delivered in B.
Ng = round(tau / del); Nb = round(DB / del); N = Ng + Nb;
nv = 5 * N; ix = @(k, n) (k - 1) * N + n;            % k: 1 x, 2 Bk, 3 pc, 4 pd, 5 E
lb = zeros(nv, 1); ub = inf(nv, 1);
ub(ix(2, 1:N)) = pf * L; ub(ix(3, 1:N)) = Ps; ub(ix(4, 1:N)) = Ps; ub(ix(5, 1:N)) = 1e3;
Aeq = sparse(0, nv); beq = []; A = sparse(0, nv); b = [];
for n = 1:N
    % backlog: Bk(n) = Bk(n-1) + pf*del - x(n)
    r = sparse(1, nv); r(ix(2, n)) = 1; r(ix(1, n)) = 1; rhs = pf * del;
    if n > 1, r(ix(2, n - 1)) = -1; else, rhs = rhs + X; end
    Aeq = [Aeq; r]; beq = [beq; rhs]; %#ok<AGROW>
    % storage: E(n) = E(n-1) + etc*pc*del - pd*del/etd
    r = sparse(1, nv); r(ix(5, n)) = 1; r(ix(3, n)) = -etc * del; r(ix(4, n)) = del / etd; rhs = 0;
    if n > 1, r(ix(5, n - 1)) = -1; else, rhs = EA; end
    Aeq = [Aeq; r]; beq = [beq; rhs]; %#ok<AGROW>
    if n <= Ng
        % gap: extra load (x/del - pf) + pc - pd <= h ; compute at least nominal: x >= pf*del ; no discharge
        r = sparse(1, nv); r(ix(1, n)) = 1 / del; r(ix(3, n)) = 1; r(ix(4, n)) = -1;
        A = [A; r]; b = [b; h + pf]; %#ok<AGROW>
        lb(ix(1, n)) = pf * del; ub(ix(4, n)) = 0;
    else
        ub(ix(3, n)) = 0;                                  % no charging during the event
    end
end
f = zeros(nv, 1);
gB = Ng + (1:Nb);
% delivered reduction in B: sum(pf*del - x + pd*del)
fB = zeros(nv, 1); fB(ix(1, gB)) = 1; fB(ix(4, gB)) = -del;
if strcmp(mode, 'IR')
    % stage 1: compute catches up as much and as early as possible in the gap
    f1 = zeros(nv, 1); f1(ix(1, 1:Ng)) = -(1 + 1e-3 * (Ng:-1:1)' / max(Ng, 1));
    x1 = glpk_solve(f1, A, b, Aeq, beq, lb, ub);
    lb(ix(1, 1:Ng)) = x1(ix(1, 1:Ng)); ub(ix(1, 1:Ng)) = x1(ix(1, 1:Ng));
end
x = glpk_solve(fB, A, b, Aeq, beq, lb, ub);
G = sum(pf * del - x(ix(1, gB)) + x(ix(4, gB)) * del);
end

function x = glpk_solve(f, A, b, Aeq, beq, lb, ub)
P = struct('f', f, 'Aineq', A, 'bineq', b, 'Aeq', Aeq, 'beq', beq, 'lb', lb, 'ub', ub, 'intcon', []);
if isempty(P.Aineq), P.Aineq = sparse(0, numel(f)); P.bineq = zeros(0, 1); end
s = solve_milp(P, struct());
if ~s.ok, error('exp11:lp', 'stylised LP not solved'); end
x = s.x;
end

function v = getf(s, f, d)
if isfield(s, f), v = s.(f); else, v = d; end
end
