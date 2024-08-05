# hacutils/term.py
# Josh Reed 2024
#
# Utils involving printing to the terminal.

# Other libs
import pendulum

# Base python
import shutil
import math
import json
import time

def get_line_header(message):
	"""Get a header line like below, fit to the width of the terminal.

	############### MESSAGE ###############

	Args:
		message (str): Message to center at top of terminal. If it's too wide, we'll truncate it. If it's an empty
			string, this will return a solid line.

	Returns:
		str: Formatted string
	"""
	tw = terminal_width()

	if len(message) > tw:
		return message[:tw]
	if len(message) == 0:
		return "#" * tw

	w_sides = int((tw - len(message) - 2) / 2)
	out = w_sides * "#" + " " + message + " " + w_sides * "#"
	if len(out) == (tw - 1):
		out += "#"
	
	return out

def terminal_width() -> int:
	"""Get the width of the terminal in characters.
	"""
	return int(shutil.get_terminal_size((80, 20))[0])

def progress_print(pct_prog, incr, sym="="):
	"""Print a progress line like:
	[=====      ] (40.5%)

	Args:
		pct_prog (float): From 0 to 1
		incr (float): The increment that gets printed
	"""
	n_incr = int(1 / incr)
	n_solid = math.floor(n_incr * pct_prog)
	line = "[" + sym*int(math.floor(n_incr * pct_prog)) + " "*(n_incr-n_solid) + "] (" + str(round(pct_prog*100, 1)) + "%)"
	if pct_prog < 1.0:
		print(line, end='\r', flush=True)
	else:
		print(line, flush=True)

def progress_print_at_interval(memspace: dict, dur_s: int, pct_prog: float, incr=0.05):
	"""Call this every loop (or whatever) and it will print progress to the terminal, only updating it once
	every 'dur_s' seconds.

	Args:
		memspace (dict): A dict which is tied to some memory that's consistent across calls to this function.
		dur_s (int): The time between progress updates
		pct_prog (float): The progress as a float from 0 to 1.
		incr (float, optional): The print symbol incr. See progress_print(). Defaults to 0.05.
	"""
	if not 'ts_last' in memspace:
		memspace['ts_last'] = 0
	if (time.time() - memspace['ts_last']) < dur_s:
		return
	
	progress_print(pct_prog, incr)

	memspace['ts_last'] = time.time()

def print_json(data):
	"""Print a JSON in dict structure

	Args:
		data (dict): Dict data
	"""
	print(json.dumps(data, indent=4))

def input_get_confirm() -> bool:
	"""Prompt y/n>> and then wait until the user has responded with one or the other.
	
	Returns:
		bool: True if y, False if n
	"""
	while True:
		resp = input("y/n >>")
		if resp == 'y':
			return True
		elif resp == 'n':
			return False

def input_get(typecast, prompt, accept_blank=False):
	"""Have the user a value that can be cast to the provided type.

	Args:
		typecast (type or function): A type, like int or float. This can also be a function that takes one argument
			and returns the cast object or raises an error.
		prompt (str): The message to display to the user to prompt them.
		accept_blank (bool, optional): Whether to accept an empty input as 'none'. Default False

	Returns:
		pdt object or None if the line was left blank.
	"""

	found = 0

	while not found:
		found = 1
		resp = input(prompt)
		if resp == "" and accept_blank:
			return None
		try:
			result = typecast(resp)
		except Exception as e:
			print("Could not be parsed.")
			found = 0

	return result

def input_get_date(tz="America/New_York", accept_blank=False):
	"""Get a date (a certain day). This will return noon on that day in the provided timezone.

	Args:
		tz (str, optional): The timezone to use. Defaults to "America/New_York".
		accept_blank (bool, optional): Whether an empty string returns None. Defaults to False.

	Returns:
		DateTime: Entered by user at noon, or None if empty string and accept_blank
	"""
	prompt = "Enter a date in format YYYY-MM-DD:"
	def caster(text):
		assert len(text) == 10
		return pendulum.parse(text + " 12:00:00", tz=tz)
	
	return input_get(caster, prompt, accept_blank=accept_blank)

