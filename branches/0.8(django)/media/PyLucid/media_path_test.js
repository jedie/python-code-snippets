/*
 * This is a small JavaScript file for a "serve static files" test.
 * hide/unhide some div blocks
 * used in: ./PyLucid/templates_PyLucid/install_generate_hash.html
 */
function hide_by_id(object_id) {
    obj = document.getElementById(object_id);
    obj.style.display = 'none';
}
function unhide_by_id(object_id) {
    obj = document.getElementById(object_id);
    obj.style.display = 'block';
}
