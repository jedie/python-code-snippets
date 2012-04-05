#coding:utf-8

from string import Template

VIEWS_DATA = (
    ("_T", "top", "false", "false"),
    ("_B", "bottom", "false", "false"),
    ("", "right", "false", "false"),
    ("_L", "left", "false", "false"),
    ("_F", "front", "false", "false"),
    ("", "back", "false", "false"),
    ("_P", "persp_user", "false", "true"),
    ("_U", "iso_user", "false", "false"),
    ("_C", "camera", "true", "true"),
    ("", "spot", "false", "false"),
    ("", "shape", "false", "false"),
    ("", "grid", "false", "false"),
)

SCRIPT = """
macroScript to_%(view_name)sView%(key)s category:"_htFX.de maxscripts"
(
    htfx_switch_viewport #view_%(view_name)s %(safeframe)s %(shaded)s
)
"""
#~ FILENAME = "_htFX_de maxscripts-switch2%sView%s.mcr"
#~ RUN_ENTRY = "copy '%s' to $userMacros"
#~ INST_ENTRY = "filein '$userMacros//%s'"


#~ for key, view_name, additional in VIEWS_DATA:
    #~ filename = FILENAME % (view_name, key)
    #~ print RUN_ENTRY % filename

#~ print "-"*79

#~ for key, view_name, additional in VIEWS_DATA:
    #~ filename = FILENAME % (view_name, key)
    #~ print INST_ENTRY % filename

#~ print "-"*79


f = file("ViewportSwitchFix.mcr", "w")
f.write("-- automatic generated with %s\n" % __file__)
f.write("--\n")
f.write("-- copyleft (c) 2011-2012 by htFX, Jens Diemer - http://www.htFX.de\n")
f.write("--\n")


for key, view_name, safeframe, shaded in VIEWS_DATA:
    print key, view_name, safeframe, shaded

    script_compiled = SCRIPT % {
        "key": key,
        "view_name":view_name,
        "safeframe":safeframe,
        "shaded":shaded,
    }
    print "-"*79
    print script_compiled
    print "-"*79

    f.write(script_compiled)

f.close()