function rs = test_days(ctx, N)
%TEST_DAYS  The N operating (test) days: the first N Monte-Carlo realisations with pairwise different PAI
%   weekdays (label 'pai<day>_<azure>_<weather>'), as used by Exp12, Exp14 and Exp16.
if nargin < 2 || isempty(N), N = 26; end
key = cellfun(@(s) strtok(s, '_'), ctx.inp.mc.label, 'UniformOutput', false);
[~, first] = unique(key, 'first');
rs = sort(first(:))';
rs = rs(1:min(N, numel(rs)));
end
