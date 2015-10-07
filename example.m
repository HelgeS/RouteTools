%% example.m - Run to view visualization options with example data

%% Import Data
tour = importdata('tour.csv')';
% [time, velocity, power, command]
t = tour(1,:);
p = tour(2,:);
v = tour(3,:);
c = tour(4,:);

track = importdata('track.csv');
% [displacement, elevation]
d = track(1,:);
e = track(2,:);

%% Interpolate elevation to desired resolution
% TODO: 1-D Kriging to get 1m resolution estimated tracks from GPS data
d=d;
e=e;

%% Unify tour and track data
trip = zeros(6,length(d));
trip(1,:) = d;
trip(2,:) = e;

t_traveled = [t(1) t(2:end)-t(1:end-1)];
t2d = cumsum(t_traveled.*v);

for i=1:length(trip)-1
    index = find(t2d > i,1)-1;
    if isempty(index)
        trip([3:6],i) = tour(:, end);
    else
        trip([3:6],i) = tour(:, index);
    end
end

