
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

format "source obj: %\n" source_obj.name

for x = 1 to all_count do
(
	obj = all[x+1]
	format "instanceReplace: % <-> %\n" source_obj obj
	
	instanceReplace source_obj obj
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
