function toggle(obj_name) {
  obj = document.getElementById(obj_name);
  if (obj.style.display == "block") {
    obj.style.display = "none";
  } else {
    obj.style.display = "block";
  }
}