#coding:utf-8

from string import Template

VIEWS_DATA = (
    ("_T", "top", "false"),
    ("_B", "bottom", "false"),
    ("", "right", "false"),
    ("_L", "left", "false"),
    ("_F", "front", "false"),
    ("", "back", "false"),
    ("_P", "persp_user", "false"),
    ("_U", "iso_user", "false"),
    ("_C", "camera", "true"),
    ("", "spot", "false"),
    ("", "shape", "false"),
    ("", "grid", "false"),
)

SCRIPT = """
macroScript to_%(view_name)sView%(key)s category:"_htFX.de maxscripts"
(
    htfx_switch_viewport #view_%(view_name)s %(additional)s
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


for key, view_name, additional in VIEWS_DATA:
    print key, view_name, additional

    script_compiled = SCRIPT % {
        "key": key,
        "view_name":view_name,
        "additional":additional
    }
    print "-"*79
    print script_compiled
    print "-"*79

    f.write(script_compiled)

f.close()