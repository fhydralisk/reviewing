from django.db.backends.mysql.operations import DatabaseOperations


class MySQLOperations(DatabaseOperations):

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        if lookup_type in {'week', 'weekend'}:
            field_name, params = self._convert_field_to_tz(field_name, tzname)
            format_str = '%%Y-%%m-%%d 00:00:00'
            sql_cast = "CAST(DATE_FORMAT(%s, '%s') AS DATETIME)" % (field_name, format_str)
            if lookup_type == 'week':
                sql = 'DATE_SUB({tf}, INTERVAL(WEEKDAY({tf})) DAY)'.format(tf=sql_cast)
            else:
                sql = 'DATE_SUB(DATE_ADD({tf}, INTERVAL(7-WEEKDAY({tf})) DAY), {mils})'.format(
                    tf=sql_cast, mils=self.format_for_duration_arithmetic('1')
                )

            # Double timezone params in sql expression.
            return sql, params + params
        else:
            return super(MySQLOperations, self).datetime_trunc_sql(lookup_type, field_name, tzname)
