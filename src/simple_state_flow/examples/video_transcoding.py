from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class VideoState(BaseModel):
    video_id: str
    resolution: int
    transcode_status: str = "pending"
    logs: List[str] = Field(default_factory=list)

class InspectVideoNode(Node[VideoState]):
    def exec(self) -> None:
        self.state.logs.append(f"Inspecting video {self.state.video_id} resolution: {self.state.resolution}p")
        if self.state.resolution >= 720:
            self.result = "high_res"
        else:
            self.result = "low_res"

class TranscodeNode(Node[VideoState]):
    def exec(self) -> None:
        self.state.logs.append("Transcoding video to multiple formats")
        self.state.transcode_status = "completed"

class NotifyUserLowQualityNode(Node[VideoState]):
    def exec(self) -> None:
        self.state.logs.append("Video resolution too low. Notifying user.")
        self.state.transcode_status = "rejected"

class VideoTranscodingFlow(StateFlow[VideoState]):
    def setup_graph(self) -> None:
        self.add_node("inspect", InspectVideoNode())
        self.add_node("transcode", TranscodeNode())
        self.add_node("notify_low_quality", NotifyUserLowQualityNode())

        self.add_edge(START, "inspect")
        self.add_conditional_edges("inspect", {
            "high_res": "transcode",
            "low_res": "notify_low_quality"
        })
        self.add_edge("transcode", END)
        self.add_edge("notify_low_quality", END)

if __name__ == "__main__":
    flow = VideoTranscodingFlow()
    # Case: Low res
    state = flow.run(VideoState(video_id="vid-101", resolution=480))
    print(f"Video: {state.video_id}, Status: {state.transcode_status}, Last Log: {state.logs[-1]}")
