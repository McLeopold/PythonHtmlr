============
ZeroViz Xmlr
============

ZeroViz Xmlr is an easy way to use python code to produce xml or html.
It creates easy shortcuts for commonly used tags with default attributes
and nodes.  You can create templates and then pass in python data to
produce xml quickly.  The code becomes simple and easier to read.

Here is an example of what can be done::

    #!/usr/bin/env python
    
    from xmlr import xmlr, xmlrlist, table, thead, tbody, tr, th, td
    
    tabledata = [{"name": "scott", "id": 1},
                 {"name": "mike", "id": 2}]
    mytable = table(
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
    print(format(mytable))
    
    # produces the following text
    # <table>
    #     <thead>
    #         <tr>
    #             <th>name</th>
    #             <th>id</th>
    #         </tr>
    #     </thead>
    #     <tbody>
    #         <tr id="1">
    #             <td>scott</td>
    #             <td>1</td>
    #         </tr>
    #         <tr id="2">
    #             <td>mike</td>
    #             <td>2</td>
    #         </tr>
    #     </tbody>
    # </table>
    
This technique keeps the developer out of a templating system that has its
own syntax.  Complex templates can be solved with python code only rather
than learning two languages.  Xmlr object template can be modified in code
for special cases without creating multiple template files or complicated
template files loaded with optional parts.

Creating Custom Objects
=======================

You can create xmlr objects that represent tags and load them with default
values.  You can also subclass objects to pass those defaults on::

    class table(xmlr):
        _attributes = {'border': 0,
                       'cellspacing': 0
                       'cellpadding': 0}
    class td(xmlr):
        _nodes = ['&nbsp;']

    class th(td): # inherits default node value of '&nbsp;'
        _attributes = {'class': 'header'}

You can now use the object and the attributes with automatically be added
to all table tags:::

    print(format(table(
                       tr(th().th()),
                       tr(td().td())
                       ))
    
    # produces the following text
    # <table>
    #     <tr>
    #         <th class="header">&nbsp;</th>
    #         <th class="header">&nbsp;</th>
    #     </tr>
    #     <tr>
    #         <td>&nbsp;</td>
    #         <td>&nbsp;</td>
    #     </tr>
    # </table>

Tell your friends about Xmlr!