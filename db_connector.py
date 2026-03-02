import sqlite3

class database:

    def __init__(self):
        #define our database "buyhire.db"
        self.DBname = "buyhire_db.db"

        #create our database connection
    def connect (self):
        conn = None
        try:
            conn = sqlite3.connect(self.DBname)
        except Exception as e:
            print(e)
        return conn
    
    #execute a select query 
    def queryDB(self, command, params=[]):
        conn = self.connect()
        conn.row_factory = sqlite3.Row  
        cur = conn.cursor()
        cur.execute(command, params)
        result = cur.fetchall()
        self.disconnect(conn)
        return result

    #updating database - commit to our database
    def updateDB(self, command, params=[]):  
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(command, params)  
        conn.commit()
        self.disconnect(conn)  
        return None  
    
    def disconnect(self,conn):
        conn.close()
        