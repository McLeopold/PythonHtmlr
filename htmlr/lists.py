from .base import Htmlr, HtmlrList

# list tags
class ol(Htmlr): pass
class ul(Htmlr): pass
class li(Htmlr): pass
class dl(Htmlr):
    def __init__(self, ddict, *nodes, **attributes):
        super(dl,self).__init__(*nodes, **attributes)
        dlist = Htmlrlist()
        if isinstance(ddict, dict):
            for key, value in ddict.items():
                dlist.append(dtdd(key,value))
        self._nodes.append(dlist)
class dt(Htmlr): pass
class dd(Htmlr): pass
class dtdd(HtmlrList):
    def __init__(self, dttext, ddtext, **attributes):
        super(dtdd,self).__init__()
        self.append(dt(dttext))
        self.append(dd(ddtext))
        self.add(**attributes)

