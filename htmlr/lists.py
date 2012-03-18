from .base import Htmlr

# list tags
class ol(Htmlr): pass
class ul(Htmlr): pass
class li(Htmlr): pass
class dl(Htmlr):
    def __init__(self, ddict, *nodes, **attributes):
        super(dl, self).__init__(*nodes, **attributes)
        dlist = Htmlr()
        if isinstance(ddict, dict):
            for key, value in ddict.items():
                dlist.append(dtdd(key, value))
        self.append(dlist)
class dt(Htmlr): pass
class dd(Htmlr): pass
class dtdd(Htmlr):
    def __init__(self, dttext, ddtext, **attributes):
        super(dtdd, self).__init__(dttext, ddtext)
        self[0](**attributes)
        self[1](**attributes)
