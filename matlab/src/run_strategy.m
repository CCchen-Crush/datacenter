function R = run_strategy(ctx, name, fmode)
%RUN_STRATEGY  Run one scheduling strategy on the DR day and evaluate it.
%   name : 'NoDR' | 'IR-R' | 'IR-O' | 'JR'
%   fmode: 'open'     - perfect-information plan solved once over the whole day, replayed open loop
%          'oracle'   - rolling horizon with perfect forecasts
%          'expected' - rolling horizon, deterministic (historical-mean) forecasts
%          'scenario' - rolling horizon, scenario-based MPC (proposed)
par = ctx.par; inp = ctx.inp;
if nargin < 3, fmode = 'open'; end
ctx.fmode = fmode;
switch name
    case 'NoDR'
        o = ctx.ref;
    case 'IR-R'
        o = run_closed_loop(par, inp.real, ctx.base, ctx.ev, @planner_irr, ctx);
    case 'IR-O'
        if strcmp(fmode, 'open')
            ctx.plan = open_plan_iro(ctx);
            o = run_closed_loop(par, inp.real, ctx.base, ctx.ev, @planner_plan, ctx);
        else
            o = run_closed_loop(par, inp.real, ctx.base, ctx.ev, @planner_iro, ctx);
        end
    case 'JR'
        if strcmp(fmode, 'open')
            ctx.plan = open_plan_jr(ctx);
            o = run_closed_loop(par, inp.real, ctx.base, ctx.ev, @planner_plan, ctx);
        else
            o = run_closed_loop(par, inp.real, ctx.base, ctx.ev, @planner_jr, ctx);
        end
    otherwise
        error('run_strategy:name', 'unknown strategy %s', name);
end
R.name = name; R.fmode = fmode; R.log = o.log;
R.M = evaluate_run(o.log, ctx.ev, ctx.base, par, inp);
end

function plan = open_plan_jr(ctx)
par = ctx.par; st = state_init(par, numel(ctx.ev));
st = add_arrivals(st, ctx.inp.real.flex(1, :), par);
c = ctx; c.fmode = 'oracle';
sc = make_scen(ctx.inp, par, ctx.base, 1, par.Tsim, c);
opt = struct('milp', ctx.milp, 'visible', true(numel(ctx.ev),1), 'terminal', true, ...
             'Eref_end', ctx.Eref(end), 'Sref_end', ctx.Sref(end));
[P, ix] = build_model(par, st, sc, ctx.ev, opt);
sol = solve_milp(P, ctx.solver);
if ~sol.ok, error('run_strategy:jr', 'JR open-loop plan infeasible'); end
plan = extract_plan(sol.x, ix);
end

function plan = open_plan_iro(ctx)
par = ctx.par; st = state_init(par, numel(ctx.ev));
st = add_arrivals(st, ctx.inp.real.flex(1, :), par);
c = ctx; c.fmode = 'oracle';
sc = make_scen(ctx.inp, par, ctx.base, 1, par.Tsim, c);
vis = true(numel(ctx.ev),1);
o1 = struct('alpha', ctx.alpha, 'visible', vis, 'pgt_nom', ctx.pgt_nom, 'ynom_now', sum(ctx.inp.real.flex(1,:)));
[P1, ix1] = build_compute_model(par, st, sc, ctx.ev, o1);
s1 = solve_milp(P1, ctx.solver);
if ~s1.ok, error('run_strategy:iro1', 'IR-O stage 1 infeasible'); end
yfix = [s1.x(ix1.Y{1}), s1.x(ix1.Y{2}), s1.x(ix1.Y{3})];
o2 = struct('milp', ctx.milp, 'fix_y', yfix, 'visible', vis, 'terminal', true, ...
            'Eref_end', ctx.Eref(end), 'Sref_end', ctx.Sref(end));
[P2, ix2] = build_model(par, st, sc, ctx.ev, o2);
s2 = solve_milp(P2, ctx.solver);
if ~s2.ok, error('run_strategy:iro2', 'IR-O stage 2 infeasible'); end
plan = extract_plan(s2.x, ix2);
plan.y = yfix;
end
