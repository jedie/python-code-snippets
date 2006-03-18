#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    Modul:          PyXO (Python XML Objects)
    Description:    Baseclass for objects, to store and load from/to xml
    Version:        1.4.4
    Copyright:      2004 by Fritz Cizmarov alias Dookie († 22.02.2005)
    Created:        16. Jul. 2004
    Last modified:  15. Jän. 2005 (by Fritz Cizmarov)
    License:        Python license
    Requirements:   Python2.3
    Exports:        Type, Object, Container, Root, CData
                    escape, unicoded, xml_prolog, indstr

    modified by Jens Diemer, 2006

    trac:
    http://pylucid.python-hosting.com/file/CodeSnippets/PyXO/trunk/PyXO.py

    Revision Log:
    http://pylucid.python-hosting.com/log/CodeSnippets/PyXO/trunk/PyXO.py

    readme:
    http://pylucid.python-hosting.com/file/CodeSnippets/PyXO/trunk/PyXO_readme_v144.html?format=raw

    Python-Forum thread:
    http://www.python-forum.de/viewtopic.php?t=1833
"""

import os
import re
import sys
import codecs
import inspect

from warnings import warn
from cStringIO import StringIO
from xml.parsers.expat import ParserCreate

sysencoding = sys.getfilesystemencoding()
xml_prolog = codecs.BOM_UTF8 + '<?xml version="1.0" encoding="utf-8"?>\n'
indstr = "  " # string for indentation

def gen_id(name, fmt="%s_%03d", _dict={}):
    id = _dict.get(name,0)+1
    _dict[name] = id
    return fmt % (name, id)


def escape(data, quote=False):
    """ encode special chars &, <, >, ", ' """
    data = data.replace("&", "&amp;")
    data = data.replace("<", "&lt;")
    data = data.replace(">", "&gt;")
    if quote:
        data = data.replace("'", "&#39;")
        data = data.replace('"', "&quot;")
    return data.encode("utf-8", "xmlcharrefreplace")


def unicoded(data, encoding=sysencoding):
    """ return data as unicode """
    if not isinstance(data, unicode):
        return str(data).decode(encoding)
    else:
        return data


