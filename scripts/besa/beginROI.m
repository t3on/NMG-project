%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% File: beginROI.m
%
% Purpose: Assumes that the  current figure
%   is a 3d output from BESA_MN. Sets
%   up the figure to allow clickable
%   selection of a ROI. To retrieve
%   the selected region, run endROI.
%
% Inputs: None.
%
% Outputs: None.
%
% Usage: beginROI
%
% Author: Doug Bemis
% Date: 3/25/08
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function beginROI

% Load up the number of tris
load 'MN_graph_3D.mat';

global numTris;
numTris = length(brain_model);

% Going to need this later
global globalSourceCoords;
globalSourceCoords = source_coords;
global globalBrainModel;
globalBrainModel = brain_model;

% Now, grab the surfaces. 
% This actually has the lights in it too, so
% as we loop, we need to check.
sHandles = getBrainPatches;
for i = 1:length(sHandles)
    if (strcmp(get(sHandles(i), 'Type'), 'patch'))
        
        % Add our recording function
        set(sHandles(i), 'ButtonDownFcn', 'recordROI');
    end
end

% Finally, this will hold the ROI
global globalROI;
globalROI = {};
disp('All ready to go!');


