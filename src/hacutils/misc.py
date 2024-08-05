# hacutils/misc.py
# Josh Reed 2021 2022 2023 2024
#
# Some random functions that come in handy. As this files grows longer parts of it will be
# split off and organized.

def strip_unicode(dictionary):
	"""Recursively converts dictionary keys to strings.
	
	Args:
		dictionary: The dict with keys and values which are u'' unicode strings.
	Returns:
		dict: The very same dict, but with all unicode strings replaced with regular strings.
	"""
	if not isinstance(dictionary, dict):
		return dictionary
	return dict((str(k), strip_unicode(v)) 
		for k, v in dictionary.items())