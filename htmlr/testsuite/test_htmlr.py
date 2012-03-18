import unittest
from htmlr import *

@unittest.skip
class TestHtmlr(unittest.TestCase):

    def test_node(self):
        n = div()
        self.assertEqual(n.display(), "div {} []\n")

    def test_node_class(self):
        n = div
        self.assertEqual(n.display(), "div {} []\n")

    def test_node_sibling(self):
        n = section().article()
        self.assertEqual(n.display(), "section {} []\n"
                                      "article {} []\n")

    def test_node_sibling_class(self):
        n = section.article
        self.assertEqual(n.display(), "section {} []\n"
                                      "article {} []\n")

    def test_node_child(self):
        n = section(article())
        self.assertEqual(n.display(), "section {} []\n"
                                      "    article {} []\n")

    def test_node_child_class(self):
        n = section(article)
        self.assertEqual(n.display(), "section {} []\n"
                                      "    article {} []\n")

    def test_each(self):
        n = each()(div)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n")

    def test_each_const(self):
        n = each('a', 'b')(div)
        self.assertEqual(n.display(), "+each-['a', 'b']{} ['a', 'b']\n"
                                      "    div {} ['a']\n"
                                      "    div {} ['b']\n")

    def test_each_chain(self):
        n = div.each('a', 'b')(div)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-['a', 'b']{} ['a', 'b']\n"
                                      "    div {} ['a']\n"
                                      "    div {} ['b']\n")

    def test_extract(self):
        n = extract('key')(div)
        self.assertEqual(n.display(), "=extract-('key',) None\n"
                                      "    div {} []\n")

    def test_extract_chain(self):
        n = div.extract('key')(div)
        self.assertEqual(n.display(), "div {} []\n"
                                      "=extract-('key',) None\n"
                                      "    div {} []\n")

    def test_compile_simple(self):
        n = html(head, body)
        c = n.compile()
        self.assertEqual(c.display(), "*str <html><head /><body /></html> [] {}\n")



    def test_compile_extract(self):
        n = table(
                thead,
                extract('fields')(tbody)
            )
        c = n.compile()
        self.assertEqual(c.display(), "*str <table><thead /> [] {}\n"
                                      "=extract-('fields',) None\n"
                                      "    *str <tbody /> [] {}\n"
                                      "*str </table> [] {}\n")

    def test_compile_each(self):
        n = table(
                thead(
                    tr(
                       each.th
                    )
                )
            )
        c = n.compile()
        self.assertEqual(c.display(), "*str <table><thead><tr> [] {}\n"
                                      "+each-[]{} None\n"
                                      "    *str <th /> [] {}\n"
                                      "*str </tr></thead></table> [] {}\n")

    def test_compile_each_const(self):
        n = each(1, 2)(div)
        c = n.compile()
        self.assertEqual(c.display(), "*str <div /><div /> [] {}\n")

    def test_sample_page(self):
        n = doctype.html(
            head(lang="en")(
                meta(charset="utf-8"),
                title("htmlr")
            ),
            body(
                h1("Hello World")
            )
        )
        self.assertEqual(n.display(), "!DOCTYPE {} []\n"
                                      "html {} []\n"
                                      "    head {} []\n"
                                      "        meta {} []\n"
                                      "        title {} []\n"
                                      "            *lit htmlr\n"
                                      "    body {} []\n"
                                      "        h1 {} []\n"
                                      "            *lit Hello World\n")

    def test_compile_full_table(self):
        fields = ['one', 'two']
        n = table(
            thead(tr(each(*fields)(th()))),
            tbody(each()(tr(each()(td())))),
            tfoot(tr(each(*fields)(th()))))
        c = n.compile()
        self.assertEqual(c.display(), "*str <table><thead><tr><th /><th /></tr></thead><tbody> [] {}\n"
                                      "+each-[]{} None\n"
                                      "    *str <tr> [] {}\n"
                                      "    +each-[]{} None\n"
                                      "        *str <td /> [] {}\n"
                                      "    *str </tr> [] {}\n"
                                      "*str </tbody><tfoot><tr><th /><th /></tr></tfoot></table> [] {}\n")

    def test_node_render(self):
        n = div(class_="test")(disabled=None)(section("Woot!"))
        self.assertEqual(n.render(), '<div class="test" disabled><section>Woot!</section></div>')

    def test_each_const_render(self):
        n = ul(each(1, 2, 3)(li("{0}")))
        self.assertEqual(n.render(), "<ul><li>1</li><li>2</li><li>3</li></ul>")

    def test_extract_render(self):
        data = {'data': ["test"]}
        n = div.extract('data')(div(class_="{0}"))
        self.assertEqual(n.render(**data), '<div /><div class="test" />')


