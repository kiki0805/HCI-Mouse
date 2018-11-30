function new_m = cut(m)
    m = m(:,2:86*86);
    cut_num = 1;
    for i = 1:85
        m = [m(:,1:i*86 - 1 - cut_num) m(:,i*86 + 2 -cut_num:86*86 - cut_num)];
        cut_num = cut_num + 2;
    end
    m = m(:,1:86*86-cut_num-1);
    cut_num = cut_num + 1;
%     new_m = m(:,5000:86*86-cut_num); % back part of G
    new_m = m(40:86,:); % back part of R
end