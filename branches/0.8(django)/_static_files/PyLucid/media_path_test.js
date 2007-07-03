/*
 * This is a small JavaScript file for a "serve static files" test.
 */
function hide_by_id(object_id) {
    /*
      This small function is used from:
      ./PyLucid/templates_PyLucid/install_generate_hash.html
    */
    obj = document.getElementById(object_id);
    obj.style.display = 'none';
}
