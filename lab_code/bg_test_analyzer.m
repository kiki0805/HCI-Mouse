% clear all;
close all;
clear all;

ave_names = ["dynamic_bg_lab_test_ave.csv"];
rgb_names = ["dynamic_bg_lab_test_rgb.csv"];
result = [];
result2 = [];
% figure;
% hold on;
tic
for i = 1:length(ave_names)
    [ber1, count1, pck_index_arr11] = vlp_parser(rgb_names(i),true);
    [ber2, count2, pck_index_arr12] = vlp_parser(rgb_names(i),false);
%     if ~contains(rgb_names(i), "freq_")
% %     count1 
% %     count2
        if count1 > count2
            pck_index_arr1 = pck_index_arr11;
        else
            pck_index_arr1 = pck_index_arr12;
        end
%     else
%         pck_index_arr1 = union(pck_index_arr11, pck_index_arr12);
%     end
    
    [ber1, count1, pck_index_arr11] = func2(ave_names(i),true);
    [ber2, count2, pck_index_arr12] = func2(ave_names(i),false);
    if count1 > count2
        pck_index_arr2 = pck_index_arr11;
    else
        pck_index_arr2 = pck_index_arr12;
    end
%     
    pck_index = union(pck_index_arr1, pck_index_arr2);
    count = length(pck_index);
    result = [result; length(pck_index_arr1), rgb_names(i)];
%     disp(length(pck_index))
    result2 = [result2; count, ave_names(i)];
    if toc > 30
        disp(i)
        tic
    end
end
% mean(double(result(:,3)) - double(result(:,4)))
% mean(double(result(:,1)) - double(result(:,4)))
% disp(result);