function new_m = normalize(m)
    new_m = (m - min(m)) / (max(m) - min(m));
end