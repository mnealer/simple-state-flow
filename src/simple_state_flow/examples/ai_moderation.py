from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class ContentState(BaseModel):
    content: str
    moderation_status: str = "pending"
    reason: Optional[str] = None
    logs: List[str] = Field(default_factory=list)

class AIModeratorNode(Node[ContentState]):
    def exec(self) -> None:
        self.state.logs.append("AI analyzing content for policy violations")
        if "bad_word" in self.state.content.lower():
            self.result = "rejected"
        elif "sensitive_topic" in self.state.content.lower():
            self.result = "flagged"
        else:
            self.result = "approved"

class PublishContentNode(Node[ContentState]):
    def exec(self) -> None:
        self.state.logs.append("Content approved and published")
        self.state.moderation_status = "published"

class HumanReviewNode(Node[ContentState]):
    def exec(self) -> None:
        self.state.logs.append("Content flagged for human review")
        self.state.moderation_status = "in_review"

class NotifyAuthorNode(Node[ContentState]):
    def exec(self) -> None:
        self.state.logs.append("Content rejected. Notifying author.")
        self.state.moderation_status = "rejected"

class AIModerationFlow(StateFlow[ContentState]):
    def setup_graph(self) -> None:
        self.add_node("ai_moderator", AIModeratorNode())
        self.add_node("publish", PublishContentNode())
        self.add_node("human_review", HumanReviewNode())
        self.add_node("notify", NotifyAuthorNode())

        self.add_edge(START, "ai_moderator")
        self.add_conditional_edges("ai_moderator", {
            "approved": "publish",
            "flagged": "human_review",
            "rejected": "notify"
        })
        self.add_edge("publish", END)
        self.add_edge("human_review", END)
        self.add_edge("notify", END)

if __name__ == "__main__":
    flow = AIModerationFlow()
    # Case: Approved
    state1 = flow.run(ContentState(content="Hello world!"))
    print(f"Content 1: {state1.moderation_status}")
    
    # Case: Flagged
    state2 = flow.run(ContentState(content="Discussing sensitive_topic"))
    print(f"Content 2: {state2.moderation_status}")