class Type(type):
    """ Metaclass of Object """

    #--- Properties ---

    __xml_classes = {}
    def xml_classes(self):
        return self.__xml_classes
    xml_classes = property(xml_classes, doc="Registered classes")

    def xml_attributes(self):
        if not hasattr(self, "__xml_attributes"):
            attrs = {}
            for base in self.__bases__:
                if hasattr(base, "xml_attributes"):
                    attrs.update(base.xml_attributes)
                if (hasattr(base, "__slots__") and
                    isinstance(base.__slots__, dict)):
                    attrs.update(base.__slots__)
            if hasattr(self, "xml_attrs"):
                attrs.update(self.xml_attrs)
            if hasattr(self, "__slots__") and isinstance(self.__slots__, dict):
                attrs.update(self.__slots__)
            for key in attrs.keys():
                if attrs[key] is None:
                    del attrs[key]
            self.__xml_attributes = attrs
        return self.__xml_attributes
    xml_attributes = property(xml_attributes, doc="Attributes for XML")

    #--- Specialmethods ---

    def __init__(self, name, bases, cdict):
        tag_name = cdict.get("xml_tag_name", name)
        setattr(self,"xml_tag_name", tag_name)
        if (tag_name in self.__xml_classes and
            self.__xml_classes[tag_name] is not self):
            raise TypeError("%s already exists!" % name)
        super(Type, self).__init__(name, bases, cdict)
        self.__xml_classes[tag_name] = (self, self.xml_attributes, None)
        if not hasattr(self, "xml_stack"):
            self.xml_stack = []
        if not hasattr(self, "obj_ids"):
            self.obj_ids = {}

    #--- Custommethods

    def obj_to_xml(self, obj, indent=0, attrs="", indstr=indstr, stream=None):
        """ write xmlrepresentation of an object to stream """
        ind = indstr*indent
        if stream is None:
            stream = StringIO()
            do_close = True
        else:
            do_close = False
        if hasattr(obj, "id"):
            if obj.id in self.obj_ids and not hasattr(obj, "no_PyXO_Ref"):
                stream.write('%s<PyXO_Ref id="%s"/>\n' % (ind, obj.id))
                return
            else:
                if obj.id in self.obj_ids:
                    raise NameError("ID '%s' used twice!" % obj.id)
                self.obj_ids[obj.id] = obj
        if hasattr(obj,"to_xml"):
            try:
                obj.to_xml(indent, indstr=indstr, stream=stream)
            except TypeError:
                try:
                    stream.write(obj.to_xml(indent, indstr))
                except TypeError:
                    stream.write(obj.to_xml(indent))
        else:
            name = obj.__class__.__name__
            if name in self.xml_classes: # is registered?
                if isinstance(self.xml_classes[name][2], basestring):
                    to_xml = getattr(obj,self.xml_classes[name][2])
                    stream.write(to_xml(indent))
                else:
                    stream.write(self.xml_classes[name][2](obj, indent))
            elif name == "bool":
                stream.write("%s<bool>%s</bool>\n" % (ind, str(obj).title()))
            elif name in ("str", "unicode"):
                stream.write("%s<%s>%s</%s>\n" % (ind, name,
                                                  escape(obj), name))
            elif name in ("tuple", "list", "xrange"):
                stream.write("%s<%s>\n" % (ind, name))
                if name == "xrange":
                    obj = [int(x) for x in re.findall(r'-?\d+', str(obj))]
                for item in obj:
                    self.obj_to_xml(item, indent+1, stream=stream)
                stream.write("%s</%s>\n" % (ind, name))
            elif name == "dict":
                stream.write(u"%s<%s>\n" % (ind, name))
                for key, value in obj.iteritems():
                    self.obj_to_xml(key, indent+1, stream=stream)
                    self.obj_to_xml(value, indent+2, stream=stream)
                stream.write(u"%s</%s>\n" % (ind, name))
            else:
                module = obj.__class__.__module__
                if module == "__main__":
                    module = os.path.basename(sys.argv[0])[:-3]
                while True: # loop
                    if module != "__builtin__":
                        if self.xml_write_python_module:
                            attrs += u' python_module="%s"' % module
                        try:
                            iterator = iter(obj)
                        except TypeError:
                            pass
                        else:
                            stream.write(u"%s<%s%s>\n" % (ind, name, attrs))
                            for i in iterator:
                                self.obj_to_xml(i, indent+1,
                                               stream=stream)
                            stream.write(u"%s</%s>\n" % (ind, name))
                            break # exit loop
                    value = str(obj)
                    if value.startswith(u"<") and value.endswith(u">"):
                        raise TypeError("Can't convert %s to xml!" % name)
                    value = escape(value)
                    stream.write(u"%s<%s%s>%s</%s>\n" % (ind, name, attrs,
                                                         value, name))
                    break # exit loop
        if do_close:
            result = stream.getvalue()
            stream.close()
            return result

    def register_other(self, name, constructor, attributes={},
                       to_xml=None):
        """
            Register Classes not derivated from Object.
            Instances have to be createt by the call constructor(children, **kw)
            where kw hold the attributes to initalise the Instances.
            There have to be a method "to_xml(indent)" in the class
            that returns the xml-representation of the instance.
            The attributes-parameter is a mapping of the names of the attributes
            and the attributetypes as values.
            Attributes given from the xml are convertet by using this
        """
        if name in self.xml_classes:
            raise KeyError("%s already registered!" % name)
        self.xml_classes[name] = (constructor, attributes, to_xml)

    def from_data(self, name, children, attrs):
        """ Create object of type name with children and attributes """
        module = attrs.pop("python_module","")
        attrs = dict([(str(key), value) for key, value in attrs.iteritems()])
        if name == "PyXO_Ref":
            return self.obj_ids[attrs["id"]]
        if isinstance(__builtins__, dict):  # __builtins__ may be
            builtins = __builtins__             # dictionary
        else:                               # or
            builtins = __builtins__.__dict__    # modul
        if name in self.xml_classes:
            constructor, attrtypes = self.xml_classes[name][:2]
            kw = {}
            for key, value in attrs.iteritems():
                if not attrtypes.has_key(key):
                    warn("Attribute %s not defined for %s" % (key, name))
                    kw[key] = str(value)
                else:
                    if isinstance(attrtypes[key], (tuple, list)):
                        at = attrtypes[key]
                        if len(attrtypes[key]) == 1:
                            value = type(at)([at[0](x) for x in value.split()])
                        else:
                            value = type(at)([at[x](y) for x, y in
                                              zip(attrtypes[key],
                                                  value.split())])
                    elif attrtypes[key] is bool:
                        value = value.lower() in ["1", "true", "on"]
                    kw[key] = attrtypes[key](value)
            if children:
                try:
                    instance = constructor(children, **kw)
                except TypeError:
                    if len(children) == 1:
                        instance = constructor(children[0], **kw)
                    else:
                        instance = constructor(**kw)
            else:
                instance = constructor(**kw)
        elif name in builtins:
            if name == "bool":
                value = children[0].strip().lower()
                if not value in ("true", "false", "1", "0", "on", "off"):
                    raise TypeError("unknown value for bool %s" % value)
                instance = value in ("true", "1", "on")
            elif name == "dict":
                instance = dict([(children[i], children[i+1])
                                 for i in xrange(0, len(children), 2)])
            elif name == "list":
                instance = list(children)
            elif name == "tuple":
                instance = tuple(children)
            elif repr(builtins[name]).startswith("<type "):
                if len(children) == 1:
                    children = children[0]
                try:
                    instance = builtins[name](children)
                except ValueError:
                    if children:
                        instance = builtins[name](children[1:-1])
                    else:
                        raise
                except TypeError:
                    if children:
                        instance = builtins[name](*children)
                    else:
                        raise
            else:
                raise TypeError("'%s' is not a type!" % name)
        else:
            if module and not module in sys.modules:
                try:
                    __import__(module, globals(), locals(), [])
                    attrs["python_module"] = module;
                    instance = self.from_data(name, children, attrs)
                except ImportError:
                    instance = self.xml_import_error_handler(module, name,
                                                            children, attrs)
                    if instance is None:
                        raise # reraise ImportError
            elif module:
                constructor = getattr(sys.modules[module], name)
                try:
                    instance = constructor(children, **attrs)
                except TypeError:
                    instance = constructor(*children, **attrs)
            else:
                raise TypeError("Unknown Object '%s'!" % name)
        if hasattr(instance, "id"):
            self.obj_ids[instance.id] = instance
        return instance

    #--- Handlermethods for xml.xml_parser ---#

    def xml_start_element(self, name, attrs):
        for key in attrs.keys():
            attrs[key] = attrs[key].replace("&lt;", "<"
                                  ).replace("&gt;", ">"
                                  ).replace("&amp;", "&"
                                  ).replace("&apos;", "'"
                                  ).replace("&quot;", '"')
        self.xml_stack.append((name, [], attrs))

    def xml_end_element(self, name):
        sname, children, attrs = self.xml_stack.pop()
        if sname != name:
            raise NameError("%s not equal to %s!" % (sname, name))
        instance = self.from_data(name, children, attrs)
        if self.xml_stack:
            self.xml_stack[-1][1].append(instance)
        else:
            self.xml_stack = [instance]

    def xml_char_data(self, data):
        if hasattr(self,"_CData"):
            self._CData += data
        else:
            data = self.xml_c_data_handler(data)
            if data.strip():
                if (self.xml_stack[-1][1] and
                    isinstance(self.xml_stack[-1][1][-1], basestring)):
                    self.xml_stack[-1][1][-1] += data
                else:
                    self.xml_stack[-1][1].append(data)

    def xml_start_cdata(self):
        self._CData = ""

    def xml_end_cdata(self):
        self.xml_stack[-1][1].append(CData(self._CData))
        del(self._CData)

    #--- Generator to load objects from xml ---

    def from_xml(self, xml):
        """ Create object from xml """
        assert self.xml_stack == [], "don't call from_xml recursive!"
        self.obj_ids = {}
        is_file = hasattr(xml, "read") # changed on suggestion from
        do_close = False               # Walter Dörwald
        if not is_file:
            try:
                xml = file(xml, 'r')
                is_file = True
                do_close = True
            except IOError:
                pass
        self.xml_parser = ParserCreate()
        self.xml_parser.StartElementHandler = self.xml_start_element
        self.xml_parser.EndElementHandler = self.xml_end_element
        self.xml_parser.CharacterDataHandler = self.xml_char_data
        self.xml_parser.StartCdataSectionHandler = self.xml_start_cdata
        self.xml_parser.EndCdataSectionHandler = self.xml_end_cdata
        self.xml_parser.buffer_text = True
        self.xml_parser.returns_unicode = True
        if is_file:
            self.xml_parser.ParseFile(xml)
        else:
            self.xml_parser.Parse(xml, True)
        self.xml_parser = None
        if do_close:
            xml.close()
        return self.xml_stack.pop()


    # Methods to easy save and load objects to/from XLM

    def save(self, xml, obj):
        """ Function to save Objects to an XML-file """
        do_close = False
        if isinstance(xml, basestring):
            xml = file(xml, 'w')
            do_close = True
        self.obj_ids.clear()
        if isinstance(obj, Root):
            obj.to_xml(stream=xml)
        else:
            fname = getattr(xml,"name", "anonymus")
            name = os.path.basename(fname)
            Root([obj], name=name, del_root = True).to_xml(stream=xml)
        if do_close:
            xml.close()
        self.obj_ids.clear()

    def load(self, xml):
        """ Function to restore Objects from an XML-File """
        self.obj_ids.clear()
        result = self.from_xml(xml)

        if isinstance(result, Root) and result.del_root:
            result = result.children[0]
        self.obj_ids.clear()
        return result


