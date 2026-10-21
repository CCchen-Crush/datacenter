addpath(fullfile(fileparts(mfilename('fullpath')), '..', 'src'));
addpath(fullfile(fileparts(mfilename('fullpath')), '..', 'config'));
par = dcdr_params();
inp = load_inputs(par);
fprintf('flex mean GPUs %.0f, inf mean %.0f, pv max %.2f MW, cop range %.2f-%.2f\n', ...
    mean(sum(inp.real.flex,2)), mean(inp.real.inf), max(inp.real.pv), min(inp.real.cop), max(inp.real.cop));
u = (sum(inp.real.flex,2) + inp.real.inf) / par.it.Ngpu;
fprintf('utilisation min %.2f mean %.2f max %.2f\n', min(u), mean(u), max(u));
fprintf('price levels: %s\n', mat2str(unique(inp.price)'));
for k = 1:numel(inp.ev), fprintf('%s: steps %d-%d C=%.1f price=%.0f notice=%d win=%d-%d\n', inp.ev(k).name, inp.ev(k).s, inp.ev(k).e, inp.ev(k).C, inp.ev(k).price, inp.ev(k).notice_step, inp.ev(k).win(1), inp.ev(k).win(end)); end
disp(inp.info)
