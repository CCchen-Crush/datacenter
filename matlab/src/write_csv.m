function write_csv(file, header, M, rowlab)
%WRITE_CSV  Octave/MATLAB-portable CSV writer (header cellstr, numeric matrix, optional row labels).
fid = fopen(file, 'w');
if nargin >= 4 && ~isempty(rowlab), fprintf(fid, 'label,'); end
fprintf(fid, '%s\n', strjoin(header, ','));
for i = 1:size(M, 1)
    if nargin >= 4 && ~isempty(rowlab), fprintf(fid, '%s,', rowlab{i}); end
    fprintf(fid, '%s\n', strjoin(arrayfun(@(v) sprintf('%.6g', v), M(i, :), 'UniformOutput', false), ','));
end
fclose(fid);
end
