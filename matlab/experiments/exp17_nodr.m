function out = exp17_nodr(ctx, root, N, tag)
%EXP17_NODR  No-DR reference operation on the N PAI test days of Exp12/Exp16: one metrics row per day.
%   The cost components of this reference are subtracted from those of every strategy to decompose the
%   daily benefit of DR participation (electricity, gas, degradation, delay, end state, shortfall, revenue).
%   Writes results/exp17_nodr<tag>.csv (tag '_jul' for the cross-month case).
if nargin < 3 || isempty(N), N = 26; end
if nargin < 4, tag = ''; end
rs = distinct_pai(ctx.inp.mc.label, N);
rows = []; hdr = {}; t0 = tic;
for j = 1:numel(rs)
    R = run_strategy(use_realization(ctx, rs(j)), 'NoDR');
    [row, hdr] = metrics_row(R.M);
    rows = [rows; rs(j), row]; %#ok<AGROW>
end
write_csv(fullfile(root, 'results', sprintf('exp17_nodr%s.csv', tag)), [{'realisation'}, hdr], rows);
fprintf('  exp17 no-DR reference on %d test days: mean net cost %.1f k (%.1f min)\n', numel(rs), ...
    mean(rows(:, 1 + find(strcmp(hdr, 'net_cost_adj')))) / 1000, toc(t0) / 60);
out.rows = rows; out.hdr = hdr;
end

function rs = distinct_pai(label, N)
% first N realisations with pairwise different PAI weekdays (label 'pai<day>_<azure>_<weather>')
key = cellfun(@(s) strtok(s, '_'), label, 'UniformOutput', false);
[~, first] = unique(key, 'first');
rs = sort(first(:))';
rs = rs(1:min(N, numel(rs)));
end
