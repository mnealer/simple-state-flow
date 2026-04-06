from typing import Optional
from pydantic import BaseModel
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class MFAState(BaseModel):
    user_id: str
    preferred_method: str = "sms"
    mfa_code: Optional[str] = None
    is_verified: bool = False
    attempts: int = 0

class GetPreferenceNode(Node[MFAState]):
    def exec(self) -> None:
        if self.state.preferred_method == "sms":
            self.result = "sms"
        else:
            self.result = "totp"

class SendSMSCodeNode(Node[MFAState]):
    def exec(self) -> None:
        print(f"Sending SMS code to user {self.state.user_id}")
        self.state.mfa_code = "123456"

class VerifyAppCodeNode(Node[MFAState]):
    def exec(self) -> None:
        print(f"Waiting for TOTP app code for user {self.state.user_id}")
        self.state.mfa_code = "654321"

class MFALogicFlow(StateFlow[MFAState]):
    def setup_graph(self) -> None:
        self.add_node("get_preference", GetPreferenceNode())
        self.add_node("send_sms", SendSMSCodeNode())
        self.add_node("verify_totp", VerifyAppCodeNode())

        self.add_edge(START, "get_preference")
        self.add_conditional_edges("get_preference", {
            "sms": "send_sms",
            "totp": "verify_totp"
        })
        self.add_edge("send_sms", END)
        self.add_edge("verify_totp", END)

if __name__ == "__main__":
    flow = MFALogicFlow()
    state = MFAState(user_id="user_789", preferred_method="totp")
    final_state = flow.run(state)
    print(f"MFA Code: {final_state.mfa_code}")
