from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class CampaignState(BaseModel):
    user_id: str
    activity_level: str  # active, churning, new
    template_sent: Optional[str] = None
    logs: List[str] = Field(default_factory=list)

class CheckEngagementNode(Node[CampaignState]):
    def exec(self) -> None:
        self.state.logs.append(f"Checking engagement for user {self.state.user_id}")
        self.result = self.state.activity_level

class LoyaltyDiscountNode(Node[CampaignState]):
    def exec(self) -> None:
        self.state.logs.append("Active user. Sending loyalty discount.")
        self.state.template_sent = "loyalty_discount_v1"

class WinBackOfferNode(Node[CampaignState]):
    def exec(self) -> None:
        self.state.logs.append("Churning user. Sending win-back offer.")
        self.state.template_sent = "winback_offer_v2"

class WelcomeSeriesNode(Node[CampaignState]):
    def exec(self) -> None:
        self.state.logs.append("New user. Sending welcome series.")
        self.state.template_sent = "welcome_series_v1"

class EmailCampaignFlow(StateFlow[CampaignState]):
    def setup_graph(self) -> None:
        self.add_node("check_engagement", CheckEngagementNode())
        self.add_node("loyalty", LoyaltyDiscountNode())
        self.add_node("winback", WinBackOfferNode())
        self.add_node("welcome", WelcomeSeriesNode())

        self.add_edge(START, "check_engagement")
        self.add_conditional_edges("check_engagement", {
            "active": "loyalty",
            "churning": "winback",
            "new": "welcome"
        })
        self.add_edge("loyalty", END)
        self.add_edge("winback", END)
        self.add_edge("welcome", END)

if __name__ == "__main__":
    flow = EmailCampaignFlow()
    # Case: Churning
    state = flow.run(CampaignState(user_id="U-55", activity_level="churning"))
    print(f"User: {state.user_id}, Template: {state.template_sent}")
