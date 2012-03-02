import unittest
from htmlr import *

class TestHtmlrs(unittest.TestCase):

    def test_node(self):
        n = div
        self.assertEqual(n.display(), "div {} []\n")

    def test_node_sibling(self):
        n = section.article
        self.assertEqual(n.display(), "section {} []\n"
                                      "article {} []\n")

    def test_node_child(self):
        n = section(article)
        self.assertEqual(n.display(), "section {} []\n"
                                      "    article {} []\n")

    def test_each(self):
        n = each()(div)
        self.assertEqual(n.display(), "+each-[]{} None {} []\n"
                                      "    div {} []\n")

    def test_each_const(self):
        n = each('a', 'b')(div)
        self.assertEqual(n.display(), "+each-['a', 'b']{} ['a', 'b'] {} []\n"
                                      "    div {} ['a']\n"
                                      "    div {} ['b']\n")

    def test_extract(self):
        n = extract('key')(div)
        self.assertEqual(n.display(), "=extract-('key',) None {} []\n"
                                      "    div {} []\n")

    def test_compile_simple(self):
        n = html(head, body)
        c = n.compile()
        self.assertEqual(c.display(), "<html><head /><body /></html>\n")

    def test_compile_extract(self):
        n = table(thead, extract('fields')(tbody))
        c = n.compile()
        self.assertEqual(c.display(), "<table><thead />\n"
                                      "=extract-('fields',) None {} []\n"
                                      "    <tbody />\n"
                                      "</table>\n")

    def test_compile_each(self):
        n = table(thead(tr(each()(th))))
        c = n.compile()
        d = c.display()
        self.assertEqual(c.display(), "<table><thead><tr>\n"
                                      "+each-[]{} None {} []\n"
                                      "    <th />\n"
                                      "</tr></thead></table>\n")

    def test_compile_each_const(self):
        n = each(1, 2)(div)
        c = n.compile()
        self.assertEqual(c.display(), "<div /><div />\n")

    def test_compile_full_table(self):
        fields = ['one', 'two']
        n = table(
            thead(tr(each(*fields)(th()))),
            tbody(each()(tr(each()(td())))),
            tfoot(tr(each(*fields)(th()))))
        c = n.compile()
        print(c.display())
        self.assertEqual(c.display(), "<table><thead><tr><th /><th /></tr></thead><tbody>\n"
                                      "+each-[]{} None {} []\n"
                                      "    <tr>\n"
                                      "    +each-[]{} None {} []\n"
                                      "        <td />\n"
                                      "    </tr>\n"
                                      "</tbody><tfoot><tr><th /><th /></tr></tfoot></table>\n")

if __name__ == '__main__':
    unittest.main()
