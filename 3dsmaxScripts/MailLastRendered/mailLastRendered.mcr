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

macroScript mailRenderedImage
	Category: "_htFX scripts"
	Tooltip: "Mail the last rendered picure"
	Buttontext: "mail"
	Icon:#("Maintoolbar",69)
(
    -- actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
    -- clearListener()
    filein "$Scripts//mailLastRendered.ms"
)
