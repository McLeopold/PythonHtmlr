#!/usr/bin/env python2

class Node(list):

    def __init__(self, name=None):
        # if name is None, then this is a list of siblings
        self._name = name
        self._datalist = []
        self._datadict = {}

    def __repr__(self):
        return self.display(0, *self._datalist, **self._datadict)

    # extend built-in list functions and return self for cascading
    def append(self, *items):
        super(Node, self).extend(items)
        return self

    def extend(self, *lists):
        for items in lists:
            super(Node, self).extend(items)
        return self

    def insert(self, index, *items):
        for item in reversed(items):
            super(Node, self).insert(index, item)
        return self

    def sort(self):
        super(Node, self).sort()
        return self

    def reverse(self):
        super(Node, self).reverse()
        return self
    # the list functions pop, index and count already return data and can not
    #     be used in a cascading style

    def each(self, *items):
        return NodeEach(self, *items)

    def extract(self, *extracts):
        return NodeExtract(self, *extracts)

    def format(self, *datalist, **datadict):
        self._datalist.extend(datalist)
        self._datadict.update(datadict)
        return self

    def display(self, indent=0, *datalist, **datadict):
        print('displaying {0}'.format(self._name))
        if self._name is None:
            # Node is list of siblings without container
            return '\n'.join(item.display(indent, *datalist, **datadict)
                             if isinstance(item, Node) else str(item)
                             for item in self)
        else:
            return ' '.join(("    " * indent,
                             self._name, 
                             str(datadict),
                             str(list(datalist)), 
                             ''.join('\n' + node.display(indent + 1, *datalist, **datadict) 
                                     for node in self)))

    def compile_nodes(self):
        s = ['']
        for node in self:
            result = node.compile()
            if isinstance(result, Node) or isinstance(s[-1], Node):
                s.append(result)
            else:
                s[-1] = s[-1] + result
        if isinstance(s[-1], Node):
            s.append('')
        if len(s) == 1:
            return s[0]
        else:
            return self.__class__().extend(s)

    def compile(self):
        nodes = self.compile_nodes()
        if self._name is None:
            return nodes
        else:
            if isinstance(nodes, Node):
                nodes[0] = '<' + self._name + '>' + nodes[0]
                result = self.__class__().extend(nodes)
            else:
                result = '<' + self._name + '>' + nodes
            return result

class NodeProxy(Node):

    def __init__(self, node):
        if isinstance(node, Node):
            self._node = node
            self._name = 'proxy-{0}'.format(node._name)
        else:
            self._node = NodeString(node)
    
    def __repr__(self):
        if isinstance(self._node, Node):
            return self.display(0, *self._node._datalist, **self._node._datadict)
        else:
            return self.display(0, self._node)

    def add(self, *nodes):
        self._node.extend(nodes)
        return self

    def format(self, *datalist, **datadict):
        self._node.format(*datalist, **datadict)
        return self

    def display(self, indent=0, *datalist, **datadict):
        print('displaying {0}'.format(self._name))
        if isinstance(self._node, Node):
            return self._node.display(indent, *datalist, **datadict)

    def __getattr__(self, name):
        if name == '_datalist':
            return self._node._datalist
        elif name == '_datadict':
            return self._node._datadict

def each(*items):
    def wrapper(node):
        return NodeEach(node, *items)
    return wrapper

class NodeString(object):
    def __init__(self, s):
        if isinstance(s, NodeString):
            s = s.s
        self.s = s
        self._name = '*str-'
    def display(self, indent, *datalist, **datadict):
        return "    " * indent + self.s
    def __repr__(self):
        return self.display(0)
    def __getattr__(self, name):
        if name == '_datalist':
            return []
        elif name == '_datadict':
            return {}
        else:
            return None

