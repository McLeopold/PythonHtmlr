from htmlr import *

doctype().html(
    head(
        meta(charset="utf-8"),
        title("sample table"),
        lang="en"
    ),
    body(
        h1("sample table"),
        table(
            tr(
                th("{id}")
            ),
            tr(
                td("{name}")
            )
        ),
        div().each()
    )
)

if __name__ == "__main__":
    data = [{'name': 'scott',
             'id': 1},
            {'name': 'mike',
             'id': 2}]
    render(data)
