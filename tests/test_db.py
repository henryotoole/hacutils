# tests/test_db.py
# Josh Reed 2024
#
# Tests for the database utilities

# Our code
from hacutils.db import Database, DatabaseTesting
from hacutils.filesys import mkdirs

# Other libs
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

# Base python
import os
import pathlib


# Setup sample database classes

ModelSQLAlchemyBase = declarative_base()

class ModelA(ModelSQLAlchemyBase):

	__tablename__ = 'tablea'

	id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
	rec = sa.Column(sa.Text(16))

	def __init__(self, rec):
		self.rec = rec

class ModelB(ModelSQLAlchemyBase):

	__tablename__ = 'tableb'

	id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
	rec = sa.Column(sa.Text(16))

	def __init__(self, rec):
		self.rec = rec


@pytest.fixture
def db_sqlite_test(fpath_dev):
	path = os.path.join(fpath_dev, "db_test.db")
	mkdirs(path)
	return "sqlite:///" + path

@pytest.fixture
def db_sqlite_main(fpath_dev):
	path = os.path.join(fpath_dev, "db_main.db")
	mkdirs(path)
	return "sqlite:///" + path

def test_main_db(db_sqlite_main):
	"""These tests are a bit confusing. Here we are testing the non-test Database class. It's the more important
	one, as it actually gets used by data that's important.

	The test below is almost trivial. More tests will be needed when I one day read the SQLAlchemy docs
	cover-to-cover and presumably revise much of this.
	"""

	db = Database(db_sqlite_main)

	# Annoyingly, since we are testing the real database, I must mirror the teardown / setup code
	for tabledef in [ModelA, ModelB]:
		try:
			tabledef.__table__.drop(db.engine)
		except:
			pass
	for tabledef in reversed([ModelA, ModelB]):
		try:
			tabledef.metadata.create_all(db.engine)
		except:
			pass

	with db.session_scope():

		assert len(db.session.query(ModelB).all()) == 0

		mb = ModelB("first_entry")
		db.session.add(mb)
		db.session.flush()

	with db.session_scope():
		assert len(db.session.query(ModelB).all()) == 1

def test_test_db(db_sqlite_test):

	# Ensure the connection actually works.
	db = DatabaseTesting(db_sqlite_test, ModelSQLAlchemyBase)