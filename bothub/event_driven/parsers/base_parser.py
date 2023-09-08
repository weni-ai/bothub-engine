from abc import ABC, abstractstaticmethod


class BaseParser(ABC):  # pragma: no cover
    @abstractstaticmethod
    def parse(stream, encoding=None):
        pass
