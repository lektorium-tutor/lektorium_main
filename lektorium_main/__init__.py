"""
One-line description for README and other doc files.
"""
import os
from pathlib import Path

__version__ = '0.1.0'

ROOT_DIRECTORY = Path(os.path.dirname(os.path.abspath(__file__)))

default_app_config = 'lektorium_main.apps.LektoriumMainConfig'  # pylint: disable=invalid-name
