try:
    import markdown as _markdown
except ImportError:
    quit()
from htmlr.base import Htmlr, HtmlrString, INDENT
import os

markdown_extensions = ['extra',
                       'codehilite',
                       'toc',
                       'wikilinks']

class markdown(Htmlr):

    def __init__(self, *fnames):
        self.extend(fnames)
        self._md = _markdown.Markdown(extensions=markdown_extensions)

    def display(self, indent=0, *datalist, **datadict):
        if len(self) == 1:
            return INDENT * indent + "$markdown: " + self[0] + "\n"
        else:
            result = INDENT * indent + "$markdown:\n"
            for fname in self:
                result += INDENT * (indent + 1) + fname + "\n"
            return result

    def compile(self):
        result = HtmlrString()
        for fname in self:
            if os.path.exists(fname):
                result += self._render_file(fname)
            else:
                result += self.__class__(fname)
        return result

    def render(self, *datalist, **datadict):
        result = HtmlrString()
        for fname in self:
            fname = fname.format(*datalist, **datadict)
            if os.path.exists(fname):
                result += self._render_file(fname).format(*datalist, **datadict)
            else:
                result += self._render_text(fname).format(*datalist, **datadict)
        return result

    def _render_text(self, mtext):
        return HtmlrString(self._md.convert(mtext))

    def _render_file(self, fname):
        try:
            with open(fname) as f:
                m = f.read()
            return HtmlrString(self._md.convert(m))
        except IOError:
            return HtmlrString()
