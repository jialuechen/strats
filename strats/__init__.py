__version__='0.0.1'
__author__='Jialue Chen'

import os
import sys

path = {
    "library": os.path.dirname(os.path.realpath(__file__)),
    "caller": os.path.dirname(os.path.realpath(sys.argv[0]))
}

__all__ = [
    'feed',
    'algo',
    'broker',
    'indicators',
    'path'
]