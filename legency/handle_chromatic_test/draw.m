R = [];
for i = 0:3:255
    R = [R;i];
end
R = repmat(R,1,86*86);

G = [];
for i = 0:3:255
    temp = [i];
    temp = repmat(temp,1,86);
    G = [G temp];
end
G = repmat(G,86,1);

B = [];
for i = 0:3:255
    B = [B i];
end
B = repmat(B,86,86);

color = csvread('mean_var_arr.csv');

mean = color(1:636056,1);
C_mean = reshape(mean,86,86*86);
var = color(:,2);
C_var = reshape(var,86,86*86);


R = cut(R);
G = cut(G);
B = cut(B);
C_mean = cut(C_mean);
C_var = cut(C_var);


subplot(1,2,1);  
surf(R,G,B,C_mean); 
axis tight
xlabel('R');
ylabel('G');
zlabel('B');
title('Mean');



subplot(1,2,2);
surf(R,G,B,C_var); 
axis tight
xlabel('R');
ylabel('G');
zlabel('B');
title('Variance');

