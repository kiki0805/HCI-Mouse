function draw3d(matrix, labels, color,equal)
scatter3(matrix(:,1),matrix(:,2),matrix(:,3),5,'MarkerEdgeColor',color,'MarkerFaceColor',color);
axis tight;
if equal
    axis equal;
end
xlabel(labels(1));
ylabel(labels(2));
zlabel(labels(3));
end

