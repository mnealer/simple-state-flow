import asyncio
import random
from typing import List
from pydantic import BaseModel, Field
from simple_state_flow.nodes import AsyncNode, START, END
from simple_state_flow.flows import AsyncStateFlow

class AsyncFlowState(BaseModel):
    history: List[str] = Field(default_factory=list)

class AsyncNodeA(AsyncNode):
    async def exec(self) -> None:
        await asyncio.sleep(0.01)
        self.state.history.append("A")

class AsyncNodeB(AsyncNode):
    async def exec(self) -> None:
        await asyncio.sleep(0.01)
        self.state.history.append("B")
        self.result = random.choice(["to_c", "to_d"])

class AsyncNodeC(AsyncNode):
    async def exec(self) -> None:
        await asyncio.sleep(0.01)
        self.state.history.append("C")

class AsyncNodeD(AsyncNode):
    async def exec(self) -> None:
        await asyncio.sleep(0.01)
        self.state.history.append("D")

class SimpleAsyncFlow(AsyncStateFlow[AsyncFlowState]):
    def _setup_graph(self) -> None:
        self.add_node("A", AsyncNodeA())
        self.add_node("B", AsyncNodeB())
        self.add_node("C", AsyncNodeC())
        self.add_node("D", AsyncNodeD())
        
        self.add_edge(START, "A")
        self.add_edge("A", "B")
        self.add_conditional_edges("B", {"to_c": "C", "to_d": "D"})
        self.add_edge("C", END)
        self.add_edge("D", END)


async def test_async_flow():
    flow = SimpleAsyncFlow()
    
    seen_c = False
    seen_d = False
    
    for _ in range(100):
        state = AsyncFlowState()
        final_state = await flow.run(state)
        
        assert final_state.history[0] == "A"
        assert final_state.history[1] == "B"
        
        last_node = final_state.history[2]
        assert last_node in ["C", "D"]
        
        if last_node == "C":
            seen_c = True
        if last_node == "D":
            seen_d = True

    assert seen_c, "Node C was never reached"
    assert seen_d, "Node D was never reached"
    print(f"Async flow history: {final_state.history}")

if __name__ == "__main__":
    asyncio.run(test_async_flow())
