from tinydb import TinyDB, Query
import uuid


class Database:
    def __init__(self, db_path='db.json'):
        self.db = TinyDB(db_path)

    def create_session(self):
        # Create a new table for the session
        session_id = str(uuid.uuid4())
        session = self.db.table(session_id)
        return session.name

    def insert_chat(self, session_id, content):
        session = self.db.table(session_id)
        session.insert({'content': content})

    def get_all_chats(self, session_id):
        session = self.db.table(session_id)
        return [c["content"] for c in session.all()]

    def get_all_sessions(self):
        return self.db.tables()

    def delete_session(self, session_id):
        self.db.drop_table(session_id)
