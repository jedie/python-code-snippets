fn switch_viewport view_type safeframe =
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


Macroscript switch2TopView_T category:"_htFX.de maxscripts"
(
	switch_viewport #view_top false
)

Macroscript switch2BottomView_B category:"_htFX.de maxscripts"
(
	switch_viewport #view_bottom false
)

Macroscript switch2RightView category:"_htFX.de maxscripts"
(
	switch_viewport #view_right false
)

Macroscript switch2LeftView_L category:"_htFX.de maxscripts"
(
	switch_viewport #view_left false
)

Macroscript switch2FrontView_F category:"_htFX.de maxscripts"
(
	switch_viewport #view_front false
)

Macroscript switch2BackView category:"_htFX.de maxscripts"
(
	switch_viewport #view_back false
)

Macroscript switch2PerspectiveView_P category:"_htFX.de maxscripts"
(
	switch_viewport #view_persp_user false
)

Macroscript switch2UserView_U category:"_htFX.de maxscripts"
(
	switch_viewport #view_iso_user false
)

Macroscript switch2CameraView_C category:"_htFX.de maxscripts"
(
	switch_viewport #view_camera true
)

Macroscript switch2SpotView category:"_htFX.de maxscripts"
(
	switch_viewport #view_spot false
)

Macroscript switch2ShapeView category:"_htFX.de maxscripts"
(
	switch_viewport #view_shape false
)

Macroscript switch2GridView category:"_htFX.de maxscripts"
(
	switch_viewport #view_grid false
)
