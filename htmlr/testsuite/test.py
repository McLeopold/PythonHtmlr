import unittest
import logging

from htmlr import Htmlr, HtmlrList
from htmlr.page import (
                             div,
                             html, head, title, body, h1)
from htmlr.form import (
                             form, input, text, textarea, hidden,
                             button, radio, checkbox)
from htmlr.table import (
                             table, thead, tbody, tr, td, th)

class Test_htmlr(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testBaseCreate(self):
        x = htmlr("div")
        self.assertEqual(str(x),
                         '<div />')
        self.assertEqual(format(x),
'''<div />''')
        
    def testClassCreate(self):
        class div(htmlr): pass
        x = div()
        self.assertEqual(str(x),'<div />')
        self.assertEqual(format(x),
'''<div />''')

    def testClassCreateDefaults(self):
        class mydiv(htmlr):
            _name = 'div'
            _nodes = ['test']
            _attributes = {'class_':'test'}
        x = mydiv()
        self.assertEqual(str(x),'<div class="test">test</div>')
        self.assertEqual(format(x),
'''<div class="test">test</div>''')
        
    def testBaseCreateNode(self):
        self.assertEqual(str(htmlr("div","test")),
                         '<div>test</div>')
        self.assertEqual(format(htmlr("div","test")),
                         '<div>test</div>')

    def testBaseCreateAttribute(self):
        self.assertEqual(str(htmlr("div",name="test")),
                         '<div name="test" />')
        self.assertEqual(format(htmlr("div",name="test")),
                         '<div name="test" />')

    def testBaseCreateNodeAttribute(self):
        self.assertEqual(str(htmlr("div","test",name="test")),
                         '<div name="test">test</div>')
        self.assertEqual(format(htmlr("div","test",name="test")),
                         '<div name="test">test</div>')
    
    def testTableEach(self):
        tabledata = [{"name": "scott", "id": 1},
                     {"name": "mike", "id": 2}]
        htmltext = table(
                       thead(
                           tr(
                               th().each(tabledata[0],"{key}")
                           )
                       ),
                       tbody(
                           tr(id="{id}").each(tabledata).each(
                               td(),"{value}"
                           )
                       )
                   )
        self.assertEqual(str(htmltext),
                         '<table><thead>' +
                         '<tr><th>name</th><th>id</th></tr>' +
                         '</thead><tbody>' +
                         '<tr id="1"><td>scott</td><td>1</td></tr>' +
                         '<tr id="2"><td>mike</td><td>2</td></tr>' +
                         '</tbody></table>')
        
    def testPage(self):
        class jsscript(htmlr):
            _name = "script"
            _attributes = {"type": "text/javascript"}
        pagedata = {"title": "Bla",
                    "scripts": ["one.js", "two.js"]}
        x = html(
                       head(
                           title("{title}"),
                           jsscript().each(pagedata["scripts"],
                               src="{}"
                           )
                       ),
                       body(
                           h1("{title}")
                       )
                   ).format(pagedata)
        self.assertEqual(format(x),
'''<html>
    <head>
        <title>Bla</title>
        <script type="text/javascript" src="one.js" />
        <script type="text/javascript" src="two.js" />
    </head>
    <body>
        <h1>Bla</h1>
    </body>
</html>''')
        
    def testForm(self):
        formdata = {"id": 1,
                    "name": "scott",
                    "which": [1,2]}
        x = form(
                       hidden(name="id",value="{id}"),
                       text(name="name",value="{name}",size=20).br(),
                       checkbox(value="").br(),
                       radio().each([(x,"checked" if x in formdata["which"] else "")
                                   for x in range(3)],
                                  name="which",value="{0}").add(checked="{1}"),
                       button(name="submit",value="Submit"),
                       button(name="cancel",value="Cancel")
                   ).format(formdata)
        self.assertEqual(format(x),
'''<form>
    <input name="id" value="1" />
    <input name="name" value="scott" size="20" />
    <br />
    <input value="" />
    <br />
    <input type="radio" value="0" name="which" checked="" />
    <input type="radio" value="1" name="which" checked="checked" />
    <input type="radio" value="2" name="which" checked="checked" />
    <input name="submit" value="Submit" />
    <input name="cancel" value="Cancel" />
</form>''')

if __name__ in '__main__':
    logger = logging.getLogger('Test_htmlr')
    logger.addHandler(logging.StreamHandler().setLevel(logging.DEBUG))
    unittest.TextTestRunner(verbosity=2).run(
        unittest.TestLoader().loadTestsFromNames(
            ['htmlr_test.Test_htmlr']))
    
