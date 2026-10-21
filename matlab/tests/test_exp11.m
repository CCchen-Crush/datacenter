here = fileparts(mfilename('fullpath')); addpath(fullfile(here, '..', 'src')); addpath(fullfile(here, '..', 'experiments'));
root = dcdr_setup_paths();
out = exp11_stylized(root);
