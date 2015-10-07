%% distView.m - View trip by distance
%
%   Assumes a trip matrix (6 X meters) with rows:
% [displacement, elevation, time, velocity, power, command]
%
%%%

%% Readability
d = trip(1,:);
e = trip(2,:);
t = trip(3,:);
p = trip(4,:);
v = trip(5,:);
c = trip(6,:);

fill_between_lines = @(X,Y1,Y2,C) fill( [X fliplr(X)],  [Y1 fliplr(Y2)], C );


%% Track and Power
subplot(2,1,1)
% Plot Track
vertCushion = .15 * (max(e)-min(e));
trackThickness = 1;
%fill_between_lines(d, e+trackThickness, e-trackThickness, 'k')
axis([min(d) max(d) min(e)-vertCushion max(e)+vertCushion])

% Plot Power Used
colormap(winter)
x = d;
z = zeros(size(x));
y = e;
col = p;  % This is the color, vary with x in this case.
surface([x;x],[y;y],[z;z],[col;col],...
        'facecol','no',...
        'edgecol','interp',...
        'linew',6);
title('Power Used on Track')
    
%% Commands and Velocity
subplot(2,1,2)

[ax, h1, h2] = plotyy(x,v,x,c);
set(h1,'LineWidth',4);
set(h2,'LineWidth',4);
set(ax(1),'XLim',[0 length(d)]);
set(ax(2),'XLim',[0 length(d)]);


title('Commands and Velocity')
