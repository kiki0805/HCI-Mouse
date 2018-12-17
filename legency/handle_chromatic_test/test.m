RGB = 0:255;
RGB = [messyit(RGB') messyit(RGB') messyit(RGB')];
% RGB = messyit(RGB);
% xyY = rgb2xyY(RGB);
% draw3d(xyY,['x','y','Y'],[1,0,0],false);

% RGB = round(rand(1,255) .* 255);
xyY = rgb2xyY(RGB);
draw3d(xyY,['x','y','Y'],[1,0,0],false);
RGB2 = round(RGB .* 0.5);
hold on;
xyY2 = rgb2xyY(RGB2);
draw3d(xyY2,['x','y','Y'],[0,1,0],false);

hold on;
RGB3 = round(RGB .* 0.7);
xyY3 = rgb2xyY(RGB3);
draw3d(xyY3,['x','y','Y'],[0,0,1],false);