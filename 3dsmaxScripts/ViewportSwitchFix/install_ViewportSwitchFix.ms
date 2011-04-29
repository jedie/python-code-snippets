
-- run the macro, to install it
filein "$userScripts//ViewportSwitchFix.mcr"

-- Display only a small Info
str = "Script installed.\n
1. goto 'Customize/Cusomize User Interface/Keyboard'
2. assign t,l,f,p,c etc. to '_htFX.de maxscripts'
"
messageBox str title:"Script installed."

actionMan.executeAction 0 "59226"  -- Customize User Interface: Customize User Interface
