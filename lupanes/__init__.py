"""
Package metadata definition.
"""
from django.utils.version import get_version as django_get_version

VERSION = (0, 1, 1, 'alpha', 1)

__version__ = django_get_version(VERSION)


def get_version():
    return __version__
