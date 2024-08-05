# hacutils/filesys.py
# Josh Reed 2024
#
# Simple utilites for dealing with filesystems.

# Other libs

# Base python
import os
import shutil
import re
import grp

def folder_empty(folder_path):
	"""Empty the provided folder path. This is recursive and will remove all folders and files in the
	provided path. It will not remove the folder itself.

	Args:
		folder_path (str): Path to the folder
	"""
	for root, dirs, files in os.walk(folder_path):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:
			shutil.rmtree(os.path.join(root, d))

def get_chmod_number(folder_path):
	"""Get the three-number string of the chmod permission number for this folder.

	Args:
		folder_path (str): Path to folder
	
	Returns:
		str: A number like '777' or '603'
	"""

	return str(oct(os.stat(folder_path).st_mode)[-3:])

def get_group(fpath):
	"""Get the group of a file or folder.

	Args:
		fpath (str): An absolute filepath

	Returns:
		str: The groupname that owns the file
	"""
	stat_info = os.stat(fpath)
	gid = stat_info.st_gid
	group = grp.getgrgid(gid)[0]
	return group

def mkdirs(fpath, folder=False):
	"""Make all needed directories to fpath. If fpath is intended to be a folder, then folder should be
	set to True to ensure that folder itself is created.

	Args:
		fpath (str): Absolute fileystem path
		folder (bool, optional): If set to True, interpet the endpoint of the provided path as a folder and create
			it. Default False.
	"""
	# If the endpoint is not specified as a folder and is not an existing folder in filesys, shorten the path.
	if (not folder) and (not os.path.isdir(fpath)):
		fpath = os.path.split(fpath)[0]
	# https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
	# While a naive solution may first use os.path.isdir followed by os.makedirs, the solution 
	# above reverses the order of the two operations. In doing so, it prevents a common race 
	# condition having to do with a duplicated attempt at creating the directory, and also disambiguates 
	# files from directories.
	try:
		os.makedirs(fpath)
	except OSError:
		if not os.path.isdir(fpath):
			raise

def path_to_filename(fpath):
	"""Get the filename from this path (e.g. /one/two/three.json -> three)

	Args:
		fpath (str): File path, filename with extension, or filename without extension

	Returns:
		str: The text-only portion of the filename.
	"""
	return os.path.splitext(os.path.basename(fpath))[0]

def is_path_safe(name):
	"""Ensure the provided text has only letters, numers, and underscores.

	Args:
		name (str): The file or folder name, sans dot.

	Returns:
		bool: True if meets above condition
	"""
	return re.match(r'^[A-Za-z0-9_]+$', name)