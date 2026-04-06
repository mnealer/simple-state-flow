import time
from typing import List, Optional
from pydantic import BaseModel, Field
from simple_state_flow.nodes import Node, START, END
from simple_state_flow.flows import StateFlow

class SyncState(BaseModel):
    last_sync: Optional[float] = None
    records_synced: int = 0
    sync_type: str = "none"
    logs: List[str] = Field(default_factory=list)

class CheckLastSyncNode(Node[SyncState]):
    def exec(self) -> None:
        if self.state.last_sync is None or (time.time() - self.state.last_sync) > 86400:
            self.result = "old"
        else:
            self.result = "recent"

class DeltaSyncNode(Node[SyncState]):
    def exec(self) -> None:
        self.state.logs.append("Performing delta sync (only changes)")
        self.state.records_synced = 5
        self.state.sync_type = "delta"

class FullSyncNode(Node[SyncState]):
    def exec(self) -> None:
        self.state.logs.append("Performing full sync (all data)")
        self.state.records_synced = 100
        self.state.sync_type = "full"

class ApiSyncFlow(StateFlow[SyncState]):
    def setup_graph(self) -> None:
        self.add_node("check", CheckLastSyncNode())
        self.add_node("delta", DeltaSyncNode())
        self.add_node("full", FullSyncNode())

        self.add_edge(START, "check")
        self.add_conditional_edges("check", {
            "recent": "delta",
            "old": "full"
        })
        self.add_edge("delta", END)
        self.add_edge("full", END)

if __name__ == "__main__":
    flow = ApiSyncFlow()
    # Case: Old sync
    state1 = flow.run(SyncState(last_sync=None))
    print(f"Sync 1: {state1.sync_type}, Records: {state1.records_synced}")
    
    # Case: Recent sync
    state2 = flow.run(SyncState(last_sync=time.time()))
    print(f"Sync 2: {state2.sync_type}, Records: {state2.records_synced}")
