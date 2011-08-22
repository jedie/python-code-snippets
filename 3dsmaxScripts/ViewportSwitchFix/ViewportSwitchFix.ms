
-- actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener

global htfx_switch_viewport

fn htfx_switch_viewport view_type safeframe =
(
	format "switch to: %\n" view_type
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
)

print "run the htFX Viewport macro, to install it..."
filein "$userMacros//ViewportSwitchFix.mcr"
print "OK"

print "htFX Viewport switch active."