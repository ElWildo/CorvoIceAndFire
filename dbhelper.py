import sqlite3

class DBHelper:
    def __init__(self,dbname="messagehandler.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        chtusrstmt = "CREATE TABLE IF NOT EXISTS chatuser (chatid text, owner text)"
        chatstmt = "CREATE INDEX IF NOT EXISTS itemIndex ON chatuser (chatid ASC)"
        ownstmt = "CREATE INDEX IF NOT EXISTS owmIndex ON chatuser (owner ASC)"
        msgtblstmt = "CREATE TABLE IF NOT EXISTS msgtable (sender text, receiver text, message text)"
        messagestmt = "CREATE INDEX IF NOT EXISTS itemIndex ON msgtable (message ASC)"
        self.conn.execute(chtusrstmt)
        self.conn.execute(chatstmt)
        self.conn.execute(ownstmt)
        self.conn.execute(msgtblstmt)
        self.conn.execute(messagestmt)
        self.conn.commit()
    
    def add_item_chat(self, chatid, owner):
        stmt = "INSERT INTO chatuser (chatid, owner) VALUES (?,?)"
        args = (chatid, owner,)
        self.conn.execute(stmt,args)
        self.conn.commit()

    def delete_item_chat(self, chatid, owner):
        stmt = "DELETE FROM chatuser WHERE chatid = (?) AND owner = (?)"
        args = (chatid, owner,)
        self.conn.execute(stmt,args)
        self.conn.commit()

    def get_user_chat(self, owner):
        stmt = "SELECT chatid FROM chatuser WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self.conn.execute(stmt, args)]
    
    def get_user_name(self, chatid):
        stmt = "SELECT owner FROM chatuser WHERE chatid = (?)"
        args = (chatid, )
        return [x[0] for x in self.conn.execute(stmt, args)]