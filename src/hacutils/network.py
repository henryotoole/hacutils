# hacutils/network.py
# Josh Reed 201X 2020 2021 2022 2023 2024
#
# Basic code to handle network requests.

# Other libs
import requests

def get_json(url, data, files={}, timeout=60, method='post'):
	"""This is a sort of quick and simple method I've been using for effectively my entire adult life. It's
	great for just fetching a JSON from a URL, like the method says. In the long term, this method is usually
	superceded by some more elegant and specialized function, but it's great for the early stages of projects.
	
	Send a post request to get a JSON from some url. Unfortunately this will just block until something returns
	or the request times out.
	
	Raises:
		requests.exceptions.ConnectTimeout
		requests.exceptions.ConnectionError

	Args:
		url (String): The absolute url at which to place this request
		data (Dict): A dictionary of key/value pairs to be sent to the server. All keys and values will be stringified
		files (dict, optional): Files to be sent with the request. Defaults to {}.
		timeout (Integer, optional): The timeout for a request in seconds. Defaults to 60
		method (String, optional): The requets method ('post' or 'get'). Defaults to 'post'

	Returns:
		Tuple: status_code, response_data e.g.    
			404, "File not found" or perhaps
			200, {'json_key', 1} <--- note that this is an actual dict, not a string.

	"""
	if method is 'post':
		r = requests.post(url, data=data, files=files, timeout=timeout)
	else:
		r = requests.get(url, params=data, files=files, timeout=timeout)
	
	if(r.status_code != 200):
		print("Request Error <" + str(r.status_code) + "> - Debug Info: '" + r.text + "'")
		return r.status_code, None # Return the status code and None to signify it wasn't a 200
	try:
		return 200, r.json() # Return the JSON and the 200 code
	except ValueError as e:
		return 200, None # No JSON parseable, but we still got a 200
	return None, None # Connection timed out, so no code or JSON