function plan = extract_plan(x, ix)
%EXTRACT_PLAN  Full-horizon decisions (scenario 1) of a solved model.
plan.y = [x(ix.Y{1}(:,1)), x(ix.Y{2}(:,1)), x(ix.Y{3}(:,1))];
plan.pch = x(ix.PCH(:,1)); plan.pdis = x(ix.PDS(:,1)); plan.pgt = x(ix.PGT(:,1));
plan.hac = x(ix.HAC(:,1)); plan.qtc = x(ix.QTC(:,1)); plan.qtd = x(ix.QTD(:,1));
plan.pg = x(ix.PG(:,1)); plan.E = x(ix.E(:,1)); plan.S = x(ix.SS(:,1));
plan.B = [x(ix.B{1}(:,1)), x(ix.B{2}(:,1)), x(ix.B{3}(:,1))];
end
