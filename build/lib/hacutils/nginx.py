# hacutils/nginx.py
# Josh Reed 2024
#
# Utilities for NginX

# Our code

# Other libs

# Base python
import os
import stat
import pathlib
import grp

def dir_nginx_check_read_accessible(fpath_dir: str, nginx_group: str=None) -> str:
	"""Determine whether nginx will be able to read and serve files from the provided directory, given
	this directory's permissions.

	Nginx has some small quirks for reading that I've stumbled over before. The directory must:
	1. Be traversable, meaning that execute permissions must exist on every folder up to root.
	2. Be readable
	3. All subfiles must also be readable, obviously.

	A group name can be provided as well, for cases in which the administrator wishes to restrict read access
	to static files but still make them accessible via group permissions. This will simply add group checking
	into the mix.

	Args:
		fpath_dir (str): Absolute path to a folder, which we are investigating.
		nginx_group (str, optional): The name of the group to which the nginx user belongs. Default None.

	Returns:
		None if the dir is accessible or a string with a reason why it is not accessible, if it is not.
	"""
	# stat.E_ETC flags
	# https://docs.python.org/3/library/stat.html

	# First, check that execute permissions exist all the way up the stack.	
	path = pathlib.Path(fpath_dir)

	flag = False
	while path.parent != path:

		statinfo = os.stat(path.resolve())
		
		grp_name = grp.getgrgid(statinfo.st_gid)[0]
		grp_execute = statinfo.st_mode & stat.S_IXGRP
		etc_execute = statinfo.st_mode & stat.S_IXOTH

		# If etc can't execute, set flag to true
		if not etc_execute:
			flag = True
			# However, if the group is the nginx group and *it* can execute, reset flag back to False
			if grp_name == nginx_group and grp_execute:
				flag = False
				
		if flag:
			return f"Directory '{fpath_dir}' is not traversable: parent directory '{path.resolve()}' does not "+ \
				f"provide execute perms."


		path = path.parent

	# Then, ensure that nginx can read the folder.
	statinfo = os.stat(fpath_dir)
	flag = False
	grp_read = statinfo.st_mode & stat.S_IRGRP
	etc_read = statinfo.st_mode & stat.S_IROTH
	grp_name = grp.getgrgid(statinfo.st_gid)[0]
	# If etc can't read, set flag to true
	if not etc_read:
		flag = True
		# However, if the group is the nginx group and *it* can read, reset flag back to False
		if grp_name == nginx_group and grp_read:
			flag = False

	if flag:
		return f"Directory '{fpath_dir}' does not allow read permissions"
	
	return None