from collections.abc import ItemsView
from pathlib import Path
from typing import Any

from utils.file_utils import load_json_file, save_json_file


class Cache:
    def __init__(self, path: str, filename: str) -> None:
        self.filepath = str(Path(path) / f"{filename}.json")
        self.data: dict = {}
        self.load()

    def load(self) -> None:
        if Path(self.filepath).exists():
            self.data = {
                int(key): value for key, value in load_json_file(self.filepath).items()
            }
        else:
            self.data = {}

    def get(self, key: int) -> Any | None:
        return self.data.get(key)

    def add(self, key: int, value: Any) -> None:
        self.data[key] = value

    def remove(self, key: int) -> None:
        if key in self.data:
            del self.data[key]

    def save(self) -> None:
        save_json_file(self.filepath, self.data)

    def items(self) -> ItemsView[int, Any]:
        return self.data.items()

    def __contains__(self, key: int) -> bool:
        return key in self.data

    def __iter__(self):
        return iter(self.data)
