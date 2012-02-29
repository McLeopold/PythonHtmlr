#!/usr/bin/env python2

INDENT = "    "

class NodeString(str):

    def __init__(self, value=''):
        self._name = '*str-'
        self._datalist = []
        self._datadict = []

    def __add__(self, other):
        if isinstance(other, Node):
            if (len(other) > 0 and
                    isinstance(other[0], NodeString)):
                other[0] = self +other[0]
            else:
                other.insert(0, self)
            return other
        else:
            return NodeString(str(self) + str(other))

    def __radd__(self, other):
        if isinstance(other, Node):
            if (len(other) > 0 and
                    isinstance(other[-1], NodeString)):
                other[-1] += self
            else:
                other.append(self)
            return other
        else:
            return NodeString(str(other) + str(self))

    def display(self, indent, *datalist, **datadict):
        if self == '':
            return ''
        else:
            return INDENT * indent + str(self) + '\n'


class Node(list):

    def __init__(self, name=None):
        # if name is None, then this is a list of siblings
        self._name = name
        self._datalist = []
        self._datadict = {}

    def __iadd__(self, other):
        if (len(self) > 0 and
                len(other) > 0 and
                isinstance(self[-1], NodeString) and
                isinstance(other[0], NodeString)):
            self[-1] += other[0]
            self.extend(other[1:])
        else:
            self.extend(other)
        return self

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
        if self._name is None:
            # Node is list of siblings without container
            return ''.join(item.display(indent, *datalist, **datadict)
                           for item in self)
        else:
            return ''.join((INDENT * indent,
                            self._name, ' ',
                            str(datadict), ' ',
                            str(list(datalist)),
                            '\n',
                            ''.join(node.display(indent + 1, *datalist, **datadict)
                                    for node in self)))

    def compile_nodes(self):
        nodes = Node()
        for node in self:
            nodes += node.compile()
        return nodes

    def compile(self):
        nodes = self.compile_nodes()
        if self._name is None:
            return nodes
        else:
            return NodeString('<' + self._name + '>') + nodes

    def render_nodes(self, *datalist, **datadict):
        s = ['']
        for node in self:
            result = node.render(*datalist, **datadict)
            if isinstance(result, Node) or isinstance(s[-1], Node):
                if len(result) <= 1:
                    s.append(result)
                else:
                    # should have len >= 3
                    s[-1] += result.pop(0)
                    s.extend(result)
            else:
                s[-1] = s[-1] + result
        if isinstance(s[-1], Node):
            s.append('')
        if len(s) == 1:
            return s[0]
        else:
            return self.__class__().extend(s)

    def render(self, *datalist, **datadict):
        nodes = self.render_nodes(*datalist, **datadict)
        if self._name is None:
            return nodes
        else:
            if isinstance(nodes, Node):
                nodes[0] = '<' + self._name + '>' + nodes[0]
                result = self.__class__().extend(nodes)
            else:
                result = '<' + self._name + '>' + nodes
            return result


def each(*items):
    def wrapper(node):
        return NodeEach(node, *items)
    return wrapper


class NodeEach(Node):

    def __init__(self, node, *itemlist, **itemdict):
        self._name = node._name
        self._datalist = list(itemlist) or node._datalist
        self._datadict = itemdict or node._datadict
        self.extend(node)

    def display(self, indent=0, *datalist, **datadict):
        # if self._items is None:
        #     if isinstance(self._node, Node):
        #         data = self._node._datalist or self._node._datadict
        #     else:
        #         self._node = NodeString(self._node)
        #         data = None
        #     data = data or datalist or datadict or None
        # else:
        #     data = self._items
        data = self._datalist or self._datadict or datalist or datadict or None
        s = ''.join((INDENT * indent,
                     '+each-{0}{1}'.format(self._datalist, self._datadict), ' ',
                     str(data), ' ',
                     str(datadict), ' ',
                     str(list(datalist)),
                     '\n'))
        if data is None:
            s += super(NodeEach, self).display(indent + 1)
        else:
            try:
                # assume mapping
                s += ''.join(super(NodeEach, self).display(indent + 1, key=key, value=value)
                             for key, value in data.items())
            except AttributeError as exc:
                # mapping failed, assume sequence of mapping
                try:
                    s += ''.join(super(NodeEach, self).display(indent + 1, **item)
                                 for item in data)
                except TypeError as exc:
                    # assume sequence of sequence
                    try:
                        s += ''.join(super(NodeEach, self).display(indent + 1, *item)
                                     for item in data)
                    except TypeError as exc:
                        # assume sequence of scaler
                        try:
                            s += ''.join(super(NodeEach, self).display(indent + 1, item)
                                         for item in data)
                        except TypeError as exc:
                            # ignore data
                            s += super(NodeEach, self).display(indent + 1)

