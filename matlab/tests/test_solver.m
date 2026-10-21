% Unit test: solver wrapper, LP builder and dual-sign convention.
addpath(fullfile(fileparts(mfilename('fullpath')), '..', 'src'));
% min x1 + 2 x2  s.t. x1 + x2 >= 3 (-> -x1 - x2 <= -3), x1 <= 2, x1 - x2 == 0.5
m = lpb_new();
[m, x] = lpb_addvar(m, 2, 0, 10, [1; 2]);
[m, r1] = lpb_addle(m, [1 1], x, [-1 -1], -3);
[m, r2] = lpb_addle(m, 1, x(1), 1, 2);
[m, r3] = lpb_addeq(m, [1 1], x, [1 -1], 0.5);
P = lpb_finalize(m);
s = solve_milp(P);
assert(s.ok, 'LP not solved');
assert(abs(s.x(1) - 1.75) < 1e-6 && abs(s.x(2) - 1.25) < 1e-6, 'wrong LP solution');
% finite-difference check of marginal of r1 (rhs -3 -> -3+d)
d = 1e-3; P2 = P; P2.bineq(r1) = P2.bineq(r1) + d; s2 = solve_milp(P2);
fd = (s2.fval - s.fval) / d;
assert(abs(fd - s.marg_ineq(r1)) < 1e-4, sprintf('dual sign mismatch: fd=%g marg=%g', fd, s.marg_ineq(r1)));
P3 = P; P3.beq(r3) = P3.beq(r3) + d; s3 = solve_milp(P3);
fd3 = (s3.fval - s.fval) / d;
assert(abs(fd3 - s.marg_eq(r3)) < 1e-4, sprintf('eq dual mismatch: fd=%g marg=%g', fd3, s.marg_eq(r3)));
% small MILP
m = lpb_new();
[m, x] = lpb_addvar(m, 2, 0, 10, [-1; -1]);
[m, z] = lpb_addvar(m, 1, 0, 1, 5, true);
[m] = lpb_addle(m, [1 1 1], [x; z], [1 1 -8], 0);   % x1+x2 <= 8 z
[m] = lpb_addle(m, [1 1], x, [1 1], 6);
s = solve_milp(lpb_finalize(m));
assert(s.ok && abs(s.fval - (-1)) < 1e-6, 'MILP wrong');
fprintf('test_solver: all passed (solver = %s)\n', s.solver);
