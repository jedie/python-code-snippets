
-- based on code from http://forums.cgsociety.org/showpost.php?p=5363342&postcount=2
-- http://forums.cgsociety.org/showthread.php?f=98&t=1044601
-- http://area.autodesk.com/forum/t65796

clearlistener()
actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener

fn refCopy source_obj =
(
	-- Create a point as base for the copy and assign a uniquename
	new_obj = point name:(uniqueName source_obj.name)
	
	-- Put in same place as old object
	new_obj.transform = source_obj.transform
	
	-- Give it a clean base to add Modifiers to
	new_obj.baseObject = copy source_obj.baseObject
	
	-- Get modifier count
	modC = source_obj.modifiers.count	
	
	-- Make sure there are modifiers
	if modC != 0 then
		-- Loop through all modifiers and copy them backwards (topmost is nr1!)
		for i in 1 to ModC do
			-- Copy the modifier before the last
			addModifier new_obj ( copy source_obj.modifiers[i] ) before:i
		
	-- Instance base object only, leaving mods
	new_obj.baseObject = source_obj.baseObject

	-- transfer material
	new_obj.material = source_obj.material
		
	-- Return the new object
	new_obj
)

with undo on (
	newObject = refCopy selection[1]
	select newObject
)