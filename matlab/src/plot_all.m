function plot_all(root)
%PLOT_ALL  Paper figures from results/*.csv (MATLAB graphics). Same content as tools/plot_results.py.
if nargin < 1, root = fileparts(fileparts(mfilename('fullpath'))); end
R = fullfile(root, 'results'); F = fullfile(root, 'figures');
col.JRS = [42 120 214]/255; col.IRO = [235 104 52]/255; col.IRR = [27 175 122]/255;
col.JRD = [237 161 0]/255; col.IRJ = [98 80 214]/255; col.grey = [0.54 0.54 0.52]; col.cap = [227 73 72]/255;
ev = [17 18; 19 20; 21 22];
set(0, 'DefaultAxesFontSize', 9, 'DefaultLineLineWidth', 1.8);

%% Fig 2: mechanism
f1 = fullfile(R, 'exp1_mechanism_CA6_DA2.csv'); f2 = fullfile(R, 'exp1_mechanism_CA6_DA1_DB2.csv');
if exist(f1, 'file') && exist(f2, 'file')
    fig = figure('Visible', 'off', 'Position', [100 100 900 360]);
    tt = {'前序 6 MW×2 h，后续 1 h', '前序 6 MW×1 h，后续 2 h'}; ff = {f1, f2};
    for j = 1:2
        T = read_csv_table(ff{j}); g = abs(T.gamma - 1.10) < 1e-9;
        subplot(1, 2, j); hold on; grid on; box on;
        plot(T.tau_h(g), T.G_IR(g) ./ T.G0(g), '-o', 'Color', col.IRO);
        plot(T.tau_h(g), T.G_IRJ(g) ./ T.G0(g), '-o', 'Color', col.IRJ);
        plot(T.tau_h(g), T.G_JR(g) ./ T.G0(g), '-o', 'Color', col.JRS);
        plot(T.tau_h(g), T.G_bound(g) ./ T.G0(g), '--', 'Color', col.grey, 'LineWidth', 1.2);
        ylim([0 1.08]); xlabel('事件间隔 \tau / h'); ylabel('\Gamma_B / \Gamma_B^0'); title(tt{j});
        legend({'独立恢复', 'IR后状态+联合恢复', '联合响应+联合恢复', '命题1上界'}, 'Location', 'southeast');
    end
    print(fig, fullfile(F, 'fig02_mechanism.png'), '-dpng', '-r200'); close(fig);
end

%% Fig 3: time series of the main case
names = {'IRR', 'IRO', 'JRS'}; lab = {'独立恢复-规则', '独立恢复-优化', '联合恢复-场景MPC(本文)'};
ok = true; D = cell(1, 3);
for i = 1:3
    fi = fullfile(R, sprintf('ts_DAcommit_%s.csv', names{i}));
    if ~exist(fi, 'file'), ok = false; break; end
    D{i} = read_csv_table(fi);
end
if ok
    fig = figure('Visible', 'off', 'Position', [100 100 850 700]);
    cs = {col.IRR, col.IRO, col.JRS};
    subplot(3,1,1); hold on; grid on; box on; shade(ev, [0 20]);
    plot(D{3}.hour, D{3}.base, '--', 'Color', col.grey); plot(D{3}.hour, D{3}.Pcap, '-', 'Color', col.cap, 'LineWidth', 1);
    for i = 1:3, plot(D{i}.hour, D{i}.pg, 'Color', cs{i}); end
    xlim([12 30]); ylabel('并网功率 / MW'); legend([{'基线', '并网容量'}, lab], 'Location', 'southwest');
    subplot(3,1,2); hold on; grid on; box on; shade(ev, [0 12]);
    for i = 1:3, plot(D{i}.hour, D{i}.E, 'Color', cs{i}); end
    xlim([12 30]); ylabel('电储能电量 / MWh');
    subplot(3,1,3); hold on; grid on; box on; shade(ev, [0 15]);
    for i = 1:3, plot(D{i}.hour, (D{i}.B1 + D{i}.B2 + D{i}.B3) / 1000, 'Color', cs{i}); end
    xlim([12 30]); ylabel('积压 / 千GPU·h'); xlabel('时刻 / h');
    print(fig, fullfile(F, 'fig03_timeseries_DAcommit.png'), '-dpng', '-r200'); close(fig);
end

%% Fig 5: sensitivity
fs = {'exp3_duration.csv', '持续时间 / h'; 'exp3_interval.csv', '事件间隔 / h'; 'exp3_gamma.csv', '并网容量裕度 \gamma'; 'exp3_commitment.csv', '承诺 / MW'};
if all(cellfun(@(x) exist(fullfile(R, x), 'file') == 2, fs(:,1)))
    fig = figure('Visible', 'off', 'Position', [100 100 1200 500]);
    cs = {col.IRR, col.IRO, col.JRS};
    for j = 1:4
        T = read_csv_table(fullfile(R, fs{j,1}));
        for r = 1:2
            subplot(2, 4, (r-1)*4 + j); hold on; grid on; box on;
            for i = 1:3
                q = T.strategy == i;
                if r == 1, plot(T.x(q), T.fulfil_pct(q), '-o', 'Color', cs{i}); ylim([0 105]);
                else, plot(T.x(q), T.max_rebound(q), '-o', 'Color', cs{i}); end
            end
            if r == 2, xlabel(fs{j,2}); end
            if j == 1 && r == 1, ylabel('兑现率 / %'); legend({'IR-R', 'IR-O', 'JR'}, 'Location', 'southwest'); end
            if j == 1 && r == 2, ylabel('最大反弹 / MW'); end
        end
    end
    print(fig, fullfile(F, 'fig05_sensitivity.png'), '-dpng', '-r200'); close(fig);
end

%% Fig 7: Monte Carlo
fm = fullfile(R, 'exp4_montecarlo.csv');
if exist(fm, 'file')
    T = read_csv_table(fm);
    fig = figure('Visible', 'off', 'Position', [100 100 1000 330]);
    ys = {T.fulfil_pct, T.max_rebound, T.net_cost / 1e4}; yl = {'兑现率 / %', '最大反弹 / MW', '综合成本 / 万元'};
    for j = 1:3
        subplot(1, 3, j); hold on; grid on; box on;
        for i = 1:4
            v = ys{j}(T.strategy == i);
            plot(i + linspace(-0.15, 0.15, numel(v)), v, 'o', 'MarkerSize', 4);
            plot([i-0.25 i+0.25], median(v) * [1 1], 'k-', 'LineWidth', 2);
        end
        set(gca, 'XTick', 1:4, 'XTickLabel', {'IR-R', 'IR-O', 'JR-D', 'JR-S'}); ylabel(yl{j});
    end
    print(fig, fullfile(F, 'fig07_montecarlo.png'), '-dpng', '-r200'); close(fig);
end

%% Fig 8: shadow prices
fsh = fullfile(R, 'exp5_shadow.csv');
if exist(fsh, 'file')
    T = read_csv_table(fsh);
    fig = figure('Visible', 'off', 'Position', [100 100 850 600]);
    subplot(3,1,1); hold on; grid on; box on; plot(T.hour, T.lambda_cap, 'Color', col.cap); xlim([12 30]); ylabel('元/MWh'); title('并网容量影子价格');
    subplot(3,1,2); hold on; grid on; box on; plot(T.hour, T.value_E, 'Color', col.JRS); plot(T.hour, T.value_S, 'Color', col.IRR); xlim([12 30]); ylabel('元/MWh'); legend({'电储能', '蓄冷'}); title('储侧状态边际价值');
    subplot(3,1,3); hold on; grid on; box on; plot(T.hour, T.cost_B1, 'Color', col.IRR); plot(T.hour, T.cost_B2, 'Color', col.IRO); plot(T.hour, T.cost_B3, 'Color', col.JRS);
    xlim([12 30]); ylabel('元/GPU·h'); xlabel('时刻 / h'); legend({'C1', 'C2', 'C3'}); title('算侧积压边际成本');
    print(fig, fullfile(F, 'fig08_shadow_prices.png'), '-dpng', '-r200'); close(fig);
end
end

function shade(ev, yl)
for k = 1:size(ev, 1)
    patch([ev(k,1) ev(k,2) ev(k,2) ev(k,1)], [yl(1) yl(1) yl(2) yl(2)], [0.85 0.9 0.97], 'EdgeColor', 'none', 'HandleVisibility', 'off');
end
end
