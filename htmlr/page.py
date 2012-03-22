from .base import Htmlr

# doctype
class doctype(Htmlr):
    _name = "!DOCTYPE"
    _attributes = {'html': None}
    _close = False

# html tags
class html(Htmlr): pass
class head(Htmlr): pass
class meta(Htmlr): pass
class link(Htmlr): pass
class title(Htmlr): pass
class body(Htmlr): pass
class div(Htmlr): pass
class hr(Htmlr): pass
class br(Htmlr): pass
class p(Htmlr): pass
class a(Htmlr): pass

# html header tags
class h1(Htmlr): pass
class h2(Htmlr): pass
class h3(Htmlr): pass
class h4(Htmlr): pass
class h5(Htmlr): pass
class h6(Htmlr): pass
class h7(Htmlr): pass

# html misc tags
class script(Htmlr):
    _empty_element = False
class javascript(script):
    _name = 'script'
    def __init__(self, js_file):
        super(javascript, self).__init__(src=js_file)
class style(Htmlr): pass
class css(link):
    _name = 'link'
    def __init__(self, css_file):
        super(css, self).__init__(rel='stylesheet', href=css_file)
class comment(Htmlr):
    def _get_open_tag(self):
        return "<!--"
    def _get_close_tag(self):
        return "-->"

