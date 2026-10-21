function y = edf_alloc(st, par, ytot)
%EDF_ALLOC  Split a total number of busy GPUs over classes: due work first, then earliest deadline.
dt = par.dt; t = st.t;
due = sum(st.rem(1:t, :), 1) / dt;
y = due;
left = ytot - sum(due);
if left <= 0, return; end
R = st.rem(t+1:end, :) / dt;             % future deadlines, rows = deadline order
[nr, nc] = size(R);
v = reshape(R', [], 1);                  % interleave: same deadline -> classes in order
cls = repmat((1:nc)', nr, 1);
take = min(v, max(0, left - (cumsum(v) - v)));
for c = 1:nc, y(c) = y(c) + sum(take(cls == c)); end
end
