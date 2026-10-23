function ctx = set_scenario(ctx, name, C)
%SET_SCENARIO  DR event scenarios of the case study (one-hour events, uniform commitment C):
%   'S1'      base case: 17-18 h and 19-20 h, both agreed (day-ahead) DR. The Jiangsu rules (2024) allow
%             at most two agreed events and two hours per day, so this is the rule-compliant base case
%   'S2-<m>'  short interval: the second event starts m minutes after the first one ends (e.g. 'S2-30')
%   'S3'      high-stress extension: 17-18, 19-20 and 21-22 h, the third one a rapid peak-shaving call
%             announced 3 h ahead (speed coefficient 1.4); a hypothetical consecutive-event scenario
if nargin < 3 || isempty(C), C = 6; end
if strcmp(name, 'S1')
    t0 = [17 19]; notice = [24 24];
elseif strncmp(name, 'S2-', 3)
    gap = str2double(name(4:end)) / 60; t0 = [17, 18 + gap]; notice = [24 24];
elseif strcmp(name, 'S3')
    t0 = [17 19 21]; notice = [24 24 3];
else
    error('set_scenario:name', 'unknown scenario %s', name);
end
ctx = set_events(ctx, t0, 1, C, notice, ones(1, numel(t0)));
ctx.scen = name;
end
