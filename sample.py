from htmlr import *

doctype.html(
    head(lang="en")(
        meta(charset="utf-8"),
        title("htmlr"),
        css('style.css'),
        javascript('script.js')
    ),
    body(
        h1("Hello World"),
        comment("woot!", h2("test")),
        div["content"]('{0}')
    )
)
