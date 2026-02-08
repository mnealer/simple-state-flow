import random
from typing import List
from pydantic import BaseModel, Field
from state_flow.nodes import Node, START, END
from state_flow.flows import StateFlow



class FlowState(BaseModel):
    history: List[str] = Field(default_factory=list)

class NodeA(Node):
    def exec(self, state: FlowState) -> None:
        state.history.append("A")

class NodeB(Node):
    def exec(self, state: FlowState) -> None:
        state.history.append("B")
        self.result = random.choice(["to_c", "to_d"])

class NodeC(Node):
    def exec(self, state: FlowState) -> None:
        state.history.append("C")

class NodeD(Node):
    def exec(self, state: FlowState) -> None:
        state.history.append("D")

class RandomFlow(StateFlow[FlowState]):
    def setup_graph(self) -> None:
        self.add_node("A", NodeA())
        self.add_node("B", NodeB())
        self.add_node("C", NodeC())
        self.add_node("D", NodeD())
        
        self.add_edge(START, "A")
        self.add_edge("A", "B")
        self.add_conditional_edges("B", {"to_c": "C", "to_d": "D"})
        self.add_edge("C", END)
        self.add_edge("D", END)

def test_random_flow():
    flow = RandomFlow()
    
    seen_c = False
    seen_d = False
    
    # Run up to 100 times to avoid infinite loop if something is wrong, 
    # but practically it should hit both very quickly.
    for _ in range(100):
        state = FlowState()
        final_state = flow.run(state)
        
        assert final_state.history[0] == "A"
        assert final_state.history[1] == "B"
        
        last_node = final_state.history[2]
        print(final_state)
        assert last_node in ["C", "D"]
        
        if last_node == "C":
            seen_c = True
        if last_node == "D":
            seen_d = True

            
    assert seen_c, "Node C was never reached"
    assert seen_d, "Node D was never reached"
    print("Test passed: Both nodes C and D were reached randomly.")

if __name__ == "__main__":
    test_random_flow()
