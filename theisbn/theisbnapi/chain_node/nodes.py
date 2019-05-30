#from __future__ import annotations
from theisbnapi.models import ISBN

from abc import ABC, abstractmethod

class Node(ABC):

    @abstractmethod
    def next(self, no : 'Node') -> 'Node':
        pass

    @abstractmethod
    def search(self, parametros):
        pass


class AbstractNode(Node):

    _next: Node = None

    def next(self, no: Node) -> Node:
        self._next = no
        return no

    @abstractmethod
    def search(self, request) -> str:
        if self._next:
            return self._next.search(request)

        return None


class LocalNode(AbstractNode):

    def search(self, request) -> str:
        print('chego')
        try:
            query = ISBN.objects.get(isbn13=request)
        except ISBN.DoesNotExist:
            return {"status":"erro"}


def chain():
    chain = LocalNode()
    return chain