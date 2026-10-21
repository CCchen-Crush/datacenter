function c = apply_commit(ctx, C, DA)
%APPLY_COMMIT  Set event commitments (vector C) and, if given, day-ahead terminal SOC references.
c = ctx;
for k = 1:numel(c.ev), c.ev(k).C = C(min(k, numel(C))); end
if nargin >= 3 && ~isempty(DA) && isfield(DA, 'Eplan')
    c.Eterm = DA.Eplan; c.Sterm = DA.Splan;
end
end
