function [m, rows] = lpb_addeq(m, I, J, V, b)
%LPB_ADDEQ  Add rows  sum_j A(i,j) x_j == b_i  given triplets (local row index I = 1..numel(b)).
b = b(:); nr = numel(b);
rows = (m.eq.nr + (1:nr))';
m.eq.I{end+1} = I(:) + m.eq.nr;
m.eq.J{end+1} = J(:);
m.eq.V{end+1} = V(:);
m.eq.b{end+1} = b;
m.eq.nr = m.eq.nr + nr;
end
