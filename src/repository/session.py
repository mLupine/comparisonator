import json
import os
from dataclasses import asdict
from typing import Optional

from dacite import from_dict

from src.entity.item import Item
from src.entity.session import Session
from src.error import AppError
from src.utils import Utils


class SessionRepository:
    def __init__(self):
        self.storage_dir = os.path.join(Utils().session_dir, "sessions")
        os.makedirs(self.storage_dir, exist_ok=True)

    def list_sessions(self) -> list[Session]:
        return [self.load_session(sid) for sid in os.listdir(self.storage_dir)]

    def load_session(self, session_id: str) -> Optional[Session]:
        session_path = os.path.join(self.storage_dir, session_id)
        if not os.path.isfile(session_path):
            return None

        with open(session_path) as f:
            return from_dict(data_class=Session, data=json.load(f))

    def save_session(self, session: Session) -> None:
        session_path = os.path.join(self.storage_dir, session.id)
        with open(session_path, "w") as f:
            json.dump(asdict(session), f)

    def delete_session(self, session_id: str) -> None:
        session_path = os.path.join(self.storage_dir, session_id)
        if not os.path.isfile(session_path):
            raise AppError(f"Session '{session_id}' does not exist")

        os.remove(session_path)

    def delete_all_sessions(self) -> None:
        for session_id in os.listdir(self.storage_dir):
            self.delete_session(session_id)

    @staticmethod
    def load_items_from_file(path: str) -> list[Item]:
        if not os.path.isfile(path):
            raise AppError(f"Path '{path}' is not valid")

        with open(path) as f:
            return [Item(name=line.strip()) for line in f.readlines()]
