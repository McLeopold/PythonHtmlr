from htmlr import *

doctype.html(
    head(lang="en")(
        meta(charset="utf-8"),
        title("htmlr")
    ),
    body(
        h1("Hello World"),
        comment("woot!", h2("test")),
        div["content"]
    )
)
