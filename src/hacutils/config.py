# hacutils/config.py
# Josh Reed 2024
#
# Functions to help with handling, loading, and parsing configs. I want to keep anything to do with configs
# as simple and functional as possible.

# Base python
import os
import textwrap
import json


def load_config(cfg_path: str) -> dict:
	"""Load a config file into memory from path by returning a dict with key/value pairs. This file
	is in 'pythonic' format, in the sense that it's really just a python script that is executed and
	stuffed into a dict. Only keys that are in all caps will make it out, all else will be ignored.

	This is handy, because math and path operations can be performed in the config file itself. However,
	it's a bit of a risk as well. Config parsed by this method might need to be sanitized, and config file
	permissions should be considered.

	# A commented line
	CONFIG_KEY = "CONFIG_VALUE"
	CONFIG_KEY_2 = 2
	CONFIG_PATH = "THIS" + "THAT"
	CONFIG_PATH_2 = CONFIG_PATH + "/OTHER"
	CONFIG_SUBDICT = {
		'KEY': 'VALUE',
		'KEY2': 'VALUE2',
	}
	KEY_BOOLEAN = True
	key_in_lowercase = 0 # Will be ignored

	Args:
		cfg_path (str): A path to a config file on disk

	Returns:
		dict: Containing key/value mappings.
	"""
	
	fname = os.path.basename(cfg_path)

	# Read the config file and compile it.
	with open(cfg_path, mode="rb") as ffile:
		# Throw name on for reference, not used.
		src = compile(ffile.read(), fname, "exec")

	# Execute the src, and dump vars into output
	output = {}
	exec(src, output)

	# Alright, but we just want to pull out things in all caps. This will handily ignore all that junk below
	# like __loader__, __doc__, etc. and just pull out names that we have defined.
	ret_config = {}
	for k, v in output.items():
		if k.isupper():
			ret_config[k] = v
	return ret_config

def find_config(module_path: str, cfg_name: str) -> str:
	"""Find a config file on the system. This is a semi-specific method I use generally to find configs
	with priority given to some. Note that cfg_name is supposed to be relatively unique. For example,
	I look in /etc and it would not do to have a collision with some other installed program.

	Config locations, in order of priority:
	.../module_path/dev/cfg_name.cfg
	/etc/cfg_name.cfg

	If no path can be found, this function will check the OS environmental variables for CFG_NAME in all
	uppercase for *a path to the config object*.

	If even that fails, an exception is raised.

	Args:
		module_path (str): Absolute path to the root of the module that is calling find_config() from.
		cfg_name (str): The name of the config file, sans extension.

	Returns:
		str: Absolute path to config file.
	"""
	if('.' in cfg_name): raise ValueError(f"Config names should not include extensions: {cfg_name}")

	paths = [
		os.path.join(module_path, 'dev', cfg_name + ".cfg"),
		os.path.join('/', 'etc', cfg_name + ".cfg")
	]

	for path in paths:
		if os.path.exists(path):
			return path
	
	if hasattr(os.environ, cfg_name.upper()):
		return os.environ[cfg_name.upper()]
	
	raise ValueError(f"No {cfg_name} config could be found. Place a config file in one of the following paths ["\
					f"{', '.join(paths)}] or point the {cfg_name.upper()} env var towards a valid config.")

class CfgEntry:

	def __init__(self, name: str, default=None, comment=None):
		"""Create a new config entry. There's very little logic associated with this class - it's really just
		a dict with good typehinting.

		Args:
			name (str): The name, or key, of the config entry. Will be converted to all caps.
			default (*, optional): The default value for the entry. None will signal that this entry MUST be
				manually specified by the user. Defaults to None.
			comment (str, optional): Optional comment about this entry to place in autogenerated configs.
				Defaults to None.
		"""
		self.name = name.upper()
		self.default = default
		self.comment = comment

def defaults_apply(cfg: dict, defaults: 'list[CfgEntry]'):
	"""Apply a list of defaults to the provided config dict. Any missing keys from the config dictionary will
	be given the default from the list. If a missing key matches to a manual-required config entry, an
	exception will be raised.

	Nothing is returned, but the cfg object will be modified.

	Args:
		cfg (dict): The config dict, a mapping of keys to values. All keys should be upper case.
		defaults (list[CfgEntry]): A list of config entry objects.
	"""
	for cfg_entry in defaults:
		if cfg_entry.name not in cfg:
			if cfg_entry.default is None:
				raise Exception(f"Config does not contain required manually-defined var '{cfg_entry.name}'.")
			cfg[cfg_entry.name] = cfg_entry.default

def generate_from_defaults(file_path: str, defaults: 'list[CfgEntry]', header=None):
	"""Generate a new config file from the provided list of defaults. Should include filename.

	The structure of this file will be:

	# Header lines
	# Header lines
	# Header lines

	# CFG Entry 1's comment, if available
	CFG_ENTRY_1_NAME = "cfg_entry_1_default_value"
	...

	The 'line width' of this file is, at max, 115 characters.

	Args:
		file_path (str): Filepath to dump this default config file at.
		defaults (list[CfgEntry]): A list of defaults.
		header (str, optional): If provided, comments to put at the top of the config file.
	"""
	with open(file_path, 'w+') as ffile:
		ffile.write(_generate_from_defaults(defaults, header=header))

def _generate_from_defaults(defaults: 'list[CfgEntry]', header=None) -> str:
	"""Does the actual work for generate_from_defaults(). See it's declaration.

	Args:
		file_path (str): Filepath to dump this default config file at.
		defaults (list[CfgEntry]): A list of defaults.
		header (str, optional): If provided, comments to put at the top of the config file.
	
	Returns:
		str: With newlines, for printing or writing to file.
	"""
	bulk_text = ""

	for line in textwrap.wrap(header, 113):
		bulk_text += f"# {line}\n"

	bulk_text += "\n"

	for entry in defaults:

		bulk_text += "\n"

		# Add the comment, if it exists
		if entry.comment:
			for line in textwrap.wrap(entry.comment, 113):
				bulk_text += f"# {line}\n"

		# Now add the value. A little trickier.
		val = entry.default
		if val is None:
			val = "MUST_BE_MANUALLY_DEFINED"
		# Use JSON parser, which is pretty good, but fix some things for python's case.
		val_str = json.dumps(val, indent='\t').replace("true", "True").replace("false", "False")
		val_str = val_str.replace("null", "None")
		# Prepend the config var name
		val_str = f"{entry.name} = {val_str}"
		# Add straight to bulk text
		bulk_text += val_str

	return bulk_text