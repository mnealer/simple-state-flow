from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class PasswordResetState(BaseModel):
    user_email: str
    has_security_questions: bool = False
    security_questions: List[str] = Field(default_factory=list)
    reset_token: Optional[str] = None
    flow_type: str = "pending"

class CheckSecurityQuestionsNode(Node[PasswordResetState]):
    def exec(self) -> None:
        if self.state.has_security_questions:
            self.result = "has_questions"
        else:
            self.result = "no_questions"

class AskSecurityQuestionsNode(Node[PasswordResetState]):
    def exec(self) -> None:
        print(f"Asking security questions for {self.state.user_email}")
        self.state.flow_type = "security_questions"

class SendEmailLinkNode(Node[PasswordResetState]):
    def exec(self) -> None:
        print(f"Sending reset link to {self.state.user_email}")
        self.state.reset_token = "reset-link-123"
        self.state.flow_type = "email_link"

class PasswordResetFlow(StateFlow[PasswordResetState]):
    def setup_graph(self) -> None:
        self.add_node("check_questions", CheckSecurityQuestionsNode())
        self.add_node("ask_questions", AskSecurityQuestionsNode())
        self.add_node("send_link", SendEmailLinkNode())

        self.add_edge(START, "check_questions")
        self.add_conditional_edges("check_questions", {
            "has_questions": "ask_questions",
            "no_questions": "send_link"
        })
        self.add_edge("ask_questions", END)
        self.add_edge("send_link", END)

if __name__ == "__main__":
    flow = PasswordResetFlow()
    state = PasswordResetState(user_email="user@example.com", has_security_questions=True)
    final_state = flow.run(state)
    print(f"Flow type used: {final_state.flow_type}")
