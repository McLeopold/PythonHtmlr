from collections import OrderedDict
from copy import copy
from xml.sax.saxutils import escape, quoteattr
from sys import stdout

# records outermost html or doctype tag
templates = []
def update_templates(item):
    if len(templates) == 0:
        templates.append(item)
    else:
        if item in templates:
            return
        for template in list(templates):
            if template in item:
                templates.remove(template)
            if item in template:
                break
        else:
            templates.append(item)

class htmlr(object):
    '''
    Expected behavior
    passing nodes and attributes in creation
    
    .add will add nodes and attributes to single htmlr
    .add will add nodes and attributes to all htmlr's in an htmlrlist
    .addend (htmlrlist only) will add nodes and attributes to last object only
        used for chaining (__getattr__)
    
    .format will add formatting parameters to single htmlr
    .format will add formatting parameters to all htmlr's in an htmlrlist
    
    .each will use htmlr or htmlrlist as template and copy for each item in list
        can pass nodes and attributes as convenience to all htmlr's in htmlrlist
    .each special case
        if passed an htmlr or htmlrlist, will put that as sub node in each item
        once for each item in the formatlist or else the formatdict

    .__getattr__ (on the fly new tag) will append to the end of a htmlrlist
        or turn a single htmlr into an htmlrlist
    '''
    # default values, can be overridden by subclasses
    _name = None
    _namespace = None
    _nodes = []
    _attributes = OrderedDict()
    _alias = {'class_': 'class'}
    _close = True
    _empty_element = True
    def __init__(self, *nodes, **attributes):
        # TODO: support name spaces
        # TODO: check for valid XML node name
        self._formatlist = []
        self._formatdict = {}
        if not self.__class__._name is None:
            self._name = self.__class__._name
        elif self.__class__.__name__ == 'htmlr' and nodes and \
         isinstance(nodes[0],str):
            self._name = nodes[0]
            nodes = nodes[1:]
        else:
            self._name = self.__class__.__name__
        if self._namespace == None and ':' in self._name:
            self._namespace, self._name = self._name.split(':')
        # overwrite nodes and attributes with those provided on constructor
        # if the user wants to merge, they should later call .add
        self._nodes = []
        if not nodes:
            self._nodes.extend(self.__class__._nodes)
        else:
            self._nodes.extend(nodes)
        self._attributes = OrderedDict()
        if not attributes:
            self._attributes.update(self.__class__._attributes)
        else:
            self._attributes.update(attributes)
        if self._name in ('html', '!DOCTYPE'):
            update_templates(self)

    def __contains__(self, item):
        if self == item:
            return True
        for node in self._nodes:
            if item in node:
                return True

    def __copy__(self):
        newhtmlr = self.__class__(*self._nodes,**self._attributes)
        newhtmlr.format(*self._formatlist,**self._formatdict)
        return newhtmlr
        
    def __getattr__(self, name):
        if name in _chain_classes:
            obj = _chain_classes[name]()
        else:
            obj = htmlr(name)
            # pick up the namespace of the creating class?
            # this might confuse xslt
            if self._namespace:
                obj._namespace = self._namespace
        objs = htmlrlist(self,obj)
        # return add function of new object, but have function return 
        # a reference to the list
        return objs.addend.__get__(objs,objs.__class__)
    
    def add(self, *nodes, **attributes):
        self._nodes.extend(nodes)
        self._attributes.update(attributes)
        return self
        
    def format(self, *formatlist, **formatdict):
        # unpack single dict or list
        if not formatdict:
            if len(formatlist) == 1:
                if isinstance(formatlist[0],(dict,)):
                    formatdict = formatlist[0]
                    formatlist = ()
                elif isinstance(formatlist[0],(list,tuple,set,frozenset)):
                    formatlist = formatlist[0]
        self._formatlist.extend(formatlist)
        self._formatdict.update(formatdict)
        return self

    def each(self, items, *nodes, **attributes):
        elements = htmlrlist()
        if isinstance(items, (dict,)):
            # create a number of elements, use value_ to get number
            for key, value in items.items():
                element = copy(self)
                element.add(*nodes,**attributes)
                element.format(key=key,value=value)
                elements.append(element)
        else:
            try:
                iteritems = iter(items)
                # create a number of elements, use value_ to get number
                for item in iteritems:
                    element = copy(self)
                    element.add(*nodes,**attributes)
                    element.format(item) # unpack dicts and lists?
                    elements.append(element)
            except TypeError:
                # return single htmlr object, not htmlrlist list
                elements = copy(self)
                elements.add(*nodes,**attributes)
                elements.format(items) # unpack?
        return elements

    def __str__(self):
        def toxml(node):
            if isinstance(node,(htmlr,htmlrlist)):
                return str(node)
            elif isinstance(node,(list, tuple, set, frozenset)):
                return ''.join([toxml(n) for n in node])
            else:
                return escape(str(node))
        attrs = ''.join([' {0}'.format(key)
                         if value is None else
                         ' {0}={1}'.format(
                             self.__class__._alias[key] 
                             if key in self.__class__._alias
                             else key, quoteattr(str(value))
                         )
                         for key, value in self._attributes.items()])
        xml = ""
        if self._empty_element and not self._nodes:
            if self._namespace:
                xml = "<{0}:{1}{2}{3}>".format(
                          self._namespace,
                          self._name, 
                          attrs,
                          ' /' if self._close else ''
                      )
            else:
                xml = "<{0}{1}{2}>".format(
                          self._name, 
                          attrs,
                          ' /' if self._close else ''
                      )
        else:
            if self._namespace:
                xml = "<{0}:{1}{2}>{3}".format(
                          self._namespace,
                          self._name,
                          attrs,
                          "".join([toxml(node) for node in self._nodes])
                      )
                if self._close:
                    xml += "</{0}:{1}>".format(
                                self._namespace,
                                self._name)
            else:    
                xml = "<{0}{1}>{2}".format(
                          self._name,
                          attrs,
                          "".join([toxml(node) for node in self._nodes])
                      )
                if self._close:
                    xml += "</{0}>".format(self._name)
        try:
            xml = xml.format(*self._formatlist,**self._formatdict)
        except:
            pass
        return xml
    
    def __format__(self, formatspec):
        # parse format spec
        if not formatspec:
            indent = 0
        else:
            indent = int(formatspec)
        indentstr = "    " * indent
        def toxml(node):
            if isinstance(node,(htmlr,htmlrlist)):
                return format(node,str(indent+1)) + "\n"
            elif isinstance(node,(list,tuple,set,frozenset)):
                return ''.join([toxml(n) for n in node])
            else:
                return "    " + indentstr + escape(str(node)) + "\n"
        attrs = ''.join([' {0}'.format(key)
                         if value is None else
                         ' {0}={1}'.format(self.__class__._alias[key]
                                       if key in self.__class__._alias
                                       else key, quoteattr(str(value)))
                          for key, value in self._attributes.items()])
        if self._empty_element and not self._nodes:
            xml = "{0}<{1}{2}{3}>".format(indentstr, self._name, attrs, ' /' if self._close else '')
        elif len(self._nodes) == 1 and \
           isinstance(self._nodes[0], (str, int, bool, float,
                                        complex, bytes, bytearray)):
            xml = "{0}<{1}{2}>{3}".format(indentstr, self._name, 
                                             attrs, escape(str(self._nodes[0])))
            if self._close:
                xml += "</{0}>".format(self._name)
        else:
            xml = "{0}<{1}{2}>\n{3}{0}".format(
                      indentstr, self._name, attrs,
                      "".join([toxml(node) for node in self._nodes]))
            if self._close:
                xml += "</{0}>".format(self._name)
        try:
            xml = xml.format(*self._formatlist,**self._formatdict)
        except:
            pass
        return xml

