function [m, id] = lpb_addvar(m, n, lb, ub, f, isint)
%LPB_ADDVAR  Append n variables. lb/ub/f may be scalars or n-vectors.
if nargin < 6, isint = false; end
id = (m.n + (1:n))';
m.lb = [m.lb; expand(lb, n)];
m.ub = [m.ub; expand(ub, n)];
m.f  = [m.f;  expand(f,  n)];
m.isint = [m.isint; repmat(logical(isint), n, 1)];
m.n = m.n + n;
end

function v = expand(x, n)
x = x(:);
if numel(x) == 1, v = repmat(x, n, 1); else, v = x; end
if numel(v) ~= n, error('lpb_addvar:size', 'bound/cost size mismatch'); end
end
