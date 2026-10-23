function sc = make_scen(inp, par, base, t0, H, ctx)
%MAKE_SCEN  Forecast data for the optimisation horizon t0..t0+H-1.
%   ctx.fmode = 'oracle'   : realised data (perfect information)
%             = 'expected' : historical-mean forecast, corrected by the latest observed error
%             = 'scenario' : ctx.S scenarios from historical days, each error-corrected
%   The current step (h = 1) is always the measured value. The chiller COP follows the temperature
%   forecast of the same weather source as PV (inp.fc.cop / the PV pool day of each scenario), unless
%   par.mpc.cop_fc = 'perfect' (realised temperature known in advance).
T = par.Tsim; hh = t0:(t0 + H - 1);
dec = par.mpc.decay .^ (0:H-1)';
da = isfield(ctx, 'da') && ctx.da;          % day-ahead: no measurement-based correction
switch ctx.fmode
    case 'oracle'
        S = 1; flex = inp.real.flex(hh, :); fix = inp.real.fix(hh); inf = inp.real.inf(hh); pv = inp.real.pv(hh);
        cop = inp.real.cop(hh);
    case 'expected'
        S = 1;
        if da                               % day-ahead: plain historical-mean forecast
            flex = inp.fc.flex(hh, :); fix = inp.fc.fix(hh); inf = inp.fc.inf(hh); pv = inp.fc.pv(hh);
            cop = inp.fc.cop(hh);
        else
        flex = corr_series(inp.fc.flex, inp.real.flex, t0, hh, dec);
        fix  = corr_series(inp.fc.fix,  inp.real.fix,  t0, hh, dec);
        inf  = corr_series(inp.fc.inf,  inp.real.inf,  t0, hh, dec);
        pv   = corr_series(inp.fc.pv,   inp.real.pv,   t0, hh, dec);
        cop  = corr_series(inp.fc.cop,  inp.real.cop,  t0, hh, dec);
        end
    case 'scenario'
        S = numel(ctx.sidx.flex);
        flex = zeros(H, 3, S); fix = zeros(H, S); inf = zeros(H, S); pv = zeros(H, S); cop = zeros(H, S);
        for s = 1:S
            if da
                flex(:, :, s) = inp.pool.flex(hh, :, ctx.sidx.flex(s)); fix(:, s) = inp.pool.fix(hh, ctx.sidx.flex(s));
                inf(:, s) = inp.pool.inf(hh, ctx.sidx.inf(s)); pv(:, s) = inp.pool.pv(hh, ctx.sidx.pv(s));
                cop(:, s) = inp.pool.cop(hh, ctx.sidx.pv(s));
            else
            flex(:, :, s) = corr_series(inp.pool.flex(:, :, ctx.sidx.flex(s)), inp.real.flex, t0, hh, dec);
            fix(:, s) = corr_series(inp.pool.fix(:, ctx.sidx.flex(s)), inp.real.fix, t0, hh, dec);
            inf(:, s) = corr_series(inp.pool.inf(:, ctx.sidx.inf(s)), inp.real.inf, t0, hh, dec);
            pv(:, s)  = corr_series(inp.pool.pv(:, ctx.sidx.pv(s)),  inp.real.pv,  t0, hh, dec);
            cop(:, s) = corr_series(inp.pool.cop(:, ctx.sidx.pv(s)), inp.real.cop, t0, hh, dec);
            end
        end
end
sc.H = H; sc.S = S; sc.prob = ones(S, 1) / S;
sc.flex = reshape(flex, H, 3, S);
sc.inf = inf; sc.fix = fix; sc.pv = max(pv, 0);
if isfield(par.mpc, 'cop_fc') && strcmp(par.mpc.cop_fc, 'perfect'), cop = inp.real.cop(hh); end
sc.cop = repmat(cop, 1, S / size(cop, 2));
sc.price = inp.price(hh);
sc.Pb = base(hh);
end

function x = corr_series(fc, real, t0, hh, dec)
% multiplicative correction with the ratio observed over the last 4 steps, decaying over the horizon
w = max(1, t0 - 3):t0;
nc = size(fc, 2);
x = fc(hh, :);
for c = 1:nc
    den = sum(fc(w, c)); num = sum(real(w, c));
    if den > 1e-6 && num > 1e-6, rho = num / den; else, rho = 1; end
    rho = min(max(rho, 0.5), 2);
    x(:, c) = fc(hh, c) .* (1 + (rho - 1) * dec);
end
x(1, :) = real(t0, :);
end
