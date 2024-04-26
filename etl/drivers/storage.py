import json
from typing import Any, Dict


class JsonFileStorage:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, 'w') as state_file:
            json.dump(state, state_file)

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        try:
            with open(self.file_path, 'r') as state_file:
                return json.load(state_file)
        except FileNotFoundError:
            return dict()
