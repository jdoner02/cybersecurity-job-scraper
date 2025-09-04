from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from ..models import Job, Query


class JobsClient(ABC):
    @abstractmethod
    def search(self, query: Query) -> Iterator[Job]:  # pragma: no cover - interface only
        raise NotImplementedError
