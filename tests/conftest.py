# tests/conftest.py
# Josh Reed 2024
#
# Fixture setup for hacutils

# Our code
from hacutils.filesys import mkdirs

# Other libs
import pytest

# Base python
import os
import pathlib



@pytest.fixture
def fpath_dev() -> str:
	"""Fixture that returns the absolute filepath to the 'dev' directory.
	"""
	
	fpath = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "dev")
	mkdirs(fpath, folder=True)
	return fpath