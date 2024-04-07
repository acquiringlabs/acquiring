"""Only modules can be imported here"""

from acquiring.contrib import paypal

__all__ = ["paypal"]

assert __all__ == sorted(__all__), sorted(__all__)
