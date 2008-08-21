--
-- Thunderbird Mailer
--
-- Please read the readme.txt !
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
-- copyleft (c) 2007-2008 by htFX, Jens Diemer - http://www.htFX.de
--

macroScript mailRenderedImage
    Category: "_htFX scripts"
    Tooltip: "Mail the last rendered picure"
    Buttontext: "mail"
    Icon:#("Maintoolbar",69)
(
    filein "$userScripts//mailLastRendered.ms"
)
