from htmlr import *

t = doctype.html(
    head(lang="en")(
        meta(charset="utf-8"),
        title("{title}")
    ),
    body(
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
    data = {'title': 'sample table',
            'data': [{'name': 'scott',
                      'id': 1},
                     {'name': 'mike',
                      'id': 2}]}
    print(t.display(**data))
    print(t.render(**data))
    c = t.compile()
    print(c.display(**data))
    print(c.render(**data))
