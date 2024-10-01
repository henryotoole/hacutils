# tests/test_nginx.py
# Josh Reed 2024
#
# Test for the nginx utils

# Our code
from hacutils.nginx import dir_nginx_check_read_accessible
from hacutils.filesys import mkdirs

# Other libs
import pytest

# Base python
import os
import stat
import grp


def test_dir_accessible(fpath_dev):
	"""
	Warning: This test is a bit brittle. It relies on having a chain of execute permissions from wherever
	this is installed up to dev.
	"""

	fpath_folder = os.path.join(fpath_dev, "nginx_folder_tests")
	fpath_sub1 = os.path.join(fpath_dev, "nginx_folder_tests", "sub1")

	os.rmdir(fpath_sub1)
	os.rmdir(fpath_folder)

	mkdirs(fpath_folder, folder=True)
	mkdirs(fpath_sub1, folder=True)

	statinfo = os.stat(fpath_folder)
	grp_name = grp.getgrgid(statinfo.st_gid)[0]

	# By def
	assert dir_nginx_check_read_accessible(fpath_folder, "nonexist") is None

	# Remove read perms for etc
	os.chmod(fpath_sub1, int("770", 8))

	assert dir_nginx_check_read_accessible(fpath_sub1, "nonexist") is not None
	assert dir_nginx_check_read_accessible(fpath_sub1, grp_name) is None

	# Remove execute perms for etc and group above
	os.chmod(fpath_folder, int("700", 8))

	assert dir_nginx_check_read_accessible(fpath_sub1, "nonexist") is not None
	assert dir_nginx_check_read_accessible(fpath_sub1, grp_name) is not None