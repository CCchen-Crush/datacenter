function M = evaluate_run(L, ev, base, par, inp)
%EVALUATE_RUN  Settlement (Jiangsu rules) and performance indicators of a simulated day.
dt = par.dt; d = sys_derived(par);
K = numel(ev);
M.avg_red = zeros(K,1); M.valid = false(K,1); M.pay = zeros(K,1); M.fulfil = zeros(K,1);
M.short = zeros(K,1); M.rebound = zeros(K,1); M.E_start = zeros(K,1); M.B_start = zeros(K,3);
for k = 1:K
    s = ev(k).s; e = ev(k).e; Dh = (e - s + 1) * dt;
    red = base(s:e) - L.pg(s:e);
    M.avg_red(k) = mean(red);
    M.valid(k) = M.avg_red(k) >= par.dr.valid_lo * ev(k).C - 1e-6 && max(L.pg(s:e)) <= max(base(s:e)) + 1e-6;
    M.pay(k) = M.valid(k) * ev(k).price * min(M.avg_red(k), par.dr.pay_hi * ev(k).C) * Dh;
    M.fulfil(k) = min(max(M.avg_red(k), 0) / ev(k).C, 1);
    M.short(k) = max(ev(k).C - M.avg_red(k), 0);
    if ~isempty(ev(k).win), M.rebound(k) = max(0, max(L.pg(ev(k).win) - base(ev(k).win))); end
    if s > 1, M.E_start(k) = L.E(s-1); M.B_start(k,:) = L.backlog(s-1,:); else, M.E_start(k) = par.bess.E0; end
end
Dk = ([ev.e] - [ev.s] + 1)' * dt; C = [ev.C]';
M.fulfil_rate = sum(Dk .* min(max(M.avg_red, 0), C)) / sum(Dk .* C);
M.n_valid = sum(M.valid);
M.max_rebound = max(M.rebound);
M.cost_energy = sum(inp.price .* L.pg) * dt;
M.cost_gas = sum(L.pgt) * dt * par.price.gas / par.gt.eta_e;
M.cost_deg = sum(L.pch + L.pdis) * dt * par.bess.c_deg;
M.cost_op = M.cost_energy + M.cost_gas + M.cost_deg;
M.dr_pay = sum(M.pay);
M.pen_dev = sum(par.dr.kappa_dev * [ev.price]' .* M.short .* Dk);
M.pen_rb = par.dr.c_rb * sum(M.rebound);
M.net_cost = M.cost_op - M.dr_pay + M.pen_dev + M.pen_rb;
M.lateness = sum(L.overdue) * dt;                    % GPU-h * h
M.peak_grid = max(L.pg);
M.cap_violation = max(L.over);
M.bess_throughput = sum(L.pch + L.pdis) * dt;
M.mean_backlog = mean(sum(L.backlog, 2));
M.fallbacks = sum(L.fallback);
M.solve_time = sum(L.solve_time);
M.Pcap = d.Pcap;
end
