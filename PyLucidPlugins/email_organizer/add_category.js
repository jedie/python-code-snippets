    function clear(formular) {
        for (var i = 0; i<formular.length; i++) {
            el = formular.elements[i].type;
            if (el!="hidden" && el!="checkbox" && el!="radio" && el!="submit" && el!="reset" && el!="button")
            formular.elements[i].value="";
        }
        return false;
    }