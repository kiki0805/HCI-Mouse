function boom = messyit(ori)
randIndex = randperm(size(ori,1));
boom = ori(randIndex,:);
end

