from typing import Optional
from pydantic import BaseModel
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class KYCState(BaseModel):
    user_id: str
    document_path: str
    status: str = "pending"
    is_verified: bool = False
    verification_error: Optional[str] = None

class ScanDocumentNode(Node[KYCState]):
    def exec(self) -> None:
        print(f"Scanning document at {self.state.document_path}")
        if "blurry" in self.state.document_path:
            self.result = "blurry"
        elif "fake" in self.state.document_path:
            self.result = "suspicious"
        else:
            self.result = "clear"

class VerifyIdentityNode(Node[KYCState]):
    def exec(self) -> None:
        print(f"Verifying identity for user {self.state.user_id}")
        self.state.is_verified = True
        self.state.status = "verified"

class RequestResubmitNode(Node[KYCState]):
    def exec(self) -> None:
        print("Document blurry. Requesting resubmission.")
        self.state.verification_error = "Document was too blurry to read."

class ManualReviewNode(Node[KYCState]):
    def exec(self) -> None:
        print("Suspicious document. Flagging for manual review.")
        self.state.status = "manual_review"

class KYCVerificationFlow(StateFlow[KYCState]):
    def setup_graph(self) -> None:
        self.add_node("scan", ScanDocumentNode())
        self.add_node("verify", VerifyIdentityNode())
        self.add_node("resubmit", RequestResubmitNode())
        self.add_node("manual", ManualReviewNode())

        self.add_edge(START, "scan")
        self.add_conditional_edges("scan", {
            "clear": "verify",
            "blurry": "resubmit",
            "suspicious": "manual"
        })
        self.add_edge("verify", END)
        self.add_edge("resubmit", END)
        self.add_edge("manual", END)

if __name__ == "__main__":
    flow = KYCVerificationFlow()
    state = flow.run(KYCState(user_id="user_456", document_path="/uploads/id_card.jpg"))
    print(f"Final Status: {state.status}, Verified: {state.is_verified}")
