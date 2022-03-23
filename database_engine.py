import sqlite3


class DatabaseEngine:
    def __init__(self, db):
        self.db_filename = db
        self.check_connection()

    def check_connection(self):
        with sqlite3.connect(self.db_filename) as conn:
            print(conn)
            print(f'You have successfully connected to {self.db_filename}')

    def execute_query(self, query, parameters=()):
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result


if __name__ == '__main__':
    db_filename = 'contacts.db'
    my_db = DatabaseEngine(db_filename)
