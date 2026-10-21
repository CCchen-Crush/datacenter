function root = dcdr_setup_paths()
%DCDR_SETUP_PATHS  Add the project folders to the path and return the matlab/ root folder.
root = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(root, 'src')); addpath(fullfile(root, 'config')); addpath(fullfile(root, 'experiments'));
if ~exist(fullfile(root, 'results'), 'dir'), mkdir(fullfile(root, 'results')); end
if ~exist(fullfile(root, 'figures'), 'dir'), mkdir(fullfile(root, 'figures')); end
end
