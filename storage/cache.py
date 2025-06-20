from pathlib import Path
from typing import Any, ItemsView

from utils.file_utils import load_json_file, save_json_file


class Cache:
    def __init__(self, path: str, filename: str) -> None:
        self.filepath = str(Path(path) / f"{filename}.json")
        self.data: dict = {}
        self.load()

    def load(self) -> None:
        if Path(self.filepath).exists():
            self.data = load_json_file(self.filepath)
        else:
            self.data = {}

    def get(self, key: int) -> dict | None:
        return self.data.get(key)

    def add(self, key: int, value: dict) -> None:
        self.data[key] = value

    def remove(self, key: int) -> None:
        if key in self.data:
            del self.data[key]

    def save(self) -> None:
        save_json_file(self.filepath, self.data)

    def items(self) -> ItemsView[Any, Any]:
        return self.data.items()

    def __contains__(self, key: int) -> bool:
        return key in self.data

    def __iter__(self):
        return iter(self.data)
