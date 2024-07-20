import logging
from typing import TypeAlias

_Level: TypeAlias = int | str


class DashLogger(logging.Logger):
    def __init__(self, name: str, level: _Level = 0) -> None:
        super().__init__(name, level)
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler("file.log")
        c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        f_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)
        self.addHandler(c_handler)
        self.addHandler(f_handler)