#            try:
#                for item in data:
#                    try:
#                        s += self._node.display(indent, **item)
#                    except TypeError:
#                        try:
#                            if isinstance(item, (str, unicode)):
#                                raise TypeError
#                            s += self._node.display(indent, *item)
#                        except TypeError:
#                            s += self._node.display(indent, item)
#            except TypeError:
#                s += self._node.display(indent + 1)
        return s

    def compile(self):
        nodes = Node()
        if not (self._datalist or self._datadict):
            nodes.append(
                self.__class__(super(NodeEach, self).compile())
                )
            return nodes
        else:
            data = self._datalist or self._datadict
            try:
                # assume mapping
                sub_nodes = [self._node.render(key=key, value=value)
                         for key, value in data.items()]
            except AttributeError as exc:
                # mapping failed, assume sequence of mapping
                try:
                    sub_nodes = [self._node.render(**item)
                             for item in data]
                except TypeError as exc:
                    # assume sequence of sequence
                    try:
                        sub_nodes = [self._node.render(*item)
                                 for item in data]
                    except TypeError as exc:
                        # assume sequence of scaler
                        try:
                            sub_nodes = [self._node.render(item)
                                     for item in data]
                        except TypeError as exc:
                            # ignore data
                            sub_nodes = [self._node.compile()]

            result_nodes = Node().append(NodeString())
            for nodes in sub_nodes:
                if isinstance(nodes, Node):
                    result_nodes[-1] += nodes[0]
                    result_nodes.extend(nodes[1:])
                else:
                    result_nodes[-1] += nodes
            if len(result_nodes) == 1:
                return result_nodes[0]
            else:
                return result_nodes

    def render(self, *datalist, **datadict):
        if self._items is None:
            if isinstance(self._node, Node):
                data = self._node._datalist or self._node._datadict
            else:
                self._node = NodeString(self._node)
                data = None
            data = data or datalist or datadict or None
        else:
            data = self._items

        if data is None:
            return self.__class__(self._node.compile())
        else:
            try:
                # assume mapping
                sub_nodes = [self._node.render(key=key, value=value)
                         for key, value in data.items()]
            except AttributeError as exc:
                # mapping failed, assume sequence of mapping
                try:
                    sub_nodes = [self._node.render(**item)
                             for item in data]
                except TypeError as exc:
                    # assume sequence of sequence
                    try:
                        sub_nodes = [self._node.render(*item)
                                 for item in data]
                    except TypeError as exc:
                        # assume sequence of scaler
                        try:
                            sub_nodes = [self._node.render(item)
                                     for item in data]
                        except TypeError as exc:
                            # ignore data
                            sub_nodes = [self._node.compile()]

            result_nodes = ['']
            for nodes in sub_nodes:
                if isinstance(nodes, Node):
                    result_nodes[-1] += nodes[0]
                    result_nodes.extend(nodes[1:])
                else:
                    result_nodes[-1] += nodes
            return self.__class__(Node().extend(result_nodes))

def extract(*extracts):
    def wrapper(node):
        return NodeExtract(node, *extracts)
    return wrapper

