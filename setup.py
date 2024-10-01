# hacutils/setup.py
# Josh Reed 2024

from setuptools import setup, find_packages
import os
import glob

# Changelog
# 0.0.1
#	This was the base creation of this utility
# 0.0.2
#	This adds the flask_test_server and tests for that test server.
# 0.1.0
# 	Improved setup.py
# 0.2.0
#	Changeover from henryotoole_utils to hacutils. This is a major change, dropping some old things
#	and adding a great many new things.
# 0.2.1
#	Fix a bug with config.generate_from_defaults and fix install_requires in setup.py
# 0.2.2
#	Add nginx directory checks
# 0.2.3
#	Change nature of imports
# 0.2.4
#	Rework db classes

# Lessons from https://blog.ionelmc.ro/2014/05/25/python-packaging/

setup(
	# This is NOT the module name e.g. 'import hacutils'. This is the library name as
	# it would appear in pip etc.
	name='hacutils',
	version='0.2.4',
	license="GNUv3",
	description="Personal utility library. Short for Henryotoole's Ars Commoditas.",
	author='Josh Reed (henryotoole)',
	url='https://github.com/henryotoole/hacutils',
	packages=find_packages('src'),
	package_dir={'': 'src'},
	py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob('src/*.py')],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"pendulum",
		"requests",
		"SQLAlchemy"
	],
	classifiers=[
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
	]
)