class Object(object):
    """
        Baseclass for objects to be stored/loaded to/from xml
        xml_attrs is a Dictionary with the names of all Attributes and as
        values the type of any Attribut
        If the value of an item in xml_attrs is None, it will not be stored
        into xml
    """
    __metaclass__ = Type
    xml_attrs = {"id" : str}

    xml_write_python_module = True

    def __init__(self, *args, **kw):
        super(Object, self).__init__(*args, **kw)
        self.id = kw.pop("id", gen_id(self.__class__.__name__))

    def xml_c_data_handler(data):
        """ return processed cdata from xml """
        return re.sub(u" +", u" ", data.replace(u"\t", u" "
                                      ).replace(u"\n", u" "),
                      re.UNICODE)
    xml_c_data_handler = staticmethod(xml_c_data_handler)

    def xml_import_error_handler(module, name, children, attrs):
        """
            Handle not installed module.
            Return instance of class "name" of module "module" or None.
        """
        return None
    xml_import_error_handler = staticmethod(xml_import_error_handler)

    def attrs_to_xml(self):
        """ Return string with key/value-pairs seperated by a "=" """
        attributes = self.__class__.xml_attributes.keys()
        attributes.sort()
        res = u""
        for attr in attributes:
            value = getattr(self, attr, None)
            if value is not None:
                if isinstance(value, (list, tuple)):
                    value = u" ".join([unicoded(x).replace(" ", "&#160;")
                                      for x in value])
                elif isinstance(value, bool):
                    value = str(value).lower()
                else:
                    value = escape(str(value), quote=True)
                res += u' %s="%s"' % (attr, value)
        return res # no strip() leading space is expected!

    def to_xml(self, indent=None, indstr=indstr, stream=None):
        """
            Write object as xml-tag with indentation 'indent' to stream
            if stream is not given, return xml-tag as String
        """
        if stream is None:
            stream = StringIO()
            do_close = True
        else:
            do_close = False
        if indent is None:
            stream.write(xml_prolog)
            ind = 0
        else:
            ind = indent
        myindent = indstr*ind
        tag_name = getattr(self.__class__, "xml_tag_name",
                           self.__class__.__name__)
        stream.write(u"%s<%s%s" % (myindent, tag_name, self.attrs_to_xml()))
        if self.xml_write_python_module:
            module = self.__class__.__module__
            if module == "__main__":
                module = os.path.basename(sys.argv[0])[:-3]
            stream.write(u' python_module="%s"' % module)
        try:
            if hasattr(self, "xml_get_children"):
                iterator = iter(self.xml_get_children())
            else:
                iterator = iter(self)
        except TypeError:
            stream.write(u"/>\n")
            return
        stream.write(">\n")
        for child in iterator:
            Object.obj_to_xml(child, ind + 1, stream=stream)
        stream.write(u"%s</%s>\n" % (myindent, tag_name))
        if do_close:
            result = stream.getvalue()
            stream.close()
            return result


