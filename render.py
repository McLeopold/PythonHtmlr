#!/usr/bin/env python2

def extract_data(extracts, datalist, datadict):
    data = None
    try:
        for extract in extracts:
            try:
                data = datadict[extract]
            except KeyError:
                data = datalist[extract]
            datalist = datadict = data
    except (KeyError, IndexError, TypeError):
        pass
    return data

def unpack(self, func, *datalist, **datadict):
    if not datadict and len(datalist) == 1:
        if not isinstance(datalist[0], (str, unicode)):
            try:
                datadict = dict(datalist[0])
            except TypeError:
                try:
                    datalist = list(datalist[0])
                except TypeError:
                    pass
    return datalist, datadict

class Node(object):

    def __init__(self, name=None):
        # if name is None, then this is a list of siblings
        self._name = name
        self._nodes = []
        self._datalist = []
        self._datadict = {}

    def __repr__(self):
        return self.display(0, *self._datalist, **self._datadict)

    def add(self, *nodes):
        self._nodes.extend(nodes)
        return self

    def format(self, *datalist, **datadict):
        self._datalist.extend(datalist)
        self._datadict.update(datadict)
        return self

    def display(self, indent=0, *datalist, **datadict):
        if self._name is None:
            # Node is list of siblings without container
            return '\n'.join(item.display(indent, *datalist, **datadict)
                             if isinstance(item, Node) else str(item)
                             for item in self._nodes)
        else:
            return ' '.join(("    " * indent,
                             self._name, 
                             str(datadict),
                             str(list(datalist)), 
                             ''.join('\n' + node.display(indent + 1, *datalist, **datadict) 
                                     for node in self._nodes)))


class NodeProxy(Node):

    def __init__(self, node):
        self._node = node
    
    def __repr__(self):
        return self.display(0, *self._node._datalist, **self._node._datadict)

    def add(self, *nodes):
        self._node.add(*nodes)
        return self

    def format(self, *datalist, **datadict):
        self._node.format(*datalist, **datadict)
        return self

    def display(self, indent=0, *datalist, **datadict):
        return self._node.display(indent, *datalist, **datadict)


def each(*extracts):
    def wrapper(node):
        return NodeEach(node, *extracts)
    return wrapper

class NodeEach(NodeProxy):

    def __init__(self, node, *extracts):
        self._extracts = extracts if len(extracts) > 0 else None
        super(NodeEach, self).__init__(node)

    def display(self, indent=0, *datalist, **datadict):
        data = extract_data(self._extracts, datalist, datadict) or datalist or datadict
        s = ' '.join(("    " * indent,
                      '+', 
                      str(data), 
                      str(datadict),
                      str(list(datalist))))
        try:
            for key, value in data.items():
                s += '\n' + self._node.display(indent, key=key, value=value)
        except AttributeError:
            try:
                for item in data:
                    try:
                        s += '\n' + self._node.display(indent, **item)
                    except TypeError:
                        try:
                            if isinstance(item, (str, unicode)):
                                raise TypeError
                            s += '\n' + self._node.display(indent, *item)
                        except TypeError:
                            s += '\n' + self._node.display(indent, item)
            except TypeError:
                s += '\n' + self._node.display(indent)
        return s
                                     

def extract(*extracts):
    def wrapper(node):
        return NodeExtract(node, *extracts)
    return wrapper

class NodeExtract(NodeProxy):

    def __init__(self, node, *extracts):
        self._extracts = extracts if len(extracts) > 0 else None
        super(NodeExtract, self).__init__(node)

    def display(self, indent=0, *datalist, **datadict):
        data = extract_data(self._extracts, datalist, datadict) or datalist or datadict
        s = ' '.join(("    " * indent,
                      '=',
                      str(data),
                      str(datadict),
                      str(list(datalist)),
                      '\n'))
        try:
            return s + super(NodeExtract, self).display(indent, **data)
        except TypeError:
            try:
                return s + super(NodeExtract, self).display(indent, *data)
            except TypeError:
                return s + super(NodeExtract, self).display(indent, data)
        

if __name__ == '__main__':
    n = Node('div')
    print(n.format(1,2))

    n = each()(Node('div'))
    print(n.format(1,2))

    n = extract(0)(Node('div'))
    print(n.format(1,2))

#    table1 = [{'id': 1, 'name': 'scott'},
#              {'id': 2, 'name': 'mike'}]
#
#    table2 = {'fields': ['id', 'name'],
#              'values': [[1, 'scott'],
#                         [2, 'mike']]}
#
#    a = Node(None).add(Node('div'), Node('div'))
#    a.format(1)
#    print(a)
#
#    a = Node('table')
#    b = Node('thead')
#    c = Node('tr')
#    d = NodeEach(NodeExtract('th', 'key'), 0)
#    e = Node('tbody')
#    f = NodeEach('tr')
#    g = NodeEach('td')
#    h = Node('tfoot')
#
#    a.add(b, e, h)
#    b.add(c)
#    c.add(d)
#    e.add(f)
#    f.add(g)
#
#    a.format(*table1)
#    print(a)
#
#    a = Node('table')
#    b = Node('thead')
#    c = Node('tr')
#    d = NodeEach('th', 'fields')
#    e = Node('tbody')
#    f = NodeEach('tr', 'values')
#    g = NodeEach('td')
#    h = Node('tfoot')
#
#    a.add(b, e, h)
#    b.add(c)
#    c.add(d)
#    e.add(f)
#    f.add(g)
#
#    a.format(**table2)
#    print(a)
