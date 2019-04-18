from django.db.backends.mysql.base import (
    DatabaseWrapper as MySQLDatabaseWrapper,
)

from .operations import MySQLOperations


class DatabaseWrapper(MySQLDatabaseWrapper):
    ops_class = MySQLOperations
