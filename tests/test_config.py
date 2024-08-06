# tests/test_config.py
# Josh Reed 2024

# Project code
from hacutils import load_config, CfgEntry, find_config, defaults_apply
from hacutils.config import _generate_from_defaults

# Other libs
import pytest

# Base python
import os
import pathlib


@pytest.fixture()
def config_path():
	
	return os.path.join(pathlib.Path(__file__).parent.resolve(), "resources", "config.cfg")

def test_load_config(config_path):

	cfg = load_config(config_path)
	
	assert cfg['CONFIG_KEY'] == 'CONFIG_VALUE'
	assert cfg['CONFIG_KEY_2'] == 2
	assert cfg['CONFIG_PATH'] == 'THISTHAT'
	assert cfg['CONFIG_PATH_2'] == 'THISTHAT/OTHER'
	assert cfg['KEY_BOOLEAN'] == True
	assert cfg['CONFIG_SUBDICT'] == {'KEY': 'VALUE', 'KEY2': 'VALUE2'}
	assert not 'lower' in cfg

def test_generate_from_defaults():
	
	comp = {
		'key_1': [1, 2, 3, 4, 5],
		'key_2': "A long ish string",
		'key_3': True,
		'key_4': {
			'subkey_1': [True, False, None]
		}
	}

	defaults = [
		CfgEntry("MKEY1", "A string", "A comment"),
		CfgEntry("MKEY2", default=None, comment="Manually enable"),
		CfgEntry("MKEY3", True),
		CfgEntry("MKEY4", comp)
	]
	header = "This is a sample config file with a header that runs into many lines. I hope that this while " + \
	"library business does not wind up being a waste of time. I am very much enjoying writing all this code " + \
	"at least. It feels good to create at will again."

	cfg_str = _generate_from_defaults(defaults, header=header)
	
	with open(os.path.join(pathlib.Path(__file__).parent.resolve(), "resources", "gen_config.cfg"), 'r') as ffile:
		assert cfg_str == ffile.read()

	# Check without header
	_generate_from_defaults(defaults, header=None)

def test_defaults_apply(config_path):

	cfg = load_config(config_path)

	defaults = [
		CfgEntry("CONFIG_KEY", "A string"), # Won't overwrite
		CfgEntry("CONFIG_KEY_NONEXIST", "FFFF"), # Will overwrite
		CfgEntry("CONFIG_KEY_2", None), # Won't complain
	]
	defaults_apply(cfg, defaults)
	
	assert cfg['CONFIG_KEY'] == 'CONFIG_VALUE'
	assert cfg['CONFIG_KEY_NONEXIST'] == 'FFFF'
	assert cfg['CONFIG_KEY_2'] == 2

	with pytest.raises(Exception):
		defaults_apply(cfg, [CfgEntry("DOES_NOT_EXIST", None)])

def test_find_config():
	
	module_path = pathlib.Path(__file__).parent.parent.resolve()

	# Silly little sanity check for paths.
	try:
		find_config(module_path, 'TEST')
	except Exception as e:
		assert 'hacutils/dev/TEST.cfg' in str(e)
		assert '/etc/TEST.cfg' in str(e)

	# Now ensure it can actually return
	module_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "resources")
	assert 'hacutils/tests/resources/dev/TEST.cfg' in find_config(module_path, 'TEST')