function xyY = rgb2xyY(rgb)
xyz = rgb2xyz(rgb);

x = xyz(:,1) ./ sum(xyz,2);
y = xyz(:,2) ./ sum(xyz,2);
Y = xyz(:,2);
xyY = [x y Y];
end