class TestHtmlrEach(unittest.TestCase):

    def gen(self, n, p=True):
        c = n.compile()
        nr = n.render()
        cr = c.render()
        if p:
            print(n.display())
            print(c.display())
            print(nr)
            print(cr)
        return c, nr, cr

    def test_each(self):
        n = each
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n")
        self.assertEqual(c.display(), "+each-[]{} None\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call(self):
        n = each()
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n")
        self.assertEqual(c.display(), "+each-[]{} None\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_const_list(self):
        n = each(1, 2)
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n")
        self.assertEqual(c.display(), "")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_div(self):
        n = each.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      "    *str <div /> [] {}\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_div2(self):
        n = each.div(class_="test")
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      '    *str <div class="test" /> [] {}\n')
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_div_div(self):
        n = each.div.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      "    *str <div /><div /> [] {}\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_div_div2(self):
        n = each.div(class_="test").div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      '    *str <div class="test" /><div /> [] {}\n')
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call_div(self):
        n = each().div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      "    *str <div /> [] {}\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call_div2(self):
        n = each().div(class_="test")
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      '    *str <div class="test" /> [] {}\n')
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call_div_div(self):
        n = each().div.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      "    *str <div /><div /> [] {}\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call_div_div2(self):
        n = each().div(class_="test").div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      '    *str <div class="test" /><div /> [] {}\n')
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call_div_div3(self):
        n = each()(div).div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      "    *str <div /><div /> [] {}\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_call_div_div4(self):
        n = each()(div)(div)
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "+each-[]{} None\n"
                                      "    *str <div /><div /> [] {}\n")
        self.assertEqual(nr, "")
        self.assertEqual(cr, "")

    def test_each_const_div(self):
        n = each(1, 2).div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
                                      "    div {} [1]\n"
                                      "    div {} [2]\n")
        self.assertEqual(c.display(), "*str <div /><div /> [] {}\n")
        self.assertEqual(nr, "<div /><div />")
        self.assertEqual(cr, "<div /><div />")

    def test_each_const_div2(self):
        n = each(1, 2).div(class_="test")
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
                                      "    div {} [1]\n"
                                      "    div {} [2]\n")
        self.assertEqual(c.display(), '*str <div class="test" /><div class="test" /> [] {}\n')
        self.assertEqual(nr, '<div class="test" /><div class="test" />')
        self.assertEqual(cr, '<div class="test" /><div class="test" />')

    def test_each_const_div_div(self):
        n = each(1, 2).div.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
                                      "    div {} [1]\n"
                                      "    div {} [1]\n"
                                      "    div {} [2]\n"
                                      "    div {} [2]\n")
        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
        self.assertEqual(nr, "<div /><div /><div /><div />")
        self.assertEqual(cr, "<div /><div /><div /><div />")

    def test_each_const_div_div2(self):
        n = each(1, 2).div(class_="test").div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
                                      "    div {} [1]\n"
                                      "    div {} [1]\n"
                                      "    div {} [2]\n"
                                      "    div {} [2]\n")
        self.assertEqual(c.display(), '*str <div class="test" /><div /><div class="test" /><div /> [] {}\n')
        self.assertEqual(nr, '<div class="test" /><div /><div class="test" /><div />')
        self.assertEqual(cr, '<div class="test" /><div /><div class="test" /><div />')

    def test_each_const_div_div3(self):
        n = each(1, 2)(div).div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
                                      "    div {} [1]\n"
                                      "    div {} [1]\n"
                                      "    div {} [2]\n"
                                      "    div {} [2]\n")
        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
        self.assertEqual(nr, "<div /><div /><div /><div />")
        self.assertEqual(cr, "<div /><div /><div /><div />")

    def test_each_const_div_div4(self):
        n = each(1, 2)(div)(div)
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
                                      "    div {} [1]\n"
                                      "    div {} [1]\n"
                                      "    div {} [2]\n"
                                      "    div {} [2]\n")
        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
        self.assertEqual(nr, "<div /><div /><div /><div />")
        self.assertEqual(cr, "<div /><div /><div /><div />")

    def test_div_each(self):
        n = div.each
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n")
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_call(self):
        n = div.each()
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n")
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_const_list(self):
        n = div.each(1, 2)
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[1, 2]{} [1, 2]\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n")
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_div(self):
        n = div.each.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      "    *str <div /> [] {}\n")
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_div2(self):
        n = div.each.div(class_="test")
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      '    *str <div class="test" /> [] {}\n')
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_div_div(self):
        n = div.each.div.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      "    *str <div /> [] {}\n"
                                      "*str <div /> [] {}\n")
        self.assertEqual(nr, "<div /><div />")
        self.assertEqual(cr, "<div /><div />")

    def test_div_each_div_div2(self):
        n = div.each.div(class_="test").div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      '    *str <div class="test" /> [] {}\n'
                                      "*str <div /> [] {}\n")
        self.assertEqual(nr, "<div /><div />")
        self.assertEqual(cr, "<div /><div />")

    def test_div_each_call_div(self):
        n = div.each().div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      '    *str <div /> [] {}\n')
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_call_div2(self):
        n = div.each().div(class_="test")
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      '    *str <div class="test" /> [] {}\n')
        self.assertEqual(nr, "<div />")
        self.assertEqual(cr, "<div />")

    def test_div_each_call_div_div(self):
        n = div.each().div.div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      '    *str <div /> [] {}\n'
                                      '*str <div /> [] {}\n')
        self.assertEqual(nr, "<div /><div />")
        self.assertEqual(cr, "<div /><div />")

    def test_div_each_call_div_div2(self):
        n = div.each().div(class_="test").div
        c, nr, cr = self.gen(n, False)
        self.assertEqual(n.display(), "div {} []\n"
                                      "+each-[]{} None\n"
                                      "    div {} []\n"
                                      "div {} []\n")
        self.assertEqual(c.display(), "*str <div /> [] {}\n"
                                      "+each-[]{} None\n"
                                      '    *str <div class="test" /> [] {}\n'
                                      '*str <div /> [] {}\n')
        self.assertEqual(nr, "<div /><div />")
        self.assertEqual(cr, "<div /><div />")

