##############################################
# The MIT License (MIT)
# Copyright (c) 2018 Kevin Walchko
# see LICENSE for full details
##############################################

try:
    from importlib.metadata import version # type: ignore
except ImportError:
    from importlib_metadata import version # type: ignore

from mbeacon.mbeacon import BeaconServer
from mbeacon.mbeacon import BeaconFinder
# from mbeacon.mbeacon import Service

__author__ = "Kevin Walchko"
__license__ = "MIT"
__version__ = version("mbeacon")
