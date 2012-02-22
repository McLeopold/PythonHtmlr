from .base import htmlr

# doctype
class doctype(htmlr):
    _name = "!DOCTYPE"
    _attributes = {'html': None}
    _close = False

# html tags
class html(htmlr): pass
class head(htmlr): pass
class meta(htmlr): pass
class link(htmlr): pass
class title(htmlr): pass
class style(htmlr): pass
class body(htmlr): pass
class div(htmlr): pass
class hr(htmlr): pass
class br(htmlr): pass
class p(htmlr): pass
class a(htmlr): pass
        
# html header tags
class h1(htmlr): pass
class h2(htmlr): pass
class h3(htmlr): pass
class h4(htmlr): pass
class h5(htmlr): pass
class h6(htmlr): pass
class h7(htmlr): pass

# html misc tags
class script(htmlr):
    _empty_element = False
class style(htmlr): pass
    
