--
-- copyright (c) 2007 by htFX, Jens Diemer - http://www.htFX.de
--
-- license:
--      GNU General Public License v2 or above
--      http://www.opensource.org/licenses/gpl-license.php
--
--
--
-- a simple time shift
-- -------------------
-- workflow:
--   1. make a key frame animation with an object
--   2. make copies with "Tools/Array"
--   3. select all objects
--   4. run the script "Ctrl-E"
--
--
-- Tested with MAX 9
--

--actionMan.executeAction 0 "40472"  -- MAX Script: MAXScript Listener
clearListener()


time_offset = 2 -- How much offset for every Object?


for x = 0 to selection.count-1 do
(
	insertTime selection[x+1] 0f (time_offset * x)
)