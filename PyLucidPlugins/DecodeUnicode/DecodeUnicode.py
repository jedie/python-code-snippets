#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    DecodeUnicode - a small PyLucid Plugin

    Last commit info:
        $LastChangedDate$
        $Rev$
        $Author$
"""

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"
__url__     = "http://www.PyLucid.org"
__version__ = "$Rev$"


import unicodedata


from PyLucid.system.BasePlugin import PyLucidBasePlugin


BLOCKS = [
    {"range": (0x0000, 0x007F), "name": "Basic Latin"},
    {"range": (0x0080, 0x00FF), "name": "Latin-1 Supplement"},
    {"range": (0x0100, 0x017F), "name": "Latin Extended-A"},
    {"range": (0x0180, 0x024F), "name": "Latin Extended-B"},
    {"range": (0x0250, 0x02AF), "name": "IPA Extensions"},
    {"range": (0x02B0, 0x02FF), "name": "Spacing Modifier Letters"},
    {"range": (0x0300, 0x036F), "name": "Combining Diacritical Marks"},
    {"range": (0x0370, 0x03FF), "name": "Greek and Coptic"},
    {"range": (0x0400, 0x04FF), "name": "Cyrillic"},
    {"range": (0x0500, 0x052F), "name": "Cyrillic Supplement"},
    {"range": (0x0530, 0x058F), "name": "Armenian"},
    {"range": (0x0590, 0x05FF), "name": "Hebrew"},
    {"range": (0x0600, 0x06FF), "name": "Arabic"},
    {"range": (0x0700, 0x074F), "name": "Syriac"},
    {"range": (0x0750, 0x077F), "name": "Arabic Supplement"},
    {"range": (0x0780, 0x07BF), "name": "Thaana"},
    {"range": (0x0900, 0x097F), "name": "Devanagari"},
    {"range": (0x0980, 0x09FF), "name": "Bengali"},
    {"range": (0x0A00, 0x0A7F), "name": "Gurmukhi"},
    {"range": (0x0A80, 0x0AFF), "name": "Gujarati"},
    {"range": (0x0B00, 0x0B7F), "name": "Oriya"},
    {"range": (0x0B80, 0x0BFF), "name": "Tamil"},
    {"range": (0x0C00, 0x0C7F), "name": "Telugu"},
    {"range": (0x0C80, 0x0CFF), "name": "Kannada"},
    {"range": (0x0D00, 0x0D7F), "name": "Malayalam"},
    {"range": (0x0D80, 0x0DFF), "name": "Sinhala"},
    {"range": (0x0E00, 0x0E7F), "name": "Thai"},
    {"range": (0x0E80, 0x0EFF), "name": "Lao"},
    {"range": (0x0F00, 0x0FFF), "name": "Tibetan"},
    {"range": (0x1000, 0x109F), "name": "Myanmar"},
    {"range": (0x10A0, 0x10FF), "name": "Georgian"},
    {"range": (0x1100, 0x11FF), "name": "Hangul Jamo"},
    {"range": (0x1200, 0x137F), "name": "Ethiopic"},
    {"range": (0x1380, 0x139F), "name": "Ethiopic Supplement"},
    {"range": (0x13A0, 0x13FF), "name": "Cherokee"},
    {"range": (0x1400, 0x167F), "name": "Unified Canadian Aboriginal Syllabics"},
    {"range": (0x1680, 0x169F), "name": "Ogham"},
    {"range": (0x16A0, 0x16FF), "name": "Runic"},
    {"range": (0x1700, 0x171F), "name": "Tagalog"},
    {"range": (0x1720, 0x173F), "name": "Hanunoo"},
    {"range": (0x1740, 0x175F), "name": "Buhid"},
    {"range": (0x1760, 0x177F), "name": "Tagbanwa"},
    {"range": (0x1780, 0x17FF), "name": "Khmer"},
    {"range": (0x1800, 0x18AF), "name": "Mongolian"},
    {"range": (0x1900, 0x194F), "name": "Limbu"},
    {"range": (0x1950, 0x197F), "name": "Tai Le"},
    {"range": (0x1980, 0x19DF), "name": "New Tai Lue"},
    {"range": (0x19E0, 0x19FF), "name": "Khmer Symbols"},
    {"range": (0x1A00, 0x1A1F), "name": "Buginese"},
    {"range": (0x1D00, 0x1D7F), "name": "Phonetic Extensions"},
    {"range": (0x1D80, 0x1DBF), "name": "Phonetic Extensions Supplement"},
    {"range": (0x1DC0, 0x1DFF), "name": "Combining Diacritical Marks Supplement"},
    {"range": (0x1E00, 0x1EFF), "name": "Latin Extended Additional"},
    {"range": (0x1F00, 0x1FFF), "name": "Greek Extended"},
    {"range": (0x2000, 0x206F), "name": "General Punctuation"},
    {"range": (0x2070, 0x209F), "name": "Superscripts and Subscripts"},
    {"range": (0x20A0, 0x20CF), "name": "Currency Symbols"},
    {"range": (0x20D0, 0x20FF), "name": "Combining Diacritical Marks for Symbols"},
    {"range": (0x2100, 0x214F), "name": "Letterlike Symbols"},
    {"range": (0x2150, 0x218F), "name": "Number Forms"},
    {"range": (0x2190, 0x21FF), "name": "Arrows"},
    {"range": (0x2200, 0x22FF), "name": "Mathematical Operators"},
    {"range": (0x2300, 0x23FF), "name": "Miscellaneous Technical"},
    {"range": (0x2400, 0x243F), "name": "Control Pictures"},
    {"range": (0x2440, 0x245F), "name": "Optical Character Recognition"},
    {"range": (0x2460, 0x24FF), "name": "Enclosed Alphanumerics"},
    {"range": (0x2500, 0x257F), "name": "Box Drawing"},
    {"range": (0x2580, 0x259F), "name": "Block Elements"},
    {"range": (0x25A0, 0x25FF), "name": "Geometric Shapes"},
    {"range": (0x2600, 0x26FF), "name": "Miscellaneous Symbols"},
    {"range": (0x2700, 0x27BF), "name": "Dingbats"},
    {"range": (0x27C0, 0x27EF), "name": "Miscellaneous Mathematical Symbols-A"},
    {"range": (0x27F0, 0x27FF), "name": "Supplemental Arrows-A"},
    {"range": (0x2800, 0x28FF), "name": "Braille Patterns"},
    {"range": (0x2900, 0x297F), "name": "Supplemental Arrows-B"},
    {"range": (0x2980, 0x29FF), "name": "Miscellaneous Mathematical Symbols-B"},
    {"range": (0x2A00, 0x2AFF), "name": "Supplemental Mathematical Operators"},
    {"range": (0x2B00, 0x2BFF), "name": "Miscellaneous Symbols and Arrows"},
    {"range": (0x2C00, 0x2C5F), "name": "Glagolitic"},
    {"range": (0x2C80, 0x2CFF), "name": "Coptic"},
    {"range": (0x2D00, 0x2D2F), "name": "Georgian Supplement"},
    {"range": (0x2D30, 0x2D7F), "name": "Tifinagh"},
    {"range": (0x2D80, 0x2DDF), "name": "Ethiopic Extended"},
    {"range": (0x2E00, 0x2E7F), "name": "Supplemental Punctuation"},
    {"range": (0x2E80, 0x2EFF), "name": "CJK Radicals Supplement"},
    {"range": (0x2F00, 0x2FDF), "name": "Kangxi Radicals"},
    {"range": (0x2FF0, 0x2FFF), "name": "Ideographic Description Characters"},
    {"range": (0x3000, 0x303F), "name": "CJK Symbols and Punctuation"},
    {"range": (0x3040, 0x309F), "name": "Hiragana"},
    {"range": (0x30A0, 0x30FF), "name": "Katakana"},
    {"range": (0x3100, 0x312F), "name": "Bopomofo"},
    {"range": (0x3130, 0x318F), "name": "Hangul Compatibility Jamo"},
    {"range": (0x3190, 0x319F), "name": "Kanbun"},
    {"range": (0x31A0, 0x31BF), "name": "Bopomofo Extended"},
    {"range": (0x31C0, 0x31EF), "name": "CJK Strokes"},
    {"range": (0x31F0, 0x31FF), "name": "Katakana Phonetic Extensions"},
    {"range": (0x3200, 0x32FF), "name": "Enclosed CJK Letters and Months"},
    {"range": (0x3300, 0x33FF), "name": "CJK Compatibility"},
    {"range": (0x3400, 0x4DBF), "name": "CJK Unified Ideographs Extension A"},
    {"range": (0x4DC0, 0x4DFF), "name": "Yijing Hexagram Symbols"},
    {"range": (0x4E00, 0x9FFF), "name": "CJK Unified Ideographs"},
    {"range": (0xA000, 0xA48F), "name": "Yi Syllables"},
    {"range": (0xA490, 0xA4CF), "name": "Yi Radicals"},
    {"range": (0xA700, 0xA71F), "name": "Modifier Tone Letters"},
    {"range": (0xA800, 0xA82F), "name": "Syloti Nagri"},
    {"range": (0xAC00, 0xD7AF), "name": "Hangul Syllables"},
    {"range": (0xD800, 0xDB7F), "name": "High Surrogates"},
    {"range": (0xDB80, 0xDBFF), "name": "High Private Use Surrogates"},
    {"range": (0xDC00, 0xDFFF), "name": "Low Surrogates"},
    {"range": (0xE000, 0xF8FF), "name": "Private Use Area"},
    {"range": (0xF900, 0xFAFF), "name": "CJK Compatibility Ideographs"},
    {"range": (0xFB00, 0xFB4F), "name": "Alphabetic Presentation Forms"},
    {"range": (0xFB50, 0xFDFF), "name": "Arabic Presentation Forms-A"},
    {"range": (0xFE00, 0xFE0F), "name": "Variation Selectors"},
    {"range": (0xFE10, 0xFE1F), "name": "Vertical Forms"},
    {"range": (0xFE20, 0xFE2F), "name": "Combining Half Marks"},
    {"range": (0xFE30, 0xFE4F), "name": "CJK Compatibility Forms"},
    {"range": (0xFE50, 0xFE6F), "name": "Small Form Variants"},
    {"range": (0xFE70, 0xFEFF), "name": "Arabic Presentation Forms-B"},
    {"range": (0xFF00, 0xFFEF), "name": "Halfwidth and Fullwidth Forms"},
    {"range": (0xFFF0, 0xFFFF), "name": "Specials"},
    {"range": (0x10000, 0x1007F), "name": "Linear B Syllabary"},
    {"range": (0x10080, 0x100FF), "name": "Linear B Ideograms"},
    {"range": (0x10100, 0x1013F), "name": "Aegean Numbers"},
    {"range": (0x10140, 0x1018F), "name": "Ancient Greek Numbers"},
    {"range": (0x10300, 0x1032F), "name": "Old Italic"},
    {"range": (0x10330, 0x1034F), "name": "Gothic"},
    {"range": (0x10380, 0x1039F), "name": "Ugaritic"},
    {"range": (0x103A0, 0x103DF), "name": "Old Persian"},
    {"range": (0x10400, 0x1044F), "name": "Deseret"},
    {"range": (0x10450, 0x1047F), "name": "Shavian"},
    {"range": (0x10480, 0x104AF), "name": "Osmanya"},
    {"range": (0x10800, 0x1083F), "name": "Cypriot Syllabary"},
    {"range": (0x10A00, 0x10A5F), "name": "Kharoshthi"},
    {"range": (0x1D000, 0x1D0FF), "name": "Byzantine Musical Symbols"},
    {"range": (0x1D100, 0x1D1FF), "name": "Musical Symbols"},
    {"range": (0x1D200, 0x1D24F), "name": "Ancient Greek Musical Notation"},
    {"range": (0x1D300, 0x1D35F), "name": "Tai Xuan Jing Symbols"},
    {"range": (0x1D400, 0x1D7FF), "name": "Mathematical Alphanumeric Symbols"},
    {"range": (0x20000, 0x2A6DF), "name": "CJK Unified Ideographs Extension B"},
    {"range": (0x2F800, 0x2FA1F), "name": "CJK Compatibility Ideographs Supplement"},
    {"range": (0xE0000, 0xE007F), "name": "Tags"},
    {"range": (0xE0100, 0xE01EF), "name": "Variation Selectors Supplement"},
    {"range": (0xF0000, 0xFFFFF), "name": "Supplementary Private Use Area-A"},
    {"range": (0x100000, 0x10FFFF), "name": "Supplementary Private Use Area-B"},
]


class DecodeUnicode(PyLucidBasePlugin):

    def lucidTag(self):
        self.display("0")

    def display(self, function_info=None):

        if function_info:
            # Use the block position from the URL
            try:
                function_info = function_info.strip("/")
                block_id = int(function_info)
            except (TypeError, ValueError, IndexError):
                self.page_msg.red("Wrong URL, please select a Block!")
                return
        else:
            # Use the block position from POST data
            try:
                block_id = self.request.POST.get("block", 0)
                block_id = int(block_id)
            except ValueError:
                self.page_msg.red("Form Error!")
                return

        try:
            block = BLOCKS[block_id]
        except IndexError:
            self.page_msg.red("Block %s not exists!" % block_id)
            return

        block_range = block["range"]
        block_data = self._get_block_data(block_range)

        back_id = block_id - 1
        if back_id < 0:
            back_id = 0

        next_id = block_id + 1
        if next_id >= len(BLOCKS):
            next_id = block_id

        block_select_data = self._get_select_data()

        context = {
            "selected_id": block_id,
            "block_select_data": block_select_data,
            "block_select_url": self.URLs.methodLink("display"),

            "back_url"  : self.URLs.methodLink("display", back_id),
            "back_name"  : BLOCKS[back_id]["name"],
            "next_url"  : self.URLs.methodLink("display", next_id),
            "next_name"  : BLOCKS[next_id]["name"],

            "url"       : self.URLs.methodLink("display", block_id),
            "block_name": block["name"],

            "range_hex1": "0x%04X" % block_range[0],
            "range_hex2": "0x%04X" % block_range[1],

            "block_data": block_data,

            "unidata_version": unicodedata.unidata_version,
        }
        self._render_template("display", context)#, debug=True)

    def _get_select_data(self):
        """
        The data for the html select form.
        """
        block_select_data = []
        for id, block in enumerate(BLOCKS):
            block_select_data.append({
                "id": id,
                "name": "0x%04X-0x%04X - %s" % (
                    block["range"][0], block["range"][1], block["name"]
                )
            })
        return block_select_data

    def _get_block_data(self, block):
        """
        Data for the current block table.
        """
        data = []
        for no in xrange(int(block[0]), int(block[1])):
            char = unichr(no)
            char_code = "%X" % no

            unicode_number = "000%s" % char_code
            unicode_number = unicode_number[-4:]

            unicode_value = "\\u%s" % unicode_number
            hex_value = "\\x%s" % char_code
            HTML = "&#x%s;" % char_code
            name = unicodedata.name(char, "(no unicode name)")

            data.append({
                "id": no,
                "char": char,
                "unicode_number": unicode_number,
                "unicode": unicode_value,
                "hex": hex_value,
                "html": HTML,
                "name": name,
            })
        return data