# hacutils/db.py
# Josh Reed 2024
#
# Utilities built around an squalchemy database. These classes currently server the needs of all the architectures
# that I've used them on, but will probably have to change in the future as I encounter increasingly diverse
# situations. I've never even used them outside of MySQL!

# Other libraries
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Base python
from contextlib import contextmanager
import os

class Database():

	def __init__(self, db_uri):
		"""Instantiate a database session/engine pair which can be used consistently to 
		interact with a database.

		Args:
			db_uri (String): the database string like 'mysql+pymysql://root:mysql_password@localhost/dbname'
		"""
		self.engine = create_engine(db_uri)

		self.Session = sessionmaker(bind=self.engine)

		self._session = None
		self._session_originator = None
		self._session_originator_pid = None
		self._memflag = None

	@property
	def session(self):
		if self._session is None:
			raise ValueError("Cannot use env.db.session outside of a session scope. Place this operation within "+\
				"'with db.session_scope():' block.")
		return self._session

	@property
	def database_name(self):
		"""
		Returns:
			str: The name of the database we are connected to
		"""
		return str(self.engine.url).split("/")[-1]

	@contextmanager
	def session_scope(self, originator:str=None):
		"""Provide a session scope around a series of transactions. This scope handles errors and other problems as
		well as ensuring a call to session.commit() is always fired at the end to close session/transaction scope.

		Be warned: If you call env.db.session.commit() within this scope, you will end the old transaction and
		start a new one.

		From the docs:
			The Session will begin a new transaction if it is used again, subsequent to the previous transaction
			ending from this it follows that the Session is capable of having a lifespan across many transactions,
			though only one at a time.

		This function yields session, which can be used. It also sets the env.db.session variable which can be
		used in the same way.

		Args:
			originator (str, optional): If provided, remember this string as the 'originator' of this session.
				Helpful when tracking certain problems through the system.
		"""
		if self._session is not None:
			msg = "Cannot start a new session scope within another session scope! "
			if self._session_originator is None:
				msg += "Previous originator unknown. "
			else:
				msg += "Previous originator: '" + str(self._session_originator) + "/" +\
					self._session_originator_pid + "'. "
				if originator is not None:
					msg += "Current originator: '" + str(originator) + "/" + str(os.getpid()) + "'. "
			raise ValueError(msg)

		self._session = self.Session()
		self._session_originator = originator
		self._session_originator_pid = str(os.getpid())
		try:
			self._session.commit()
			yield
			self._session.commit()
		except:
			self._session.rollback()
			raise
		finally:
			self._session.close()
			self._session = None

class DatabaseTesting(Database):
	"""A 'testing' database is just a little convenience wrapping for the classic Database object. It's intended
	to be pointed at a dedicated 'test' database which mirrors the project's real database, whatever that might
	be. It should be given a list of all table definitions that a project uses, so that it can create a brand
	new, clean DB for every time tests are run.

	It's best to instantiate such a database 
	"""

	def __init__(self, db_uri, all_table_defs):
		"""Instantiate a connection to the test database (which will be emptied).
		This database will be populated with the current state of the db_models models.

		Args:
			db_uri (str): The database URI
			all_table_defs (list): A list of Model Definitions (e.g. classes that extend declarative_base) to be
				dropped and re-added at the start of a run.
		"""
		super().__init__(db_uri)

		# Regenerate all tables.
		for tabledef in all_table_defs:
			try:
				print("Dropping table " + str(tabledef.__tablename__))
				tabledef.__table__.drop(self.engine)
			except OperationalError:
				print("Table " + str(tabledef) + " did not exist.")
			except:
				inspector = inspect(self.engine)
				table_names = inspector.get_table_names()
				print("Exception when trying to drop table " + str(tabledef.__tablename__))
				print("Check that an orphaned existing table is not causing this issue. Existing tables: " )
				for t in table_names:
					print(t)
				raise

		for tabledef in reversed(all_table_defs):
			print("Adding table " + str(tabledef.__tablename__))
			tabledef.metadata.create_all(self.engine)

		self.all_table_defs = all_table_defs

	@contextmanager
	def session_scope(self):
		"""This method differs from base Database method in that it will properly catch and handle integrity
		errors even when using pytest. This is actually a pretty tricky thing to do, and I don't fully understand
		it.

		It appears that, even though except: rollback() is the same here as in Database.session_scope(), it's
		not triggered properly or something if commit() is allowed to be called around the yield statement.

		If we wish to keep permanence with this scope, simply call commit() after adding stuff in your test
		fixture.
		"""
		if self._session is not None:
			raise ValueError("Cannot start a new session scope within another session scope!")
		
		session = self.Session()
		try:
			self._session = session
			yield session
		except:
			# Note that we don't actually catch exceptions from test functions here, due to the nature of pytest
			session.rollback()
			raise
		finally:
			session.rollback()
			session.close()
			self._session = None

	def teardown(self):
		"""Rollback all changes made to this test database.
		"""
		# Roll back the top level transaction and disconnect from the database
		#self.transaction.rollback()
		#self.connection.close()
		self.engine.dispose()