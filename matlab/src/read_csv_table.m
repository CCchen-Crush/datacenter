function T = read_csv_table(file)
%READ_CSV_TABLE  Read a CSV written by WRITE_CSV into a struct of column vectors (MATLAB/Octave).
%   A leading 'label' column (strings) is returned in T.label_ as a cellstr.
fid = fopen(file, 'r');
if fid < 0, error('read_csv_table:open', 'cannot open %s', file); end
hdr = strsplit(strtrim(fgetl(fid)), ',');
haslab = strcmp(hdr{1}, 'label');
fmt = repmat('%f', 1, numel(hdr)); if haslab, fmt = ['%s', repmat('%f', 1, numel(hdr) - 1)]; end
C = textscan(fid, fmt, 'Delimiter', ',');
fclose(fid);
T = struct();
for i = 1:numel(hdr)
    nm = regexprep(hdr{i}, '[^A-Za-z0-9_]', '_');
    if haslab && i == 1, T.label_ = C{1}; else, T.(nm) = C{i}; end
end
end
