from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class PaymentState(BaseModel):
    user_id: str
    amount: float
    card_token: str
    status: str = "pending"
    error_message: Optional[str] = None
    audit_logs: List[str] = Field(default_factory=list)

class ChargeCardNode(Node[PaymentState]):
    def exec(self) -> None:
        self.state.audit_logs.append(f"Attempting to charge {self.state.amount} to {self.state.card_token}")
        
        # Mock logic for demonstration
        if self.state.amount > 1000:
            self.result = "fraud_flag"
            self.state.error_message = "High value transaction flagged for review"
        elif self.state.card_token == "expired_token":
            self.result = "expired"
            self.state.error_message = "Card has expired"
        elif self.state.amount > 500:
            self.result = "insufficient_funds"
            self.state.error_message = "Insufficient funds in account"
        else:
            self.result = "success"
            self.state.status = "completed"

class EmailReceiptNode(Node[PaymentState]):
    def exec(self) -> None:
        self.state.audit_logs.append("Email receipt sent to user")

class NotifyUserNode(Node[PaymentState]):
    def exec(self) -> None:
        self.state.audit_logs.append(f"Notification sent: {self.state.error_message}")

class EscalateToSecurityNode(Node[PaymentState]):
    def exec(self) -> None:
        self.state.status = "blocked"
        self.state.audit_logs.append("Transaction escalated to security team")

class PaymentGatewayFlow(StateFlow[PaymentState]):
    def setup_graph(self) -> None:
        self.add_node("charge", ChargeCardNode())
        self.add_node("receipt", EmailReceiptNode())
        self.add_node("notify", NotifyUserNode())
        self.add_node("escalate", EscalateToSecurityNode())

        self.add_edge(START, "charge")
        
        self.add_conditional_edges("charge", {
            "success": "receipt",
            "insufficient_funds": "notify",
            "expired": "notify",
            "fraud_flag": "escalate"
        })

        self.add_edge("receipt", END)
        self.add_edge("notify", END)
        self.add_edge("escalate", END)

if __name__ == "__main__":
    payment_flow = PaymentGatewayFlow()
    state = payment_flow.run(PaymentState(user_id="user1", amount=50.0, card_token="valid_token"))
    print(f"Payment Status: {state.status}, Logs: {state.audit_logs}")
