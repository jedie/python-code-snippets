--
-- Mail grabbed viewports via Thunderbird Mailer
--
-- Please read the readme.txt !
--
-- license:
--   GNU General Public License v3 or above
--   http://www.opensource.org/licenses/gpl-license.php
--
-- copyleft (c) 2016 by htFX, Jens Diemer - http://www.htFX.de
--

actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()

suffix = "screenshot"
seperator = "_"
ext = ".jpg"



function grab_viewports = (
	-- http://help.autodesk.com/view/3DSMAX/2016/ENU/?guid=__files_GUID_8AA71F9E_F4F0_4437_A44E_9683619E89DE_htm
	viewport1 = viewport.getViewportDib index:1 gammaCorrect:False
	viewport2 = viewport.getViewportDib index:2 gammaCorrect:False
	viewport3 = viewport.getViewportDib index:3 gammaCorrect:False
	viewport4 = viewport.getViewportDib index:4 gammaCorrect:False

	gap=4

	width=viewport1.width + viewport2.width
	height=viewport1.height + viewport3.height

	width=width + (gap * 3)
	height=height + (gap * 3)

	viewports=bitmap width height color:black

	-- pasteBitmap <src_bitmap> <dest_bitmap> (<src_box2> | <src_point2>) <dest_point2> \
	-- [maskColor:<color>type:{#paste|#composite|#blend|#function}] \
	-- [function:<composite_fn>] [alphaMultiplier:<float>] 

	pasteBitmap viewport1 viewports [0,0] [gap, gap]
	pasteBitmap viewport2 viewports [0,0] [viewport1.width+(gap*2), gap]
	pasteBitmap viewport3 viewports [0,0] [gap, viewport1.height+(gap*2)]
	pasteBitmap viewport4 viewports [0,0] [viewport1.width+(gap*2), viewport1.height+(gap*2)]

    return viewports
)

------------------------------------------------------------------------------

function get_ini_path = (
    -- return the path to the .ini file

    ini_path = pathConfig.appendPath "$userScripts" "mailLastRendered.ini"

    print "ini_path:"
    print ini_path

    return ini_path
)

function setup_tb_path = (
    -- Dialog to setup the path to TB

    Messagebox "thunderbird.exe not found!\nPlease open it in the next dialog."

    tb_path = getOpenFileName \
        caption:"Open A Test File:" \
        filename:"thunderbird.exe" \
        types:"thunderbird.exe|thunderbird.exe" \
        initialDir:"$userScripts"

    if tb_path == undefined then return false

    if doesfileexist tb_path == false then (
        Messagebox "thunderbird.exe not found!"
        return false
    )

    ini_file = get_ini_path()
    setINISetting ini_file "thunderbird" "path" tb_path

    return tb_path
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

------------------------------------------------------------------------------

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

------------------------------------------------------------------------------

image_file = undefined

function main = (
    if maxFileName == "" then (
        messageBox "Error: You must save the scene first!"
        return false
    )

    thunderbird_exe = get_mailer_path()
	format "TB path: '%'\n" thunderbird_exe

    if thunderbird_exe == false then return false

    clean_filename = get_clean_maxFileName()
    format "clean_filename: '%'\n" clean_filename

    filename = clean_filename + seperator + suffix + seperator

    filename = get_expand_filename(filename)
    abs_path = abs_filename(filename)
    format "filename: '%'\n" filename

	format "get the image\n"
	
	image_file = grab_viewports()
-- 	display image_file

	format "save file dialog\n"
    type_filter = "*" + ext + "|*" + ext
    abs_path = getSaveFileName caption:"save rendered pic" filename:abs_path types:type_filter
    if abs_path == undefined then (
        return false
    )
    format "abs_path:\n%\n" abs_path

    -- use the filename from the getSaveFileName dialog
    tokens = filterString abs_path "\\"
    filename = tokens[tokens.count]

    tokens = filterString filename ","
    if tokens.count>1 then (
        messageBox "Error: Invalid filename. Filename may contain no commas!"
        return false
    )

    image_file.filename = abs_path
    JPEG.setQuality(90)
    save image_file

    cmd_string = " -compose \""
    cmd_string += "subject=" + filename
    cmd_string += ",body=" + filename
    cmd_string += ",attachment='file:///" + abs_path + "'"

    format "cmd line:\n%\n" cmd_string

    shellLaunch thunderbird_exe cmd_string
)

------------------------------------------------------------------------------

-- Start the Script
main()


-- END



