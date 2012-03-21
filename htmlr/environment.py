from os import path

class TemplateNotFound(IOError, LookupError):
    pass

class TemplateNotSingle(IOError, LookupError):
    pass

def split_template_path(template):
    """Split a path into segments and perform a sanity check.  If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    for piece in template.split('/'):
        if path.sep in piece \
           or (path.altsep and path.altsep in piece) or \
           piece == path.pardir:
            raise TemplateNotFound(template)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces

class Environment(object):

    def __init__(self, search_path, encoding='utf-8'):
        if isinstance(search_path, basestring):
            search_path = [search_path]
        self.search_path = list(search_path)
        self.encoding = encoding
        self.cache = {}

    def get_template(self, template):
        pieces = split_template_path(template)
        pieces[-1] += '.py'
        for searchpath in self.search_path:
            filename = path.join(searchpath, *pieces)
            if path.exists(filename):
                vars = {}
                execfile(filename, vars)
                templates = vars.get('templates')
                if len(templates) == 1:
                    return templates[0].compile()
                else:
                    raise TemplateNotSingle
        raise TemplateNotFound
