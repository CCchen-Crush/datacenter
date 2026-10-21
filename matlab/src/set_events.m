function ctx = set_events(ctx, t0_h, dur_h, C, notice_h, prob)
%SET_EVENTS  Replace the DR events (start hours, durations, commitments) and refresh derived fields.
par = ctx.par; K = numel(t0_h);
if numel(dur_h) == 1, dur_h = repmat(dur_h, 1, K); end
if numel(C) == 1, C = repmat(C, 1, K); end
if nargin < 5 || isempty(notice_h), notice_h = [ctx.par.ev.notice]; notice_h = notice_h(min(1:K, numel(notice_h))); end
if nargin < 6 || isempty(prob), prob = ones(1, K); end
par.ev = struct('t0', num2cell(t0_h), 't1', num2cell(t0_h + dur_h), 'notice', num2cell(notice_h), ...
                'C', num2cell(C), 'prob', num2cell(prob));
ctx.par = par;
ev = make_events(par);
for k = 1:K
    ev(k).Pbmax = max(ctx.base(ev(k).s:ev(k).e));
    ev(k).mode = 'settle';
end
ctx.ev = ev;
end
