/**
 *
 * adds support for tabulators to the textarea
 *
 * :copyright: 2006-2007 by Armin Ronacher.
 * :license: GNU GPL, see LICENSE for more details.
 */

tabs = "    ";
lastkey = -1;

function tabs(e) {
    var e = (e) ? e : window.event;
    alert(e.keyCode);
    if (e.keyCode != 9) {
    //~ if (((e.keyCode) ? e.keyCode : e.which) != 9) {
        return
        lastkey = e.keyCode
    }
    //~ if (e.keyCode == lastkey) { return true; }
    //~ lastkey = e.keyCode

    // For Internet Explorer
    if (document.selection && !textarea.selectionStart &&
        textarea.selectionStart != 0) {
        var range = document.selection.createRange();
        range.text = tabs;
        range.select();
    }
    // Mozilla Browsers
    else if (textarea.selectionStart || textarea.selectionStart == 0) {
        var startVal = textarea.value.substring(0, textarea.selectionStart);
        var endVal = textarea.value.substring(textarea.selectionStart);
        textarea.value = startVal + tabs + endVal;
        textarea.selectionStart = startVal.length + 1;
        textarea.selectionEnd = startVal.length + 1;
        textarea.focus();
    }
    // others won't work, continue with default behaviour
    else {
        return true;
    }
    return false;
}

function tabs_support(textarea_id) {
    var textarea = document.getElementById(textarea_id);
    textarea.onkeydown = tabs;
    //textarea.onkeypress = onKeyDown;
}




page_content_changed = 0;

// resize the textarea
function resize_big() {
    textarea = document.getElementsByTagName("textarea")[0]
    textarea.rows = textarea.rows*1.2;
}
function resize_small() {
    textarea = document.getElementsByTagName("textarea")[0]
    textarea.rows = textarea.rows/1.2;
}

// tinyTextile help and TagList in a window
function OpenInWindow(URL) {
  win1 = window.open(URL, "", "width=1000, height=600, dependent=yes, resizable=yes, scrollbars=yes, location=no, menubar=no, status=no, toolbar=no");
  win1.focus();
}

// encode from db warning
function encoding_warning() {
  if (page_content_changed == 1) {
    return confirm('Made changes are lost! Continue?');
  }
}