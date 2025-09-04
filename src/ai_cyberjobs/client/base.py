from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from ..models import Job
from ..models import Query


class JobsClient(ABC):
    @abstractmethod
    def search(self, query: Query) -> Iterator[Job]:  # pragma: no cover - interface only
        raise NotImplementedError

