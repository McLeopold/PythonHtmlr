from .base import Htmlr

# html form tags
class form(Htmlr):
    _attributes = {'method': 'POST', 'action': ''}
class input_(Htmlr):
    _name = "input"
    _attributes = {"type": "", "value": ""}
class button(input_):
    _attributes = {"type": "button", "value": ""}
class text(input_):
    _attributes = {"type": "text", "value": ""}
class checkbox(input_):
    _attributes = {"type": "checkbox", "value": ""}
class radio(input_):
    _attributes = {"type": "radio", "value": ""}
class textarea(Htmlr): pass
class select(Htmlr): pass
class fileinput(input_):
    _attributes = {'type': 'file'}

class hidden(Htmlr):
    _name = 'input'
    _attributes = {'type': 'hidden'}
    def __init__(self, name, value, *nodes, **attributes):
        super(hidden,self).__init__(*nodes, **attributes)
        self.add(name=name, value=value)
        
class submit(hidden):
    _attributes = {'type': 'submit',}
    
