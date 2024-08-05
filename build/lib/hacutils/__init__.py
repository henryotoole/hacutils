# hacutils/__init__.py
# Josh Reed 2024
#
# Module file

# For now I export these all under a flat namespace. I'm considering reversing this and simply using
# the files as namespaces for individual modules. Time will tell which approach is the better.

# Exports
from hacutils.config import load_config, generate_from_defaults, defaults_apply, CfgEntry, find_config
from hacutils.misc import strip_unicode
from hacutils.db import Database, DatabaseTesting
from hacutils.filesys import (
	folder_empty,
	get_chmod_number,
	get_group,
	mkdirs,
	path_to_filename,
	is_path_safe
)
from hacutils.network import get_json
from hacutils.term import (
	get_line_header,
	terminal_width,
	progress_print,
	progress_print_at_interval,
	print_json,
	input_get_confirm,
	input_get,
	input_get_date,
	input_get_choice,
	input_get_choices,
	input_get_enum,
	input_get_enums,
	input_get_multiline,
)