from htmlr import *

t = doctype.html(
    head(lang="en")(
        meta(charset="utf-8"),
        title("{title}")
    ),
    body(
        form(
            button(id="test", value="Test")
        ),
        h1("{title}"),
        extract('data').table(
            thead(
                tr(
                    extract(0)(each.th('{key}'))
                )
            ),
            tbody(
                each.tr(
                    each.td('{value}')
                )
            )
        )
    )
)

if __name__ == "__main__":
    import xml.dom.minidom

    data = {'title': 'sample table',
            'data': [{'name': 'scott',
                      'id': 1},
                     {'name': 'mike',
                      'id': 2}]}
    c = t.compile()
    print(xml.dom.minidom.parseString(c.render(**data)).toprettyxml())
