import pg8000
import logging

class PostgresHelper:
    def __init__(self):
        self.__cursors = {}
        self.__db = None

    def test_connection (self):
        logging.getLogger(__name__).debug("Testing connection")
        cur = self.__get_cursor('test_cursor')
        cur.execute("SELECT 1")
        result = cur.fetchone()[0]
        success = False
        if result == 1:
            success = True
        self.__close_cursor('test_cursor')

        return success

    def get_cursor (self, cursor_name):
        if cursor_name in self.__cursors:
            return self.__cursors[cursor_name]

        self.__cursors[cursor_name] = self.__get_connection().cursor()
        return self.__cursors[cursor_name]

    def close_cursor (self, cursor_name):
        if cursor_name in self.__cursors:
            self.__cursors[cursor_name].close()
            del self.__cursors[cursor_name]

    def cleanup (self):
        # close any open cursors
        for cursor in [*self.__cursors]:
            self.close_cursor(cursor)

        if self.__db is not None:
            self.__db.close()
            self.__db = None

    def commit (self):
        self.__get_connection().commit()

    def get_connection (self):
        return self.__get_connection()

    def __get_connection (self):
        if self.__db is None:
            try:
                self.__db = pg8000.connect(user='matt', database='navigation', unix_sock='/var/run/postgresql/.s.PGSQL.5432')
            except Exception as e:
                self.__db = pg8000.connect(
                    user='mattcalhoun',
                    host='localhost',
                    database='mattcalhoun',
                    password=None,
                    port = 5432
                )
            self.__db.autocommit = False
        return self.__db