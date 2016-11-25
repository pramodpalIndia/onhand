import warnings

warnings.warn("{% load regsitration_tags %} is deprecated, use {% load registration %}",
              DeprecationWarning)

from .registration import *
