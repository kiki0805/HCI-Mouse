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

mean = color(:,1);
C_mean = reshape(mean',86*86,86)';
var = color(:,2);
C_var = reshape(var',86*86,86)';


R = cut(R);
G = cut(G);
B = cut(B);
C_mean = cut(C_mean);
C_var = cut(C_var);

R = reshape(R',1,[])';
G = reshape(G',1,[])';
B = reshape(B',1,[])';
C_mean = reshape(C_mean',1,[])';
C_var = reshape(C_var',1,[])';
C_color = [R G B];

scatter3(R,G,B,5,C_color,'filled');
xlabel('R');
ylabel('G');
zlabel('B');
title('Color');

% subplot(1,2,1);  
% scatter3(R,G,B,5,C_mean,'filled'); 
% axis tight
% xlabel('R');
% ylabel('G');
% zlabel('B');
% title('Mean');
% 
% subplot(1,2,2);
% scatter3(R,G,B,5,C_var,'filled'); 
% axis tight
% xlabel('R');
% ylabel('G');
% zlabel('B');
% title('Variance');
