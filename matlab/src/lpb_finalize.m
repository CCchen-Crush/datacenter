function P = lpb_finalize(m)
%LPB_FINALIZE  Assemble sparse matrices for SOLVE_MILP.
P.f  = m.f;  P.lb = m.lb;  P.ub = m.ub;
P.intcon = find(m.isint);
if m.le.nr > 0
    P.Aineq = sparse(cat(1, m.le.I{:}), cat(1, m.le.J{:}), cat(1, m.le.V{:}), m.le.nr, m.n);
    P.bineq = cat(1, m.le.b{:});
else
    P.Aineq = sparse(0, m.n); P.bineq = zeros(0,1);
end
if m.eq.nr > 0
    P.Aeq = sparse(cat(1, m.eq.I{:}), cat(1, m.eq.J{:}), cat(1, m.eq.V{:}), m.eq.nr, m.n);
    P.beq = cat(1, m.eq.b{:});
else
    P.Aeq = sparse(0, m.n); P.beq = zeros(0,1);
end
end
