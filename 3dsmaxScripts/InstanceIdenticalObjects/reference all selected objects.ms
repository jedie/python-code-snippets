--
-- copyleft (c) 2012 by htFX, Jens Diemer - http://www.htFX.de
--

disableSceneRedraw()
max create mode -- faster than modify tab (if objects selected)
actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

format "do max hold..."
max hold
format "ok\n"

disableSceneRedraw()

filtered_objects = selection as array
filtered_objects = (for o in filtered_objects where o.isHidden == false collect o)

all_count = filtered_objects.count
format "Anzahl: %\n" all_count

source_obj = selection[1]
source_base_object = source_obj


with undo on (
	processed = 0
	for obj in filtered_objects do (
		processed += 1
		format "--------------------------------------------------\n"
		format "%/% - object %\n" processed all_count obj
		format "object category: %\n" obj.baseObject.category 
		format "baseObject %\n" (classof obj.baseObject)
		
		if (obj.baseobject == source_base_object) or (areNodesInstances obj source_obj) then (
			format "make unique: %\n" obj
			InstanceMgr.MakeObjectsUnique obj #individual
		)
		
		format "made a reference: %\n" obj
		obj.baseobject = source_base_object
		windows.processPostedMessages()
	)
)

format "force garbage collection:"
gc()
--light:true
enableSceneRedraw()
max views redraw
format " - END -\n"