#    def test_each_call_div_div3(self):
#        n = each()(div).div
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[]{} None\n"
#                                      "    div {} []\n"
#                                      "    div {} []\n")
#        self.assertEqual(c.display(), "+each-[]{} None\n"
#                                      "    *str <div /><div /> [] {}\n")
#        self.assertEqual(nr, "")
#        self.assertEqual(cr, "")
#
#    def test_each_call_div_div4(self):
#        n = each()(div)(div)
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[]{} None\n"
#                                      "    div {} []\n"
#                                      "    div {} []\n")
#        self.assertEqual(c.display(), "+each-[]{} None\n"
#                                      "    *str <div /><div /> [] {}\n")
#        self.assertEqual(nr, "")
#        self.assertEqual(cr, "")
#
#    def test_each_const_div(self):
#        n = each(1, 2).div
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [2]\n")
#        self.assertEqual(c.display(), "*str <div /><div /> [] {}\n")
#        self.assertEqual(nr, "<div /><div />")
#        self.assertEqual(cr, "<div /><div />")
#
#    def test_each_const_div2(self):
#        n = each(1, 2).div()
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [2]\n")
#        self.assertEqual(c.display(), "*str <div /><div /> [] {}\n")
#        self.assertEqual(nr, "<div /><div />")
#        self.assertEqual(cr, "<div /><div />")
#
#    def test_each_const_div_div(self):
#        n = each(1, 2).div.div
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [2]\n"
#                                      "    div {} [2]\n")
#        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
#        self.assertEqual(nr, "<div /><div /><div /><div />")
#        self.assertEqual(cr, "<div /><div /><div /><div />")
#
#    def test_each_const_div_div2(self):
#        n = each(1, 2).div().div
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [2]\n"
#                                      "    div {} [2]\n")
#        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
#        self.assertEqual(nr, "<div /><div /><div /><div />")
#        self.assertEqual(cr, "<div /><div /><div /><div />")
#
#    def test_each_const_div_div3(self):
#        n = each(1, 2)(div).div
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [2]\n"
#                                      "    div {} [2]\n")
#        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
#        self.assertEqual(nr, "<div /><div /><div /><div />")
#        self.assertEqual(cr, "<div /><div /><div /><div />")
#
#    def test_each_const_div_div4(self):
#        n = each(1, 2)(div)(div)
#        c, nr, cr = self.gen(n, False)
#        self.assertEqual(n.display(), "+each-[1, 2]{} [1, 2]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [1]\n"
#                                      "    div {} [2]\n"
#                                      "    div {} [2]\n")
#        self.assertEqual(c.display(), "*str <div /><div /><div /><div /> [] {}\n")
#        self.assertEqual(nr, "<div /><div /><div /><div />")
#        self.assertEqual(cr, "<div /><div /><div /><div />")

if __name__ == '__main__':
    unittest.main()
