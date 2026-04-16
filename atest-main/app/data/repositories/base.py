from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    @abstractmethod
    def add(self, item: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, item_id: str) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    def update(self, item: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, item_id: str) -> None:
        raise NotImplementedError
