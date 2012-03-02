from .base import *
from .page import *
from .lists import *
from .tables import *
from .forms import *
from .html5 import *

update_classes()

__all__ = []
for a in list(locals()):
    if not a.startswith('_'):
        __all__.append(a)

