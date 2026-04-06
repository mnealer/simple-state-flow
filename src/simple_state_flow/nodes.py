from abc import ABC, abstractmethod
from typing import Tuple, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

START = "__start__"
END = "__end__"

class Node(ABC, Generic[T]):
    """Abstract base class for synchronous nodes."""

    def __init__(self) -> None:
        self.state: T = None  # type: ignore
        self.result: str = "done"

    @abstractmethod
    def exec(self) -> None:
        """Execute the node's logic.

        This method MUST be overridden by subclasses to implement the node's specific behavior.
        The current state is available as `self.state`.
        To define the path for conditional edges, set `self.result` to the desired outcome string.
        By default, `self.result` is set to "done".
        """
        pass

    def _pre_run(self, state: T) -> None:
        """Internal method to set the state before execution.

        Args:
            state: The current state object.

        Raises:
            TypeError: If state is not a Pydantic BaseModel.
        """
        if not isinstance(state, BaseModel):
            raise TypeError("State must be a Pydantic BaseModel.")
        self.state = state
        self.result = "done"

    def _post_run(self, state: T, result: str) -> None:
        """Internal method to update the state after execution.

        Args:
            state: The updated state object.
            result: The execution result.
        """
        if state is not None:
            self.state = state
        if result is not None:
            self.result = result

    def _run(self, state: T) -> Tuple[T, str]:
        """Internal method to execute the node.

        Args:
            state: The current state object.

        Returns:
            A tuple of (updated state, next status).
        """
        self._pre_run(state)
        self.exec()
        return self.state, self.result

class AsyncNode(ABC, Generic[T]):
    """Abstract base class for asynchronous nodes."""

    def __init__(self) -> None:
        self.state: T = None  # type: ignore
        self.result: str = "done"

    @abstractmethod
    async def exec(self) -> None:
        """Execute the node's logic asynchronously.

        This method MUST be overridden by subclasses to implement the node's specific behavior.
        The current state is available as `self.state`.
        To define the path for conditional edges, set `self.result` to the desired outcome string.
        By default, `self.result` is set to "done".
        """
        pass

    def _pre_run(self, state: T) -> None:
        """Internal method to set the state before execution.

        Args:
            state: The current state object.

        Raises:
            TypeError: If state is not a Pydantic BaseModel.
        """
        if not isinstance(state, BaseModel):
            raise TypeError("State must be a Pydantic BaseModel.")
        self.state = state
        self.result = "done"

    async def _run(self, state: T) -> Tuple[T, str]:
        """Internal method to execute the node.

        Args:
            state: The current state object.

        Returns:
            A tuple of (updated state, next status).
        """
        self._pre_run(state)
        await self.exec()
        return self.state, self.result
