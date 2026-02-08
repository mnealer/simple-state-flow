import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, Union, TypeVar, Generic, Coroutine
from pydantic import BaseModel
from src.nodes import START, END, Node, AsyncNode

T = TypeVar("T", bound=BaseModel)

class StateFlow(ABC, Generic[T]):
    """Standard synchronous state flow."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node[T]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Dict[str, str]] = {}
        self.setup_graph()

    @abstractmethod
    def setup_graph(self) -> None:
        """Override this method to add nodes and edges to the flow."""
        pass

    def add_node(self, name: str, node: Node[T]) -> None:
        """Add a node to the flow.

        Args:
            name: The name of the node.
            node: The Node instance to execute for this node.
        """
        self.nodes[name] = node

    def add_edge(self, start_node: str, end_node: str) -> None:
        """Add a directed edge between two nodes.

        Args:
            start_node: The name of the starting node.
            end_node: The name of the ending node.
        """
        self.edges[start_node] = end_node

    def add_conditional_edges(
        self,
        start_node: str,
        mapping: Dict[str, str]
    ) -> None:
        """Add conditional edges from a node.

        Args:
            start_node: The name of the starting node.
            mapping: A dictionary mapping node execution results to destination nodes.
        """
        self.conditional_edges[start_node] = mapping

    def run(self, state: T) -> T:
        """Run the flow starting from the START node.

        Args:
            state: The initial Pydantic state object.

        Returns:
            The final state object.
        """
        current_node = START
        
        while current_node != END:
            # Determine next node
            if current_node == START:
                next_node = self.edges.get(START)
                if not next_node:
                    raise ValueError("START node must have an outgoing edge.")
                current_node = next_node
                continue

            # Execute current node action
            if current_node not in self.nodes:
                raise ValueError(f"Node {current_node} not found in flow.")
            
            state, result = self.nodes[current_node].run(state)

            # Check for conditional edges first
            if current_node in self.conditional_edges:
                mapping = self.conditional_edges[current_node]
                if result in mapping:
                    current_node = mapping[result]
                elif current_node in self.edges:
                    current_node = self.edges[current_node]
                else:
                    raise ValueError(f"Result '{result}' not found in mapping for node {current_node} and no default edge found.")
            # Check for regular edges
            elif current_node in self.edges:
                current_node = self.edges[current_node]
            else:
                if current_node != END:
                    raise ValueError(f"Node {current_node} has no outgoing edges and is not END.")

        return state

class AsyncStateFlow(ABC, Generic[T]):
    """Asynchronous state flow that only accepts async nodes."""

    def __init__(self) -> None:
        self.nodes: Dict[str, AsyncNode[T]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Dict[str, str]] = {}
        self._setup_graph()

    @abstractmethod
    def _setup_graph(self) -> None:
        """Override this method to add nodes and edges to the flow."""
        pass

    def add_node(self, name: str, node: AsyncNode[T]) -> None:
        """Add an async node to the flow.

        Args:
            name: The name of the node.
            node: The AsyncNode instance to execute for this node.
        """
        self.nodes[name] = node

    def add_edge(self, start_node: str, end_node: str) -> None:
        """Add a directed edge between two nodes.

        Args:
            start_node: The name of the starting node.
            end_node: The name of the ending node.
        """
        self.edges[start_node] = end_node

    def add_conditional_edges(
        self,
        start_node: str,
        mapping: Dict[str, str]
    ) -> None:
        """Add conditional edges from a node.

        Args:
            start_node: The name of the starting node.
            mapping: A dictionary mapping node execution results to destination nodes.
        """
        self.conditional_edges[start_node] = mapping

    async def run(self, state: T) -> T:
        """Run the flow starting from the START node.

        Args:
            state: The initial Pydantic state object.

        Returns:
            The final state object.
        """
        current_node = START
        
        while current_node != END:
            # Determine next node
            if current_node == START:
                next_node = self.edges.get(START)
                if not next_node:
                    raise ValueError("START node must have an outgoing edge.")
                current_node = next_node
                continue

            # Execute current node action
            if current_node not in self.nodes:
                raise ValueError(f"Node {current_node} not found in flow.")
            
            state, result = await self.nodes[current_node].run(state)

            # Check for conditional edges first
            if current_node in self.conditional_edges:
                mapping = self.conditional_edges[current_node]
                if result in mapping:
                    current_node = mapping[result]
                elif current_node in self.edges:
                    current_node = self.edges[current_node]
                else:
                    raise ValueError(f"Result '{result}' not found in mapping for node {current_node} and no default edge found.")
            # Check for regular edges
            elif current_node in self.edges:
                current_node = self.edges[current_node]
            else:
                if current_node != END:
                    raise ValueError(f"Node {current_node} has no outgoing edges and is not END.")

        return state