class NodeEach(NodeProxy):

    def __init__(self, node, *items):
        super(NodeEach, self).__init__(node)
        self._items = items if len(items) > 0 else None
        self._name = '+each-{0}'.format(items)

    def display(self, indent=0, *datalist, **datadict):
        print('displaying {0}'.format(self._name))
        if self._items is None:
            if isinstance(self._node, Node):
                data = self._node._datalist or self._node._datadict
            else:
                self._node = NodeString(self._node)
                data = None
            data = data or datalist or datadict or None
        else:
            data = self._items
        s = ' '.join(("    " * indent,
                      self._name, 
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
                s += '\n' + self._node.display(indent + 1)
        if isinstance(self._node, NodeString):
            self._node = self._node.s
        return s
                                     
    def compile(self):
        result = self.__class__(self._node.compile())
        return result


def extract(*extracts):
    def wrapper(node):
        return NodeExtract(node, *extracts)
    return wrapper

class NodeExtract(NodeProxy):

    def __init__(self, node, *extracts):
        super(NodeExtract, self).__init__(node)
        self._extracts = extracts if len(extracts) > 0 else None
        self._name = '=extract-{0}'.format(extracts)

    def extract_data(self, datalist, datadict):
        data = None
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
        print('displaying {0}'.format(self._name))
        data = self.extract_data(datalist, datadict) or datalist or datadict
        s = ' '.join(("    " * indent,
                      self._name,
                      str(data),
                      str(datadict),
                      str(list(datalist)),
                      '\n'))
        try:
            return s + self._node.display(indent + 1, **data)
        except TypeError:
            try:
                if isinstance(data, (str, unicode)):
                    raise TypeError
                return s + self._node.display(indent + 1, *data)
            except TypeError:
                return s + self._node.display(indent + 1, data)
        
    def compile(self):
        result = self.__class__(self._node.compile())
        return result


table = Node('table').append(Node('thead').append(Node('tr').append(each()(Node('th')))))

if __name__ == '__main__':
    n = Node('table').append(Node('thead').append(Node('tr').append(each()(Node('th')))))
    c = n.compile()
    print(c)

    quit()

    n = Node('div').extract(0).each().extract('key')
    print(n)
    print
    c = n.compile()
    print(c)
    print

    n = Node('div').append(Node().append(Node('section'), Node('article')).each())
    print(n)
    print
    c = n.compile()
    print(c)
    print
    print([i for i in c])
    print

    n = Node('div')
    print(n.display(0, 1, 2))
    print

    n = extract(0)(Node('div'))
    print(n.display(0, 1, 2))
    print

    n = Node('div').extract(0)
    print(n.display(0, 1, 2))
    print

    n = each()(Node('div'))
    print(n.display(0, 1, 2))
    print

    n = Node('div').each()
    print(n.display(0, 1, 2))
    print

    n = each()(Node('div').append(
        each()
        (Node('div'))
    ))
    print(n.display(0, [1,2], [3,4]))
    print

    n = each()(Node('div').append(
        each('a', 'b')
        (Node('div')).format('a', 'b')
    ))
    print(n.display(0, [1,2], [3,4]))
    print

    n = each()(Node('div').append(
        each()
        (Node('div')).format('a', 'b')
    ))
    print(n.display(0, [1,2], [3,4]))
    print

    table1 = [{'id': 1, 'name': 'scott'},
              {'id': 2, 'name': 'mike'}]

    table2 = {'fields': ['id', 'name'],
              'values': [[1, 'scott'],
                         [2, 'mike']]}

    a = Node('table')
    b = Node('thead')
    c = Node('tr')
    d = Node('th').extract('key').each().extract(0)
    e = Node('tbody')
    f = Node('tr').each()
    g = Node('td').each()
    h = Node('tfoot')

    a.append(b, e, h)
    b.append(c)
    c.append(d)
    e.append(f)
    f.append(g)

    c = a.compile()
    print(c)
    print(a.display(0, *table1))
    print

    a = Node('table')
    b = Node('thead')
    c = Node('tr')
    d = Node('th').each().extract('fields')
    e = Node('tbody')
    f = Node('tr').each().extract('values')
    g = Node('td').each()
    h = Node('tfoot')

    a.append(b, e, h)
    b.append(c)
    c.append(d)
    e.append(f)
    f.append(g)

    print(a.display(0, **table2))
