from typing import Optional
from pydantic import BaseModel
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class AccountState(BaseModel):
    user_id: str
    suspension_reason: str = "unknown"
    appeal_submitted: bool = False
    payment_method_updated: bool = False
    status: str = "suspended"

class GetSuspensionReasonNode(Node[AccountState]):
    def exec(self) -> None:
        if self.state.suspension_reason == "tos_violation":
            self.result = "tos_violation"
        elif self.state.suspension_reason == "billing_issue":
            self.result = "billing_issue"
        else:
            self.result = "unknown"

class AppealsProcessNode(Node[AccountState]):
    def exec(self) -> None:
        print(f"Starting TOS appeal for {self.state.user_id}")
        self.state.appeal_submitted = True
        self.state.status = "under_review"

class PaymentUpdateNode(Node[AccountState]):
    def exec(self) -> None:
        print(f"Updating billing for {self.state.user_id}")
        self.state.payment_method_updated = True
        self.state.status = "active"

class RecoveryFlow(StateFlow[AccountState]):
    def setup_graph(self) -> None:
        self.add_node("get_reason", GetSuspensionReasonNode())
        self.add_node("appeals", AppealsProcessNode())
        self.add_node("payment", PaymentUpdateNode())

        self.add_edge(START, "get_reason")
        self.add_conditional_edges("get_reason", {
            "tos_violation": "appeals",
            "billing_issue": "payment"
        })
        self.add_edge("appeals", END)
        self.add_edge("payment", END)

if __name__ == "__main__":
    flow = RecoveryFlow()
    state = AccountState(user_id="user_vandal", suspension_reason="tos_violation")
    final_state = flow.run(state)
    print(f"Final Status: {final_state.status}, Appeal: {final_state.appeal_submitted}")
