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
-- copyleft (c) 2010-2015 by htFX, Jens Diemer - http://www.htFX.de
--
--
-- based on scripts:
--  * "Find identical geometry and instance it. " by Martin Enthed (at IKEA Communications AB)
--  * "Instance Identical Geometry" by Anubis [project3d.narod.ru]
--


-- display debug messages in script listener:
DEBUG = false
-- DEBUG = true


-- if DEBUG then (
	actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
	clearListener()
-- )


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

fn compare n1 n2 reverse:off = 
(	-- for reversed qsort
	a = if n1 < n2 then -1 else if n1 > n2 then 1 else 0
	if reverse then -a else a
)


fn is_sameGeometry a b = (
		-- return:
		-- 1: is alrady instanced
		-- 2: not the same (can't replace with instance
		-- 3: instanceable objects

		-- is already Instanced ?
		if (areNodesInstances a b) then (
			if DEBUG then format "Already a instance.\n"
			return 1
		)
		
		-- http://forums.cgsociety.org/showpost.php?p=6000653&postcount=2
		if (a.baseobject == b.baseobject) then (
			if DEBUG then format "Already a referece.\n"
			return 1
		)
		
		-- are the same class?
		class_a=classof a
		class_b=classof b
		if (class_a != class_b) then (
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
		if DEBUG then format "has same PolygonCount -> instanceable object found!\n"
		
		return 3
	)


 
rollout InstanceIdenticalObjectsRollout "instance identical objects" width:730 height:550
(
	button btn_instanceIt "Instance:" align:#left width: 120
	radioButtons object_filter labels:#("selected objects", "all objects") align:#left offset:[130,-23]
	checkbox InstanceReplaceCheckBox "use alternative InstanceReplace (usefull if max crashed)"
	group "result"
	(
		edittext result height:330 readOnly:true
		
		label total_lable "total nodes processed: " align:#left
		progressbar total_progress color:blue
		
		label instance_made_lable "new instance made:" align:#left
		progressbar instance_made_progress color:green
		
		label instance_found_lable "instance found:" align:#left
		progressbar instance_found_progress color:black
		
		hyperlink theHyperlink "copyleft (c) 2010 by htFX, Jens Diemer - www.htFX.de" address:"www.htFX.de" color:blue across:2 align:#right offset:[130,10]
	)

	on btn_instanceIt pressed do
	(
		disableSceneRedraw()
		max create mode -- faster than modify tab (if objects selected)
		
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

		total_obj_count = current_count = all.count

		instances_made_count=0
		instances_found_count=0
		compare_count = 0
		total_compare_count = dreieckszahl current_count
		result.text+="total compare count:" + total_compare_count as String + "\r\n"
		
		-- 'reset' old instance progress bar (run in the past)
		instance_made_progress.value = 0
		instance_made_lable.text = "instance made: 0"
		instance_found_progress.value = 0
		instance_found_lable.text = "instance found: 0"
		 
		while (current_count>1) do
		(
			obj_x = all[current_count]
			deleteItem all current_count
			current_count -= 1
			
			to_comp = dreieckszahl current_count 
			format "total compare: %\n" to_comp
			
			skip_in_next_round = #()
			for x =1 to current_count do
			(
				obj_y = all[x]
				compare_count += 1

				to_delete = #()

				if DEBUG then format "compare % <-> %\n" obj_x.name obj_y.name

				-- statuscode are:
				-- 1: is alrady instanced
				-- 2: not the same (can't replace with instance)
				-- 3: instanceable objects			
				statuscode = is_samegeometry obj_x obj_y
				
				if (statuscode == 1 or statuscode == 3) do (
					try(
						obj_y.wirecolor = obj_x.wirecolor
						if DEBUG then format "wirecolor % <-> %\n" obj_x.wirecolor obj_y.wirecolor
					) catch (
						format "Error with %\n" obj
						continue
					)
					-- we must not test the object again:
					append skip_in_next_round x
				)
				
				case statuscode of
				(
					1: (
						if DEBUG then format "is alrady instanced: % <-> %\n" obj_x.name obj_y.name
						instances_found_count+=1
					)
					2: (
						if DEBUG then format "not the same: % <-> %\n" obj_x.name obj_y.name
					)
					3: ( --instanceable objects
						msg = "instanceReplace: "+obj_x.name+"<->"+obj_y.name+"\r\n"
						if DEBUG then format msg
						result.text+=msg
						
						if InstanceReplaceCheckBox.checked then (
							select obj_x
							maxOps.cloneNodes $ cloneType:#instance newNodes:&new_objs
							new_obj = new_objs[1]
							new_obj.transform = obj_y.transform
							new_obj.name = obj_y.name
							append to_delete obj_y
						) else (
							instanceReplace obj_x obj_y
						)
						instances_made_count+=1
					)
				)
			)
		
			-- remove all instances from the list
			qsort skip_in_next_round compare reverse:on
			for i in skip_in_next_round do
			(
		-- 		format "remove % (%)\n" i all[i]
				deleteItem all i
			)

			current_count = all.count
			if (current_count==0) then (
				total_progress.value = 100
				msg = "total nodes processed: " + compare_count as string + " (total compare: " + total_compare_count as string + ")"
			) else (
				to_compare_count = dreieckszahl current_count
				
				msg = "total nodes processed: " + compare_count as string + " (to compare: " + total_compare_count as string + "/" + to_compare_count as string + ")"
				total_lable.text = msg
				if DEBUG then format "*** %\n" msg
				format msg
				total_progress.value = 100.*total_compare_count/to_compare_count
			)
			
			instance_found_lable.text = "instance found: " + instances_found_count as string
			instance_found_progress.value = 100.*instances_found_count/total_obj_count
			
			instance_made_lable.text = "instance made: " + instances_made_count as string
			instance_made_progress.value = 100.*instances_made_count/total_obj_count
			format "%s\n" instance_made_progress.value			
			
			windows.processPostedMessages()
		)
	
		result.text+="\r\n"+(current_count as string)+ " nodes processed.\r\n"
		result.text+=(instances_made_count as string)+ " instanced made.\r\n"
		result.text+=(instances_found_count as string)+ " instanced found.\r\n"
		result.text+="------------------------------------------------------------------\r\n"
		
		if InstanceReplaceCheckBox.checked do (
			result.text+="delete obsolete objects..."
			select to_delete
			max delete
			result.text+="ok\r\n"
		)
		
		format "force garbage collection:"
		gc light:true delayed:true
		enableSceneRedraw()
		max views redraw
		format " - END -\n"
	)
)

createdialog InstanceIdenticalObjectsRollout