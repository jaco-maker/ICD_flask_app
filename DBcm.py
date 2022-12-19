import mysql.connector 

class ConnectionError(Exception):
    pass


class SQLError(Exception):
    pass


class UseDatabase:
    def __init__(self, config:dict) -> None:
        self.configuration = config
    
    def __enter__(self) -> 'cursor':
        """ __enter__ allows you to use your class the same way you would use with()"""
        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)
    
    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """defines code that will execute after your with() suite closes"""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)