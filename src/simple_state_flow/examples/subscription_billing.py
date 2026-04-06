from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class SubscriptionState(BaseModel):
    user_id: str
    subscription_id: str
    status: str = "active"
    expiry_date: datetime
    last_billed: Optional[datetime] = None
    grace_period_ends: Optional[datetime] = None

class CheckSubscriptionNode(Node[SubscriptionState]):
    def exec(self) -> None:
        now = datetime.now()
        if self.state.expiry_date > now:
            self.result = "active"
        elif self.state.grace_period_ends and self.state.grace_period_ends > now:
            self.result = "grace_period"
        else:
            self.result = "past_due"

class RenewSubscriptionNode(Node[SubscriptionState]):
    def exec(self) -> None:
        print(f"Renewing subscription {self.state.subscription_id}")
        self.state.expiry_date += timedelta(days=30)
        self.state.last_billed = datetime.now()

class SendReminderNode(Node[SubscriptionState]):
    def exec(self) -> None:
        print(f"Sending payment reminder for {self.state.subscription_id}")

class LockAccountNode(Node[SubscriptionState]):
    def exec(self) -> None:
        print(f"Locking account for user {self.state.user_id}")
        self.state.status = "locked"

class SubscriptionFlow(StateFlow[SubscriptionState]):
    def setup_graph(self) -> None:
        self.add_node("check", CheckSubscriptionNode())
        self.add_node("renew", RenewSubscriptionNode())
        self.add_node("remind", SendReminderNode())
        self.add_node("lock", LockAccountNode())

        self.add_edge(START, "check")
        self.add_conditional_edges("check", {
            "active": "renew",
            "grace_period": "remind",
            "past_due": "lock"
        })
        self.add_edge("renew", END)
        self.add_edge("remind", END)
        self.add_edge("lock", END)

if __name__ == "__main__":
    flow = SubscriptionFlow()
    # Mocking a state in grace period
    state = SubscriptionState(
        user_id="user_1",
        subscription_id="sub_abc",
        expiry_date=datetime.now() - timedelta(days=1),
        grace_period_ends=datetime.now() + timedelta(days=2)
    )
    final_state = flow.run(state)
    print(f"Final Status: {final_state.status}")
