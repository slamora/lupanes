"""
Package metadata definition.
"""
from django.utils.version import get_version as django_get_version

VERSION = (0, 1, 1, 'final', 0)

__version__ = django_get_version(VERSION)


def get_version():
    return __version__
