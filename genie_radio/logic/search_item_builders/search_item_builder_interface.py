from abc import ABC, abstractmethod
from typing import Optional

from spotipyio import SearchItem


class ISearchItemBuilder(ABC):
    @abstractmethod
    async def build(self, recognition_output: dict) -> Optional[SearchItem]:
        raise NotImplementedError
