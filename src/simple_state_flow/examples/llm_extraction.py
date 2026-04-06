from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class ExtractionState(BaseModel):
    raw_text: str
    extracted_data: Optional[dict] = None
    validation_error: Optional[str] = None
    retry_count: int = 0
    logs: List[str] = Field(default_factory=list)

class ValidateExtractionNode(Node[ExtractionState]):
    def exec(self) -> None:
        self.state.logs.append("Validating LLM extraction")
        if self.state.extracted_data and "name" in self.state.extracted_data:
            self.result = "valid"
        else:
            self.result = "invalid"
            self.state.validation_error = "Missing required field 'name'"

class SaveToDBNode(Node[ExtractionState]):
    def exec(self) -> None:
        self.state.logs.append("Saving valid extraction to database")

class RefinePromptNode(Node[ExtractionState]):
    def exec(self) -> None:
        self.state.logs.append(f"Retrying extraction with refined prompt. Error: {self.state.validation_error}")
        self.state.retry_count += 1
        # In a real app, this would call the LLM again
        self.state.extracted_data = {"name": "John Doe", "age": 30}

class LLMExtractionFlow(StateFlow[ExtractionState]):
    def setup_graph(self) -> None:
        self.add_node("validate", ValidateExtractionNode())
        self.add_node("save", SaveToDBNode())
        self.add_node("refine", RefinePromptNode())

        self.add_edge(START, "validate")
        self.add_conditional_edges("validate", {
            "valid": "save",
            "invalid": "refine"
        })
        self.add_edge("refine", "validate")  # Loop back for re-validation
        self.add_edge("save", END)

if __name__ == "__main__":
    flow = LLMExtractionFlow()
    # Case: Needs one retry
    initial_state = ExtractionState(raw_text="Name is John Doe", extracted_data={})
    state = flow.run(initial_state)
    print(f"Retries: {state.retry_count}, Data: {state.extracted_data}, Logs: {len(state.logs)}")
