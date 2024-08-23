from copy import deepcopy
from typing import List, Generic, TypeVar

T = TypeVar("T")

class Queue(Generic[T]):
    def __init__(self):
        self.queue: List[T] = []

    # Put an item into the queue.
    def put(self, item: T):
        self.queue.append(item)

    # Remove and return an item from the queue.
    def get(self):
        return self.queue.pop(0)

    def empty(self):
        return len(self.queue) == 0

    @property
    def skim_content(self):
        return deepcopy(self.queue)

    