from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class ExpenseState(BaseModel):
    employee_id: str
    amount: float
    category: str
    description: str
    is_processed: bool = False
    audit_trail: List[str] = Field(default_factory=list)
    manager_approval_required: bool = False

class CategorizeExpenseNode(Node[ExpenseState]):
    def exec(self) -> None:
        if self.state.category == "travel":
            self.result = "travel"
        elif self.state.category == "hardware":
            self.result = "hardware"
        else:
            self.result = "other"

class TravelPolicyCheckNode(Node[ExpenseState]):
    def exec(self) -> None:
        print(f"Checking travel policy for {self.state.employee_id}")
        self.state.audit_trail.append("Travel policy check completed")
        self.state.manager_approval_required = True

class InventoryUpdateNode(Node[ExpenseState]):
    def exec(self) -> None:
        print(f"Updating hardware inventory for {self.state.employee_id}")
        self.state.audit_trail.append("Hardware inventory updated")
        self.state.manager_approval_required = True

class GeneralApprovalNode(Node[ExpenseState]):
    def exec(self) -> None:
        print(f"General expense review for {self.state.employee_id}")
        self.state.audit_trail.append("General approval process started")
        if self.state.amount < 100:
             self.state.is_processed = True
        else:
             self.state.manager_approval_required = True

class ExpenseFlow(StateFlow[ExpenseState]):
    def setup_graph(self) -> None:
        self.add_node("categorize", CategorizeExpenseNode())
        self.add_node("travel_check", TravelPolicyCheckNode())
        self.add_node("hardware_inventory", InventoryUpdateNode())
        self.add_node("general_review", GeneralApprovalNode())

        self.add_edge(START, "categorize")
        self.add_conditional_edges("categorize", {
            "travel": "travel_check",
            "hardware": "hardware_inventory",
            "other": "general_review"
        })
        self.add_edge("travel_check", END)
        self.add_edge("hardware_inventory", END)
        self.add_edge("general_review", END)

if __name__ == "__main__":
    flow = ExpenseFlow()
    state = ExpenseState(employee_id="E101", amount=250.0, category="hardware", description="New Laptop")
    final_state = flow.run(state)
    print(f"Processed: {final_state.is_processed}, Manager Required: {final_state.manager_approval_required}")
