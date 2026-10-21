function [rows, hdr, Rs] = run_list(c, S, tag)
%RUN_LIST  Run the strategies of list S (see bench_list) on context c; one metrics_row per strategy.
%   For 'open' IR-O* the static split is chosen with hindsight (alpha_hindsight) and for 'open' IR-P
%   the price signal comes from the perfect-information joint plan, unless already set in c.
if nargin < 3, tag = ''; end
rows = []; Rs = cell(1, size(S, 1)); hdr = {};
for i = 1:size(S, 1)
    ci = c; t = tic;
    if strcmp(S{i, 1}, 'IR-O*') && ~isfield(ci, 'alpha_star')
        ci.alpha_star = alpha_hindsight(ci);
    end
    if strcmp(S{i, 1}, 'IR-P') && (~isfield(ci, 'lambda_hr_da') || isempty(ci.lambda_hr_da))
        if strcmp(S{i, 2}, 'open'), ci.lambda_hr_da = dayahead_prices(ci, 'oracle'); else, ci.lambda_hr_da = dayahead_prices(ci); end
    end
    R = run_strategy(ci, S{i, 1}, S{i, 2}); M = R.M;
    [row, hdr] = metrics_row(M); rows = [rows; row]; %#ok<AGROW>
    if nargout > 2, Rs{i} = R; end
    fprintf('  %s%-16s ful=%6.2f%% valid=%d/%d rb=%.2f rb6=%.2f payG=%.2f net=%.0f adj=%.0f exrb=%.0f (%.0fs)\n', tag, S{i, 3}, ...
        100 * M.fulfil_rate, M.n_valid, M.n_called, M.max_rebound, M.max_rebound6, M.payback_gap, M.net_cost, ...
        M.net_cost_adj, M.net_cost_excl_rb, toc(t));
end
end
