--
-- TB Mailer
--
-- copyright (c) 2007 by htFX, Jens Diemer - http://www.htFX.de
--
-- license:
--      GNU General Public License v2 or above
--      http://www.opensource.org/licenses/gpl-license.php
--
--
-- Save the last rendered picture as jpeg and compose a mail with thunderbird
--
--
-- Tested with MAX 9
--
-- Note:
--    You must insert the right path to thunderbird.exe !!!
--
-- Install:
--		1. goto "Customize/Cusomize User Interface/Toolbars"
--		2. goto Category: "htFX Scripts"
--		3. Drag&Drop the Action to you Toolbar
--
-- more Info: "MaxScript Reference/MacroScripts for New Users"
--
--
-- subversion information:
--  $HeadURL$
--  $LastChangedDate$
--  $Rev$
--  $Author$
--
-- license:
--   GNU General Public License v2 or above
--   http://www.opensource.org/licenses/gpl-license.php
--
-- copyright (c) 2007 by htFX, Jens Diemer - http://www.htFX.de
--

-- actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

suffix = "preview"
seperator = "_"
ext = ".jpg"


-----------------------------------

function setup_tb_path = (
	-- Dialog to setup the path to TB

	Messagebox "thunderbird.exe not found!\nPlease open it in the next dialog."

	tb_path = getOpenFileName \
		caption:"Open A Test File:" \
		filename:"thunderbird.exe" \
		types:"thunderbird.exe|thunderbird.exe" \
		initialDir:"$scripts"

	if tb_path == undefined then return false

	if doesfileexist tb_path == false then (
	 	Messagebox "thunderbird.exe not found!"
		return false
	)

	ini_file = get_ini_path()
	setINISetting ini_file "thunderbird" "path" tb_path

	return tb_path
)

function get_ini_path = (
	-- return the path to the .ini file

	path = pathConfig.appendPath "$scripts" "mailLastRendered.ini"

	print "ini path:"
	print path

	return path
)

function get_mailer_path = (
	-- return the path to thunderbird.exe

	ini_file = get_ini_path()
	print ini_file
	tb_path = GetINISetting ini_file "thunderbird" "path"
	if tb_path == "" then (
		tb_path = setup_tb_path()
	)
	print "Thunderbird path:"
	print tb_path

	if tb_path == false then return false

	if doesfileexist tb_path == false then (
	 	Messagebox "thunderbird.exe not found!"
		return false
	)

	return tb_path
)
-----------------------------------


function abs_filename filename = (
	-- make filename absolute, using maxFilePath
	return maxFilePath + filename
)


function get_clean_maxFileName = (
	-- Script filename without the last part
	-- convert spaces into "_"

	-- split string into a Array
	tokens = filterString maxFileName " "

	-- join the tokens without the last one
	len = tokens.count-1
	clean_filename = ""
	for i = 1 to len do (
  		clean_filename += "_" + tokens[i]
	)
	clean_filename = trimLeft clean_filename "_"
    return clean_filename
)


function get_expand_filename source_filename = (
	-- Expand the filename with a number and suffix + ext
	i = 0
    while true do (
		i += 1

		no = i as String
		if no.count == 1 do (
			no = "0" + no
		)

		filename = source_filename + no + ext
		abs_path = abs_filename(filename)
		if not doesfileexist abs_path then (
			-- Dateiname existiert noch nicht -> OK
			return filename
		)
	)
)

-----------------------------------

function main = (
	if maxFileName == "" then (
		messageBox "Error: You must save the scene first!"
		return false
	)

	thunderbird_path = get_mailer_path()
	print "TB path:"
    print thunderbird_path

	if thunderbird_path == false then return false

	clean_filename = get_clean_maxFileName()
	print clean_filename

	filename = clean_filename + seperator + suffix + seperator

	filename = get_expand_filename(filename)
	abs_path = abs_filename(filename)
	print filename
	print abs_path

	JPEG.setQuality(90)
	--image_file = gw.getViewportDib()
	image_file = getLastRenderedImage()
	if image_file == undefined then (
		messageBox "Error: You must render a picture first!"
		return false
	)
	image_file.filename = abs_path
	save image_file

	cmd_string = thunderbird_path + " -compose \""
	cmd_string += "subject=" + filename
	cmd_string += ",body=" + filename
	cmd_string += ",attachment='file://" + abs_path + "'"
	cmd_string += "\""

	print cmd_string

	Doscommand cmd_string
)

-- Start the Script
main()


-- END