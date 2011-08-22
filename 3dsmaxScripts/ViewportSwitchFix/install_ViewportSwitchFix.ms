
-- actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
-- clearListener()

print "install ViewportSwitchFix..."

src = GetDir #temp + "/ViewportSwitchFix.ms"
dst = GetDir #userStartupScripts  + "/ViewportSwitchFix.ms"

if (doesFileExist dst) then (
	format "remove existing file %...\n" dst
	deleteFile dst
	print "OK"
)

format "copy % to %...\n" src dst
System_IO_File = dotNetClass "System.IO.File"
System_IO_File.Copy src dst
print "OK"

print "run the macro, to install it..."
filein "$userMacros//ViewportSwitchFix.mcr"
print "OK"

-- Display only a small Info
str = "Script installed.\n
1. goto 'Customize/Cusomize User Interface/Keyboard'
2. assign t,l,f,p,c etc. to '_htFX.de maxscripts'
"
messageBox str title:"Script installed."

actionMan.executeAction 0 "59226"  -- Customize User Interface: Customize User Interface

print "-- END --"