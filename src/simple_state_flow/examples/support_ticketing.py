from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class TicketState(BaseModel):
    ticket_id: str
    message: str
    sentiment: str = "neutral"
    routing: str = "general"
    logs: List[str] = Field(default_factory=list)

class SentimentAnalysisNode(Node[TicketState]):
    def exec(self) -> None:
        self.state.logs.append(f"Analyzing sentiment of ticket {self.state.ticket_id}")
        msg = self.state.message.lower()
        if any(word in msg for word in ["angry", "upset", "terrible", "fix"]):
            self.result = "angry"
        elif any(word in msg for word in ["happy", "great", "thanks"]):
            self.result = "happy"
        else:
            self.result = "neutral"

class EscalateToLeadNode(Node[TicketState]):
    def exec(self) -> None:
        self.state.logs.append("Angry sentiment detected. Escalating to lead...")
        self.state.routing = "support_lead"

class AutoReplyNode(Node[TicketState]):
    def exec(self) -> None:
        self.state.logs.append("Neutral sentiment. Sending automated response.")
        self.state.routing = "auto_reply"

class RequestReviewNode(Node[TicketState]):
    def exec(self) -> None:
        self.state.logs.append("Happy customer! Requesting a review.")
        self.state.routing = "review_request"

class SupportTicketingFlow(StateFlow[TicketState]):
    def setup_graph(self) -> None:
        self.add_node("analyze", SentimentAnalysisNode())
        self.add_node("escalate", EscalateToLeadNode())
        self.add_node("auto_reply", AutoReplyNode())
        self.add_node("request_review", RequestReviewNode())

        self.add_edge(START, "analyze")
        self.add_conditional_edges("analyze", {
            "angry": "escalate",
            "neutral": "auto_reply",
            "happy": "request_review"
        })
        self.add_edge("escalate", END)
        self.add_edge("auto_reply", END)
        self.add_edge("request_review", END)

if __name__ == "__main__":
    flow = SupportTicketingFlow()
    # Case: Angry
    state = flow.run(TicketState(ticket_id="T-1", message="This is terrible, fix it!"))
    print(f"Ticket: {state.ticket_id}, Routing: {state.routing}")
