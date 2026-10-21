function m = lpb_new()
%LPB_NEW  Create an empty LP/MILP model container (struct based, MATLAB/Octave compatible).
%   Variables are added with LPB_ADDVAR, constraints with LPB_ADDLE / LPB_ADDEQ,
%   and the model is turned into solver matrices with LPB_FINALIZE.
m.n   = 0;
m.lb  = zeros(0,1);
m.ub  = zeros(0,1);
m.f   = zeros(0,1);
m.isint = false(0,1);
m.le.I = {}; m.le.J = {}; m.le.V = {}; m.le.b = {}; m.le.nr = 0;
m.eq.I = {}; m.eq.J = {}; m.eq.V = {}; m.eq.b = {}; m.eq.nr = 0;
m.tag = struct();      % named index sets, filled by the model builders
end
