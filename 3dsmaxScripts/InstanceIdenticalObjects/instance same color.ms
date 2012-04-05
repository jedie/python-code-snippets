


actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()


-- disableSceneRedraw()
max create mode -- faster than modify tab (if objects selected)


all=$* as array
-- all=$*/geometry as array
-- all = selection as array

 fn compare n1 n2 reverse:off = 
 (
 	   a = if n1 < n2 then -1 else if n1 > n2 then 1 else 0
 	   if reverse then -a else a
 )
 
fn dreieckszahl n = 
(	-- https://oeis.org/A000217
	return n * (n-1) / 2
)

fn random_wirecolor obj =
(
	red = random 0 255
	green = random 0 255
	blue = random 0 255
	obj.wirecolor = color red green blue
)

all_count = all.count

to_comp = dreieckszahl all_count 
format "total compare: %\n" to_comp
 
compare_count = 0
instance_found = 0



while (all_count>1) do
(
	obj_x = all[all_count]
	
-- 	random_wirecolor obj_x
	
	deleteItem all all_count
	all_count -= 1
	
	to_delete = #()
	for x =1 to all_count do
	(
		obj_y = all[x]
		compare_count += 1
		
		
-- 		format "compare % <-> %\n" obj_x.name obj_y.name
		if (areNodesInstances obj_x obj_y) or (obj_x.baseobject == obj_y.baseobject) then (
			instance_found += 1
			obj_y.wirecolor = obj_x.wirecolor
			format "instance found % <-> %\n" obj_x.name obj_y.name
			append to_delete x
		)
	)
	
	-- remove all instances from the list
	
-- 	format "%\n" to_delete
	qsort to_delete compare reverse:on
-- 	format "%\n" to_delete
	for i in to_delete do
	(
-- 		format "remove % (%)\n" i all[i]
		deleteItem all i
	)
	
	all_count = all.count
	windows.processPostedMessages()
)

format "Compare count: % - Instance found: %\n" compare_count instance_found

format "force garbage collection:"
gc()
--light:true
enableSceneRedraw()
max views redraw
format " - END -\n"
