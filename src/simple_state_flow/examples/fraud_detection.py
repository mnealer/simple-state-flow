from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class FraudState(BaseModel):
    transaction_id: str
    amount: float
    user_location: str
    risk_score: int = 0
    decision: str = "pending"
    mfa_verified: bool = False
    alerts: List[str] = Field(default_factory=list)

class RiskScoreNode(Node[FraudState]):
    def exec(self) -> None:
        if self.state.amount > 5000:
            self.state.risk_score += 80
        elif self.state.user_location == "suspicious_node":
            self.state.risk_score += 50
        else:
            self.state.risk_score += 10
        
        if self.state.risk_score > 70:
            self.result = "high"
        elif self.state.risk_score > 30:
            self.result = "medium"
        else:
            self.result = "low"

class ApproveTransactionNode(Node[FraudState]):
    def exec(self) -> None:
        self.state.decision = "approved"
        print(f"Transaction {self.state.transaction_id} approved.")

class TriggerMFANode(Node[FraudState]):
    def exec(self) -> None:
        self.state.decision = "mfa_required"
        print(f"MFA triggered for {self.state.transaction_id}.")

class BlockTransactionNode(Node[FraudState]):
    def exec(self) -> None:
        self.state.decision = "blocked"
        self.state.alerts.append("High risk transaction blocked")
        print(f"Transaction {self.state.transaction_id} blocked.")

class FraudDetectionFlow(StateFlow[FraudState]):
    def setup_graph(self) -> None:
        self.add_node("score", RiskScoreNode())
        self.add_node("approve", ApproveTransactionNode())
        self.add_node("mfa", TriggerMFANode())
        self.add_node("block", BlockTransactionNode())

        self.add_edge(START, "score")
        self.add_conditional_edges("score", {
            "low": "approve",
            "medium": "mfa",
            "high": "block"
        })
        self.add_edge("approve", END)
        self.add_edge("mfa", END)
        self.add_edge("block", END)

if __name__ == "__main__":
    flow = FraudDetectionFlow()
    state = FraudState(transaction_id="tx_123", amount=6000, user_location="US")
    final_state = flow.run(state)
    print(f"Decision: {final_state.decision}")
    print(f"Risk Score: {final_state.risk_score}")
