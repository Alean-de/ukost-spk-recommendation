from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Allow Django to work seamlessly with MariaDB 10.4.x (standard XAMPP MariaDB)
DatabaseWrapper.check_database_version_supported = lambda self: None
DatabaseFeatures.can_return_columns_from_insert = property(
    lambda self: self.connection.mysql_is_mariadb and self.connection.mysql_version >= (10, 5, 0)
)
DatabaseFeatures.can_return_rows_from_bulk_insert = property(
    lambda self: self.connection.mysql_is_mariadb and self.connection.mysql_version >= (10, 5, 0)
)