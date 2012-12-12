%getdataforexcel.m 
% outputs columns of length of time window, all of the condition 1, by
% subjects, then all of the second condition by subjects... and so on

function getdataforexcel(struct_name,file_name)
if nargin < 2
    file_name = 'data';
end

data = [];

for i = 1 : length(struct_name.waves(:,1,1))
    for j = 1 : length(struct_name.waves(1,:,1))
        data = [data struct_name.waves(i,j,:)];
    end
end
data = squeeze(data);

csvwrite([file_name '.csv'],data);

end