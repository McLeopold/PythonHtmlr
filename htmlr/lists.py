from .base import htmlr, htmlrlist

# list tags
class ol(htmlr): pass
class ul(htmlr): pass
class li(htmlr): pass
class dl(htmlr):
    def __init__(self, ddict, *nodes, **attributes):
        super(dl,self).__init__(*nodes, **attributes)
        dlist = htmlrlist()
        if isinstance(ddict, dict):
            for key, value in ddict.items():
                dlist.append(dtdd(key,value))
        self._nodes.append(dlist)
class dt(htmlr): pass
class dd(htmlr): pass
class dtdd(htmlrlist):
    def __init__(self, dttext, ddtext, **attributes):
        super(dtdd,self).__init__()
        self.append(dt(dttext))
        self.append(dd(ddtext))
        self.add(**attributes)

