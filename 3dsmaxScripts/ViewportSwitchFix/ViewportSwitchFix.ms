--
-- copyleft (c) 2011-2012 by htFX, Jens Diemer - http://www.htFX.de
--

-- http://docs.autodesk.com/3DSMAX/14/ENU/MAXScript Help 2012/files/GUID-8AA71F9E-F4F0-4437-A44E-9683619E89D-1999.htm

clearlistener()
actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener


fn htfx_switch_viewport view_type safeframe shaded =
(
	format "switch to: %\n" view_type

-- 	format "viewport.activeViewport 1: %\n" viewport.activeViewport
	if (viewport.numViews != 4) then (
		max tool maximize
		case view_type of (
			#view_top: (
-- 				format "set activeViewport to 1\n"
				viewport.activeViewport = 1
			)
			#view_front: (
-- 				format "set activeViewport to 2\n"
				viewport.activeViewport = 2
			)
			#view_left: (
-- 				format "set activeViewport to 3\n"
				viewport.activeViewport = 3
			)
			default: (
-- 				format "set activeViewport to 4 (default)\n"
				viewport.activeViewport = 4
			)
		)
		max tool maximize
-- 		format "viewport.activeViewport 2: %\n" viewport.activeViewport
	)

	actionMan.executeAction 0 "40227" -- Save Active View
	viewport.setType view_type
	try(
            actionMan.executeAction 0 "40228" -- Restore Active View
	) catch(
            print "error restore active view"
	)

	if (displaySafeFrames != safeframe) then (
            format "toggle safeframe for %\n" view_type
            max safeframe toggle
	)
        if (shaded == true) then (
            actionMan.executeAction 0 "550"  -- Views: Viewport Visual Style Shaded
        ) else (
            actionMan.executeAction 0 "551"  -- Views: Viewport Visual Style Wireframe
        )
)

global htfx_switch_viewport

print "run the htFX Viewport macro, to install it..."
filein "$userMacros//ViewportSwitchFix.mcr"
print "OK"

print "htFX Viewport switch active."
