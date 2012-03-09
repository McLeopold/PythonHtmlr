#!/usr/bin/env python2
from collections import OrderedDict
from xml.sax.saxutils import escape, quoteattr
from sys import stdout

INDENT = "    "

# records outermost html or doctype tag
templates = []
def update_templates(item):
    if len(templates) == 0:
        templates.append(item)
    else:
        for template in list(templates):
            if template in item:
                templates.remove(template)
        if item in templates:
            return
        for template in templates:
            if item in template:
                break
        else:
            templates.append(item)


class HtmlrString(str):

    def __init__(self, value=''):
        self._name = None
        self._datalist = []
        self._datadict = []

    def __add__(self, other):
        if isinstance(other, Htmlr):
            if len(other) == 0:
                return self
            elif type(other) is Htmlr:
                if len(other) == 1 and isinstance(other[0], HtmlrString):
                    return self +other[0]
                elif len(other) > 1 and isinstance(other[0], HtmlrString):
                    other[0] = self +other[0]
                    return other
                else:
                    other.insert(0, self)
                    return other
            else:
                return Htmlr()(self, other)
        else:
            return HtmlrString(str(self) + str(other))

    def __radd__(self, other):
        if isinstance(other, Htmlr):
            if (len(other) > 0 and
                    isinstance(other[-1], HtmlrString)):
                other[-1] += self
            else:
                other.append(self)
            return other
        else:
            return HtmlrString(str(other) + str(self))

    def display(self, indent=0, *datalist, **datadict):
        if self == '':
            return ''
        else:
            result = str(self)
            try:
                result = result.format(*datalist, **datadict)
            except Exception as exc:
                pass
            result = ''.join((INDENT * indent,
                              '*str ',
                              result,
                              ' ', str(list(datalist)),
                              ' ', str(datadict),
                              '\n'))
            return result


class HtmlrMeta(type):

    def __getattr__(self, name):
        return self().__getattr__(name)

    # allows div.display() instead of div().display()
    # also allows div(div) instead of div(div())
    def __getattribute__(self, name):
        if name in {'display',
                    'render',
                    'compile',
                    'format'}:
            return self().__getattribute__(name)
        return type.__getattribute__(self, name)


