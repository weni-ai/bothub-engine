from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FileResponseDTO:
    status: int = None
    file_url: str = None
    err: str = None
    file_name: str = None


class FileDataBase(ABC):

    @abstractmethod
    def add_file(file) -> FileResponseDTO:
        ...
