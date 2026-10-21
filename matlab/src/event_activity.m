function act = event_activity(ctx, t0, S, mode)
%EVENT_ACTIVITY  Which events a planner treats as happening, per scenario (K x S logical).
%   An event is known once t0 >= notice_step (then its realised status 'called' is used) or if its
%   call probability is 1. Before confirmation an uncertain event (prob < 1) is
%     mode 'scenario' : active in round(prob*S) scenarios (scen_called; scenario tree over event calls)
%     mode 'ce'       : active iff prob >= ctx.par.mpc.ce_threshold (certainty equivalent)
%     mode 'oracle'   : realised status (perfect information)
%   ctx.myopic = true keeps only the earliest unfinished active event (event-by-event planning).
ev = ctx.ev; K = numel(ev); act = false(K, S);
thr = ctx.par.mpc.ce_threshold;
for k = 1:K
    if strcmp(mode, 'oracle') || t0 >= ev(k).notice_step || ev(k).prob >= 1
        act(k, :) = ev(k).called;
    elseif strcmp(mode, 'scenario')
        act(k, :) = scen_called(ev(k).prob, S);
    else
        act(k, :) = ev(k).prob >= thr;
    end
end
if isfield(ctx, 'myopic') && ctx.myopic
    unfinished = [ev.e]' >= t0;
    k0 = find(unfinished & any(act, 2), 1);
    for k = 1:K
        if unfinished(k) && (isempty(k0) || k ~= k0), act(k, :) = false; end
    end
end
end
