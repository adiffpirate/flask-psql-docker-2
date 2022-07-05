import psycopg2 as psql
import os


# Config access to database
class Config:
    def __init__(self):
        self.config = {
            'postgres' : {
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'database': os.getenv('DB_DATABASE'),
                'host': os.getenv('DB_HOST'),
                'port': os.getenv('DB_PORT')
            }
        }


# Create connector class responsible for handle database operations
class Connector(Config):
    def __init__(self):
        Config.__init__(self)
        try:
            self.conn = psql.connect(**self.config['postgres'])
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.info('Erro na conexão ao database', e)
            exit(1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        return self.cur

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def fetchall(self):
        return self.cursor.fetchall()

    def execute(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            affected_rows_count = self.cursor.rowcount
            self.commit()
            return affected_rows_count
        except:
            self.rollback()

    def query(self, sql, params=None):
        try:
            self.cursor.execute(sql, params or ())
            content = self.fetchall()
            self.commit()
            return content
        except:
            self.rollback()
