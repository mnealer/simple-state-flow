from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class OnboardingState(BaseModel):
    user_id: str
    user_role: str = "member"
    team_name: str
    onboarding_steps: List[str] = Field(default_factory=list)
    has_admin_access: bool = False

class GetUserTypeNode(Node[OnboardingState]):
    def exec(self) -> None:
        if self.state.user_role == "admin":
            self.result = "admin"
        else:
            self.result = "member"

class SetupTeamNode(Node[OnboardingState]):
    def exec(self) -> None:
        print(f"Setting up new team: {self.state.team_name} for admin {self.state.user_id}")
        self.state.has_admin_access = True
        self.state.onboarding_steps.append("Team created")

class JoinTeamNode(Node[OnboardingState]):
    def exec(self) -> None:
        print(f"Adding user {self.state.user_id} to existing team: {self.state.team_name}")
        self.state.onboarding_steps.append("Team joined")

class UserOnboardingFlow(StateFlow[OnboardingState]):
    def setup_graph(self) -> None:
        self.add_node("get_type", GetUserTypeNode())
        self.add_node("setup_team", SetupTeamNode())
        self.add_node("join_team", JoinTeamNode())

        self.add_edge(START, "get_type")
        self.add_conditional_edges("get_type", {
            "admin": "setup_team",
            "member": "join_team"
        })
        self.add_edge("setup_team", END)
        self.add_edge("join_team", END)

if __name__ == "__main__":
    flow = UserOnboardingFlow()
    state = OnboardingState(user_id="user_admin", user_role="admin", team_name="Engineering")
    final_state = flow.run(state)
    print(f"Admin Access: {final_state.has_admin_access}, Steps: {final_state.onboarding_steps}")
