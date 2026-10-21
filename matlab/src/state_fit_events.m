function st = state_fit_events(st, K)
%STATE_FIT_EVENTS  Make the event bookkeeping of a saved state match K events (pad with zeros).
f = {'ev_r', 'ev_n', 'ev_mx', 'rb'};
for i = 1:numel(f)
    v = st.(f{i}); v = v(:);
    if numel(v) < K, v = [v; zeros(K - numel(v), 1)]; else, v = v(1:K); end
    st.(f{i}) = v;
end
end
