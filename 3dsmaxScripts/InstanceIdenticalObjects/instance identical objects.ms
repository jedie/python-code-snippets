--
-- ----------------------------
-- instance identical objects
-- ----------------------------
--
-- replace identical geometry objects with instances.
--
-- TODO:
--  * How can we scroll the result edittext field?
--
--
-- copyleft (c) 2010 by htFX, Jens Diemer - http://www.htFX.de
--
--
-- based on scripts:
--  * "Find identical geometry and instance it. " by Martin Enthed (at IKEA Communications AB)
--  * "Instance Identical Geometry" by Anubis [project3d.narod.ru]
--


-- display debug messages in script listener:
DEBUG = false
-- DEBUG = true


if DEBUG then (
	actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
	clearListener()
)


fn is_sameGeometry a b = (
		-- return:
		-- 1: is alrady instanced
		-- 2: not the same (can't replace with instance
		-- 3: instanceable objects

		-- is already Instanced ?
		if (areNodesInstances a b) then (
			if DEBUG then format "Already Instanced.\n"
			return 1
		)
		
		-- are the same class?
		class_a=classof a
		class_b=classof b
		if (class_a!=class_b) then (
			if DEBUG then format "has not the same class.\n"
			return 2
		)
		
		-- bounding box has the same size?
		if DEBUG then format "check BoundingBox..."
		boundingbox_size_a = (nodeGetBoundingBox a a.transform) as string
		boundingbox_size_b = (nodeGetBoundingBox b b.transform) as string
		if (boundingbox_size_a != boundingbox_size_b) then (
			if DEBUG then format "is not the same.\n"
			return 2
		)
		if DEBUG then format "has the same BoundingBox size.\n"
		
		-- polygon count is the same?
		if DEBUG then format "check PolygonCount..."
		polycount_a=(getPolygonCount a) as string
		polycount_b=(getPolygonCount b) as string
		if (polycount_a != polycount_b) then (
			if DEBUG then format "is not the same.\n"
			return 2
		)
		if DEBUG then format "has same PolygonCount.\n"
		
		format "instanceable object found!"
		return 3
	)

rollout InstanceIdenticalObjectsRollout "instance identical objects" width:730 height:550
(
	button btn_instanceIt "Instance:" align:#left width: 120
	radioButtons object_filter labels:#("selected objects", "all objects") align:#left offset:[130,-23]
	group "result"
	(
		edittext result height:330 readOnly:true
		
		label total_lable "total nodes processed: " align:#left
		progressbar total_progress color:blue
		
		label instance_made_lable "new instance made:" align:#left
		progressbar instance_made_progress color:green
		
		label instance_found_lable "instance found:" align:#left
		progressbar instance_found_progress color:black
		
		hyperlink theHyperlink "copyleft (c) 2010 by htFX, Jens Diemer - http://www.htFX.de" url:"http://www.htFX.de" color:blue across:2 align:#right offset:[130,10]
	)

	on btn_instanceIt pressed do
	(
		result.text+="hold the scene, so you can revert with fetch..."
		max hold
		result.text += "OK\r\n"
		
		case object_filter.state of (
			1: (
				result.text+="process selected nodes\r\n"
				all = selection as array
			)
			2: (
				result.text+="process all geometry nodes\r\n"
				all=$*/geometry as array
			)
		)
		
		max create mode -- faster than modify tab (if objects selected)

		all_count = all.count

		compare_count = 0
		to_compare_count = int((all_count-1) * floor(all_count / 2))
		
		-- 'reset' old instance progress bar (run in the past)
		instance_made_progress.value = 0
		instance_made_lable.text = "instance made: 0"
		instance_found_progress.value = 0
		instance_found_lable.text = "instance found: 0"
		
		-- start
		y_all = deepcopy all -- use deepcopy to make y_all independent

		instances_made_count=0
		instances_found_count=0
		
		for x = 1 to all_count do
		(
			obj_x = all[x]
			
			y_all_count = y_all.count
			y = y_all_count

			while (y>0) do
			(
				if DEBUG then format "\n------------------------------------------------------------------\n"

				obj_y = y_all[y]
				if DEBUG then format "compare % <-> %\n" obj_x.name obj_y.name

				-- statuscode are:
				-- 1: is alrady instanced
				-- 2: not the same (can't replace with instance)
				-- 3: instanceable objects			
				statuscode = is_samegeometry obj_x obj_y
				case statuscode of
				(
					1: (
						if DEBUG then format "is alrady instanced: % <-> %\n" obj_x.name obj_y.name
						instances_found_count+=1
						instance_found_lable.text = "instance found: " + instances_found_count as string
						instance_found_progress.value = 100.*instances_found_count/all_count
					)
					2: (
						if DEBUG then format "not the same: % <-> %\n" obj_x.name obj_y.name
					)
					3: ( --instanceable objects
						msg = "instanceReplace: "+obj_x.name+"<->"+obj_y.name+"\r\n"
						if DEBUG then format msg
						result.text+=msg
						
						instanceReplace obj_x obj_y
						
						instances_made_count+=1
						instance_made_lable.text = "instance made: " + instances_made_count as string
						instance_made_progress.value = 100.*instances_made_count/all_count
					)
				)
				compare_count += 1
				total_progress.value = 100.*compare_count/to_compare_count
				if (statuscode == 1 or statuscode == 3) do (
					-- we must not test the object again:
					deleteItem y_all y 
					y_all_count -= 1
					to_compare_count = (compare_count + int((y_all_count) * floor(y_all_count / 2))/2) -- FIXME
					y = 0 -- exit from while loop ('exit' statement is very slow!)
				)
				y -= 1
			)
			total_lable.text = "total nodes processed: " + x as string + " (to compare: " + compare_count as string + "/" + to_compare_count as string + ")"
		)	
		result.text+="\r\n"+(all_count as string)+ " nodes processed.\r\n"
		result.text+=(instances_made_count as string)+ " instanced made.\r\n"
		result.text+=(instances_found_count as string)+ " instanced found.\r\n"
		result.text+="------------------------------------------------------------------\r\n"
	)
)

createdialog InstanceIdenticalObjectsRollout