class Htmlr(list):
    __metaclass__ = HtmlrMeta
    _name = None
    _namespace = None
    _nodes = []
    _attributes = OrderedDict()
    _alias = {'class_', 'class'}
    _close = True
    _empty_element = True
    _inited = False

    def __init__(self, *nodes, **attributes):
        # set node name
        if not self.__class__._name is None:
            # name from class default
            self._name = self.__class__._name
        elif self.__class__.__name__ == 'Htmlr':
            if nodes and isinstance(nodes[0], (str, unicode)):
                # name from first node if it is a string
                nodes = list(nodes)
                self._name = nodes.pop(0)
            else:
                # no name, this is just a list of siblings
                self._name = None
        else:
            # name from class name
            self._name = self.__class__.__name__
        if self._name is not None:
            # set node namespace
            if self._namespace is None and ':' in self._name:
                self._namespace, self._name = self._name.split(':', 1)
            # set attributes
            self._attributes = OrderedDict()
            if not attributes:
                self._attributes.update(self.__class__._attributes)
            else:
                self._attributes.update(attributes)
        # set nodes
        if not nodes:
            self.extend(self.__class__._nodes)
        else:
            self.extend(nodes)
        # set data
        self._datalist = []
        self._datadict = {}
        self._inited = True
        update_templates(self)

    def __eq__(self, other):
        return (isinstance(other, Htmlr) and
                    self._name == other._name)

    def __getattr__(self, name):
        # automatic creation of ad-hoc elements
        if name in _chain_classes:
            obj = _chain_classes[name]()
        else:
            obj = Htmlr(name)
            if self._namespace:
                obj._namespace = self._namespace
        obj._inited = False
        if self._name is None:
            self.append(obj)
            return self
        else:
            objs = Htmlr(self, obj)
            return objs

    def __call__(self, *nodes, **attributes):
        if self._inited:
            if self._name is None and len(self) > 0:
                if self[-1]._inited:
                    for item in self:
                        item.extend(nodes)
                        item._attributes.update(attributes)
                else:
                    try:
                        self[-1].__init__(*nodes, **attributes)
                    except TypeError:
                        self[-1] = self[-1](*nodes, **attributes)
            else:
                super(Htmlr, self).extend(nodes)
                self._attributes.update(attributes)
        else:
            self.__init__(*nodes, **attributes)
        return self

    def __iadd__(self, other):
        # append node lists together, merge adjacent strings
        if isinstance(other, HtmlrString):
            if len(self) == 0:
                return other
            elif len(self) == 1 and isinstance(self[0], HtmlrString):
                return self[0] + other
            elif len(self) > 1 and isinstance(self[-1], HtmlrString):
                self[-1] += other
                return self
            else:
                self.append(other)
                return self
        elif isinstance(other, Htmlr):
            if (len(self) > 0 and
                    len(other) > 0 and
                    isinstance(self[-1], HtmlrString) and
                    isinstance(other[0], HtmlrString)):
                self[-1] += other[0]
                self.extend(other[1:])
            else:
                self.extend(other)
            return self

    # extend built-in list functions and return self for cascading
    def append(self, item):
        super(Htmlr, self).append(item)
        return self

    def extend(self, items):
        super(Htmlr, self).extend(items)
        return self

    def insert(self, index, *items):
        for item in reversed(items):
            super(Htmlr, self).insert(index, item)
        return self

    def sort(self):
        super(Htmlr, self).sort()
        return self

    def reverse(self):
        super(Htmlr, self).reverse()
        return self
    # the list functions pop, index and count already return data and can not
    #     be used in a cascading style

    def format(self, *datalist, **datadict):
        self._datalist.extend(datalist)
        self._datadict.update(datadict)
        return self

    def display(self, indent=0, *datalist, **datadict):
        if self._name is None:
            # Htmlr is list of siblings without container
            result = HtmlrString()
            for node in self:
                try:
                    result += node.display(indent, *datalist, **datadict)
                except AttributeError:
                    result += INDENT * indent + '*lit ' + str(node) + '\n'
            return result
            return ''.join(item.display(indent, *datalist, **datadict)
                           for item in self)
        else:
            result = HtmlrString(''.join((INDENT * indent,
                                          self._name, ' ',
                                          str(datadict), ' ',
                                          str(list(datalist)),
                                          '\n')))
            for node in self:
                try:
                    result += node.display(indent + 1, *datalist, **datadict)
                except AttributeError:
                    result += INDENT * (indent + 1) + '*lit ' + str(node) + '\n'
            return result

    def _get_open_tag(self):
        xml = ['<']
        if self._namespace is not None:
            xml.append(self._namespace)
            xml.append(':')
        xml.append(self._name)
        xml.append(''.join([' {0}'.format(key)
                            if value is None else
                            ' {0}={1}'.format(
                                self.__class__._alias[key]
                                if key in self.__class__._alias
                                else key, quoteattr(str(value))
                            )
                            for key, value in self._attributes.items()]))
        if self._close and not self and self._empty_element:
            xml.append(' /')
        xml.append('>')
        return HtmlrString(''.join(xml))

    def _get_close_tag(self):
        if self._close and (self or not self and not self._empty_element):
            xml = ['</']
            if self._namespace is not None:
                xml.append(self._namespace)
                xml.append(':')
            xml.append(self._name)
            xml.append('>')
            return HtmlrString(''.join(xml))
        else:
            return HtmlrString('')

    def _compile_nodes(self):
        nodes = HtmlrString()
        for node in self:
            try:
                nodes += node.compile()
            except AttributeError as exc:
                nodes += str(node)
        return nodes

    def compile(self):
        nodes = self._compile_nodes()
        if self._name is None:
            return nodes
        else:
            return self._get_open_tag() + nodes + self._get_close_tag()

    def _render_nodes(self, *datalist, **datadict):
        nodes = HtmlrString()
        for node in self:
            try:
                nodes += node.render(*datalist, **datadict)
            except AttributeError:
                nodes += str(node)
        return nodes

    def render(self, *datalist, **datadict):
        nodes = self._render_nodes(*datalist, **datadict)
        if self._name is None:
            return nodes
        else:
            return self._get_open_tag() + nodes + self._get_close_tag()


