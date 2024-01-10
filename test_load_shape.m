fn = './shapes/shape0.json';
s = load_json_dict(fn);


fig = figure;
fig.Position = [680 414 377 563];
hold on
plot(s.rl, s.zl, 'k', 'linewidth', 1.5)
plot(s.rb, s.zb, 'r')
scatter(s.rcp, s.zcp, 20, 'b')
plot(s.segs(:,[1 3])', s.segs(:,[2 4])', 'color', [1 1 1]*0.7)
axis equal
grid on
axis([min(s.rl) max(s.rl) min(s.zl) max(s.zl)] + [-1 1 -1 1]*0.4)
scatter([s.r1 s.r2 s.r3 s.r4 s.r5 s.r6 s.r7 s.r8], ...
  [s.z1 s.z2 s.z3 s.z4 s.z5 s.z6 s.z7 s.z8], 20, 'b')
plot([s.rx1 s.rx2 s.rx3 s.rx4], [s.zx1 s.zx2 s.zx3 s.zx4], ...
  'rx', 'markersize', 12, 'linewidth', 3)