def input_get_choice(choices, message="Choose one of the following:", accept_blank=False):
	"""Use the command line to make the user select an operation from a list.

	Args:
		choices (list): A list of strings, which should describe choices.
		message (str, optional): A message to print before the list of options
		accept_blank (bool, optional): Whether an empty string returns None. Defaults to False.

	Returns:
		int: The index of the operation that was chosen
	"""
	print(message)
	for ii, o in enumerate(choices):
		print("[" + str(ii + 1) + "] - " + str(o))

	while 1:
		resp = input("Enter a number between 1 and " + str(len(choices)) + ": ")
		if resp == "" and accept_blank:
			return None
		try:
			code = int(resp)
		except ValueError:
			print("Not a valid option.")
			continue
		if code > 0 and code < len(choices) + 1:
			return code - 1
		else:
			print("Not a valid option.")

def input_get_choices(choices, message="Choose multiple of the following:", accept_blank=False):
	"""Use the command line to make the user select multiple values from a list.

	Args:
		choices (list): A list of strings, which are operation descriptions
		message (str, optional): A message to print before the list of options
		accept_blank (bool, optional): If provided, allow an empty response to be taken as an empty list.

	Returns:
		list: Of indices chosen.
	"""
	print(message)
	for ii, o in enumerate(choices):
		print("[" + str(ii + 1) + "] - " + str(o))

	while 1:
		resp = input("Enter a comma-separated list of selections (e.g. '1, 4, 2'):")
		if resp == "" and accept_blank:
			return []
		try:
			vals = resp.split(",")
			codes = [(int(val) - 1) for val in vals]
		except ValueError:
			print("Input not parseable.")
			continue
		all_valid = True
		for code in codes:
			if code >= len(choices):
				print("Entry is too high: " + str(code + 1))
				all_valid = False
				break
		if all_valid: return codes

def input_get_enum(cls_enum, prompt=None, accept_blank=False):
	"""Select one type of Enum from the provided enum class.

	Args:
		cls_enum (Enum): The class definition of the enum to choose from
		prompt (str, optional): If provided, the prompt for the user. Defaults to None, which causes one to be
			automatically generated.
		accept_blank (bool, optional): Whether an empty response returns None. Defaults to False.

	Returns:
		Enum: Instance of the provided enum class or None if allowed.
	"""
	if prompt is None:
		prompt = "Select " + str(cls_enum.__name__)

	enum_names = [enum_instance.name for enum_instance in cls_enum]
	enum_name = enum_names[input_get_choice(enum_names, message=prompt, accept_blank=accept_blank)]
	if enum_name is None:
		return None
	return cls_enum[enum_name]

def input_get_enums(cls_enum, prompt=None, accept_blank=False) -> list:
	"""Select multiple types of Enum from the provided enum class.

	Args:
		cls_enum (Enum): The class definition of the enum to choose from
		prompt (str, optional): If provided, the prompt for the user. Defaults to None, which causes one to be
			automatically generated.
		accept_blank (bool, optional): Whether an empty response returns None. Defaults to False.

	Returns:
		list: A list of Enum instances
	"""
	if prompt is None:
		prompt = "Select " + str(cls_enum.__name__)

	enum_names = [enum_instance.name for enum_instance in cls_enum]
	codes_selected = input_get_choices(enum_names, message=prompt, accept_blank=accept_blank)
	enums_selected = []
	for code in codes_selected:
		enums_selected.append(cls_enum[enum_names[code]])
	return enums_selected

def input_get_multiline() -> 'list[str]':
	"""Prompt to get multiline input from the user. This will not include newlines.

	Returns:
		str: Complex str
	"""
	print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
	contents = []
	while True:
		try:
			line = input()
		except EOFError:
			break
		contents.append(line)
	return contents