class Container(Object):
    """ Baseclass for collections of Objects and other objects """
    xml_attrs = {"name" : str}

    def children(self):
        return self.__children
    children = property(children, doc="list of childobjects of container")

    def __init__(self, *args, **kw):
        super(Container, self).__init__(*args, **kw)
        if args:
            self.__children = args[0]
        else:
            self.__children = []
        self.name = kw.pop("name", "anonymus")

    def __iter__(self):
        """ return iterator over self.children """
        return iter(self.__children)

    def __len__(self):
        return len(self.__children)

    def append(self, child):
        self.__children.append(child)

    def remove(self, child):
        self.__children.remove(child)

    xml_get_children = __iter__


class Root(Container):
    """ Use Root or an subclass to cover your objects """
    xml_attrs = {"del_root" : bool}

    xml_tag_name = "PyXO"

    def __init__(self, *args, **kw):
        super(Root, self).__init__(*args, **kw)
        self.del_root = kw.pop("del_root", False)

    def save(self, xml):
        Object.save(xml, self)


class CData(Object):
    """ Class for XML-CDATA-Section """

    def __init__(self, cdata, **kw):
        self.__cdata = cdata

    def to_xml(self, indent, indstr=indstr, stream=None):
        value = self.__cdata.encode("utf-8","xmlcharrefreplace")
        if stream is not None:
            stream.write("%s<![CDATA[%s]]>\n" % (indstr*indent, value))
        else:
            return "%s<![CDATA[%s]]>\n" % (indstr*indent, value)

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.__cdata)

    def __str__(self):
        return self.__cdata