class htmlrlist(object):
    def __init__(self, *items):
        self.myitems = list(items)
        for item in items:
            if item._name in ('html', '!DOCTYPE'):
                update_templates(self)
                break
        
    def __contains__(self, item):
        return item in self.myitems

    def __iter__(self):
        return self.myitems
    
    def __copy__(self):
        newhtmlrlist = htmlrlist()
        for item in self.myitems:
            newhtmlr = copy(item)
            newhtmlrlist.append(newhtmlr)
        return newhtmlrlist
    
    def append(self, item):
        self.myitems.append(item)
    
    def __getattr__(self, name):
        if name in _chain_classes:
            obj = _chain_classes[name]()
        else:
            obj = htmlr(name)
        self.myitems.append(obj)
        return self.addend.__get__(self,self.__class__)

    def add(self, *nodes, **attributes):
        for item in self.myitems:
            item.add(*nodes, **attributes)
        return self

    def addend(self, *nodes, **attributes):
        self.myitems[-1].add(*nodes, **attributes)
        return self
        
    def format(self, *formatlist, **formatdict):
        for item in self.myitems:
            item.format(*formatlist,**formatdict)
        return self
            
    def each(self, items, *nodes, **attributes):
        # if passing in a normal iterator
        #     chain what is created to end of existing list using last item as template
        # pass in htmlr or htmlrlist, use as template for creating sub nodes
        #    for each item in this lists items format list
        if isinstance(items,(htmlr,htmlrlist)):
            for item in self.myitems:
                # put template in as node of each item in this htmlrlist
                # clone lists?
                if isinstance(item, htmlr):
                    obj = copy(items)
                    obj.add(*nodes,**attributes)
                    if item._formatlist:
                        obj = obj.each(item._formatlist)
                    elif item._formatdict:
                        obj = obj.each(item._formatdict)
                    item.add(obj) # adds as sub node
                elif isinstance(item, htmlrlist):
                    item.each(items,*nodes,**attributes) # simple recursive
        else:
            elements = htmlrlist()
            if isinstance(items, (dict,)):
                # create a number of elements, use value_ to get number
                for key, value in items.items():
                    for myitem in self.myitems:
                        element = copy(myitem)
                        element.add(*nodes,**attributes)
                        element.format(key=key,value=value)
                        elements.append(element)
                    
            else:
                try:
                    iteritems = iter(items)
                    # create a number of elements, use value_ to get number
                    for item in iteritems:
                        for myitem in self.myitems:
                            element = copy(myitem)
                            element.add(*nodes,**attributes)
                            element.format(item)
                            elements.append(element)
                except TypeError:
                    # call format on htmlrlist
                    elements = self.myitems
                    self.add(*nodes,**attributes)
                    self.format(items)
            self.myitems = elements
        return self
    
    def __str__(self):
        return ''.join([str(item) for item in self.myitems])
            
    def __format__(self, formatspec):
        return '\n'.join([format(item, formatspec) for item in self.myitems])

