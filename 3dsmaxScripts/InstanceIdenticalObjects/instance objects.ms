--
-- copyleft (c) 2012 by htFX, Jens Diemer - http://www.htFX.de
--
--


actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

fn instance_objects obj1 dest_objects copy_type = (
	format "instance % <-> % - copy type: %\n" obj1 dest_objects copy_type
	for dest_object in dest_objects do (
		case copy_type of (
			1: ( -- instance
				format "instanceReplace % with %\n" dest_object obj1
				instanceReplace dest_object obj1
			)
			2: ( -- reference
				format "set baseiobject from % to %\n" dest_object obj1
				dest_object.baseobject = obj1.baseobject
			)
		)
		dest_object.wirecolor = obj1.wirecolor
	)
)
 
rollout InstanceObjectsRollout "instance objects" --width:730 height:550
(
	pickbutton choose_obj1 "pick source object" width:140
	radiobuttons copy_type labels:#("instance", "reference")
	pickbutton choose_obj2 "pick destination object" width:140
	
	on choose_obj1 picked source_object do
	(
		if source_object != undefined do
		( -- user did not cancel the picking...
			choose_obj1.text = source_object.name
		)
	)
	
	on choose_obj2 picked dest_object do
	(
		if (choose_obj1.object == undefined) then
		(
			messageBox "Please pick source object first!"
		) else (
			if dest_object != undefined do
			( -- user did not cancel the picking...
				undo on
				(
					instance_objects choose_obj1.object dest_object copy_type.state
				)
-- 				DestroyDialog InstanceObjectsRollout
-- 				CreateDialog InstanceObjectsRollout
			)
		)
	)
)

CreateDialog InstanceObjectsRollout