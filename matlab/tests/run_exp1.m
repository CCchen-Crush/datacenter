here = fileparts(mfilename('fullpath')); addpath(fullfile(here, '..', 'src'));
root = dcdr_setup_paths(); par = dcdr_params(); ctx = setup_case(par); ctx.all_visible = true;
for cfg = {[9 1 1], [6 2 1], [9 1 2]}
    v = cfg{1}; fprintf('--- C_A=%g D_A=%g D_B=%g\n', v);
    out = exp1_mechanism(ctx, root, struct('gammas', [1.05 1.2], 'taus', [0.25 0.5 1 2 3], 'CA', v(1), 'DA_h', v(2), 'DB_h', v(3)));
end
