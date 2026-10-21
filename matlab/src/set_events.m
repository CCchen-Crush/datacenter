function ctx = set_events(ctx, t0_h, dur_h, C, notice_h)
%SET_EVENTS  Replace the DR events (start hours, durations, commitments) and refresh derived fields.
par = ctx.par; K = numel(t0_h);
if numel(dur_h) == 1, dur_h = repmat(dur_h, 1, K); end
if numel(C) == 1, C = repmat(C, 1, K); end
if nargin < 5, notice_h = [ctx.par.ev.notice]; notice_h = notice_h(min(1:K, numel(notice_h))); end
par.ev = struct('t0', num2cell(t0_h), 't1', num2cell(t0_h + dur_h), 'notice', num2cell(notice_h), 'C', num2cell(C));
ctx.par = par;
tmp = load_inputs_events(par);
for k = 1:K
    tmp(k).Pbmax = max(ctx.base(tmp(k).s:tmp(k).e));
    tmp(k).mode = 'settle';
end
ctx.ev = tmp;
end

function ev = load_inputs_events(par)
ev = struct('s', {}, 'e', {}, 'C', {}, 'price', {}, 'notice_step', {}, 'win', {}, 'name', {});
E = par.ev;
for k = 1:numel(E)
    ev(k).s = round(E(k).t0 / par.dt) + 1;
    ev(k).e = round(E(k).t1 / par.dt);
    ev(k).C = E(k).C;
    nt = E(k).notice;
    if nt >= 24, coef = 1.0; elseif nt > 2, coef = par.dr.coef_2to4h; elseif nt > 0.5, coef = par.dr.coef_05to2h; else, coef = 1.0; end
    ev(k).price = par.dr.price_da * coef;
    ev(k).notice_step = max(1, ev(k).s - round(nt / par.dt));
    ev(k).name = sprintf('E%d', k);
end
for k = 1:numel(ev)
    w1 = ev(k).e + 1; w2 = ev(k).e + round(par.dr.rb_win_h / par.dt);
    if k < numel(ev), w2 = min(w2, ev(k+1).s - 1); end
    ev(k).win = w1:min(w2, par.Tsim);
end
end