# keeps list of subclassed htmlr objects for chaining syntax
_chain_classes = {'htmlr': htmlr}
def update_classes():
    _classes = {}
    def itersubclasses(cls):
        for sub in cls.__subclasses__():
            if sub.__name__ not in _classes:
                _classes[sub.__name__] = sub
                itersubclasses(cls)
    itersubclasses(htmlr)
    _chain_classes.update(_classes)

# renders all templates to file
def render(outfile=stdout):
    for template in templates:
        outfile.write(str(template)+'\n')

__all__ = ['htmlr', 'htmlrlist', 'update_classes', 'render']

if __name__ == "__main__":
    from htmlr.page import div
    print(div("{0} {1}").format(["hello","world"]))
    
    # using htmlr
    # simplest example
    print(div())
    # <div />
    
    # add stuff to tag
    # note attributes are first in xml and last in htmlr
    print(div("hello",id=1))
    # <div id="1">hello</div>"
    
    # create class with defaults
    class div(htmlr):
        _nodes = ["hello"]
        _attributes = {"id": 1}
    print(div())
    # <div id="1">hello</div>
    
    # add stuff to defaults
    # notice that nodes are replaced, but attributes are merged
    print(div("world",name="first"))
    # <div id="1" name="first">world</div>
    
    # use add to add nodes and attributes to existing class
    print(div().add("world",name="first"))
    # <div id="1" name="first">helloworld</div>
    
    # reset for examples
    class div(htmlr): pass
    
    # add formatting
    print(div("{0} {1}").format(["hello","world"]))
    # <div>hello world</div>
    print(div("{name}",id="{id}").format({"name": "scott", "id": 1}))
    # <div id="1">scott</div>
    
    # create class with different name
    class mydiv(htmlr):
        _name = "div"
        _attributes = {"class": "mydiv"}
    print(mydiv())
    # <div class="mydiv" />
    
    # using htmlrlist
    # chain a tag after a tag
    print(div().mydiv())
    # <div /><div class="mydiv" />
    
    # chaining looks for existing htmlr class with name, otherwise it creates a tag
    del mydiv
    print(div().mydiv())
    # <div /><mydiv />
    
    # duplicate for each item in a list
    print(div().each(range(3)))
    # <div /><div /><div />
    print(div("hello").each(range(3)))
    # <div>hello</div><div>hello</div><div>hello</div>
    
    # duplicate automatically adds formatting for each item
    print(div(id="{0}").each(range(3)))
    # <div id="0" /><div id="1" /><div id="2" />
    print(div("{name}",id="{id}").each([{"name": "scott", "id": 1},{"name": "mike", "id": 2}]))
    # <div id="1">scott</div><div id="2">mike</div>
    
    # add effects all tags in a list from chaining or duplication
    print(div().div().add(name="hello"))
    # <div name="hello" /><div name="hello" />
    print(div().each(range(2)).add(name="hello"))
    # <div name="hello" /><div name="hello" />
    
    # format effects all tags in a list from chaining or duplication
    print(div("{0}").div("{1}").format(["hello","world"]))
    # <div name="hello" /><div name="hello" />
    # TODO: this may break in python2/3
    print(div("{0}").each(range(2)).format(["hello","world"]))
    # <div name="hello" /><div name="hello" />

