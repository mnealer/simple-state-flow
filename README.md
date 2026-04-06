# Simple State Flow

`simple-state-flow` is a lightweight, graph-based workflow orchestrator for Python. It allows you to define complex, stateful workflows using Pydantic models for state management and a simple node-based architecture for execution logic.

The library is inspired by LangGraph's StateGraph but focuses on class-based nodes and strict Pydantic enforcement. It supports both synchronous and asynchronous execution, circular flows (loops), and dynamic routing via conditional edges.

## Features

- **Pydantic-First**: All state objects must be Pydantic `BaseModel` instances, ensuring type safety and automatic validation.
- **Class-Based Nodes**: Encapsulate logic within `Node` or `AsyncNode` classes for better organization and reusability.
- **Flexible Routing**: Define standard edges for linear flows or conditional edges for complex branching logic.
- **Async Support**: Native support for `asyncio` with `AsyncStateFlow` and `AsyncNode`.
- **Mermaid Export**: Automatically generate Mermaid diagrams from your flow definitions for documentation and visualization.

## Installation

This project uses `uv` for dependency management.

```bash
uv add simple-state-flow
```

Or with pip:

```bash
pip install simple-state-flow
```

## Core Concepts

### 1. The State
The state is a Pydantic `BaseModel` that stores all data passed between nodes. It is validated at every step of the workflow.

```python
from pydantic import BaseModel, Field
from typing import List

class MyState(BaseModel):
    count: int = 0
    history: List[str] = Field(default_factory=list)
```

### 2. Nodes
Nodes represent individual tasks. You define them by inheriting from `Node` (sync) or `AsyncNode` (async) and implementing the `exec` method. Access the state via `self.state` and set the next path via `self.result`.

```python
from simple_state_flow import Node

class IncrementNode(Node[MyState]):
    def exec(self) -> None:
        self.state.count += 1
        self.state.history.append(f"Incremented to {self.state.count}")
        
        # 'result' determines which conditional edge to follow
        if self.state.count < 5:
            self.result = "continue"
        else:
            self.result = "finished"
```

### 3. Flows
Flows define the graph structure. Inherit from `StateFlow` (sync) or `AsyncStateFlow` (async) and override `setup_graph`.

```python
from simple_state_flow import StateFlow, START, END

class MyFlow(StateFlow[MyState]):
    def setup_graph(self) -> None:
        self.add_node("increment", IncrementNode())
        
        # Connect START to the first node
        self.add_edge(START, "increment")
        
        # Conditional logic: Loop back or finish
        self.add_conditional_edges("increment", {
            "continue": "increment",
            "finished": END
        })
```

## Usage Examples

### Synchronous Execution

```python
flow = MyFlow()
final_state = flow.run(MyState())
print(f"Final Count: {final_state.count}")
# Output: Final Count: 5
```

### Asynchronous Execution

```python
import asyncio
from simple_state_flow import AsyncStateFlow, AsyncNode, START, END

class AsyncWorker(AsyncNode[MyState]):
    async def exec(self) -> None:
        await asyncio.sleep(0.1)
        self.state.history.append("Async Work Done")

class MyAsyncFlow(AsyncStateFlow[MyState]):
    def setup_graph(self) -> None:
        self.add_node("worker", AsyncWorker())
        self.add_edge(START, "worker")
        self.add_edge("worker", END)

async def main():
    flow = MyAsyncFlow()
    state = await flow.run(MyState())
    print(state.history)

asyncio.run(main())
```

### Visualizing the Flow
You can export your flow as a Mermaid diagram:

```python
flow = MyFlow()
mermaid_str = flow.to_mermaid()
print(mermaid_str)

# Or save directly to a file
flow.save_mermaid("flow_chart.mmd")
```

## Why simple-state-flow?

- **Simplicity**: No complex configuration; just classes and methods.
- **Validation**: Pydantic ensures your state is always valid before any node processes it.
- **Traceability**: The state object can accumulate logs or history, making it easy to debug complex flows.
- **Scalability**: Split large business processes into small, testable nodes.

For more detailed use cases, see [src/simple_state_flow/examples/README.md](src/simple_state_flow/examples/README.md).
