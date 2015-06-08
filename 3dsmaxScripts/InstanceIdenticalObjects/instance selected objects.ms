
actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

format "do max hold..."
max hold
format "ok\n"

disableSceneRedraw()
max create mode -- faster than modify tab (if objects selected)

all = selection as array
all_count = all.count - 1

fn special_sort obj1 obj2 reverse:off = 
(
	property1 = obj1.name
	property2 = obj2.name
	
-- 	property1 = obj1.position.x
-- 	property2 = obj2.position.x
	
-- 	property1 = obj1.position.controller.percent
-- 	property2 = obj2.position.controller.percent
	
-- 	print property1
-- 	print property2
	
	a = if property1 < property2 then -1 else if property1 > property2 then 1 else 0
	if reverse then -a else a
)
-- qsort filtered_obj special_sort reverse:on
qsort all special_sort reverse:off

source_obj = all[1]
-- all = selection as array
-- source = all[1]
-- dest = all[2]
-- instanceReplace dest source
-- dest.baseobject = source.baseobject


format "source obj: %\n" source_obj.name

-- for obj in all do
for x = 1 to all_count do
(
	obj = all[x+1]
	
	try (
		format "instanceReplace: % <-> %\n" obj source_obj
-- 		instanceReplace obj source_obj
		
-- 		obj.baseobject = source_obj.baseobject
		
-- 		obj.wirecolor = source_obj.wirecolor
-- 		obj.parent = source_obj.parent
		
		select source_obj
		maxOps.cloneNodes $ cloneType:#instance newNodes:&new_objs
		new_obj = new_objs[1]
		new_obj.transform = obj.transform
		new_obj.name = obj.name
		new_obj.parent = obj.parent
		new_obj.wirecolor = obj.wirecolor
		delete obj
		
		windows.processPostedMessages()
		
	) catch (
		format "Error with %\n" obj
		-- http://forums.cgsociety.org/showpost.php?p=6000653&postcount=2
		format "Replace with a Refecence: % <-> %\n" obj source_obj
		obj.baseobject = source_obj.baseobject
	)
	
)

format "force garbage collection..."
options.showGCStatus=true
gc light:true delayed:true

enableSceneRedraw()
max views redraw
format " - END -\n"
