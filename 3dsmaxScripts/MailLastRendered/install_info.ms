
-- run the macro, to install it
filein "$userScripts//mailLastRendered.mcr"

-- Display only a small Info
str = "Script installed.\n
1. goto 'Customize/Cusomize User Interface/Toolbars'
2. goto Category: '_htFX Scripts'
3. Drag and Drop the Action to you Toolbar
"
messageBox str title:"Script installed."

actionMan.executeAction 0 "59226"  -- Customize User Interface: Customize User Interface
