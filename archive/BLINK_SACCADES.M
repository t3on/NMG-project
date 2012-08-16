function blink_saccades

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% run blink block
%
% Author: Christian Brodbeck
% Date: 3/21/2012
%
%
% MEG triggers:
% 
% Blink:
%  1: fixation
%  2: blink
% 
% Saccades:
%  10: center
%  11-... for saccades (value corresponding to locs)
%
%
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


PTBVersionCheck(1,1,7,'at least');


% screen coordinates for the subjective center in the MEG: 
global GL_vertical_offset
GL_vertical_offset = -100;
center = [0 GL_vertical_offset];

% position argument for paragraphs:
paragraph_pos = {'center', 10, GL_vertical_offset}; 


% ask for subject name. The default 'R0' starts in debug mode, which 
% includes:
%  - skip screen sync test
%  - fewer trials
answers = inputdlg({'Subject ID'}, 'Options', 1, ...
                   {'R0'});
if isempty(answers)
    disp('Aborted')
    return
else
    subject = answers{1};
    is_debugging = strcmp(subject, 'R0');
    if is_debugging
        Screen('Preference', 'SkipSyncTests', 1);
        num_blinks = 2;
        num_saccades = 1;
        use_eyetracker = 0;
    else
        num_blinks = 20; % This value determines the number of blinks trials
        num_saccades = 20; % number of saccades to each location
        use_eyetracker = 1; % whether or not to use the eye tracker
    end
end


% define the spatial locations for saccades in the locs variable
x = 55;
y = 30;
locs = {center + [x, y], center + [x, -y], ...
        center - [x, y], center + [-x, y]};




% setup PTB
if not(exist('logs', 'dir'))
    mkdir('logs')
end
PTBSetLogFiles(['logs' filesep subject '_log.txt'], ...
               ['logs' filesep subject '_data.txt']);
PTBSetExitKey('q');
PTBSetIsDebugging(is_debugging);
PTBSetBackgroundColor([127 127 127]);

try
	PTBSetupExperiment('blink');
    if not(is_debugging)
        PTBInitUSBBox;
    end
    
    
    if use_eyetracker
        PTBInitEyeTracker();
        paragraph = {'Eyetracker initialized.','Get ready to calibrate.'};
        PTBDisplayParagraph(paragraph, paragraph_pos, {'a'});
        PTBCalibrateEyeTracker;
        
        % actually starts the recording
        % name correponding to MEG file (can only be 8 characters!!, no extension)
        PTBStartEyeTrackerRecording('eyelink');
    end

    
    
    % Blink
    % -----
    paragraph = {'Please blink naturally', ...
                 'whenever the cross disappears.'};
	PTBDisplayParagraph(paragraph, paragraph_pos, {'a'});
    
	% present the blink block
%     PTBDisplayText('+',{'center', center}, {1});
    for i = 1:num_blinks
        PTBDisplayText('+',{'center', center}, {1}, 1);
        PTBDisplayBlank({1}, 'Blink_Break', 2);
    end
    
    
    
    % Saccades
    % --------
    paragraph = {'Now please keep looking at the cross.', ...
                 'Whenever the cross moves,' ...
                 'follow it with your eyes.'};
	PTBDisplayParagraph(paragraph, paragraph_pos, {'a'});
    
    % present the saccade block
    seq = Shuffle(repmat(1:length(locs), 1, num_saccades));
    for i = seq
        PTBDisplayText('+',{'center', center}, {1}, 10);
        loc = locs{i};
        PTBDisplayText('+',{'center', loc}, {1}, 10 + i);
    end
        
    
	
    % Finish
    % ------
    if use_eyetracker
        % retrieve the file
        PTBDisplayText('Saving Data...', {'center', center}, {.1});
        PTBStopEyeTrackerRecording; % <----------- (can take a while)
        
        % move the file to the logs directory
        destination = ['logs' filesep subject '_eyelink_'];
        i = 0;
        while exist([destination num2str(i) '.edf'], 'file')
            i = i + 1;
        end
        movefile('eyelink.edf', [destination num2str(i) '.edf'])
    end
    
    paragraph = {'The blink block is over.', ...
                 'Please continue to lie still',...
                 'for a quick tone test.'};
	PTBDisplayParagraph(paragraph, paragraph_pos, {'a'});
    PTBDisplayBlank({.1},'EBD');
    
    
    

    
    
    PTBCleanupExperiment;

catch
    PTBHandleError;
end





