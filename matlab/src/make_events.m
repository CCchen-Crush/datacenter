function ev = make_events(par)
%MAKE_EVENTS  DR events from par.ev (start/end hours, notice, commitment, call probability).
%   ev(k): s, e (steps), C, price (with Jiangsu speed coefficient), notice_step, win (post-event
%   rebound window), prob (probability that the pre-announced event is called), called (realisation).
ev = struct('s', {}, 'e', {}, 'C', {}, 'price', {}, 'notice_step', {}, 'win', {}, 'name', {}, ...
            'prob', {}, 'called', {});
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
    if isfield(E, 'prob') && ~isempty(E(k).prob), ev(k).prob = E(k).prob; else, ev(k).prob = 1; end
    ev(k).called = true;
end
for k = 1:numel(ev)
    w1 = ev(k).e + 1;
    w2 = ev(k).e + round(par.dr.rb_win_h / par.dt);
    if k < numel(ev), w2 = min(w2, ev(k+1).s - 1); end
    w2 = min(w2, par.Tsim);
    ev(k).win = w1:w2;
end
end
