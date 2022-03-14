import importlib.metadata

__version__ = importlib.metadata.version("dvg")

from . import scdv_embedding
from . import models
from . import scanners
from . import iter_funcs
from . import text_funcs
from . import main

from .main import main

from . import dvgi