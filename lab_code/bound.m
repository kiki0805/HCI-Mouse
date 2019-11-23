function in = bound(in)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
    start = -20;
    end_ = 20; 
    max_e = max(in);
    min_e = min(in);
    for i = 1:length(in)
        in(i) = (end_-start) .*(in(i) -min_e) ./ (max_e - min_e) + start;
    end
end

% def bound_amplitude(data, start=-1, end=1):
%     max_e = max(data)
%     min_e = min(data)
%     for i in range(len(data)):
%         data[i] = (end - start) * (data[i] - min_e) / (max_e - min_e) + start
%     return data