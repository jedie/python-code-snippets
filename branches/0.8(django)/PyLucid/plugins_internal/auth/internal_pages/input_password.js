if (!document.getElementById) {
  alert("Error: Your Browser is not supported!");
}

if (navigator.cookieEnabled) {
  if (navigator.cookieEnabled != true) {
    alert("You must enable Cookies in your Browser!");
  }
}

check_ok = false;
debug_msg = false;
HASH_LEN = 40;

/* ___________________________________________________________________________
 *  debugging
 */

function init_debug() {
    if (debug_msg != true) { return; }
    property = "dependent=yes,resizable=yes,width=350,height=400,top=1,left=" + window.outerWidth;
    debug_window = window.open("about:blank", "Debug", property);
    debug_window.focus();
    debug_win = debug_window.document;
    debug_win.writeln("<style>* { font-size: 0.85em; }</style>");
    debug_win.writeln("<h1>JS Debug:</h1>");
    debug_win.writeln("---[DEBUG START]---");
    debug_win.writeln("cookie:" + document.cookie +"<br />");

    document.body.onunload = "debug_window.close();";
}
function debug(msg) {
   if (debug_msg != true) { return; }
   debug_win.writeln(msg + "<br />");
}
function debug_confirm() {
   if (debug_msg != true) { return; }
   debug_window.focus();
   debug_win.writeln("---[DEBUG END]---");
   alert('OK for submit.');
   debug_window.close();
}

/* ___________________________________________________________________________
 *  password input
 */

function set_focus(object_id) {
   debug("set focus on id:" + object_id);
   document.getElementById(object_id).focus();
}

function init() {
    init_debug()

    debug("salt value from server:" + salt);
    if (salt.length<5) {
        alert("salt from Server fail!"); return false;
    }

    debug("challenge value from server:" + challenge);
    if (challenge.length<5) {
        alert("challenge from Server fail!"); return false;
    }

    set_focus(focus_id);

    check_ok = true;
}

function change_color(id_name, color_name) {
    obj = document.getElementById(id_name);
    obj.style.backgroundColor = color_name;
}

function check() {
    if (check_ok != true) {
       alert("Internal error.");
       return False;
    }

    in_pass = document.getElementById("plaintext_pass").value;
    debug("in_pass:" + in_pass);
    if (in_pass.length<8) {
        alert("Password min len 8! - current len:" + in_pass.length);
        return false;
    }

    for (var i = 1; i <= in_pass.length; i++) {
       unicode_charcode = in_pass.charCodeAt(i);
       if (unicode_charcode > 127) {
           alert("Only ASCII letters are allowed!");
           return false;
       }
    }

    shapass = hex_sha1(salt + in_pass);
    debug("shapass - hex_sha(salt + in_pass):" + shapass);
    if (shapass.length!=HASH_LEN) {
        alert("hex_sha salt error! shapass length:" + shapass.length);
        return false;
    }

    // Passwort aufteilen
    sha_a = shapass.substr(0, HASH_LEN/2);
    sha_b = shapass.substr(HASH_LEN/2, HASH_LEN/2);
    debug("substr: sha_a:|"+sha_a+"| sha_b:|"+sha_b+"|");

    sha_a2 = hex_sha1(challenge + sha_a)
    debug("sha_a2 - hex_sha(challenge + sha_a): " + sha_a2);

    // hex_sha setzten
    document.getElementById("sha_a2").value = sha_a2;
    change_color("sha_a2", "lightgreen");
    document.getElementById("sha_b").value = sha_b;
    change_color("sha_b", "lightgreen");

    document.getElementById("plaintext_pass").value = "";
    change_color("plaintext_pass", "grey");

    document.login.action = submit_url;

    check_ok = true;
    debug_confirm();

    return true;
}