class HtmlrEach(Htmlr):

    def __init__(self, *itemlist, **itemdict):
        if self._inited is None:
            self._inited = True
            self(*itemlist, **itemdict)
        else:
            self._datalist = list(itemlist)
            self._datadict = itemdict
            self._inited = None
            update_templates(self)

    def display(self, indent=0, *datalist, **datadict):
        data = self._datalist or self._datadict or datalist or datadict or None
        result = HtmlrString(''.join((INDENT * indent,
                                      '+each-{0}{1}'.format(self._datalist, self._datadict), ' ',
                                      str(data),
#                                      ' ', str(datadict),
#                                      ' ', str(list(datalist)),
                                      '\n')))
        if data is None:
            result += super(HtmlrEach, self).display(indent + 1)
        else:
            try:
                # assume mapping
                for key, value in data.items():
                    result += super(HtmlrEach, self).display(indent + 1, key=key, value=value)
            except AttributeError as exc:
                try:
                    for item in data:
                        try:
                            result += super(HtmlrEach, self).display(indent + 1, **item)
                        except TypeError:
                            try:
                                if isinstance(item, (str, unicode)):
                                    raise TypeError
                                result += super(HtmlrEach, self).display(indent + 1, *item)
                            except TypeError:
                                result += super(HtmlrEach, self).display(indent + 1, item)
                except TypeError:
                    result += super(HtmlrEach, self).display(indent + 1)
        return result

    def compile(self):
        nodes = HtmlrString()
        if not (self._datalist or self._datadict):
            nodes += self.__class__()(super(HtmlrEach, self).compile())
            return nodes
        else:
            data = self._datalist or self._datadict
            try:
                # assume mapping
                for key, value in data.items():
                    nodes += super(HtmlrEach, self).render(key=key, value=value)
            except AttributeError as exc:
                try:
                    for item in data:
                        try:
                            nodes += super(HtmlrEach, self).render(**item)
                        except TypeError:
                            try:
                                if isinstance(item, (str, unicode)):
                                    raise TypeError
                                nodes += super(HtmlrEach, self).render(*item)
                            except TypeError:
                                nodes += super(HtmlrEach, self).render(item)
                except TypeError:
                    nodes += super(HtmlrEach, self).render()
        return nodes

    def render(self, *datalist, **datadict):
        data = self._datalist or self._datadict or datalist or datadict or None
        data = datalist or datadict or None
        if self._name is None:
            s = []
        else:
            s = ['<' + self._name + '>']
        if data is None:
            s.append(super(HtmlrEach, self).render())
        else:
            try:
                # assume mapping
                for key, value in data.items():
                    s.append(super(HtmlrEach, self).render(key=key, value=value))
            except AttributeError as exc:
                try:
                    for item in data:
                        try:
                            s.append(super(HtmlrEach, self).render(**item))
                        except TypeError:
                            try:
                                if isinstance(item, (str, unicode)):
                                    raise TypeError
                                s.append(super(HtmlrEach, self).render(*item))
                            except TypeError:
                                s.append(super(HtmlrEach, self).render(item))
                except TypeError:
                    s.append(super(HtmlrEach, self).render())
        return HtmlrString(''.join(s))

class each(HtmlrEach): pass


class HtmlrExtract(Htmlr):

    def __init__(self, *extracts, **kwds):
        if self._inited is None:
            self._inited = True
            self(*extracts, **kwds)
        else:
            self._datalist = []
            self._datadict = {}
            self._extracts = extracts if len(extracts) > 0 else None
            self._inited = None
            update_templates(self)

    def extract_data(self, datalist, datadict):
        data = None
        datalist = self._datalist or datalist
        datadict = self._datadict or datadict
        try:
            for extract in self._extracts:
                try:
                    data = datadict[extract]
                except KeyError:
                    data = datalist[extract]
                datalist = datadict = data
        except (KeyError, IndexError, TypeError):
            pass
        return data

    def display(self, indent=0, *datalist, **datadict):
        data = self.extract_data(datalist, datadict)
        result = HtmlrString(''.join((INDENT * indent,
                                      '=extract-{0}'.format(self._extracts), ' ',
                                      str(data),
#                                      ' ', str(datadict),
#                                      ' ', str(list(datalist)),
                                      '\n')))
        if data is None:
            return result + super(HtmlrExtract, self).display(indent + 1)
        else:
            try:
                return result + super(HtmlrExtract, self).display(indent + 1, **data)
            except TypeError:
                try:
                    if isinstance(data, (str, unicode)):
                        raise TypeError
                    return result + super(HtmlrExtract, self).display(indent + 1, *data)
                except TypeError:
                    return result + super(HtmlrExtract, self).display(indent + 1, data)

    def compile(self):
        nodes = HtmlrString()
        nodes += self.__class__(*self._extracts)(super(HtmlrExtract, self).compile())
        return nodes

class extract(HtmlrExtract): pass


# keeps list of subclassed htmlr objects for chaining syntax
_chain_classes = {'Htmlr': Htmlr}
def update_classes():
    _classes = {}
    def itersubclasses(cls):
        for sub in cls.__subclasses__():
            if sub.__name__ not in _classes:
                _classes[sub.__name__] = sub
                itersubclasses(sub)
    itersubclasses(Htmlr)
    _chain_classes.update(_classes)

# renders all templates to file
def render(*datalist, **datadict):
    if 'outfile' in datadict:
        outfile = datadict.pop('outfile')
    else:
        outfile = stdout
    for template in templates:
        outfile.write(template.render(*datalist, **datadict))
        outfile.write('\n')

__all__ = ['HtmlrMeta', 'Htmlr', 'HtmlrString', 'HtmlrExtract', 'HtmlrEach',
           'update_classes', 'render', 'each', 'extract']
