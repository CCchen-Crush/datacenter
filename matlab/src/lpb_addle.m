function [m, rows] = lpb_addle(m, I, J, V, b)
%LPB_ADDLE  Add rows  sum_j A(i,j) x_j <= b_i  given triplets (local row index I = 1..numel(b)).
b = b(:); nr = numel(b);
rows = (m.le.nr + (1:nr))';
m.le.I{end+1} = I(:) + m.le.nr;
m.le.J{end+1} = J(:);
m.le.V{end+1} = V(:);
m.le.b{end+1} = b;
m.le.nr = m.le.nr + nr;
end
