--
-- copyleft (c) 2012 by htFX, Jens Diemer - http://www.htFX.de
--
--


actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

fn instance_objects obj1 obj2 copy_type = (
	format "instance % <-> % - copy type: %\n" obj1 obj2 copy_type
	
	undo on
	(
		case copy_type of (
			1: ( -- instance
				instanceReplace obj2 obj1
			)
			2: ( -- reference
				obj2.baseobject = obj1.baseobject
			)
		)
		obj2.wirecolor = obj1.wirecolor
	)
)
 
rollout InstanceObjectsRollout "instance objects" --width:730 height:550
(
	pickbutton choose_obj1 "source object" width:140
	pickbutton choose_obj2 "destination object" width:140
	radiobuttons copy_type labels:#("instance", "reference")
	button btn_instanceIt "do instance!" align:#left width: 120

	on choose_obj1 picked obj do
	(
		if obj != undefined do
		( -- user did not cancel the picking...
			choose_obj1.text = obj.name
		)
	)
	
	on choose_obj2 picked obj do
	(
		if obj != undefined do
		( -- user did not cancel the picking...
			choose_obj2.text = obj.name
		)
	)
	
	on btn_instanceIt pressed do
	(
		obj1 = choose_obj1.object
		obj2 = choose_obj2.object
		if (obj1 == undefined or obj2 == undefined) then
		(
			messageBox "Please pick source/dest objects!"
		) else (
			instance_objects obj1 obj2 copy_type.state
			DestroyDialog InstanceObjectsRollout
			CreateDialog InstanceObjectsRollout
		)
	)
)

CreateDialog InstanceObjectsRollout