"""
class PyXO_Ref(object):

    __slots__ = ["id"]
    xml_attrs = {"id", str}

    def __init__(self, id=None):
        self.id = id
"""

#----------------------------------------------------------------------------
# Testing Objects
#----------------------------------------------------------------------------
if __name__ == "__main__": # Test
    import os.path
    xmlname = "PyXO_demo.xml"
    if not os.path.exists(xmlname):
        # create simple xml-data
        xml= codecs.BOM_UTF8 + """<?xml version="1.0" encoding="utf-8"?>
<PyXO del_root="true">
    <list>
        Hallo Welt! €
        <![CDATA[<test>123
        äüö</test>]]>
        <int>1960</int>
        1.0 2.0 3.0 4.0
        5.0 6.0 7.0 8.0
        <Set python_module="sets"> <!-- Object from extern Modul -->
            <str>a</str>
            <str>b</str>
            <str>c</str>
        </Set>
        <bool>true</bool>
        <dict>
            <str>a</str><int>1</int>
            <str>b</str><int>2</int>
            <str>c</str><int>3</int>
        </dict>
    </list>
</PyXO>"""
        #write xml-data to file
        f = file(xmlname, 'w')
        f.write(xml)
        f.close()
        print "XML-data written to %s" % xmlname
        print "Pleas run script once more to test loading XML-Data!"
    else:
        # demo of loading objects from xml-file, also sets.Set is loaded!
        my_objects = Object.load(xmlname)
        print "my_objects load from %s" % xmlname
        print my_objects # print Objects
        print my_objects[0]
        Object.save(sys.stdout, my_objects) # test saving to xml

