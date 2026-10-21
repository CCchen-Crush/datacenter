function DA = dayahead_commit(ctx, mode, Smode)
%DAYAHEAD_COMMIT  Day-ahead DR commitment of the AIDC-IES.
%   mode = 'coupled' : two-stage stochastic MILP over the whole day; commitments C_k are first-stage
%                      decisions shared by all scenarios, the second stage is the joint
%                      computing-storage recovery model (all events together -> cross-event coupling)
%        = 'single'  : conventional single-event capability assessment - each event is assessed
%                      alone from the nominal state, ignoring the other events
%   Smode = 'scenario' (default) or 'expected'.
if nargin < 3, Smode = 'scenario'; end
par = ctx.par; K = numel(ctx.ev);
c = ctx; c.fmode = Smode; c.da = true;
sc = make_scen(ctx.inp, par, ctx.base, 1, par.Tsim, c);
st = state_init(par, K);
st = add_arrivals(st, sc.flex(1, :, 1), par);
sc.flex(1, :, :) = repmat(sc.flex(1, :, 1), [1 1 sc.S]);   % identical first step
sc.inf(1, :) = sc.inf(1, 1); sc.fix(1, :) = sc.fix(1, 1); sc.pv(1, :) = sc.pv(1, 1);
% events with call probability < 1 occur only in the first round(prob*S) scenarios
amode = 'scenario'; if sc.S == 1, amode = 'ce'; end
act = event_activity(ctx, 1, sc.S, amode);
opt = struct('milp', true, 'visible', any(act, 2), 'active', act, 'terminal', true, 'Eref_end', ctx.Eref(end), ...
             'Sref_end', ctx.Sref(end), 'Cmax', 15);
DA.C = zeros(K, 1); DA.mode = mode;
switch mode
    case 'coupled'
        ev = ctx.ev; for k = 1:K, ev(k).mode = 'commit'; end
        [P, ix] = build_model(par, st, sc, ev, opt);
        sol = solve_milp(P, ctx.solver);
        if ~sol.ok, error('dayahead_commit:infeasible', 'coupled day-ahead model not solved'); end
        for k = 1:K, DA.C(k) = sol.x(ix.ev(k).C); end
        DA.obj = sol.fval; DA.time = sol.time;
        DA.Eplan = mean(sol.x(ix.E), 2); DA.Splan = mean(sol.x(ix.SS), 2);
        DA.valid_prob = zeros(K,1);
        for k = 1:K, DA.valid_prob(k) = mean(round(sol.x(ix.ev(k).Z))); end
    case 'single'
        DA.time = 0;
        for k = 1:K
            ev = ctx.ev; for j = 1:K, ev(j).mode = 'none'; end
            ev(k).mode = 'commit';
            [P, ix] = build_model(par, st, sc, ev, opt);
            sol = solve_milp(P, ctx.solver);
            if ~sol.ok, error('dayahead_commit:infeasible', 'single-event model not solved'); end
            DA.C(k) = sol.x(ix.ev(k).C); DA.time = DA.time + sol.time;
        end
end
end
