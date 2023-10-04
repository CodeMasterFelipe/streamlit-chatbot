from tinydb import TinyDB, Query, where
import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionMetadata(BaseModel):
    session_id: str
    session_name: str
    creation_date: str = str(datetime.now())
    modified_date: str = str(datetime.now())


class Database:
    def __init__(self, db_path='db/db.json', character_path='db/character_db.json'):
        self.db = TinyDB(db_path)
        self.metadata = self.db.table("metadata")
        self.characters_db = TinyDB(character_path)

    # === Chat Sessions Methods ===
    def create_session(self):
        # Create a new table for the session
        session_id = str(uuid.uuid4())
        session = self.db.table(session_id)
        self.metadata.insert(SessionMetadata(
            session_id=session_id, session_name=session_id).model_dump())
        # session.insert({'session_name': session_name})
        return session.name

    def set_session_name(self, session_id, session_name):
        print(">>>> ", session_name)
        self.db.table("metadata").update({'session_name': session_name},
                                         where('session_id') == session_id)

    def insert_chat(self, session_id, content):
        session = self.db.table(session_id)
        session.insert({'content': content})

    def get_all_chats(self, session_id):
        session = self.db.table(session_id)
        return [c["content"] for c in session.all()]

    # def get_all_sessions(self):
    #     return self.db.tables()
    def get_all_sessions(self):
        return self.db.table("metadata").all()

    # def get_all_sessions(self):
    #     return [{'name': table.get().get('session_name'), 'id': table.name} for table in self.db.tables()]

    def delete_session(self, session_id):
        self.metadata.remove(where('session_id') == session_id)
        self.db.drop_table(session_id)

    # === Character Methods ===
    def insert_character(self, character_info):
        self.characters_db.insert(character_info)

    def get_all_characters(self):
        characters = [c["name"] for c in self.characters_db.all()]
        return characters

    def get_character(self, character_name):
        Character = Query()
        char_info = self.characters_db.get(Character.name == character_name)
        return char_info if char_info else {
            "name": "Assistant",
            "system_prompt": "You are a helpful Assistant",
            "temperature": 0.75
        }

    def update_character(self, updated_info):
        Character = Query()
        self.characters_db.update(
            updated_info, Character.name == updated_info["name"])

    def delete_character(self, character_name):
        Character = Query()
        self.characters_db.remove(Character.name == character_name)
