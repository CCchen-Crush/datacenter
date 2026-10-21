function w = scen_called(p, S)
%SCEN_CALLED  Scenario tree of an uncertain event: logical 1xS, true in round(p*S) scenarios spread
%   evenly over the (load-quantile ordered) scenarios, so that the call is not tied to the load level.
w = false(1, S); n = round(p * S);
if n >= 1, w(unique(round(linspace(1, S, n)))) = true; end
end
