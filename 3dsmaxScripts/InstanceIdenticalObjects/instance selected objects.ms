
actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

format "do max hold..."
max hold
format "ok\n"

disableSceneRedraw()
max create mode -- faster than modify tab (if objects selected)

all = selection as array
all_count = all.count - 1

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
		instanceReplace obj source_obj
	) catch (
		format "Error with %\n" obj
		-- http://forums.cgsociety.org/showpost.php?p=6000653&postcount=2
		format "Replace with a Refecence: % <-> %\n" obj source_obj
		obj.baseobject = source_obj.baseobject
	)

	obj.wirecolor = source_obj.wirecolor
	
-- 	select source_obj
-- 	maxOps.cloneNodes $ cloneType:#instance newNodes:&new_objs
-- 	new_obj = new_objs[1]
-- 	new_obj.transform = obj.transform
-- 	new_obj.name = obj.name
-- 	delete obj
-- 	new_obj.wirecolor = source_obj.wirecolor
	
)

format "force garbage collection:"
gc()
--light:true
enableSceneRedraw()
max views redraw
format " - END -\n"
