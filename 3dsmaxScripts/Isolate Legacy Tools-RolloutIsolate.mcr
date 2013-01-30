
--
-- Lagacy "Isolate Selection" for max 2013
--
-- Please vote:
-- http://3dsmaxfeedback.autodesk.com/forums/76763-small-annoying-things/suggestions/2771695-max-2013-make-isolate-selection-recursively
--
-- Original script by: Kelly Michels 03/30/2012
-- Enhanced version from 'fajar' 2012-11-15 :
-- http://www.scriptspot.com/3ds-max/scripts/isolate-selection-legacy-mode-for-2013#comment-19409
--
-- changes 2013 by htFX.de - Jens Diemer:
-- 		* put the "exit isolate button" at top/right corner of the max window
--		* add help text here
--
-- install:
-- Just drop to the max 2013 window
-- or copy the file to "%LOCALAPPDATA%\Autodesk\3dsMax\2013 - 64bit\ENU\usermacros" and evaluate
-- goto:
--		Customize / Customize User Interface / Toolbars / Isolate Legacy Tools
-- and add "Isolate lagancy Selection" to a toolbar
-- goto:
--		Customize / Customize User Interface / Keyboard / Isolate Legacy Tools
-- and assign Alt+Q hotkey to "Isolate lagancy Selection"
--

macroScript RolloutIsolate
category:             "Isolate Legacy Tools"
internalCategory:     "Isolate Legacy Tools"
buttonText:           "RolloutIsolate"
icon:                 #("Systems",2)
tooltip:             "Isolate legacy Selection"

(
    local isolateFloater

	fn ToggleIsolateSelectionMode =
		(
		if(IsolateSelection.IsolateSelectionModeActive()) then
			(
			IsolateSelection.ExitIsolateSelectionMode()
			)
		else
			(
			IsolateSelection.EnterIsolateSelectionMode()
			)
		)

	fn ExpandIsolateSelectionMode =
		(
		if (IsolateSelection.IsolateSelectionModeActive()) do
			IsolateSelection.ExitIsolateSelectionMode()
			IsolateSelection.EnterIsolateSelectionMode()
		)

	fn exitIsolation=
	(
	if (IsolateSelection.IsolateSelectionModeActive()) do IsolateSelection.ExitIsolateSelectionMode()
	)

    rollout IsolateRollout "Warning:Isolate Selection" width:186 height:38
    (
    	checkbutton btnIsolate "Exit Isolate Selection" width:184 height:32

    	on IsolateRollout open do
    	(
    	   if selection.count >=1 then
    	   (
    		   ExpandIsolateSelectionMode()
    		   btnIsolate.checked=true
    	   )
    	)

		on IsolateRollout close do
		(
			exitIsolation()
		)

    	on btnIsolate changed state do
    	(
    	  if btnIsolate.checked==false do
			(
				exitIsolation()
				btnIsolate.checked=false
				try (destroyDialog IsolateRollout) catch()
			)
    	)

    	on btnIsolate pressed do
    	(
    		ToggleIsolateSelectionMode()
    	)
    )

    on Execute do
    (
	if selection.count>=1 do
		(
		try (destroyDialog IsolateRollout) catch()
			max_pos = getMAXWindowPos()
			max_size = getMAXWindowSize()

			x = max_pos.x + max_size.x - 250
			y = max_pos.y + 15

			CreateDialog IsolateRollout pos:[x,y]
		)
    )
)