class NodeExtract(Node):

    def __init__(self, node, *extracts):
        self._name = node._name
        self._datalist = node._datalist
        self._datadict = node._datadict
        self.extend(node)
        self._extracts = extracts if len(extracts) > 0 else None

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
        s = ''.join((INDENT * indent,
                     '=extract-{0}'.format(self._extracts), ' ',
                     str(data), ' ',
                     str(datadict), ' ',
                     str(list(datalist)),
                     '\n'))
        if data is None:
            return s + super(NodeExtract, self).display(indent + 1)
        else:
            try:
                return s + super(NodeExtract, self).display(indent + 1, **data)
            except TypeError:
                try:
                    if isinstance(data, (str, unicode)):
                        raise TypeError
                    return s + super(NodeExtract, self).display(indent + 1, *data)
                except TypeError:
                    return s + super(NodeExtract, self).display(indent + 1, data)

    def compile(self):
        nodes = Node().append(
            self.__class__(super(NodeExtract, self).compile(), *self._extracts)
            )
        return nodes


table = Node('table').append(Node('thead').append(Node('tr').append(each()(Node('th')))))

if __name__ == '__main__':
    import unittest

    class TestNodes(unittest.TestCase):

        def test_node(self):
           n = Node('div')
           self.assertEqual(n.display(), "div {} []\n")

        def test_node_sibling(self):
           n = Node().append(Node('one'), Node('two'))
           self.assertEqual(n.display(), "one {} []\n"
                                         "two {} []\n")

        def test_node_child(self):
           n = Node('one').append(Node('two'))
           self.assertEqual(n.display(), "one {} []\n"
                                         "    two {} []\n")

        def test_each(self):
           n = each()(Node('div'))
           self.assertEqual(n.display(), "+each-[]{} None {} []\n"
                                         "    div {} []\n")

        def test_each_const(self):
           n = each('a', 'b')(Node('div'))
           self.assertEqual(n.display(), "+each-['a', 'b']{} ['a', 'b'] {} []\n"
                                         "    div {} ['a']\n"
                                         "    div {} ['b']\n")

        def test_extract(self):
           n = extract('key')(Node('div'))
           self.assertEqual(n.display(), "=extract-('key',) None {} []\n"
                                         "    div {} []\n")

        def test_compile_simple(self):
           n = Node('html').append(Node('head'), Node('body'))
           c = n.compile()
           self.assertEqual(c.display(), "<html><head><body>\n")

        def test_compile_extract(self):
           n = Node('table').append(Node('thead'), extract('fields')(Node('tbody')))
           c = n.compile()
           self.assertEqual(c.display(), "<table><thead>\n"
                                         "=extract-('fields',) None {} []\n"
                                         "    <tbody>\n")

        def test_compile_each(self):
           n = Node('table').append(Node('thead').append(Node('tr').append(each()(Node('th')))))
           c = n.compile()
           self.assertEqual(c.display(), "<table><thead><tr>\n"
                                         "+each-[]{} None {} []\n"
                                         "    <th>\n")

        def test_compile_each_const(self):
            n = each(1, 2)(Node('div'))
            c = n.compile()
            self.assertEqual(c.display(), "+each-[1, 2]{} [1, 2] {} []\n"
                                          "    <div>")

        # def test_compile_full_table(self):
        #     fields = ['one', 'two']
        #     n = Node('table').append(
        #         Node('thead').append(Node('tr').append(each(*fields)(Node('th')))),
        #         Node('tbody').append(each()(Node('tr').append(each()(Node('td'))))),
        #         Node('tfoot').append(Node('tr').append(each(*fields)(Node('th')))))
        #     print(n.display(0))
        #     c = n.compile()
        #     print(c.display(0))
        #     self.assertEqual(str(c), "<table><thead><tr><th><th><tbody>\n"
        #                              "+each-() None {} []\n"
        #                              "    <tr>\n"
        #                              "    +each-() None {} []\n"
        #                              "        <td>\n<tfoot><tr><th><th>\n")

    unittest.main()
