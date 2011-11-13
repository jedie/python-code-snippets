
-- disableSceneRedraw()
max create mode -- faster than modify tab (if objects selected)
actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()


rollout pick_box_test "manual instance replace" width:355
(
	fn is_valid_node obj = (
-- 		format "object: %\n" obj
		return isValidNode obj
	)

	pickbutton source_object "Select source Object" width:350 filter:is_valid_node
	pickbutton destination_object "Select destination Object" width:350 filter:is_valid_node \
		tooltip:"Destination Object would be instance-replaced with source object"
	
	checkbutton do_hold_button "do max hold" checked:true tooltip:"Do a scene hold before process"
	
	button do_button "do instance replace"
	
	edittext result height:330 readOnly:true
	
	hyperlink theHyperlink "copyleft (c) 2010 by htFX, Jens Diemer - www.htFX.de" address:"www.htFX.de" color:blue
	
	on source_object picked obj do source_object.text = obj.name
	on destination_object picked obj do 
	(
		destination_object.text = obj.name
		if (areNodesInstances source_object.object destination_object.object) then (
			msg = "Objects already instances: "+source_object.object.name+" <-> "+destination_object.object.name+"\n"
			format msg
			result.text+=msg
		)
	)
	
	on do_button pressed do 
	(
		if (isValidNode source_object.object) and (isValidNode destination_object.object) do
		(
			result.text = "start...\n"
			
			if do_hold_button.checked do
			(
				msg = "hold the scene, so you can revert with fetch..."
				format msg
				result.text+=msg
				max hold
				result.text += "OK\n"
			)
			
			obj_x = source_object.object
			obj_y = destination_object.object
			
			msg = "instanceReplace: "+obj_x.name+" -> "+obj_y.name+"\n"
			format msg
			result.text+=msg
			
			instanceReplace obj_y obj_x
			
			max views redraw
		)
	)
	
)
createDialog pick_box_test


format " - END -\n"