from .base import htmlr

# html form tags
class form(htmlr):
    _attributes = {'method': 'POST', 'action': ''}
class input_(htmlr):
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
class textarea(htmlr): pass
class select(htmlr): pass
class fileinput(input_):
    _attributes = {'type': 'file'}

class hidden(htmlr):
    _name = 'input'
    _attributes = {'type': 'hidden'}
    def __init__(self, name, value, *nodes, **attributes):
        super(hidden,self).__init__(*nodes, **attributes)
        self.add(name=name, value=value)
        
class submit(hidden):
    _attributes = {'type': 'submit',}
    
