from typing import Optional
from pydantic import BaseModel
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class RefundState(BaseModel):
    order_id: str
    amount: float
    is_approved: bool = False
    approver: Optional[str] = None

class CheckAmountNode(Node[RefundState]):
    def exec(self) -> None:
        if self.state.amount < 50.0:
            self.result = "auto_approve"
        else:
            self.result = "manual_review"

class ProcessRefundNode(Node[RefundState]):
    def exec(self) -> None:
        self.state.is_approved = True
        self.state.approver = "System (Auto)"

class AssignToManagerNode(Node[RefundState]):
    def exec(self) -> None:
        self.state.approver = "Manager (Pending)"

class RefundApprovalFlow(StateFlow[RefundState]):
    def setup_graph(self) -> None:
        self.add_node("check", CheckAmountNode())
        self.add_node("process", ProcessRefundNode())
        self.add_node("manager", AssignToManagerNode())

        self.add_edge(START, "check")
        self.add_conditional_edges("check", {
            "auto_approve": "process",
            "manual_review": "manager"
        })
        self.add_edge("process", END)
        self.add_edge("manager", END)

if __name__ == "__main__":
    refund_flow = RefundApprovalFlow()
    state = refund_flow.run(RefundState(order_id="order123", amount=75.0))
    print(f"Refund Approver: {state.approver}")
