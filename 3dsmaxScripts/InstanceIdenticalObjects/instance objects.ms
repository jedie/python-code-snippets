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
	pickbutton choose_obj1 "source object" width:140
	radiobuttons copy_type labels:#("instance", "reference")
	button btn_instanceIt "go: select destination" align:#left width: 120
	
	on choose_obj1 picked obj do
	(
		if obj != undefined do
		( -- user did not cancel the picking...
			choose_obj1.text = obj.name
		)
	)
	
	on btn_instanceIt pressed do
	(
		obj1 = choose_obj1.object
		if (obj1 == undefined) then
		(
			messageBox "Please pick source object!"
		) else (
			dest_objects = selectByName title:"Select destination objects" buttonText:"make instance" showHidden:false single:false
			if (dest_objects == undefined or dest_objects.count == 0) then (
				messageBox "Please select destination objects."
			) else (
				undo on
				(
					instance_objects obj1 dest_objects copy_type.state
				)
				DestroyDialog InstanceObjectsRollout
				CreateDialog InstanceObjectsRollout
			)
		)
	)
)

CreateDialog InstanceObjectsRollout