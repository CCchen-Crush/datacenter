function known = event_known(ctx, t)
%EVENT_KNOWN  Certainty-equivalent view (K x 1) of which events will happen, as seen at step t.
known = event_activity(ctx, t, 1, 'ce');
end
