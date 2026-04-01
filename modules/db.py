import sqlite3


def get_connection():
    connection = sqlite3.connect("game_database.db")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection

def execute(sql, parameters=[]):
    connection = get_connection()
    try:
        if type(sql)==str:
            connection.execute(sql, parameters)

        elif type(sql)==list:
            
            cursor=connection.cursor()
            
            cursor.execute("BEGIN TRANSACTION")
            
            for statement,parameter in zip(sql,parameters):
                print(statement,parameter)
                cursor.execute(statement,parameter)
                
        connection.commit()
        return "success"
            
    except sqlite3.Error as error:
        return error
    finally:
        connection.close()

    
def query(sql, parameters=[]):
    connection = get_connection()
    result = connection.execute(sql, parameters).fetchall()
    connection.close()
    return result